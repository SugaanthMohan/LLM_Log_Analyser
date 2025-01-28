from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from sentence_transformers import util
import os


def main():

    word1, word2 = "apple", "orange"

    # Get embedding for a word.
    embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    vector = embedding_function.embed_query(word1)
    print(f"Vector for '{word1}': {vector}")
    print(f"Vector length: {len(vector)}")

    #  Compute cosine similarity
    vector2 = embedding_function.embed_query(word2)
    print(f"Vector for '{word2}': {vector2}")
    print(f"Vector length: {len(vector2)}")
    cosine_similarity = util.cos_sim(vector, vector2)

    print(f"Cosine Similarity between '{word1}' and '{word2}': {cosine_similarity.item():.4f}")


if __name__ == "__main__":
    main()
