try:
    from fastapi import FastAPI, Request  # type: ignore[import]
except Exception:  # pragma: no cover - fallback for editor/linting environments without FastAPI
    # Provide lightweight fallbacks so linters/editors won't show import errors
    from typing import Any

    class Request:  # simple stub
        pass

    class FastAPI:  # minimal stub with decorator behavior used in this file
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        def post(self, *args: Any, **kwargs: Any):
            def decorator(func):
                return func

            return decorator
from typing import Any
from pydantic import BaseModel

from openai import OpenAI
from groq import Groq
from google import genai

from api.core.config import config

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def _messages_to_google_prompt(messages: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for message in messages or []:
        role = str(message.get("role", "user")).lower()
        content = str(message.get("content", ""))
        if role == "assistant":
            parts.append(f"Assistant: {content}")
        elif role == "system":
            parts.append(f"System: {content}")
        else:
            parts.append(f"User: {content}")
    return "\n".join(parts)


def run_llm(provider, model_name, messages, max_tokens=500):
    print(f"Provider: {provider}")
    
    if provider == "OpenAI":
        client = OpenAI(api_key=config.OPENAI_API_KEY)
        return client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_completion_tokens=max_tokens,
            reasoning_effort="low"
        ).choices[0].message.content
    elif provider == "Groq":
        client = Groq(api_key=config.GROQ_API_KEY)
        return client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_completion_tokens=max_tokens
        ).choices[0].message.content
    elif provider == "Google":
        client: Any = genai.Client(api_key=config.GOOGLE_API_KEY)
        response = client.models.generate_content(
            model=model_name,
            contents=_messages_to_google_prompt(messages),
            config={"maxOutputTokens": max_tokens},
        )
        return getattr(response, "text", None) or ""

    raise ValueError(f"Unsupported provider: {provider}")


class ChatRequest(BaseModel):
    provider: str
    model_name: str | None = None
    models_name: str | None = None
    messages: list[dict]

class ChatResponse(BaseModel):
    message: str


app = FastAPI()

@app.post("/chat")
def chat(
    request: Request,
    payload: ChatRequest
) -> ChatResponse:

    model_name = payload.model_name or payload.models_name or ""
    try:
        result = run_llm(payload.provider, model_name, payload.messages)
    except Exception as exc:
        logger.exception("LLM request failed")
        return ChatResponse(message=f"Error: {exc}")

    return ChatResponse(message=result)