from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import CommaSeparatedListOutputParser
from .base import BaseQueryTranslator

class DecompositionTranslator(BaseQueryTranslator):
    """
    Query Decomposition translator.
    Breaks down complex queries into simpler sub-questions.
    """
    
    def __init__(self, llm):
        self.llm = llm
        self.output_parser = CommaSeparatedListOutputParser()
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("human", """You are an AI recruiter. 
            Break down the following complex user query into 2-3 simpler sub-questions that would help in retrieving the right documents.
            If the query is already simple, just return it as is.
            
            User query: {query}
            
            Output sub-questions separated by commas."""),
        ])

    async def translate(self, query: str) -> List[str]:
        chain = self.prompt | self.llm | self.output_parser
        print(f"Decomposing query: '{query}'...")
        sub_questions = await chain.ainvoke({"query": query})
        
        # Include original query + sub-questions
        result = list(set([query] + [q.strip() for q in sub_questions]))
        print(f"Decomposed into: {result}")
        return result
