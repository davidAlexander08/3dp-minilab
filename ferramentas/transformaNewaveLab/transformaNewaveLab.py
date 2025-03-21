import pandas as pd
from inewave.newave import Confhd
from inewave.newave import Hidr
from inewave.newave import Ree
from inewave.newave import Term
from inewave.newave import Conft
from inewave.newave import Clast
from inewave.newave import Sistema
import json
import re
import numpy as np


class usinaHidreletrica():

    def __init__(self):
        self.nome =     None
        self.jusante =  None
        self.POSTO =    None
        self.GHMIN =    None
        self.GHMAX =    None
        self.TURBMAX =  None
        self.VOLMIN =   None
        self.VOLMAX =   None
        self.PRODT =    None
        self.VOLINI =   None
        self.BARRA =    None
        self.SUBMERCADO = None
        self.CODIGO =   None
        

    def to_dict(self):
        return {
            "NOME": self.nome,
            "POSTO":self.POSTO if self.POSTO is not None else 999,
            "JUSANTE": self.jusante if self.jusante is not None else "",
            "GHMIN": self.GHMIN if self.GHMIN is not None else 0.0,
            "GHMAX": self.GHMAX if self.GHMAX is not None else 0.0,
            "TURBMAX": self.TURBMAX if self.TURBMAX is not None else 0.0,
            "VOLUME_MINIMO": self.VOLMIN if self.VOLMIN is not None else 0.0,
            "VOLUME_MAXIMO": self.VOLMAX if self.VOLMAX is not None else 0.0,
            "PRODT": self.PRODT if self.PRODT is not None else 0,
            "VOLUME_INICIAL": self.VOLINI if self.VOLINI is not None else 0,
            "BARRA": self.BARRA if self.BARRA is not None else 0,
            "SUBMERCADO": self.SUBMERCADO if self.SUBMERCADO is not None else 0,
            "CODIGO": self.CODIGO if self.CODIGO is not None else 0
        }


class usinaTermica():

    def __init__(self):
        self.NOME =     None
        self.GTMIN =  None
        self.GTMAX =    None
        self.CUSTO_GERACAO =    None
        self.BARRA =    None
        self.SUBMERCADO = None
        self.CODIGO =   None
        

    def to_dict(self):
        return {
            "NOME": self.NOME,
            "GTMIN": self.GTMIN if self.GTMIN is not None else 0.0,
            "GTMAX": self.GTMAX if self.GTMAX is not None else 0.0,
            "CUSTO_GERACAO": self.CUSTO_GERACAO if self.CUSTO_GERACAO is not None else 0.0,
            "BARRA": self.BARRA if self.BARRA is not None else 0,
            "SUBMERCADO": self.SUBMERCADO if self.SUBMERCADO is not None else 0,
            "CODIGO": self.CODIGO if self.CODIGO is not None else 0
        }

class classeSubmercado():

    def __init__(self):
        self.NOME =     None
        self.CODIGO =   None
        self.CUSTO_DEFICIT =    None
        self.DEMANDA =    None        

    def to_dict(self):
        return {
            "NOME": self.NOME,
            "CODIGO": self.CODIGO if self.CODIGO is not None else 0,
            "CUSTO_DEFICIT": self.CUSTO_DEFICIT if self.CUSTO_DEFICIT is not None else 0.0,
            "DEMANDA": self.DEMANDA if self.DEMANDA is not None else [],
        }


class classeRestricaoVazmin():

    def __init__(self):
        self.USIH =     None
        self.VAZMIN =    None
    def to_dict(self):
        return {
            "NOME": self.NOME,
            "VAZMIN": self.VAZMIN if self.VAZMIN is not None else 0.0,
        }


class classeRestricaoVolMin():

    def __init__(self):
        self.USIH =     None
        self.VOLMIN =    None
    def to_dict(self):
        return {
            "NOME": self.NOME,
            "VOLMIN": self.VOLMIN if self.VOLMIN is not None else 0.0,
        }

class classeRestricaoVolMax():

    def __init__(self):
        self.USIH =     None
        self.VOLMAX =    None
    def to_dict(self):
        return {
            "NOME": self.NOME,
            "VOLMAX": self.VOLMAX if self.VOLMAX is not None else 0.0,
        }

