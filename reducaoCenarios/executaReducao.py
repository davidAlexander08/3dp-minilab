import sys
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from anytree import Node, RenderTree
from clusterization.clusterization import reducaoArvoreClusterizacao
from clusterization.reducaoPenteKmeans import reducaoArvoreClusterizacaoPente
from neuralGas.neuralGas import reducaoArvoreNeuralGas
from backwardReduction.simultaneousBackwardReduction import backwardReduction
import os

def printaArvore(texto, path_saida, df_arvore):
    estagios = df_arvore["PER"].unique()
    for est in estagios:
        total_nos_estagio = df_arvore.loc[df_arvore["PER"] == est]["NO"].unique()
        print("EST: ", est, " Total NOS: ", len(total_nos_estagio))
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


def calculaMapaReducaoEstagio(mapa_aberturas_estagio, df_arvore, perservaFolhas):

    mapa_reducao_estagio = {}
    mapaCenariosRemanescentes = {}
    cenariosRemanescentesEstagio = 1
    for key in mapa_aberturas_estagio:
        cenariosRemanescentesEstagio = cenariosRemanescentesEstagio*mapa_aberturas_estagio[key]
    numeroTotalCenariosUltimoEstagio = len(df_arvore.loc[(df_arvore["PER"] == max(df_arvore["PER"].unique()))]["NO"].unique())
    mapa_reducao_estagio[int(max(df_arvore["PER"].unique()))] = numeroTotalCenariosUltimoEstagio - cenariosRemanescentesEstagio
    mapaCenariosRemanescentes[int(max(df_arvore["PER"].unique()))] = cenariosRemanescentesEstagio
    estagios = sorted(df_arvore["PER"].unique(), reverse=True)
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
        
    assert prob >= 0.996, f"Distribuição das probabilidades dos filhos está errada para o teste {texto}, prob {prob}, filhos do no {no}"
    assert prob <= 1.004, f"Distribuição das probabilidades dos filhos está errada para o teste {texto}, prob {prob}, filhos do no {no}"

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

def testeEstruturaArvore(df_arvore_teste, df_arvore, texto):
    total_nos_arvore_teste = df_arvore_teste["NO"].unique()
    total_nos_arvore = df_arvore["NO"].unique()
    assert (len(total_nos_arvore_teste) == len(total_nos_arvore)), f"Numero de Nos Totais diferentes. - {texto}. NOrig {len(total_nos_arvore_teste)}. NRed {len(total_nos_arvore)}"
    for est in df_arvore_teste["PER"].unique():
        total_nos_arvore_teste_per = df_arvore_teste.loc[(df_arvore_teste["PER"] == est)]["NO"].unique()
        total_nos_arvore_per = df_arvore.loc[(df_arvore["PER"] == est)]["NO"].unique()
        assert (len(total_nos_arvore_teste_per) == len(total_nos_arvore_per)), f"Numero de Nos Totais diferentes no Estagio {est}. - {texto}"
        lista_prob_orig = []
        lista_prog_red = []
        for no_orig in total_nos_arvore_teste_per:
            prob_orig = df_arvore_teste.loc[(df_arvore_teste["NO"] == no_orig)]["PROB"].iloc[0]
            lista_prob_orig.append(prob_orig)
            encontrou_prob = 0
            for no_red in total_nos_arvore_per:
                prob_red = df_arvore.loc[(df_arvore["NO"] == no_red)]["PROB"].iloc[0]
                if(abs(prob_orig - prob_red) <= 0.0004):
                    encontrou_prob = 1
            assert (encontrou_prob == 1), f"Há probabilidades diferentes. No Original {no_orig} com probabilidade não encontrada. Estágio {est}. - {texto} - Diff - {prob_orig - prob_red} Arvore: {df_arvore.loc[df_arvore["PER"] == est]}"
        for no_red in total_nos_arvore_per:
            prob_red = df_arvore.loc[(df_arvore["NO"] == no_red)]["PROB"].iloc[0]
            lista_prog_red.append(prob_red)
        assert (abs(sum(lista_prob_orig) - sum(lista_prog_red)) <= 0.001), f"A soma das probabilidades está diferente no estágio {est}. - {texto} - {df_arvore.loc[df_arvore["PER"] == est]}"
    print(f"Teste de Estrutura da Árvore - {texto} - OK")

def testeEstruturaVazoes(df_vazoes_teste, df_vazoes, texto):
    total_nos_arvore_teste = df_vazoes_teste["NO"].unique()
    total_nos_arvore = df_vazoes["NO"].unique()
    assert (len(total_nos_arvore_teste) == len(total_nos_arvore)), f"Numero de Nos Totais diferentes nos arquivos de vazões - {texto}"
    lista_orig = []
    lista_red = []
    for no_orig in total_nos_arvore_teste:
        vazao_orig = df_vazoes_teste.loc[(df_vazoes_teste["NO"] == no_orig)]["VAZAO"].iloc[0]
        lista_orig.append(vazao_orig)
        encontrou_prob = 0
    for no_red in total_nos_arvore:
        vazao_red = df_vazoes.loc[(df_vazoes["NO"] == no_red)]["VAZAO"].iloc[0]
        lista_red.append(vazao_red)
    assert (abs(sum(lista_orig) - sum(lista_red))) <= 0.001, f"A soma das vazoes está diferente. - {texto} - Soma Orig: {sum(lista_orig)}, Soma Red: {sum(lista_red)}"
    print(f"Teste de Estrutura dos Cenários - {texto} - OK")


