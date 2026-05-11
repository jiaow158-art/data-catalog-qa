"""Abstract LLM adapter interface."""

from abc import ABC, abstractmethod


class BaseLLM(ABC):
    """Abstract base for LLM providers."""

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str, max_tokens: int = 1024) -> str:
        """Generate a response from the LLM."""
        ...


class NoOpLLM(BaseLLM):
    """Fallback LLM that returns empty string — used when no API key is configured."""

    def generate(self, system_prompt: str, user_prompt: str, max_tokens: int = 1024) -> str:
        return ""
