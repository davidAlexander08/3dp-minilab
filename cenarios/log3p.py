import pandas as pd
import numpy as np
from scipy.linalg import solve
import math

def calculaVazaoMinima(dfTemporal):
 # Step 1: Set eas to assimetriaSerie or 0.05 if it is <= 0
    eas = dfTemporal["vazao"].skew()
    mediaSerie = dfTemporal["vazao"].mean()
    desviopadraoSerie = dfTemporal["vazao"].std(ddof = 0)
    if eas <= 0:
        eas = 0.05
    
    # Step 2: Calculate A, B, C, and FI
    A = 1 + (eas ** 2) / 2
    B = math.sqrt((eas ** 2) / 2 + (eas ** 4) / 4)
    C = 1 / 3
    FI = (A + B) ** C + (A - B) ** C - 1
    
    # Step 3: Calculate deslocamento
    deslocamento = (mediaSerie - math.sqrt((desviopadraoSerie ** 2) / (FI - 1)))
    vazaoMinima = min(dfTemporal["vazao"])
    D = mediaSerie - (3 * desviopadraoSerie)
    if vazaoMinima >= 0:
        Z = 0
        D = max(Z, D)
    if D < 0:
        if eas >= 4:
            vazaoMinima = max(D, vazaoMinima * 1.4)
        elif eas >= 2:
            if deslocamento >= 0:
                A = min(D, vazaoMinima)
                vazaoMinima = max(D, A * 1.5)
            else:
                vazaoMinima = max(D, vazaoMinima * 1.5)
        elif eas >= 1:
            vazaoMinima = max(D, vazaoMinima * 1.65)
        else:
            vazaoMinima = max(D, vazaoMinima * 1.85)
    else:
        if eas >= 4:
            vazaoMinima = max(D, vazaoMinima * 0.6)
        elif eas >= 2:
            if deslocamento >= 0:
                A = min(D, vazaoMinima)
                vazaoMinima = max(D, A * 0.5)
            else:
                vazaoMinima = max(D, vazaoMinima * 0.5)
        elif eas >= 1:
            vazaoMinima = max(D, vazaoMinima * 0.35)
        else:
            vazaoMinima = max(D, vazaoMinima * 0.15)
    
    # Return the final vazaoMinima
    return vazaoMinima



def transformaLog3P(ruidosCorrelacinados_posto, df_posto_per, df_residuos_periodo, parteDeterministica):
    desvio = df_posto_per["vazao"].std(ddof = 0)
    media = df_posto_per["vazao"].mean()
    desvioResiduos = df_residuos_periodo["residuo"].std(ddof = 0)
    mediaResiduos = df_residuos_periodo["residuo"].mean()

    vazaoMinima = calculaVazaoMinima(df_posto_per)
    #print("vazaoMinima: ", vazaoMinima , " parteDeterministica: ", parteDeterministica , " desvio: ", desvio)
    deslocamento = (vazaoMinima - parteDeterministica)/desvio
    # Calculate BFI, BMEDN, BDPADN, NI, and EXC
    BFI = 1 + (desvioResiduos ** 2) / ((mediaResiduos - deslocamento) ** 2)
    BMEDN = 0.5 * np.log((desvioResiduos ** 2) / (BFI ** 2 - BFI))
    BDPADN = np.sqrt(np.log(BFI))
    NI = np.sqrt(np.exp(BDPADN ** 2) - 1)
    EXC = (NI ** 8 + 6 * NI ** 6 + 15 * NI ** 4 + 16 * NI ** 2)

    ruidoslog3p = np.zeros_like(ruidosCorrelacinados_posto)

    for abertura in range(0, ruidosCorrelacinados_posto.shape[0]):
        ruidoslog3p[abertura] = np.exp(BMEDN + ruidosCorrelacinados_posto[abertura] * BDPADN) + deslocamento
        #print("BMEDN: ", BMEDN , " ruidosCorrelacinados_posto[abertura]: ", ruidosCorrelacinados_posto[abertura], " BDPADN: ", BDPADN , " deslocamento: ", deslocamento)
    return ruidoslog3p
