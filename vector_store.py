import os

import faiss
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class VectorStore:
    """
    Simple FAISS-based vector store for textbook chunks.
    """

    def __init__(self):
        self.dimension = 1536
        self.index = faiss.IndexFlatIP(self.dimension)
        self.chunks = []

    def get_embedding(self, text):
        """
        Converts text into an embedding vector using OpenAI.
        """

        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )

        embedding = response.data[0].embedding

        return np.array(embedding, dtype="float32")

    def add_chunks(self, chunks):
        """
        Embeds and stores textbook chunks.
        """

        embeddings = []

        for chunk in chunks:
            embedding = self.get_embedding(chunk["text"])
            embeddings.append(embedding)
            self.chunks.append(chunk)

        embeddings_matrix = np.vstack(embeddings)

        faiss.normalize_L2(embeddings_matrix)

        self.index.add(embeddings_matrix)

    def search(self, query, k=5):
        """
        Retrieves the top-k most relevant chunks for a query.
        """

        query_embedding = self.get_embedding(query)
        query_matrix = np.array([query_embedding], dtype="float32")

        faiss.normalize_L2(query_matrix)

        scores, indices = self.index.search(query_matrix, k)

        results = []

        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue

            result = self.chunks[idx].copy()
            result["similarity_score"] = float(score)
            results.append(result)

        return results
