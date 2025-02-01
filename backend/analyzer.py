from langchain_core.prompts import PromptTemplate
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_community.query_constructors.chroma import ChromaTranslator
from langchain.chains.query_constructor.base import (
    StructuredQueryOutputParser,
    get_query_constructor_prompt,
    load_query_constructor_runnable
)

import re
from backend import attribute_info, parse_documents

ANALYSER_PROMPT = """
[ROLE] Professional Software Logs Analyzer  
[TASK] Based on the provided log snippets and query context, analyze and summarize the information in a structured manner. Your response should address any discrepancies, anomalies, or questions raised in the query. If no issues are found, identify and reference a "happy path" scenario from the logs. This analysis should be generic enough to handle any query regarding the logs—not solely error reporting.

Please follow these steps and output the response using the structure below:

1. Steps and Reasoning:
   - **Step 1:** Identify the critical information in the query (e.g., errors, performance issues, process flows, metadata).
   - **Step 2:** Parse the provided log snippets and match relevant details with the query requirements.
   - **Step 3:** Look for discrepancies, anomalies, or inconsistencies in the logs. If none are found, select a representative “happy path” scenario.
   - **Step 4:** Provide a detailed chain-of-thought that outlines your analysis and reasoning.
   - **Step 5:** Summarize the issue (or the scenario) and suggest remediation or improvements, if applicable.

2. Output Structure:  
   **1. Summary:**  
   - Provide a high-level summary of the findings (issue description, insights, or happy path reference).

   **2. Incident/Scenario Report:**  
   - **Time:** <Timestamp of the event or relevant log entry>  
   - **Faced By:** <Customer/Teller/User ID or context if available>  
   - **Trace Id:** <TraceID/SessionID from logs>  
   - **Application:** <Application Identifier>  
   - **Component:** <Component involved, e.g., SpringBoot, Middleware, OracleDB>  
   - **Additional Metadata:** <Other key-value pairs as available>

   **3. Explanation:**  
   - Provide a detailed explanation of the root cause or context of the scenario.  
   - Explain your reasoning in at least five lines, linking the log evidence to the analysis.

   **4. Expected Ideal Flow (Happy Path):**  
   - Describe what the ideal, error-free scenario should look like (if applicable).  
   - Provide at least three key points that define the optimal process.

   **5. Remediation / Recommendations:**  
   - Suggest actionable remediation steps or improvements based on the analysis.  
   - Include at least three recommendations.

Below are the contexts for you to refer:  
{context}

Below is the query for you to answer:  
{query}
"""

