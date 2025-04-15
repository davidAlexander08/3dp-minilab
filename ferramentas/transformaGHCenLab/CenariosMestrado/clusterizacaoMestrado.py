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



def calcula_prodt_65(codigo_usi, df_hidr):
    df_hidr_uhe = df_hidr.loc[(df_hidr["codigo_usina"] == codigo_usi)]
    vol_65 = (df_hidr_uhe["volume_maximo"].iloc[0] - df_hidr_uhe["volume_minimo"].iloc[0])*0.65 + df_hidr_uhe["volume_minimo"].iloc[0]
    vol_cota_A0 = df_hidr_uhe["a0_volume_cota"].iloc[0]
    vol_cota_A1 = df_hidr_uhe["a1_volume_cota"].iloc[0]*vol_65
    vol_cota_A2 = df_hidr_uhe["a2_volume_cota"].iloc[0]*vol_65**2
    vol_cota_A3 = df_hidr_uhe["a3_volume_cota"].iloc[0]*vol_65**3
    vol_cota_A4 = df_hidr_uhe["a4_volume_cota"].iloc[0]*vol_65**4
    cota_med_fuga = df_hidr_uhe["canal_fuga_medio"].iloc[0]
    perdas = df_hidr_uhe["perdas"].iloc[0]
    prodt_esp = df_hidr_uhe["produtibilidade_especifica"].iloc[0]
    cota_65 = vol_cota_A0 + vol_cota_A1 + vol_cota_A2 + vol_cota_A3 + vol_cota_A4
    fprodt_65 = (cota_65 - cota_med_fuga - perdas)*prodt_esp
    return fprodt_65


def encontraUsinaJusante(codigo_usi, df_confhd):
    df_conf_uhe = df_confhd.loc[(df_confhd["codigo_usina"] == codigo_usi)].reset_index(drop = True)
    return df_conf_uhe["codigo_usina_jusante"].iloc[0]
    
def calcula_prodt_acum_65(codigo_usi, df_confhd, df_hidr):
    usi_jusante = codigo_usi
    prodt = calcula_prodt_65(codigo_usi, df_hidr)
    #print("codigo_usi: ", codigo_usi, " prodt: ", prodt)
    while (usi_jusante != 0):
        usi_jusante = encontraUsinaJusante(usi_jusante, df_confhd)
        if(usi_jusante != 0):
            prodt += calcula_prodt_65(usi_jusante, df_hidr)
            #print("usi_jusante: ", usi_jusante, " prodt: ", prodt)
    return prodt





df_confhd = Confhd.read("C:\\Users\\testa\\Documents\\CenariosFelipe\\cenarios_2020_01\\deck_newave_2020_01\\CONFHD.dat").usinas
df_hidr = Hidr.read("C:\\Users\\testa\\Documents\\CenariosFelipe\\cenarios_2020_01\\deck_newave_2020_01\\HIDR.dat").cadastro
df_hidr = df_hidr.reset_index()
# Marca o tempo de início
inicio = time.time()
os.environ["LOKY_MAX_CPU_COUNT"] = "4" 

caminho = "C:\\Users\\testa\\Documents\\mestrado\\ResultadosDissertacao\\"
df_resultante = pd.read_parquet(caminho+"cenarios_GhcenSemanais_5.parquet", engine = "pyarrow")
postos = df_resultante["posto"].unique()
print(postos)
print(df_resultante)


lista_df_ena = []
for posto in postos:
    df_conf_uhe = df_confhd.loc[(df_confhd["posto"] == posto)].reset_index(drop = True)
    if(not df_conf_uhe.empty):
        codigo_usi = df_conf_uhe["codigo_usina"].iloc[0]
        fprodt_acum_65 = calcula_prodt_acum_65(codigo_usi, df_confhd,  df_hidr)
        df_uhe = df_resultante.loc[(df_resultante["posto"] == posto)].reset_index(drop = True)
        df_ena = df_uhe.copy()
        df_ena["ENA"] = fprodt_acum_65*df_uhe["previsao_incremental"]
        df_ena["ENA"] = df_ena["ENA"].round(0)
        lista_df_ena.append(df_ena)
        print("uhe: ", posto, " fprodt_acum_65: ", fprodt_acum_65)

