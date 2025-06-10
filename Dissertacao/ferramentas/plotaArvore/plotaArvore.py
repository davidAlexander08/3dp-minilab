import sys
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from anytree import Node, RenderTree
import os

def printaArvore(texto, path_saida, df_arvore):
    df_arvore_plota = df_arvore.copy()
    estagios = df_arvore_plota["PER"].unique()
    for est in estagios:
        total_nos_estagio = df_arvore_plota.loc[df_arvore_plota["PER"] == est]["NO"].unique()
        print("EST: ", est, " Total NOS: ", len(total_nos_estagio))
    df_arvore_plota.loc[df_arvore_plota["NO_PAI"] == 0, "NO_PAI"] = 1
    #df_arvore.loc[df_arvore["NO_PAI"] == 0, "NO_PAI"] = -1  # You can use any value that is not part of the graph
    G = nx.DiGraph()
    for _, row in df_arvore_plota.iterrows():
        if row['NO_PAI'] != row['NO']:
            G.add_edge(row['NO_PAI'], row['NO'], weight=row['PROB'])
    pos = nx.drawing.nx_pydot.pydot_layout(G, prog='dot')
    plt.figure(figsize=(15, 12))
    nx.draw(G, pos, with_labels=True, node_size=1, node_color='lightblue', font_size=1, font_weight='bold', arrows=False)
    
    #edge_labels = nx.get_edge_attributes(G, 'weight')
    #nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    plt.savefig(path_saida+"\\"+texto+".png", format="png", dpi=100, bbox_inches="tight")
    plt.title("Tree Visualization")
    #plt.show()

texto = "imagem.png"
path_arvore = r"C:\Users\testa\Documents\git\3dp-minilab\Academico_Dissertacao\exercicio_36D\A_4x4x2\BKAssimetrico"
df_arvore = pd.read_csv(path_arvore+"\\arvore.csv")
printaArvore(texto, path_arvore, df_arvore)