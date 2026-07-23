import os
import numpy as np

from dotenv import load_dotenv
from openai import OpenAI

from config import (
    OPENAI_PROVIDER,
    OLLAMA_PROVIDER,
    OPENAI_EMBEDDING_MODEL,
    LOCAL_EMBEDDING_MODEL,
)

load_dotenv()

_openai_client = None
_local_embedding_model = None


def get_embedding_dimension(provider):
    if provider == OPENAI_PROVIDER:
        return 1536

    if provider == OLLAMA_PROVIDER:
        return 384

    raise ValueError(f"Unsupported provider: {provider}")


def get_openai_client():
    global _openai_client

    if _openai_client is None:

        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "OpenAI embeddings require an OPENAI_API_KEY."
            )

        _openai_client = OpenAI(
            api_key=api_key
        )

    return _openai_client


def get_local_embedding_model():
    global _local_embedding_model

    if _local_embedding_model is None:

        from sentence_transformers import SentenceTransformer

        _local_embedding_model = SentenceTransformer(
            LOCAL_EMBEDDING_MODEL
        )

    return _local_embedding_model


def embed_text(text, provider):

    if provider == OPENAI_PROVIDER:

        client = get_openai_client()

        response = client.embeddings.create(
            model=OPENAI_EMBEDDING_MODEL,
            input=text
        )

        return np.array(
            response.data[0].embedding,
            dtype="float32"
        )

    if provider == OLLAMA_PROVIDER:

        model = get_local_embedding_model()

        embedding = model.encode(
            text,
            normalize_embeddings=True
        )

        return np.array(
            embedding,
            dtype="float32"
        )

    raise ValueError(f"Unsupported provider: {provider}")


def embed_texts(texts, provider):

    if provider == OPENAI_PROVIDER:

        client = get_openai_client()

        response = client.embeddings.create(
            model=OPENAI_EMBEDDING_MODEL,
            input=texts
        )

        return [
            np.array(item.embedding, dtype="float32")
            for item in response.data
        ]

    if provider == OLLAMA_PROVIDER:

        model = get_local_embedding_model()

        embeddings = model.encode(
            texts,
            normalize_embeddings=True
        )

        return [
            np.array(embedding, dtype="float32")
            for embedding in embeddings
        ]

    raise ValueError(f"Unsupported provider: {provider}")