def testeReducaoArvoresGVZP(texto, df_arvore_pente_teste1, df_vazoes_pente_teste1 , df_arvore_arvore_teste1,  df_vazoes_arvore_teste1, mapa_aberturas_estagio, mapa_reducao_estagio ):
    Weighted = True
    perservaFolhas = False
    print("###########################################################################")
    Simetrica = False
    df_arvore, df_vazoes = reducaoArvoreClusterizacao(mapa_aberturas_estagio, df_vazoes_pente_teste1.copy(), df_arvore_pente_teste1.copy(), Simetrica, perservaFolhas, Weighted)
    #print(df_arvore)
    testeCorrespondenciaArvoreVazoes(df_arvore, df_vazoes,   texto+" Clusterizacao Assimetrica")
    realizaTesteConsistenciaProbabilidadesFilhos(df_arvore,  texto+" Clusterizacao Assimetrica")
    testeEstruturaArvore(df_arvore_arvore_teste1, df_arvore, texto+" Clusterizacao Assimetrica")
    testeEstruturaVazoes(df_vazoes_arvore_teste1, df_vazoes, texto+" Clusterizacao Assimetrica")
    print("###########################################################################")
    df_arvore, df_vazoes = backwardReduction(mapa_reducao_estagio, mapa_aberturas_estagio, df_vazoes_pente_teste1.copy(), df_arvore_pente_teste1.copy(), Simetrica, perservaFolhas)
    testeCorrespondenciaArvoreVazoes(df_arvore, df_vazoes,   texto+" Backward Reduction Assimetrica")
    realizaTesteConsistenciaProbabilidadesFilhos(df_arvore,  texto+" Backward Reduction Assimetrica")
    testeEstruturaArvore(df_arvore_arvore_teste1, df_arvore, texto+" Backward Reduction Assimetrica")
    testeEstruturaVazoes(df_vazoes_arvore_teste1, df_vazoes, texto+" Backward Reduction Assimetrica")
    #df_arvore.to_csv("casosTestesUnitarios/Export/arvore.csv")
    #df_vazoes.to_csv("casosTestesUnitarios/Export/cenarios.csv")
    #exit(1)

    print("###########################################################################")
    Simetrica = True
    df_arvore, df_vazoes = backwardReduction(mapa_reducao_estagio, mapa_aberturas_estagio, df_vazoes_pente_teste1.copy(), df_arvore_pente_teste1.copy(), Simetrica, perservaFolhas)
    testeCorrespondenciaArvoreVazoes(df_arvore, df_vazoes,   texto+" Backward Reduction Simetrica")
    realizaTesteConsistenciaProbabilidadesFilhos(df_arvore,  texto+" Backward Reduction Simetrica")
    testeEstruturaArvore(df_arvore_arvore_teste1, df_arvore, texto+" Backward Reduction Simetrica")
    testeEstruturaVazoes(df_vazoes_arvore_teste1, df_vazoes, texto+" Backward Reduction Simetrica")
    testeSimetriaFilhos(df_arvore, " Backward Reduction Simetrica")

    print("###########################################################################")
    ## METODO CLUSTERIZACAO SIMETRICO
    if(mapa_reducao_estagio[max(df_arvore_pente_teste1["PER"].tolist())] != 0):
        print("Clusterizacao Simetrica Usual Pós Backward Reduction no Último Estágio")
        #print(mapa_reducao_estagio[max(df_arvore_original["PER"].tolist())])
        mapa_red_auxiliar = {}
        for est in df_arvore_pente_teste1["PER"].tolist():
            mapa_red_auxiliar[est] = 0
        mapa_red_auxiliar[max(df_arvore_pente_teste1["PER"].tolist())] =  mapa_reducao_estagio[max(df_arvore_pente_teste1["PER"].tolist())]
        Simetrica = False
        df_arvore_BK, df_vazoes_BK = backwardReduction(mapa_red_auxiliar, mapa_aberturas_estagio, df_vazoes_pente_teste1.copy(), df_arvore_pente_teste1.copy(), Simetrica, perservaFolhas, Weighted)
        Simetrica = True
        df_arvore, df_vazoes = reducaoArvoreClusterizacao(mapa_aberturas_estagio, df_vazoes_BK.copy(), df_arvore_BK.copy(), Simetrica)
    else:
        print("Clusterizacao Simetrica Usual")
        Simetrica = True
        df_arvore, df_vazoes = reducaoArvoreClusterizacao(mapa_aberturas_estagio, df_vazoes_pente_teste1.copy(), df_arvore_pente_teste1.copy(), Simetrica, perservaFolhas, Weighted)
    testeCorrespondenciaArvoreVazoes(df_arvore, df_vazoes,   texto+" Clustering Simetrica")
    realizaTesteConsistenciaProbabilidadesFilhos(df_arvore,  texto+" Clustering Simetrica")
    testeEstruturaArvore(df_arvore_arvore_teste1, df_arvore, texto+" Clustering Simetrica")
    testeEstruturaVazoes(df_vazoes_arvore_teste1, df_vazoes, texto+" Clustering Simetrica")
    testeSimetriaFilhos(df_arvore, " Clustering Simetrica")
    print("###########################################################################")



    print("###########################################################################")
    ### METODO NEURAL GAS
    Simetrica = False
    df_arvore, df_vazoes = reducaoArvoreNeuralGas(mapa_aberturas_estagio, df_vazoes_pente_teste1.copy(), df_arvore_pente_teste1.copy(), Simetrica, perservaFolhas)
    #print(df_arvore)
    testeCorrespondenciaArvoreVazoes(df_arvore, df_vazoes,   texto+" Neural Gas Assimetrica")
    realizaTesteConsistenciaProbabilidadesFilhos(df_arvore,  texto+" Neural Gas Assimetrica")
    testeEstruturaArvore(df_arvore_arvore_teste1, df_arvore, texto+" Neural Gas Assimetrica")
    testeEstruturaVazoes(df_vazoes_arvore_teste1, df_vazoes, texto+" Neural Gas Assimetrica")



    #print("###########################################################################")
    #### METODO NEURAL GAS
    #Simetrica = True
    #df_arvore, df_vazoes = reducaoArvoreNeuralGas(mapa_aberturas_estagio, df_vazoes_pente_teste1.copy(), df_arvore_pente_teste1.copy(), Simetrica)
    ##print(df_arvore)
    #testeCorrespondenciaArvoreVazoes(df_arvore, df_vazoes,   texto+" Neural Gas Simetrica")
    #realizaTesteConsistenciaProbabilidadesFilhos(df_arvore,  texto+" Neural Gas Simetrica")
    #testeEstruturaArvore(df_arvore_arvore_teste1, df_arvore, texto+" Neural Gas Simetrica")
    #testeEstruturaVazoes(df_vazoes_arvore_teste1, df_vazoes, texto+" Neural Gas Simetrica")



