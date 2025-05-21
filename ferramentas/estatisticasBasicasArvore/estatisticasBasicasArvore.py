import pandas as pd
import numpy as np
import networkx as nx
import pydot
import matplotlib.pyplot as plt
from anytree import Node, RenderTree

def getFilhos(no, df_arvore):
    filhos = df_arvore[df_arvore["NO_PAI"] == no]["NO"].values
    return filhos

def busca_pai(no, df_arvore):
    pai = df_arvore[df_arvore["NO"] == no]["NO_PAI"].values[0]
    return pai

def retorna_lista_caminho(no, df_arvore):
    lista = [no]
    no_inicial = no
    periodo_no = df_arvore[df_arvore["NO"] == no]["PER"].values[0]
    for _ in range(periodo_no - 1):
        pai = busca_pai(no_inicial, df_arvore)
        lista.append(pai)
        no_inicial = pai
    return lista

def retorna_lista_caminho_forward(no, df_arvore):
    lista = [no]
    no_inicial = no
    periodo_no = df_arvore[df_arvore["NO"] == no]["PER"].values[0]
    max_per = df_arvore["PER"].max()
    for _ in range(max_per-periodo_no):
        filho = getFilhos(no_inicial, df_arvore)[0]
        lista.append(filho)
        no_inicial = filho
    return lista
caminho_arvore = r"C:\Users\testa\Documents\git\3dp-minilab\Academico\exercicio_1D_PenteArvore\2cen\10Perc\Arvore"
caminho_arvore = r"C:\Users\testa\Documents\git\3dp-minilab\Academico\exercicio_1D_PenteArvore\27cen\Orig\Pente_GVZP_27cen"
caminho_arvore = r"C:\Users\testa\Documents\git\3dp-minilab\Academico\exercicio_1D_PenteArvore\27cen\10Perc\Pente_Gerado"
caminho_arvore = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\caso_mini_500Cen_cluster_semanais\Dissertacao\Casos_A\A_25x3x2\KMeansAssimetricoProbPente"
caminho_arvore = r"C:\Users\testa\Documents\git\3dp-minilab\Academico_Dissertacao\exercicio_1D\semFCF\A_4x4x2\BKAssimetrico"
caminho_arvore = r"C:\Users\testa\Documents\git\3dp-minilab\Academico_Dissertacao\exercicio_1D\semFCF\Pente_GVZP"
caminho_arvore = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\caso_mini_500Cen_cluster_semanais\Dissertacao\Pente"

arvore = pd.read_csv(caminho_arvore+"\\arvore.csv")
cenarios = pd.read_csv(caminho_arvore+"\\cenarios.csv")
estagios = arvore["PER"].unique()
maior_estagio = arvore["PER"].max()
total_nodes = arvore["NO"].unique()
#print(cenarios)
usina =169

lista_df  = []
for est in estagios:
    nodes_est = arvore.loc[(arvore["PER"] == est)]["NO"].unique()
    arvore_est = arvore.loc[(arvore["PER"] == est)]
    vazoes_per_posto = cenarios.loc[(cenarios["NOME_UHE"] == usina)]
    for node in nodes_est:
        vazao_posto_node = vazoes_per_posto.loc[(vazoes_per_posto["NO"] == node)]["VAZAO"].iloc[0]
        prob_cond = 1
        caminho = retorna_lista_caminho(node, arvore)
        for elemento in caminho:
            prob_elemento = arvore.loc[(arvore["NO"] == elemento)]["PROB"].iloc[0]
            prob_cond = prob_cond*prob_elemento
        
        lista_df.append(
            pd.DataFrame({
                "NO":[node],
                "EST":[est],
                "PROB":[round(prob_cond,4)],
                "VAZAO":[round(vazao_posto_node,2)],
            })
        )

resultado_final = pd.concat(lista_df).reset_index(drop = True)
resultado_final.to_csv(f"{caminho_arvore}\\arvore_usi_{usina}.csv", index=False)

for est in estagios:
    nodes_est = arvore.loc[(arvore["PER"] == est)]["NO"].unique()
    #print(nodes_est)
    arvore_est = arvore.loc[(arvore["PER"] == est)]
    vazoes_per = resultado_final.loc[(resultado_final["NO"].isin(nodes_est))]
    
    #print(vazoes_per)
    media = vazoes_per["VAZAO"].mean()
    desvio = vazoes_per["VAZAO"].std()
    print(f"ESTAGIO {est}  MEDIA {media}  DESVIO {round(desvio,2)}")
