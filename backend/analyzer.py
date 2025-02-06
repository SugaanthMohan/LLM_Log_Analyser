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

1. Steps and Reasoning (Do not print these at any cost):
   - **Step 1:** Identify the critical information in the query (e.g., errors, performance issues, process flows, metadata).
   - **Step 2:** Parse the provided log snippets and match relevant details with the query requirements.
   - **Step 3:** Look for discrepancies, anomalies, or inconsistencies in the logs. If none are found, select a representative “happy path” scenario.
   - **Step 4:** Provide a detailed chain-of-thought that outlines your analysis and reasoning.
   - **Step 5:** Summarize the issue (or the scenario) and suggest remediation or improvements, if applicable.

2. Output Structure (Strictly follow the same format):  
   **1. Summary:**  
   - Provide a summary of the findings (issue description, insights, or happy path reference).

   **2. Incident/Scenario Report:**  
   - Time: <Timestamp of the event or relevant log entry>  
   - Faced By: <Customer/Teller/User Id or name or context if available>  
   - Trace Id: <TraceID/SessionID from logs>  
   - Application: <Application Identifier>  
   - Component: <Component involved, e.g., TellerApplication, AccountProcessSystem, OracleDB>  
   - Additional Metadata: <Other key-value pairs as available>

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

Below is the exact error snippet the user is referring to and make use of information in these snippets to fill in the information
for incident report. Look for fields like traceId, time, faced by, application, component, customer Id, customer name and additional metadata.
{error_snippet}

Below is the query for you to answer:  
{query}
"""

EMBEDDING_QUERY_PROMPT = """
[ROLE] Log Snippet Generator
[TASK] To generate log snippets for the provided query similar to the provided context
[PURPOSE] Generated log snippets will be embedded and used against a vector database to effectively retrieve similar documents


[DESCRIPTION]
You will be provided with bunch of enterprise software log snippets and a plain user query.
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

2025-02-01T16:10:00.127Z [DEBUG] [TellerApplication] [TRACE123456] SOAP Request:
<?xml version="1.0"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:mid="http://AccountProcessSystem.example.com/CustInfo">
   <soapenv:Header/>
   <soapenv:Body>
      <mid:GetCustomerInfoRequest>
         <mid:AccountNumber>987654321</mid:AccountNumber>
         <mid:CustomerId>1234123</mid:CustomerId>
         <mid:CustomerName>John</mid:CustomerName>
      </mid:GetCustomerInfoRequest>
   </soapenv:Body>