def executaTestesReducaoArvoresGVZP():

    perservaFolhas = False

    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    texto = "Teste 1D 6A 2A, 3 EQUIPROVAVEL Est GVZP"
    print(texto)
    caso_teste1 = "casosTestesUnitarios\\1D\\3Estagios\\6Aberturas"
    df_vazoes_pente_teste1 = pd.read_csv(caso_teste1+"\\Pente_GVZP\\cenarios.csv")
    df_arvore_pente_teste1 = pd.read_csv(caso_teste1+"\\Pente_GVZP\\arvore.csv")
    df_vazoes_arvore_teste1 = pd.read_csv(caso_teste1+"\\Arvore_GVZP\\cenarios.csv")
    df_arvore_arvore_teste1 = pd.read_csv(caso_teste1+"\\Arvore_GVZP\\arvore.csv")
    mapa_aberturas_estagio = {1:6,    2:2}
    mapa_reducao_estagio = calculaMapaReducaoEstagio(mapa_aberturas_estagio, df_arvore_pente_teste1.copy(), perservaFolhas)
    testeReducaoArvoresGVZP(texto, df_arvore_pente_teste1, df_vazoes_pente_teste1 , df_arvore_arvore_teste1,  df_vazoes_arvore_teste1, mapa_aberturas_estagio, mapa_reducao_estagio )
    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    #exit(1)

    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    texto = "Teste 1D 6A 2A, 3 ASSIMETRICO Est GVZP"
    print(texto)
    caso_teste1 = "casosTestesUnitarios\\1D\\3Estagios\\6Aberturas_Assim"
    df_vazoes_pente_teste1 = pd.read_csv(caso_teste1+"\\Pente_GVZP\\cenarios.csv")
    df_arvore_pente_teste1 = pd.read_csv(caso_teste1+"\\Pente_GVZP\\arvore.csv")
    df_vazoes_arvore_teste1 = pd.read_csv(caso_teste1+"\\Arvore_GVZP\\cenarios.csv")
    df_arvore_arvore_teste1 = pd.read_csv(caso_teste1+"\\Arvore_GVZP\\arvore.csv")
    mapa_aberturas_estagio = {1:6,    2:2}
    mapa_reducao_estagio = calculaMapaReducaoEstagio(mapa_aberturas_estagio, df_arvore_pente_teste1.copy(), perservaFolhas)
    testeReducaoArvoresGVZP(texto, df_arvore_pente_teste1, df_vazoes_pente_teste1 , df_arvore_arvore_teste1,  df_vazoes_arvore_teste1, mapa_aberturas_estagio, mapa_reducao_estagio )
    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")


    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    texto = "Teste 2 A, 3 Est Simetrica GVZP"
    print(texto)
    caso_teste1 = "casosTestesUnitarios\\1D\\3Estagios\\2Aberturas"
    df_vazoes_pente_teste1 = pd.read_csv(caso_teste1+"\\Pente_GVZP\\cenarios.csv")
    df_arvore_pente_teste1 = pd.read_csv(caso_teste1+"\\Pente_GVZP\\arvore.csv")
    df_vazoes_arvore_teste1 = pd.read_csv(caso_teste1+"\\Arvore_GVZP\\cenarios.csv")
    df_arvore_arvore_teste1 = pd.read_csv(caso_teste1+"\\Arvore_GVZP\\arvore.csv")
    mapa_aberturas_estagio = {1:2,    2:2}
    mapa_reducao_estagio = calculaMapaReducaoEstagio(mapa_aberturas_estagio, df_arvore_pente_teste1.copy(), perservaFolhas)
    testeReducaoArvoresGVZP(texto, df_arvore_pente_teste1, df_vazoes_pente_teste1 , df_arvore_arvore_teste1,  df_vazoes_arvore_teste1, mapa_aberturas_estagio, mapa_reducao_estagio )
    
    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    texto = "Teste 2 A, 3 Est Assimetrica GVZP"
    print(texto)
    caso_teste1 = "casosTestesUnitarios\\1D\\3Estagios\\2Aberturas_Assim"
    df_vazoes_pente_teste1 = pd.read_csv(caso_teste1+"\\Pente_GVZP\\cenarios.csv")
    df_arvore_pente_teste1 = pd.read_csv(caso_teste1+"\\Pente_GVZP\\arvore.csv")
    df_vazoes_arvore_teste1 = pd.read_csv(caso_teste1+"\\Arvore_GVZP\\cenarios.csv")
    df_arvore_arvore_teste1 = pd.read_csv(caso_teste1+"\\Arvore_GVZP\\arvore.csv")
    mapa_aberturas_estagio = {1:2,    2:2}
    mapa_reducao_estagio = calculaMapaReducaoEstagio(mapa_aberturas_estagio, df_arvore_pente_teste1.copy(), perservaFolhas)
    testeReducaoArvoresGVZP(texto, df_arvore_pente_teste1, df_vazoes_pente_teste1 , df_arvore_arvore_teste1,  df_vazoes_arvore_teste1, mapa_aberturas_estagio, mapa_reducao_estagio )
    
    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    texto = "Teste 3 A, 3 Est Assimetrica GVZP"
    print(texto)
    caso_teste1 = "casosTestesUnitarios\\1D\\3Estagios\\3AberturasAssim"
    df_vazoes_pente_teste1 = pd.read_csv(caso_teste1+"\\Pente_GVZP\\cenarios.csv")
    df_arvore_pente_teste1 = pd.read_csv(caso_teste1+"\\Pente_GVZP\\arvore.csv")
    df_vazoes_arvore_teste1 = pd.read_csv(caso_teste1+"\\Arvore_GVZP\\cenarios.csv")
    df_arvore_arvore_teste1 = pd.read_csv(caso_teste1+"\\Arvore_GVZP\\arvore.csv")
    mapa_aberturas_estagio = {1:3,    2:3}
    mapa_reducao_estagio = calculaMapaReducaoEstagio(mapa_aberturas_estagio, df_arvore_pente_teste1.copy(), perservaFolhas)
    testeReducaoArvoresGVZP(texto, df_arvore_pente_teste1, df_vazoes_pente_teste1 , df_arvore_arvore_teste1,  df_vazoes_arvore_teste1, mapa_aberturas_estagio, mapa_reducao_estagio )

    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    texto = "Teste 2 A, 4 Est Simetrica GVZP"
    print(texto)
    caso_teste1 = "casosTestesUnitarios\\1D\\4Estagios\\2Aberturas"
    df_vazoes_pente_teste1 = pd.read_csv(caso_teste1+"\\Pente_GVZP\\cenarios.csv")
    df_arvore_pente_teste1 = pd.read_csv(caso_teste1+"\\Pente_GVZP\\arvore.csv")
    df_vazoes_arvore_teste1 = pd.read_csv(caso_teste1+"\\Arvore_GVZP\\cenarios.csv")
    df_arvore_arvore_teste1 = pd.read_csv(caso_teste1+"\\Arvore_GVZP\\arvore.csv")
    mapa_aberturas_estagio = {1:2,    2:2, 3:2}
    mapa_reducao_estagio = calculaMapaReducaoEstagio(mapa_aberturas_estagio, df_arvore_pente_teste1.copy(), perservaFolhas)
    testeReducaoArvoresGVZP(texto, df_arvore_pente_teste1, df_vazoes_pente_teste1 , df_arvore_arvore_teste1,  df_vazoes_arvore_teste1, mapa_aberturas_estagio, mapa_reducao_estagio )
    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")

    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    texto = "Teste 2 A, 4 Est Assimetrica GVZP"
    print(texto)
    caso_teste1 = "casosTestesUnitarios\\1D\\4Estagios\\2Aberturas_Assim"
    df_vazoes_pente_teste1 = pd.read_csv(caso_teste1+"\\Pente_GVZP\\cenarios.csv")
    df_arvore_pente_teste1 = pd.read_csv(caso_teste1+"\\Pente_GVZP\\arvore.csv")
    df_vazoes_arvore_teste1 = pd.read_csv(caso_teste1+"\\Arvore_GVZP\\cenarios.csv")
    df_arvore_arvore_teste1 = pd.read_csv(caso_teste1+"\\Arvore_GVZP\\arvore.csv")
    mapa_aberturas_estagio = {1:2,    2:2, 3:2}
    mapa_reducao_estagio = calculaMapaReducaoEstagio(mapa_aberturas_estagio, df_arvore_pente_teste1.copy(), perservaFolhas)
    testeReducaoArvoresGVZP(texto, df_arvore_pente_teste1, df_vazoes_pente_teste1 , df_arvore_arvore_teste1,  df_vazoes_arvore_teste1, mapa_aberturas_estagio, mapa_reducao_estagio )
    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")


    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    texto = "Teste 3 A, 4 Est Simetrica GVZP"
    print(texto)
    caso_teste1 = "casosTestesUnitarios\\1D\\4Estagios\\3Aberturas_Equiprovavel"
    df_vazoes_pente_teste1 = pd.read_csv(caso_teste1+"\\Pente_GVZP\\cenarios.csv")
    df_arvore_pente_teste1 = pd.read_csv(caso_teste1+"\\Pente_GVZP\\arvore.csv")
    df_vazoes_arvore_teste1 = pd.read_csv(caso_teste1+"\\Arvore_GVZP\\cenarios.csv")
    df_arvore_arvore_teste1 = pd.read_csv(caso_teste1+"\\Arvore_GVZP\\arvore.csv")
    mapa_aberturas_estagio = {1:3,    2:3, 3:3}
    mapa_reducao_estagio = calculaMapaReducaoEstagio(mapa_aberturas_estagio, df_arvore_pente_teste1.copy(), perservaFolhas)
    testeReducaoArvoresGVZP(texto, df_arvore_pente_teste1, df_vazoes_pente_teste1 , df_arvore_arvore_teste1,  df_vazoes_arvore_teste1, mapa_aberturas_estagio, mapa_reducao_estagio )
    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")


    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    texto = "Teste 3 A, 4 Est Assimetrica GVZP"
    print(texto)
    caso_teste1 = "casosTestesUnitarios\\1D\\4Estagios\\3Aberturas"
    df_vazoes_pente_teste1 = pd.read_csv(caso_teste1+"\\Pente_GVZP\\cenarios.csv")
    df_arvore_pente_teste1 = pd.read_csv(caso_teste1+"\\Pente_GVZP\\arvore.csv")
    df_vazoes_arvore_teste1 = pd.read_csv(caso_teste1+"\\Arvore_GVZP\\cenarios.csv")
    df_arvore_arvore_teste1 = pd.read_csv(caso_teste1+"\\Arvore_GVZP\\arvore.csv")
    mapa_aberturas_estagio = {1:3,    2:3, 3:3}
    mapa_reducao_estagio = calculaMapaReducaoEstagio(mapa_aberturas_estagio, df_arvore_pente_teste1.copy(), perservaFolhas)
    testeReducaoArvoresGVZP(texto, df_arvore_pente_teste1, df_vazoes_pente_teste1 , df_arvore_arvore_teste1,  df_vazoes_arvore_teste1, mapa_aberturas_estagio, mapa_reducao_estagio )
    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")


