import os
import sys
import warnings
from langchain_chroma import Chroma
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEndpoint
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
from backend import analyzer
from backend import extract_snippets
from backend import parse_documents


# Suppress all warnings
warnings.filterwarnings("ignore")

load_dotenv()

hf_token = os.getenv("HF_TOKEN")
os.environ["HUGGINGFACEHUB_API_TOKEN"] = hf_token


def init(APP_ID):
   llm = HuggingFaceEndpoint(
      repo_id="mistralai/Mistral-7B-Instruct-v0.2", 
      max_new_tokens=1024,
      top_k=10,
      top_p=0.95,
      typical_p=0.95,
      temperature=0.01,
      repetition_penalty=1.03
   )

   CHROMA_PATH = f"chroma/{APP_ID}"
   embedding_function = HuggingFaceEmbeddings(model_name="Snowflake/snowflake-arctic-embed-m-long", \
                                             model_kwargs={'trust_remote_code': True})
   db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

   return llm, db


def get_filtered_docs(db, APP_ID, TIME_FROM, TIME_TO):
   docs = db.get(
      where = {
         "$and": [
            {"APP_ID": APP_ID},  # Exact match for APP_ID
            {"Timestamp": {"$gte": TIME_FROM}},  # Greater than or equal to
            {"Timestamp": {"$lte": TIME_TO}}   # Less than or equal to
        ]
      }
   )
   return docs


def analyse(APP_ID, TIME_FROM, TIME_TO, QUERY):
   # output = {
   #    "RawLogs": "raw",
   #    "Summary": "summary",
   #    "Report": "report",
   #    "Explanation": "explanation",
   #    "ExpectedFlow": "expected_flow",
   #    "Remediation": "remediation",
   #    "HappyPath": "happy_path_snippet"
   # }
   # return output

   llm, db = init(APP_ID)

   # log_entry_count = get_filtered_docs(db, APP_ID, TIME_FROM, TIME_TO)

   results = analyzer.get_relevant_docs(db, llm, APP_ID, TIME_FROM, TIME_TO, QUERY)
   error_snippet = extract_snippets.error_flow(llm, QUERY, results)

   analysis = analyzer.analyze_without_metadata(llm, QUERY, results, error_snippet)
   summary, report, explanation, expected_flow, remediation = parse_documents.parse_response(analysis)


   happy_path_snippet = extract_snippets.success_flow(llm, QUERY, results, analysis)

   print(analysis)
   print("\n\n")
   print(error_snippet)
   print("\n\n")
   print(happy_path_snippet)
   print("\n\n")


   output = {
      "RawLogs": error_snippet,
      "Summary": summary,
      "Report": report,
      "Explanation": explanation,
      "ExpectedFlow": expected_flow,
      "Remediation": remediation,
      "HappyPath": happy_path_snippet
   }

   
   import pprint
   pprint.pprint(output)

   return output

if __name__ == "__main__":
   # APP_ID = input("APP ID: ")
   # TIME_FROM = input("TIME FROM: ")
   # TIME_TO = input("TIME TO: ")
   # QUERY = input("QUERY: ") 

   # filtered_docs = get_filtered_docs('APP_3', 1718445912345, 1718447418123)
   # print(f"\n\nAnalysing {len(filtered_docs['ids'])} log entries...\n\n")
   
   # First usecase - to summarise in plain English about the problem noticed 
   # try:
   #    analysis = analyzer.analyze_with_metadata(db, llm, APP_ID, TIME_FROM, TIME_TO, QUERY)
   #    print("\n\nBelow is my analysis with metadata usage based on your query")
   #    print(analysis)
   #    raise RuntimeError
   # except:
   # results, analysis = analyzer.analyze_without_metadata(db, llm, APP_ID, TIME_FROM, TIME_TO, QUERY)
   # print("Below is my analysis without metadata usage based on your query")
   # print(analysis)

   # Second usecase - to extract the error log snippets and happy path log snippets

   # error_snippet = extract_snippets.error_flow(llm, QUERY, results)
   # happy_path_snippet = extract_snippets.success_flow(llm, QUERY, results)

   # print("\nError snippet: \n")
   # print(error_snippet)

   # print("\nHappy Path snippet: \n")
   # print(happy_path_snippet)

   QUERY = "List the app dependencies and REST or SOAP endpoints "
   analyse('APP_4', '2025-02-01T00:39', '2025-02-01T21:40', QUERY)
