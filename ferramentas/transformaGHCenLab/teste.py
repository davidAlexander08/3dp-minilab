# Codigo transforma ECO
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import MiniBatchKMeans
import math
import os
from datetime import timedelta  # <-- Add this import at the top of your script

import time


df = pd.read_csv("previsaoM_inc_semTV_2020_01.csv", sep=";")
print(df)
postos = df["postos"].unique()
print(postos)
print("TOTAL POSTOS: ", len(postos))
print(df.loc[(df["postos"] == 266)])
print(df.loc[(df["postos"] == 66)])

df_2 = pd.read_parquet("CenariosMestrado\\cenarios_GhcenSemanais_4.parquet", engine = "pyarrow")
print(df_2)
postos_2 = df_2["posto"].unique()
print(postos_2)
print("TOTAL POSTOS: ", len(postos_2))
print(df_2.loc[(df_2["posto"] == 266)])
print(df_2.loc[(df_2["posto"] == 66)])
exit(1)

# Marca o tempo de início
inicio = time.time()
os.environ["LOKY_MAX_CPU_COUNT"] = "4" 
df_n =      pd.read_parquet("previsao_diaria/previsao_total_n.parquet", engine = "pyarrow")
df_ne =     pd.read_parquet("previsao_diaria/previsao_total_ne.parquet", engine = "pyarrow")
df_ose =    pd.read_parquet("previsao_diaria/previsao_total_ose.parquet", engine = "pyarrow")
df_parana = pd.read_parquet("previsao_diaria/previsao_total_parana.parquet", engine = "pyarrow")
df_sul =    pd.read_parquet("previsao_diaria/previsao_total_s.parquet", engine = "pyarrow")
print(df_n)
print(df_ne)
print(df_ose)
print(df_parana)
print(df_sul)

df_resultante = pd.concat([df_n, df_ne, df_ose, df_parana, df_sul]).reset_index(drop = True)
df_resultante = df_resultante.drop(columns=["data_rodada", "previsao_total", "previsao_total_sem_tv", "previsao_inc_tv", "nome"])
df_resultante['data_previsao'] = pd.to_datetime(df_resultante['data_previsao'])
data_inic = pd.to_datetime("2020-01-01")
print("data_ini: ", data_inic)
semanas = 5
lista_df_semanas = []
for i in range(0,semanas):
    
    print("data_inic: ", data_inic)
    df_data = df_resultante.loc[(df_resultante["data_previsao"] == data_inic)]
    data_inic = data_inic + timedelta(days=7)
    print(df_data)
    lista_df_semanas.append(df_data)

resultado = pd.concat(lista_df_semanas).reset_index(drop = True)
resultado.to_csv("cenarios_GhcenSemanais_"+str(semanas)+".csv", index = False)
resultado.to_parquet("cenarios_GhcenSemanais_"+str(semanas)+".parquet", index = False)

print(resultado)