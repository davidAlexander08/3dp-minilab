import sys
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from anytree import Node, RenderTree
from clusterization.clusterization import reducaoArvoreClusterizacao
from neuralGas.neuralGas import reducaoArvoreNeuralGas
from backwardReduction.simultaneousBackwardReduction import backwardReduction
from inewave.newave import Confhd
from inewave.newave import Hidr
import json

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


def calculaMapaReducaoEstagio(mapa_aberturas_estagio, df_arvore):

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
    print("###########################################################################")
    Simetrica = False
    df_arvore, df_vazoes = reducaoArvoreClusterizacao(mapa_aberturas_estagio, df_vazoes_pente_teste1.copy(), df_arvore_pente_teste1.copy(), Simetrica)
    #print(df_arvore)
    testeCorrespondenciaArvoreVazoes(df_arvore, df_vazoes,   texto+" Clusterizacao Assimetrica")
    realizaTesteConsistenciaProbabilidadesFilhos(df_arvore,  texto+" Clusterizacao Assimetrica")
    testeEstruturaArvore(df_arvore_arvore_teste1, df_arvore, texto+" Clusterizacao Assimetrica")
    testeEstruturaVazoes(df_vazoes_arvore_teste1, df_vazoes, texto+" Clusterizacao Assimetrica")
    print("###########################################################################")
    df_arvore, df_vazoes = backwardReduction(mapa_reducao_estagio, mapa_aberturas_estagio, df_vazoes_pente_teste1.copy(), df_arvore_pente_teste1.copy(), Simetrica)
    testeCorrespondenciaArvoreVazoes(df_arvore, df_vazoes,   texto+" Backward Reduction Assimetrica")
    realizaTesteConsistenciaProbabilidadesFilhos(df_arvore,  texto+" Backward Reduction Assimetrica")
    testeEstruturaArvore(df_arvore_arvore_teste1, df_arvore, texto+" Backward Reduction Assimetrica")
    testeEstruturaVazoes(df_vazoes_arvore_teste1, df_vazoes, texto+" Backward Reduction Assimetrica")
    print("###########################################################################")
    Simetrica = True
    df_arvore, df_vazoes = backwardReduction(mapa_reducao_estagio, mapa_aberturas_estagio, df_vazoes_pente_teste1.copy(), df_arvore_pente_teste1.copy(), Simetrica)
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
        df_arvore_BK, df_vazoes_BK = backwardReduction(mapa_red_auxiliar, mapa_aberturas_estagio, df_vazoes_pente_teste1.copy(), df_arvore_pente_teste1.copy(), Simetrica)
        Simetrica = True
        df_arvore, df_vazoes = reducaoArvoreClusterizacao(mapa_aberturas_estagio, df_vazoes_BK.copy(), df_arvore_BK.copy(), Simetrica)
    else:
        print("Clusterizacao Simetrica Usual")
        Simetrica = True
        df_arvore, df_vazoes = reducaoArvoreClusterizacao(mapa_aberturas_estagio, df_vazoes_pente_teste1.copy(), df_arvore_pente_teste1.copy(), Simetrica)
    testeCorrespondenciaArvoreVazoes(df_arvore, df_vazoes,   texto+" Clustering Simetrica")
    realizaTesteConsistenciaProbabilidadesFilhos(df_arvore,  texto+" Clustering Simetrica")
    testeEstruturaArvore(df_arvore_arvore_teste1, df_arvore, texto+" Clustering Simetrica")
    testeEstruturaVazoes(df_vazoes_arvore_teste1, df_vazoes, texto+" Clustering Simetrica")
    testeSimetriaFilhos(df_arvore, " Clustering Simetrica")
    print("###########################################################################")



    print("###########################################################################")
    ### METODO NEURAL GAS
    Simetrica = False
    df_arvore, df_vazoes = reducaoArvoreNeuralGas(mapa_aberturas_estagio, df_vazoes_pente_teste1.copy(), df_arvore_pente_teste1.copy(), Simetrica)
    #print(df_arvore)
    testeCorrespondenciaArvoreVazoes(df_arvore, df_vazoes,   texto+" Neural Gas Assimetrica")
    realizaTesteConsistenciaProbabilidadesFilhos(df_arvore,  texto+" Neural Gas Assimetrica")
    testeEstruturaArvore(df_arvore_arvore_teste1, df_arvore, texto+" Neural Gas Assimetrica")
    testeEstruturaVazoes(df_vazoes_arvore_teste1, df_vazoes, texto+" Neural Gas Assimetrica")



    print("###########################################################################")
    ### METODO NEURAL GAS
    Simetrica = True
    df_arvore, df_vazoes = reducaoArvoreNeuralGas(mapa_aberturas_estagio, df_vazoes_pente_teste1.copy(), df_arvore_pente_teste1.copy(), Simetrica)
    #print(df_arvore)
    testeCorrespondenciaArvoreVazoes(df_arvore, df_vazoes,   texto+" Neural Gas Simetrica")
    realizaTesteConsistenciaProbabilidadesFilhos(df_arvore,  texto+" Neural Gas Simetrica")
    testeEstruturaArvore(df_arvore_arvore_teste1, df_arvore, texto+" Neural Gas Simetrica")
    testeEstruturaVazoes(df_vazoes_arvore_teste1, df_vazoes, texto+" Neural Gas Simetrica")



