import os
import sys
import warnings
import json
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
   TIME_FROM = int(parse_documents.parse_unix_epoch_timestamp(TIME_FROM))
   TIME_TO = int(parse_documents.parse_unix_epoch_timestamp(TIME_TO))

   docs = db.get(
      where = {
         "$and": [
            {"APP_ID": APP_ID},  # Exact match for APP_ID
            {"Timestamp": {"$gte": TIME_FROM}},  # Greater than or equal to
            {"Timestamp": {"$lte": TIME_TO}}   # Less than or equal to
        ]
      }
   )

   count = len(docs['documents'])
   return count


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

   log_entry_count = get_filtered_docs(db, APP_ID, TIME_FROM, TIME_TO)
   print(log_entry_count)

   results = analyzer.get_relevant_docs(db, llm, APP_ID, TIME_FROM, TIME_TO, QUERY)

   error_snippet = extract_snippets.error_flow(llm, QUERY, results)
   print(error_snippet)
   print("\n\n")

   analysis = analyzer.analyze_without_metadata(llm, QUERY, results, error_snippet)
   summary, report, explanation, expected_flow, remediation = parse_documents.parse_response(analysis)

   # summary = f"<i>Analyzed {log_entry_count} log snippets...<i>\n\n" + summary
   print(analysis)
   print("\n\n")


   happy_path_snippet = extract_snippets.success_flow(llm, QUERY, results, analysis)
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

   with open('output.json', 'w') as f:
      json.dump(output, f, indent=4)

   return output

if __name__ == "__main__":
   QUERY = "List the REST or SOAP URL endpoints application is communicating to"
   analyse('APP_4', '2025-02-01T00:39', '2025-02-05T21:40', QUERY)
