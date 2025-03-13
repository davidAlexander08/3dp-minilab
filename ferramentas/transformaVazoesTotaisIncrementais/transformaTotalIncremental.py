import pandas as pd
from inewave.newave import Confhd
from inewave.newave import Hidr
from inewave.newave import Vazoes
import json

##ROTINA PARA TRANSFORMAR VAZOES TOTAIS EM INCREMENTAIS, V0 PARTINDO DO ARQUIVO VAZOES.DAT DO NEWAVE
df_vaz = Vazoes.read("..\\transformaNewaveLab\\deck_newave_2020_01\\VAZOES.dat").vazoes
df_confhd = Confhd.read("..\\transformaNewaveLab\\deck_newave_2020_01\\CONFHD.dat").usinas
print(df_confhd)
print(df_vaz)

def buscaUsinasMontante(codigo_usi, df_confhd):
    lista_montantes = []
    lista_usinas = df_confhd["codigo_usina"].unique()
    print("codigo_usi: ", codigo_usi)
    for usi in lista_usinas:
        df_montante = df_confhd.loc[(df_confhd["codigo_usina"] == usi)].reset_index(drop = True)
        usina_jusante = df_montante["codigo_usina_jusante"].iloc[0]
        if(usina_jusante == codigo_usi):
            posto_montante = df_montante["posto"].iloc[0]
            lista_montantes.append(posto_montante)
    return lista_montantes


lista_postos = df_confhd["posto"].unique()
for posto in lista_postos:
    df_conf_uhe = df_confhd.loc[(df_confhd["posto"] == posto)].reset_index(drop = True)
    codigo_usi = df_conf_uhe["codigo_usina"].iloc[0]
    lista_montantes = buscaUsinasMontante(codigo_usi, df_confhd)
    for montante in lista_montantes:
        df_vaz[posto] = df_vaz[posto] - df_vaz[montante]
print(df_vaz)
df_vaz.to_csv("vazoes_incrementais.csv")