from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import TokenTextSplitter, RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_chroma import Chroma
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEndpoint

import os
import shutil
import re
import json

APP_ID = 'APP_3'

CHROMA_PATH = "chroma"
DATA_PATH = f"data/logs/{APP_ID}"


def main():
    generate_data_store()


def generate_data_store():
    documents = load_documents()
    chunks = split_text(documents)
    save_to_chroma(chunks)


def load_documents():
    loader = DirectoryLoader(DATA_PATH, glob="*.log")
    documents = loader.load()
    return documents

def extract_metadata_snippet(log_snippet):
    metadatas = log_snippet.split()
    return " | ".join(metadatas[:6])

def get_metadata(log_snippet):
    
    PROMPT_TEMPLATE = '''
        Look for the below log snippets and suggest some suitable keyword names for
        the metadata fields in the rows of the logs. When I say metadata, I only refer to
        the first five to six words of each row used to identify rows separately.
        So only look for the starting six words in each line and not beyond. As they 
        have a common syntax for starting of each line, carefully analyse 
        what could the metadata that represents each row. Based on your analysis, 
        list down names of metadata for first six fields one after the other as requested later.

        Log snippet for your reference:
        {log_snippet}

        List them one after another as shown below.
        Strictly restrict down your response format as below and your response SHOULDN'T
        EXCEED 7 LINES. Give a generic key name to represent each field.

        Response Format:
        Below are the metadata fields:
        1. key1
        2. key2
        3. key3
        4. key4
        5. key5
        6. key6
        (Order of listing should be same as order in which words appear in each row)
        End of Response.

    '''

    prompt = PromptTemplate.from_template(PROMPT_TEMPLATE)
     
    llm = HuggingFaceEndpoint(
        repo_id="mistralai/Mistral-7B-Instruct-v0.2", 
        max_new_tokens=512,
        top_k=10,
        top_p=0.95,
        typical_p=0.95,
        temperature=0.01,
        repetition_penalty=1.03
    )

    llm_chain = prompt | llm
    response_text = llm_chain.invoke({"log_snippet": log_snippet})

    # Extract only text after numbering (handles different spacings)
    metadata_list = re.findall(r"\d+\.\s*(.+)", response_text)

    return metadata_list


def split_text(documents: list[Document]):
    # First split by log entries
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n"],  # Split on log entry boundaries
        chunk_size=350,
        chunk_overlap=30
    )
    
    # Then process with token splitter
    # token_splitter = TokenTextSplitter(
    #     chunk_size=500,
    #     chunk_overlap=300
    # )
    
    final_chunks = text_splitter.split_documents(documents)
    # final_chunks = token_splitter.split_documents(initial_chunks)
    # for chunk in final_chunks:
    #     print(chunk.page_content)
    # exit()

    log_snippets = '\n'.join([extract_metadata_snippet(chunk.page_content) for chunk in final_chunks[:10]])

    metadata_keys = get_metadata(log_snippets)
    
    # Create dictionary mapping metadata fields to values
    for chunk in final_chunks:
        metadata_snippet = extract_metadata_snippet(chunk.page_content)
        metadata = metadata_snippet.split('|') 
        metadata_dict = dict(zip(metadata_keys[:5], metadata[:5]))
        metadata_dict = {'APP_ID': APP_ID, **metadata_dict}
        chunk.metadata = metadata_dict

    with open(f'{DATA_PATH}/chunks-metadata.json', 'w') as file:
        json.dump(final_chunks[0].metadata, file, indent=4) 
    
    return final_chunks


def save_to_chroma(chunks: list[Document]):
    # Clear out the database first.
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    # Create a new DB from the documents.
    db = Chroma.from_documents(
        chunks, HuggingFaceEmbeddings(model_name="Snowflake/snowflake-arctic-embed-m-long", model_kwargs={'trust_remote_code': True}), persist_directory=CHROMA_PATH
    )
    print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}.")


if __name__ == "__main__":
    main()
