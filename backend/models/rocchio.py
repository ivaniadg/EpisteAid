import numpy as np
from sklearn.metrics.pairwise import pairwise_distances
import bottleneck as bn


# query = Initial Query
# alpha = Weight of modified Query
# beta = Weight of initial Query
# gamma = Weight of relevant documents
# delta = Weight of irrelevant documents


class Rocchio:
    def __init__(self, query, alpha=1, beta=1, gamma=1, delta=1, metric="euclidean"):
        self.query = query
        self.metric = metric
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.delta = delta
        self.relevant = None

        self.non_relevant = None

    def compute_query(self, relevant=None, non_relevant=None):

        if self.relevant is None or self.alpha == 0:
            alpha_result = np.zeros(self.query.shape)
        else:
            alpha_result = self.alpha * self.relevant

        if self.beta > 0:
            beta_result = self.beta * self.query
        else:
            beta_result = np.zeros(self.query.shape)

        if relevant is not None and relevant.shape[0] > 0 and self.gamma > 0:
            gamma_result = relevant.sum(axis=0) * self.gamma / relevant.shape[0]
        else:
            gamma_result = np.zeros(self.query.shape)

        if non_relevant is not None and non_relevant.shape[0] > 0 and self.delta > 0:
            delta_result = non_relevant.sum(axis=0) * self.gamma / non_relevant.shape[0]
        else:
            delta_result = np.zeros(self.query.shape)

        return alpha_result + beta_result + gamma_result - delta_result

    def fit(self, X, y):
        if X is not None:
            # In target, Relevant = 1. Irrelevant = -1. Unknown = 0.

            mask = y[:, 0] == 1
            relevant = X[np.where(mask.todense())[0], :]
            mask = y[:, 0] == -1
            non_relevant = X[np.where(mask.todense())[0], :]
        else:
            relevant = None
            non_relevant = None
        self.relevant = self.compute_query(relevant=relevant, non_relevant=non_relevant)
        self.non_relevant = self.compute_query(relevant=non_relevant, non_relevant=relevant)
        return self

    def predict(self, X):
        centroids_ = np.vstack((self.non_relevant, self.relevant))
        distances = pairwise_distances(X, np.array(centroids_), metric=self.metric)
        normalized_distance = distances.T / distances.sum(1)
        classes = np.array([-1, 1])
        return classes[distances.argmin(axis=1)]  # Queremos solo el porcentaje de la pertenecer

    def rank_relevant(self, X, top=50):
        if top is None:
            top = X.shape[0]
        centroids_ = self.relevant
        distance = pairwise_distances(X, np.array(centroids_), metric=self.metric)[:, 0]
        order = bn.argpartition(distance, top)[:top]  # los menores son mejores
        order = order[np.argsort(distance[order], axis=0)]
        return None, order

    def rank_nonrel(self, X, top=50):
        centroids_ = self.non_relevant
        distance = pairwise_distances(X, np.array(centroids_), metric=self.metric)
        order = np.argsort(distance, top)
        return distance, order[:top]

    @property
    def name(self):
        return "Rocchio"

    def __repr__(self):
        return self.name + "_" + "_".join(
            ["{}-{}".format(k, self.__dict__[k]) for k in ["alpha", "beta", "gamma", "delta", "metric"]])