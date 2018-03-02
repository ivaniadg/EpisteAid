import logging
import os
from representation.data_cursor import CorpusCursor, DBDataCursor, get_cursor_for_matrix, get_file_cursor
from gensim.models import LdaMulticore
from pymongo import MongoClient

import utils


def exec_lda():
    client = MongoClient()
    db = client.epistemonikos_files

    num_topics = range(2, 51)
    files = range(12)  # Número de combinaciones posibles de preprocesamiento

    # TODOS los documentos
    for f in files:
        for t in num_topics:
            data_cursor = DBDataCursor(db, 'preprocess_{0}'.format(f))
            corpus_cursor = CorpusCursor(data_cursor)
            lda = LdaMulticore(corpus=corpus_cursor,
                               id2word=corpus_cursor.dictionary, num_topics=t)
            lda.save(
                'processing_data/lda/all_docs/preprocess_{0}_topics_{1}'.format(
                    f, t))

    # Para cada TIPO de documento
    config_list = utils.create_config_list(
        'processing_data/lda/types/config_list.json')

    for i, config in enumerate(config_list):
        for f in files:
            for t in num_topics:
                data_cursor = DBDataCursor(db, 'preprocess_{0}'.format(f),
                                           **config)
                corpus_cursor = CorpusCursor(data_cursor, config=i)
                lda = LdaMulticore(corpus=corpus_cursor,
                                   id2word=corpus_cursor.dictionary,
                                   num_topics=t)
                lda.save(
                    'processing_data/lda/types/preprocess_{0}-topics_{1}-config_{2}'.format(
                        f, t, i))


def lda_matrix(matrix_id, preprocess, topics, data_path):

    data_cursor, corpus_cursor = get_file_cursor(matrix_id, preprocess, data_path)
    lda = LdaMulticore(corpus=corpus_cursor, id2word=corpus_cursor.dictionary,
                       num_topics=topics)
    lda.save(os.path.join(data_path, '{2}-preprocess_{0}-topics_{1}.lda'.format(
                preprocess, topics, matrix_id)))
    return lda, corpus_cursor, data_cursor


if __name__ == "__main__":
    # exec_lda()
    client = MongoClient()
    db = client.epistemonikos_files
    data_path = os.path.abspath('../../Data/citation_screnning/sample_data_rocchio/')
    lda_matrix('53f9e0928374405aac15260d', 'x', 10, data_path)
