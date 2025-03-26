import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import os
import pandas as pd
import numpy as np
import networkx as nx
import pydot
import matplotlib.pyplot as plt
from anytree import Node, RenderTree
import time
from joblib import Parallel, delayed, parallel_backend
from k_means_constrained import KMeansConstrained
import os
os.environ["LOKY_MAX_CPU_COUNT"] = "4"  # Adjust based on your CPU
os.environ["PATH"] += os.pathsep + r"C:\\Program Files (x86)\\Graphviz\\bin"
#from numba import jit
from itertools import combinations  # Efficiently generate unique (i, j) pairs
from scipy.stats import skew

start_time = time.time()
tempo_Total = time.time()
caso = "..\\..\\Mestrado\\caso_1D"
#caso = "..\\..\\casos\\Mestrado\\caso_2D"
caso = "..\\..\\casos\\Mestrado\\caso_construcaoArvore_8cen"
caso = "..\\..\\Dissertacao\\apresentacaoCarmen\\caso_mini"
#caso = "..\\..\\Mestrado\\caso_construcaoArvore_SIN"
#caso = "..\\..\\Mestrado\\caso_construcaoArvore_SIN_2000cen"
#caso = "..\\..\\Mestrado\\caso_construcaoArvore_SIN_1000cen"
#caso = "..\\..\\Mestrado\\caso_construcaoArvore_SIN_500cen"
#caso = "..\\..\\Mestrado\\caso_construcaoArvore_SIN_500cen_ENASIN"
#caso = "..\\..\\Mestrado\\caso_construcaoArvore_SIN_50cen"
#caso = "..\\..\\Mestrado\\teste_wellington"

arquivo_vazoes = caso+"\\vazao_feixes.csv"
#arquivo_vazoes = caso+"\\ena_feixes.csv"
df_vazoes = pd.read_csv(arquivo_vazoes)
print(df_vazoes)
df_vazoes.to_csv("saidas_ArvoreSimetrica\\vazoes_estudo.csv", index=False)

arquivo_probabilidades = caso+"\\probabilidades_feixes.csv"
df_probs = pd.read_csv(arquivo_probabilidades)
arquivo_estrutura_feixes = caso+"\\arvore_julia.csv"
df_arvore = pd.read_csv(arquivo_estrutura_feixes)
df_arvore["PROB"] = df_probs["PROBABILIDADE"]
df_arvore = df_arvore.drop(columns = "VAZAO")
print(df_arvore)
df_arvore.to_csv("saidas_ArvoreSimetrica\\arvore_estudo.csv", index=False)
df_arvore_original = df_arvore.copy()

estagios = df_arvore["PER"].unique()
estagios = sorted(estagios, reverse=False)[:-1]#[1:]
postos = df_vazoes["NOME_UHE"].unique()
postos = sorted(postos, reverse=False)


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


## CLUSTERIZACAO PARA OS FILHOS DOS NOS EM DETERMINADO ESTAGIO
mapa_clusters_estagio = {
    1:2,
    2:2,
    3:2
}
mapa_clusters_estagio = {
    1:5,
    2:5,
    3:5
}

