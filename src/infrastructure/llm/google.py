from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage
from src.core.interfaces.llm import LLMInterface

class GoogleLLM(LLMInterface):
    def __init__(self, model_name: str, api_key: str):
        self.model_name = model_name
        self.client = ChatGoogleGenerativeAI(model=model_name, api_key=api_key)

    async def invoke(self, messages: List[BaseMessage]) -> str:
        response = await self.client.ainvoke(messages)
        return response.content

    def get_model_name(self) -> str:
        return self.model_name
