from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import TokenTextSplitter, RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_chroma import Chroma
from langchain_huggingface.embeddings import HuggingFaceEmbeddings

import os
import shutil
import json


import parse_documents
import extract_metadata

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
    parse_documents.process_all_log_files(DATA_PATH)
    loader = DirectoryLoader(DATA_PATH, glob="*.log")
    documents = loader.load()
    return documents


def split_text(documents: list[Document]):

    # First split by log entries
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["|||"],  # Split on the delimiter we added
        chunk_size=100,      # Larger than the biggest log entry
        chunk_overlap=0,
        keep_separator=False, # Remove '|||' from the output
    )

    final_chunks = text_splitter.split_documents(documents)

    log_snippets = '\n'.join([extract_metadata.extract_metadata_snippet(chunk.page_content) for chunk in final_chunks[:10]])

    metadata_keys = extract_metadata.get_metadata(log_snippets)
    
    # Create dictionary mapping metadata fields to values
    for chunk in final_chunks:
        metadata_snippet = extract_metadata.extract_metadata_snippet(chunk.page_content)
        metadata = metadata_snippet.split('|') 
        metadata_dict = dict(zip(metadata_keys[:6], metadata[:6]))
        metadata_dict = {'APP_ID': APP_ID, **metadata_dict}
        
        for key in ['Timestamp', 'Date', 'Datetime']:  # List of potential keys
            if key in metadata_dict.keys():
                timestamp_str = metadata_dict[key]
                timestamp = parse_documents.parse_unix_epoch_timestamp(timestamp_str)
                metadata_dict[key] = timestamp

        chunk.metadata = metadata_dict
    #     print(chunk)
    #     print("\n~~~~\n")
    # exit()

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