def percorreArvoreClusterizando(no_analise, df_arvore, df_vazoes, mapa_clusters_estagio):
    filhos = getFilhos(no_analise, df_arvore)
    
    print("no_analise: ", no_analise, " filhos: ", filhos)
    est = df_arvore.loc[(df_arvore["NO"] == no_analise)]["PER"].iloc[0]
    if(len(filhos) > mapa_clusters_estagio[est]):
        matriz_valores = np.zeros((len(filhos), len(postos)))
        mapa_linha_no = {}
        for linha, no in enumerate(filhos):  # FIXED: Use enumerate() to track row index
            for coluna, posto in enumerate(postos):  # FIXED: Same for column index
                vazao = df_vazoes[(df_vazoes["NOME_UHE"] == posto) & (df_vazoes["NO"] == no)]["VAZAO"].iloc[0]
                matriz_valores[linha, coluna] = vazao
                mapa_linha_no[linha] = no
                #print("no: ", no, " posto: ", posto, " Vazao: ", vazao)
        k = mapa_clusters_estagio[est]
        #kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        #clusters = kmeans.fit_predict(matriz_valores)

        # Perform balanced K-Means clustering
        size_min = len(filhos) // k  # Minimum number of points per cluster
        size_max = len(filhos) // k  # Maximum number of points per cluster
        # Use KMeansConstrained for balanced clustering
        kmeans = KMeansConstrained(n_clusters=k, size_min=size_min, size_max=size_max, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(matriz_valores)
        #print("Cluster assignments:", clusters)
        #print(clusters)
        new_matrix = np.zeros((len(clusters), len(postos)))
        #for cluster_id, nodes in clusters.items():
        #    new_matrix[cluster_id, :] = original_matrix[nodes, :].mean(axis=0)
        #print(matriz_valores)
        # Print results
        maior_no = max(df_arvore["NO"].unique())
        #print("maior_no: ", maior_no)
        #print("mapa_linha_no: ", mapa_linha_no)
        for i in range(k):
            novo_no = maior_no + i + 1
            lista_linhas_matriz = np.where(clusters == i)[0]
            #print("lista_linhas_matriz: ", lista_linhas_matriz)
            
            lista_nos_cluster = [mapa_linha_no[key] for key in lista_linhas_matriz]
            #print("lista_nos_cluster: ", lista_nos_cluster)

            matriz_cluster = matriz_valores[lista_linhas_matriz,:]
            novas_realizacoes = np.round(matriz_cluster.mean(axis=0), 0).astype(int)
            print("novas_realizacoes: ", novas_realizacoes)
            #print(f"Cluster {i} node {novo_no}: Lines assigned ->", np.where(clusters == i)[0], " Nodes: ", lista_nos_cluster)
            #print(matriz_cluster)
            df_nos_excluidos = df_arvore[df_arvore["NO"].isin(lista_nos_cluster)].reset_index(drop = True)
            df_arvore = df_arvore[~df_arvore["NO"].isin(lista_nos_cluster)]
            prob_novo_no = df_nos_excluidos["PROB"].sum()
            pai_novo_no = df_nos_excluidos["NO_PAI"].unique()[0]
            per_novo_no = df_nos_excluidos["PER"].unique()[0]
            abertura = i+1

            for coluna, posto in enumerate(postos):
                df_vaz = pd.DataFrame({"NOME_UHE":[posto], "NO":[novo_no], "VAZAO":[novas_realizacoes[coluna]]})
                df_vazoes = pd.concat([df_vazoes, df_vaz]).reset_index(drop = True)

            ### COMENTE ESSA LINHA PARA IMPRIMIR TAMBEM NO CADASTRO DE VAZOES OS NOS ELIMINADOS ALEM DO NO RESULTANTE
            df_vazoes = df_vazoes[~df_vazoes["NO"].isin(lista_nos_cluster)] 

            df_novo_no = pd.DataFrame({"NO_PAI":[pai_novo_no], "NO":[novo_no], "Abertura":[abertura], "PER":[per_novo_no], "PROB":[prob_novo_no]})
            novos_filhos = df_arvore[(df_arvore["NO_PAI"].isin(df_nos_excluidos["NO"].tolist()))].reset_index(drop = True)
            #print(novos_filhos, "len(df_novo_no[NO].tolist()): ", len(novos_filhos["NO"].tolist()))

            
            for idx, row in df_nos_excluidos.iterrows():
                no_excluido = row.NO
                filhos = df_arvore.loc[(df_arvore["NO_PAI"] == no_excluido)].reset_index(drop = True)["NO"].tolist()
                for filho in filhos:
                    df_arvore.loc[df_arvore["NO"] == filho, "NO_PAI"] = novo_no
                    df_arvore.loc[df_arvore["NO"] == filho, "PROB"] = 1/len(novos_filhos["NO"].tolist())
                print(no_excluido, " Filhos: ", filhos)
            df_arvore = pd.concat([df_arvore, df_novo_no]).reset_index(drop = True)
            print("Arvore resultante: ")
            print(df_arvore)
    return (df_arvore, df_vazoes)

for est in estagios:
    nos_estagio = df_arvore.loc[(df_arvore["PER"] == est)]["NO"].tolist()
    print("est: ", est, " nos_estagio: ", nos_estagio)
    for no_cluster in nos_estagio:
        df_arvore, df_vazoes = percorreArvoreClusterizando(no_cluster, df_arvore, df_vazoes, mapa_clusters_estagio)
    print(df_arvore)


printaArvore("saidas_ArvoreSimetrica\\Arvore_reduzida", df_arvore)
print(df_arvore)
print(df_vazoes)

df_arvore.to_csv("saidas_ArvoreSimetrica\\df_arvore_reduzida.csv", index=False)
df_vazoes.to_csv("saidas_ArvoreSimetrica\\df_vazoes_reduzida.csv", index=False)

exit(1)
## Example: 10 nodes, each with 180 measurements
##data = np.random.rand(10, 5)  # Replace with your actual data
##print(data)
## Normalize data
##scaler = StandardScaler()
##data_scaled = scaler.fit_transform(data)
#
## Apply k-means with 4 clusters
#k = 4
#kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
#clusters = kmeans.fit_predict(data_scaled)
#
## Print results
#for i in range(k):
#    print(f"Cluster {i}: Nodes assigned ->", np.where(clusters == i)[0])