from typing import List
from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage
from src.core.interfaces.llm import LLMInterface

class OllamaLLM(LLMInterface):
    def __init__(self, model_name: str, temperature: float = 0.7):
        self.model_name = model_name
        self.client = ChatOllama(model=model_name, temperature=temperature)

    async def invoke(self, messages: List[BaseMessage]) -> str:
        response = await self.client.ainvoke(messages)
        return response.content

    def get_model_name(self) -> str:
        return self.model_name
