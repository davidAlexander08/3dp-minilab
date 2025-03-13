import pandas as pd
from inewave.newave import Confhd
from inewave.newave import Hidr
import json

### VAZOES_FEIXES_INCR_SIN
caso = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\Mestrado\\caso_construcaoArvore_SIN_500cen\\"
df_vazoes = pd.read_csv(caso+"vazao_feixes.csv")
print(df_vazoes)
lista_df = []
df_aux = df_vazoes.loc[df_vazoes["NOME_UHE"] == df_vazoes["NOME_UHE"].iloc[0]].copy()
df_aux["VAZAO"] = df_aux["VAZAO"]*0
for uhe in df_vazoes["NOME_UHE"].unique():
    df_uhe = df_vazoes.loc[(df_vazoes["NOME_UHE"] == uhe)].reset_index(drop = True)
    df_aux["VAZAO"] += df_uhe["VAZAO"]
df_vaz_incr_SIN = df_aux
df_vaz_incr_SIN.to_csv("vazoes_feixes_incr_sin.csv", index = False)
print("df_vaz_incr_SIN: ", df_vaz_incr_SIN)
## TRANSFORMA EM ENA COM BASE EM UM DECK DE NEWAVE, UTILIZANDO O HIDR PARA VER A FUNCAO DE PRODUCAO A 65% E CONHECENDO A CASCATA
## POR MEIO DO ARQUIVO DE CASCATA DO NEWAVE
## VAZOES_FEIXES_ENA_SIN
### VAZOES_FEIXES_INCR_SIN

df_confhd = Confhd.read("..\\transformaNewaveLab\\deck_newave_2020_01\\CONFHD.dat").usinas
df_hidr = Hidr.read("..\\transformaNewaveLab\\deck_newave_2020_01\\HIDR.dat").cadastro
df_hidr = df_hidr.reset_index()
postos_considerados = df_vazoes["NOME_UHE"].unique()

#print(df_hidr)
#print(df_confhd)
#print(postos_considerados)

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

lista_df_ena = []
for uhe in df_vazoes["NOME_UHE"].unique():
    df_conf_uhe = df_confhd.loc[(df_confhd["posto"] == uhe)].reset_index(drop = True)
    
    if(not df_conf_uhe.empty):
        codigo_usi = df_conf_uhe["codigo_usina"].iloc[0]
        fprodt_acum_65 = calcula_prodt_acum_65(codigo_usi, df_confhd,  df_hidr)
        df_uhe = df_vazoes.loc[(df_vazoes["NOME_UHE"] == uhe)].reset_index(drop = True)
        df_ena = df_uhe.copy()
        df_ena["VAZAO"] = fprodt_acum_65*df_uhe["VAZAO"]
        df_ena["VAZAO"] = df_ena["VAZAO"].round(0)
        lista_df_ena.append(df_ena)
        print("uhe: ", uhe, " fprodt_acum_65: ", fprodt_acum_65)

df_ena_result = pd.concat(lista_df_ena)
df_ena_result.to_csv("ena_feixes_incr.csv")


### AGregar as ENAS no SIN

lista_df = []
df_aux = df_ena_result.loc[df_ena_result["NOME_UHE"] == df_ena_result["NOME_UHE"].iloc[0]].copy()
df_aux["VAZAO"] = df_aux["VAZAO"]*0
for uhe in df_ena_result["NOME_UHE"].unique():
    df_ena = df_ena_result.loc[(df_ena_result["NOME_UHE"] == uhe)].copy().reset_index(drop = True)
    df_aux["VAZAO"] += df_ena["VAZAO"]

df_ena_sin = df_aux
df_ena_sin.to_csv("ena_feixes_incr_sin.csv", index = False)

print("df_vazoes: ", df_vazoes)
print("df_ena_result: ", df_ena_result)
print("df_vaz_incr_SIN: ", df_vaz_incr_SIN)
print("df_ena_sin: ", df_ena_sin)