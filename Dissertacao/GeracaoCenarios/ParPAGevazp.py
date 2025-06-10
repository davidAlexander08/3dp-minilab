import pandas as pd
import numpy as np
from scipy.linalg import solve
from ParPGevazp import *

def exec_PARPA(df_parp, ordemMaxima):
    ## Metodo PAR-P GEVAZP
    df_FAC = calculaFAC(df_parp, ordemMaxima)
    df_anual = calculaHistoricoMediasAnuais(df_parp)
    df_FAC_Anual = calculaFACAnual(df_parp, df_anual, ordemMaxima)
    df_FACP = calculaFACPPARPA(df_parp, df_anual, df_FAC, df_FAC_Anual, ordemMaxima)
    mapaPeriodoOrdem = encontraOrdensPeriodos(df_parp, df_FACP, ordemMaxima-1)
    df_Coefs = calculaCoeficientes(df_parp, df_FAC, mapaPeriodoOrdem)
    df_residuos = calculaResiduosModelos(df_parp, df_Coefs)
    return [df_Coefs, df_residuos]

def calculaHistoricoMediasAnuais(df_parp):
    df_anual = pd.DataFrame()
    df_anual["coefA"] = df_parp['vazao'].rolling(window=len(df_parp["periodo"].unique())).mean()
    df_anual["start_date"] = df_parp["Data"].shift(len(df_parp["periodo"].unique())-1)  # The first date in the rolling window
    df_anual["end_date"] = df_parp["Data"]             # The last date in the rolling window
    df_anual = df_anual.iloc[:-1].reset_index(drop = True)
    df_anual["periodo"] = df_parp["periodo"][1:].reset_index(drop = True)
    df_anual = df_anual.dropna()
    df_anual = df_anual.reset_index(drop = True)
    
    #print(df_anual)
    for per in df_parp["periodo"].unique():
        df_teste = df_anual.loc[(df_anual["periodo"] == per)].reset_index(drop = True)
        #print("per: ",  per, " mean: ", df_teste["coefA"].mean(), " std: ", df_teste["coefA"].std(ddof = 0))
    return df_anual






def calculaFACAnual(df_parp, df_anual, ordemMaxima):
    lista_FAC_dataFrame = []
    for per in df_parp["periodo"].unique():
        df_per_anual = df_anual.loc[df_anual["periodo"] == per].reset_index(drop = True)
        mediaA = df_per_anual["coefA"].mean()
        stdA = df_per_anual["coefA"].std(ddof=0)
        for ord in range(0,ordemMaxima):
            passado = per - ord         
            eliminaAno = 0   
            if(passado <= 0):
                passado = per - ord + len(df_parp["periodo"].unique())
                eliminaAno = 1

            df_per_temp = df_parp.loc[df_parp["periodo"] == passado].reset_index(drop = True)
            dev_hist, mean_hist = df_per_temp["vazao"].std(ddof =0), df_per_temp["vazao"].mean()

            df_per = df_per_temp.iloc[1:] if eliminaAno == 0 else df_per_temp.iloc[:-1]
            df_per = df_per.reset_index(drop = True)

            df_anual_temp = df_per_anual.copy()
            df_anual_temp["coefA"] -= mediaA  # Subtract mediaA directly
            df_per["vazao"] -= mean_hist      # Subtract mean_hist directly
            correlation = (df_anual_temp["coefA"] * df_per["vazao"]).sum() / (stdA * dev_hist * len(df_per_temp["vazao"]))
            lista_FAC_dataFrame.append(pd.DataFrame({"periodo": [per], "ordem": [ord+1], "correl":[correlation]}))
    df_FAC_Anual = pd.concat(lista_FAC_dataFrame).reset_index(drop = True)
    return df_FAC_Anual










def calculaFACPPARPA(df_parp, df_anual, df_FAC, df_FAC_Anual, ordemMaxima):
    lista_coefs = []
    ##Calculo das matrizes de covariância
    for per in df_parp["periodo"].unique():
        for ord in range(1,ordemMaxima):
            #if(ord == 2): exit(1)
            #print("per: ", per, " ord: ", ord)
            
            rho = df_FAC.loc[(df_FAC["periodo"] == per) & (df_FAC["ordem"] == ord) ]["correl"].iloc[0]

            M11 = np.eye(2)
            M11[0, 1] = rho
            M11[1, 0] = rho
            #print("M11: ", M11)

            rhos_anual  = df_FAC_Anual.loc[(df_FAC_Anual["periodo"] == per) & (df_FAC_Anual["ordem"] == 1)]["correl"].iloc[0]
            rhos_lag  = df_FAC_Anual.loc[(df_FAC_Anual["periodo"] == per) & (df_FAC_Anual["ordem"] == ord+1)]["correl"].iloc[0]

            M21 = np.zeros((2, ord))
            M21[0, ord - 1] = rhos_anual
            M21[1, ord - 1] = rhos_lag
            
            lag = 0
            if ord > 1:
                for i in range(1, ord):
                    #print("per: ", per, " i: ", i)
                    rho = df_FAC.loc[(df_FAC["periodo"] == per) & (df_FAC["ordem"] == i) ]["correl"].iloc[0]
                    M21[0, i-1] = rho
                    lag = per - i
                    if lag <= 0:
                        lag += len(df_parp["periodo"].unique())
                    #print("i: ", i , " lag: ", lag)
                    rho_1 = df_FAC.loc[(df_FAC["periodo"] == lag) & (df_FAC["ordem"] == ord-i) ]["correl"].iloc[0]
                    M21[1, i-1] = rho_1
            #print("M21: ", M21)

            M12 = M21.T

            #print("M12: ", M12)
            M22 = np.identity(ord)
            for linha in range(ord):
                contador = 0
                for coluna in range(linha, ord):
                    if linha != coluna:
                        lag = per - linha - 1
                        if lag <= 0:
                            lag += 12
                        #print("linha: ", linha, " lag: ", lag, " coluna: ", coluna, " per: ", per, " ord: ", ord)
                        if coluna == ord - 1:
                            rho = df_FAC_Anual.loc[(df_FAC_Anual["periodo"] == per) & (df_FAC_Anual["ordem"] == linha + 2) ]["correl"].iloc[0]
                            M22[linha, coluna] = rho
                            M22[coluna, linha] = rho
                        else:
                            contador += 1
                            rho = df_FAC.loc[(df_FAC["periodo"] == lag) & (df_FAC["ordem"] == contador) ]["correl"].iloc[0]
                            M22[linha, coluna] = rho
                            M22[coluna, linha] = rho

            invM22 = np.linalg.inv(M22)
            #print("M22: ", M22)
            Resultado = M11 + (M21 @ invM22) @ M12
            phi = Resultado[0, 1] / (np.sqrt(Resultado[0, 0]) * np.sqrt(Resultado[1, 1]))
            #coeficientesDeCorrelacaoParcial[periodo, ord - 1] = phi
            print("per: ", per, " ord: ", ord, " phi: ", phi)
            lista_coefs.append(pd.DataFrame({"periodo": [per], "ordem": [ord], "partial_correl":[phi]}))
    df_coefs_a = pd.concat(lista_coefs).reset_index(drop = True)
    return df_coefs_a

