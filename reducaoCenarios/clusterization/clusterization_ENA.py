import numpy as np

from sklearn.base import BaseEstimator, ClusterMixin
from sklearn.utils.extmath import row_norms
from scipy.spatial.distance import cdist

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from k_means_constrained import KMeansConstrained
from sklearn.utils.extmath import row_norms, squared_norm, stable_cumsum
import ot  # POT - Python Optimal Transport

import os
import pandas as pd
import numpy as np
import networkx as nx
import pydot
import matplotlib.pyplot as plt
from anytree import Node, RenderTree
import time
from joblib import Parallel, delayed, parallel_backend
import os
os.environ["LOKY_MAX_CPU_COUNT"] = "4"  # Adjust based on your CPU
os.environ["PATH"] += os.pathsep + r"C:\\Program Files (x86)\\Graphviz\\bin"
#from numba import jit
from itertools import combinations  # Efficiently generate unique (i, j) pairs
from scipy.stats import skew
import plotly.graph_objects as go
import cvxpy as cp
#caso = "..\\..\\Mestrado\\caso_1D"
##caso = "..\\..\\casos\\Mestrado\\caso_2D"
#caso = "..\\..\\casos\\Mestrado\\caso_construcaoArvore_8cen"
#caso = "..\\..\\casos\\Mestrado\\caso_construcaoArvore_SIN"
#caso = "..\\..\\Dissertacao\\apresentacaoCarmen\\caso_mini"
##caso = "..\\..\\Mestrado\\caso_construcaoArvore_SIN_2000cen"
##caso = "..\\..\\Mestrado\\caso_construcaoArvore_SIN_1000cen"
##caso = "..\\..\\Mestrado\\caso_construcaoArvore_SIN_500cen"
##caso = "..\\..\\Mestrado\\caso_construcaoArvore_SIN_500cen_ENASIN"
##caso = "..\\..\\Mestrado\\caso_construcaoArvore_SIN_50cen"
##caso = "..\\..\\Mestrado\\teste_wellington"
#
#caso = "..\\..\\Dissertacao\\apresentacaoCarmen_Gevazp\\caso_mini\\exercicioGevazp\\4Estagios\\3Aberturas\\Pente"
#caso = "..\\..\\Dissertacao\\apresentacaoCarmen_Gevazp\\caso_mini\\exercicioGevazp\\3Estagios\\2Aberturas\\Pente_GVZP"
#caso = "..\\..\\Dissertacao\\apresentacaoCarmen_Gevazp\\caso_mini\\exercicioGevazp\\4Estagios\\2Aberturas\\Pente"
#caso = "..\\..\\Dissertacao\\apresentacaoCarmen_Gevazp\\caso_mini\\exercicioGevazp\\4Estagios\\3Aberturas_Equiprovavel\\Pente_GVZP"
#caso = "..\\..\\Dissertacao\\apresentacaoCarmen_Gevazp\\caso_mini\\exercicioGevazp\\4Estagios\\3Aberturas\\Pente_GVZP"



def printaArvore(texto, df_arvore):
    df_arvore.loc[df_arvore["NO_PAI"] == 0, "NO_PAI"] = 1
    #df_arvore.loc[df_arvore["NO_PAI"] == 0, "NO_PAI"] = -1  # You can use any value that is not part of the graph
    G = nx.DiGraph()
    for _, row in df_arvore.iterrows():
        if row['NO_PAI'] != row['NO']:
            G.add_edge(row['NO_PAI'], row['NO'], weight=row['PROB'])
    pos = nx.drawing.nx_pydot.pydot_layout(G, prog='dot')
    plt.figure(figsize=(15, 12))
    nx.draw(G, pos, with_labels=True, node_size=1, node_color='lightblue', font_size=1, font_weight='bold', arrows=False)
    
    #edge_labels = nx.get_edge_attributes(G, 'weight')
    #nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    plt.savefig(texto+".png", format="png", dpi=100, bbox_inches="tight")
    plt.title("Tree Visualization")
    #plt.show()

