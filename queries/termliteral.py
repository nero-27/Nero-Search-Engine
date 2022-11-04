from indexing.postings import Posting
from .querycomponent import QueryComponent
from text import BasicTokenProcessor

class TermLiteral(QueryComponent):
    """
    A TermLiteral represents a single term in a subquery.
    """

    def __init__(self, term : str):
        self.term = term

    def get_postings(self, index, tp) -> list[Posting]:
        l = tp.process_token([self.term])
        # return index.get_postings(l[0])
        return index.get_postings_without_positions(l[0]) # goes to diskpositionalindex

    def get_author_postings(self, soundex) -> list[Posting]:
        return soundex.get_author_postings(self.term)

    def __str__(self) -> str:
        return self.term