def executaTestesReducaoArvoresGVZP():
    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    texto = "Teste 2 A, 3 Est Simetrica GVZP"
    print(texto)
    caso_teste1 = "casosTestesUnitarios\\1D\\3Estagios\\2Aberturas"
    df_vazoes_pente_teste1 = pd.read_csv(caso_teste1+"\\Pente_GVZP\\cenarios.csv")
    df_arvore_pente_teste1 = pd.read_csv(caso_teste1+"\\Pente_GVZP\\arvore.csv")
    df_vazoes_arvore_teste1 = pd.read_csv(caso_teste1+"\\Arvore_GVZP\\cenarios.csv")
    df_arvore_arvore_teste1 = pd.read_csv(caso_teste1+"\\Arvore_GVZP\\arvore.csv")
    mapa_aberturas_estagio = {1:2,    2:2}
    mapa_reducao_estagio = calculaMapaReducaoEstagio(mapa_aberturas_estagio, df_arvore_pente_teste1.copy())
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
    mapa_reducao_estagio = calculaMapaReducaoEstagio(mapa_aberturas_estagio, df_arvore_pente_teste1.copy())
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
    mapa_reducao_estagio = calculaMapaReducaoEstagio(mapa_aberturas_estagio, df_arvore_pente_teste1.copy())
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
    mapa_reducao_estagio = calculaMapaReducaoEstagio(mapa_aberturas_estagio, df_arvore_pente_teste1.copy())
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
    mapa_reducao_estagio = calculaMapaReducaoEstagio(mapa_aberturas_estagio, df_arvore_pente_teste1.copy())
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
    mapa_reducao_estagio = calculaMapaReducaoEstagio(mapa_aberturas_estagio, df_arvore_pente_teste1.copy())
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
    mapa_reducao_estagio = calculaMapaReducaoEstagio(mapa_aberturas_estagio, df_arvore_pente_teste1.copy())
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
    mapa_reducao_estagio = calculaMapaReducaoEstagio(mapa_aberturas_estagio, df_arvore_pente_teste1.copy())
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
    mapa_reducao_estagio = calculaMapaReducaoEstagio(mapa_aberturas_estagio, df_arvore_pente_teste1.copy())
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
    mapa_reducao_estagio = calculaMapaReducaoEstagio(mapa_aberturas_estagio, df_arvore_pente_teste1.copy())
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
    mapa_reducao_estagio = calculaMapaReducaoEstagio(mapa_aberturas_estagio, df_arvore_pente_teste1.copy())
    testeReducaoArvoresGVZP(texto, df_arvore_pente_teste1, df_vazoes_pente_teste1 , df_arvore_arvore_teste1,  df_vazoes_arvore_teste1, mapa_aberturas_estagio, mapa_reducao_estagio )
    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")


