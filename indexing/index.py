from abc import ABC, abstractmethod
from typing import Iterable
from .postings import Posting

class Index(ABC):
    """An Index can retrieve postings for a term from a data structure associating terms and the documents
    that contain them."""

    def get_postings_with_positions(self, term : str) -> Iterable[Posting]:
        """Retrieves a sequence of Postings of documents that contain the given term."""        
        pass

    # def get_postings(self, term : str) -> Iterable[Posting]:
    #     """Retrieves a sequence of Postings of documents that contain the given term."""        
    #     pass

    def get_postings_without_positions(self, term : str) -> Iterable[Posting]:
        """ Retrieves postings of document without positions"""
        pass

    def get_author_postings(self, author : str) -> Iterable[Posting]:
        """Retrieves a sequence of Postings of documents that contain the given term."""
        pass

    def vocabulary(self) -> list[str]:
        """A (sorted) list of all terms in the index vocabulary."""
        pass