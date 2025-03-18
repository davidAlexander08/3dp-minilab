import pandas as pd
from inewave.newave import Confhd
from inewave.newave import Hidr
import json
import numpy as np

class usinaHidreletrica():

    def __init__(self):
        self.nome =     None
        self.jusante =  None
        self.posto =    None
        self.GHMIN =    None
        self.GHMAX =    None
        self.TURBMAX =  None
        self.VOLMIN =   None
        self.VOLMAX =   None
        self.PRODT =    None
        self.VOLINI =   None
        self.BARRA =    None
        self.CODIGO =   None

    def to_dict(self):
        return {
            "NOME": self.nome,
            "JUSANTE": self.jusante if self.jusante is not None else "",
            "GHMIN": self.GHMIN if self.GHMIN is not None else 0.0,
            "GHMAX": self.GHMAX if self.GHMAX is not None else 0.0,
            "TURBMAX": self.TURBMAX if self.TURBMAX is not None else 0.0,
            "VOLUME_MINIMO": self.VOLMIN if self.VOLMIN is not None else 0.0,
            "VOLUME_MAXIMO": self.VOLMAX if self.VOLMAX is not None else 0.0,
            "PRODT": self.PRODT if self.PRODT is not None else 0,
            "VOLUME_INICIAL": self.VOLINI if self.VOLINI is not None else 0,
            "BARRA": self.BARRA if self.BARRA is not None else 0,
            "CODIGO": self.CODIGO if self.CODIGO is not None else 0
        }

def save_to_json(usinas, filename="usinas.json"):
    data = {"UHEs": [usina.to_dict() for usina in usinas]}
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


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

def calculaEngolimentoMaximo(codigo_usi, df_hidr):
    df_hidr_uhe = df_hidr.loc[(df_hidr["codigo_usina"] == codigo_usi)]
    vaz_nom_1 = df_hidr_uhe["vazao_nominal_conjunto_1"].iloc[0]
    vaz_nom_2 = df_hidr_uhe["vazao_nominal_conjunto_2"].iloc[0]
    vaz_nom_3 = df_hidr_uhe["vazao_nominal_conjunto_3"].iloc[0]
    vaz_nom_4 = df_hidr_uhe["vazao_nominal_conjunto_4"].iloc[0]
    vaz_nom_5 = df_hidr_uhe["vazao_nominal_conjunto_5"].iloc[0]
    conj_maq_1 = df_hidr_uhe["maquinas_conjunto_1"].iloc[0]
    conj_maq_2 = df_hidr_uhe["maquinas_conjunto_2"].iloc[0]
    conj_maq_3 = df_hidr_uhe["maquinas_conjunto_3"].iloc[0]
    conj_maq_4 = df_hidr_uhe["maquinas_conjunto_4"].iloc[0]
    conj_maq_5 = df_hidr_uhe["maquinas_conjunto_5"].iloc[0]
    turb_max = vaz_nom_1*conj_maq_1 + vaz_nom_2*conj_maq_2 + vaz_nom_3*conj_maq_3 + vaz_nom_4*conj_maq_4 + vaz_nom_5*conj_maq_5
    return int(turb_max)

caso = "deck_newave_2020_01_reduzido"
caso = "deck_newave_2020_01_mini"
caso = "deck_newave_2020_01_mini_mini"
caso = "deck_newave_2020_01_mini_mini_min"
caso = "deck_newave_2020_01_mini_mini_min_mini"
caso = "deck_newave_2020_01_reduzido_180325"
df_confhd = Confhd.read(caso+"\\CONFHD.dat").usinas
df_hidr = Hidr.read(caso+"\\HIDR.dat").cadastro
df_hidr = df_hidr.reset_index()
df_postos_considerados = pd.read_csv("vazao_feixes.csv")
postos_considerados = df_postos_considerados["NOME_UHE"].unique()

#df_hidr.to_csv("hidr.csv")
lista_uhes = []
for idx, row in df_confhd.iterrows():
    hidr_usi = df_hidr.loc[(df_hidr["codigo_usina"] == row.codigo_usina)].reset_index(drop = True)
    usi_jusante = df_confhd.loc[(df_confhd["codigo_usina"] == row.codigo_usina_jusante)].reset_index(drop = True)
    usina = usinaHidreletrica()
    turb_max = calculaEngolimentoMaximo(row.codigo_usina, df_hidr)
    prodt = calcula_prodt_65(row.codigo_usina, df_hidr)
    #usina.nome =     row.nome_usina
    #usina.nome =     str(row.codigo_usina)
    usina.nome =     str(row.posto)
    #usina.jusante =  str(row.codigo_usina_jusante) if row.codigo_usina_jusante != 0 else ""
    print(usina.nome)
    usina.jusante =  str(usi_jusante["posto"].iloc[0]) if row.codigo_usina_jusante != 0 else ""
    usina.posto =    row.posto
    usina.GHMIN =    0
    usina.GHMAX =    100000
    usina.TURBMAX =  round(turb_max,2)
    usina.VOLMIN =   int(hidr_usi["volume_minimo"].iloc[0]) - int(hidr_usi["volume_minimo"].iloc[0])
    usina.VOLMAX =   int(hidr_usi["volume_maximo"].iloc[0]) - int(hidr_usi["volume_minimo"].iloc[0])
    usina.PRODT =    round(prodt,2)
    usina.VOLINI =   int((hidr_usi["volume_maximo"].iloc[0]-hidr_usi["volume_minimo"].iloc[0]) * (row.volume_inicial_percentual/100) + hidr_usi["volume_minimo"].iloc[0]) - int(hidr_usi["volume_minimo"].iloc[0])
    usina.BARRA =    1
    #usina.CODIGO =   row.codigo_usina
    usina.CODIGO =   row.posto
    lista_uhes.append(usina)

lista_usinas = []
for usi in lista_uhes:
    if("FICT" not in usi.nome):
        if(usi.posto in postos_considerados):
            lista_usinas.append(usi)
            print("nome: ", usi.nome, " posto: ", usi.posto)
save_to_json(lista_usinas)
exit(1)