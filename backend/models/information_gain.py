import numpy as np

# transacciones => matrix
# clases => numpy array

#calcula la entropía con respecto a las clases


def calcular_entropia(clases):
    unique, counts = np.unique(clases, return_counts=True)
    probabilidades = counts.astype(float)/counts.sum()
    total = 0
    for p in probabilidades:
        if p != 0:
            total -= p*np.log2(p)
    return total


def calcular_ganancia(transacciones, clases):
    entropia_total = calcular_entropia(clases)
    entropy_attributes = []
    for i in range(transacciones.shape[1]):  # por cada atributo
        unique, counts = np.unique(transacciones[:, i], return_counts=True)
        entropy = []
        for value in unique: # por cada valor posible del atributo. En nuestro caso 1 o 0

            entries = clases[transacciones[:, i] == value]
            entropy.append(calcular_entropia(entries))

        entropy = np.array(entropy)
        prob = counts.astype(float)/counts.sum()
        entropy_attributes.append(entropia_total - np.dot(entropy, prob))
    return entropy_attributes


if __name__ == '__main__':
    clases = np.array([0, 0, 1, 1, 1, 1, 0, 0])
    matrix = np.array([[1, 2, 1],
              [1, 0, 1],
              [2, 2, 1],
              [2, 1, 1],
              [1, 0, 0],
              [2, 1, 0],
              [1, 1, 2],
              [2, 1, 2]])
    print(calcular_entropia(clases))
    print(calcular_ganancia(matrix, clases ))