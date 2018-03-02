import os
import pickle
import numpy as np
from scipy.sparse import csr_matrix, vstack
from backend.utils import binary_search
from collections import OrderedDict

from sklearn.preprocessing import normalize


def reshape_sparse_X_y(X, y, positions, all_db, classes):
    if X is None:
        X = csr_matrix(all_db.shape)

    max_p = positions.max() + 1
    if y is not None and max_p > y.shape[0]:
        # Agregamos las filas que falta (si es que faltan
        y = vstack(
            (y, csr_matrix((max_p - y.shape[0], y.shape[1]), dtype=np.int8)))
    # En las posiciones nuevas, ponemos las clases que corresponden. hay que hacer reshape de classes porque es de una dimensión
    X = X.tocoo()

    aux = all_db[positions].tocoo()
    data, col, row = X.data, X.col, X.row
    data_, col_, row_ = aux.data, aux.col, aux.row
    rows = list()
    for r in row_:
        rows.append(
            positions[r])  # debemos obtener la posición en alldb, no en aux

    rows = np.hstack((row, np.array(rows)))
    X = csr_matrix((np.hstack((data, data_)), (rows, np.hstack((col, col_)))),
                   shape=(rows.max() + 1, all_db.shape[1]))

    if y is None:
        y = csr_matrix((X.shape[0], 1))
    y[positions, 0] = classes.reshape((len(classes), y.shape[1]))
    return X, y


def remove_zero_columns(matrix):
    mask = matrix.getnnz(0) > 0  # nonzero columns
    nonremoved_columns = np.where(mask)[0].tolist()
    matrix = matrix[:, mask]

    return matrix


def get_bow(inputpath, db, config):
    if "output_bow_data_{}".format(config) in os.listdir(inputpath):
        with open(os.path.join(inputpath, "output_bow_data_{}".format(config)),
                  "rb") as f:
            data = pickle.load(f)
        with open(os.path.join(inputpath, "output_bow_rows_{}".format(config)),
                  "rb") as f:
            rows = pickle.load(f)
        with open(os.path.join(inputpath, "output_bow_cols_{}".format(config)),
                  "rb") as f:
            cols = pickle.load(f)
        with open(os.path.join(inputpath, "output_bow_ids_{}".format(config)),
                  "rb") as f:
            ids = pickle.load(f)
    else:
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT t.counter, d.row, ti.col, d.id FROM tokenization as t, token_id as ti, document as d "
                "WHERE t.document = d.id AND ti.token = t.token AND config{}".format(
                    config))
            data = np.asarray(cursor.fetchall())
            cols = data[:, 2].astype(int)
            rows = data[:, 1].astype(int)
            ids = list(OrderedDict.fromkeys(data[:, 3]))
            data = data[:, 0].astype(np.int8)

        cursor.close()

        with open(os.path.join(inputpath, "output_bow_data_{}".format(config)),
                  "wb") as f:
            pickle.dump(data, f)
        with open(os.path.join(inputpath, "output_bow_rows_{}".format(config)),
                  "wb") as f:
            pickle.dump(rows, f)
        with open(os.path.join(inputpath, "output_bow_cols_{}".format(config)),
                  "wb") as f:
            pickle.dump(cols, f)
        with open(os.path.join(inputpath, "output_bow_ids_{}".format(config)),
                  "wb") as f:
            pickle.dump(ids, f)

    rows_aux = list(OrderedDict.fromkeys(rows))
    bow = remove_zero_columns(csr_matrix((data, (rows, cols)), dtype=np.int64))
    return bow, dict(zip(ids, rows_aux)), dict(zip(rows_aux, ids))



def get_document_row(db):
    with db.cursor() as cursor:
        cursor.execute(
            "SELECT d.id, d.row FROM document as d where abstract!=''")
        data = dict(cursor.fetchall())
        reverse_data = {v: k for k, v in data.items()}
    return data, reverse_data


def update_data(self, X, y, docs_pos, all_db, classes):
    X, y = self.reshape_sparse_X_y(X, y, docs_pos, all_db, classes)
    return X, y


def get_bow_representation(doc2row, all_db):
    def _get_bow_representation(ids, current_truth):
        X = all_db
        if ids is not None:
            rows = np.array([doc2row[id_] for id_ in ids])
            data = all_db[rows]
            data = data.tocoo()

            X = csr_matrix((data.data, ([rows[r] for r in data.row], data.col)),
                           shape=(rows.max() + 1, all_db.shape[1]))
        y = None
        if current_truth is not None:
            classes = [-1 if binary_search(current_truth, id_) == -1 else 1 for
                       id_ in ids]
            y = csr_matrix((classes, (rows, np.zeros(len(rows)))))

        return X, y

    return _get_bow_representation


def get_document(doc2row, all_db):
    def _get_document(id):
        return all_db[doc2row[id]]

    return _get_document
