# Codigo transforma ECO
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import MiniBatchKMeans
import math
import os
import time
from inewave.newave import Confhd
from inewave.newave import Hidr
import json
import random

inicio = time.time()
os.environ["LOKY_MAX_CPU_COUNT"] = "4" 

caminho = "C:\\Users\\testa\\Documents\\mestrado\\ResultadosDissertacao\\"
df_resultante = pd.read_parquet("cenarios_GhcenSemanais_4.parquet", engine = "pyarrow")
postos = df_resultante["posto"].unique()
print(postos)
print(df_resultante)

postos = df_resultante["posto"].unique()

cenarios = df_resultante["cenario"].unique()
print("postos: ", postos , " tamanho: ", len(postos))
print("cenarios: ", cenarios , " tamanho: ", len(cenarios))
selected = random.sample(list(cenarios), 8)
print(selected)
lista_sorteio = []
serie = 1
for elemento in selected:
    df = df_resultante.loc[(df_resultante["cenario"] == elemento)].reset_index(drop = True)
    df["serie"] = serie
    lista_sorteio.append(df)
    serie += 1
print(lista_sorteio)
df_final = pd.concat(lista_sorteio).reset_index(drop = True)
print(df_final)
df_final.to_csv('cenarios_semanais_sorteio_4sem_8cen_toy.csv', index=False)
df_final.to_parquet('cenarios_semanais_sorteio_4sem_8cen_toy.parquet', index=False)
fim = time.time()
tempo_execucao = fim - inicio
minutos = int(tempo_execucao // 60)
segundos = int(tempo_execucao % 60)
print(f"Tempo de execução: {minutos} minutos e {segundos} segundos")
















exit(1)
lista_df_GhCen = []
inicio_est = time.time()
matriz_valores = np.zeros((len(cenarios), len(postos)))
mapa_linha_no = {}
for linha, no in enumerate(cenarios):  # FIXED: Use enumerate() to track row index
    for coluna, posto in enumerate(postos):  # FIXED: Same for column 

        #print("no: ",no, " posto: ", posto)
        #print(df_ena_summed[(df_ena_summed["posto"] == posto) & (df_ena_summed["cenario"] == no)]["ENA"])
        df_temp = df_ena_summed[(df_ena_summed["posto"] == posto) & (df_ena_summed["cenario"] == no)]["ENA"]
        if(not df_temp.empty):
            vazao = df_temp.iloc[0]
            matriz_valores[linha, coluna] = vazao
    print(linha, " ", no, " total: ", len(cenarios))
    mapa_linha_no[linha] = no
        #print("no: ", no, " posto: ", posto, " Vazao: ", vazao)
print(matriz_valores)
num_columns = matriz_valores.shape[1]
num_rows = matriz_valores.shape[0]
#print("Number of columns:", num_columns)
#print("Number of columns:", num_rows)
print(matriz_valores)
exit(1)
k = 200
#print("K: ", k, " matriz: ", matriz_valores)
kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
clusters = kmeans.fit_predict(matriz_valores)
#kmeans = MiniBatchKMeans(n_clusters=200, random_state=42, batch_size=256, n_init=10)
#clusters = kmeans.fit_predict(matriz_valores)
cluster_counts = np.bincount(clusters)
empty_clusters = np.where(cluster_counts == 0)[0]
if len(empty_clusters) > 0:
    print(f"Empty clusters found: {empty_clusters}")
    non_empty_clusters = np.where(cluster_counts > 0)[0]
    means_of_non_empty_clusters = []
    for cluster in non_empty_clusters:
        points_in_cluster = matriz_valores[clusters == cluster]
        cluster_mean = np.mean(points_in_cluster, axis=0)
        means_of_non_empty_clusters.append(cluster_mean)
    for empty_cluster in empty_clusters:
        kmeans.cluster_centers_[empty_cluster] = np.mean(means_of_non_empty_clusters, axis=0)


#print("Unique clusters:", len(set(clusters)))  # Should be 200
new_matrix = np.zeros((len(clusters), len(postos)))
n_total_cenarios = 0
for i in range(k):
    lista_linhas_matriz = np.where(clusters == i)[0]
    map_from_0_to_total = {i: lista_linhas_matriz[i] for i in range(len(lista_linhas_matriz))}

    matriz_cluster = matriz_valores[lista_linhas_matriz,:]
    centroid = kmeans.cluster_centers_[i]
    num_rows = matriz_cluster.shape[0]
    #print("Est: ", est, " Calc. Cen: ", i, " No Cenarios no Cluster: ", num_rows)
    n_total_cenarios += num_rows
    mapa_linhas_distanciaCentroi = {}
    for row in range(num_rows):
        mapa_linhas_distanciaCentroi[row] = [distanceBetweenLists(matriz_cluster[row,:], centroid)]

    if(num_rows != 0):
        min_row = min(mapa_linhas_distanciaCentroi, key=mapa_linhas_distanciaCentroi.get)      
        #novas_realizacoes = np.round(matriz_cluster.mean(axis=0), 0).astype(int)
        new_matrix[i,:] = matriz_cluster[min_row,:]
        lista_representante = matriz_cluster[min_row,:]
        cenario_representante = map_from_0_to_total[min_row]
    else:
        lista_representante = kmeans.cluster_centers_[i]
        cenario_representante = 0
        print(kmeans.cluster_centers_[i])
    for coluna, posto in enumerate(postos):
        lista_df_GhCen.append(
            pd.DataFrame({
                "data":[est],
                "posto":[posto],
                "cenario":[i+1],
                "representante":[cenario_representante],
                "valor":[lista_representante[coluna]]

            })
        )
fim_est = time.time()
tempo_execucao_est = fim_est - inicio_est
minutos = int(tempo_execucao_est // 60)
segundos = int(tempo_execucao_est % 60)
tempo_execucao_tot = fim_est - inicio
minutos_tot = int(tempo_execucao_tot // 60)
segundos_tot = int(tempo_execucao_tot % 60)
print("Finalizou Estágio: ", est, " total de Cenários Avaliados: ", n_total_cenarios)
print(f"Tempo de execução do estagio: {minutos} minutos e {segundos} segundos")
print(f"Tempo de execução total: {minutos_tot} minutos e {segundos_tot} segundos")
print("Proceso Finalizado")

df_cenariosFinais = pd.concat(lista_df_GhCen).reset_index(drop = True)
df_cenariosFinais.to_csv('cenarios_finais.csv', index=False)
df_cenariosFinais.to_parquet('cenarios_finais.parquet', index=False)
fim = time.time()
tempo_execucao = fim - inicio
minutos = int(tempo_execucao // 60)
segundos = int(tempo_execucao % 60)
print(f"Tempo de execução: {minutos} minutos e {segundos} segundos")