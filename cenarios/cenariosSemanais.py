import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px
from dadosTabela import DadosMensais
from dadosSemanais import DadosSemanais
import numpy as np
from scipy.linalg import solve
from ParPGevazp import *
from ParPAGevazp import *
df_parp = DadosSemanais().dados
#df_parp = DadosMensais().dados

print(df_parp)
ordemMaxima = 6

## Metodo PAR-P GEVAZP
df_FAC = calculaFAC(df_parp, ordemMaxima)
df_FACP = calculaFACP(df_parp, df_FAC, ordemMaxima)
mapaPeriodoOrdem = encontraOrdensPeriodos(df_parp, df_FACP, ordemMaxima)
df_Coefs = calculaCoeficientes(df_parp, df_FAC, mapaPeriodoOrdem)
df_residuos = calculaResiduosModelos(df_parp, df_Coefs)


##  Método PARP-A GEVAZP
#df_FAC = calculaFAC(df_parp, ordemMaxima)
#df_anual = calculaHistoricoMediasAnuais(df_parp)
#df_FAC_Anual = calculaFACAnual(df_parp, df_anual, ordemMaxima)
#df_FACP = calculaFACPPARPA(df_parp, df_anual, df_FAC, df_FAC_Anual, ordemMaxima)
#mapaPeriodoOrdem = encontraOrdensPeriodos(df_parp, df_FACP, ordemMaxima-1)
#df_Coefs = calculaCoeficientes(df_parp, df_FAC, mapaPeriodoOrdem)
#df_residuos = calculaResiduosModelos(df_parp, df_Coefs)


#print(df_anual.head(25))
#print(df_parp.head(25))