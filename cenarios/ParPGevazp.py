import pandas as pd
import numpy as np
from scipy.linalg import solve


def calculaFAC(df_parp, ordemMaxima):
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
                ## DESVIO PADRAO POPULACIONAL (N), DDOF = 0
                ## DESVIO PADRAO AMOSTRAL (N-1), DDOF = 1
                correlation = pernovo["valor"].sum()/(df_atual["vazao"].std(ddof=1)*df_past["vazao"].std(ddof=1)*pernovo["valor"].shape[0])
            df_temp = pd.DataFrame({"periodo": [per], "ordem": [ord], "correl":[correlation]})
            lista_FAC_dataFrame.append(df_temp)
            #print("passado: ", passado , " per: ", per, " correlation: ", correlation)

    df_FAC = pd.concat(lista_FAC_dataFrame).reset_index(drop = True)
    print(df_FAC)
    return df_FAC


def calculate_result(ord, per, df_FAC):
    A = np.eye(ord)  # Identity matrix of size (ord, ord)
    B = np.zeros(ord)  # Zero vector of size (ord,)    
    for lin in range(ord):
        for ordem_facp in range(1, ord - lin):
            per_anterior = per - 1 - lin
            if per_anterior <= 0:
                per_anterior = per - 1 - lin + len(df_FAC["periodo"].unique())
            valor = df_FAC.loc[(df_FAC["periodo"] == per_anterior) & (df_FAC["ordem"] == ordem_facp)]["correl"].iloc[0]
            A[lin, ordem_facp + lin] = valor
            A[ordem_facp + lin, lin] = valor
    # Fill vector B
    for ordem_facp in range(1, ord + 1):
        valor = df_FAC.loc[(df_FAC["periodo"] == per) & (df_FAC["ordem"] == ordem_facp)]["correl"].iloc[0]
        B[ordem_facp - 1] = valor
    Result = solve(A, B)
    return Result


def calculaFACP(df_parp, df_FAC, ordemMaxima):
    lista_FACP_dataFrame = []
    for per in df_parp["periodo"].unique():
        for ord in range(1,ordemMaxima+1):
                result = calculate_result(ord, per, df_FAC)
                df_temp = pd.DataFrame({"periodo": [per], "ordem": [ord], "partial_correl":[result[-1]]})
                lista_FACP_dataFrame.append(df_temp)
    df_FACP= pd.concat(lista_FACP_dataFrame).reset_index(drop = True)
    print(df_FACP)
    return df_FACP


def encontraOrdensPeriodos(df_parp, df_FACP, ordemMaxima):
        
    mapaPeriodoOrdem = {}
    for per in df_parp["periodo"].unique():
        df = df_parp.loc[df_parp["periodo"] == per].reset_index(drop = True)
        IC = 1.96 / np.sqrt(df.shape[0] - 3)
        for ord in range(1, ordemMaxima+1):        
            valor = df_FACP.loc[(df_FACP["periodo"] == per) & (df_FACP["ordem"] == ord)]["partial_correl"].iloc[0]
            if valor >= IC or valor <= -IC:
                mapaPeriodoOrdem[per] = ord
    print(mapaPeriodoOrdem)
    return mapaPeriodoOrdem


def calculaCoeficientes(df_parp, df_FAC, mapaPeriodoOrdem):
    ## EstimaCoeficientes
    lista_df_coeficientes = []
    for per in df_parp["periodo"].unique():
        ordem = mapaPeriodoOrdem[per]
        coefs = calculate_result(ordem, per, df_FAC)
        contador = 1
        for coef in coefs:
            per_anterior = 0
            per_anterior = per - contador
            if(per_anterior <= 0):
                per_anterior = per - contador + len(df_parp["periodo"].unique())
            contador += 1
            df_temp = pd.DataFrame({"periodo": [per], "ordem": [ordem], "per_anterior": [per_anterior], "coef":[coef]})
            lista_df_coeficientes.append(df_temp)
    df_Coefs= pd.concat(lista_df_coeficientes).reset_index(drop = True)
    print(df_Coefs)
    return df_Coefs


## Calculo dos Resíduos
def calculaResiduosModelos(df_parp, df_Coefs):
    lista_residuos = []
    for per in df_parp["periodo"].unique():
        df_per = df_parp.loc[(df_parp["periodo"] == per)].reset_index(drop = True)
        for data in df_per["Data"].unique()[1:]:
            ano = data.year
            vazao = (df_per.loc[(df_per["Data"].dt.year == ano)]["vazao"].iloc[0] - df_per["vazao"].mean())/df_per["vazao"].std(ddof=0) ## USANDO DESVIO PADRAO POPULACIONAL
            df_coef = df_Coefs.loc[(df_Coefs["periodo"] == per)].reset_index(drop = True)
            for index, row in df_coef.iterrows():  # `_` ignores the index
                ano_per_anterior = ano - 1 if per < row["per_anterior"] else ano 
                df_per_anterior =  df_parp.loc[(df_parp["periodo"] == row["per_anterior"])]
                vazao_anterior = df_per_anterior.loc[(df_per_anterior["Data"].dt.year == ano_per_anterior)]["vazao"].iloc[0]
                vazao = vazao - row["coef"]*(vazao_anterior - df_per_anterior["vazao"].mean())/df_per_anterior["vazao"].std(ddof=0)
            df_temp = pd.DataFrame({"Data": [data], "periodo": [per], "residuo":[vazao]})
            lista_residuos.append(df_temp)

    df_residuos = pd.concat(lista_residuos).reset_index(drop = True)
    print(df_residuos)

