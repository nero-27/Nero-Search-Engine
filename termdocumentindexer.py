from calendar import c
from msilib.schema import Component
from multiprocessing import AuthenticationError
from os import getcwd
from pathlib import Path
from tabnanny import process_tokens
from xmlrpc.client import boolean

from regex import P
from documents import DocumentCorpus, DirectoryCorpus, document
from indexing import Index
from indexing.positionalinvertedindex import PositionalInvertedIndex
from indexing.soundexindex import SoundexIndex
from queries import booleanqueryparser, querycomponent
from queries.andquery import AndQuery
from text import BasicTokenProcessor, EnglishTokenStream
from queries import BooleanQueryParser
import pathlib
import os
from porter2stemmer import Porter2Stemmer
import time
from io import StringIO
import json
from indexing.diskindexwriter import DiskIndexWriter
from indexing.diskpositionalindex import DiskPositionalIndex
import math
from queue import PriorityQueue
from strategy import Ranking
import sys


def index_corpus(corpus : DocumentCorpus, originalPath) -> Index:
    
    token_processor = BasicTokenProcessor()
    diskWriter = DiskIndexWriter(originalPath)
    vocabulary = set()
    vocabulary_authors = set()
    corpus_length = len(corpus)

    positional_inverted_index = PositionalInvertedIndex(vocabulary, corpus_length)
    soundex_index = SoundexIndex(vocabulary_authors, corpus_length)
    doc_weights = []
    docLengthAcc = 0

    for d in corpus:
        byteSized = d.get_doc_size()
        docLengthd = 0    # no of tokens in d
        pos = 0
        tftd = {}
        for ets in EnglishTokenStream(d.get_content()):
            pos += 1
            list_of_tokens = token_processor.remove_hyphens(ets)
            for t in token_processor.process_token(list_of_tokens):
                docLengthd += 1
                if t not in tftd:
                    tftd[t] = 1
                else:
                    tftd[t] += 1
                vocabulary.add(t)
                positional_inverted_index.add_term(t, d.id, pos)

        docLengthAcc += docLengthd
        

        # TODO: calculate Ld, write to disk docWeights.bin
        # create function to write to docWeights.bin file in diskWriter,call it here
        wdt_sum =  0
        ld = 0
        tftd_avg = 0
        for key, value in tftd.items():
            wdt = (1 + math.log(value)) # store in dict of docid > wdt
            wdt_sum += wdt*wdt
            tftd_avg += value

        if len(tftd) != 0:
            tftd_avg = docLengthd / len(tftd)
        else:
            tftd_avg = 0

        ld = math.sqrt(wdt_sum)
        # print(ld)
        doc_weights.append( (ld, tftd_avg, docLengthd, byteSized) )
  


        author = d.author.split(' ')
        if len(author) > 1:
            vocabulary_authors.add(author[0])
            vocabulary_authors.add(author[1])
            soundex_index.add_author(author[0], d.id)
            soundex_index.add_author(author[1], d.id)

    docLengthA = docLengthAcc / corpus_length
    doc_weights.append(docLengthA)  # append average length of doc at the end 

    diskWriter.writeDocWeights(doc_weights)
    
    return positional_inverted_index, soundex_index, vocabulary

def get_directory(corpusPath):  # corpusPath > upto folder name
    first_file = os.listdir(corpusPath)[0]
    extension = os.path.splitext(first_file)[1]
    if extension == '.json':
        d = DirectoryCorpus.load_json_directory(corpusPath, extension)
    if extension == '.txt':
        d = DirectoryCorpus.load_text_directory(corpusPath, extension)
    
    return d

def _print_documents(d, postings):
    # print('postings in indexer = ', postings)
    print("The documents for your query : \n")
    for i in postings:
        if d.get_document(i[0]).author:
            print(i[0],"=> ", d.get_document(i[0]).title, '===> ', d.get_document(i[0]).author)
        else:
            print(i[0],"=> ", d.get_document(i[0]).title)    
    print("\nNumber of documents = ", len(postings))

