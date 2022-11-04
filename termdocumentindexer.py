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


"""This basic program builds a term-document matrix over the .txt files in 
the same directory as this file."""


def index_corpus(corpus : DocumentCorpus, originalPath) -> Index:
    
    token_processor = BasicTokenProcessor()
    diskWriter = DiskIndexWriter(originalPath)
    vocabulary = set()
    vocabulary_authors = set()

    positional_inverted_index = PositionalInvertedIndex(vocabulary, len(corpus))
    soundex_index = SoundexIndex(vocabulary_authors, len(corpus))
    doc_weights = []
    for d in corpus:
        # print(f"Found document {d.id, d.title}")
        # TODO:
        #   Tokenize the document's content by creating an EnglishTokenStream around the document's .content()
        #   Iterate through the token stream, processing each with token_processor's process_token method.
        #   Add the processed token (a "term") to the vocabulary set.
        pos = 0
        tftd = {}
        for ets in EnglishTokenStream(d.get_content()):
            pos += 1
            list_of_tokens = token_processor.remove_hyphens(ets)
            for t in token_processor.process_token(list_of_tokens):
                if t not in tftd:
                    tftd[t] = 1
                else:
                    tftd[t] += 1
                vocabulary.add(t)
                positional_inverted_index.add_term(t, d.id, pos)

        

        # TODO: calculate Ld, write to disk docWeights.bin
        # create function to write to docWeights.bin file in diskWriter,call it here
        wdt_sum =  0
        ld = 0

        for key, value in tftd.items():
            wdt = (1 + math.log(value))
            wdt_sum += wdt*wdt

        ld = math.sqrt(wdt_sum)
        doc_weights.append(ld)
        # diskWriter.writeDocWeights(ld)


        author = d.author.split(' ')
        if len(author) > 1:
            vocabulary_authors.add(author[0])
            vocabulary_authors.add(author[1])
            soundex_index.add_author(author[0], d.id)
            soundex_index.add_author(author[1], d.id)

    # diskWriter = DiskIndexWriter(originalPath)
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
    original_path = os.path.join(corpus_path, folder.lower())

    startIndexTime = time.time()
    print(f'indexing...\n')
    index, soundex, vocab = index_corpus(d, original_path)
    executionTime = time.time() - startIndexTime
    print("Indexing time = ", executionTime ," seconds\n")

    start_disk_time = time.time()
    print(f'disk writing...\n')
    diskWriter = DiskIndexWriter(original_path)
    diskWriter.writeIndex(index, vocab)
    print('disk writing time = ', time.time() - start_disk_time, ' seconds\n')

    tp = BasicTokenProcessor()
    diskIndex = DiskPositionalIndex(original_path)
    while True:
        # user query
        option = input('\nSelect one: \t\n1. Input query manually \t\n2. Use Special queries \n\n')
        if option == '1':
            # Input Query manually
            search_by = input("Search by : \n\t1. Query \n\t2. Author \n\nSelect one : ")
            if search_by == '1':
                # Query
                query = input('Enter a word to search : ')
                bqp = BooleanQueryParser()
                comps = bqp.parse_query(query)
                print(comps)
                print('-'*80)
                try:
                    boolean_posting = comps.get_postings(diskIndex, tp)
                except KeyError:
                    print('Cannot find postings for the term')
                    break

                if len(boolean_posting) == 0:
                    print("Query not found in corpus. Search another query\n")
                    continue

                _print_documents(d, boolean_posting)
                print('-'*80)
                _open = input('Open a document? (y/n) \n')
                if _open == 'y' or _open == 'Y':
                    id = int(input("Enter the id of document to open it = "))
                    print('-'*80, '\n')
                    print(d.get_document(id).get_string_content)
                    print('-'*80, '\n')
                    
                end_query = input("Search another query? y / n\n")
                if end_query.lower() == 'n':
                    break
                else:
                    continue


            if search_by == '2':
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
  

        if option == '2':
            # search by special query            
            while True:
                print("Input one of the following special queries \n:q => to quit \n:stem <word> => to stem a word \n:index <folder_name> => to search different folder \n:vocab => get 1st 1000 words from vocabulary\n:author <author_name> => to search by author\n")
                special_query = input('Input special query: ')
                qry = special_query.split(' ')
                if len(qry) > 2:
                    print('Invalid query: special query accept only one argument')
                    break

                if qry[0] == ':q':
                    break
                if qry[0] == ':stem':
                    stemmer = Porter2Stemmer()
                    print(stemmer.stem(qry[1]))
                if qry[0] == ':index':
                    _index_folder(corpus_path, qry[1])
                if qry[0] == ':vocab':
                    l = sorted(list(vocab)[0:1000])
                    for i in l:
                        print(i)
                    print("Number of vocab words = ", len(l)) 
                if qry[0] == ':author':
                    try:
                        docs = soundex.get_author_postings(qry[1])
                        _print_documents(d, docs)
                    except:
                        print('The directory you chose does not contain authors')
                        break

                end_special_query = input("Search another special query? y / n\n")
                if end_special_query.lower() == 'n':
                    break 
                else:
                    continue

            if qry[0] == ':q':
                break    

        quit = input('Do you want to continue searching? (Y/y or  N/n) \n')
        if quit == 'N' or quit == 'n':
            break


