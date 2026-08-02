import os
import json
import hashlib

import faiss
import numpy as np

from config import OPENAI_PROVIDER
from ai.embeddings import (
    embed_text,
    embed_texts,
    get_embedding_dimension,
)


CACHE_DIR = "outputs/cache/embeddings"
os.makedirs(CACHE_DIR, exist_ok=True)


class VectorStore:
    """
    FAISS vector store with provider-based embeddings.

    Retrieval can be restricted to one chapter through chunk metadata.
    """

    def __init__(self, provider=OPENAI_PROVIDER):
        self.provider = provider
        self.dimension = get_embedding_dimension(provider)
        self.index = faiss.IndexFlatIP(self.dimension)
        self.chunks = []

    def _cache_path(self, text):
        key_source = f"{self.provider}_{text}"
        key = hashlib.md5(key_source.encode("utf-8")).hexdigest()
        return os.path.join(CACHE_DIR, f"{key}.json")

    def get_embedding(self, text):
        cache_path = self._cache_path(text)

        if os.path.exists(cache_path):
            with open(cache_path, "r", encoding="utf-8") as file:
                return np.array(
                    json.load(file),
                    dtype="float32",
                )

        embedding = embed_text(text, self.provider)

        with open(cache_path, "w", encoding="utf-8") as file:
            json.dump(embedding.tolist(), file)

        return embedding

    def get_embeddings_batch(self, texts):
        embeddings = []
        uncached_texts = []
        uncached_indices = []

        for index, text in enumerate(texts):
            cache_path = self._cache_path(text)

            if os.path.exists(cache_path):
                with open(cache_path, "r", encoding="utf-8") as file:
                    embeddings.append(
                        np.array(
                            json.load(file),
                            dtype="float32",
                        )
                    )
            else:
                embeddings.append(None)
                uncached_texts.append(text)
                uncached_indices.append(index)

        if uncached_texts:
            new_embeddings = embed_texts(
                uncached_texts,
                self.provider
            )

            for embedding, original_index, text in zip(
                new_embeddings,
                uncached_indices,
                uncached_texts
            ):
                embeddings[original_index] = embedding

                cache_path = self._cache_path(text)

                with open(cache_path, "w", encoding="utf-8") as file:
                    json.dump(embedding.tolist(), file)

        return embeddings

    def add_chunks(self, chunks):
        if not chunks:
            return

        for chunk in chunks:
            if "chapter_number" not in chunk:
                raise ValueError(
                    "Every vector-store chunk must contain "
                    "'chapter_number' metadata."
                )

        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.get_embeddings_batch(texts)

        embeddings_matrix = np.vstack(
            embeddings
        ).astype("float32")

        faiss.normalize_L2(embeddings_matrix)

        self.index.add(embeddings_matrix)
        self.chunks.extend(chunks)

    def search(
        self,
        query,
        k=5,
        *,
        chapter_number=None,
    ):
        """
        Search for relevant chunks.

        When chapter_number is supplied, results from every other chapter are
        removed before returning the top-k chunks.
        """

        if k <= 0 or self.index.ntotal == 0:
            return []

        query_embedding = self.get_embedding(query)
        query_matrix = np.array(
            [query_embedding],
            dtype="float32",
        )

        faiss.normalize_L2(query_matrix)

        if chapter_number is None:
            search_k = min(k, self.index.ntotal)
        else:
            search_k = self.index.ntotal

        scores, indices = self.index.search(
            query_matrix,
            search_k,
        )

        required_chapter = (
            None
            if chapter_number is None
            else str(chapter_number).strip().casefold()
        )

        results = []

        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue

            result = self.chunks[idx].copy()

            if required_chapter is not None:
                result_chapter = str(
                    result.get("chapter_number", "")
                ).strip().casefold()

                if result_chapter != required_chapter:
                    continue

            result["similarity_score"] = float(score)
            results.append(result)

            if len(results) >= k:
                break

        return results
