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
            t_postings = diskIndex.get_postings_without_positions(t[0])
            dft = len(t_postings)
            wqt = math.log(1 + (corpus_length / dft))
            for doc in t_postings:
                doc_id = doc[0]
                tftd = doc[-1]
                wdt = 1 + math.log(tftd)
                weights = diskIndex.get_doc_weights(doc_id)
                Ld = weights['ld']
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
            t_postings = diskIndex.get_postings_without_positions(t[0])
            dft = len(t_postings)
            wqt = math.log(corpus_length / dft)
            for doc in t_postings:
                doc_id = doc[0]
                wdt = doc[-1]   # wdt = tftd
                weights = diskIndex.get_doc_weights(doc_id)
                Ld = weights['ld']
                temp = (wdt*wqt) / Ld
                if doc_id in ad:
                    ad[doc_id] += temp
                else:
                    ad[doc_id] = temp

        return ad

class OkapiBM25(ScoringStrategy):
    def scoring(self, query, diskIndex, corpus_length) -> PriorityQueue:
        ad = {}
        docLengthA = diskIndex.get_docLengthA()
        for t in query:
            t_postings = diskIndex.get_postings_without_positions(t[0])
            dft = len(t_postings)
            wqt = max(0.1, math.log( (corpus_length-dft+0.5)/(dft+0.5) ))
            for doc in t_postings:
                doc_id = doc[0]
                tftd = doc[-1]
                # TODO: get docLengthd and docLengthA from disk
                weights = diskIndex.get_doc_weights(doc_id)
                docLengthd = weights['docLengthd']
                wdt = (2.2*tftd)/( 1.2*(0.25+(0.75*(docLengthd/docLengthA)) ) + tftd )
                Ld = 1
                temp = (wdt*wqt) / Ld
                if doc_id in ad:
                    ad[doc_id] += temp
                else:
                    ad[doc_id] = temp

        return ad

class Wacky(ScoringStrategy):
    def scoring(self, query, diskIndex, corpus_length) -> PriorityQueue:
        ad = {}
        for t in query:
            t_postings = diskIndex.get_postings_without_positions(t[0])
            dft = len(t_postings)
            wqt = max(0, math.log( (corpus_length-dft)/dft ))
            for doc in t_postings:
                doc_id = doc[0]
                tftd = doc[-1]
                weights = diskIndex.get_doc_weights(doc_id)
                tftd_avg = weights['tftd_avg']
                byteSized = weights['byteSized']
                wdt = ( (1+math.log(tftd))/(1+math.log(tftd_avg)) )
                Ld = math.sqrt(byteSized)
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
            '2' : Tf_idf(),
            '3' : OkapiBM25(),
            '4' : Wacky()
        }

    def get_scores(self, ScoringStrategy):
        obj = self.scoring_objects[ScoringStrategy]
        self.ad = obj.scoring(self.query, self.diskIndex, self.corpus_length)
        return self.ad

