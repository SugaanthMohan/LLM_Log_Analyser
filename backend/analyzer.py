from langchain_core.prompts import PromptTemplate
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_community.query_constructors.chroma import ChromaTranslator
from langchain.chains.query_constructor.base import (
    StructuredQueryOutputParser,
    get_query_constructor_prompt,
    load_query_constructor_runnable
)
import attribute_info

def get_prompt():

    ANALYSER_PROMPT = """
[ROLE] Professional Software Logs Analyzer  
[TASK] Based on the provided context of log snippets, 
analyze the query in a structured manner by explaining any discrepancies, causes, and remediation steps. 
If a related scenario is found without any issues, consider it the "happy path" and reference it in your response. 

You should clearly outline your chain of thought and reasoning to arrive at a solution using the below set of steps.

1. Steps:  
   - Step 1: Identify the critical pieces of information required to answer the query.  
   - Step 2: Analyze the provided log snippets and match them with the query.  
   - Step 3: Look for any discrepancies, errors, or anomalies in the logs that might be causing the issue.  
   - Step 4: If no issue is found, look for a "happy path" scenario (where everything works as expected) and provide that as a reference.  
   - Step 5: Based on the analysis, provide a concise summary of the issue and suggest remediation steps.

Formulate your response as below:

1. Summary:  
   <Provide a high-level summary of the issue, if applicable, or describe the happy path scenario.>

2. Incident Report:  
   - Time: <Timestamp>  
   - Faced By: <Customer/Teller/User Id>  
   - Trace Id: <TraceID/SessionID>  
   - Application: <AppID>  
   - Component: <Component>  
   - <Additional metadata key-value pairs, if available>  

3. Explanation:  
   <Explain in detail the root cause of the issue, based on the log analysis.>
   <atleast five lines>

4. Expected Ideal Flow (Happy Path):  
   <If applicable, describe what should have been the ideal scenario given this issue/error hadn't happened>
   <atleast three points>

5. Remediation:  
   <Based on the identified issue or happy path scenario, suggest possible remediation steps to resolve the problem.>
   <atleast three points>


Below are the contexts for you to refer:  
{context}

Below is the query for you to answer:  
{query}
"""
    return ANALYSER_PROMPT


def analyze_without_metadata(db, llm, APP_ID, TIME_FROM, TIME_TO, QUERY):

    retriever = db.as_retriever(
                search_type="mmr",  # Maximal Marginal Relevance
                search_kwargs={
                    'k': 10,  # Final results
                    'fetch_k': 20,  # Initial candidate pool
                    'lambda_mult': 0.65,  # 65% relevance, 35% diversity
                    'score_threshold': 0.6,  # Minimum relevance floor
                    'where': {   # Metadata filtering
                        "$and": [
                            {"APP_ID": APP_ID},  
                            {"Timestamp": {"$gte": TIME_FROM}},  
                            {"Timestamp": {"$lte": TIME_TO}}  
                        ]
                    }
                }
            )
    
    prompt = PromptTemplate.from_template(get_prompt())

     # Using the 'invoke' method instead of 'get_relevant_documents'
    results = retriever.invoke(QUERY)
    context_text = "\n\n---\n\n".join([doc.page_content for doc in results])

    # Create the conversation history text
    # conversation_history_text = "\n".join([f'{entry["role"]}: {entry["content"]}' for entry in conversation_history])
    # print("Context:")
    # print(context_text)

    # Update the prompt with conversation history
    llm_chain = prompt | llm
    response_text = llm_chain.invoke({
        "context": context_text,
        "query": QUERY,
        # "conversation_history": conversation_history_text
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
    prompt = PromptTemplate.from_template(get_prompt())

    llm_chain = prompt | llm
    response_text = llm_chain.invoke({"context": context_text, "query": QUERY})
    return response_text