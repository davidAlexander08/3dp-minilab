import sys
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from anytree import Node, RenderTree
from clusterization.clusterization import reducaoArvoreClusterizacao
from backwardReduction.simultaneousBackwardReduction import backwardReduction


def printaArvore(texto, path_saida, df_arvore):
    df_arvore.loc[df_arvore["NO_PAI"] == 0, "NO_PAI"] = 1
    #df_arvore.loc[df_arvore["NO_PAI"] == 0, "NO_PAI"] = -1  # You can use any value that is not part of the graph
    G = nx.DiGraph()
    for _, row in df_arvore.iterrows():
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


def calculaMapaReducaoEstagio(mapa_aberturas_estagio, df_arvore):

    mapa_reducao_estagio = {}
    mapaCenariosRemanescentes = {}
    cenariosRemanescentesEstagio = 1
    for key in mapa_aberturas_estagio:
        cenariosRemanescentesEstagio = cenariosRemanescentesEstagio*mapa_aberturas_estagio[key]
    numeroTotalCenariosUltimoEstagio = len(df_arvore_original.loc[(df_arvore_original["PER"] == max(df_arvore_original["PER"].unique()))]["NO"].unique())
    mapa_reducao_estagio[int(max(df_arvore_original["PER"].unique()))] = numeroTotalCenariosUltimoEstagio - cenariosRemanescentesEstagio
    mapaCenariosRemanescentes[int(max(df_arvore_original["PER"].unique()))] = cenariosRemanescentesEstagio
    estagios = sorted(df_arvore_original["PER"].unique(), reverse=True)
    estagios = estagios[1:-1]
    for est in estagios:
        cenariosRemanescentesEstagio = cenariosRemanescentesEstagio/mapa_aberturas_estagio[est]
        mapaCenariosRemanescentes[int(est)] = cenariosRemanescentesEstagio
        mapa_reducao_estagio[int(est)] = mapaCenariosRemanescentes[int(est+1)] - cenariosRemanescentesEstagio
    return mapa_reducao_estagio


def getFilhos(no, df_arvore):
    filhos = df_arvore[df_arvore["NO_PAI"] == no]["NO"].values
    return filhos

def busca_pai(no, df_arvore):
    pai = df_arvore[df_arvore["NO"] == no]["NO_PAI"].values[0]
    return pai

def testeConsistenciaProbabilidadesFilhos(no, df_arvore, texto):
    filhos = getFilhos(no, df_arvore)
    prob = 0
    for filho in filhos:
        prob_filho = df_arvore.loc[(df_arvore["NO"] == filho)]["PROB"].iloc[0]
        prob += prob_filho
        
    assert prob >= 0.999, f"Distribuição das probabilidades dos filhos está errada para o teste {texto}, prob {prob}"
    assert prob <= 1.001, f"Distribuição das probabilidades dos filhos está errada para o teste {texto}, prob {prob}"

def retornaNosComFilhos(df_arvore):
    nos_com_filhos = []
    for no in df_arvore["NO"].unique():
        if(len(getFilhos(no, df_arvore)) != 0):
            nos_com_filhos.append(no)
    return nos_com_filhos


def realizaTesteConsistenciaProbabilidadesFilhos(df_arvore, texto):
    lista_nos_com_filhos = retornaNosComFilhos(df_arvore)
    for no in lista_nos_com_filhos:
        testeConsistenciaProbabilidadesFilhos(no, df_arvore, texto)
    print(f"Teste de Consistencia de Probabilidades Filhos - {texto} - OK")


def testeSimetriaFilhos(df_arvore, texto):
    periodos = df_arvore["PER"].unique()
    for per in periodos:
        nos_periodo = df_arvore.loc[(df_arvore["PER"] == per)]["NO"].unique()
        lista = []
        for no in nos_periodo:
            filhos = getFilhos(no, df_arvore)
            lista.append(len(filhos))
        assert all(x == lista[0] for x in lista), f"Numero de Aberturas Diferentes Para Nos do Estagio: {per}"
    print(f"Teste de Consistencia de Simetria da Árvore - {texto} - OK")

def testeCorrespondenciaArvoreVazoes(df_arvore, df_vazoes, texto):
    lista_nos = df_arvore["NO"].unique()
    for no in lista_nos:
        if not (df_vazoes["NO"] == no).any():
            raise AssertionError(f"NO {no} da árvore não encontrado em vazoes - {texto}!")
    print(f"Teste Correspondencia Arvore e Vazoes - {texto} - OK")

caso = "..\\..\\Dissertacao\\apresentacaoCarmen_Gevazp\\caso_mini\\exercicioGevazp\\4Estagios\\3Aberturas\\Pente"
caso = "..\\..\\Dissertacao\\apresentacaoCarmen_Gevazp\\caso_mini\\exercicioGevazp\\3Estagios\\2Aberturas\\Pente_GVZP"
caso = "..\\..\\Dissertacao\\apresentacaoCarmen_Gevazp\\caso_mini\\exercicioGevazp\\4Estagios\\2Aberturas\\Pente"
caso = "..\\..\\Dissertacao\\apresentacaoCarmen_Gevazp\\caso_mini\\exercicioGevazp\\4Estagios\\3Aberturas_Equiprovavel\\Pente_GVZP"
caso = "..\\Dissertacao\\apresentacaoCarmen_Gevazp\\caso_mini\\exercicioGevazp\\4Estagios\\3Aberturas\\Pente_GVZP"

mapa_aberturas_estagio = {1:3,    2:3,    3:3}
mapa_aberturas_estagio = {1:2,    2:2,    3:2}

##ARVORE CARMEN EXEMPLO
#mapa_reducao_estagio = {
#    2:6,
#    3:18,
#    4:0
#}


