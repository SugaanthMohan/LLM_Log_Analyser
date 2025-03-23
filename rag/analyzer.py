import os
import sys
import warnings
from langchain_chroma import Chroma
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

from rag import parser, extract_snippets
from db import create_database
from rag.prompts import ANALYSER_PROMPT, EMBEDDING_QUERY_PROMPT

warnings.filterwarnings("ignore")
load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
os.environ["GOOGLE_API_KEY"] = gemini_api_key

def init(APP_ID):
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.1,
        top_p=0.95,
        top_k=40,
        max_output_tokens=2048,
    )

    CHROMA_PATH = f"db/chroma/{APP_ID}"
    if not os.path.exists(CHROMA_PATH):
        create_database.create(APP_ID, llm)

    embedding_function = HuggingFaceEmbeddings(model_name="Snowflake/snowflake-arctic-embed-m-long", \
                                                model_kwargs={'trust_remote_code': True})
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    return llm, db

def get_filtered_docs(db, APP_ID, TIME_FROM, TIME_TO):
   TIME_FROM = int(parser.parse_unix_epoch_timestamp(TIME_FROM))
   TIME_TO = int(parser.parse_unix_epoch_timestamp(TIME_TO))
   docs = db.get(
      where = {
         "$and": [
            {"APP_ID": APP_ID},  
            {"timestamp": {"$gte": TIME_FROM}},  
            {"timestamp": {"$lte": TIME_TO}}   
        ]
      }
   )
   return len(docs['documents'])

def get_relevant_docs(db, llm, APP_ID, TIME_FROM, TIME_TO, QUERY):
    TRACE_IDS = re.findall(r"TRACE(\d_)+", QUERY)
    TIME_FROM = int(parser.parse_unix_epoch_timestamp(TIME_FROM))
    TIME_TO = int(parser.parse_unix_epoch_timestamp(TIME_TO))
    
    EMBEDDING_QUERY = PromptTemplate.from_template(EMBEDDING_QUERY_PROMPT).invoke({
        "QUERY": QUERY,
        "TIME_FROM": TIME_FROM,
        "TIME_TO": TIME_TO,
        "TRACE_IDS": TRACE_IDS
    }).content

    search_kwargs = {
        'k': 40,
        'where': {"$and": [{"APP_ID": APP_ID}, {"timestamp": {"$gte": TIME_FROM}}, {"timestamp": {"$lte": TIME_TO}}]}
    }
    
    retriever = db.as_retriever(search_type="mmr", search_kwargs=search_kwargs)
    results = retriever.invoke(EMBEDDING_QUERY)
    return results

def analyse(APP_ID, TIME_FROM, TIME_TO, QUERY):
    llm, db = init(APP_ID)
    log_entry_count = get_filtered_docs(db, APP_ID, TIME_FROM, TIME_TO)

    if log_entry_count < 1:
        return {"message": "No relevant log snippets found. Try a broader time range."}
    
    results = get_relevant_docs(db, llm, APP_ID, TIME_FROM, TIME_TO, QUERY)
    error_snippet = extract_snippets.error_flow(llm, QUERY, results)
    
    analysis = PromptTemplate.from_template(ANALYSER_PROMPT).invoke({
        "context": "\n\n---\n\n".join([doc.page_content for doc in results]),
        "query": QUERY,
        "error_snippet": error_snippet
    }).content
    
    summary, report, explanation, expected_flow, remediation = parser.parse_response(analysis)
    
    return {
        "RawLogs": error_snippet,
        "Summary": summary,
        "IncidentReport": report,
        "Explanation": explanation,
        "ExpectedFlow": expected_flow,
        "Remediation": remediation,
    }

if __name__ == "__main__":
    print(analyse('APP_4', '2025-01-01T00:39', '2025-02-20T21:40', "Identify database errors"))
