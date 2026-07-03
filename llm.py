import os

from dotenv import load_dotenv
from openai import OpenAI

from config import (
    OPENAI_PROVIDER,
    OLLAMA_PROVIDER,
    OPENAI_GENERATION_MODEL,
    OPENAI_EVALUATION_MODEL,
    OPENAI_REWRITE_MODEL,
    DEFAULT_OLLAMA_MODEL,
)

load_dotenv()

_openai_client = None
_ollama_client = None


def get_client(provider):

    global _openai_client
    global _ollama_client

    if provider == OPENAI_PROVIDER:

        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "OpenAI mode requires an OPENAI_API_KEY.\n"
                "Either add one to your .env file or switch to Ollama mode."
            )

        if _openai_client is None:

            _openai_client = OpenAI(
                api_key=api_key
            )

        return _openai_client

    if provider == OLLAMA_PROVIDER:

        if _ollama_client is None:

            _ollama_client = OpenAI(
                base_url="http://localhost:11434/v1",
                api_key="ollama"
            )

        return _ollama_client

    raise ValueError(f"Unsupported provider: {provider}")


def get_model(provider, task, ollama_model=None):

    if provider == OPENAI_PROVIDER:

        if task == "generation":
            return OPENAI_GENERATION_MODEL

        if task == "evaluation":
            return OPENAI_EVALUATION_MODEL

        if task == "rewrite":
            return OPENAI_REWRITE_MODEL

    if provider == OLLAMA_PROVIDER:

        return ollama_model or DEFAULT_OLLAMA_MODEL

    raise ValueError(f"Unsupported provider/task: {provider}, {task}")


def chat_completion(
    provider,
    task,
    system_prompt,
    user_prompt,
    ollama_model=None,
    temperature=None
):

    client = get_client(provider)

    model = get_model(
        provider,
        task,
        ollama_model
    )

    kwargs = {

        "model": model,

        "messages": [

            {
                "role": "system",
                "content": system_prompt
            },

            {
                "role": "user",
                "content": user_prompt
            }

        ]

    }

    # GPT-5.5 ignores temperature in the Chat Completions API.
    # Apply temperature only to Ollama models.

    if (
        provider == OLLAMA_PROVIDER
        and temperature is not None
    ):
        kwargs["temperature"] = temperature

    response = client.chat.completions.create(
        **kwargs
    )

    return response.choices[0].message.content