df_resultante_ena = pd.concat(lista_df_ena).reset_index(drop = True)

####### ENA COM SOMA TEMPORAL
df_ena_summed = df_resultante_ena.groupby(['cenario', 'posto']).agg({ 'ENA': 'sum'}).reset_index()
df_ena_summed['ENA'] = df_ena_summed['ENA'].round(0).reset_index(drop = True)
print("df_ena_summed: ", df_ena_summed)

####### ENA COM SOMA TEMPORAL E ESPACIAL
df_ena_total = df_resultante_ena.groupby('cenario')['ENA'].sum().reset_index()
df_ena_total['ENA'] = df_ena_total['ENA'].round(0)
df_ena_total = df_ena_total.rename(columns={'ENA': 'ENA_SUM'})
print(df_ena_total)

postos = df_resultante["posto"].unique()
cenarios = df_resultante["cenario"].unique()
print("postos: ", postos , " tamanho: ", len(postos))
print("cenarios: ", cenarios , " tamanho: ", len(cenarios))


def distanceBetweenLists(list1, list2):
    # Ensure the lists are of the same length
    if len(list1) != len(list2):
        raise ValueError("The lists must have the same length")
   # Initialize distance
    distance = 0
    # Calculate the sum of squared differences
    for i in range(len(list1)):
        distance += (list1[i] - list2[i]) ** 2
    # Return the square root of the sum of squared differences
    return math.sqrt(distance)



lista_df_GhCen = []
inicio_est = time.time()
matriz_valores = np.zeros(len(cenarios))
mapa_linha_no = {}
for linha, no in enumerate(cenarios):  # FIXED: Use enumerate() to track row index
    df_temp = df_ena_total[(df_ena_total["cenario"] == no)]["ENA_SUM"]
    if(not df_temp.empty):
        vazao = df_temp.iloc[0]
        matriz_valores[linha] = vazao
    print(linha, " ", no, " total: ", len(cenarios))
    mapa_linha_no[linha] = no
        #print("no: ", no, " posto: ", posto, " Vazao: ", vazao)
print(matriz_valores)
print(mapa_linha_no)
num_rows = matriz_valores.shape[0]
#print("Number of columns:", num_columns)
print("Number of columns:", num_rows)
print(matriz_valores)

#matriz_valores = np.array(matriz_valores)

matriz_valores = np.array(matriz_valores).reshape(-1, 1)
#clusters = kmeans.fit_predict(matriz_array)

k = 500
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


print(matriz_valores)

new_matrix = np.zeros((len(clusters)))
n_total_cenarios = 0
contador_series = 1
for i in range(k):
    lista_linhas_matriz = np.where(clusters == i)[0]
    map_from_0_to_total = {i: lista_linhas_matriz[i] for i in range(len(lista_linhas_matriz))}

    matriz_cluster = matriz_valores[lista_linhas_matriz]
    print(matriz_cluster)

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
        new_matrix[i] = matriz_cluster[min_row]
        lista_representante = matriz_cluster[min_row]
        cenario_representante = map_from_0_to_total[min_row]
    else:
        lista_representante = kmeans.cluster_centers_[i]
        cenario_representante = 0
        print(kmeans.cluster_centers_[i])

    print("lista_representante: ", lista_representante , " cenario_representante: ", cenario_representante, " cenario_original: ", mapa_linha_no[cenario_representante])
    df_representante = df_resultante.loc[df_resultante["cenario"] == mapa_linha_no[cenario_representante]]
    df_representante["serie"] = contador_series
    contador_series += 1
    lista_df_GhCen.append(df_representante)

df_cenariosFinais = pd.concat(lista_df_GhCen).reset_index(drop = True)
df_cenariosFinais.rename(columns={"V1": "valor"}, inplace=True)
print(df_cenariosFinais)
df_cenariosFinais.to_csv('cenarios_semanais.csv', index=False)
df_cenariosFinais.to_parquet('cenarios_semanais.parquet', index=False)
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