def getFilhos(no, df_arvore):
    filhos = df_arvore[df_arvore["NO_PAI"] == no]["NO"].values
    return filhos

def busca_pai(no, df_arvore):
    pai = df_arvore[df_arvore["NO"] == no]["NO_PAI"].values[0]
    return pai






class MyKMeans(BaseEstimator, ClusterMixin):
    def __init__(self, n_clusters=8, max_iter=300, tol=1e-4, random_state=None):
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.tol = tol
        self.random_state = random_state

    def k_init(self, X, n_clusters, n_local_trials=None):
        """Init n_clusters seeds according to k-means++

        Parameters
        -----------
        X : array or sparse matrix, shape (n_samples, n_features)
            The data to pick seeds for. To avoid memory copy, the input data
            should be double precision (dtype=np.float64).

        n_clusters : integer
            The number of seeds to choose

        x_squared_norms : array, shape (n_samples,)
            Squared Euclidean norm of each data point.

        random_state : numpy.RandomState
            The generator used to initialize the centers.

        n_local_trials : integer, optional
            The number of seeding trials for each center (except the first),
            of which the one reducing inertia the most is greedily chosen.
            Set to None to make the number of trials depend logarithmically
            on the number of seeds (2+log(k)); this is the default.

        Notes
        -----
        Selects initial cluster centers for k-mean clustering in a smart way
        to speed up convergence. see: Arthur, D. and Vassilvitskii, S.
        "k-means++: the advantages of careful seeding". ACM-SIAM symposium
        on Discrete algorithms. 2007

        Version ported from http://www.stanford.edu/~darthur/kMeansppTest.zip,
        which is the implementation used in the aforementioned paper.
        """
        n_samples, n_features = X.shape

        centers = np.empty((n_clusters, n_features), dtype=X.dtype)
        # Set the number of local seeding trials if none is given
        if n_local_trials is None:
            # This is what Arthur/Vassilvitskii tried, but did not report
            # specific results for other than mentioning in the conclusion
            # that it helped.
            n_local_trials = 2 + int(np.log(n_clusters))

        # Pick first center randomly
        center_id = np.random.mtrand._rand.randint(n_samples)
        centers[0,:] = X[center_id, :]

        # Initialize list of closest distances and calculate current potential
        #closest_dist_sq = self.personalEuclidianDistance(centers[0, np.newaxis], X)
        #print(centers[0,:])
        
        closest_dist_sq = []
        for line in range(0,n_samples):
            distancias = np.linalg.norm(np.array(centers[0,:]) - np.array(X[line,:]))
            closest_dist_sq.append(distancias)

        closest_dist_sq = np.array(closest_dist_sq)
        current_pot = closest_dist_sq.sum()
        #print(X)
        #print("closest_dist_sq: ", closest_dist_sq, " current_pot: ", current_pot, " X[center_id, :]: ", X[center_id, :])
        # Pick the remaining n_clusters-1 points
        for c in range(1, n_clusters):
            list_trials = np.random.random(n_local_trials)
            rand_vals = list_trials * current_pot
            #print("list_trials: ", list_trials, " rand_vals: ", rand_vals)
            soma_probs = stable_cumsum(closest_dist_sq)
            candidate_ids = np.searchsorted(soma_probs, rand_vals)
            #print("soma_probs: ", soma_probs,  " candidate_ids: ", candidate_ids)

            # Compute distances to center candidates
            #print("X[candidate_ids]: ", X[candidate_ids])
            distance_to_candidates = np.zeros((len(candidate_ids), len(X[:, 0])))
            for candidato in range(0, len(candidate_ids)):
                for linhaMatriz in range(0, len(X[:,0])):
                    #print("candidato: ", candidato, " line: ", X[candidate_ids[candidato],:])
                    distance_to_candidates[candidato, linhaMatriz] = np.linalg.norm(np.array(X[candidate_ids[candidato],:]) - np.array(X[linhaMatriz,:]))
            
            
            #distance_to_candidates = self.euclidean_distances(X[candidate_ids], X)
            #print(distance_to_candidates)
            # Decide which candidate is the best
            best_candidate = None
            best_pot = None
            best_dist_sq = None
            for trial in range(n_local_trials):
                # Compute potential when including center candidate
                new_dist_sq = np.minimum(closest_dist_sq, distance_to_candidates[trial,:])
                new_pot = new_dist_sq.sum()
                #print(new_dist_sq)
                #print(new_pot)
                # Store result if it is the best local trial so far
                if (best_candidate is None) or (new_pot < best_pot):
                    best_candidate = candidate_ids[trial]
                    best_pot = new_pot
                    best_dist_sq = new_dist_sq

            #print(rand_vals)
            #print(candidate_ids)
            #print(distance_to_candidates)
            # Permanently add best center candidate found in local tries
            centers[c] = X[best_candidate]
            current_pot = best_pot
            closest_dist_sq = best_dist_sq
        return centers


    #def _wasserstein_distance(self, x, y):
    #    # x and y are 1D distributions (e.g., vectors)
    #    x = x.reshape(-1, 1)
    #    y = y.reshape(-1, 1)
    #    a = np.ones((x.shape[0],)) / x.shape[0]
    #    b = np.ones((y.shape[0],)) / y.shape[0]
    #    M = ot.dist(x, y)  # Cost matrix
    #    return ot.emd2(a, b, M)  # Squared Wasserstein distance


    def fit(self, X, weights, Weighted, quad):
        rng = np.random.RandomState(self.random_state)

        n_samples, n_features = X.shape

        ## Randomly choose initial centers
        #initial_idx = rng.choice(n_samples, self.n_clusters, replace=False)
        #centers = X[initial_idx]
        #print(centers)

        centers = self.k_init(X, self.n_clusters)
        #print(centers)
        #exit(1)
        for i in range(self.max_iter):
            # Assign labels based on closest center
            distances = 0
            if(quad):
                #print("Executando Assimetrico Quadratico Weights: ", Weighted)
                distances = (cdist(X, centers, 'euclidean')**2) * weights[:, np.newaxis] if Weighted else cdist(X, centers, 'euclidean')**2
            else:
                #print("Executando Assimetrico Linear  Weights: ", Weighted)
                distances = cdist(X, centers, 'euclidean') * weights[:, np.newaxis] if Weighted else cdist(X, centers, 'euclidean')

            #distances = cdist(X, centers, 'euclidean')
            #distances = distances * weights[:, np.newaxis]
            labels = np.argmin(distances, axis=1)

            #labels = []
            #for i in range(n_samples):
            #    dists = [self._wasserstein_distance(X[i], c) for c in centers]
            #    labels.append(np.argmin(dists))
            #labels = np.array(labels)



            # Compute new centers
            #new_centers = np.array([X[labels == j].mean(axis=0) for j in range(self.n_clusters)])
            new_centers = []
            for j in range(self.n_clusters):
                # Get all points assigned to cluster j
                points_in_cluster = X[labels == j]
                weights_in_cluster = weights[labels == j]

                #print(points_in_cluster, " j: ", j)
                

                # Compute the mean of those points
                if len(points_in_cluster) > 0:
                    center = np.average(points_in_cluster, axis=0, weights=weights_in_cluster) if Weighted else points_in_cluster.mean(axis=0)
                    #center = points_in_cluster.mean(axis=0)
                    #center = np.average(points_in_cluster, axis=0, weights=weights_in_cluster)

                else:
                    # If no points are assigned to the cluster, keep the old center
                    center = centers[j]

                new_centers.append(center)
            # Convert the list to a numpy array
            new_centers = np.array(new_centers)



            # Check for convergence
            center_shift = np.linalg.norm(new_centers - centers)
            if center_shift < self.tol:
                break
            centers = new_centers

        self.cluster_centers_ = centers
        self.labels_ = labels
        #print(self.cluster_centers_)
        #print(self.labels_)
        return self

    def predict(self, X):
        distances = cdist(X, self.cluster_centers_, 'euclidean')
        return np.argmin(distances, axis=1)


    def fit_predict(self, X, weights, Weighted, quad):
        self.fit(X, weights, Weighted, quad)
        return self.labels_

