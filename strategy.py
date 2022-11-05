from abc import ABC, abstractmethod
from queue import PriorityQueue
import math

class ScoringStrategy(ABC):
    @abstractmethod
    def scoring(self, query, diskIndex, corpus_length) -> PriorityQueue:
        pass

class Default(ScoringStrategy):
    def scoring(self, query, diskIndex, corpus_length) -> dict:
        # store score of query for docs in ad
        ad = {} 
        for t in query:
            t_postings = diskIndex.get_postings_with_positions(t)
            dft = len(t_postings)
            wqt = math.log(1 + (corpus_length / dft))
            for doc in t_postings:
                doc_id = doc[0]
                tftd = len(doc[-1])
                wdt = 1 + math.log(tftd)
                Ld = diskIndex.get_doc_weight(doc_id)
                temp = (wdt*wqt) / Ld
                if doc_id in ad:
                    ad[doc_id] += temp
                else:
                    ad[doc_id] = temp

        return ad


class Tf_idf(ScoringStrategy):
    def scoring(self, query, diskIndex, corpus_length) -> dict:
        ad = {} 
        for t in query:
            t_postings = diskIndex.get_postings_with_positions(t)
            dft = len(t_postings)
            wqt = math.log(corpus_length / dft)
            for doc in t_postings:
                doc_id = doc[0]
                wdt = len(doc[-1])
                Ld = diskIndex.get_doc_weight(doc_id)
                temp = (wdt*wqt) / Ld
                if doc_id in ad:
                    ad[doc_id] += temp
                else:
                    ad[doc_id] = temp

        return ad

class Ranking:
    def __init__(self, query, diskIndex, corpus_length):
        self.query = query
        self.diskIndex = diskIndex
        self.corpus_length = corpus_length
        self.scoring_objects = {
            '1' : Default(),
            '2' : Tf_idf()
        }

    def get_scores(self, ScoringStrategy):
        obj = self.scoring_objects[ScoringStrategy]
        self.ad = obj.scoring(self.query, self.diskIndex, self.corpus_length)
        return self.ad

