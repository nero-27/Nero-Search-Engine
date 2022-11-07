from bisect import bisect, bisect_left
from decimal import InvalidOperation
from pydoc import doc
from typing import Iterable
from .index import Index
from .postings import Posting


class PositionalInvertedIndex(Index):
    """Implements an Index using a term-document matrix. Requires knowing the full corpus
    vocabulary and number of documents prior to construction."""

    def __init__(self, vocab : Iterable[str], corpus_size : int):
        """Constructs an empty index using the given vocabulary and corpus size."""
        self.vocabulary = list(vocab)
        self.vocabulary.sort()
        self.corpus_size = corpus_size
        self.hashmap = {}

    def add_term(self, term : str, doc_id : int, pos: int):
        """Check if the term present in hashmap and check if doc_id present in value of that term > must be O(1) runtime"""
        

        if term in self.hashmap.keys():
            if doc_id != self.hashmap[term][-1][0]:
                self.hashmap[term].append([doc_id, [pos]])
                # self.hashmap[term][0] += 1
                # print(self.hashmap)
            else:
                self.hashmap[term][-1][1].append(pos)
        
        else:
            self.hashmap[term] = [ [doc_id, [pos]] ] 

        # print(self.hashmap)
 

    def get_postings(self, term : str) -> Iterable[Posting]:
        """Retrieves a sequence of Postings of documents that contain the given term."""
        return self.hashmap[term]
        


    def vocabulary(self) -> list[str]:
        """A (sorted) list of all terms in the index vocabulary."""
        return self.vocabulary
