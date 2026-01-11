from src.core.interfaces.document_parser import DocumentParser

class TextParser(DocumentParser):
    def parse(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def supports_extension(self, extension: str) -> bool:
        return extension.lower() in [".txt", ".md"]