def _index_folder(corpus_path, folder, d):

    tp = BasicTokenProcessor()
    diskIndex = DiskPositionalIndex(corpus_path)

    # search by author
    while True:
        author_query = input('Enter author name to search : ')
        bqp = BooleanQueryParser()
        comps_author = bqp.parse_query(author_query)
        print('query = ',comps_author)
        print('-'*80)
        try:
            author_posting = comps_author.get_author_postings(soundex)
        except KeyError:
            print('Cannot find postings for the term')
            break

        if len(author_posting) == 0:
            print("No results found\n")
            continue

        _print_documents(d, author_posting)

        print('-'*80)
        _open = ('Open a document? (y/n)')
        if _open == 'y' or _open == 'Y':
            id = input("Enter the id of document to open it = ")
            print('-'*80, '\n')
            print(d.get_document(id).get_string_content)
            print('-'*80, '\n')

        end_author_query = input("Search another author? y / n\n")
        if end_author_query.lower() == 'n':
            break
        else:
            continue

def special_queries(query, corpus_path, bqp):
    qry = query.split(' ')
    if len(qry) > 2:
        print('Invalid query: special query accept only one argument')
        sys.exit()
    if qry[0] == ':q':
        sys.exit()
    if qry[0] == ':stem':
        stemmer = Porter2Stemmer()
        print(stemmer.stem(qry[1]))
    if qry[0] == ':vocab':
        l = sorted(list(vocab)[0:1000])
        for i in l:
            print(i)
        print("Number of vocab words = ", len(l)) 
    if qry[0] == ':author':
        try:
            author_comps = bqp.parse_query(qry[1])
            docs = author_comps.get_author_postings(soundex)
            _print_documents(d, docs)
        except:
            print('The directory you chose does not contain authors')
    

def buildMemoryIndex(path, d):  
    startIndexTime = time.time()
    print(f'indexing...\n')
    index, soundex, vocab = index_corpus(d, path)
    executionTime = time.time() - startIndexTime
    print("Indexing time = ", executionTime ," seconds\n")

    return index, soundex, vocab

def buildDiskIndex(corpus_path, index, vocab):
    # call diskindexwriter on positional index
    diskWriter = DiskIndexWriter(corpus_path)
    startDiskTime = time.time()
    print("Disk Indexing...\n")
    diskWriter.writeIndex(index, vocab)
    endDiskTime = time.time() - startDiskTime
    print("Disk Indexing time = ", endDiskTime, end='\n')
    
def priority_queue(ad):
    # store ad in binary heap priority queue by value (score)
    queue = PriorityQueue()

    # add all ad elements to queue, gets sorted implicity after every put
    for doc_id, score in ad.items():
        queue.put((-1*score, doc_id))

    return queue


def scoring_method(phraseQueryBag, diskIndex, corpus_length, method):
    rank = Ranking(phraseQueryBag, diskIndex, corpus_length)
    ad = rank.get_scores(method)
    queue = priority_queue(ad)
    print('-'*80)
    count = 0
    while True:
        if not queue.empty():
            count += 1
            i = queue.get()
            if i:
                if d.get_document(i[1]).author:
                    print(i[1],"=> ", d.get_document(i[1]).title, '===> ', d.get_document(i[1]).author, '(score: ',abs(i[0]), ')')
                else:
                    print(i[1],"=> ", d.get_document(i[1]).title, '(score: ',abs(i[0]), ')') 
            if count == 10:
                break  
        else:
            break
    print("\nNumber of documents = ", count)



def ranked_query_search(corpusPath, d):
    tp = BasicTokenProcessor()
    diskIndex = DiskPositionalIndex(corpusPath)
    path_to_folder = os.path.dirname(corpusPath)
    
    while True:
        method = input ("Select one ranking method: \n1.Default \n2.tf-idf \n3.Okapi BM25 \n4.Wacky \n").lower()
        phraseQuery = input('> ')

        query = phraseQuery.split(' ')  # bag of words
        for q in range(len(query)):
            query[q] = tp.process_token([query[q]])
        corpus_length = len(d)

        # 4 different scoring methods for additional requirements
        scoring_method(query, diskIndex, corpus_length, method)

        print('-'*80)
        _open = input('Open a document? (y/n) \n')
        if _open == 'y' or _open == 'Y':
            id = int(input("Enter doc_id = "))
            print('-'*80, '\n')
            print(d.get_document(id).get_string_content)
            print('-'*80, '\n')
            
        end_query = input("Search another query? y / n\n")
        if end_query.lower() == 'n':
            break
        else:
            continue

