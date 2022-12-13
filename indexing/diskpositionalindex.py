import string
from .index import Index
from .diskindexwriter import DiskIndexWriter
import os
import struct

class DiskPositionalIndex(Index):
    # to retrieve postings from the disk index
    
    def __init__(self, path) -> None:
        self.path = path
        self.diw = DiskIndexWriter(path)
    # get postings with positions
    def get_postings_with_positions(self, term : string):
        
        frmt = '>i'
        b = struct.calcsize(frmt)    # size of integer format used for packing
        with open(os.path.join(self.path,'postings.bin'), 'rb') as f:
            postingBegins = self.diw.get_entry(term)
            finalPostings = []
            if postingBegins != None:
                f.seek(postingBegins)
                dft = struct.unpack(frmt, f.read(b))[0]
                doc_gap = 0
                while dft>0:
                    posting = []
                    doc_id = struct.unpack(frmt, f.read(b))[0]
                    posting.append(doc_id + doc_gap)
                    doc_gap = doc_id
                    tft = struct.unpack(frmt, f.read(b))[0]
                    positions = []
                    pos_gap = 0
                    while tft>0:
                        pos = struct.unpack(frmt, f.read(b))[0]
                        positions.append(pos + pos_gap)
                        pos_gap = pos
                        tft -= 1

                    posting.append(positions)
                    dft -= 1
                    finalPostings.append(posting)

        return finalPostings

    # get postings without positions
    def get_postings_without_positions(self, term : string):
        posting_docids = []
        frmt = '>i'
        b = struct.calcsize(frmt)

        with open(os.path.join(self.path, 'postings.bin'), 'rb') as f:
            start_position = self.diw.get_entry(term)
            if start_position != None:    
                f.seek(start_position)
                dft = struct.unpack(frmt, f.read(b))[0] # no of docs
                doc_gap = 0
                while dft > 0:
                    posting = []
                    doc_id = struct.unpack(frmt, f.read(b))[0]
                    posting.append(doc_id + doc_gap) # append doc_id
                    doc_gap = doc_id
                    tft = struct.unpack(frmt, f.read(b))[0]
                    posting.append(tft)
                    f.seek(b*tft, 1)
                    dft -= 1
                    posting_docids.append(posting)

        return posting_docids

      
    def get_doc_weights(self, doc_id) -> dict:
        
        b = struct.calcsize('f')
        weights = {}
        with open(os.path.join(self.path, 'docWeights.bin'), 'rb') as f:
            f.seek(b*doc_id*4, 1)
            weights['ld'] = struct.unpack('f', f.read(b))[0]
            weights['tftd_avg'] = struct.unpack('f', f.read(b))[0]
            weights['docLengthd'] = struct.unpack('i', f.read(b))[0]
            weights['byteSized'] = struct.unpack('i', f.read(b))[0]

            return weights

    def get_docLengthA(self):
        b = struct.calcsize('f')
        with open(os.path.join(self.path, 'docWeights.bin'), 'rb') as f:
            f.seek(-b,2)    # last position - b bytes
            return struct.unpack('f', f.read(b))[0] 
    


    