def solve_ilp(X, centroids, size_min, size_max, weights, Weighted , quad):
    n_samples = X.shape[0]
    k = centroids.shape[0]

    # Compute squared distances
    #dist = np.array([[np.sum((x - c) ** 2) for c in centroids] for x in X])
    #print(dist)
    ########### DISTANCIA QUADRATICA
    dist = 0
    if(quad):
        #print("Executando Simetrico Quadratico Weights: ", Weighted)
        dist = (cdist(X, centroids, 'euclidean')**2) *weights[:, np.newaxis] if Weighted else cdist(X, centroids, 'euclidean')**2
    else:
        #print("Executando Simetrico Linear Weights: ", Weighted)
        dist = (cdist(X, centroids, 'euclidean')) *weights[:, np.newaxis] if Weighted else cdist(X, centroids, 'euclidean')

    #print(dist)
    # Decision variables
    #print("n_samples: ", n_samples)
    #print("clusters: ", k)
    z = cp.Variable((n_samples, k), boolean=True)
    #print(z)

    # Objective: minimize total squared distance
    objective = cp.Minimize(cp.sum(cp.multiply(dist, z)))
    #print(objective)
    # Constraints
    constraints = []
    # Each sample assigned to exactly one cluster
    for i in range(n_samples):
        constraints.append(cp.sum(z[i, :]) == 1)

    # Each cluster has size within bounds
    for j in range(k):
        constraints.append(cp.sum(z[:, j]) >= size_min)
        constraints.append(cp.sum(z[:, j]) <= size_max)

    # Solve the problem
    prob = cp.Problem(objective, constraints)
    prob.solve(solver=cp.GLPK_MI)
    #print("Checking z before solving:")
    #print(z)    
    #prob.solve(solver=cp.ECOS_BB)
    #prob.solve(solver=cp.GUROBI)
    #print(z.value)
    #if prob.status != cp.OPTIMAL:
    #    print(f"Solver did not find an optimal solution: {prob.status}")
    #else:
    #    print(z.value.shape)
    labels = []
    if z.value is not None:
        labels = np.argmax(z.value, axis=1)
    else:
        print("Solver did not find a valid solution for z.")
    #print("labels: ", labels)
    return labels