arquivo_vazoes = caso+"\\cenarios.csv"
df_vazoes_original = pd.read_csv(arquivo_vazoes)
df_vazoes_original.to_csv("saidas\\vazoes_estudo.csv", index=False)
arquivo_estrutura_feixes = caso+"\\arvore.csv"
df_arvore_original = pd.read_csv(arquivo_estrutura_feixes)
df_arvore_original.to_csv("saidas\\arvore_estudo.csv", index=False)
print(df_arvore_original)

mapa_reducao_estagio = calculaMapaReducaoEstagio(mapa_aberturas_estagio, df_arvore_original.copy())
print("mapa_aberturas_estagio: ", mapa_aberturas_estagio)
print("mapa_reducao_estagio: ", mapa_reducao_estagio)


###########Realizacao de testes unitários
texto = "Arvore Original"
realizaTesteConsistenciaProbabilidadesFilhos(df_arvore_original, texto)
testeSimetriaFilhos(df_arvore_original, texto)
testeCorrespondenciaArvoreVazoes(df_arvore_original, df_vazoes_original, texto)


print("###########################################################################")
### METODOS DE CLUSTERIZACAO ASSIMETRICO
Simetrica = False
df_arvore, df_vazoes = reducaoArvoreClusterizacao(mapa_aberturas_estagio, df_vazoes_original.copy(), df_arvore_original.copy(), Simetrica)
path_saida = "saidas\\ClusterAssimetrico"
df_arvore.to_csv(path_saida+"\\arvore.csv", index=False)
df_vazoes.to_csv(path_saida+"\\cenarios.csv", index=False)

texto = "Arvore Cluster Assimetrico"
realizaTesteConsistenciaProbabilidadesFilhos(df_arvore, texto)
testeCorrespondenciaArvoreVazoes(df_arvore, df_vazoes, texto)
printaArvore("ClusterAssimetrico", path_saida, df_arvore)



print("###########################################################################")
### METODO -  BACKWARD REDUCTION ASSIMETRICO
Simetrica = False
df_arvore, df_vazoes = backwardReduction(mapa_reducao_estagio, mapa_aberturas_estagio, df_vazoes_original.copy(), df_arvore_original.copy(), Simetrica)
path_saida = "saidas\\BKAssimetrico"
df_arvore.to_csv(path_saida+"\\arvore.csv", index=False)
df_vazoes.to_csv(path_saida+"\\cenarios.csv", index=False)


texto = "Arvore Backward Reduction Assimetrico"
realizaTesteConsistenciaProbabilidadesFilhos(df_arvore, texto)
testeCorrespondenciaArvoreVazoes(df_arvore, df_vazoes, texto)
printaArvore("BKAssimetrico", path_saida, df_arvore)



print("###########################################################################")
### METODO -  BACKWARD REDUCTION SIMETRICO
Simetrica = True
df_arvore, df_vazoes = backwardReduction(mapa_reducao_estagio, mapa_aberturas_estagio, df_vazoes_original, df_arvore_original, Simetrica)
path_saida = "saidas\\BKSimetrico"
df_arvore.to_csv(path_saida+"\\arvore.csv", index=False)
df_vazoes.to_csv(path_saida+"\\cenarios.csv", index=False)

texto = "Arvore Backward Reduction Simetrico"
realizaTesteConsistenciaProbabilidadesFilhos(df_arvore, texto)
testeSimetriaFilhos(df_arvore, texto)
testeCorrespondenciaArvoreVazoes(df_arvore, df_vazoes, texto)
printaArvore("BKSimetrico", path_saida, df_arvore)



print("###########################################################################")
## METODO CLUSTERIZACAO SIMETRICO
if(mapa_reducao_estagio[max(df_arvore_original["PER"].tolist())] != 0):
    print("Clusterizacao Simetrica Usual Pós Backward Reduction no Último Estágio")
    #print(mapa_reducao_estagio[max(df_arvore_original["PER"].tolist())])
    mapa_red_auxiliar = {}
    for est in df_arvore_original["PER"].tolist():
        mapa_red_auxiliar[est] = 0
    mapa_red_auxiliar[max(df_arvore_original["PER"].tolist())] =  mapa_reducao_estagio[max(df_arvore_original["PER"].tolist())]
    Simetrica = False
    df_arvore, df_vazoes = backwardReduction(mapa_red_auxiliar, mapa_aberturas_estagio, df_vazoes_original.copy(), df_arvore_original.copy(), Simetrica)

    Simetrica = True
    df_arvore, df_vazoes = reducaoArvoreClusterizacao(mapa_aberturas_estagio, df_vazoes_original.copy(), df_arvore.copy(), Simetrica)
    path_saida = "saidas\\ClusterSimetrico"
    df_arvore.to_csv(path_saida+"\\arvore.csv", index=False)
    df_vazoes.to_csv(path_saida+"\\cenarios.csv", index=False)
    
else:
    print("Clusterizacao Simetrica Usual")
    Simetrica = True
    df_arvore, df_vazoes = reducaoArvoreClusterizacao(mapa_aberturas_estagio, df_vazoes_original.copy(), df_arvore_original.copy(), Simetrica)
    path_saida = "saidas\\ClusterSimetrico"
    df_arvore.to_csv(path_saida+"\\arvore.csv", index=False)
    df_vazoes.to_csv(path_saida+"\\cenarios.csv", index=False)


texto = "Arvore Cluster Simetrico"
realizaTesteConsistenciaProbabilidadesFilhos(df_arvore, texto)
testeSimetriaFilhos(df_arvore, texto)
testeCorrespondenciaArvoreVazoes(df_arvore, df_vazoes, texto)
printaArvore("ClusterSimetrico", path_saida, df_arvore)