def boolean_query_search(corpusPath, d):
    tp = BasicTokenProcessor()
    bqp = BooleanQueryParser()
    diskIndex = DiskPositionalIndex(corpusPath)
    while True:
        boolean_query = input("> ")
        if boolean_query.startswith(':'):
            special_queries(boolean_query, corpusPath, bqp)

        
        comps = bqp.parse_query(boolean_query)
        
        print('-'*80)
        try:
            # get postings without positions
            boolean_postings = comps.get_postings(diskIndex, tp) # got to termliteral
        except KeyError:
            print('Cannot find postings for the term')
            break

        try:
            len(boolean_postings) == 0
        except TypeError:
            print("Query not found in corpus. Search another query\n")
            continue
                    
        _print_documents(d, boolean_postings)
        print('-'*80)
        _open = input('Open a document? (y/n) \n')
        if _open == 'y' or _open == 'Y':
            id = int(input("Enter doc_id = "))
            print('-'*80, '\n')
            print(d.get_document(id).get_string_content)
            print('-'*80, '\n')
            
        end_query = input("Search another query? y / n\n")
        if end_query.lower() == 'n':
            break
        else:
            continue




if __name__ == "__main__":
    corpusPath = Path(__file__).parent

    rankedOrBoolean = input("Select an option : \n1. Ranked queries \n2. Boolean Queries \n")

    if rankedOrBoolean == '1':
        # Ranked queries
        build = input("Select one: \n1. Build Index \n2. Query index\n")
        if build == '1':
            # build memory index and disk index
            corpusName = input("Enter folder name (no spaces) \n=> National Park \n=> Moby Dick \n=> mlb (major league baseball)\nType folder name without spaces:\n")
            path = os.path.join(corpusPath, corpusName)
            d = get_directory(path)
            # index, soundex, vocab = buildMemoryIndex(corpusPath, corpusName, d)
            index, soundex, vocab = buildMemoryIndex(path, d)
            buildDiskIndex(path, index, vocab)
            ranked_query_search(path, d)
            
        elif build == '2':
            # query index
            path = input("Path to directory: ")
            # corpusName = os.path.basename(os.path.normpath(path))
            d = get_directory(path)
            ranked_query_search(path, d)
        else:
            print("Please select the correct option.\n")

    elif rankedOrBoolean == '2':
        # Boolean Queries
        build = input("Select one: \n1. Build Index \n2. Query index\n")
        
        if build == '1':
            # build index
            corpusName = input("Enter folder name (no spaces) \n=> National Park \n=> Moby Dick \n=> mlb (major league baseball)\nType folder name without spaces:\n")
            path = os.path.join(corpusPath, corpusName)
            d = get_directory(path)
            index, soundex, vocab = buildMemoryIndex(path, d)
            if corpusName.startswith('mlb'):
                author = input("Search by author? (y/n)\n")
                if author == 'y':
                    author_query = input("> ")
                    bqp = BooleanQueryParser()
                    comps_author = bqp.parse_query(author_query)
                    author_postings = comps_author.get_author_postings(soundex)
                    _print_documents(d, author_postings)
                    print('-'*80)
                    _open = input('Open a document? (y/n) \n')
                    if _open == 'y' or _open == 'Y':
                        id = int(input("Enter doc_id = "))
                        print('-'*80, '\n')
                        print(d.get_document(id).get_string_content)
                        print('-'*80, '\n')
                   
            else:
                buildDiskIndex(path, index, vocab)
                boolean_query_search(path, d)
            
        elif build == '2':
            # query index
            path = input("Path to directory: ")
            d = get_directory(path)
            boolean_query_search(path, d)
            
        else:
            print("Please select the correct option.\n")
        pass
