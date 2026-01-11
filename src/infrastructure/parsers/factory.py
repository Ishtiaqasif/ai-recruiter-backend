import os
from typing import List
from src.core.interfaces.document_parser import DocumentParser
from .pdf import PDFParser
from .text import TextParser

class ParserFactory:
    """
    Factory for document parsers.
    Follows OCP by allowing new parsers to be added without changing client code.
    """
    _parsers: List[DocumentParser] = [PDFParser(), TextParser()]

    @classmethod
    def get_parser(cls, file_name: str) -> DocumentParser:
        ext = os.path.splitext(file_name)[1]
        for parser in cls._parsers:
            if parser.supports_extension(ext):
                return parser
        
        # Fallback to TextParser or raise error
        return TextParser()
