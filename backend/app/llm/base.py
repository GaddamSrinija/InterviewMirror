from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    @abstractmethod
    async def chat_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
        tool_choice: str | dict = "auto",
    ) -> dict[str, Any]:
        pass

    @abstractmethod
    async def generate_embedding(self, text: str) -> list[float]:
        pass

    @abstractmethod
    async def chat(self, messages: list[dict]) -> str:
        pass


def get_llm_provider() -> LLMProvider:
    from app.llm.openrouter_provider import OpenRouterProvider
    return OpenRouterProvider()