import argparse
import os
from langchain_chroma import Chroma
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEndpoint   
from dotenv import load_dotenv

load_dotenv()

hf_token = os.getenv("HF_TOKEN")
os.environ["HUGGINGFACEHUB_API_TOKEN"] = hf_token


CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
[ROLE] Log Analysis Engineer
[TASK] Analyze error patterns and identify happy path deviations

[CONTEXT]
{context}

[ANALYSIS FRAMEWORK]
1. Error Pattern Identification
2. Temporal Analysis (error frequency)
3. Dependency Mapping
4. Happy Path Deviation Points

[OUTPUT FORMAT]
**Summary**: <concise problem statement>
**Root Cause**: <primary suspect>
**Happy Path Flow**: <ideal sequence>
**Recommendations**: <actionable items>
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
    
    retriever = db.as_retriever(
        search_type="mmr",  # Max marginal relevance
        search_kwargs={
            'k': 7,                   # Final results
            'fetch_k': 20,            # Initial candidate pool
            'lambda_mult': 0.65,      # 65% relevance, 35% diversity
            'score_threshold': 0.6    # Minimum relevance floor
        }
    )

    results = retriever.get_relevant_documents(query_text)
    
    context_text = "\n\n---\n\n".join([doc.page_content for doc in results])

    prompt = PromptTemplate.from_template(PROMPT_TEMPLATE)

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

    llm_chain = prompt | llm
    response_text = llm_chain.invoke({"context": context_text, "question": query_text})
    print("\n\n\nResponse:", response_text)


if __name__ == "__main__":
    main()
