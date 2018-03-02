import numpy as np
from scipy.sparse import csr_matrix
import bottleneck as bn


class BM25:
    def __init__(self, query, df=None, N=None, L_ave=None, k1=1.2, k3=2, b=0.75, top_words_include=10):
        self.k1 = k1
        self.k3 = k3
        self.b = b

        self.query = query
        if df is None or N is None or L_ave is None:
            raise(ValueError("DF or N cannot be Null"))
        if isinstance(df, list):
            df = np.array(df)
        self.df = df
        self.N = N
        self.L_ave = L_ave
        self.c = None
        self.query_weighting = None
        self.top_words = top_words_include

    def compute_c(self, VR, VNR):
        # vector de (1, tamaño diccionario). El primer término
        if VR is None:
            self.c = np.log(self.N) - np.log(self.df)
        else:
            VR_t = VR.sum(axis=0)
            upper = (VR_t + 0.5)/(VNR.sum(axis=0) + 0.5)
            lower = (self.df - VR_t + 0.5)/(self.N - self.df - VR.shape[0] + VR_t + 0.5)
            self.c = np.log(upper) - np.log(lower)
            self.c = np.nan_to_num(self.c)
            self.c = np.asarray(self.c)[0]

    def fit(self, X, y):
        if X is not None:
            # Separar entre VR (relevant) y VNR (non relevant)
            mask = y[:, 0] == 1
            VR = csr_matrix(X[np.where(mask.todense())[0], :], dtype=np.bool)
            mask = y[:, 0] == -1
            VNR = csr_matrix(X[np.where(mask.todense())[0], :], dtype=np.bool)
            self.compute_c(VR, VNR)
            self.expand_query()
        else:
            self.compute_c(None, None)


        self.compute_query_weighting()
        return self

    def compute_query_weighting(self):
        self.query_weighting = (self.k3 + 1) * self.query / (np.full(self.query.shape, self.k3) + self.query)

    def expand_query(self):
        tokens_to_add = np.argpartition(-self.c, self.top_words, axis=0)[:self.top_words]
        aux = np.zeros(self.query.shape)
        aux[0, tokens_to_add] = 1
        self.query = self.query + aux

    def rank_relevant(self, X, top=50):
        if top is None:
            top = X.shape[0]
        upper = (self.k1 + 1) * X
        mask = upper.getnnz(0) > 0  # nonzero columns

        upper = upper[:, mask]

        # document_weighting = upper / lower
        aux1 = csr_matrix(np.multiply(self.c, self.query_weighting))[:, mask]
        document_score = upper.multiply(aux1)
        mask = document_score.getnnz(0) > 0  # nonzero columns
        document_score = document_score[:, mask]
        X = X[:, mask]
        lower = self.k1 * ((1 - self.b) + self.b * X.sum(axis=1) / self.L_ave)
        lower = lower + X
        document_score /= lower
        document_score = np.asarray(document_score.sum(axis=1))
        order = bn.argpartition(document_score, self.N - top, axis=0)[-top:].T[0] # los mayores son los mejores
        return None, order[np.argsort(document_score[order], axis=0)[::-1]].T.tolist()[0]


    @property
    def name(self):
        return "BM25"

    def __repr__(self):
        return self.name + "_".join(["{}-{}".format(k, self.__dict__[k]) for k in ["k1", "k3", "b"]])