import pandas as pd
from inewave.newave import Confhd
from inewave.newave import Hidr
import json

### VAZOES_FEIXES_INCR_SIN
df_vazoes = pd.read_csv("vazao_feixes.csv")
print(df_vazoes)
lista_df = []
df_aux = df_vazoes.loc[df_vazoes["NOME_UHE"] == df_vazoes["NOME_UHE"].iloc[0]].copy()
df_aux["VAZAO"] = df_aux["VAZAO"]*0
for uhe in df_vazoes["NOME_UHE"].unique():
    df_uhe = df_vazoes.loc[(df_vazoes["NOME_UHE"] == uhe)].reset_index(drop = True)
    df_aux["VAZAO"] += df_uhe["VAZAO"]
print(df_aux)
df_aux.to_csv("vazoes_feixes_incr_sin.csv", index = False)

## TRANSFORMA EM ENA COM BASE EM UM DECK DE NEWAVE, UTILIZANDO O HIDR PARA VER A FUNCAO DE PRODUCAO A 65% E CONHECENDO A CASCATA
## POR MEIO DO ARQUIVO DE CASCATA DO NEWAVE
## VAZOES_FEIXES_ENA_SIN
### VAZOES_FEIXES_INCR_SIN

df_confhd = Confhd.read("..\\transformaNewaveLab\\deck_newave_2020_01\\CONFHD.dat").usinas
df_hidr = Hidr.read("..\\transformaNewaveLab\\deck_newave_2020_01\\HIDR.dat").cadastro
df_hidr = df_hidr.reset_index()
postos_considerados = df_vazoes["NOME_UHE"].unique()

print(df_hidr)
print(df_confhd)
print(postos_considerados)
exit(1)
df_vazoes = pd.read_csv("vazao_feixes.csv")
print(df_vazoes)
lista_df = []
df_aux = df_vazoes.loc[df_vazoes["NOME_UHE"] == df_vazoes["NOME_UHE"].iloc[0]].copy()
df_aux["VAZAO"] = df_aux["VAZAO"]*0
for uhe in df_vazoes["NOME_UHE"].unique():
    df_uhe = df_vazoes.loc[(df_vazoes["NOME_UHE"] == uhe)].reset_index(drop = True)
    df_aux["VAZAO"] += df_uhe["VAZAO"]
print(df_aux)
df_aux.to_csv("vazoes_feixes_incr_sin.csv", index = False)