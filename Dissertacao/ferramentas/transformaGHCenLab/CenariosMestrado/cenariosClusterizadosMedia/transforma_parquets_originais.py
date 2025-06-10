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


#### PEGA MEDIA DOS VALORES DIARIOS
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
semanas = 4
lista_df_semanas = []
for i in range(0,semanas):
    print("data_inic: ", data_inic)
    data_inicial = data_inic
    data_inic = data_inic + timedelta(days=7)
    df_data = df_resultante.loc[(df_resultante["data_previsao"] < data_inic) & (df_resultante["data_previsao"] >= data_inicial) ].reset_index(drop = True)
    cenarios = df_data['cenario'].unique()
    postos = df_data["posto"].unique()
    lista_df = []
    for cen in cenarios:
        df_cenario = df_data.loc[(df_data["cenario"] == cen)].reset_index(drop = True)
        for posto in postos:
            df_posto = df_cenario.loc[(df_cenario["posto"] == posto)].reset_index(drop = True)
            #print(df_posto)
            media = df_posto["previsao_incremental"].mean()
            #print("media: ", media)
            lista_df.append(
                pd.DataFrame(
                    {
                        "cenario":[cen],
                        "posto":[posto],
                        "previsao_incremental":[media]
                    }
                )
            )

    df_semana = pd.concat(lista_df).reset_index(drop =True)
    #print(df_data)
    #print(df_data["data_previsao"].unique())

    lista_df_semanas.append(df_semana)

resultado = pd.concat(lista_df_semanas).reset_index(drop = True)
print(resultado)

resultado.to_csv("media_cenarios_GhcenSemanais_"+str(semanas)+".csv", index = False)
resultado.to_parquet("media_cenarios_GhcenSemanais_"+str(semanas)+".parquet", index = False)

print(resultado)



exit(1)

############################### PEGA PRIMEIRO VALOR DIARIO
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