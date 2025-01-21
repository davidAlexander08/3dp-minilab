import pandas as pd
import numpy as np
from scipy.linalg import solve
import random
from sklearn.cluster import KMeans


def geraMatrizRuidosPostos(lista_postos):
    semente = 100
    numeroDeRuidos = 100
    matrizRuidos = np.zeros((numeroDeRuidos, len(lista_postos)))
    random.seed(semente)
    np.random.seed(semente)  # For numpy random generators
    for j in range(len(lista_postos)):
        for i in range(numeroDeRuidos):
            matrizRuidos[i, j] = np.random.normal(0, 1)
    return matrizRuidos


def agregaRuidosKmeansMatriz(numeroDeAberturasPeriodo, matrizRuidos, lista_postos):
    # Perform k-means clustering
    numero_clusters = numeroDeAberturasPeriodo
    numero_iteracoes = 10
    kmeans = KMeans(n_clusters=numero_clusters, max_iter=numero_iteracoes, init="random", n_init=1)
    try:
        kmeans.fit(matrizRuidos)
        distances = np.linalg.norm(matrizRuidos[:, np.newaxis] - kmeans.cluster_centers_, axis=2)
        print(distances)
        probabilities = np.exp(-distances) / np.sum(np.exp(-distances), axis=1, keepdims=True)
        print(probabilities)
        exit(1)
    except Exception as e:
        print("Clustering failed:", str(e))
        exit(1)
    # Extract cluster centers
    means = kmeans.cluster_centers_
    print("CLUSTER CENTERS (MEANS):\n", means)
    # Prepare the matrizRuidosAgregados
    matrizRuidosAgregados = np.zeros((numero_clusters, len(lista_postos)))
    # Populate matrizRuidosAgregados
    for j in range(numero_clusters):
        for i in range(len(lista_postos)):
            matrizRuidosAgregados[j, i] = means[j, i]
    print("FINAL AGGREGATED MATRIX (matrizRuidosAgregados):\n", matrizRuidosAgregados)
    return matrizRuidosAgregados