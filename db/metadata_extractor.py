from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEndpoint
import re

from rag.prompts import METADATA_EXTRACTOR_PROMPT

def get_metadatas(log_snippet):
    log_snippet = log_snippet.replace('[', '')
    log_snippet = log_snippet.replace(' ]', '')
    log_snippet = log_snippet.replace(']', '')
    metadatas = log_snippet.split(' ')
    return " | ".join(metadatas[:6])

def extract_keys(log_snippet, llm):
    
    prompt = PromptTemplate.from_template(METADATA_EXTRACTOR_PROMPT)

    llm_chain = prompt | llm
    response_text = llm_chain.invoke({"log_snippet": log_snippet})
    metadata_list = re.findall(r"\d+\.\s*(.+)", response_text.content)
    return metadata_list
