from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.manifold import TSNE, MDS
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from scipy.stats import entropy
from skbio.stats.distance import DistanceMatrix
import scipy.spatial.distance as dist
import numpy as np

N_COMPONENTS = 2
TRANSFORMATIONS = [('pca', 'Principal Components Analysis PCA'),
                    ('lda', 'Linear Discriminant Analysis LDA'),
                    ('lsa', 'Latent Semantic Analysis LSA'),
                    ('tsne', 't-distributed Stochastic Neighbor Embedding t-SNE'),
                    ('mds', 'Multidimensional Scaling MDS')]


def reduce_dimensions(transformation, data, classes=None, to_transform=None):
    if transformation == 'lda' and classes is None:
        raise ValueError('Linear Discriminant Analysis necesita las clases')
    elif transformation == 'pca':
        return principal_components_analysis(data, to_transform=to_transform)
    elif transformation == 'lda':
        return linear_discriminant_analysis(data, classes, to_transform=to_transform)
    elif transformation == 'lsa':
        return latent_semantic_analysis(data, to_transform=to_transform)
    elif transformation == 'tsne':
        return tsne(data, to_transform=to_transform)
    elif transformation == 'mds':
        return multidimensional_scalling(data, to_transform=to_transform)
    else:
        raise ValueError(
            'La transformación {0} no está disponible'.format(transformation))


def principal_components_analysis(data, to_transform=None):
    dim_red = PCA(n_components=N_COMPONENTS).fit(data)
    data_new_dimensions = dim_red.transform(data)
    if isinstance(to_transform, list):
        reductions = []
        for d in to_transform:
            reductions.append(dim_red.transform(d))
        return data_new_dimensions, reductions
    return data_new_dimensions


def linear_discriminant_analysis(data, classes, to_transform=None):
    # Aquí primero hay que obtener las clases, y luego bajar las dimensiones

    # print(np.linalg.eigvalsh(data))
    dim_red = LinearDiscriminantAnalysis(solver='svd', n_components=N_COMPONENTS).fit(data, classes)
    data_new_dimensions = dim_red.transform(data)
    if isinstance(to_transform, list):
        reductions = []
        for d in to_transform:
            reductions.append(dim_red.transform(d))
        return data_new_dimensions, reductions
    return data_new_dimensions


def latent_semantic_analysis(data, to_transform=None):
    dim_red = TruncatedSVD(n_components=N_COMPONENTS).fit(data)
    data_new_dimensions = dim_red.transform(data)
    if isinstance(to_transform, list):
        reductions = []
        for d in to_transform:
            reductions.append(dim_red.transform(d))
        return data_new_dimensions, reductions
    return data_new_dimensions


def tsne(data, to_transform=None):
    if to_transform is not None:
        data_new_dimensions = TSNE(n_components=N_COMPONENTS).fit_transform(np.vstack((data, to_transform)))
    else:
        data_new_dimensions = TSNE(n_components=N_COMPONENTS).fit_transform(data)
    return data_new_dimensions


def multidimensional_scalling(data, to_transform=None):
    if to_transform is not None:
        data_new_dimensions = MDS(n_components=N_COMPONENTS).fit_transform(np.vstack((data, to_transform)))
    else:
        data_new_dimensions = MDS(n_components=N_COMPONENTS).fit_transform(data)
    return data_new_dimensions


# de pyLDAvis
def _jensen_shannon(_P, _Q):
    _M = 0.5 * (_P + _Q)
    return 0.5 * (entropy(_P, _M) + entropy(_Q, _M))


# de pyLDAvis
def tsne_precomputed(data):
    dist_matrix = DistanceMatrix(
        dist.squareform(dist.pdist(data.values, _jensen_shannon)))
    model = TSNE(n_components=2, random_state=0, metric='precomputed')
    return model.fit_transform(dist_matrix.data)
