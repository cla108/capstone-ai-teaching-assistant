import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_PROVIDER = "OpenAI"
OLLAMA_PROVIDER = "Ollama"

OPENAI_GENERATION_MODEL = "gpt-5.5"
OPENAI_EVALUATION_MODEL = "gpt-4o-mini"
OPENAI_REWRITE_MODEL = "gpt-5.5"
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"

OLLAMA_MODELS = {
    "Llama 3.2 (3B)": "llama3.2:3b",
    "Qwen 2.5 (7B)": "qwen2.5:7b",
}

DEFAULT_OLLAMA_MODEL_LABEL = "Llama 3.2 (3B)"
DEFAULT_OLLAMA_MODEL = OLLAMA_MODELS[DEFAULT_OLLAMA_MODEL_LABEL]

LOCAL_EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

DEFAULT_PROVIDER = os.getenv("MODEL_PROVIDER", OPENAI_PROVIDER)
