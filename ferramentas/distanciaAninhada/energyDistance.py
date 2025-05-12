# Codigo transforma ECO
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import MiniBatchKMeans
import math
import os
from datetime import timedelta  # <-- Add this import at the top of your script
import random
import time
from scipy.spatial.distance import cdist

def getFilhos(no, df_arvore):
    filhos = df_arvore[df_arvore["NO_PAI"] == no]["NO"].values
    return filhos

def busca_pai(no, df_arvore):
    pai = df_arvore[df_arvore["NO"] == no]["NO_PAI"].values[0]
    return pai

def retorna_lista_caminho(no, df_arvore):
    lista = []
    lista.append(no)
    no_inicial = no
    periodo_no = df_arvore.loc[df_arvore["NO"] == no, "PER"].iloc[0]
    
    for est in range(1, periodo_no):
        pai = busca_pai(no_inicial, df_arvore)
        lista.append(pai)
        no_inicial = pai
    
    return lista

caminho = r"C:\Users\testa\Documents\git\3dp-minilab\Carmen\exercicio_27cen_1D\27_Aberturas_Equiprovavel\Pente_GVZP"
arvore = pd.read_csv(caminho+"\\arvore.csv")
cenarios = pd.read_csv(caminho+"\\cenarios.csv")

caminho_modelo = r"C:\Users\testa\Documents\git\3dp-minilab\Carmen\exercicio_27cen_1D\27_Aberturas_Equiprovavel\Pente_8cen\A_8cen_1"
arvore_modelo = pd.read_csv(caminho_modelo+"\\arvore.csv")
cenarios_modelo = pd.read_csv(caminho_modelo+"\\cenarios.csv")

ultimo_estagio = arvore["PER"].max()
folhas = arvore[arvore["PER"] == ultimo_estagio]["NO"].values

ultimo_estagio_modelo = arvore_modelo["PER"].max()
folhas_modelo = arvore_modelo[arvore_modelo["PER"] == ultimo_estagio_modelo]["NO"].values
# === Step 2: Build paths for each leaf ===
paths = []
for folha in folhas:
    caminho = retorna_lista_caminho(folha, arvore)
    paths.append(caminho[::-1][1:])  # Reverse to get from root -> leaf

paths_modelo = []
for folha in folhas_modelo:
    caminho = retorna_lista_caminho(folha, arvore_modelo)
    paths_modelo.append(caminho[::-1][1:])

print(paths)
print(paths_modelo)


# === Step 3: Collect sequence of values along each path ===
# Assuming cenarios["VAZAO"] has the variable you care about (e.g., hydrology)
def build_matrix(paths, cenarios):
    matrix = []
    for path in paths:
        values = []
        for no in path:
            vazoes = cenarios.loc[cenarios["NO"] == no, "VAZAO"].values
            values.extend(vazoes)  # Append all realizations
        matrix.append(values)
    return np.array(matrix)

X = build_matrix(paths, cenarios)  # Original tree paths
Y = build_matrix(paths_modelo, cenarios_modelo)  # Reduced tree paths

print(X)
print(Y)


# === Step 4: Get probabilities ===
# You must have the probabilities in the tree file
probs_X = []
for folha in folhas:
    prob_cond = 1
    caminho_folha = retorna_lista_caminho(folha, arvore)
    for node in caminho_folha:
        prob = arvore.loc[arvore["NO"] == node, "PROB"].values[0]
        prob_cond = prob_cond*prob
    probs_X.append(prob_cond)
#probs_X = np.array(probs_X)

probs_Y = []
for folha in folhas_modelo:
    prob_cond = 1
    caminho_folha = retorna_lista_caminho(folha, arvore)
    for node in caminho_folha:
        prob = arvore.loc[arvore["NO"] == node, "PROB"].values[0]
        prob_cond = prob_cond*prob
    probs_Y.append(prob_cond)
#probs_Y = np.array(probs_Y)

print(probs_X)
print(probs_Y)
probs_X = np.array(probs_X)
probs_Y = np.array(probs_Y)

# === Step 5: Energy Distance ===
def energy_distance_weighted(X, probs_X, Y, probs_Y):
    dists_xx = cdist(X, X, metric="euclidean")
    dists_yy = cdist(Y, Y, metric="euclidean")
    dists_xy = cdist(X, Y, metric="euclidean")
    print("dists_xx: ", dists_xx)
    print("dists_yy: ", dists_yy)
    print("dists_xy: ", dists_xy)
    term_xx = np.sum(probs_X[:, None] * probs_X[None, :] * dists_xx)
    term_yy = np.sum(probs_Y[:, None] * probs_Y[None, :] * dists_yy)
    term_xy = np.sum(probs_X[:, None] * probs_Y[None, :] * dists_xy)
    
    return 2 * term_xy - term_xx - term_yy

distance = energy_distance_weighted(X, probs_X, Y, probs_Y)

print(f"Energy Distance between trees = {distance:.6f}")