#executaTestesReducaoArvoresGVZP()
#exit(1)



caso = "..\\..\\Dissertacao\\apresentacaoCarmen_Gevazp\\caso_mini\\exercicioGevazp\\4Estagios\\3Aberturas\\Pente"
caso = "..\\..\\Dissertacao\\apresentacaoCarmen_Gevazp\\caso_mini\\exercicioGevazp\\3Estagios\\2Aberturas\\Pente_GVZP"
caso = "..\\..\\Dissertacao\\apresentacaoCarmen_Gevazp\\caso_mini\\exercicioGevazp\\4Estagios\\2Aberturas\\Pente"
caso = "..\\..\\Dissertacao\\apresentacaoCarmen_Gevazp\\caso_mini\\exercicioGevazp\\4Estagios\\3Aberturas_Equiprovavel\\Pente_GVZP"
caso = "..\\Dissertacao\\apresentacaoCarmen_Gevazp\\caso_mini\\exercicioGevazp\\4Estagios\\3Aberturas\\Pente_GVZP"
caso = "..\\Capitulo_5\\caso_mini_300Cen"
caso = "..\\Capitulo_5\\caso_mini_300Cen_sorteio"
caso = "..\\Capitulo_5\\caso_mini_300Cen_sorteio_8cen"
caso = "..\\Capitulo_5\\caso_mini_300Cen_sorteio_8cen_toy"
caso = "..\\Capitulo_5\\caso_mini_500Cen_sorteio_mensais"


#caso = "..\\Dissertacao\\apresentacaoCarmen_Gevazp\\caso_mini\\exercicioGevazp\\3Estagios\\3AberturasAssim\\Pente_GVZP"
#caso = "..\\Dissertacao\\apresentacaoCarmen_Gevazp\\caso_mini\\exercicioGevazp\\4Estagios\\3Aberturas_teste\\Pente_GVZP"
#mapa_aberturas_estagio = {1:3,    2:3,    3:3}
mapa_aberturas_estagio = {1:4,    2:5,    3:15}
mapa_aberturas_estagio = {1:25,    2:4,    3:3}
mapa_aberturas_estagio = {1:15,    2:4,    3:5}
mapa_aberturas_estagio = {1:10,    2:10,    3:3}
mapa_aberturas_estagio = {1:75,    2:2,    3:2}
mapa_aberturas_estagio = {1:125,    2:2,    3:2}
mapa_aberturas_estagio = {1:50,    2:5,    3:2}
mapa_aberturas_estagio = {1:25,    2:10,    3:2}
#mapa_aberturas_estagio = {1:5,    2:50,    3:2}


arquivo_vazoes = caso+"\\cenarios.csv"
#arquivo_vazoes = caso+"\\cenarios_teste.csv"
df_vazoes_original = pd.read_csv(arquivo_vazoes)
df_vazoes_original.to_csv("saidas\\vazoes_estudo.csv", index=False)
arquivo_estrutura_feixes = caso+"\\arvore.csv"
#arquivo_estrutura_feixes = caso+"\\arvore_teste.csv"
df_arvore_original = pd.read_csv(arquivo_estrutura_feixes)
df_arvore_original.to_csv("saidas\\arvore_estudo.csv", index=False)

print(df_arvore_original)
print("TOTAL POSTOS: ", len(df_vazoes_original["NOME_UHE"].unique()))
mapa_reducao_estagio = calculaMapaReducaoEstagio(mapa_aberturas_estagio, df_arvore_original.copy())
print("mapa_aberturas_estagio: ", mapa_aberturas_estagio)
print("mapa_reducao_estagio: ", mapa_reducao_estagio)




