import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px
from dadosTabela import DadosMensais
from dadosSemanais import DadosSemanais
import numpy as np
from scipy.linalg import solve
from scipy.linalg import svd

from ParPGevazp import *
from ParPAGevazp import *
from matrizCarga import *
from ruidos import *
#df_parp = DadosSemanais().dados

ordemMaxima = 6
arq = "/home/david/git/3dp-minilab/CenariosSemanais/vazoesMensaisCamargos.csv"
df_camargos = DadosMensais(arq).dados
#coef_residuos_camargos = exec_PARP(df_camargos, ordemMaxima)

arq = "/home/david/git/3dp-minilab/CenariosSemanais/vazoesMensaisFurnas.csv"
df_furnas = DadosMensais(arq).dados
#coef_residuos_furnas = exec_PARP(df_furnas, ordemMaxima)
#coef_residuos_furnas = exec_PARPA(df_furnas, ordemMaxima)
lista_postos = []
lista_postos.append(df_camargos)
lista_postos.append(df_furnas)
mapaMatrizCorrelacoesPer = retornaMatrizCarga(lista_postos)
print(mapaMatrizCorrelacoesPer)

#SORTEIO DOS RUIDOS
periodoInicial = 11
numeroDeAberturasPeriodo = 3
matrizRuidos = geraMatrizRuidosPostos(lista_postos)
tupla = agregaRuidosKmeansMatriz(numeroDeAberturasPeriodo, matrizRuidos, lista_postos)
##Clusteriza ruidos pelo método do GEVAZP
matrizRuidosAgregados = tupla[0]
probabilidades = tupla[1]
matrizCargaPer = mapaMatrizCorrelacoesPer[periodoInicial]
ruidosCorrelacinados = np.dot(matrizCargaPer, matrizRuidosAgregados.T).T
print("ruidosCorrelacinados: ", ruidosCorrelacinados)

arq = "/home/david/git/3dp-minilab/CenariosSemanais/arvore_julia.csv"
df = pd.read_csv(arq)
print(df)

arq = "/home/david/git/3dp-minilab/CenariosSemanais/tendencia.csv"
df_tendencia = pd.read_csv(arq)
print(df_tendencia)
contador = 1
lista_df_arvore_vazoes = []

arq = "/home/david/git/3dp-minilab/CenariosSemanais/mapaPeriodoEstudo.csv"
df_mapaPeriodoEstudo = pd.read_csv(arq)
for df_posto in lista_postos:
    df_tendencia_posto = df_tendencia.loc[(df_tendencia["POSTO"] == contador)]
    print("df_tendencia_posto: ", df_tendencia_posto)
    df_posto = df.copy()
    df_posto.loc[df_posto["NO"] ==1,"VAZAO"] = df_tendencia_posto.loc[df_tendencia_posto["NO"] == 1,"VAZAO"].iloc[0]
    for per in df_posto["PER"].unique():
        if(per != 1):
            lista_nos  = df_posto.loc[df_posto["PER"] == per]["NO"].unique()
            aberturas = len(lista_nos)
            periodoHistorico = df_mapaPeriodoEstudo.loc[(df_mapaPeriodoEstudo["PERIODO"] == per)]["HISTORICO"].iloc[0]
            print("lista_nos: ", lista_nos , " aberturas: ", aberturas, " periodoHistorico: ", periodoHistorico)
            
            exit(1)
        #if(codigo_no in df_tendencia_posto["NO"].unique()):
        #    df_posto.loc[df_posto["NO"] ==codigo_no,"VAZAO"] = df_tendencia_posto.loc[df_tendencia_posto["NO"] == codigo_no,"VAZAO"].iloc[0]
        #else:
        #    print(df_posto.loc[df_posto["NO"] == codigo_no])
        #    per_otimizacao = df_posto.loc[df_posto["NO"] == codigo_no].reset_index(drop = True)["PER"].iloc[0]
        #    periodoHistorico = df_mapaPeriodoEstudo.loc[(df_mapaPeriodoEstudo["PERIODO"] == per_otimizacao)]["HISTORICO"].iloc[0]
            
            
            
            print("per_otimizacao: ", per_otimizacao , " periodoHistorico: " , periodoHistorico)
            #df_posto.loc[df_posto["NO"] ==codigo_no,"VAZAO"] = 

    
    print(df_posto)
    #["VAZAO"].iloc[0]
    

    contador += 1
















#print(df_anual.head(25))
#print(df_parp.head(25))