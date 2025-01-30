import argparse
import os
from langchain_chroma import Chroma
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEndpoint   
from dotenv import load_dotenv
from langchain.retrievers.self_query.base import SelfQueryRetriever

import attribute_info

load_dotenv()

hf_token = os.getenv("HF_TOKEN")
os.environ["HUGGINGFACEHUB_API_TOKEN"] = hf_token


CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
[ROLE] Professional Software Logs Analyser
[TASK] Based on the provided context of log snippets, you are to answer the query provided in a
more concise manner explaining the discrepancy, cause and steps to remediation. 

If you find a related scenario in the context without any error/issues, consider that as the happy path scenario 
and you should provide it back in the response as shown in the result format below

Formulate your response as below:

Summary:
<Summary of the issue at high level>

Provide a detailed report as below (if the field doesn't exist then ignore and add all possible information 
about the entry with the help of log's metadata):
Incident Report:
Time: <Timestamp>
Faced By: <Customer/Teller/User Id>
Trace Id: <TraceID/SessionID>
Application: <AppID>
Component: <Component>
... <Additional key - value pairs if it exists in the metadata>

Explanation: 
<Detailed explanation of the root cause of the issue>

Expected Ideal Flow (only if you are able to figure it in the context): 
<Happy Path Log Snippet>

Remediation: 
<Based on the context/happy path scenario, provide what could be the possible remediation steps>

Below are the contexts for you to refer:

{context}

Below is the query for you to answer:

{QUERY}

"""


def main():
    # Create CLI.
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    query_text = args.query_text

    # Prepare the DB.
    embedding_function = HuggingFaceEmbeddings(model_name="Snowflake/snowflake-arctic-embed-m-long", model_kwargs={'trust_remote_code': True})
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    
    metadata_field_info = attribute_info.get_attribute_info()

    document_content_description = "Log snippets of an enterprise software application"
    
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


    retriever = SelfQueryRetriever.from_llm(
        llm, db, document_content_description, metadata_field_info, verbose=True,
        enable_limit=True,
        search_kwargs={"k": 20}
    )

    results = retriever.get_relevant_documents(query_text)
    
    context_text = "\n\n---\n\n".join([doc.page_content for doc in results])

    prompt = PromptTemplate.from_template(PROMPT_TEMPLATE)

    llm_chain = prompt | llm
    response_text = llm_chain.invoke({"context": context_text, "question": query_text})
    print("\n\n\nResponse:", response_text)


if __name__ == "__main__":
    main()