def Myconstrained_kmeans(X, k, size_min, size_max, weights, Weighted , quad, max_iter=10):
    #centroids = initialize_centroids(X, k)
    kmeans = MyKMeans(n_clusters=k, random_state=42)
    centroids = kmeans.k_init(X, k)
    #print("centroids: ", centroids)
    for iteration in range(max_iter):
        # Assignment step via ILP
        labels = solve_ilp(X, centroids, size_min, size_max, weights, Weighted, quad )
        #print("iter: ", iteration, " labels: ", labels)
        # Update centroids
        #new_centroids = np.array([
        #    X[labels == i].mean(axis=0) if np.any(labels == i) else centroids[i]
        #    for i in range(k)
        #])
        new_centroids = []

        # Loop through each cluster (0 to k-1)
        for i in range(k):
            # Get the data points assigned to this cluster
            points_in_cluster = X[labels == i]
            weights_in_cluster = weights[labels == i]
            # If there are points in the cluster, calculate the mean
            if len(points_in_cluster) > 0:
                #new_centroid = points_in_cluster.mean(axis=0)
                new_centroid = np.average(points_in_cluster, axis=0, weights=weights_in_cluster) if Weighted else points_in_cluster.mean(axis=0)

            else:
                # If no points are assigned to this cluster, keep the old centroid
                new_centroid = centroids[i]
            
            # Append the new centroid to the list
            new_centroids.append(new_centroid)

        # Convert the list to a numpy array
        new_centroids = np.array(new_centroids)
        #print("new_centroids: ", new_centroids)
        # Convergence check
        #if np.allclose(centroids, new_centroids):
        diff = np.abs(centroids - new_centroids)
        #print("diff: ", diff)
        #print("diff: ", np.sum(diff))
        if (np.allclose(centroids, new_centroids, atol=0.1)) or (np.sum(diff) == 0):
            print("CLUSTERIZACAO FINALIZADA COM SUCESSO")
            break
        centroids = new_centroids
    return labels, centroids




