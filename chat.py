import os
from typing import List
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from database import get_vector_store

def get_llm():
    provider = os.getenv("LLM_PROVIDER", "google").lower()
    
    if provider == "openai":
        return ChatOpenAI(model="gpt-3.5-turbo")
    elif provider == "ollama":
        return ChatOllama(model=os.getenv("OLLAMA_MODEL", "llama3"), temperature=0.7)
    elif provider == "google":
        return ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7)
    else:
        return ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

async def ask_question(question: string, session_id: string):
    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 10, "filter": {"metadata.sessionId": session_id}}
    )
    
    llm = get_llm()
    
    template = """You are the AI Recruiter Assistant, a specialized tool designed to help hiring managers analyze candidate CVs/resumes against user queries, as datasouce we have a cv-bank. Your purpose is to provide data-driven insights, shortlist relevant profiles, and answer specific questions about candidates using only the provided context.

Communication Guidelines:

Professional & Precise: Maintain a formal yet helpful recruitment professional tone.
Context-First: Base all candidate-specific claims strictly on the provided CV chunks. If information is missing, clearly state that it's not present.
Concise Responses: Provide structured and scannable answers (bullet points are preferred for comparisons).
Cite Sources: Always mention the candidate's filename or name when discussing their profile.
Generic Polish: You can handle greetings and basic assistant interactions politely, but always steer back to the recruitment task.
No Hallucinations: Do not invent skills, experience, or qualifications..

CONTEXT:
{context}

User Question: {question}

Answer:"""

    prompt = PromptTemplate.from_template(template)
    
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    # We can stream or invoke. For now invoke.
    response = await rag_chain.ainvoke(question)
    return response
