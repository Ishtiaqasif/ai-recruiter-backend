from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
from src.core.interfaces.llm import LLMInterface

class OpenAILLM(LLMInterface):
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.client = ChatOpenAI(model=model_name)

    async def invoke(self, messages: List[BaseMessage]) -> str:
        response = await self.client.ainvoke(messages)
        return response.content

    def get_model_name(self) -> str:
        return self.model_name
