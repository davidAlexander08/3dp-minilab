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











def percorreArvoreClusterizando(no_analise, df_arvore, df_vazoes, mapa_clusters_estagio, postos, Simetrica):
    filhos = getFilhos(no_analise, df_arvore)
    #print("no_analise: ", no_analise, " filhos: ", filhos)
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

        if(Simetrica == True):
            size_min = len(filhos) // k  # Minimum number of points per cluster
            size_max = len(filhos) // k  # Maximum number of points per cluster
            kmeans = KMeansConstrained(n_clusters=k, size_min=size_min, size_max=size_max, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(matriz_valores)
        else:
            #print("K: ", k, " matriz: ", matriz_valores)
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(matriz_valores)

        new_matrix = np.zeros((len(clusters), len(postos)))
        maior_no = max(df_arvore["NO"].unique())
        for i in range(k):
            novo_no = maior_no + i + 1
            lista_linhas_matriz = np.where(clusters == i)[0]
            #print("lista_linhas_matriz: ", lista_linhas_matriz)
            
            lista_nos_cluster = [mapa_linha_no[key] for key in lista_linhas_matriz]
            #print("lista_nos_cluster: ", lista_nos_cluster)

            matriz_cluster = matriz_valores[lista_linhas_matriz,:]
            novas_realizacoes = np.round(matriz_cluster.mean(axis=0), 0).astype(int)
            #print("novas_realizacoes: ", novas_realizacoes)
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
            #print(novos_filhos)
            #Repassa probabilidade para frente
            prob_soma = 0
            for idx, row in df_nos_excluidos.iterrows():
                no_excluido = row.NO
                filhos = df_arvore.loc[(df_arvore["NO_PAI"] == no_excluido)].reset_index(drop = True)["NO"].tolist()
                for filho in filhos:
                    prob_old_pai = df_nos_excluidos.loc[df_nos_excluidos["NO"] == no_excluido]["PROB"].iloc[0]
                    #print("filho: ", filho, " Prob: ", prob_old_pai)
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
                    df_arvore.loc[df_arvore["NO"] == filho, "PROB"] = round(df_arvore.loc[df_arvore["NO"] == filho, "PROB"]/prob_soma,4)
            #print(no_excluido, " Filhos: ", filhos)
            df_arvore = pd.concat([df_arvore, df_novo_no]).reset_index(drop = True)
            #print("Arvore resultante: ")
            #print(df_arvore)
    return (df_arvore, df_vazoes)



def reducaoArvoreClusterizacao(mapa_clusters_estagio, df_vazoes, df_arvore, Simetrica):
    start_time = time.time()
    tempo_Total = time.time()
    
    if(Simetrica == True):
        
        print("Realizando Redução Simetrica - Clustering")
        
    else:
        print("Realizando Redução Assimetrica  - Clustering")
    estagios = df_arvore["PER"].unique()
    estagios = sorted(estagios, reverse=False)[:-1]#[1:]
    postos = df_vazoes["NOME_UHE"].unique()
    postos = sorted(postos, reverse=False)
    for est in estagios:
        nos_estagio = df_arvore.loc[(df_arvore["PER"] == est)]["NO"].tolist()
        for no_cluster in nos_estagio:
            df_arvore, df_vazoes = percorreArvoreClusterizando(no_cluster, df_arvore, df_vazoes, mapa_clusters_estagio, postos, Simetrica)
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
