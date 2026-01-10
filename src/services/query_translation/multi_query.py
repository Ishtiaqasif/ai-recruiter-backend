from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import CommaSeparatedListOutputParser
from .base import BaseQueryTranslator

class MultiQueryTranslator(BaseQueryTranslator):
    """
    Generates multiple variations of the user query to capture different 
    recruitement jargon and perspectives.
    """
    
    def __init__(self, llm):
        self.llm = llm
        self.output_parser = CommaSeparatedListOutputParser()
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("human", """You are an AI recruiter assistant. 
            Your goal is to generate 3 alternative versions of the user's query to help find relevant CVs.
            Provide different variations using recruitment jargon, acronyms, or broader terms.
            
            Original query: {query}
            
            Output ONLY the 3 variations separated by commas."""),
        ])

    async def translate(self, query: str) -> List[str]:
        chain = self.prompt | self.llm | self.output_parser
        print(f"Generating variations for: '{query}'...")
        variations = await chain.ainvoke({"query": query})
        
        # Include original query + variations
        result = list(set([query] + [v.strip() for v in variations]))
        print(f"Generated variations: {result}")
        return result
