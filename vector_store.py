import os
import json
import hashlib

import faiss
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CACHE_DIR = "outputs/cache/embeddings"
os.makedirs(CACHE_DIR, exist_ok=True)


class VectorStore:
    """
    FAISS vector store with batched OpenAI embeddings and local caching.
    """

    def __init__(self):
        self.dimension = 1536
        self.index = faiss.IndexFlatIP(self.dimension)
        self.chunks = []

    def _cache_path(self, text):
        key = hashlib.md5(text.encode("utf-8")).hexdigest()
        return os.path.join(CACHE_DIR, f"{key}.json")

    def get_embedding(self, text):
        cache_path = self._cache_path(text)

        if os.path.exists(cache_path):
            with open(cache_path, "r", encoding="utf-8") as file:
                return np.array(json.load(file), dtype="float32")

        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )

        embedding = response.data[0].embedding

        with open(cache_path, "w", encoding="utf-8") as file:
            json.dump(embedding, file)

        return np.array(embedding, dtype="float32")

    def get_embeddings_batch(self, texts):
        embeddings = []
        uncached_texts = []
        uncached_indices = []

        for index, text in enumerate(texts):
            cache_path = self._cache_path(text)

            if os.path.exists(cache_path):
                with open(cache_path, "r", encoding="utf-8") as file:
                    embeddings.append(np.array(json.load(file), dtype="float32"))
            else:
                embeddings.append(None)
                uncached_texts.append(text)
                uncached_indices.append(index)

        if uncached_texts:
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=uncached_texts
            )

            for response_item, original_index, text in zip(
                response.data,
                uncached_indices,
                uncached_texts
            ):
                embedding = response_item.embedding
                embeddings[original_index] = np.array(embedding, dtype="float32")

                cache_path = self._cache_path(text)

                with open(cache_path, "w", encoding="utf-8") as file:
                    json.dump(embedding, file)

        return embeddings

    def add_chunks(self, chunks):
        if not chunks:
            return

        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.get_embeddings_batch(texts)

        embeddings_matrix = np.vstack(embeddings).astype("float32")
        faiss.normalize_L2(embeddings_matrix)

        self.index.add(embeddings_matrix)
        self.chunks.extend(chunks)

    def search(self, query, k=5):
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