def percorreArvoreClusterizando_ENA(no_analise, df_arvore, df_vazoes_ENA, df_vazoes, mapa_clusters_estagio, postos, Simetrica, Weighted, pacoteKmeans, quad, plotar = False):
    filhos = getFilhos(no_analise, df_arvore)
    #print("no_analise: ", no_analise, " filhos: ", filhos)
    est = df_arvore.loc[(df_arvore["NO"] == no_analise)]["PER"].iloc[0]
    postos_multi = df_vazoes["NOME_UHE"].unique()
    postos_multi = sorted(postos_multi, reverse=False)

    postos_ENA = df_vazoes_ENA["NOME_UHE"].unique()
    postos_ENA = sorted(postos_ENA, reverse=False)
    print("postos_ENA: ", postos_ENA)
    if(len(filhos) > mapa_clusters_estagio[est]):
        matriz_valores = np.zeros((len(filhos), len(postos_ENA)))
        mapa_linha_no = {}
        mapa_linha_posto = {}
        weights =[]
        for linha, no in enumerate(filhos):  # FIXED: Use enumerate() to track row index
            for coluna, posto in enumerate(postos_ENA):  # FIXED: Same for column index
                vazao = df_vazoes_ENA[(df_vazoes_ENA["NOME_UHE"] == posto) & (df_vazoes_ENA["NO"] == no)]["VAZAO"].iloc[0]
                matriz_valores[linha, coluna] = vazao
                mapa_linha_posto[posto] = coluna
            mapa_linha_no[linha] = no
            weights.append(
                df_arvore.loc[(df_arvore["NO"] == no)]["PROB"].iloc[0]
            )
        weights = np.array(weights)


        matriz_valores_multi = np.zeros((len(filhos), len(postos_multi)))
        mapa_linha_posto_multi = {}
        for linha, no in enumerate(filhos):  # FIXED: Use enumerate() to track row index
            for coluna, posto in enumerate(postos_multi):  # FIXED: Same for column index
                vazao = df_vazoes[(df_vazoes["NOME_UHE"] == posto) & (df_vazoes["NO"] == no)]["VAZAO"].iloc[0]
                matriz_valores_multi[linha, coluna] = vazao
                mapa_linha_posto_multi[posto] = coluna



                #print("no: ", no, " posto: ", posto, " Vazao: ", vazao)
        k = mapa_clusters_estagio[est]
        clusters = []
        if(Simetrica == True):
            size_min = len(filhos) // k  # Minimum number of points per cluster
            size_max = len(filhos) // k  # Maximum number of points per cluster
            #print(filhos)
            #print(df_arvore)
            #print("no_analise: ", no_analise, "len(filhos): ", len(filhos), " k: ", k, " size_min: ", size_min, "size_max: ", size_max, " no_analise: ", no_analise, " est: ", est)
            
            if(pacoteKmeans):
                #print("Executando Pacote Simetrico")
                kmeans = KMeansConstrained(n_clusters=k, size_min=size_min, size_max=size_max, random_state=42, n_init=10)
                clusters = kmeans.fit_predict(matriz_valores)
            else:
                #print("Executando Artesanal Simetrico")
                (clusters, centroids) = Myconstrained_kmeans(matriz_valores, k, size_min, size_max, weights, Weighted , quad)
                #clusters = Myconstrained_kmeans(matriz_valores, k, size_min, size_max)


            #print(clusters)
        else:

            
            #print("K: ", k, " matriz: ", matriz_valores)

            
            if(pacoteKmeans):
                #print("Executando Pacote Assimetrico")
                kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                clusters = kmeans.fit_predict(matriz_valores)
            else:
                #print("Executando Artesanal Assimetrico")
                #kmeans = MyKMeans(n_clusters=k, random_state=42)
                kmeans = MyKMeans(n_clusters=k, random_state=10)
                kmeans = MyKMeans(n_clusters=k, random_state=10)
                clusters= kmeans.fit_predict(matriz_valores, weights, Weighted, quad)

            centers_kmeans = kmeans.cluster_centers_
            #empty_clusters = np.where(cluster_counts == 0)[0]
            #if len(empty_clusters) > 0:
            #    print(f"Empty clusters found: {empty_clusters}")
            #    non_empty_clusters = np.where(cluster_counts > 0)[0]
            #    means_of_non_empty_clusters = []
            #    for cluster in non_empty_clusters:
            #        points_in_cluster = matriz_valores[clusters == cluster]
            #        cluster_mean = np.mean(points_in_cluster, axis=0)
            #        means_of_non_empty_clusters.append(cluster_mean)
            #    for empty_cluster in empty_clusters:
            #        kmeans.cluster_centers_[empty_cluster] = np.mean(means_of_non_empty_clusters, axis=0)
            #exit(1) 

            #print(clusters)
            #print("K: ", k)
            for j in range(k):
                points_in_cluster = np.where(clusters == j)[0]
                #print("points_in_cluster: ", points_in_cluster)
                if len(points_in_cluster) == 0:
                    print(f"Cluster {j} is empty. Fixing it...")
                    distances_to_j = np.linalg.norm(matriz_valores - centers_kmeans[j], axis=1)
                    sorted_indices = np.argsort(distances_to_j)
                    #print(distances_to_j)
                    #print(sorted_indices)
                    for idx in sorted_indices:
                        current_cluster = clusters[idx]
                        if np.sum(clusters == current_cluster) > 1:
                            clusters[idx] = j  # Reassign this point to the empty cluster
                            break
                    # Recalculate centers after fixing
                    new_centers = []
                    for j in range(k):
                        new_centers.append(matriz_valores[clusters == j].mean(axis=0))
                    centers_kmeans = np.array(new_centers)

        #cluster_counts = np.bincount(clusters)
        #print(cluster_counts)

        #new_matrix = np.zeros((len(clusters), len(postos)))
        maior_no = max(df_arvore["NO"].unique())
        #print("matriz_valores: ", matriz_valores)


        #print("k: ", k)
        for i in range(k):
            novo_no = maior_no + i + 1

            #print("clusters: ", clusters)
            lista_linhas_matriz = np.where(clusters == i)[0]
            #print("lista_linhas_matriz: ", lista_linhas_matriz)
            
            lista_nos_cluster = [mapa_linha_no[key] for key in lista_linhas_matriz]
            #print("lista_nos_cluster: ", lista_nos_cluster)

            matriz_cluster = matriz_valores[lista_linhas_matriz,:]
            #print("matriz_cluster 1", matriz_cluster)
            
            matriz_cluster = matriz_valores_multi[lista_linhas_matriz,:]

            #print("matriz_cluster 2", matriz_cluster)
            #exit(1)
            #######################################
            #novas_realizacoes = np.round(matriz_cluster.mean(axis=0), 0).astype(int)  ####### CLUSTER NORMAL AVERAGE
            #################
            ########## CLUSTER WEIGHTED AVERAGE
            save_lines = matriz_cluster*0
            soma_probs = 0
            for indice, no in enumerate(lista_nos_cluster):
                prob = df_arvore.loc[df_arvore["NO"] == no]["PROB"].iloc[0]
                soma_probs += prob
            #print("no_analise: ", no_analise, " soma_probs: ", soma_probs, " total_nos: ", len(lista_nos_cluster))
            for indice, no in enumerate(lista_nos_cluster):
                prob = df_arvore.loc[df_arvore["NO"] == no]["PROB"].iloc[0]/soma_probs
                linha = matriz_cluster[indice,:]
                #if(no_analise == 1502):
                #    print(" prob: ", prob, " mult: ", linha*prob)
                save_lines[indice,:] = linha*prob     
            ########################################

            novas_realizacoes = np.sum(save_lines, axis=0)

            

            df_nos_excluidos = df_arvore[df_arvore["NO"].isin(lista_nos_cluster)].reset_index(drop = True)
            df_arvore = df_arvore[~df_arvore["NO"].isin(lista_nos_cluster)]
            prob_novo_no = df_nos_excluidos["PROB"].sum()
            pai_novo_no = df_nos_excluidos["NO_PAI"].unique()[0]
            per_novo_no = df_nos_excluidos["PER"].unique()[0]
            abertura = i+1

            #for coluna, posto in enumerate(postos):
            for coluna, posto_multi in enumerate(postos_multi):
                df_vaz = pd.DataFrame({"NOME_UHE":[posto_multi], "NO":[novo_no], "VAZAO":[novas_realizacoes[coluna]]})
                df_vazoes = pd.concat([df_vazoes, df_vaz]).reset_index(drop = True)

            ### COMENTE ESSA LINHA PARA IMPRIMIR TAMBEM NO CADASTRO DE VAZOES OS NOS ELIMINADOS ALEM DO NO RESULTANTE
            df_vazoes = df_vazoes[~df_vazoes["NO"].isin(lista_nos_cluster)] 

            df_novo_no = pd.DataFrame({"NO_PAI":[pai_novo_no], "NO":[novo_no], "Abertura":[abertura], "PER":[per_novo_no], "PROB":[prob_novo_no]})
            novos_filhos = df_arvore[(df_arvore["NO_PAI"].isin(df_nos_excluidos["NO"].tolist()))].reset_index(drop = True)
            #print(novos_filhos, "len(df_novo_no[NO].tolist()): ", len(novos_filhos["NO"].tolist()))
            #print(novos_filhos)
            #Repassa probabilidade para frente
            prob_soma = 0
            for idx, row in df_nos_excluidos.iterrows():
                no_excluido = row.NO
                filhos = df_arvore.loc[(df_arvore["NO_PAI"] == no_excluido)].reset_index(drop = True)["NO"].tolist()
                for filho in filhos:
                    prob_old_pai = df_nos_excluidos.loc[df_nos_excluidos["NO"] == no_excluido]["PROB"].iloc[0]
                    #if(no_analise == 1502):
                    #    print("cluster: ", i, " filho: ", filho, " Prob: ", prob_old_pai)
                    df_arvore.loc[df_arvore["NO"] == filho, "PROB"] = prob_old_pai
                    prob_soma += prob_old_pai
            for idx, row in df_nos_excluidos.iterrows():
                no_excluido = row.NO
                #print("no_excluido: ", no_excluido)
                filhos = df_arvore.loc[(df_arvore["NO_PAI"] == no_excluido)].reset_index(drop = True)["NO"].tolist()
                for filho in filhos:
                    #print(df_arvore.loc[(df_arvore["NO"] == filho)])
                    df_arvore.loc[df_arvore["NO"] == filho, "NO_PAI"] = novo_no
                    #df_arvore.loc[df_arvore["NO"] == filho, "PROB"] = round(1/len(novos_filhos["NO"].tolist()),3)
                    df_arvore.loc[df_arvore["NO"] == filho, "PROB"] = round(df_arvore.loc[df_arvore["NO"] == filho, "PROB"]/prob_soma,7)
            #print(no_excluido, " Filhos: ", filhos)
            df_arvore = pd.concat([df_arvore, df_novo_no]).reset_index(drop = True)
            #print("Arvore resultante: ")
            #print(df_arvore)
    #if(no_analise == 1502):
        #exit(1)

    return (df_arvore, df_vazoes)