###########################################################
    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    texto = "Teste 2D 3 A, 4 Est GVZP"
    print(texto)
    caso_teste1 = "casosTestesUnitarios\\2D\\4Estagios\\3Aberturas"
    df_vazoes_pente_teste1 = pd.read_csv(caso_teste1+"\\Pente_GVZP\\cenarios.csv")
    df_arvore_pente_teste1 = pd.read_csv(caso_teste1+"\\Pente_GVZP\\arvore.csv")
    df_vazoes_arvore_teste1 = pd.read_csv(caso_teste1+"\\Arvore_GVZP\\cenarios.csv")
    df_arvore_arvore_teste1 = pd.read_csv(caso_teste1+"\\Arvore_GVZP\\arvore.csv")
    mapa_aberturas_estagio = {1:3,    2:3, 3:3}
    mapa_reducao_estagio = calculaMapaReducaoEstagio(mapa_aberturas_estagio, df_arvore_pente_teste1.copy(), perservaFolhas)
    testeReducaoArvoresGVZP(texto, df_arvore_pente_teste1, df_vazoes_pente_teste1 , df_arvore_arvore_teste1,  df_vazoes_arvore_teste1, mapa_aberturas_estagio, mapa_reducao_estagio )
    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")

###########################################################
    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    texto = "Teste 4D 3 A, 4 Est GVZP"
    print(texto)
    caso_teste1 = "casosTestesUnitarios\\4D\\4Estagios\\3Aberturas"
    df_vazoes_pente_teste1 = pd.read_csv(caso_teste1+"\\Pente_GVZP\\cenarios.csv")
    df_arvore_pente_teste1 = pd.read_csv(caso_teste1+"\\Pente_GVZP\\arvore.csv")
    df_vazoes_arvore_teste1 = pd.read_csv(caso_teste1+"\\Arvore_GVZP\\cenarios.csv")
    df_arvore_arvore_teste1 = pd.read_csv(caso_teste1+"\\Arvore_GVZP\\arvore.csv")
    mapa_aberturas_estagio = {1:3,    2:3, 3:3}
    mapa_reducao_estagio = calculaMapaReducaoEstagio(mapa_aberturas_estagio, df_arvore_pente_teste1.copy(), perservaFolhas)
    testeReducaoArvoresGVZP(texto, df_arvore_pente_teste1, df_vazoes_pente_teste1 , df_arvore_arvore_teste1,  df_vazoes_arvore_teste1, mapa_aberturas_estagio, mapa_reducao_estagio )
    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")

###########################################################
    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    texto = "Teste 5D 3 A, 4 Est GVZP"
    print(texto)
    caso_teste1 = "casosTestesUnitarios\\5D\\4Estagios\\3Aberturas"
    df_vazoes_pente_teste1 = pd.read_csv(caso_teste1+"\\Pente_GVZP\\cenarios.csv")
    df_arvore_pente_teste1 = pd.read_csv(caso_teste1+"\\Pente_GVZP\\arvore.csv")
    df_vazoes_arvore_teste1 = pd.read_csv(caso_teste1+"\\Arvore_GVZP\\cenarios.csv")
    df_arvore_arvore_teste1 = pd.read_csv(caso_teste1+"\\Arvore_GVZP\\arvore.csv")
    mapa_aberturas_estagio = {1:3,    2:3, 3:3}
    mapa_reducao_estagio = calculaMapaReducaoEstagio(mapa_aberturas_estagio, df_arvore_pente_teste1.copy(), perservaFolhas)
    testeReducaoArvoresGVZP(texto, df_arvore_pente_teste1, df_vazoes_pente_teste1 , df_arvore_arvore_teste1,  df_vazoes_arvore_teste1, mapa_aberturas_estagio, mapa_reducao_estagio )
    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")



