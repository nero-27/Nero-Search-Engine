from indexing.postings import Posting
from queries import phraseliteral
from .querycomponent import QueryComponent
from text import BasicTokenProcessor
from . import PhraseLiteral

class NearLiteral(QueryComponent):
    """
    A TermLiteral represents a single term in a subquery.
    """

    def __init__(self, terms : str):
        self.terms = terms.split(' ')
        self.near_k = self.terms[1].split('/')
        del self.terms[1]

    def get_postings(self, index, tp) -> list[Posting]: 
        # token_processor = BasicTokenProcessor()
        # near_k = self.terms[1].split('/')
        # diff = near_k[1]
        # del self.terms[1]

        _tk = tp.process_token([self.terms[0]])[0] # 0th term of single term list
        print(_tk)
        # result = index.get_postings(_tk)
        result = index.get_postings_with_positions(_tk)
        

        # TODO: program this method. Retrieve the postings for the individual terms in the phrase,
		# and positional merge them together.

        for t in self.terms[1:]:
            # doclist = []
            tk = tp.process_token([t])[0]
            try:
                # posting = index.get_postings(tk)
                posting = index.get_postings_with_positions(tk)
            except KeyError:
                print(f'Term {t} not found in corpus')
            temp = self._PositionalMerge(self, result, posting, int(self.near_k[1]))     # near_k = diff
            result = temp
        return result

    def _PositionalMerge(self, posting1, posting2, diff):
        doc1 = doc2 = 0
        merged_result = []

        while doc1 < len(posting1) and doc2 < len(posting2):
            if posting1[doc1][0] == posting2[doc2][0]:      # if doc id is same

                # check for diff
                pos1 = 0
                pos2 = 0
                merged_positions = []
                while pos1 < len(posting1[doc1][1]) and pos2 < len(posting2[doc2][1]):
                    # if difference between positions is diff
                    if posting2[doc2][1][pos2] - posting1[doc1][1][pos1] <= diff:
                        merged_positions.append(posting1[doc1][1][pos1])
                        pos1 += 1
                        pos2 += 1
                    elif posting1[doc1][1][pos1] < posting2[doc2][1][pos2]:
                        pos1 += 1
                    else:
                        pos2 += 1
                
                if len(merged_positions) != 0:
                    merged_result.append([posting1[doc1][0], merged_positions])
                doc1 += 1
                doc2 += 1
                
            elif posting1[doc1][0] < posting2[doc2][0]:
                doc1 += 1
            else:
                doc2 += 1

        return merged_result

    def __str__(self) -> str:
        return '[' + ' '.join(self.terms) + ']'