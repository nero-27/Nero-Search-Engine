from bisect import bisect, bisect_left
from decimal import InvalidOperation
from pydoc import doc
from typing import Iterable
from .index import Index
from .postings import Posting


class TermDocumentIndex(Index):
    """Implements an Index using a term-document matrix. Requires knowing the full corpus
    vocabulary and number of documents prior to construction."""

    def __init__(self, vocab : Iterable[str], corpus_size : int):
        """Constructs an empty index using the given vocabulary and corpus size."""
        self.vocabulary = list(vocab)
        self.vocabulary.sort()
        self.corpus_size = corpus_size

    def add_term(self, term : str, doc_id : int):
        """Records that the given term occurred in the given document ID."""
        # bisect_left does a binary search to find where the given item would be in the list, if it is there.
        vocab_index = bisect_left(self.vocabulary, term)
        # Check to make sure the term is actually in the list.
        if vocab_index != len(self.vocabulary) and self.vocabulary[vocab_index] == term:
            self._matrix[vocab_index][doc_id] = True
        else:
            raise InvalidOperation("Cannot add a term that is not already in the matrix")

    def get_postings(self, term : str) -> Iterable[Posting]:
        """Returns a list of Postings for all documents that contain the given term."""
        # TODO: implement this method.
		# Binary search the self.vocabulary list for the given term. (see bisect_left, above)
		# Walk down the self._matrix row for the term and collect the document IDs (column indices)
		# of the "true" entries.

        insert_index = bisect_left(self.vocabulary, term)
        query_row = self._matrix[insert_index]
        true_doc_ids = []
        for i in range(len(query_row)):
            if query_row[i] == True:
                true_doc_ids.append(i)

        # print(true_doc_ids)
        return true_doc_ids


    def vocabulary(self) -> Iterable[str]:
        return self.vocabulary
