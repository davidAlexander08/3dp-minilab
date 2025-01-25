import pandas as pd
import numpy as np
from scipy.linalg import solve

def retornaMatrizCarga(lista_postos):
    mapaMatrizCorrelacoesPeriodo = {}
    for per in lista_postos[0].historico["periodo"].unique():
        matrizDeCorrelacaoEspacial = np.eye((len(lista_postos)))
        for linha in range(len(lista_postos)):
            for coluna in range(linha, len(lista_postos)):
                if linha < len(lista_postos) and coluna < len(lista_postos) and linha != coluna:
                    df_usi1 = lista_postos[linha].historico.loc[lista_postos[linha].historico["periodo"] == per].reset_index(drop = True)
                    df_usi2 = lista_postos[coluna].historico.loc[lista_postos[coluna].historico["periodo"] == per].reset_index(drop = True)
                    correlacao = df_usi1["vazao"].corr(df_usi2["vazao"])
                    matrizDeCorrelacaoEspacial[linha, coluna] = correlacao
                    matrizDeCorrelacaoEspacial[coluna, linha] = correlacao  # Symmetric matrix
        U, S, Vt = np.linalg.svd(matrizDeCorrelacaoEspacial, full_matrices=False)
        U = U*-1
        Vt = Vt*-1
        matrizdiagonal = np.zeros((matrizDeCorrelacaoEspacial.shape[1], matrizDeCorrelacaoEspacial.shape[1]))
        for i in range(len(S)):
            matrizdiagonal[i, i] = np.sqrt(S[i])  # Square root of singular values
        matrizCarga = np.dot(U, matrizdiagonal)
        matrizCarga_alternative = np.dot(U, np.diag(S))
        mapaMatrizCorrelacoesPeriodo[per] = matrizCarga_alternative
    return mapaMatrizCorrelacoesPeriodo