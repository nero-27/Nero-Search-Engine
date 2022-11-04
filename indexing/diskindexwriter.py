from ctypes import sizeof
from io import SEEK_END
from .index import Index
from .positionalinvertedindex import PositionalInvertedIndex
import os
import struct
import sqlite3

class DiskIndexWriter():

        def __init__(self, path) -> None:
            self.path = path
            self.conn = sqlite3.connect('database.db')
            self.c = self.conn.cursor()
            # self.w = self.conn.cursor()
            self.c.execute(''' CREATE TABLE IF NOT EXISTS bytes (
                term text PRIMARY KEY,
                position integer
            )
            ''')

        def add_entry(self, term, position):
            self.c.execute("INSERT OR REPLACE INTO bytes VALUES (?, ?)", (term, position))

        def get_entry(self, term):  # returns position
            with self.conn:
                print(term)
                self.c.execute("SELECT position FROM bytes WHERE term = (?) ", (term[0],))
                return self.c.fetchone()[0]

        def writeIndex(self, index, vocab):
            # connect to database
            frmt = '>i'
            # create postings.bin file
            start_position = 0
            step = struct.calcsize(frmt)

            
            with self.conn:
                # open postings.bin in binary mode
                with open(os.path.join(self.path, 'postings.bin'), 'wb') as f:
                    for term in vocab:
                        postings_list = index.get_postings(term)
                        
                        # add (term, start_position) to database
                        # self.c.execute("INSERT OR REPLACE INTO bytes VALUES (?, ?)", (term, start_position))
                        self.add_entry(term, start_position)

                        # write dft (len of postings_list) to file
                        f.write(struct.pack(frmt, len(postings_list)))
                        start_position += step

                        prev_docid = 0
                        # iterate through postings list for term
                        for doc in postings_list:
                            gap_docid = doc[0]-prev_docid
                            f.write(struct.pack(frmt, gap_docid))
                            start_position += step
                            prev_docid = gap_docid

                            f.write(struct.pack(frmt, len(doc[-1])))
                            start_position += step
                            prev_pos = 0

                            for p in doc[-1]:
                                gap_pos = p - prev_pos
                                f.write(struct.pack(frmt, gap_pos))
                                start_position += step
                                prev_pos = gap_pos

            
        def writeDocWeights(self, doc_weights):
            # s = struct.pack('f'*len(doc_weights), *doc_weights)
            with open(os.path.join(self.path, 'docWeights.bin'), 'ab') as f:
                for ld in doc_weights:
                    f.write(struct.pack('d', ld))

                

            

        