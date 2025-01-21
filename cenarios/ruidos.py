import pandas as pd
import numpy as np
from scipy.linalg import solve
import random
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from scipy.stats import mstats
from kmeans import KmeansGevazp


def geraMatrizRuidosPostos(lista_postos):
    semente = 100
    numeroDeRuidos = 6
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

    ##Metodo GaussianMixture
    gmm = GaussianMixture(n_components=numero_clusters, random_state=42)
    gmm.fit(matrizRuidos)
    cluster_centers = gmm.means_
    probabilities = gmm.predict_proba(matrizRuidos)
    print("cluster_centers: ", cluster_centers)
    #print("GMM Probabilities:\n", probabilities)
    aggregate_probabilities = probabilities.mean(axis=0)
    print("\nAggregate Probabilities for Each Cluster:\n", aggregate_probabilities)

    # KMeans Clustering
    kmeans = KMeans(n_clusters=numero_clusters, max_iter=numero_iteracoes, init="random", n_init=1, random_state=42)
    kmeans.fit(matrizRuidos)
    distances = np.linalg.norm(matrizRuidos[:, np.newaxis] - kmeans.cluster_centers_, axis=2)
    probabilities_kmeans = np.exp(-distances) / np.sum(np.exp(-distances), axis=1, keepdims=True)
    aggregate_probabilities = probabilities_kmeans.mean(axis=0)
    print("\nAggregate Probabilities for Each Cluster Kmeans:\n", aggregate_probabilities)
    means = kmeans.cluster_centers_
    print("CLUSTER CENTERS (MEANS):\n", means)

    gvzp = KmeansGevazp(numero_clusters, matrizRuidos)

    print("matrizRuidosAgregados GEVAZP: ", gvzp.matrizRuidosAgregados)
    exit(1)
    matrizRuidosAgregados = means
    return matrizRuidosAgregados
    ## Prepare the aggregated noise matrix (matrizRuidosAgregados)
    #matrizRuidosAgregados = np.zeros((numero_clusters, len(lista_postos)))
    #for j in range(numero_clusters):
    #    for i in range(len(lista_postos)):
    #        matrizRuidosAgregados[j, i] = means[j, i]
    #print("FINAL AGGREGATED MATRIX (matrizRuidosAgregados):\n", matrizRuidosAgregados)
    #exit(1)
#
    #kmeans = KMeans(n_clusters=numero_clusters, max_iter=numero_iteracoes, init="random", n_init=1)
    #try:
    #    kmeans.fit(matrizRuidos)
    #    distances = np.linalg.norm(matrizRuidos[:, np.newaxis] - kmeans.cluster_centers_, axis=2)
    #    print(distances)
    #    probabilities = np.exp(-distances) / np.sum(np.exp(-distances), axis=1, keepdims=True)
    #    print(probabilities)
    #    exit(1)
    #except Exception as e:
    #    print("Clustering failed:", str(e))
    #    exit(1)
    ## Extract cluster centers
    #means = kmeans.cluster_centers_
    #print("CLUSTER CENTERS (MEANS):\n", means)
    ## Prepare the matrizRuidosAgregados
    #matrizRuidosAgregados = np.zeros((numero_clusters, len(lista_postos)))
    ## Populate matrizRuidosAgregados
    #for j in range(numero_clusters):
    #    for i in range(len(lista_postos)):
    #        matrizRuidosAgregados[j, i] = means[j, i]
    #print("FINAL AGGREGATED MATRIX (matrizRuidosAgregados):\n", matrizRuidosAgregados)
    #return matrizRuidosAgregados

