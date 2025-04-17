# Codigo transforma ECO
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import MiniBatchKMeans
import math
import os
from datetime import timedelta  # <-- Add this import at the top of your script
import random
import time
caminho = r"C:\Users\testa\Documents\git\3dp-minilab\Dissertacao\apresentacaoCarmen_Gevazp\caso_mini\exercicioGevazp\4Estagios\3Aberturas\Pente_GVZP"
caminho = r"C:\Users\testa\Documents\git\3dp-minilab\Carmen\exercicio_27cen\3Aberturas_Equiprovavel\Pente_GVZP"
arvore = pd.read_csv(caminho+"\\arvore.csv")
cenarios = pd.read_csv(caminho+"\\cenarios.csv")




caminho_modelo = r"C:\Users\testa\Documents\git\3dp-minilab\Dissertacao\apresentacaoCarmen_Gevazp\caso_mini\exercicioGevazp\4Estagios\3Aberturas\PenteBase_16cen"
caminho_modelo = r"C:\Users\testa\Documents\git\3dp-minilab\Carmen\exercicio_27cen\3Aberturas_Equiprovavel\Pente_24cen\Pente_modelo_24cen"
arvore_modelo = pd.read_csv(caminho_modelo+"\\arvore.csv")
cenarios_modelo = pd.read_csv(caminho_modelo+"\\cenarios.csv")

print(arvore_modelo)
cenarios_modelo["VAZAO"] = cenarios_modelo["VAZAO"]*0
periodos = arvore_modelo["PER"].unique()
usinas = cenarios_modelo["NOME_UHE"].unique()

for uhe in usinas:
    vazao_no1 = cenarios.loc[(cenarios["NOME_UHE"] == uhe) & (cenarios["NO"] == 1)]["VAZAO"].iloc[0]
    cenarios_modelo.loc[(cenarios_modelo["NOME_UHE"] == uhe) & (cenarios_modelo["NO"] == 1), "VAZAO"] = vazao_no1

periodos = periodos[periodos != 1]
for per in sorted(periodos):
    lista_nodes_modelo = arvore_modelo.loc[(arvore_modelo["PER"] == per)]["NO"].unique()
    lista_nodes_originais = arvore.loc[(arvore["PER"] == per)]["NO"].unique()
    for node in lista_nodes_modelo:
        escolhido = random.choice(lista_nodes_originais)
        df_vazoes_escolhido = cenarios.loc[(cenarios["NO"] == escolhido)].reset_index(drop = True)
        for uhe in usinas:
            vazao_uhe = df_vazoes_escolhido.loc[(df_vazoes_escolhido["NOME_UHE"] == uhe)]["VAZAO"].iloc[0]
            cenarios_modelo.loc[(cenarios_modelo["NOME_UHE"] == uhe) & (cenarios_modelo["NO"] == node), "VAZAO"] = vazao_uhe
    #for uhe in usinas:
print(arvore_modelo)
print(cenarios_modelo)

arvore_modelo.to_csv("arvore.csv", index = False)
cenarios_modelo.to_csv("cenarios.csv", index = False)

exit(1)

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