def buildMemoryIndex(corpusPath, corpusName, d):
    originalPath = os.path.join(corpusPath, corpusName.lower())
    # first_file = os.listdir(originalPath)[0] # get name of first file
    # extension = os.path.splitext(first_file)[1] # get extension of file
    # if extension == '.json':
    #     d = DirectoryCorpus.load_json_directory(originalPath, extension)
    # if extension == '.txt':
    #     d = DirectoryCorpus.load_text_directory(originalPath, extension)

    # d = get_directory(originalPath)

    
    startIndexTime = time.time()
    print(f'indexing...\n')
    index, soundex, vocab = index_corpus(d, originalPath)
    executionTime = time.time() - startIndexTime
    print("Indexing time = ", executionTime ," seconds\n")

    return index, soundex, vocab

def buildDiskIndex(corpusPath, corpusName, index, vocab):
    # call diskindexwriter on positional index
    diskWriter = DiskIndexWriter(os.path.join(corpusPath, corpusName))
    startDiskTime = time.time()
    print("Disk Indexing...\n")
    diskWriter.writeIndex(index, vocab)
    endDiskTime = time.time() - startDiskTime
    print("Disk Indexing time = ", endDiskTime, end='\n')
    

def ranked_query_search(corpusPath, d):
    tp = BasicTokenProcessor()
    diskIndex = DiskPositionalIndex(corpusPath)

    while True:
    
        phraseQuery = input('Enter a query for ranked retrieval : ')
        query = phraseQuery.split(' ')  # bag of words
        phraseQueryBag = [tp.process_token([q]) for q in query]
        corpus_length = len(d)

        # store score of query for docs in ad
        ad = {} 
        for t in phraseQueryBag:
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

        # store ad in binary heap priority queue by value (score)
        queue = PriorityQueue()

        # add all ad elements to queue, gets sorted implicity after every put
        for doc_id, score in ad.items():
            queue.put((-1*score, doc_id))

       
        print('-'*80)
        # try:
        #     # get postings without positions
        #     phraseQueryPosting = comps.get_postings(diskIndex, tp) # got to termliteral
        # except KeyError:
        #     print('Cannot find postings for the term')
        #     break

        # try:
        #     len(phraseQueryPosting) == 0
        # except TypeError:
        #     print("Query not found in corpus. Search another query\n")
        #     continue
        count = 0
        while True:
            if not queue.empty():
                count += 1
                i = queue.get()
                if i:
                    if d.get_document(i[1]).author:
                        print(i[1],"=> ", d.get_document(i[1]).title, '===> ', d.get_document(i[1]).author)
                    else:
                        print(i[1],"=> ", d.get_document(i[1]).title, '(score: ',abs(i[0]), ')') 
                if count == 10:
                    break  
            else:
                break
        print("\nNumber of documents = ", count)

                    
        # _print_documents(d, phraseQueryPosting)
        print('-'*80)
        _open = input('Open a document? (y/n) \n')
        if _open == 'y' or _open == 'Y':
            id = int(input("Enter the id of document to open it = "))
            print('-'*80, '\n')
            print(d.get_document(id).get_string_content)
            print('-'*80, '\n')
            
        end_query = input("Search another query? y / n\n")
        if end_query.lower() == 'n':
            break
        else:
            continue

def boolean_query_search(corpusPath):
    tp = BasicTokenProcessor()
    diskIndex = DiskPositionalIndex(corpusPath)
    while True:
        boolean_query = input("Enter a boolean or phrase query : ")
        bqp = BooleanQueryParser()
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
            id = int(input("Enter the id of document to open it = "))
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
            corpusName = input("Pleae select one of the following folder to search (no spacses) \n=> National Park \n=> Moby Dick \n=> mlb (major league baseball)\nType folder name without spaces:\n")
            d = get_directory(os.path.join(corpusPath, corpusName))
            index, soundex, vocab = buildMemoryIndex(corpusPath, corpusName, d)
            buildDiskIndex(corpusPath, corpusName, index, vocab)
            ranked_query_search(os.path.join(corpusPath, corpusName), d)
            
        elif build == '2':
            # query index
            path = input("Enter path of disk index (excluding file): ")
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
            corpusName = input("Pleae select one of the following folder to search (no spacses) \n=> National Park \n=> Moby Dick \n=> mlb (major league baseball)\nType folder name without spaces:\n")
            d = get_directory(os.path.join(corpusPath, corpusName))
            index, soundex, vocab = buildMemoryIndex(corpusPath, corpusName, d)
            buildDiskIndex(corpusPath, corpusName, index, vocab)
            boolean_query_search(os.path.join(corpusPath, corpusName))
            
        elif build == '2':
            # query index
            path = input("Enter path of disk index (excluding file): ")
            # corpusName = os.path.basename(os.path.normpath(path))
            d = get_directory(path)
            boolean_query_search(path)
            
        else:
            print("Please select the correct option.\n")
        pass
