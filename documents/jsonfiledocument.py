from os import read
from pathlib import Path
from typing import Iterable
from .document import Document
import json
from io import StringIO

class JsonFileDocument(Document):
    """
    Represents a document that is saved as a simple text file in the local file system.
    """
    def __init__(self, id : int, path : Path):
        super().__init__(id)
        self.path = path
    
    @property
    def title(self) -> str:
        with open(self.path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        file_like_title = json_data['title']
        return file_like_title

    # returns TextIOWrapper
    def get_content(self) -> Iterable[str]:
        with open(self.path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            file_like_body = StringIO(json_data['body'])
            # file_like_body = json_data['body']
        return file_like_body

    @property
    def get_string_content(self) -> Iterable[str]:
        with open(self.path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            file_like_body = json_data['body']
            # file_like_body = json_data['body']
        return file_like_body

    @property
    def author(self) -> str:
        with open(self.path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        try:
            file_like_title = json_data['author']
        except KeyError:
            return ""
        return file_like_title


    @staticmethod
    def load_from(abs_path : Path, doc_id : int) -> 'JsonFileDocument' :
        """A factory method to create a TextFileDocument around the given file path."""
        return JsonFileDocument(doc_id, abs_path)