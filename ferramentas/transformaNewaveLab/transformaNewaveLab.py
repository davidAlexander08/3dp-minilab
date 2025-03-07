import pandas as pd
from inewave.newave import Confhd
from inewave.newave import Hidr
import json

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

df_confhd = Confhd.read("deck_newave_2020_01\\CONFHD.dat").usinas
df_hidr = Hidr.read("deck_newave_2020_01\\HIDR.dat").cadastro
df_hidr = df_hidr.reset_index()
df_postos_considerados = pd.read_csv("vazao_feixes.csv")
postos_considerados = df_postos_considerados["NOME_UHE"].unique()

#df_hidr.to_csv("hidr.csv")
lista_uhes = []
for idx, row in df_confhd.iterrows():

    hidr_usi = df_hidr.loc[(df_hidr["codigo_usina"] == row.codigo_usina)].reset_index(drop = True)
    usi_jusante = df_confhd.loc[(df_confhd["codigo_usina"] == row.codigo_usina_jusante)].reset_index(drop = True)
    usina = usinaHidreletrica()
    #usina.nome =     row.nome_usina
    #usina.nome =     str(row.codigo_usina)
    usina.nome =     str(row.posto)
    #usina.jusante =  str(row.codigo_usina_jusante) if row.codigo_usina_jusante != 0 else ""
    usina.jusante =  str(usi_jusante["posto"].iloc[0]) if row.codigo_usina_jusante != 0 else ""
    usina.posto =    row.posto
    usina.GHMIN =    0
    usina.GHMAX =    100000
    usina.TURBMAX =  100000
    usina.VOLMIN =   hidr_usi["volume_minimo"].iloc[0]
    usina.VOLMAX =   hidr_usi["volume_maximo"].iloc[0]
    usina.PRODT =    1
    usina.VOLINI =   (hidr_usi["volume_maximo"].iloc[0]-hidr_usi["volume_minimo"].iloc[0]) * (row.volume_inicial_percentual/100) + hidr_usi["volume_minimo"].iloc[0]
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