def reducaoArvoreClusterizacaoENA(mapa_clusters_estagio, df_vazoes_ENA, df_vazoes, df_arvore, Simetrica, perservaFolhas, Weighted, pacoteKmeans, quad, plotar = False):
    
    print("perservaFolhas: ", perservaFolhas)
    print("Weighted: ", Weighted)
    print("pacoteKmeans: ", pacoteKmeans)
    print("quad: ", quad)

    start_time = time.time()
    tempo_Total = time.time()
    
    if(Simetrica == True):
        
        print("Realizando Redução Simetrica - Clustering")
        
    else:
        print("Realizando Redução Assimetrica  - Clustering")
    estagios = df_arvore["PER"].unique()
    estagios = sorted(estagios, reverse=False)[:-1]#[1:]


    if(perservaFolhas):
        estagios.remove(max(estagios))

    for est in estagios:
        #if(est < max(estagios)):
        #    print("est: ", est)
        #if(True):
        nos_estagio = df_arvore.loc[(df_arvore["PER"] == est)]["NO"].tolist()
        for no_cluster in nos_estagio:
            #def percorreArvoreClusterizando(no_analise, df_arvore, df_vazoes, mapa_clusters_estagio, postos, Simetrica, Weighted, pacoteKmeans, quad, plotar = False):
            df_arvore, df_vazoes = percorreArvoreClusterizando_ENA(no_cluster, df_arvore, df_vazoes_ENA, df_vazoes, mapa_clusters_estagio, Simetrica, Weighted, pacoteKmeans, quad, plotar)
    df_arvore.loc[df_arvore["NO"] == 1, "NO_PAI"] = 0
    #df_arvore["NO_PAI"] = df_arvore["NO_PAI"].mask(df_arvore["NO"] == 1, 0)
    end_time = time.time()
    elapsed_time = end_time - start_time  # Calculate elapsed time
    print(f"Tempo de Exeucao da Clusterizacao: {elapsed_time:.4f} seconds")
    start_time = time.time()


    ### COMENTE ESSA LINHA PARA IMPRIMIR TAMBEM NO CADASTRO DE VAZOES OS NOS ELIMINADOS ALEM DO NO RESULTANTE
    df_vazoes = df_vazoes[df_vazoes["NO"].isin(df_arvore["NO"].unique())].reset_index(drop = True)
    return (df_arvore, df_vazoes)







##mapa_clusters_estagio = {
#    1:5,
#    2:5,
#    3:5
##}
##mapa_clusters_estagio = {
#    1:3,
#    2:3,
#    3:3
##}
##mapa_clusters_estagio = {
#    1:2,
#    2:2
##}
##mapa_clusters_estagio = {
#    1:2,
#    2:2,
#    3:2
##}
##mapa_clusters_estagio = {
#    1:3,
#    2:3,
#    3:3
#}
#arquivo_vazoes = caso+"\\cenarios.csv"
#df_vazoes = pd.read_csv(arquivo_vazoes)
#df_vazoes.to_csv("..\\saidas\\ClusterAssimetrico\\vazoes_estudo.csv", index=False)
#arquivo_estrutura_feixes = caso+"\\arvore.csv"
#df_arvore = pd.read_csv(arquivo_estrutura_feixes)
#df_arvore.to_csv("..\\saidas\\ClusterAssimetrico\\arvore_estudo.csv", index=False)
#df_arvore_original = df_arvore.copy()
#Simetrica = False
#df_arvore, df_vazoes = reducaoArvoreClusterizacao(caso, mapa_clusters_estagio, df_vazoes, df_arvore, Simetrica)
