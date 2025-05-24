import pandas as pd
import numpy as np
import networkx as nx
import pydot
import matplotlib.pyplot as plt
from anytree import Node, RenderTree
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
caminho_arvore = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\caso_mini_500Cen_cluster_semanais\Dissertacao\Pente"
caminho_arvore = r"C:\Users\testa\Documents\git\3dp-minilab\Academico_Dissertacao\exercicio_1D\semFCF\A_2x2x8\BKAssimetrico"
caminho_arvore = r"C:\Users\testa\Documents\git\3dp-minilab\Academico_Dissertacao\exercicio_1D\semFCF\A_2x2x8\KMeansAssimetricoProbPente"
caminho_arvore = r"C:\Users\testa\Documents\git\3dp-minilab\Academico_Dissertacao\exercicio_36D\A_4x4x2\KMeansAssimetricoProbPente"
caminho_arvore = r"C:\Users\testa\Documents\git\3dp-minilab\Academico_Dissertacao\exercicio_36D\A_4x4x2\BKAssimetrico"
caminho_orig = r"C:\Users\testa\Documents\git\3dp-minilab\Academico_Dissertacao\exercicio_36D\Pente_GVZP"


caminho_arvore1 = r"C:\Users\testa\Documents\git\3dp-minilab\Academico_Dissertacao\exercicio_36D\A_4x4x2\BKAssimetrico"
caminho_arvore2 = r"C:\Users\testa\Documents\git\3dp-minilab\Academico_Dissertacao\exercicio_36D\A_4x4x2\KMeansAssimetricoProbPente"
caminho_arvore3 = r"C:\Users\testa\Documents\git\3dp-minilab\Academico_Dissertacao\exercicio_36D\A_4x4x2\NeuralGas"
caminho_orig = r"C:\Users\testa\Documents\git\3dp-minilab\Academico_Dissertacao\exercicio_36D\Pente_GVZP"


caminho_arvore1 = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\caso_mini_500Cen_cluster_semanais\Dissertacao\Final_TOL001\A_25x3x2\BKAssimetrico"
caminho_arvore2 = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\caso_mini_500Cen_cluster_semanais\Dissertacao\Final_TOL001\A_25x3x2\KMeansAssimetricoProbPente"
#caminho_arvore3 = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\caso_mini_500Cen_cluster_semanais\Dissertacao\Final_TOL001\A_25x3x2\NeuralGas"
caminho_orig = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\caso_mini_500Cen_cluster_semanais\Dissertacao\Final_TOL001\Pente"
caminho_orig = r"C:\Users\testa\Documents\git\3dp-minilab\Academico_Dissertacao\exercicio_36D\Pente_GVZP"
caminho_arvore1 = r"C:\Users\testa\Documents\git\3dp-minilab\Academico_Dissertacao\exercicio_36D\A_4x4x2\BKAssimetrico"
caminho_arvore2 = r"C:\Users\testa\Documents\git\3dp-minilab\Academico_Dissertacao\exercicio_36D\A_4x4x2\KMeansAssimetricoProbPente"
caminho_arvore3 = r"C:\Users\testa\Documents\git\3dp-minilab\Academico_Dissertacao\exercicio_36D\A_4x4x2\NeuralGas"

caminho_orig = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\cenarios_500Cen_cluster_semanais_EOL\EOL_2\Eol_cen\Pente"
caminho_arvore1 = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\cenarios_500Cen_cluster_semanais_EOL\EOL_2\Eol_cen\A_25x3x2\BKAssimetrico"
caminho_arvore2 = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\cenarios_500Cen_cluster_semanais_EOL\EOL_2\Eol_cen\A_25x3x2\KMeansAssimetricoProbPente"
caminho_arvore3 = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\cenarios_500Cen_cluster_semanais_EOL\EOL_2\Eol_cen\A_25x3x2\KMeansSimetricoProbQuadPente"


mapa_nome_caso = {
    caminho_arvore1:"RR",
    caminho_arvore2:"KM",
    caminho_arvore3:"KMS",
    caminho_orig:"Pente",
}
cores = {
    caminho_arvore1:"blue",
    caminho_arvore2:"red",
    caminho_arvore3:"green",
    caminho_orig:"black",
}

lista_casos = [caminho_orig,caminho_arvore2, caminho_arvore1, caminho_arvore3   ] #caminho_arvore3
#print(cenarios)
usina =992
fig2 = make_subplots(rows=1, cols=1, subplot_titles=(" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "))
linha = 1
coluna = 1
contador = 0
mostra_legendaLimites = True