###########################################################
    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    texto = "Teste 3D 2 A, 3 Est GVZP"
    print(texto)
    caso_teste1 = "casosTestesUnitarios\\3D\\3Estagios\\2Aberturas"
    df_vazoes_pente_teste1 = pd.read_csv(caso_teste1+"\\Pente_GVZP\\cenarios.csv")
    df_arvore_pente_teste1 = pd.read_csv(caso_teste1+"\\Pente_GVZP\\arvore.csv")
    df_vazoes_arvore_teste1 = pd.read_csv(caso_teste1+"\\Arvore_GVZP\\cenarios.csv")
    df_arvore_arvore_teste1 = pd.read_csv(caso_teste1+"\\Arvore_GVZP\\arvore.csv")
    mapa_aberturas_estagio = {1:2,    2:2}
    mapa_reducao_estagio = calculaMapaReducaoEstagio(mapa_aberturas_estagio, df_arvore_pente_teste1.copy(), perservaFolhas)
    testeReducaoArvoresGVZP(texto, df_arvore_pente_teste1, df_vazoes_pente_teste1 , df_arvore_arvore_teste1,  df_vazoes_arvore_teste1, mapa_aberturas_estagio, mapa_reducao_estagio )
    
    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    texto = "Teste 3D 3 A, 3 Est GVZP"
    print(texto)
    caso_teste1 = "casosTestesUnitarios\\3D\\3Estagios\\3Aberturas"
    df_vazoes_pente_teste1 = pd.read_csv(caso_teste1+"\\Pente_GVZP\\cenarios.csv")
    df_arvore_pente_teste1 = pd.read_csv(caso_teste1+"\\Pente_GVZP\\arvore.csv")
    df_vazoes_arvore_teste1 = pd.read_csv(caso_teste1+"\\Arvore_GVZP\\cenarios.csv")
    df_arvore_arvore_teste1 = pd.read_csv(caso_teste1+"\\Arvore_GVZP\\arvore.csv")
    mapa_aberturas_estagio = {1:3,    2:3}
    mapa_reducao_estagio = calculaMapaReducaoEstagio(mapa_aberturas_estagio, df_arvore_pente_teste1.copy(), perservaFolhas)
    testeReducaoArvoresGVZP(texto, df_arvore_pente_teste1, df_vazoes_pente_teste1 , df_arvore_arvore_teste1,  df_vazoes_arvore_teste1, mapa_aberturas_estagio, mapa_reducao_estagio )

    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    texto = "Teste 3D 2 A, 4 Est GVZP"
    print(texto)
    caso_teste1 = "casosTestesUnitarios\\3D\\4Estagios\\2Aberturas"
    df_vazoes_pente_teste1 = pd.read_csv(caso_teste1+"\\Pente_GVZP\\cenarios.csv")
    df_arvore_pente_teste1 = pd.read_csv(caso_teste1+"\\Pente_GVZP\\arvore.csv")
    df_vazoes_arvore_teste1 = pd.read_csv(caso_teste1+"\\Arvore_GVZP\\cenarios.csv")
    df_arvore_arvore_teste1 = pd.read_csv(caso_teste1+"\\Arvore_GVZP\\arvore.csv")
    mapa_aberturas_estagio = {1:2,    2:2, 3:2}
    mapa_reducao_estagio = calculaMapaReducaoEstagio(mapa_aberturas_estagio, df_arvore_pente_teste1.copy(), perservaFolhas)
    testeReducaoArvoresGVZP(texto, df_arvore_pente_teste1, df_vazoes_pente_teste1 , df_arvore_arvore_teste1,  df_vazoes_arvore_teste1, mapa_aberturas_estagio, mapa_reducao_estagio )
    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")

    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    texto = "Teste 3D 3 A, 4 Est GVZP"
    print(texto)
    caso_teste1 = "casosTestesUnitarios\\3D\\4Estagios\\3Aberturas"
    df_vazoes_pente_teste1 = pd.read_csv(caso_teste1+"\\Pente_GVZP\\cenarios.csv")
    df_arvore_pente_teste1 = pd.read_csv(caso_teste1+"\\Pente_GVZP\\arvore.csv")
    df_vazoes_arvore_teste1 = pd.read_csv(caso_teste1+"\\Arvore_GVZP\\cenarios.csv")
    df_arvore_arvore_teste1 = pd.read_csv(caso_teste1+"\\Arvore_GVZP\\arvore.csv")
    mapa_aberturas_estagio = {1:3,    2:3, 3:3}
    mapa_reducao_estagio = calculaMapaReducaoEstagio(mapa_aberturas_estagio, df_arvore_pente_teste1.copy(), perservaFolhas)
    testeReducaoArvoresGVZP(texto, df_arvore_pente_teste1, df_vazoes_pente_teste1 , df_arvore_arvore_teste1,  df_vazoes_arvore_teste1, mapa_aberturas_estagio, mapa_reducao_estagio )
    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")







#executaTestesReducaoArvoresGVZP()
#exit(1)


caso = "..\\Capitulo_5\\caso_mini_500Cen_sorteio_mensais"
caso = r"C:\Users\testa\Documents\git\3dp-minilab\Dissertacao\apresentacaoCarmen_Gevazp_V2\caso_mini\exercicioGevazp\TesteCarmen\Pente_GVZP_6A_Eq"
caso = r"C:\Users\testa\Documents\git\3dp-minilab\Carmen\exercicio_27cen_1D\1D_3Aberturas_Equiprovavel\Pente_GVZP"
#caso = r"C:\Users\testa\Documents\git\3dp-minilab\Carmen\exercicio_27cen_2D\2D_3Aberturas_Equiprovavel\Pente_GVZP"
caso = r"C:\Users\testa\Documents\git\3dp-minilab\Carmen\exercicio_27cen_3D\3Aberturas_Equiprovavel\Pente_GVZP"
#caso = r"C:\Users\testa\Documents\git\3dp-minilab\Carmen\exercicio_27cen_4D_Teste\4D_3Aberturas_Equiprovavel\Pente_GVZP"
#caso = r"C:\Users\testa\Documents\git\3dp-minilab\Carmen\exercicio_27cen_5D\5D_3Aberturas_Equiprovavel\Pente_GVZP"
caso = "..\\Capitulo_5\\caso_mini_500Cen_cluster_semanais"
caso = "..\\Carmen\\exercicio_27cen_5D\\27_Aberturas_Equiprovavel\\Pente_GVZP"
caso = "..\\Carmen\\exercicio_27cen_5D\\27_Aberturas_Equiprovavel\\Pente_GVZP"
caso = "..\\Carmen\\exercicio_27cen_4D_Teste\\27_Aberturas_Equiprovavel\\Pente_GVZP"
caso = "..\\Carmen\\exercicio_27cen_3D\\27_Aberturas_Equiprovavel\\Pente_GVZP"
caso = "..\\Carmen\\exercicio_27cen_1D\\27_Aberturas_Equiprovavel\\Pente_GVZP"
caso = "..\\Carmen\\exercicio_27cen_10D\\27_Aberturas_Equiprovavel\\Pente_GVZP"
caso = "..\\Carmen\\exercicio_27cen_20D\\27_Aberturas_Equiprovavel\\Pente_GVZP"
#caso = r"C:\Users\testa\Documents\git\3dp-minilab\Carmen\exercicio_27cen_5D\5D_3Aberturas_Equiprovavel\Pente_GVZP"
#caso = "..\\Dissertacao\\apresentacaoCarmen_Gevazp\\caso_mini\\exercicioGevazp\\3Estagios\\3AberturasAssim\\Pente_GVZP"
#caso = "..\\Dissertacao\\apresentacaoCarmen_Gevazp\\caso_mini\\exercicioGevazp\\4Estagios\\3Aberturas_teste\\Pente_GVZP"
caso = "..\\Capitulo_5\\caso_mini_500Cen_cluster_semanais\\avaliaArvoresRepresentativo\\Pente"

#mapa_aberturas_estagio = {1:3,    2:3,    3:3}
mapa_aberturas_estagio = {1:4,    2:5,    3:15}
mapa_aberturas_estagio = {1:25,    2:4,    3:3}
mapa_aberturas_estagio = {1:15,    2:4,    3:5}
mapa_aberturas_estagio = {1:10,    2:10,    3:3}


mapa_aberturas_estagio = {1:8,    2:1,    3:1}
mapa_aberturas_estagio_pente = {1:8, 2:1, 3:1}

caminho_saida = "..\\Carmen\\exercicio_27cen_5D\\64_Aberturas_Equiprovavel\\8Folhas\\A_8x1x1"



caso = "..\\Carmen\\exercicio_27cen_20D\\128_Aberturas_Equiprovavel_Pfundo\\Pente_GVZP"
reducoes = [
    ({1:2, 2:2, 3:8}, 32, "revisaoDebora\\A_2x2x8"),
    ({1:4, 2:4, 3:2}, 32, "revisaoDebora\\A_4x4x2"),
    ({1:8, 2:2, 3:2}, 32, "revisaoDebora\\A_8x2x2"),
    ({1:32, 2:1, 3:1}, 32, "revisaoDebora\\A_32x1x1"),
    ({1:4, 2:6, 3:3}, 72, "revisaoDebora\\A_4x6x3"),
]


