import pandas as pd
import numpy as np
import networkx as nx
import pydot
import matplotlib.pyplot as plt
from anytree import Node, RenderTree

def printaArvore(texto, df_arvore, df_cenarios, path):
    df_arvore.loc[df_arvore["NO_PAI"] == 0, "NO_PAI"] = 1
    #df_arvore.loc[df_arvore["NO_PAI"] == 0, "NO_PAI"] = -1  # You can use any value that is not part of the graph
    G = nx.DiGraph()
    for _, row in df_arvore.iterrows():
        if row['NO_PAI'] != row['NO']:
            G.add_edge(row['NO_PAI'], row['NO'], weight=row['PROB'])
    # Add inflow as node attribute
    inflow_dict = df_cenarios.set_index("NO")["VAZAO"].to_dict()
    nx.set_node_attributes(G, inflow_dict, name="inflow")
    pos = nx.drawing.nx_pydot.pydot_layout(G, prog='dot')
    plt.figure(figsize=(20, 15))
    nx.draw(G, pos, with_labels=True, node_size=2000, node_color='lightblue', font_size=1, font_weight='bold', arrows=False)
    
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)
    # Node labels with inflow values
    node_labels = {
        node: f"{node}\n{G.nodes[node].get('inflow', 'NA')}" for node in G.nodes
    }
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=10)
    plt.title("Tree Visualization")
    plt.savefig(caminho_saida+ "\\"+texto+".png", format="png", dpi=100, bbox_inches="tight")
    
    #plt.show()

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

caminho_arvore = r"C:\Users\testa\Documents\git\3dp-minilab\Academico\exercicio_1D_PenteArvore\27cen\1Perc\Arvore"
caminho_saida = r"C:\Users\testa\Documents\git\3dp-minilab\Academico\exercicio_1D_PenteArvore\27cen\1Perc\Pente_Gerado"

caminho_arvore = r"C:\Users\testa\Documents\git\3dp-minilab\Academico\exercicio_1D_PenteArvore\2cen\10Perc\Arvore"
caminho_saida = r"C:\Users\testa\Documents\git\3dp-minilab\Academico\exercicio_1D_PenteArvore\2cen\10Perc\Pente_Gerado"

arvore = pd.read_csv(caminho_arvore+"\\arvore.csv")
cenarios = pd.read_csv(caminho_arvore+"\\cenarios.csv")

estagios = arvore["PER"].unique()
maior_estagio = arvore["PER"].max()
total_nodes = arvore["NO"].unique()

lista_df =[]
lista_df_cenarios = []

folhas = arvore.loc[arvore["PER"] == maior_estagio]["NO"].unique()
print(folhas)

lista_df_cenarios.append(
    cenarios.loc[(cenarios["NO"] == 1)]
)
lista_df.append(
    arvore.loc[(arvore["NO"] == 1)]
)


print(lista_df)
print(lista_df_cenarios)
contador_nodes = 2
for idx,folha in enumerate(folhas):
    caminho = retorna_lista_caminho(folha, arvore)
    caminho = [est for est in caminho if est not in [1]][::-1]
    print("caminho: ", caminho)
    for elemento in caminho:
        no_pai = contador_nodes - 1
        estagio_node = arvore.loc[(arvore["NO"] == elemento)]["PER"].iloc[0]
        vazao = cenarios.loc[(cenarios["NO"] == elemento)]["VAZAO"].iloc[0]
        prob = 1
        abertura = 1
        if(estagio_node == 2):
            no_pai = 1
            no_pai = arvore.loc[(arvore["NO"] == elemento)]["NO_PAI"].iloc[0]
            prob = 1/len(folhas)
            abertura = idx
        lista_df.append(
            pd.DataFrame(
                {
                    "NO_PAI":no_pai,
                    "NO":contador_nodes,
                    "Abertura":abertura,
                    "PER":estagio_node,
                    "PROB":prob,
                },
                index = [0]
            )
        )
        lista_df_cenarios.append(
            pd.DataFrame(
                {
                    "NOME_UHE":6,
                    "NO":contador_nodes,
                    "VAZAO":vazao,
                },
                index = [0]
            )
        )

        contador_nodes += 1

df_arvore = pd.concat(lista_df).reset_index(drop =True)
df_cenarios = pd.concat(lista_df_cenarios).reset_index(drop =True)



df_arvore.to_csv(caminho_saida+"\\arvore.csv", index=False)
df_cenarios.to_csv(caminho_saida+"\\cenarios.csv", index=False)



printaArvore("arvore", df_arvore, df_cenarios, caminho_saida)
printaArvore("arvore_orig", arvore, cenarios, caminho_saida)


print(df_arvore)
print(df_cenarios)