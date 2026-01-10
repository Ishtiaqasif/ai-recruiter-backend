from typing import List
from langchain_core.prompts import ChatPromptTemplate
from .base import BaseQueryTranslator

class HyDETranslator(BaseQueryTranslator):
    """
    Hypothetical Document Embeddings (HyDE) translator.
    Generates a hypothetical answer to the query to improve retrieval.
    """
    
    def __init__(self, llm):
        self.llm = llm
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("human", """You are an AI recruiter. 
            Write a short, hypothetical paragraph of a CV or an answer that would perfectly satisfy the user's query.
            Focus on skills, experience, and keywords that would build a strong match.
            
            User query: {query}
            
            Hypothetical content:"""),
        ])

    async def translate(self, query: str) -> List[str]:
        chain = self.prompt | self.llm
        print(f"Generating hypothetical answer for: '{query}'...")
        hypothetical_answer = await chain.ainvoke({"query": query})
        
        # Use BOTH the original query and the fake answer for retrieval
        result = [query, hypothetical_answer.content]
        print(f"Generated HyDE context (first 50 chars): {result[1][:50]}...")
        return result
