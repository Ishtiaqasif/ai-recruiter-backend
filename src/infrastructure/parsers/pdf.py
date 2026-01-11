from langchain_community.document_loaders import PyPDFLoader
from src.core.interfaces.document_parser import DocumentParser

class PDFParser(DocumentParser):
    def parse(self, file_path: str) -> str:
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        return "\n".join([d.page_content for d in docs])

    def supports_extension(self, extension: str) -> bool:
        return extension.lower() in [".pdf"]
