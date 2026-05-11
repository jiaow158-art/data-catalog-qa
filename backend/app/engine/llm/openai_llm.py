"""OpenAI LLM adapter."""

from __future__ import annotations

from app.engine.llm.base import BaseLLM
from app.core.config import settings
from app.core.llm_config import get_llm_config


class OpenAILLM(BaseLLM):
    """OpenAI-compatible LLM adapter. Supports custom base_url for proxies and local models."""

    def __init__(self) -> None:
        # Runtime config takes precedence over env-file settings
        runtime = get_llm_config()
        self.api_key = runtime.get("api_key") or settings.LLM_API_KEY
        self.base_url = runtime.get("base_url") or settings.LLM_BASE_URL or None
        self.model = runtime.get("model") or settings.LLM_MODEL
        self.temperature = settings.LLM_TEMPERATURE
        self.max_tokens = settings.LLM_MAX_TOKENS

    def generate(self, system_prompt: str, user_prompt: str, max_tokens: int = 1024) -> str:
        try:
            from openai import OpenAI
        except ImportError:
            return ""

        if not self.api_key or self.api_key == "sk-xxx":
            return ""

        try:
            kwargs = {"api_key": self.api_key}
            if self.base_url:
                kwargs["base_url"] = self.base_url
            client = OpenAI(**kwargs)
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=max_tokens or self.max_tokens,
                temperature=self.temperature,
            )
            return response.choices[0].message.content or ""
        except Exception:
            return ""