caso = "..\\Capitulo_5\\caso_mini_500Cen_cluster_semanais\\avaliaArvoresRepresentativo\\Pente"
reducoes = [
    #({1:25, 2:4, 3:2}, 200, "revisaoDebora\\A_25x4x2_13_96"),
    #({1:1, 2:1, 3:1}, 1, "revisaoDebora\\Detrm"),
    ({1:25, 2:3, 3:2}, 150, "exercicio_27cen_20D\\A_25x3x2"),
    #({1:50, 2:2, 3:2}, 200, "revisaoDebora\\A_50x2x2_S39_255"),
    #({1:100, 2:1, 3:1}, 100, "revisaoDebora\\A_100x1x1_254_20"),
    #({1:100, 2:2, 3:1}, 200, "revisaoDebora\\A_100x2x1"),
    #({1:60, 2:3, 3:2}, 360, "revisaoDebora\\A_60x3x2"),
    #({1:1, 2:1, 3:300}, 300, "revisaoDebora\\Vassoura"),
]

#caminho_base = "..\\Carmen\\exercicio_27cen_10D\\27_Aberturas_Equiprovavel_2\\"

reducoes = [
    ({1:2, 2:2, 3:2}, 8, "A_2x2x2"),
    ({1:4, 2:2, 3:1}, 8, "A_4x2x1"),
    ({1:8, 2:1, 3:1}, 8, "A_8x1x1"),
    ({1:2, 2:3, 3:4}, 24, "A_2x3x4"),
]

caso = "Pente_GVZP"
caminho_base = "..\\Carmen\\exercicio_27cen_5D\\128_Aberturas_Equiprovavel_13052025\\"
reducoes = [
    ({1:2, 2:2, 3:8}, 32, "A_2x2x8"),
    ({1:4, 2:4, 3:2}, 32, "A_4x4x2"),
    ({1:8, 2:2, 3:2}, 32, "A_8x2x2"),
    ({1:32, 2:1, 3:1}, 32, "A_32x1x1"),
    ({1:4, 2:6, 3:3}, 72, "A_4x6x3"),
]


for red in reducoes:
    mapa_aberturas_estagio = red[0]
    mapa_aberturas_estagio_pente = {1:red[1], 2:1, 3:1}
    #caminho_saida = "..\\Carmen\\exercicio_27cen_5D\\128_Aberturas_Equiprovavel_Pfundo\\"+red[2]
    caminho_saida = caminho_base+red[2]

    arquivo_vazoes = caminho_base+caso+"\\cenarios.csv"
    #arquivo_vazoes = caso+"\\cenarios_teste.csv"
    df_vazoes_original = pd.read_csv(arquivo_vazoes)
    df_vazoes_original.to_csv("saidas\\vazoes_estudo.csv", index=False)
    arquivo_estrutura_feixes = caminho_base+caso+"\\arvore.csv"
    #arquivo_estrutura_feixes = caso+"\\arvore_teste.csv"
    df_arvore_original = pd.read_csv(arquivo_estrutura_feixes)
    df_arvore_original.to_csv("saidas\\arvore_estudo.csv", index=False)


    #####################PARAMETROS
    Plota = False
    perservaFolhas = False
    #################################
    print(df_arvore_original)
    print("TOTAL POSTOS: ", len(df_vazoes_original["NOME_UHE"].unique()))
    mapa_reducao_estagio = calculaMapaReducaoEstagio(mapa_aberturas_estagio, df_arvore_original.copy(), perservaFolhas)
    print("mapa_aberturas_estagio: ", mapa_aberturas_estagio)
    print("mapa_reducao_estagio: ", mapa_reducao_estagio)


    ###########Realizacao de testes unitários
    texto = "Arvore Original"
    realizaTesteConsistenciaProbabilidadesFilhos(df_arvore_original, texto)
    testeSimetriaFilhos(df_arvore_original, texto)
    testeCorrespondenciaArvoreVazoes(df_arvore_original, df_vazoes_original, texto)
    #printaArvore("Arvore Original", "saidas\\",df_arvore_original)


    if(red[1] != 0):
        ###            #SIMETR, WEIGHT, QUAD, PACOTE
        binarios_pente =  [False, False, False, False]
        df_arvore, df_vazoes = reducaoArvoreClusterizacaoPente(mapa_aberturas_estagio_pente, df_vazoes_original.copy(), df_arvore_original.copy(), 
            binarios_pente[0], perservaFolhas, binarios_pente[1], binarios_pente[3], binarios_pente[2], Plota)
        path_saida = caminho_saida+"\\KMeansPente"
        os.makedirs(path_saida, exist_ok=True)
        df_arvore.to_csv(path_saida+"\\arvore.csv", index=False)
        df_vazoes.to_csv(path_saida+"\\cenarios.csv", index=False)
    
    #exit(1)
    #texto = "Arvore "+"KMeansPente"
    #realizaTesteConsistenciaProbabilidadesFilhos(df_arvore, texto)
    #testeCorrespondenciaArvoreVazoes(df_arvore, df_vazoes, texto)
    #printaArvore("KMeansPente", path_saida, df_arvore)
#
#
    ######################################### COMPARACAO METODOS 
    print("###########################################################################")
    ### METODO -  BACKWARD REDUCTION ASSIMETRICO
    Simetrica = False
    df_arvore, df_vazoes = backwardReduction(mapa_reducao_estagio, mapa_aberturas_estagio, df_vazoes_original.copy(), df_arvore_original.copy(), Simetrica, perservaFolhas, Plota)
    path_saida = "saidas\\BKAssimetrico"
    path_saida = caminho_saida+"\\BKAssimetrico"
    os.makedirs(path_saida, exist_ok=True)
    df_arvore.to_csv(path_saida+"\\arvore.csv", index=False)
    df_vazoes.to_csv(path_saida+"\\cenarios.csv", index=False)
