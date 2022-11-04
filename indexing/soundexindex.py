from bisect import bisect, bisect_left
from decimal import InvalidOperation
from pydoc import doc
from typing import Iterable
from .index import Index
from .postings import Posting


class SoundexIndex(Index):
    """Implements an Index using a term-document matrix. Requires knowing the full corpus
    vocabulary and number of documents prior to construction."""

    def __init__(self, vocab : Iterable[str], corpus_size : int):
        """Constructs an empty index using the given vocabulary and corpus size."""
        self.vocabulary = list(vocab)
        self.vocabulary.sort()
        self.corpus_size = corpus_size
        self.hashmap_authors = {}

    def add_author(self, author_fn : str, doc_id : int):
        """Check if the term present in hashmap and check if doc_id present in value of that term > must be O(1) runtime"""
        
        hashed_author = self.hash_code(author_fn)

        if hashed_author in self.hashmap_authors.keys():
            if doc_id != self.hashmap_authors[hashed_author][-1][0]:
                self.hashmap_authors[hashed_author].append([doc_id, []])

        else:
            self.hashmap_authors[hashed_author] = [ [doc_id, []] ] 


    def get_author_postings(self, hashed_author : str) -> Iterable[Posting]:
        """Retrieves a sequence of Postings of documents that contain the given term."""
        hashed_author = self.hash_code(hashed_author)
        return self.hashmap_authors[hashed_author]
        


    def vocabulary(self) -> list[str]:
        """A (sorted) list of all terms in the index vocabulary."""
        return self.vocabulary

    def hash_code(self, string):
        s = string.lower()
        to_zero = 'aeiouhwy'
        to_one = 'bfpv'
        to_two = 'cgjkqsxz'
        to_three = 'dt'
        to_four = 'l'
        to_five = 'mn'
        to_six = 'r'

        code = s[0]

        for i in range(1,len(s)):
            if s[i] in to_zero:
                code += '0'
            if s[i] in to_one:
                code += '1'
            if s[i] in to_two:
                code += '2'
            if s[i] in to_three:
                code += '3'
            if s[i] in to_four:
                code += '4'
            if s[i] in to_five:
                code += '5'
            if s[i] in to_six:
                code += '6'

        # remove consecutive duplicate numbers
        code = self._removeConsecutiveDuplicates(code)
        code = code.replace('0','')
        while len(code) < 4:
            code += '0'
        return code

    def _removeConsecutiveDuplicates(self, s):
        if len(s) < 2:
            return s
        if s[0] != s[1]:
            return s[0]+ self._removeConsecutiveDuplicates(s[1:])
        return self._removeConsecutiveDuplicates(s[1:])        