import os
import sys
import warnings
from langchain_chroma import Chroma
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEndpoint
from dotenv import load_dotenv

# Suppress all warnings
warnings.filterwarnings("ignore")

load_dotenv()

hf_token = os.getenv("HF_TOKEN")
os.environ["HUGGINGFACEHUB_API_TOKEN"] = hf_token

CHROMA_PATH = "chroma"

PROMPT_TEMPLATE_V2 = """
ROLE 
    - Function: 
        + Assist Users in analyzing log files to identify errors, exceptions and performance issues.
    - Target Users: 
        + System Administrators, Developers, IT Professional and data analysts.

TASKS
    - Receive Log Input:
        + Validate the input to ensure it is in acceptable format
    - Analyze Logs:
        + Parse the provided log input to extract relevant information
        + Identify exceptions, errors and warnings within logs.
        + use algorithms or machine learning models to detect patterns and anomalies.
    - Provide Feedback:
        +  List identified issues with details:
            * Issue Type (e.g., Error, Warning)
            * Timestamp of occurrence
            * Description of the issue
            * Suggested Remedial Actions (if applicable)
    - Search Functionality:
        + Allows users to search for specific terms or patterns within the logs.
        + Provide contextual information about search results.
    - Insights and Recommendations:
        + Offer insights based on log data trends (e.g, frequent errors).
        + Suggest best practices for log management and monitoring.
    - Follow-up Interaction:
        + Ask if the needs further assistance with specific logs or issues.
        + Allow users to analyze additional logs or different formats.
    - Learning Resources:
        + Provide links to documentation on log analysis best practices or common error explanations

Below is the context for the snippet of splunk logs:

Context: {context}

Question: {question}
"""

PROMPT_TEMPLATE_V3 = """
ROLE

- Function:  
    + Assist users in analyzing log files to identify errors, exceptions, performance issues, and security events.

- Target Users:  
    + System Administrators, Developers, IT Professionals, Data Analysts, and Security Analysts.

---

TASKS

1. Receive Log Input:  
    - Validate the input to ensure it follows an acceptable format (e.g., CSV, JSON, text logs).  
    - Check for completeness and any inconsistencies or missing data.

2. Analyze Logs:  
    - Parse the provided log data and extract key information such as:  
        * Timestamp  
        * Log levels (Error, Warning, Info, Debug)  
        * Error/Exception codes and messages  
        * Performance metrics (e.g., latency, response times)  
        * User IDs or system identifiers (if applicable)  
    - Identify issues in the logs, including:  
        * Errors  
        * Warnings  
        * Exceptions  
        * Unusual patterns (e.g., spikes in errors or performance issues)  
    - Use appropriate algorithms or machine learning models to detect anomalies, trends, and outliers.

3. Provide Feedback:  
    - List identified issues with the following details:  
        * Issue Type (e.g., Error, Warning, Exception)  
        * Timestamp of occurrence  
        * Description of the issue (e.g., “Database connection timeout”)  
        * Suggested Remedial Actions (e.g., “Check database server connectivity”, “Increase timeout threshold”)  
    - For errors or exceptions, suggest common causes and solutions based on known patterns.

4. Search Functionality:  
    - Allow users to search for specific terms, patterns, or event types (e.g., search by error codes, keywords).  
    - Provide contextual information about search results, including the occurrence of the term and its relevance to potential issues.

5. Insights and Recommendations:  
    - Offer insights based on the analyzed log data trends, such as:  
        * Frequent occurrences of a specific error or exception type.  
        * Possible recurring performance issues (e.g., high response times or system crashes).  
    - Suggest **best practices** for log management and monitoring:  
        * Frequency of log review.  
        * Optimal log rotation and retention strategies.  
        * Error categorization and notification mechanisms.

6. Follow-up Interaction:  
    - Ask if the user needs further assistance with specific logs or issues.  
    - Offer to analyze additional logs or logs in different formats (e.g., JSON, XML, CSV).  
    - Provide the option to narrow down the analysis based on specific timeframes, error types, or systems.

7. Learning Resources:  
    - Provide links to documentation on:  
        * Log analysis best practices.  
        * Common error explanations and troubleshooting steps.  
        * Recommended tools and software for log management and analysis.

---

Context for Log Snippet:  
{context}

---

Question:  
{question}

---

Output:  
- Analyze the context provided in the log snippet to provide targeted feedback, insights, and suggestions based on the user’s query.
"""

PROMPT_TEMPLATE_V3 = """
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

4. Expected Ideal Flow (Happy Path):  
   <If applicable, describe a scenario from the logs where the process worked as expected.>

5. Remediation:  
   <Based on the identified issue or happy path scenario, suggest possible remediation steps to resolve the problem.>

Below are the contexts for you to refer:  
{context}

Below is the query for you to answer:  
{query}
"""



# Initialize conversation history
chain_of_thought = []

def main():
    # Prepare the DB.
    embedding_function = HuggingFaceEmbeddings(model_name="Snowflake/snowflake-arctic-embed-m-long",
                                               model_kwargs={'trust_remote_code': True})
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    retriever = db.as_retriever(
        search_type="mmr",  # Max marginal relevance
        search_kwargs={
            'k': 7,  # Final results
            'fetch_k': 20,  # Initial candidate pool
            'lambda_mult': 0.65,  # 65% relevance, 35% diversity
            'score_threshold': 0.6  # Minimum relevance floor
        }
    )

    prompt = PromptTemplate.from_template(PROMPT_TEMPLATE_V3)
    llm = HuggingFaceEndpoint(
        repo_id="mistralai/Mistral-7B-Instruct-v0.2",
        max_length=128,
        max_new_tokens=512,
        top_k=10,
        top_p=0.95,
        typical_p=0.95,
        temperature=0.01,
        repetition_penalty=1.03
    )

    # Start a continuous conversation loop.
    print("Starting the Log Analyser Chatbot! Type 'exit' to end the conversation.")

    while True:
        query_text = input("You: ")
        if query_text.lower() == 'exit':
            print("Goodbye!")
            break

        # Add user query to conversation history
        chain_of_thought.append({"question": "\n\n" + query_text})

        # Using the 'invoke' method instead of 'get_relevant_documents'
        results = retriever.invoke(query_text)
        context_text = "\n\n---\n\n".join([doc.page_content for doc in results])

        # Create the conversation history text
        # conversation_history_text = "\n".join([f'{entry["role"]}: {entry["content"]}' for entry in conversation_history])

        # Update the prompt with conversation history
        llm_chain = prompt | llm
        response_text = llm_chain.invoke({
            "context": context_text,
            "query": query_text,
            # "conversation_history": conversation_history_text
        })

        # Add bot response to conversation history
        chain_of_thought.append({"role": "bot", "content": response_text})

        print("\nBot:", response_text, "\n")


if __name__ == "__main__":
    main()