##
    #texto = "Arvore Backward Reduction Assimetrico"
    #realizaTesteConsistenciaProbabilidadesFilhos(df_arvore, texto)
    #testeCorrespondenciaArvoreVazoes(df_arvore, df_vazoes, texto)
    #printaArvore("BKAssimetrico", path_saida, df_arvore)
    #exit(1)


    #print("###########################################################################")
    #### METODO -  BACKWARD REDUCTION SIMETRICO
    #Simetrica = True
    #df_arvore, df_vazoes = backwardReduction(mapa_reducao_estagio, mapa_aberturas_estagio, df_vazoes_original.copy(), df_arvore_original.copy(), Simetrica, Plota)
    #path_saida = "saidas\\BKSimetrico"
    #path_saida = caminho_saida+"\\BKSimetrico"
    #os.makedirs(path_saida, exist_ok=True)
    #df_arvore.to_csv(path_saida+"\\arvore.csv", index=False)
    #df_vazoes.to_csv(path_saida+"\\cenarios.csv", index=False)
    #
    #texto = "Arvore Backward Reduction Simetrico"
    #realizaTesteConsistenciaProbabilidadesFilhos(df_arvore, texto)
    #testeSimetriaFilhos(df_arvore, texto)
    #testeCorrespondenciaArvoreVazoes(df_arvore, df_vazoes, texto)
    #printaArvore("BKSimetrico", path_saida, df_arvore)


    perservaFolhas = True

    #####################PARAMETROS PARA CLUSTERIZACAO
    DicionarioListaKmeans = {          #SIMETR, WEIGHT, QUAD, PACOTE
    #    "KMeansAssimetricoLinear":      [False, False, False, False],
    #    "KMeansAssimetricoLinearQuad":  [False, False, True , False],
    #    "KMeansAssimetricoPacote":      [False, False, False, True ],
        "KMeansAssimetricoProbPente":        [False, True , False, False],
    #    "KMeansAssimetricoProbQuad":    [False, True , True , False],
    #    "KMeansSimetricoLinear":        [True , False, False, False],
    #    "KMeansSimetricoLinearQuad":    [True , False, True , False],
    #    "KMeansSimetricoPacote":        [True , False, False, True ],
    #    "KMeansSimetricoProb":          [True , True , False, False],
        "KMeansSimetricoProbQuadPente":      [True , True , True , False],
    }

    if(red[1] != 0):
        print("ENTROU AQUI REDUCAO COM KMEANS PENTE")
        for chave in DicionarioListaKmeans:
            binarios = DicionarioListaKmeans[chave]
            if(binarios[0] == False):
                print("###########################################################################")
                
                print(chave+ " K-Means Reduction no Último Estágio")
                binarios_pente =  [False, False, False, False]
                df_arvore, df_vazoes = reducaoArvoreClusterizacaoPente(mapa_aberturas_estagio_pente, df_vazoes_original.copy(), df_arvore_original.copy(), 
                    binarios_pente[0], perservaFolhas, binarios_pente[1], binarios_pente[3], binarios_pente[2], Plota)
                print(df_arvore)
                df_arvore, df_vazoes = reducaoArvoreClusterizacao(mapa_aberturas_estagio, df_vazoes.copy(), df_arvore.copy(), 
                    False, perservaFolhas, binarios[1], binarios[3], binarios[2], Plota)
                path_saida = "saidas\\"+chave
                path_saida = caminho_saida+"\\"+chave
                os.makedirs(path_saida, exist_ok=True)
                df_arvore.to_csv(path_saida+"\\arvore.csv", index=False)
                df_vazoes.to_csv(path_saida+"\\cenarios.csv", index=False)

                texto = "Arvore "+chave
                realizaTesteConsistenciaProbabilidadesFilhos(df_arvore, texto)
                testeCorrespondenciaArvoreVazoes(df_arvore, df_vazoes, texto)
                printaArvore(chave, path_saida, df_arvore)

            if(binarios[0] == True):
                # METODO CLUSTERIZACAO SIMETRICO
                if(mapa_reducao_estagio[max(df_arvore_original["PER"].tolist())] != 0):
                    print("###########################################################################")
                    print(chave+" K-Means Reduction no Último Estágio")
                    binarios_pente =  [False, False, False, False]
                    df_arvore, df_vazoes = reducaoArvoreClusterizacaoPente(mapa_aberturas_estagio_pente, df_vazoes_original.copy(), df_arvore_original.copy(), 
                        binarios_pente[0], perservaFolhas, binarios_pente[1], binarios_pente[3], binarios_pente[2], Plota)
                    print(df_arvore)
                    df_arvore, df_vazoes = reducaoArvoreClusterizacao(mapa_aberturas_estagio, df_vazoes.copy(), df_arvore.copy(), 
                        binarios[0], perservaFolhas, binarios[1], binarios[3], binarios[2], Plota)
                    path_saida = "saidas\\"+chave
                    path_saida = caminho_saida+"\\"+chave
                    os.makedirs(path_saida, exist_ok=True)
                    df_arvore.to_csv(path_saida+"\\arvore.csv", index=False)
                    df_vazoes.to_csv(path_saida+"\\cenarios.csv", index=False)
                    
                texto = "Arvore "+chave
                realizaTesteConsistenciaProbabilidadesFilhos(df_arvore, texto)
                testeSimetriaFilhos(df_arvore, texto)
                testeCorrespondenciaArvoreVazoes(df_arvore, df_vazoes, texto)
                printaArvore(chave, path_saida, df_arvore)


