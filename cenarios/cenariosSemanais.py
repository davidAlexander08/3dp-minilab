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
numeroDeAberturasPeriodo = 5

matrizRuidos = geraMatrizRuidosPostos(lista_postos)
matrizRuidosAgregados = agregaRuidosKmeansMatriz(numeroDeAberturasPeriodo, matrizRuidos, lista_postos)
matrizCargaPer = mapaMatrizCorrelacoesPer[periodoInicial]
ruidosCorrelacinados = np.dot(matrizCargaPer, matrizRuidosAgregados.T).T
print("ruidosCorrelacinados: ", ruidosCorrelacinados)




















#print(df_anual.head(25))
#print(df_parp.head(25))