for caso in lista_casos:
    arvore = pd.read_csv(caso+"\\arvore.csv")
    cenarios = pd.read_csv(caso+"\\cenarios.csv")
    estagios = arvore["PER"].unique()
    maior_estagio = arvore["PER"].max()
    total_nodes = arvore["NO"].unique()
    lista_x = []
    lista_y = []
    for est in estagios:
        arvore_est = arvore.loc[(arvore["PER"] == est)]
        nodes_est = arvore_est.loc[(arvore_est["PER"] == est)]["NO"].unique()
        vazoes_per_posto = cenarios.loc[(cenarios["NOME_UHE"] == usina) & (cenarios["NO"].isin(nodes_est))]
        lista_y = lista_y + vazoes_per_posto["VAZAO"].tolist()
        lista_x = lista_x + [est]*len(vazoes_per_posto["VAZAO"].tolist())

    fig2.add_trace(go.Box(
        x=lista_x,
        y=lista_y,  # or simply [0, slope]
        #y=lista_media,  # or simply [0, slope]
        name = mapa_nome_caso[caso],
        legendgroup  = mapa_nome_caso[caso],
        #line=dict(color=colors[contador], width=2),
        marker_color = cores[caso],
        #boxpoints="suspectedoutliers",
        boxpoints=False,
        showlegend=True,
    ), row=linha, col=coluna)
    contador += 1
    mostra_legendaLimites = False
titulo = "Redução Árvore de Cenários"
nome_figura = f"Red_cen"
fig2.update_layout(
    title=titulo,
    title_font=dict(size=30, family="Arial", color="black"),
    xaxis_title="estágios",
    yaxis_title="m3/s",
    font=dict(size=30), 
    xaxis=dict(title_font=dict(size=30)),  
    yaxis=dict(title_font=dict(size=30)),
    boxmode='group',
    showlegend=True
)
fig2.write_html(f"BOX_{nome_figura}.html", auto_open=True)



lista_casos = [caminho_orig,caminho_arvore2, caminho_arvore1,   ]
#print(cenarios)
usinas = [6, 8, 11, 12]
usinas = [17, 18, 34, 156]
usinas = [227, 229, 270, 257]
usinas = [273, 285, 287, 279]
usinas = [24, 25, 31,32]
usinas = [33, 47, 61, 62]
usinas = [63, 74 , 217, 92]
usinas = [93, 115, 77, 222]
usinas = [271, 275, 6, 11]




fig2 = make_subplots(rows=1, cols=1, subplot_titles=(" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "))
linha = 1
coluna = 1
estagio = 2
contador_titulo = 0
mostra_legendaLimites = True
for caso in lista_casos:
    lista_x = []
    lista_y = []
    for usi in usinas:
        arvore = pd.read_csv(caso+"\\arvore.csv")
        cenarios = pd.read_csv(caso+"\\cenarios.csv")
        df_cen_usi = cenarios.loc[(cenarios["NOME_UHE"] == usi)]
        arvore_est = arvore.loc[(arvore["PER"] == estagio)]
        nodes_est = arvore_est.loc[(arvore_est["PER"] == estagio)]["NO"].unique()
        vazoes_per_posto = df_cen_usi.loc[(df_cen_usi["NO"].isin(nodes_est))]
        lista_y = lista_y + (vazoes_per_posto["VAZAO"]).tolist()
        #lista_x = lista_x + [estagio]*len(vazoes_per_posto["VAZAO"].tolist())
        lista_x = lista_x + [str(usi)]*len(vazoes_per_posto["VAZAO"].tolist())

    fig2.add_trace(go.Box(
        x=lista_x,
        y=lista_y,  # or simply [0, slope]
        name = mapa_nome_caso[caso],
        legendgroup  = mapa_nome_caso[caso],
        marker_color = cores[caso],
        #boxpoints="suspectedoutliers",
        boxpoints=False,
        showlegend=True,
    ), row=1, col=1)

    titulo =  "Usina " + str(usina)
    titulo =  "Comparação Boxplot Usinas"
    fig2.layout.annotations[0].update(text=titulo, font=dict(size=20)) 
    contador_titulo += 1
    print("linha: ", linha, " coluna: ", coluna, " anotation: ", contador_titulo)
    coluna = coluna + 1
    if(coluna == 3):
        coluna = 1
        linha = linha + 1
    mostra_legendaLimites = False
titulo = "Redução Árvore de Cenários"
nome_figura = f"Red_cen"
fig2.update_layout(
    title=titulo,
    title_font=dict(size=30, family="Arial", color="black"),
    xaxis_title="estágios",
    yaxis_title="m3/s",
    font=dict(size=30), 
    xaxis=dict(title_font=dict(size=30)),  
    yaxis=dict(title_font=dict(size=30)),
    boxmode='group',
    showlegend=True
)
#fig2.write_html(f"BOX_EST2_{nome_figura}.html", auto_open=True)