EMBEDDING_QUERY_PROMPT = """
[ROLE] Log Snippet Generator
[TASK] To generate log snippets for the provided query similar to the provided context
[PURPOSE] Generated log snippets will be embedded and used against a vector database to effectively retrieve similar documents


[DESCRIPTION]
You will provided with bunch of enterprise software log snippets and a plain user query.
Based on your understanding of the user's query you are to generate relevant log snippets that 
can possibly represent user's query in the same format as the of context.

[GUIDELINES TO CONSIDER]
- Understand the time range from query and simulate the time range in the same format as in context
- Understand log level from query and appropriate mention in generate snippet as [INFO], [ERROR], [DEBUG] or so on.
- Understand the component the query is possibly talking about and mention it accordingly
- Understand all the other relevant metadata fields and generate the same as in context's format
- Understand the query clearly and interpret what could be the relevant description for it
- Generate all varied kinds of formats of snippets for the query based on the provided context
- Try to mask the numbers in trace id if not provided in the query

[CONTEXT FOR YOUR REFERENCE]

2025-02-01T15:10:00.090Z [INFO ] [SpringBoot] [TRACE432109] Credit transaction confirmed. Finalizing funds transfer.
2025-02-01T15:10:00.095Z [DEBUG] [SpringBoot] [TRACE432109] Initiating transaction record update in OracleDB.
2025-02-01T15:10:00.100Z [DEBUG] [OracleDB] [TRACE432109] Executing query:
INSERT INTO TRANSACTION_HISTORY (TRANSACTION_ID, FROM_ACCOUNT, TO_ACCOUNT, AMOUNT, STATUS, TIMESTAMP)
VALUES ('TXN667788', '246810123', '135791357', 1000, 'COMPLETED', TO_TIMESTAMP('2025-02-01T15:10:00.100Z', 'YYYY-MM-DD"T"HH24:MI:SS.FF3"Z"'));
2025-02-01T15:10:00.105Z [INFO ] [OracleDB] [TRACE432109] Transaction record inserted successfully. Transaction ID: TXN667788.
2025-02-01T15:10:00.110Z [INFO ] [SpringBoot] [TRACE432109] Transaction successfully recorded in DB. Proceeding to complete transaction.
2025-02-01T16:00:00.055Z [INFO ] [SpringBoot] [TRACE981234] Debit confirmed. Initiating credit request.
2025-02-01T16:00:00.060Z [DEBUG] [SpringBoot] [TRACE777888] Preparing credit request.
2025-02-01T16:00:00.065Z [DEBUG] [SpringBoot] [TRACE777888] REST Request:
POST /middleware/corebanking/credit
{{
   "accountNumber": "654123987",
   "amount": 500,
   "transactionId": "TXN123450",
   "transactionType": "CREDIT"
}}
2025-02-01T16:00:00.070Z [INFO ] [Middleware] [TRACE777888] Processing credit request.
2025-02-01T16:00:00.075Z [DEBUG] [Middleware] [TRACE777888] Validating recipient account.
2025-02-01T16:00:00.080Z [INFO ] [Middleware] [TRACE777888] Credit successful. New balance: $3500.
2025-02-01T16:00:00.085Z [DEBUG] [Middleware] [TRACE777888] REST Response:
{{
   "status": "SUCCESS",
   "transactionId": "TXN123450",
   "message": "Credit successful"
}}
2025-02-01T16:00:00.090Z [INFO ] [SpringBoot] [TRACE777888] Credit transaction confirmed.
2025-02-01T16:40:00.015Z [ERROR] [PaymentGateway] [TRACE334455] REST API call failed: HTTP 500 Internal Server Error.
2025-02-01T16:40:00.020Z [INFO ] [SpringBoot] [TRACE334455] Payment request failed due to PaymentGateway error.
2025-02-01T16:40:00.025Z [ERROR] [UI] [TRACE334455] Displaying error to user: "Payment failed due to server error. Please try again later."
2025-02-01T16:40:00.030Z [DEBUG] [SpringBoot] [TRACE334455] Initiating rollback for payment transaction.
2025-02-01T16:30:10.380Z [DEBUG] [Middleware] [TRACE556677] Validating account information for Account: 112233445.
2025-02-01T16:30:10.385Z [ERROR] [SpringBoot] [TRACE556677] Exception: NullPointerException in service layer while processing response.
2025-02-01T16:30:10.390Z [INFO ] [SpringBoot] [TRACE556677] Transaction failed due to unexpected server error.
2025-02-01T16:30:10.395Z [ERROR] [UI] [TRACE556677] Displaying error to user: "Withdrawal failed due to internal server error."
2025-02-01T16:30:10.400Z [DEBUG] [SpringBoot] [TRACE556677] Initiating rollback of transaction due to NullPointerException.
2025-02-01T16:30:00.155Z [INFO ] [Middleware] [TRACE111222] Processing debit request for account 123456789.
2025-02-01T16:30:00.160Z [DEBUG] [Middleware] [TRACE111222] Checking account balance.
2025-02-01T16:30:00.165Z [ERROR] [OracleDB] [TRACE111222] Failed to execute INSERT query: ORA-00001: unique constraint (TRANSACTION_HISTORY_PK) violated.
2025-02-01T16:30:00.170Z [INFO ] [SpringBoot] [TRACE111222] Transaction aborted due to database constraint violation.
2025-02-01T16:30:00.175Z [ERROR] [UI] [TRACE111222] Displaying error to user: "Withdrawal failed due to duplicate transaction record."
2025-02-01T16:10:00.123Z [INFO ] [UI] [TRACE123456] User initiated cash withdrawal request. Amount: $500, Account: 987654321.
2025-02-01T16:10:00.124Z [DEBUG] [UI] [TRACE123456] Sending withdrawal request to Spring Boot server.
2025-02-01T16:10:00.125Z [INFO ] [SpringBoot] [TRACE123456] Received withdrawal request. Amount: $500, Account: 987654321.

[QUERY]
query: {QUERY}
time_from (in epoch milliseconds): {TIME_FROM}
time_to (in epoch milliseconds): {TIME_TO}
trace_ids: {TRACE_IDS}

[RESPONSE FORMAT] (*** TO BE FOLLOWED VERY STRICTLY ***)

1. Snippet1
2. Snippet2
3. Snippet3
4. Snippet4
... Do no generate more than six. Ensure all are of various formats.

<end of response>
"""



