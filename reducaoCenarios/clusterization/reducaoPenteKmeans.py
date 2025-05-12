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
def retorna_lista_caminho(no, df_arvore):
    lista = [no]
    no_inicial = no
    periodo_no = df_arvore[df_arvore["NO"] == no]["PER"].values[0]
    for _ in range(periodo_no - 1):
        pai = busca_pai(no_inicial, df_arvore)
        lista.append(pai)
        no_inicial = pai
    return lista





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

def caminho_futuro_pente(no, df_arvore, lista_caminho):
    filhos = getFilhos(no, df_arvore)
    if(len(filhos == 1)):
        lista_caminho.append(filhos[0])
        caminho_futuro_pente(filhos[0], df_arvore, lista_caminho)
    elif(len(filhos) == 0):
        return lista_caminho
    else:
        print("REDUCAO PENTE ERRADA, NO COM MAIS DE UM FILHO")
        exit(1)

def percorreArvoreClusterizando(no_analise, df_arvore, df_vazoes, mapa_clusters_estagio, postos, Simetrica, Weighted, pacoteKmeans, quad, plotar = False):
    filhos = getFilhos(no_analise, df_arvore)
    #print("no_analise: ", no_analise, " filhos: ", filhos)
    est = df_arvore.loc[(df_arvore["NO"] == no_analise)]["PER"].iloc[0]
    estagios = df_arvore["PER"].unique()
    estagios = list(estagios)
    estagios.remove(1)

    mapa_linha_no = {}
    mapa_linha_no_avaliado = {}
    mapa_coluna_posto = {}
    weights =[]
    mapaMatrixes_Weights = {}
    matriz_valores = np.zeros((len(filhos), len(postos)*len(estagios)))
    for linha, no in enumerate(filhos):  # FIXED: Use enumerate() to track row index
        lista_caminho = []
        lista_caminho.append(no)
        caminho_futuro_pente(no, df_arvore, lista_caminho)
        #print(lista_caminho)
        
        coluna = 0
        for col_1, no_avaliacao in enumerate(lista_caminho):
            for col_2, posto in enumerate(postos):  # FIXED: Same for column index
                #coluna = col_1 + col_2
                vazao = df_vazoes[(df_vazoes["NOME_UHE"] == posto) & (df_vazoes["NO"] == no_avaliacao)]["VAZAO"].iloc[0]
                matriz_valores[linha, coluna] = vazao
                mapa_coluna_posto[col_2] = posto
                coluna += 1
            mapa_linha_no_avaliado[col_1] = no_avaliacao
        mapa_linha_no[linha] = no
        prob_weight = df_arvore.loc[(df_arvore["NO"] == no)]["PROB"].iloc[0]
        weights.append(prob_weight)
        mapaMatrixes_Weights[linha] = prob_weight
    #print(matriz_valores)

    weights = np.array(weights)
    #print("weights: ", weights)
    k = mapa_clusters_estagio[est]
    clusters = []
    
    if(pacoteKmeans):
        #print("Executando Pacote Assimetrico")
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(matriz_valores)
    else:
        #print("Executando Artesanal Assimetrico")
        #kmeans = MyKMeans(n_clusters=k, random_state=42)
        kmeans = MyKMeans(n_clusters=k, random_state=96)
        #kmeans = MyKMeans(n_clusters=k, random_state=42)
        #kmeans = MyKMeans(n_clusters=k, random_state=55)
        #kmeans = MyKMeans(n_clusters=k, random_state=84)
        clusters= kmeans.fit_predict(matriz_valores, weights, Weighted, quad)

        centers_kmeans = kmeans.cluster_centers_
        print(clusters)
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

    
    #print("matriz_valores: ", matriz_valores)
    #print("k: ", k)
    for i in range(k):
        maior_no = max(df_arvore["NO"].unique())
        novo_no = maior_no + i + 1
        #print("clusters: ", clusters)
        lista_linhas_matriz = np.where(clusters == i)[0]
        #print("lista_linhas_matriz: ", lista_linhas_matriz)

        lista_nos_cluster = [mapa_linha_no[key] for key in lista_linhas_matriz]
        #print("lista_nos_cluster: ", lista_nos_cluster)

        matriz_cluster = matriz_valores[lista_linhas_matriz,:]
        #print(lista_linhas_matriz)
        #print(matriz_cluster)

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
        #print("novas_realizacoes: ", novas_realizacoes)

        lista_exclusao = []
        for no_cluster in lista_nos_cluster:
            lista_caminho = []
            lista_caminho.append(no_cluster)
            caminho_futuro_pente(no_cluster, df_arvore, lista_caminho)
            #print(lista_caminho)
            lista_exclusao = lista_exclusao + lista_caminho
        df_nos_excluidos = df_arvore[df_arvore["NO"].isin(lista_nos_cluster)].reset_index(drop = True)
        df_arvore = df_arvore[~df_arvore["NO"].isin(lista_exclusao)]
        abertura = i+1


        coluna = 0
        no_aux = novo_no
        lista_nos_novos = []
        for col_1, no_avaliacao in enumerate(lista_caminho):
            for col_2, posto in enumerate(postos):  # FIXED: Same for column index
                #coluna = col_1 + col_2
                df_vaz = pd.DataFrame({"NOME_UHE":[posto], "NO":[no_aux], "VAZAO":[novas_realizacoes[coluna]]})
                df_vazoes = pd.concat([df_vazoes, df_vaz]).reset_index(drop = True)
                coluna += 1
            lista_nos_novos.append(no_aux)
            no_aux += 1
        ### COMENTE ESSA LINHA PARA IMPRIMIR TAMBEM NO CADASTRO DE VAZOES OS NOS ELIMINADOS ALEM DO NO RESULTANTE
        df_vazoes = df_vazoes[~df_vazoes["NO"].isin(lista_exclusao)] 
        #print(lista_nos_novos)
        #print("soma_probs: ", soma_probs)
        
        for index, no_criado in enumerate(lista_nos_novos):
            if(index == 0):
                per = 2
                no_anterior = 1
                prob_ = soma_probs
                
            else:
                per = per + 1
                prob_ = 1
            df_novo_no = pd.DataFrame({"NO_PAI":[no_anterior], "NO":[no_criado], "Abertura":[abertura], "PER":[per], "PROB":[prob_]})
            no_anterior = no_criado
            df_arvore = pd.concat([df_arvore, df_novo_no]).reset_index(drop = True)
    return (df_arvore, df_vazoes)



def reducaoArvoreClusterizacaoPente(mapa_clusters_estagio, df_vazoes, df_arvore, Simetrica, perservaFolhas, Weighted, pacoteKmeans, quad, plotar = False):
    
    start_time = time.time()
    tempo_Total = time.time()
    
    estagios = df_arvore["PER"].unique()
    estagios = sorted(estagios, reverse=False)[:-1]#[1:]
    postos = df_vazoes["NOME_UHE"].unique()
    postos = sorted(postos, reverse=False)

    for est in [min(estagios)]:
        nos_estagio = df_arvore.loc[(df_arvore["PER"] == est)]["NO"].tolist()
        for no_cluster in nos_estagio:
            df_arvore, df_vazoes = percorreArvoreClusterizando(no_cluster, df_arvore, df_vazoes, mapa_clusters_estagio, postos, Simetrica, Weighted, pacoteKmeans, quad, plotar)
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