#    #####################PARAMETROS PARA CLUSTERIZACAO
#    DicionarioListaKmeans = {          #SIMETR, WEIGHT, QUAD, PACOTE
#    #    "KMeansAssimetricoLinear":      [False, False, False, False],
#    #    "KMeansAssimetricoLinearQuad":  [False, False, True , False],
#    #    "KMeansAssimetricoPacote":      [False, False, False, True ],
#        "KMeansAssimetricoProbRegress":        [False, True , False, False],
#    #    "KMeansAssimetricoProbQuad":    [False, True , True , False],
#    #    "KMeansSimetricoLinear":        [True , False, False, False],
#    #    "KMeansSimetricoLinearQuad":    [True , False, True , False],
#    #    "KMeansSimetricoPacote":        [True , False, False, True ],
#    #    "KMeansSimetricoProb":          [True , True , False, False],
#        "KMeansSimetricoProbQuadRegress":      [True , True , True , False],
#    }
#
#    if(red[1] != 0):
#        for chave in DicionarioListaKmeans:
#            binarios = DicionarioListaKmeans[chave]
#            if(binarios[0] == False):
#                print("###########################################################################")
#                print(chave)
#                ### METODOS DE CLUSTERIZACAO ASSIMETRICO
#
#                print(chave+ " Pós Backward Reduction no Último Estágio")
#                #print(mapa_reducao_estagio[max(df_arvore_original["PER"].tolist())])
#                mapa_red_auxiliar = {}
#                for est in df_arvore_original["PER"].tolist():
#                    mapa_red_auxiliar[est] = 0
#                mapa_red_auxiliar[max(df_arvore_original["PER"].tolist())] =  mapa_reducao_estagio[max(df_arvore_original["PER"].tolist())]
#                
#                print("###########################################################################")
#                print(chave+" Backward Reduction no Último Estágio")
#                Simetrica = False
#                df_arvore, df_vazoes = backwardReduction(mapa_red_auxiliar, mapa_aberturas_estagio, df_vazoes_original.copy(), df_arvore_original.copy(), Simetrica, Plota)
#                print(df_arvore)
#
#                df_arvore, df_vazoes = reducaoArvoreClusterizacao(mapa_aberturas_estagio, df_vazoes_original.copy(), df_arvore.copy(), 
#                    False, perservaFolhas, binarios[1], binarios[3], binarios[2], Plota)
#                path_saida = "saidas\\"+chave
#                path_saida = caminho_saida+"\\"+chave
#                os.makedirs(path_saida, exist_ok=True)
#                df_arvore.to_csv(path_saida+"\\arvore.csv", index=False)
#                df_vazoes.to_csv(path_saida+"\\cenarios.csv", index=False)
#
#                texto = "Arvore "+chave
#                realizaTesteConsistenciaProbabilidadesFilhos(df_arvore, texto)
#                testeCorrespondenciaArvoreVazoes(df_arvore, df_vazoes, texto)
#                printaArvore(chave, path_saida, df_arvore)
#
#            if(binarios[0] == True):
#                # METODO CLUSTERIZACAO SIMETRICO
#                if(mapa_reducao_estagio[max(df_arvore_original["PER"].tolist())] != 0):
#                    print(chave+ " Pós Backward Reduction no Último Estágio")
#                    #print(mapa_reducao_estagio[max(df_arvore_original["PER"].tolist())])
#                    mapa_red_auxiliar = {}
#                    for est in df_arvore_original["PER"].tolist():
#                        mapa_red_auxiliar[est] = 0
#                    mapa_red_auxiliar[max(df_arvore_original["PER"].tolist())] =  mapa_reducao_estagio[max(df_arvore_original["PER"].tolist())]
#                    
#                    print("###########################################################################")
#                    print(chave+" Backward Reduction no Último Estágio")
#                    Simetrica = False
#                    df_arvore, df_vazoes = backwardReduction(mapa_red_auxiliar, mapa_aberturas_estagio, df_vazoes_original.copy(), df_arvore_original.copy(), Simetrica, Plota)
#                    print(df_arvore)
#                    df_arvore, df_vazoes = reducaoArvoreClusterizacao(mapa_aberturas_estagio, df_vazoes_original.copy(), df_arvore.copy(), 
#                        binarios[0], perservaFolhas, binarios[1], binarios[3], binarios[2], Plota)
#                    path_saida = "saidas\\"+chave
#                    path_saida = caminho_saida+"\\"+chave
#                    os.makedirs(path_saida, exist_ok=True)
#                    df_arvore.to_csv(path_saida+"\\arvore.csv", index=False)
#                    df_vazoes.to_csv(path_saida+"\\cenarios.csv", index=False)
#                    
#                texto = "Arvore "+chave
#                realizaTesteConsistenciaProbabilidadesFilhos(df_arvore, texto)
#                testeSimetriaFilhos(df_arvore, texto)
#                testeCorrespondenciaArvoreVazoes(df_arvore, df_vazoes, texto)
#                printaArvore(chave, path_saida, df_arvore)
#
#
#
#

    perservaFolhas = False
    print("###########################################################################")
    ### METODO NEURAL GAS
    Simetrica = False
    df_arvore, df_vazoes = reducaoArvoreNeuralGas(mapa_aberturas_estagio, df_vazoes_original.copy(), df_arvore_original.copy(), Simetrica, perservaFolhas, Plota)
    path_saida = "saidas\\NeuralGas"
    path_saida = caminho_saida+"\\NeuralGas"
    os.makedirs(path_saida, exist_ok=True)
    df_arvore.to_csv(path_saida+"\\arvore.csv", index=False)
    df_vazoes.to_csv(path_saida+"\\cenarios.csv", index=False)

    texto = "Arvore Neural Gas"
    realizaTesteConsistenciaProbabilidadesFilhos(df_arvore, texto)
    testeCorrespondenciaArvoreVazoes(df_arvore, df_vazoes, texto)
    printaArvore("NeuralGas", path_saida, df_arvore)


    ### TESTES UNITARIOS PARA GARANTIR CONSISTENCIA DAS ARVORES GERADAS
    #executaTestesReducaoArvoresGVZP()

#    print("###########################################################################")
#    ### METODO NEURAL GAS
#    Simetrica = True
#    df_arvore, df_vazoes = reducaoArvoreNeuralGas(mapa_aberturas_estagio, df_vazoes_original.copy(), df_arvore_original.copy(), Simetrica, perservaFolhas, Plota)
#    path_saida = "saidas\\NeuralGasSimetrico"
#    path_saida = caminho_saida+"\\NeuralGasSimetrico"
#    os.makedirs(path_saida, exist_ok=True)
#    df_arvore.to_csv(path_saida+"\\arvore.csv", index=False)
#    df_vazoes.to_csv(path_saida+"\\cenarios.csv", index=False)
#
#    texto = "Arvore Neural Gas Simetrico"
#    realizaTesteConsistenciaProbabilidadesFilhos(df_arvore, texto)
#    testeCorrespondenciaArvoreVazoes(df_arvore, df_vazoes, texto)
#    printaArvore("NeuralGasSimetrico", path_saida, df_arvore)



    #####################PARAMETROS PARA CLUSTERIZACAO
    DicionarioListaKmeans = {          #SIMETR, WEIGHT, QUAD, PACOTE
    #    "KMeansAssimetricoLinear":      [False, False, False, False],
    #    "KMeansAssimetricoLinearQuad":  [False, False, True , False],
    #    "KMeansAssimetricoPacote":      [False, False, False, True ],
        #"KMeansAssimetricoProb":        [False, True , False, False],
    #    "KMeansAssimetricoProbQuad":    [False, True , True , False],
    #    "KMeansSimetricoLinear":        [True , False, False, False],
    #    "KMeansSimetricoLinearQuad":    [True , False, True , False],
    #    "KMeansSimetricoPacote":        [True , False, False, True ],
    #    "KMeansSimetricoProb":          [True , True , False, False],
    #    "KMeansSimetricoProbQuad":      [True , True , True , False],
    }




    for chave in DicionarioListaKmeans:
        binarios = DicionarioListaKmeans[chave]
        if(binarios[0] == False):
            print("###########################################################################")
            print(chave)
            ### METODOS DE CLUSTERIZACAO ASSIMETRICO
            df_arvore, df_vazoes = reducaoArvoreClusterizacao(mapa_aberturas_estagio, df_vazoes_original.copy(), df_arvore_original.copy(), 
                False, perservaFolhas, binarios[1], binarios[3], binarios[2], Plota)
            path_saida = "saidas\\"+chave
            path_saida = caminho_saida+"\\"+chave
            os.makedirs(path_saida, exist_ok=True)
            df_arvore.to_csv(path_saida+"\\arvore.csv", index=False)
            df_vazoes.to_csv(path_saida+"\\cenarios.csv", index=False)

            texto = "Arvore "+chave
            realizaTesteConsistenciaProbabilidadesFilhos(df_arvore, texto)
            testeCorrespondenciaArvoreVazoes(df_arvore, df_vazoes, texto)
            printaArvore(chave, path_saida, df_arvore)
        if(binarios[0] == True):

            print("###########################################################################")
            print(chave)
            #df_arvore, df_vazoes = reducaoArvoreClusterizacao(mapa_aberturas_estagio, df_vazoes_original.copy(), df_arvore_original.copy(), 
            df_arvore, df_vazoes = reducaoArvoreClusterizacao(mapa_aberturas_estagio, df_vazoes_original.copy(), df_arvore_original.copy(), 
            binarios[0], perservaFolhas, binarios[1], binarios[3], binarios[2], Plota)
            path_saida = "saidas\\"+chave
            path_saida = caminho_saida+"\\"+chave
            os.makedirs(path_saida, exist_ok=True)
            df_arvore.to_csv(path_saida+"\\arvore.csv", index=False)
            df_vazoes.to_csv(path_saida+"\\cenarios.csv", index=False)
            texto = "Arvore "+chave
            realizaTesteConsistenciaProbabilidadesFilhos(df_arvore, texto)
            testeSimetriaFilhos(df_arvore, texto)
            testeCorrespondenciaArvoreVazoes(df_arvore, df_vazoes, texto)
            printaArvore(chave, path_saida, df_arvore)

