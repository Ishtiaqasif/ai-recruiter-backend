from langchain_core.messages import HumanMessage, SystemMessage
from src.database import get_vector_store
from src.config import OPENAI_LLM_MODEL, GOOGLE_LLM_MODEL, LOCAL_LLM_MODEL, LLM_PROVIDER
# Import specific Chat models as needed, or use a factory. 
# Re-using the logic from old chat.py but placing here.
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
import os

def get_llm():
    provider = LLM_PROVIDER
    
    if provider == "openai":
        return ChatOpenAI(model=OPENAI_LLM_MODEL)
    elif provider in ["ollama", "local"]:
        return ChatOllama(model=LOCAL_LLM_MODEL, temperature=0.7)
    elif provider == "google":
        return ChatGoogleGenerativeAI(model=GOOGLE_LLM_MODEL, temperature=0.7)
    else:
        return ChatGoogleGenerativeAI(model=GOOGLE_LLM_MODEL, temperature=0.7)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

async def ask_question(question: str, session_id: str):
    docs=[]
    vector_store = get_vector_store()
    
    # Configure filter based on provider
    search_kwargs = {"k": 5}
    
    # For MongoDB vector-only index, use pre_filter (or filter in LangChain generic)
    # This filters BEFORE vector search, ensuring we find docs in the session.
    search_kwargs["pre_filter"] = {"sessionId": session_id}
    retriever = vector_store.as_retriever(search_kwargs=search_kwargs)
    docs = await retriever.ainvoke(question)
    
    
    context = format_docs(docs)

    system_prompt = """You are an expert AI Recruiter Assistant.
    Use the following context (resumes/CVs) to answer the user's question.
    If the answer is not in the context, say you don't know.
    
    Context:
    {context}
    """
    
    formatted_system = system_prompt.format(context=context)
    
    messages = [
        SystemMessage(content=formatted_system),
        HumanMessage(content=question)
    ]
    
    llm = get_llm()
    response = await llm.ainvoke(messages)
    return response.content
