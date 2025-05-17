import pandas as pd
import numpy as np
import networkx as nx
import pydot
import matplotlib.pyplot as plt
from anytree import Node, RenderTree

caminho_arvore = r"C:\Users\testa\Documents\git\3dp-minilab\Academico\exercicio_1D_PenteArvore\2cen\10Perc\Arvore"
caminho_arvore = r"C:\Users\testa\Documents\git\3dp-minilab\Academico\exercicio_1D_PenteArvore\27cen\Orig\Pente_GVZP_27cen"
caminho_arvore = r"C:\Users\testa\Documents\git\3dp-minilab\Academico\exercicio_1D_PenteArvore\27cen\10Perc\Pente_Gerado"

arvore = pd.read_csv(caminho_arvore+"\\arvore.csv")
cenarios = pd.read_csv(caminho_arvore+"\\cenarios.csv")
estagios = arvore["PER"].unique()
maior_estagio = arvore["PER"].max()
total_nodes = arvore["NO"].unique()

for est in estagios:
    nodes_est = arvore.loc[(arvore["PER"] == est)]["NO"].unique()
    #print(nodes_est)
    vazoes_per = cenarios.loc[(cenarios["NO"].isin(nodes_est))]
    #print(vazoes_per)
    media = vazoes_per["VAZAO"].mean()
    desvio = vazoes_per["VAZAO"].std()
    print(f"ESTAGIO {est}  MEDIA {media}  DESVIO {round(desvio,2)}")
