import pandas as pd
import numpy as np
import networkx as nx
import pydot
import matplotlib.pyplot as plt
from anytree import Node, RenderTree

def printaArvore(texto, df_arvore, df_cenarios):
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
    plt.savefig(texto+".png", format="png", dpi=100, bbox_inches="tight")
    
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

caminho_pente = r"C:\Users\testa\Documents\git\3dp-minilab\Academico\exercicio_1D\Exercicio_Pente_Arvore\Pente_GVZP_27cen"
#caminho_pente = r"C:\Users\testa\Documents\git\3dp-minilab\Academico\exercicio_1D_Debora\Pente_GVZP_8cen"
#caminho_pente = r"C:\Users\testa\Documents\git\3dp-minilab\Academico\exercicio_1D_Debora\Pente_GVZP_2cen"
#caminho_pente = r"C:\Users\testa\Documents\git\3dp-minilab\Academico\exercicio_1D_Debora\Pente_GVZP_4cen"
#caminho_saida = r"C:\Users\testa\Documents\git\3dp-minilab\Academico\exercicio_1D_Debora\Arvore_2_2_2"
#caminho_saida = r"C:\Users\testa\Documents\git\3dp-minilab\Academico\exercicio_1D_Debora\Arvore_4_2_2"
#caminho_saida = r"C:\Users\testa\Documents\git\3dp-minilab\Academico\exercicio_1D_Debora\Arvore_8_2_2"
caminho_saida = r"C:\Users\testa\Documents\git\3dp-minilab\Academico\exercicio_1D\Exercicio_Pente_Arvore\Arvore_27_2_2"
arvore = pd.read_csv(caminho_pente+"\\arvore.csv")
cenarios = pd.read_csv(caminho_pente+"\\cenarios.csv")

print(arvore)
print(cenarios)
estagios = arvore["PER"].unique()
total_nodes = arvore["NO"].unique()
print(total_nodes)
lista_df =[]
lista_df_cenarios = []
aberturas = 2
novo_node = 1
estagios_filtrados = [est for est in estagios if est not in [1]][::-1]
max_node = arvore["NO"].max()
contador_novos_nodes = max_node + 1
print("contador_novos_nodes: ", contador_novos_nodes)

lista_df_cenarios.append(
    cenarios.loc[(cenarios["NO"] == 1)]
)
print(lista_df)
print(lista_df_cenarios)
aberturas = [1,1,2,2]

print(aberturas)
df_arvore = arvore.copy()
df_cenarios = cenarios.copy()
for idx,est in enumerate(estagios):
    df_arvore_est = df_arvore.loc[(df_arvore["PER"] == est)]
    if(est == 1):
        lista_df.append(df_arvore_est)
    else:
        nodes_est = df_arvore_est["NO"].unique()
        for node in nodes_est:
            
            caminho_forward = retorna_lista_caminho_forward(node, df_arvore)
            lista_df_novo = []
            lista_df_vaz = []
            
            if(aberturas[idx] != 1):
                print("est: ", est, " idx: ", idx)
                max_node = df_arvore["NO"].max()+1
                lista_df_novo.append(df_arvore)
                lista_df_vaz.append(df_cenarios)
                for abertura in range(1,aberturas[idx]):
                    print("abertura: ", abertura)
                    for node_caminho in caminho_forward:
                        no_pai = max_node - 1
                        estagio_node = df_arvore.loc[(df_arvore["NO"] == node_caminho)]["PER"].iloc[0]
                        vazao = df_cenarios.loc[(df_cenarios["NO"] == node_caminho)]["VAZAO"].iloc[0]
                        prob = 1
                        vazao_node = vazao
                        if(estagio_node == est):
                            no_pai = 1
                            no_pai = df_arvore.loc[(df_arvore["NO"] == node)]["NO_PAI"].iloc[0]
                            prob = 1/aberturas[idx]
                            vazao_node = vazao + vazao/aberturas[idx]
                        lista_df_novo.append(
                            pd.DataFrame(
                                {
                                    "NO_PAI":no_pai,
                                    "NO":max_node,
                                    "Abertura":abertura,
                                    "PER":estagio_node,
                                    "PROB":prob,
                                },
                                index = [0]
                            )
                        )
                        lista_df_vaz.append(
                            pd.DataFrame(
                                {
                                    "NOME_UHE":6,
                                    "NO":max_node,
                                    "VAZAO":vazao_node,
                                },
                                index = [0]
                            )
                        )
                        max_node += 1
                elemento_inicial = caminho_forward[0]
                df_arvore.loc[df_arvore["NO"] == elemento_inicial, "PROB"] = 1/aberturas[idx]
                vazao = df_cenarios.loc[(df_cenarios["NO"] == elemento_inicial)]["VAZAO"].iloc[0]
                df_cenarios.loc[df_cenarios["NO"] == elemento_inicial, "VAZAO"] = vazao - vazao/aberturas[idx]
                print(caminho_forward)
                
                df_arvore = pd.concat(lista_df_novo).reset_index(drop =True)
                df_cenarios = pd.concat(lista_df_vaz).reset_index(drop =True)
                print(df_arvore)
                print(df_cenarios)


df_arvore.to_csv(caminho_saida+"\\arvore.csv")
df_cenarios.to_csv(caminho_saida+"\\cenarios.csv")


printaArvore("arvore", df_arvore, df_cenarios)
printaArvore("arvore_orig", arvore, cenarios)

exit(1)