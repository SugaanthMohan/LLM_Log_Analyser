from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer
from sentence_transformers import util


def main():

    word1, word2 = "apple fruit", "apple iphone"

    # Get embedding for a word.
    embedding_function = HuggingFaceEmbeddings(model_name="Snowflake/snowflake-arctic-embed-m-long", model_kwargs={'trust_remote_code': True})
    vector = embedding_function.embed_query(word1)
    print(f"Vector length: {len(vector)}")

    #  Compute cosine similarity
    vector2 = embedding_function.embed_query(word2)
    print(f"Vector length: {len(vector2)}")
    cosine_similarity = util.cos_sim(vector, vector2)

    print(f"Cosine Similarity between '{word1}' and '{word2}': {cosine_similarity.item():.4f}")


if __name__ == "__main__":
    main()
