# -*- coding: utf-8 -*-
import sqlite3
import os
from interface import DataApi
from gensim.models import Word2Vec

class WordFilter(DataApi.AbsWordFilter):
    __dataFile = 'db/word_filter.db'
    __schemaFile = 'db/schema/word_filter.sql'

    __extendDict = {}
    __reduceList = []

    def __init__(self):
        db = sqlite3.connect(WordFilter.__dataFile)

        with db:
            WordFilter.__createTable(db)
            cursor = db.cursor()

            rv = cursor.execute('select * from extend_words')
            WordFilter.__extendDict = {x: y for x, y in rv}

            rv = cursor.execute('select text from reduce_words')
            WordFilter.__reduceList = [x[0] for x in rv]

            cursor.close()

    def get_extend_word_dict(self, params=None):
        return WordFilter.__extendDict

    def get_reduce_word_list(self, params=None):
        return WordFilter.__reduceList

    def add_extend_word(self, match_text, text, params=None):
        with sqlite3.connect(WordFilter.__dataFile) as db:
            WordFilter.__createTable(db)

            cursor = db.cursor()
            cursor.execute('insert or replace into extend_words values(:match_text, :text)',
                                {'match_text': match_text, 'text': text})

            db.commit()
            cursor.close()

            self.__init__()

    def add_reduce_word(self, text, params=None):
        with sqlite3.connect(WordFilter.__dataFile) as db:
            WordFilter.__createTable(db)

            cursor = db.cursor()
            cursor.execute('insert or replace into reduce_words values(:text)', {'text': text})

            db.commit()
            cursor.close()

            self.__init__()

    @classmethod
    def __createTable(cls, db):
        with open(cls.__schemaFile, encoding='utf-8', mode='r') as f:
            cursor = db.cursor()
            cursor.executescript(f.read())
            db.commit()
            cursor.close()


class WordRelationship(DataApi.AbsWordRelationship):
    __model_file = 'db/word2vec.model'
    __model = None

    def __init__(self):
        pass

    @classmethod
    def run_word2vec(cls):
        import model.word2vec as wv
        sentences = []

        WordRelationship.__model = wv.run_word2vec(WordRelationship.__model_file, sentences, None)
        pass

    def get_similar_list(self, keyword, result_count, params=None):
        if not os.path.isfile(WordRelationship.__model_file):
            WordRelationship.run_word2vec()

        if keyword not in WordRelationship.__model:
            return []

        return WordRelationship.__model.most_similar(keyword, topn=result_count)


class WordPool(DataApi.AbsWordPool):
    __data_path = 'db/pool'
    __data_set = []

    def __init__(self):
        file_list = list(filter(lambda f: os.path.isfile(os.path.join(WordPool.__data_path, f)),
                                os.listdir(WordPool.__data_path)))

        for file in file_list:
            with open(os.path.join(WordPool.__data_path, file), mode='r', encoding='utf-8') as f:
                WordPool.__data_set.append(f.read())
        # pass

    def get_word_pool_list(self, params=None):
        if 'data_count' in params:
            print('data_count', params['data_count'])
            return WordPool.__data_set[:params['data_count']]

        return WordPool.__data_set

    def add_word_pool(self, text, params=None):
        WordPool.__data_set.append(text)
        pass
