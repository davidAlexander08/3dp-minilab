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

