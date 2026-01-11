from abc import ABC, abstractmethod

class DocumentParser(ABC):
    """
    Abstract interface for parsing files into raw text.
    """
    
    @abstractmethod
    def parse(self, file_path: str) -> str:
        """
        Parses a file and returns its text content.
        """
        pass

    @abstractmethod
    def supports_extension(self, extension: str) -> bool:
        """
        Checks if the parser supports a given file extension.
        """
        pass