###########Realizacao de testes unitários
texto = "Arvore Original"
realizaTesteConsistenciaProbabilidadesFilhos(df_arvore_original, texto)
testeSimetriaFilhos(df_arvore_original, texto)
testeCorrespondenciaArvoreVazoes(df_arvore_original, df_vazoes_original, texto)
#printaArvore("Arvore Original", "saidas\\",df_arvore_original)
#exit(1)
######################################### COMPARACAO GRANULARIDADE



def calcula_prodt_65(codigo_usi, df_hidr):
    df_hidr_uhe = df_hidr.loc[(df_hidr["codigo_usina"] == codigo_usi)]
    vol_65 = (df_hidr_uhe["volume_maximo"].iloc[0] - df_hidr_uhe["volume_minimo"].iloc[0])*0.65 + df_hidr_uhe["volume_minimo"].iloc[0]
    vol_cota_A0 = df_hidr_uhe["a0_volume_cota"].iloc[0]
    vol_cota_A1 = df_hidr_uhe["a1_volume_cota"].iloc[0]*vol_65
    vol_cota_A2 = df_hidr_uhe["a2_volume_cota"].iloc[0]*vol_65**2
    vol_cota_A3 = df_hidr_uhe["a3_volume_cota"].iloc[0]*vol_65**3
    vol_cota_A4 = df_hidr_uhe["a4_volume_cota"].iloc[0]*vol_65**4
    cota_med_fuga = df_hidr_uhe["canal_fuga_medio"].iloc[0]
    perdas = df_hidr_uhe["perdas"].iloc[0]
    prodt_esp = df_hidr_uhe["produtibilidade_especifica"].iloc[0]
    cota_65 = vol_cota_A0 + vol_cota_A1 + vol_cota_A2 + vol_cota_A3 + vol_cota_A4
    fprodt_65 = (cota_65 - cota_med_fuga - perdas)*prodt_esp
    return fprodt_65

def encontraUsinaJusante(codigo_usi, df_confhd):
    df_conf_uhe = df_confhd.loc[(df_confhd["codigo_usina"] == codigo_usi)].reset_index(drop = True)
    return df_conf_uhe["codigo_usina_jusante"].iloc[0]
    
def calcula_prodt_acum_65(codigo_usi, df_confhd, df_hidr):
    usi_jusante = codigo_usi
    prodt = calcula_prodt_65(codigo_usi, df_hidr)
    #print("codigo_usi: ", codigo_usi, " prodt: ", prodt)
    while (usi_jusante != 0):
        usi_jusante = encontraUsinaJusante(usi_jusante, df_confhd)
        if(usi_jusante != 0):
            prodt += calcula_prodt_65(usi_jusante, df_hidr)
            #print("usi_jusante: ", usi_jusante, " prodt: ", prodt)
    return prodt



## TRANSFORMA EM ENA COM BASE EM UM DECK DE NEWAVE, UTILIZANDO O HIDR PARA VER A FUNCAO DE PRODUCAO A 65% E CONHECENDO A CASCATA
## POR MEIO DO ARQUIVO DE CASCATA DO NEWAVE
## VAZOES_FEIXES_ENA_SIN
### VAZOES_FEIXES_INCR_SIN
caminho_caso_newave = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\ferramentas"
df_confhd = Confhd.read(caminho_caso_newave+"\\transformaNewaveLab\\deck_newave_2020_01\\CONFHD.dat").usinas
df_hidr = Hidr.read(caminho_caso_newave+"\\transformaNewaveLab\\deck_newave_2020_01\\HIDR.dat").cadastro
df_hidr = df_hidr.reset_index()
postos_considerados = df_vazoes_original["NOME_UHE"].unique()
lista_df_ena = []
for uhe in df_vazoes_original["NOME_UHE"].unique():
    df_conf_uhe = df_confhd.loc[(df_confhd["posto"] == uhe)].reset_index(drop = True)
    if(not df_conf_uhe.empty):
        codigo_usi = df_conf_uhe["codigo_usina"].iloc[0]
        fprodt_acum_65 = calcula_prodt_acum_65(codigo_usi, df_confhd,  df_hidr)
        df_uhe = df_vazoes_original.loc[(df_vazoes_original["NOME_UHE"] == uhe)].reset_index(drop = True)
        df_ena = df_uhe.copy()
        df_ena["ENA"] = fprodt_acum_65*df_uhe["VAZAO"]
        df_ena["ENA"] = df_ena["ENA"].round(0)
        lista_df_ena.append(df_ena)
        #print("uhe: ", uhe, " fprodt_acum_65: ", fprodt_acum_65)