def save_to_json(data, filename="usinas.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def calcula_prodt_65(codigo_usi, df_hidr):
    df_hidr_uhe = df_hidr.loc[(df_hidr["codigo_usina"] == codigo_usi)]
    vol_cota_A0 = df_hidr_uhe["a0_volume_cota"].iloc[0]
    vol_cota_A1 = df_hidr_uhe["a1_volume_cota"].iloc[0]
    vol_cota_A2 = df_hidr_uhe["a2_volume_cota"].iloc[0]
    vol_cota_A3 = df_hidr_uhe["a3_volume_cota"].iloc[0]
    vol_cota_A4 = df_hidr_uhe["a4_volume_cota"].iloc[0]
    cota_med_fuga = df_hidr_uhe["canal_fuga_medio"].iloc[0]
    perdas = df_hidr_uhe["perdas"].iloc[0]
    prodt_esp = df_hidr_uhe["produtibilidade_especifica"].iloc[0]
    vol_min = df_hidr_uhe["volume_minimo"].iloc[0]
    vol_max = df_hidr_uhe["volume_maximo"].iloc[0]


    if(vol_min != vol_max):
        h_min_integral = vol_cota_A0*vol_min + vol_cota_A1*(vol_min**2)/2 + vol_cota_A2*(vol_min**3)/3 + vol_cota_A3*(vol_min**4)/4 + vol_cota_A4*(vol_min**5)/5
        h_max_integral = vol_cota_A0*vol_max + vol_cota_A1*(vol_max**2)/2 + vol_cota_A2*(vol_max**3)/3 + vol_cota_A3*(vol_max**4)/4 + vol_cota_A4*(vol_max**5)/5
        h_eq = (h_max_integral-h_min_integral)/(vol_max-vol_min)
        fprodt = (h_eq - cota_med_fuga - perdas)*prodt_esp 
    else:
        vol_65 = (df_hidr_uhe["volume_maximo"].iloc[0] - df_hidr_uhe["volume_minimo"].iloc[0])*0.65 + df_hidr_uhe["volume_minimo"].iloc[0]
        h_65 =  vol_cota_A0 + vol_cota_A1*vol_65 + vol_cota_A2*(vol_65**2)+ vol_cota_A3*(vol_65**3) + vol_cota_A4*(vol_65**4)
        fprodt =  (h_65 - cota_med_fuga - perdas)*prodt_esp 
    print("codigo_usi: ", codigo_usi, " prodt: ", fprodt)
    return fprodt

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


def calculaPotenciaMaxima(codigo_usi, df_hidr):
    df_hidr_uhe = df_hidr.loc[(df_hidr["codigo_usina"] == codigo_usi)]
    pot_nom_1 = df_hidr_uhe["potencia_nominal_conjunto_1"].iloc[0]
    pot_nom_2 = df_hidr_uhe["potencia_nominal_conjunto_2"].iloc[0]
    pot_nom_3 = df_hidr_uhe["potencia_nominal_conjunto_3"].iloc[0]
    pot_nom_4 = df_hidr_uhe["potencia_nominal_conjunto_4"].iloc[0]
    pot_nom_5 = df_hidr_uhe["potencia_nominal_conjunto_5"].iloc[0]
    conj_maq_1 = df_hidr_uhe["maquinas_conjunto_1"].iloc[0]
    conj_maq_2 = df_hidr_uhe["maquinas_conjunto_2"].iloc[0]
    conj_maq_3 = df_hidr_uhe["maquinas_conjunto_3"].iloc[0]
    conj_maq_4 = df_hidr_uhe["maquinas_conjunto_4"].iloc[0]
    conj_maq_5 = df_hidr_uhe["maquinas_conjunto_5"].iloc[0]
    pot_max = pot_nom_1*conj_maq_1 + pot_nom_2*conj_maq_2 + pot_nom_3*conj_maq_3 + pot_nom_4*conj_maq_4 + pot_nom_5*conj_maq_5
    return int(pot_max)

caso = "deck_newave_2020_01_reduzido"
caso = "deck_newave_2020_01_mini"
caso = "deck_newave_2020_01_mini_mini"
caso = "deck_newave_2020_01_mini_mini_min"
caso = "deck_newave_2020_01_mini_mini_min_mini"
caso = "deck_newave_2020_01_reduzido_180325"
df_confhd = Confhd.read(caso+"\\CONFHD.dat").usinas
df_hidr = Hidr.read(caso+"\\HIDR.dat").cadastro
df_term = Term.read(caso+"\\TERM.dat").usinas
df_conft = Conft.read(caso+"\\CONFT.dat").usinas
df_clast = Clast.read(caso+"\\CLAST.dat").usinas
df_sistema = Sistema.read(caso+"\\SISTEMA.dat").mercado_energia
df_hidr = df_hidr.reset_index()
df_ree = Ree.read(caso+"\\REE.dat").rees
df_postos_considerados = pd.read_csv("vazao_feixes.csv")
postos_considerados = df_postos_considerados["NOME_UHE"].unique()
lista_submercados = set()


lista_indices_ano_estudo = df_clast["indice_ano_estudo"].unique()
df_clast = df_clast.loc[(df_clast["indice_ano_estudo"] == lista_indices_ano_estudo[0])].reset_index(drop = True)

lista_utes = []
meses = df_term["mes"].unique()
df_term = df_term.loc[(df_term["mes"] == meses[0])].reset_index(drop = True)
for idx, row in df_term.iterrows():
    submercado_usina = df_conft.loc[(df_conft["codigo_usina"] == row.codigo_usina)]["submercado"].iloc[0]
    custo_usina = df_clast.loc[(df_clast["codigo_usina"] == row.codigo_usina)]["valor"].iloc[0]
    usinaT = usinaTermica()
    usinaT.NOME =   row.nome_usina
    usinaT.GTMIN =  row.geracao_minima
    usinaT.GTMAX =    row.potencia_instalada
    usinaT.CUSTO_GERACAO =    custo_usina
    usinaT.BARRA =    1
    usinaT.SUBMERCADO = int(submercado_usina)
    usinaT.CODIGO =   row.codigo_usina
    lista_utes.append(usinaT)
#exit(1)
lista_uhes = []
lista_codigo_usinas = []
mapaCodigoUsinaNome = {}
for idx, row in df_confhd.iterrows():
    hidr_usi = df_hidr.loc[(df_hidr["codigo_usina"] == row.codigo_usina)].reset_index(drop = True)
    usi_jusante = df_confhd.loc[(df_confhd["codigo_usina"] == row.codigo_usina_jusante)].reset_index(drop = True)
    ree_usina = row.ree
    submercado = df_ree.loc[(df_ree["codigo"] == ree_usina)]["submercado"].iloc[0]
    lista_submercados.add(submercado)
    usina = usinaHidreletrica()
    turb_max = calculaEngolimentoMaximo(row.codigo_usina, df_hidr)
    pot_max = calculaPotenciaMaxima(row.codigo_usina, df_hidr)
    prodt = calcula_prodt_65(row.codigo_usina, df_hidr)
    lista_codigo_usinas.append(row.codigo_usina)
    #usina.nome =     row.nome_usina
    #usina.nome =     str(row.codigo_usina)
    usina.nome =     str(row.codigo_usina)
    mapaCodigoUsinaNome[row.codigo_usina] = usina.nome
    #usina.jusante =  str(row.codigo_usina_jusante) if row.codigo_usina_jusante != 0 else ""
    #print(usina.nome)
    usina_jusante =  str(usi_jusante["codigo_usina"].iloc[0]) if row.codigo_usina_jusante != 0 else ""
    usina.jusante =  usina_jusante
    usina.POSTO =    row.posto
    usina.GHMIN =    0
    usina.GHMAX =    round(pot_max,2)
    usina.TURBMAX =  round(turb_max,2)
    usina.VOLMIN =   int(hidr_usi["volume_minimo"].iloc[0]) - int(hidr_usi["volume_minimo"].iloc[0])
    usina.VOLMAX =   int(hidr_usi["volume_maximo"].iloc[0]) - int(hidr_usi["volume_minimo"].iloc[0])
    usina.PRODT =    round(prodt,2)
    usina.VOLINI =   int((hidr_usi["volume_maximo"].iloc[0]-hidr_usi["volume_minimo"].iloc[0]) * (row.volume_inicial_percentual/100) + hidr_usi["volume_minimo"].iloc[0]) - int(hidr_usi["volume_minimo"].iloc[0])
    usina.BARRA =    1
    #usina.CODIGO =   row.codigo_usina
    usina.SUBMERCADO =   int(submercado)
    usina.CODIGO =   row.codigo_usina
    lista_uhes.append(usina)
    print(row.posto)
print(lista_submercados)
mapa_codigo_nomeSBM = {
    1:"SUDESTE", 2:"SUL", 3:"NORDESTE", 4:"NORTE"
} 
datas = df_sistema["data"].unique()[0:4]
df_sistema = df_sistema.loc[(df_sistema["data"].isin(datas))].reset_index(drop = True)
#print(datas)
#print(df_sistema)

listaObjetoSubmercados = []
for elemento in lista_submercados:
    lista_demanda = df_sistema.loc[(df_sistema["codigo_submercado"] == int(elemento))]["valor"].tolist()
    sbm = classeSubmercado()
    #print(elemento)
    #print(int(elemento))
    sbm.NOME = mapa_codigo_nomeSBM[int(elemento)]
    sbm.CODIGO = int(elemento)
    sbm.CUSTO_DEFICIT = 5000
    sbm.DEMANDA = lista_demanda
    listaObjetoSubmercados.append(sbm)



lista_usinas = []
for usi in lista_uhes:
    if(usi.POSTO in postos_considerados):
        lista_usinas.append(usi)
        #print("nome: ", usi.nome, " posto: ", usi.posto)
            
## PEGA VAZMIN e PRIMEIRO VAZMINT
with open(caso+"\\MODIF.DAT", "r", encoding="utf-8") as file:
    lines = file.readlines()
# Process lines to extract USINA and VAZMIN
print(lista_codigo_usinas)
flag_vazmin = 0
flag_vmaxT = 0
flag_vazminT = 0
flag_vminT = 0
lista_df_vazmin  = []
lista_df_vmax = []
lista_df_vmin = []
for i, line in enumerate(lines):
    line = line.strip()
    
    if(line.startswith("USINA")):
        codigo_usi = int(line.split()[1])  # Extract the second element
        if(codigo_usi in lista_codigo_usinas):
            flag_vazmin = 1
            flag_vazminT = 1
            flag_vminT = 1
            flag_vmaxT = 1
            print("CODIGO: ", codigo_usi)
    if line.startswith("VAZMIN ") and flag_vazmin == 1 and codigo_usi in lista_codigo_usinas:
        vazmin_value = float(line.split()[1])  # Extract the second element
        print("codigo_usi: ", codigo_usi, " vazmin: ", vazmin_value)
        flag_vazmin = 0
        lista_df_vazmin.append(pd.DataFrame({
            "USI":[mapaCodigoUsinaNome[codigo_usi]],
            "vazmin":[vazmin_value],
        }))
    if line.startswith("VAZMINT ") and flag_vazminT == 1 and codigo_usi in lista_codigo_usinas:
        vazmin_value = float(line.split()[3])  # Extract the second element
        print("codigo_usi: ", codigo_usi, " vazmin: ", vazmin_value)
        flag_vazminT = 0
        lista_df_vazmin.append(pd.DataFrame({
            "USI":[mapaCodigoUsinaNome[codigo_usi]],
            "vazmin":[vazmin_value],
        }))
    if line.startswith("VMINT ") and flag_vminT == 1 and codigo_usi in lista_codigo_usinas:
        vmin_value = float(line.split()[3])  # Extract the second element
        print("codigo_usi: ", codigo_usi, " vmin: ", vmin_value)
        flag_vminT = 0
        lista_df_vmin.append(pd.DataFrame({
            "USI":[mapaCodigoUsinaNome[codigo_usi]],
            "vmin":[vmin_value],
        }))
    if line.startswith("VMAXT ") and flag_vmaxT == 1 and codigo_usi in lista_codigo_usinas:
        vmax_value = float(line.split()[3])  # Extract the second element
        print("codigo_usi: ", codigo_usi, " vmax: ", vmax_value)
        flag_vmaxT = 0
        lista_df_vmax.append(pd.DataFrame({
            "USI":[mapaCodigoUsinaNome[codigo_usi]],
            "vmax":[vmax_value],
        }))

df_vazmin = pd.concat(lista_df_vazmin).reset_index(drop = True)
for idx, row in df_vazmin.iterrows():
    restr_vazmin = classeRestricaoVazmin()
    restr_vazmin.USIH   =    row.USI
    restr_vazmin.VAZMIN =    row.vazmin
df_vazmin.to_csv("restr_vazao_minima.csv", index = False)

df_vmin = pd.concat(lista_df_vmin).reset_index(drop = True)
for idx, row in df_vmin.iterrows():
    restr_vmin = classeRestricaoVolMin()
    restr_vmin.USIH   =    row.USI
    restr_vmin.VOLMIN =    row.vmin
df_vmin.to_csv("restr_vol_min.csv", index = False)

df_vmax = pd.concat(lista_df_vmax).reset_index(drop = True)
for idx, row in df_vmax.iterrows():
    restr_vmax = classeRestricaoVolMax()
    restr_vmax.USIH   =    row.USI
    restr_vmax.VOLMAX =    row.vmax
df_vmax.to_csv("restr_vol_max.csv", index = False)


data = {"UHEs": [usina.to_dict() for usina in lista_usinas],
        "UTEs": [usiT.to_dict() for usiT in lista_utes],
        "SUBMERCADOs": [sbm.to_dict() for sbm in listaObjetoSubmercados]}
save_to_json(data)


exit(1)