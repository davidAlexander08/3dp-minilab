import pandas as pd
import numpy as np
from scipy.linalg import solve

def retornaMatrizCarga(lista_postos):
    mapaMatrizCorrelacoesPeriodo = {}
    for per in lista_postos[0]["periodo"].unique():
        matrizDeCorrelacaoEspacial = np.eye((len(lista_postos)))
        for linha in range(len(lista_postos)):
            for coluna in range(linha, len(lista_postos)):
                if linha < len(lista_postos) and coluna < len(lista_postos) and linha != coluna:
                    #print("per: ", per, " linha: ", linha ," coluna: ", coluna)
                    #correlacao = estudosEstatisticos.correlacaoEntreVetores(
                    #    lista_postos[linha],
                    #    lista_postos[coluna]
                    #)
                    df_usi1 = lista_postos[linha].loc[lista_postos[linha]["periodo"] == per].reset_index(drop = True)
                    df_usi2 = lista_postos[coluna].loc[lista_postos[coluna]["periodo"] == per].reset_index(drop = True)
                    correlacao = df_usi1["vazao"].corr(df_usi2["vazao"])
                    matrizDeCorrelacaoEspacial[linha, coluna] = correlacao
                    matrizDeCorrelacaoEspacial[coluna, linha] = correlacao  # Symmetric matrix
        #print(matrizDeCorrelacaoEspacial)

        # Assuming matrizDeCorrelacaoEspacial is a NumPy array (matrix)
        U, S, Vt = np.linalg.svd(matrizDeCorrelacaoEspacial, full_matrices=False)
        U = U*-1
        Vt = Vt*-1
        #print("U: ", U)
        #print("S: ", S)
        #print("Vt: ", Vt)
        matrizdiagonal = np.zeros((matrizDeCorrelacaoEspacial.shape[1], matrizDeCorrelacaoEspacial.shape[1]))
        for i in range(len(S)):
            matrizdiagonal[i, i] = np.sqrt(S[i])  # Square root of singular values
            #print(i)
            #print(f"FOR i: \n {matrizdiagonal}")

        #print("\n matrizdiagonal after the loop : \n", matrizdiagonal)
        matrizCarga = np.dot(U, matrizdiagonal)
        matrizCarga_alternative = np.dot(U, np.diag(S))
        #print("\n Matriz De Carga : \n", matrizCarga)
        #print("\n Matriz De matrizCarga_alternative : \n", matrizCarga_alternative)
        # U, S, and Vt are the results of the SVD
        # - U is the left singular vectors (thin U in the case of full_matrices=False)
        # - S is the singular values (a 1D array)
        # - Vt is the transpose of the right singu
        mapaMatrizCorrelacoesPeriodo[per] = matrizCarga_alternative
    return mapaMatrizCorrelacoesPeriodo