def get_trace_id(QUERY):
    pattern = r"TRACE\d+"
    return re.findall(pattern, QUERY)

def get_embedding_query(llm, QUERY, TIME_FROM, TIME_TO, TRACE_IDS):
    
    prompt = PromptTemplate.from_template(EMBEDDING_QUERY_PROMPT)    

    llm_chain = prompt | llm
    response_text = llm_chain.invoke({
        "QUERY": QUERY,
        "TIME_FROM": TIME_FROM,
        "TIME_TO": TIME_TO,
        "TRACE_IDS": TRACE_IDS
    })

    embedding_query_snippets = []
    for line in response_text.split("\n"):
        keywords = ['TRACE', 'DEBUG', 'INFO', 'ERROR', '2025']
        if any(keyword in line for keyword in keywords):
            embedding_query_snippets.append(line)
    
    return ("\n".join(embedding_query_snippets[:3]))

def analyze_without_metadata(db, llm, APP_ID, TIME_FROM, TIME_TO, QUERY):

    TRACE_IDS = get_trace_id(QUERY)
    TIME_FROM = int(parse_documents.parse_unix_epoch_timestamp(TIME_FROM))
    TIME_TO = int(parse_documents.parse_unix_epoch_timestamp(TIME_TO))


    EMBEDDING_QUERY = get_embedding_query(llm, QUERY, TIME_FROM, TIME_TO, TRACE_IDS) 
    print("\n\nGenerated Embedding Query: ")
    print(EMBEDDING_QUERY, "\n")

    if len(TRACE_IDS) > 0:
        metadata_filter_query = {   # Metadata filtering
                        "$and": [
                            {"APP_ID": APP_ID},  
                            {"Timestamp": {"$gte": TIME_FROM}},  
                            {"Timestamp": {"$lte": TIME_TO}},
                            {"TraceID": {"$in": TRACE_IDS}}  
                        ]
                    }
    else:
        metadata_filter_query = {   # Metadata filtering
                        "$and": [
                            {"APP_ID": APP_ID},  
                            {"Timestamp": {"$gte": TIME_FROM}},  
                            {"Timestamp": {"$lte": TIME_TO}},
                        ]
                    }

    retriever = db.as_retriever(
                search_type="similarity", 
                search_kwargs={
                    'k': 20,  # Final results
                    # 'fetch_k': 60,  # Initial candidate pool
                    # 'lambda_mult': 0.6,  # 65% relevance, 35% diversity
                    # 'score_threshold': 0.6,  # Minimum relevance floor
                    # 'where': metadata_filter_query
                },
            )
    

    results = retriever.invoke(EMBEDDING_QUERY)
    context_text = "\n\n---\n\n".join([doc.page_content for doc in results])


    prompt = PromptTemplate.from_template(ANALYSER_PROMPT)

    llm_chain = prompt | llm
    response_text = llm_chain.invoke({
        "context": context_text,
        "query": QUERY,
    })

    return results, response_text


def analyze_with_metadata(db, llm, APP_ID, TIME_FROM, TIME_TO, QUERY):

    QUERY = QUERY + f"\n Look for Log entries of Application {APP_ID} that has timestamp entries from {TIME_FROM} epoch milliseconds to {TIME_TO} epoch milliseconds."

    metadata_field_info = attribute_info.get_attribute_info(APP_ID)

    document_content_description = "Log snippets of an enterprise software application"

    retriever = SelfQueryRetriever.from_llm(
                    llm,
                    db,
                    document_content_description,
                    metadata_field_info,
                    structured_query_translator=ChromaTranslator(),
                )
    
    results = retriever.invoke(QUERY) 

    context_text = "\n\n---\n\n".join([doc.page_content for doc in results])
    prompt = PromptTemplate.from_template(ANALYSER_PROMPT)

    llm_chain = prompt | llm
    response_text = llm_chain.invoke({"context": context_text, "query": QUERY})
    return results, response_text