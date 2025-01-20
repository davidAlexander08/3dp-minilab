import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px
from dadosTabela import DadosMensais
from dadosSemanais import DadosSemanais
import numpy as np
from scipy.linalg import solve

#df_parp = DadosSemanais().dados
df_parp = DadosMensais().dados

print(df_parp)
ordemMaxima = 6

df_FAC = pd.DataFrame(np.zeros((len(df_parp["periodo"].unique()), ordemMaxima+1)))
df_FAC["periodo"] = df_parp["periodo"].unique()
print(df_FAC)

lista_FAC_dataFrame = []
for per in df_parp["periodo"].unique():
    lista_FAC = []
    for ord in range(0,ordemMaxima+1):
        passado = 0
        if per > ord:
            passado = per - ord
            per_past = df_parp.loc[df_parp["periodo"] == passado].reset_index(drop = True)
            per_atual = df_parp.loc[df_parp["periodo"] == per].reset_index(drop = True)
            correlation = per_atual["vazao"].corr(per_past["vazao"])
            #correlation = cor(df_vazoes[:,mes_past][2:end], df_vazoes[:,mes][2:end])
        else:
            per_atual = df_parp.loc[df_parp["periodo"] == per].reset_index(drop = True)
            passado = per - ord + len(df_parp["periodo"].unique())
            per_past = df_parp.loc[df_parp["periodo"] == passado].reset_index(drop = True)
            df_atual = per_atual
            df_past = per_past
            per_atual = per_atual.iloc[1:].reset_index(drop = True) #Exclui a primeira linha
            per_past = per_past.iloc[:-1].reset_index(drop = True) #Exclui a ultima linha
            per_atual["vazao"] = (per_atual["vazao"] - df_atual["vazao"].mean())
            per_past["vazao"] = (per_past["vazao"] - df_past["vazao"].mean())
            pernovo = pd.DataFrame()
            pernovo["valor"] = per_atual["vazao"]*per_past["vazao"]
            correlation = pernovo["valor"].sum()/(df_atual["vazao"].std()*df_past["vazao"].std()*pernovo["valor"].shape[0])
        df_FAC.iloc[per-1, ord] = correlation
        df_temp = pd.DataFrame({"periodo": [per], "ordem": [ord], "correl":[correlation]})
        lista_FAC_dataFrame.append(df_temp)
        print("passado: ", passado , " per: ", per, " correlation: ", correlation)
print(df_FAC)

df_FAC_novo = pd.concat(lista_FAC_dataFrame).reset_index(drop = True)
print(df_FAC_novo)



def calculate_result_novo(ord, per, FAC):
    A = np.eye(ord)  # Identity matrix of size (ord, ord)
    B = np.zeros(ord)  # Zero vector of size (ord,)    
    for lin in range(ord):
        for ordem_facp in range(1, ord - lin):
            per_anterior = per - 1 - lin
            if per_anterior <= 0:
                per_anterior = per - 1 - lin + len(df_FAC["periodo"].unique())
            valor = FAC.loc[(FAC["periodo"] == per_anterior) & (FAC["ordem"] == ordem_facp)]["correl"].iloc[0]
            A[lin, ordem_facp + lin] = valor
            A[ordem_facp + lin, lin] = valor
    # Fill vector B
    for ordem_facp in range(1, ord + 1):
        valor = FAC.loc[(FAC["periodo"] == per) & (FAC["ordem"] == ordem_facp)]["correl"].iloc[0]
        B[ordem_facp - 1] = valor
    Result = solve(A, B)

    #print("A:", A)
    #print("B:", B)
    #print("Result:", Result)
    return Result

## Resolvendo etapa 2 de estimar a matriz FACP
lista_FACP_dataFrame = []
for per in df_parp["periodo"].unique():
    for ord in range(1,ordemMaxima+1):
            result = calculate_result_novo(ord, per, df_FAC_novo)
            df_temp = pd.DataFrame({"periodo": [per], "ordem": [ord], "partial_correl":[result[-1]]})
            lista_FACP_dataFrame.append(df_temp)
df_FACP_novo = pd.concat(lista_FACP_dataFrame)
print(df_FACP_novo)
exit(1)



def calculate_result(ord, per, FAC):
    # Initialize matrices and vectors
    A = np.eye(ord)  # Identity matrix of size (ord, ord)
    B = np.zeros(ord)  # Zero vector of size (ord,)
    
    # Fill matrix A
    for lin in range(ord):
        for col in range(1, ord - lin):
            per_anterior = per - 2 - lin
            if per_anterior < 0:
                per_anterior = per - 2 - lin + len(df_FAC["periodo"].unique())
            A[lin, col + lin] = FAC.iloc[per_anterior, col]
            A[col + lin, lin] = FAC.iloc[per_anterior, col]
    # Fill vector B
    for t in range(1, ord + 1):
        B[t - 1] = FAC.iloc[per-1, t]

    # Solve the system A * Result = B
    Result = solve(A, B)

    #print("A:", A)
    #print("B:", B)
    #print("Result:", Result)

    return Result



## Resolvendo etapa 2 de estimar a matriz FACP

df_FACP = pd.DataFrame(np.zeros((len(df_parp["periodo"].unique()), ordemMaxima+1)))
df_FACP["periodo"] = df_parp["periodo"].unique()
print(df_FACP)
for per in df_parp["periodo"].unique():
    for ord in range(1,ordemMaxima+1):
            #Eigen::VectorXd Result = resolveYuleWalker(ord,mes2);
            result = calculate_result(ord, per, df_FAC)
            df_FACP.loc[per-1,ord-1] = result[-1]
print(df_FACP)

mapaPeriodoOrdem = {}
for per in df_parp["periodo"].unique():
    df = df_parp.loc[df_parp["periodo"] == per].reset_index(drop = True)
    df_linha_FACP = df_FACP.loc[(df_FACP["periodo"] == per)].drop(columns = ["periodo"]).reset_index(drop = True)
    IC = 1.96 / np.sqrt(df.shape[0] - 3)
    for ord in range(0, ordemMaxima):        
        if df_linha_FACP.iloc[0,ord] >= IC or df_linha_FACP.iloc[0,ord] <= -IC:
            mapaPeriodoOrdem[per] = ord + 1

print(mapaPeriodoOrdem)