df_ena_result = pd.concat(lista_df_ena).reset_index(drop = True)
print(df_ena_result)
df_mean = df_ena_result.groupby("NOME_UHE")["VAZAO"].mean().reset_index()
top_uhe = df_mean.sort_values(by=["VAZAO"], ascending=[False])
top_uhe["VAZAO"] = top_uhe["VAZAO"].round(0)
top_uhe.to_csv("saidas_ENA\\top_ena.csv")
df_ena_result.to_csv("saidas_ENA\\ena_feixes_incr.csv")


lista_df = []
df_aux = df_ena_result.loc[df_ena_result["NOME_UHE"] == df_ena_result["NOME_UHE"].iloc[0]].copy()
df_aux["VAZAO"] = df_aux["VAZAO"]*0
df_aux["ENA"] = df_aux["ENA"]*0
print(df_aux)

for uhe in df_ena_result["NOME_UHE"].unique():
    df_ena = df_ena_result.loc[(df_ena_result["NOME_UHE"] == uhe)].copy().reset_index(drop = True)
    df_aux["ENA"] += df_ena["ENA"]

df_ena_sin = df_aux
df_ena_sin = df_ena_sin.drop(columns = "VAZAO")
df_ena_sin = df_ena_sin.rename(columns={"ENA": "VAZAO"})
df_ena_sin.to_csv("saidas_ENA\\soma_ena.csv", index = False)

print("df_vazoes: ", df_vazoes_original)
print("df_ena_result: ", df_ena_result)
print("df_ena_sin: ", df_ena_sin)



### METODO -  BACKWARD REDUCTION ASSIMETRICO
Simetrica = False
df_arvore, df_vazoes = backwardReduction(mapa_reducao_estagio, mapa_aberturas_estagio, df_ena_sin.copy(), df_arvore_original.copy(), Simetrica, False)
path_saida = "saidas_ENA\\BKAssimetrico"
df_arvore.to_csv(path_saida+"\\arvore.csv", index=False)

print(df_vazoes)
########### DESAGREGA AS ENAS EM VAZAO NOVAMENTE
lista_df_novas_vazoes = []
for idx, row in df_vazoes.iterrows():
    node = row.NO
    df_temp = df_vazoes_original.loc[(df_vazoes_original["NO"] == node)].reset_index(drop = True)
    lista_df_novas_vazoes.append(df_temp)

df_vazoes_reduzidas_ENA = pd.concat(lista_df_novas_vazoes).reset_index(drop = True)
print(df_vazoes_reduzidas_ENA)
df_vazoes_reduzidas_ENA.to_csv(path_saida+"\\cenarios.csv", index=False)


texto = "Arvore Backward Reduction Assimetrico"
realizaTesteConsistenciaProbabilidadesFilhos(df_arvore, texto)
testeCorrespondenciaArvoreVazoes(df_arvore, df_vazoes_reduzidas_ENA, texto)
printaArvore("BKAssimetrico", path_saida, df_arvore)