</soapenv:Envelope>
2025-02-01T16:10:00.130Z [INFO ] [AccountProcessSystem] [TRACE123456] Received SOAP request. Processing...
2025-02-01T16:10:00.135Z [DEBUG] [AccountProcessSystem] [TRACE123456] Validating account information for Account: 987654321.
2025-02-01T16:10:00.145Z [ERROR] [AccountProcessSystem] [TRACE123456] Account validation failed. Invalid account number format.
2025-02-01T16:10:00.150Z [INFO ] [TellerApplication] [TRACE123456] Received failed response from AccountProcessSystem. Aborting transaction. Response time: 3 ms
2025-02-01T16:10:00.155Z [DEBUG] [UI] [TRACE123456] Displaying error message to user: "Invalid account number format. Please check your details."
2025-02-01T16:10:00.160Z [ERROR] [UI] [TRACE123456] User interaction failed. Unable to process withdrawal due to invalid account.
2025-02-01T16:10:00.165Z [DEBUG] [TellerApplication] [TRACE123456] Transaction aborted due to validation failure.
2025-02-01T16:00:00.090Z [INFO ] [TellerApplication] [TRACE777888] Credit transaction confirmed.
2025-02-01T16:10:10.330Z [INFO ] [TellerApplication] [TRACE876543] Received withdrawal request. Amount: $200, Account: 123987654.
2025-02-01T16:10:10.340Z [DEBUG] [TellerApplication] [TRACE876543] Preparing REST request for AccountProcessSystem.
2025-02-01T16:10:10.345Z [DEBUG] [TellerApplication] [TRACE876543] REST Request:
POST /api/v1/getCustomerInfo
{{
   "accountNumber": "123987654",
   "customerId": "89213",
   "customerName": "David"
}}
2025-02-01T16:10:10.355Z [INFO ] [AccountProcessSystem] [TRACE876543] Received REST request. Processing...
2025-02-01T16:10:10.360Z [DEBUG] [AccountProcessSystem] [TRACE876543] Validating account information for Account: 123987654.
2025-02-01T16:10:10.370Z [ERROR] [AccountProcessSystem] [TRACE876543] Error occurred while validating account: Account number not found in database.
2025-02-01T16:10:10.375Z [INFO ] [TellerApplication] [TRACE876543] Received failed response from AccountProcessSystem. Aborting transaction. Response time: 1 ms
2025-02-01T16:10:10.380Z [DEBUG] [UI] [TRACE876543] Displaying error message to user: "Account number not found. Please check your details."
2025-02-01T16:10:10.385Z [ERROR] [UI] [TRACE876543] User interaction failed. Unable to process withdrawal due to account not found.
2025-02-01T16:10:00.130Z [INFO ] [AccountProcessSystem] [TRACE123456] Received SOAP request. Processing...
2025-02-01T16:10:00.135Z [DEBUG] [AccountProcessSystem] [TRACE123456] Validating account information for Account: 987654321.
2025-02-01T16:10:00.145Z [ERROR] [AccountProcessSystem] [TRACE123456] Account validation failed. Invalid account number format.
2025-02-01T16:10:00.150Z [INFO ] [TellerApplication] [TRACE123456] Received failed response from AccountProcessSystem. Aborting transaction. Response time: 4 ms
2025-02-01T16:10:00.155Z [DEBUG] [UI] [TRACE123456] Displaying error message to user: "Invalid account number format. Please check your details."
2025-02-01T16:10:00.160Z [ERROR] [UI] [TRACE123456] User interaction failed. Unable to process withdrawal due to invalid account.
2025-02-01T16:10:00.165Z [DEBUG] [TellerApplication] [TRACE123456] Transaction aborted due to validation failure.
2025-02-01T16:40:00.010Z [DEBUG] [TellerApplication] [TRACE334455] REST Request:
POST /payment/charge
{{
   "accountNumber": "555666777",
   "amount": 1000,
   "customerId": "90912",
   "customerName": "Marie"
}}
2025-02-01T16:40:00.015Z [ERROR] [PaymentGateway] [TRACE334455] REST API call failed: HTTP 500 Internal Server Error. Response time: 1 ms
2025-02-01T16:40:00.020Z [INFO ] [TellerApplication] [TRACE334455] Payment request failed due to PaymentGateway error.
2025-02-01T16:40:00.025Z [ERROR] [UI] [TRACE334455] Displaying error to user: "Payment failed due to server error. Please try again later."
2025-02-01T16:30:15.485Z [ERROR] [TellerApplication] [TRACE556677] Error during shutdown: Failed to close one or more resources.
2025-02-01T16:30:10.370Z [DEBUG] [TellerApplication] [TRACE556677] REST Request:
POST /api/v1/getCustomerInfo
{{
   "accountNumber": "112233445",
   "customerId": "124235",
   "customerName": "Jacob"
}}
2025-02-01T16:30:10.375Z [INFO ] [AccountProcessSystem] [TRACE556677] Received REST request. Processing...
2025-02-01T16:30:10.380Z [DEBUG] [AccountProcessSystem] [TRACE556677] Validating account information for Account: 112233445.
2025-02-01T16:30:10.385Z [ERROR] [TellerApplication] [TRACE556677] Exception: NullPointerException in service layer while processing response.
2025-02-01T16:30:10.390Z [INFO ] [TellerApplication] [TRACE556677] Transaction failed due to unexpected server error. Response time: 1 ms
2025-02-01T16:30:10.395Z [ERROR] [UI] [TRACE556677] Displaying error to user: "Withdrawal failed due to internal server error.
2025-02-01T16:30:05.280Z [DEBUG] [AccountProcessSystem] [TRACE223344] Error: Malformed JSON in incoming request.
2025-02-01T16:30:05.285Z [ERROR] [AccountProcessSystem] [TRACE223344] Request processing failed due to invalid JSON format. Response time: 3 ms
2025-02-01T16:30:05.290Z [INFO ] [TellerApplication] [TRACE223344] Aborting transaction due to AccountProcessSystem error.
2025-02-01T16:30:05.295Z [ERROR] [UI] [TRACE223344] User notified: "Withdrawal failed due to request format error."
2025-02-01T16:30:00.160Z [DEBUG] [AccountProcessSystem] [TRACE111222] Checking account balance.
2025-02-01T16:30:00.165Z [ERROR] [OracleDB] [TRACE111222] Failed to execute INSERT query: ORA-00001: unique constraint (TRANSACTION_HISTORY_PK) violated.
2025-02-01T16:30:00.170Z [INFO ] [TellerApplication] [TRACE111222] Transaction aborted due to database constraint violation.
2025-02-01T16:30:00.175Z [ERROR] [UI] [TRACE111222] Displaying error to user: "Withdrawal failed due to duplicate transaction record." Response time: 2 ms

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
        keywords = ['TRACE', 'DEBUG', 'INFO', 'ERROR', '2025', 'POST', 'GET', "Customer", "customer"]
        if any(keyword in line for keyword in keywords):
            embedding_query_snippets.append(line)
    
    return ("\n".join(embedding_query_snippets[:5]))

def get_relevant_docs(db, llm, APP_ID, TIME_FROM, TIME_TO, QUERY):

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
    
    results = []
    for line in EMBEDDING_QUERY.split("\n"):
        result = retriever.invoke(line)
        results.extend(result[:10])

    return results

def analyze_without_metadata(llm, QUERY, results, error_snippet):
    context_text = "\n\n---\n\n".join([doc.page_content for doc in results])
    
    prompt = PromptTemplate.from_template(ANALYSER_PROMPT)

    llm_chain = prompt | llm
    response_text = llm_chain.invoke({
        "context": context_text,
        "query": QUERY,
        "error_snippet": error_snippet
    })

    return response_text


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