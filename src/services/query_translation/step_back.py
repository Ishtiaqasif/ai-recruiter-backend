from typing import List
from langchain_core.prompts import ChatPromptTemplate
from .base import BaseQueryTranslator

class StepBackTranslator(BaseQueryTranslator):
    """
    Step-back Prompting translator.
    Generates a broader, more general query to provide better context.
    """
    
    def __init__(self, llm):
        self.llm = llm
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("human", """You are an AI recruiter. 
            Given a specific recruitment query, generate a more general, high-level "step-back" question 
            that would provide the necessary context to answer the user's specific request.
            
            Specific User Query: {query}
            
            Step-back Query:"""),
        ])

    async def translate(self, query: str) -> List[str]:
        chain = self.prompt | self.llm
        print(f"Generating step-back for: '{query}'...")
        step_back_query = await chain.ainvoke({"query": query})
        
        # Use BOTH original and step-back
        result = [query, step_back_query.content]
        print(f"Generated step-back: {result[1]}")
        return result
