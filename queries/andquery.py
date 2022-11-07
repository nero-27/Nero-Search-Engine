from .querycomponent import QueryComponent
from indexing import Index, Posting

from queries import querycomponent 

class AndQuery(QueryComponent):
    def __init__(self, components : list[QueryComponent]):
        self.components = components


    def get_postings(self, index : Index, tp) -> list[Posting]:
        result = self.components[0].get_postings(index, tp)
      
        for comp in self.components[1:]:
            posting = comp.get_postings(index, tp)
            temp = self._AndMerge(result, posting)
            result = temp

        return result

    def get_author_postings(self, soundex : Index) -> list[Posting]:
        result = self.components[0].get_author_postings(soundex)

        doclists = []
        for comp in self.components[1:]:
            posting = comp.get_author_postings(soundex)
            temp = self._AndMerge(result, posting)
            result = temp

        return result

    # without positions
    def _AndMerge(self, posting1, posting2):
        pos1 = pos2 = 0
        merged_result = []

        while pos1 < len(posting1) and pos2 < len(posting2):
            if posting1[pos1][0] == posting2[pos2][0]:
                merged_result.append(posting1[pos1])
                pos1 += 1
                pos2 += 1
            elif posting1[pos1] < posting2[pos2]:
                pos1 += 1
            else:
                pos2 += 1

        return merged_result


    def __str__(self):
        return " AND ".join(map(str, self.components))