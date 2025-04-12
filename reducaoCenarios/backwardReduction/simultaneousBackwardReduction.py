import pandas as pd
import numpy as np
import networkx as nx
import pydot
import matplotlib.pyplot as plt
from anytree import Node, RenderTree
import time
from joblib import Parallel, delayed, parallel_backend
import os
os.environ["PATH"] += os.pathsep + r"C:\\Program Files (x86)\\Graphviz\\bin"
#from numba import jit
from itertools import combinations  # Efficiently generate unique (i, j) pairs
from scipy.stats import skew
import plotly.graph_objects as go

def printaArvoreFiguraGrande(texto, df_arvore):
    df_arvore.loc[df_arvore["NO_PAI"] == 0, "NO_PAI"] = 1
    print(df_arvore)
    G = nx.DiGraph()
    for _, row in df_arvore.iterrows():
        G.add_edge(row['NO_PAI'], row['NO'], weight=row['PROB'])
    pos = nx.drawing.nx_pydot.pydot_layout(G, prog='dot')
    plt.figure(figsize=(10, 8))
    nx.draw(G, pos, with_labels=True, node_size=2000, node_color='lightblue', font_size=10, font_weight='bold', arrows=True)
    
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    plt.savefig(texto+".png", format="png", dpi=100, bbox_inches="tight")
    plt.title("Tree Visualization")
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

def retornaMatrizAfluenciasCaminho(caminho, df_vazoes):
    df_filtered = df_vazoes[df_vazoes["NO"].isin(caminho)]
    matriz_df = df_filtered.pivot(index="NOME_UHE", columns="NO", values="VAZAO")
    matriz_df = matriz_df.reindex(columns=reversed(caminho), fill_value=0)
    return matriz_df.to_numpy()



def retornaMenorValorLimiteSuperior(no_base, no_foco, dicionario_distancias, Q):
    return min(dicionario_distancias[(no_foco, no_analisado)] for no_analisado in Q)

    
def retornaNoMaisProximo(no_base, no_foco, dicionario_distancias, Q):
    menor_valor = float('inf')
    mais_proximo = None
    for no_analisado in Q:
        if no_analisado != no_base:
            dist = dicionario_distancias.get((no_foco, no_analisado), float('inf'))
            if dist < menor_valor:
                menor_valor = dist
                mais_proximo = no_analisado
    return mais_proximo


def retornaNoMaisProximoSimetrico(no_base, no_foco, dicionario_distancias, Q, df_arvore, aberturas_estagio, mapa_excluidos):
    menor_valor = float('inf')
    mais_proximo = None
    #print("no_excluido: ", no_foco)
    for no_analisado in Q:
        #print("Antes no_analisado: ", no_analisado, " nfilhos: ", len(getFilhos(no_analisado, df_arvore)) , " excluidos: ", mapa_excluidos[no_analisado] )
        #if no_analisado != no_base and len(getFilhos(no_analisado, df_arvore)) < aberturas_estagio :
        if no_analisado != no_base and len(mapa_excluidos[no_analisado]) < aberturas_estagio-1 :
            dist = dicionario_distancias.get((no_foco, no_analisado), float('inf'))
            if dist < menor_valor:
                menor_valor = dist
                mais_proximo = no_analisado
    return mais_proximo

def calcular_dist_kantorovich(no_foco, J, Q, dicionario_distancias, dicionarioDeProbabilidades, dicionarioLinhaMatrizCrescente, dicionarioLinhaMatrizCrescenteNo):
    dist_kantorovich = 0
    Exclude_Temp = [no_foco] + J 
    for no_excluido in Exclude_Temp:
        indexes_to_remove = []
        for idx, (node, distance) in enumerate(zip(dicionarioLinhaMatrizCrescenteNo[no_excluido], dicionarioLinhaMatrizCrescente[no_excluido])):
            if node in J or node == no_excluido:
                indexes_to_remove.append(idx)
            if node not in Exclude_Temp:
                lowest_valid_node = node
                lowest_valid_distance = distance
                break  # Stop at the first valid node
        #for idx in indexes_to_remove:
        #    del dicionarioLinhaMatrizCrescenteNo[no_excluido][idx]
        #    del dicionarioLinhaMatrizCrescente[no_excluido][idx]

        
        #print("no_excluido: ", no_excluido, " lowest_valid_node: ", lowest_valid_node, " lowest_valid_distance: ", lowest_valid_distance)
        
        #menorValor = min(dicionario_distancias[(no_excluido, no_analisado)] for no_analisado in Q if no_analisado != no_foco)
        #print("no_excluido: ", no_excluido, " menorValor: ", menorValor)
        #dist_kantorovich += dicionarioDeProbabilidades[no_excluido] * retornaMenorValor(no_foco, no_excluido, dicionario_distancias, Q)
        #dist_kantorovich += dicionarioDeProbabilidades[no_excluido] * menorValor
        dist_kantorovich += dicionarioDeProbabilidades[no_excluido] * lowest_valid_distance
        #print(f"no_excluido: {no_excluido}, prob: {dicionarioDeProbabilidades[no_excluido]}, menorValor: {retornaMenorValor(no_foco, no_excluido, dicionario_distancias, Q)}")
    return dist_kantorovich


def compute_distance(i, j, matrizFoco, matrizAnalise):
    frobenius_norm = np.linalg.norm(matrizFoco - matrizAnalise, ord='fro')
    return i, j, frobenius_norm

def compute_caminho_probabilidade_matriz(no, df_arvore, df_vazoes):
    caminho = retorna_lista_caminho(no, df_arvore)[:-1]
    matrizAfluencias = retornaMatrizAfluenciasCaminho(caminho, df_vazoes)
    df_arvore_dict = df_arvore.set_index("NO")["PROB"].to_dict()
    prob_no = df_arvore_dict[min(caminho)]
    return no, caminho, matrizAfluencias, prob_no


def backwardReduction(mapa_reducao_estagio, mapa_aberturas_estagio,  df_vazoes, df_arvore, Simetrico):
    start_time = time.time()
    tempo_Total = time.time()
    
    if(Simetrico == True):
        print("Realizando Redução Simetrica - Backward Reduction")
    else:
        print("Realizando Redução Assimetrica  - Backward Reduction")

    ################## FLAG TOLERANCIA PARA EXCLUSAO DE CENARIOS COM BASE NO LIM SUP (MAXIMA DIFF DAS ARVORES) #################
    flag_criterio_de_parada_por_tolerancia = 0
    ##################  ACELERADOR DE CONVERGENCIA, STEP DA EXCLUSAO DE CENARIOS ##############
    flag_acelerador_exclusao_cenarios = 0 #Exclui sempre uma % dos cenários juntos
    parametro_exclusao_cenarios = 0.01 #1% dos meores cenários para serem excluídos a cara iteração
    NumeroIteracoesAcelerador = 50
    ################### CORES PROCESSAMENTO PARALELO ##########################
    cores = -1
    cores = 1
    ###################################

    dicionario_distancias = {}
    #MONTANDO A MATRIZ DE DISTANCIAS ENTRE OS NOS DE TERMINADO ESTAGIO
    estagios_estocasticos = sorted(df_arvore["PER"].unique()[1:])#df_arvore["PER"].unique()[1:]
    #printaArvore("ArvoreInicial", df_arvore_original)
    end_time = time.time()
    elapsed_time = end_time - start_time  # Calculate elapsed time
    print(f"Tempo de Inicialização: {elapsed_time:.4f} seconds")
    start_time = time.time()

    for est in reversed(estagios_estocasticos):
        
        nos_do_estagio = df_arvore.loc[(df_arvore["PER"] == est) & (df_arvore["PROB"] != 0.0)]["NO"].tolist()
        fig = go.Figure()
        lista_x = []
        lista_y = []
        for no_plot in nos_do_estagio:
            vazao_usi1 = df_vazoes.loc[(df_vazoes["NOME_UHE"] == 6) & (df_vazoes["NO"] == no_plot)]["VAZAO"].iloc[0]
            vazao_usi2 = df_vazoes.loc[(df_vazoes["NOME_UHE"] == 275) & (df_vazoes["NO"] == no_plot)]["VAZAO"].iloc[0]
            lista_x.append(vazao_usi2)
            lista_y.append(vazao_usi1)
        fig.add_trace(go.Scatter(
            x=lista_x,
            y=lista_y,
            marker=dict(color='blue', size=8),
            mode="markers",
            name="TucuruixFurnas",
            showlegend=False  
        ))







        matrizDistancias = np.zeros((len(nos_do_estagio), len(nos_do_estagio)))
        dicionarioDeProbabilidades = {}
        #PASSO 1 -> MONTAR MATRIZ DE DISTANCIAS ENTRE OS CENARIOS
        results = Parallel(n_jobs=cores)(
        delayed(compute_caminho_probabilidade_matriz)(no, df_arvore, df_vazoes)
        for no in nos_do_estagio)

        caminhos = {}
        matrizesAfluencias = {}
        probabilidades = {}

        for no, caminho, matrizAfluencias, prob_no in results:
            caminhos[no] = caminho
            matrizesAfluencias[no] = matrizAfluencias
            probabilidades[no] = prob_no

        # Update the dictionary with probabilities
        dicionarioDeProbabilidades.update(probabilidades)

        end_time = time.time()
        elapsed_time = end_time - start_time  # Calculate elapsed time
        #print(f"Tempo de Parâmetros Iniciais: {elapsed_time:.4f} seconds")
        start_time = time.time()
        
        nos_indices = {no: idx for idx, no in enumerate(nos_do_estagio)}
        matriz_stack = np.array([matrizesAfluencias[no] for no in nos_do_estagio])


        results = Parallel(n_jobs=cores)(
            delayed(compute_distance)(i, j, matriz_stack[i], matriz_stack[j])
            for i, j in combinations(range(len(nos_do_estagio)), 2)  # Only unique pairs
        )

        ## Store results in matrix and dictionary
        for i, j, frobenius_norm in results:
            matrizDistancias[i, j] = frobenius_norm
            matrizDistancias[j, i] = frobenius_norm
            dicionario_distancias[(nos_do_estagio[i], nos_do_estagio[j])] = frobenius_norm
            dicionario_distancias[(nos_do_estagio[j], nos_do_estagio[i])] = frobenius_norm
        
        dicionarioLinhaMatrizCrescente = {}
        dicionarioLinhaMatrizCrescenteNo = {}
        for no in nos_do_estagio:
            node_distance_pairs = list(zip(nos_indices.keys(), matrizDistancias[nos_indices[no],:]))
            sorted_pairs = sorted(node_distance_pairs, key=lambda x: x[1])
            sorted_nodes = [node for node, _ in sorted_pairs]
            sorted_distances = [dist for _, dist in sorted_pairs]
            dicionarioLinhaMatrizCrescente[no] = sorted_distances
            dicionarioLinhaMatrizCrescenteNo[no] = sorted_nodes

        end_time = time.time()
        elapsed_time = end_time - start_time  # Calculate elapsed time
        #print(f"Tempo de Matriz Distância: {elapsed_time:.4f} seconds")
        start_time = time.time()
        
        #print(dicionarioDeProbabilidades)
        #print(matrizDistancias)
        #exit(1)
        #np.savetxt("matrizDistancias.csv", matrizDistancias, delimiter=",", fmt="%.6f")  # "%.6f" ensures 6 decimal places

        # PASSO 1.2 -> Verificar a máxima distância obtida entre as árvores testando todos elementos excluídos menos 1
        limSup = float('inf')
        for no in nos_do_estagio:
            J = nos_do_estagio.copy()
            J.remove(no)
            Q = [no]
            mapa_distancias = {}
            dist_kantorovich = 0
            for no_excluido in J:
                dist_kantorovich += dicionarioDeProbabilidades[no_excluido] * retornaMenorValorLimiteSuperior(no, no_excluido, dicionario_distancias, Q)
            limSup = dist_kantorovich if dist_kantorovich < limSup else limSup
            #print(f"NO: {no}, Kantorovich: {dist_kantorovich}, limSup:  {limSup}")
        #exit(1)
        # PASSO 2 -> INICIALIZAR O PROCESSO ITERATIVO. CALCULAR A DISTANCIA DE KANTOROVICH PARA CADA CENARIO E VERICICAR O QUE TEM MENOR PESO
        #CONSIDERANDO J = {}, avaliar o imacto de 
        J = []
        Q = nos_do_estagio
        if(flag_criterio_de_parada_por_tolerancia):
            erro = 0
            iteracao = 1
            while (erro < mapa_tolerancia_estagio[est]):
                mapa_distancias = {}
                #for i, no_foco in enumerate(Q):
                #    dist_kantorovich = calcular_dist_kantorovich(no_foco, J, Q, dicionario_distancias, dicionarioDeProbabilidades, dicionarioLinhaMatrizCrescente, dicionarioLinhaMatrizCrescenteNo)
                #    mapa_distancias[no_foco] = dist_kantorovich
                #    #print(f"NO: {no_foco}, Kantorovich: {dist_kantorovich} Degradacação: {dist_kantorovich/limSup}")

                ##Thread computation
                with parallel_backend("threading"):  # Uses threads instead of processes
                    results = Parallel(n_jobs=cores)(
                        delayed(calcular_dist_kantorovich)(no_foco, J, Q, dicionario_distancias, dicionarioDeProbabilidades, dicionarioLinhaMatrizCrescente, dicionarioLinhaMatrizCrescenteNo)
                        for no_foco in Q
                    )
                mapa_distancias.update(zip(Q, results))


                if(flag_acelerador_exclusao_cenarios and iteracao < NumeroIteracoesAcelerador):
                    total_cenarios = len(nos_do_estagio)
                    numero_cenarios_excluidos_por_iter = total_cenarios*parametro_exclusao_cenarios
                    numero_cenarios_excluidos_por_iter = int(round(numero_cenarios_excluidos_por_iter,0))
                    if(numero_cenarios_excluidos_por_iter == 0): numero_cenarios_excluidos_por_iter = 1
                    lowest_10_keys = [x[0] for x in sorted(mapa_distancias.items(), key=lambda x: x[1])[:numero_cenarios_excluidos_por_iter]]
                    lowest_10_values = [x[1] for x in sorted(mapa_distancias.items(), key=lambda x: x[1])[:numero_cenarios_excluidos_por_iter]]
                    J.extend(lowest_10_keys)  
                    Q = [q for q in Q if q not in lowest_10_keys]  # If Q is a list
                    erro = max(lowest_10_values)/limSup
                    print("EST: ", est , " FIM ITER: ", iteracao, " erro: ", erro)
                    print(" Tamanho J: ", len(J))
                    print(" Tamanho Q: ", len(Q))
                else:
                    key_min_value = min(mapa_distancias, key=mapa_distancias.get)
                    min_value = mapa_distancias[key_min_value]
                    J.append(key_min_value)
                    Q.remove(key_min_value)
                    erro = min_value/limSup
                    print("Tamanho J: ", len(J), " EST: ", est , " ITER: ", iteracao, " erro: ", erro)
                    #print("J: ", J)
                #print("EST: ", est , " FIM ITER: ", iteracao, " J: ", J, " Q: ", Q, " erro: ", erro)                
                end_time = time.time()
                elapsed_time = end_time - start_time  # Calculate elapsed time
                print(f"Tempo Final Iteracao {iteracao}: Tempo {elapsed_time:.4f} seconds")
                start_time = time.time()
                iteracao += 1
        else:
            for iter in range(1,int(mapa_reducao_estagio[est]+1)):
                mapa_distancias = {}
                for i, no_foco in enumerate(Q):
                    dist_kantorovich = calcular_dist_kantorovich(no_foco, J, Q, dicionario_distancias, dicionarioDeProbabilidades, dicionarioLinhaMatrizCrescente, dicionarioLinhaMatrizCrescenteNo)
                    mapa_distancias[no_foco] = dist_kantorovich
                    #print("no: ", no_foco, " dist_K: ", dist_kantorovich)
                #print("Tamanho J: ", len(J), " EST: ", est , " FIM ITER: ", iter)
                key_min_value = min(mapa_distancias, key=mapa_distancias.get)
                min_value = mapa_distancias[key_min_value]
                J.append(key_min_value)
                Q.remove(key_min_value)
                #print("FIM ITER: ", iter, " J: ", J, " Q: ", Q)

        # PASSO I+1, REDISTRIBUIR AS PROBABILIDADES
        #Cria listas de nos proximos para aglutinacao
        mapa_excluidos = {}
        for i, no_remanescente in enumerate(Q):
            mapa_excluidos[no_remanescente] = []
        #print('df_arvore: ', df_arvore)

        for i, no_excluido in enumerate(J):
            if(Simetrico and est < max(estagios_estocasticos)):
                aberturas_estagio = mapa_aberturas_estagio[est]
                no_mais_proximo = retornaNoMaisProximoSimetrico(no_excluido, no_excluido, dicionario_distancias, Q, df_arvore, aberturas_estagio, mapa_excluidos)
                #print("est: ", est, " no_excluido: ", no_excluido, " No_mais_prox: ", no_mais_proximo)
                
            if(Simetrico == False or est == max(estagios_estocasticos)):
                no_mais_proximo = retornaNoMaisProximo(no_excluido, no_excluido, dicionario_distancias, Q)
            mapa_excluidos[no_mais_proximo].append(no_excluido)
            #print(mapa_excluidos)

            #print("no_prox: ", no_mais_proximo, " no_exl: ", no_excluido)



        if(est == max(estagios_estocasticos)):
            #df_arvore.to_csv("debug_arvore.csv", index = False)
            for key in mapa_excluidos:
                if(len(mapa_excluidos[key]) > 0):
                    prob_resultante = 0
                    caminho_no_proximo = retorna_lista_caminho(key, df_arvore)[:-1]

                    prob_resultante += df_arvore.loc[(df_arvore["NO"] == min(caminho_no_proximo))]["PROB"].iloc[0]
                    for i, no_excluido in enumerate(mapa_excluidos[key]):
                        caminho_no_excluido = retorna_lista_caminho(no_excluido, df_arvore)[:-1]
                        prob_resultante += df_arvore.loc[(df_arvore["NO"] == min(caminho_no_excluido))]["PROB"].iloc[0]
                        df_arvore = df_arvore[~df_arvore["NO"].isin(caminho_no_excluido)].reset_index(drop = True)
                        #print("caminho_no_excluido: ", caminho_no_excluido, " no proximo: ", key, " min no: ", min(caminho_no_excluido))
                    #print("caminho_proximo: ", caminho_no_proximo, " min no: ", min(caminho_no_proximo))
                    df_arvore.loc[(df_arvore["NO"] == min(caminho_no_proximo)),"PROB"] = prob_resultante
                #df_arvore.to_csv("debug_arvore2.csv", index = False)
            #print("FIM EST: ", est)
        else:
            #print(mapa_excluidos)
            #print(df_arvore)
            for key in mapa_excluidos:
                if(len(mapa_excluidos[key]) > 0):
                    caminho_no_proximo = retorna_lista_caminho(key, df_arvore)[:-1]
                    #print("key: ", key)
                    #print("mapa_excluidos[key]: ", mapa_excluidos[key])
                    filhos = []
                    df_filhos = df_arvore.loc[df_arvore["NO_PAI"] == key, "NO"].tolist()
                    #print(df_filhos)
                    assert len(df_filhos) == 1, f"More than one child found for key {key}: {df_filhos}"
                    filho = df_filhos[0]
                    filhos.append(filho)
                    for i, no_excluido in enumerate(mapa_excluidos[key]):
                        #print("no_excluido: ", no_excluido)
                        df_filhos = df_arvore.loc[df_arvore["NO_PAI"] == no_excluido, "NO"].tolist()
                        assert len(df_filhos) == 1, f"More than one child found for key {key}: {df_filhos}"
                        filho = df_filhos[0]
                        filhos.append(filho)
                    #print(filhos)
                    for filho in filhos:
                        no_pai = df_arvore.loc[(df_arvore["NO"] == filho), "NO_PAI"].iloc[0]
                        caminho_no_pai = retorna_lista_caminho(no_pai, df_arvore)[:-1]
                        prob_pai = df_arvore.loc[(df_arvore["NO"] == min(caminho_no_pai)), "PROB"].iloc[0]
                        #print("no_pai: ", no_pai, " prob: ", prob_pai, " filho: ", filho)
                        df_arvore.loc[(df_arvore["NO"] == filho), "PROB"] = prob_pai
                        df_arvore.loc[(df_arvore["NO"] == filho), "NO_PAI"] = key

            for key in mapa_excluidos:
                if(len(mapa_excluidos[key]) > 0):
                    prob_resultante = 0
                    caminho_no_proximo = retorna_lista_caminho(key, df_arvore)[:-1]
                    prob_resultante += df_arvore.loc[(df_arvore["NO"] == min(caminho_no_proximo))]["PROB"].iloc[0]
                    for i, no_excluido in enumerate(mapa_excluidos[key]):
                        caminho_no_excluido = retorna_lista_caminho(no_excluido, df_arvore)[:-1]
                        prob_resultante += df_arvore.loc[(df_arvore["NO"] == min(caminho_no_excluido))]["PROB"].iloc[0]
                        df_arvore = df_arvore[~df_arvore["NO"].isin(caminho_no_excluido)].reset_index(drop = True)
                    df_arvore.loc[(df_arvore["NO"] == min(caminho_no_proximo)),"PROB"] = round(prob_resultante,4)
                    df_arvore = df_arvore[~df_arvore["NO"].isin(mapa_excluidos[key])].reset_index(drop = True)
                    #print("key: ", key, " prob: ", round(prob_resultante,4))
                    

                    ## Arrumando probabilidade dos filhos
                    filhos = df_arvore.loc[df_arvore["NO_PAI"] == key]["NO"].tolist()
                    for filho in filhos:
                        df_arvore.loc[df_arvore["NO"] == filho, "PROB"] = round(df_arvore.loc[df_arvore["NO"] == filho, "PROB"]/prob_resultante,4)
                    #print(filhos)


        
            #print(df_arvore)
        end_time = time.time()
        elapsed_time = end_time - start_time  # Calculate elapsed time
        #print(f"Tempo Calculos Estagio: {est} Tempo: {elapsed_time:.4f} seconds")
        start_time = time.time()

        lista_x = []
        lista_y = []
        for no_plot in Q:
            vazao_usi1 = df_vazoes.loc[(df_vazoes["NOME_UHE"] == 6) & (df_vazoes["NO"] == no_plot)]["VAZAO"].iloc[0]
            vazao_usi2 = df_vazoes.loc[(df_vazoes["NOME_UHE"] == 275) & (df_vazoes["NO"] == no_plot)]["VAZAO"].iloc[0]
            lista_x.append(vazao_usi2)
            lista_y.append(vazao_usi1)
        fig.add_trace(go.Scatter(
            x=lista_x,
            y=lista_y,
            marker=dict(color='red', size=8),
            mode="markers",
            name="TucuruixFurnas",
            showlegend=False  
        ))

        fig.update_layout(
            title='Scater Plot Centroides',
            xaxis_title='m3/s',
            yaxis_title='m3/s'
        )
        text_out = "BKSimetrico" if Simetrico == True else "BKAssimetrico"
        fig.write_html("saidas\\"+text_out+"\\BackwardRed_"+str(est)+'.html', auto_open=False)




    tempo_final = time.time()
    elapsed_time = tempo_final - tempo_Total  # Calculate elapsed time
    print(f"Tempo Total: {elapsed_time:.4f} seconds")


    ### COMENTE ESSA LINHA PARA IMPRIMIR TAMBEM NO CADASTRO DE VAZOES OS NOS ELIMINADOS ALEM DO NO RESULTANTE
    df_vazoes = df_vazoes[df_vazoes["NO"].isin(df_arvore["NO"].unique())].reset_index(drop = True)
    return df_arvore, df_vazoes



















#
#caso = "..\\..\\Mestrado\\caso_1D"
##caso = "..\\..\\casos\\Mestrado\\caso_2D"
#caso = "..\\..\\casos\\Mestrado\\caso_construcaoArvore"
##caso = "..\\..\\Mestrado\\caso_construcaoArvore_SIN"
##caso = "..\\..\\Mestrado\\caso_construcaoArvore_SIN_2000cen"
##caso = "..\\..\\Mestrado\\caso_construcaoArvore_SIN_1000cen"
##caso = "..\\..\\Mestrado\\caso_construcaoArvore_SIN_500cen"
##caso = "..\\..\\Mestrado\\caso_construcaoArvore_SIN_500cen_ENASIN"
##caso = "..\\..\\Mestrado\\caso_construcaoArvore_SIN_50cen"
##caso = "..\\..\\Mestrado\\teste_wellington"
#caso = "..\\..\\Dissertacao\\apresentacaoCarmen_Gevazp\\caso_mini\\exercicioGevazp\\3Estagios\\2Aberturas\\Pente"
#caso = "..\\..\\Dissertacao\\apresentacaoCarmen_Gevazp\\caso_mini\\exercicioGevazp\\4Estagios\\2Aberturas\\Pente"
#caso = "..\\..\\Dissertacao\\apresentacaoCarmen_Gevazp\\caso_mini\\exercicioGevazp\\4Estagios\\3Aberturas_Equiprovavel\\Pente_GVZP"
#caso = "..\\..\\Dissertacao\\apresentacaoCarmen_Gevazp\\caso_mini\\exercicioGevazp\\4Estagios\\3Aberturas\\Pente_GVZP"
##caso = "..\\..\\Dissertacao\\apresentacaoCarmen_Gevazp\\caso_mini\\exercicioGevazp\\4Estagios\\2Aberturas_Assim\\Pente_GVZP"
##caso = "..\\..\\Dissertacao\\apresentacaoCarmen_Gevazp\\caso_mini\\exercicioGevazp\\3Estagios\\2Aberturas_Assim\\Pente_GVZP"
##caso = "..\\..\\Dissertacao\\apresentacaoCarmen_Gevazp\\caso_mini\\exercicioGevazp\\3Estagios\\3AberturasAssim\\Pente_GVZP"
#arquivo_vazoes = caso+"\\cenarios.csv"
#arquivo_estrutura_feixes = caso+"\\arvore.csv"
#df_vazoes = pd.read_csv(arquivo_vazoes)
#df_vazoes.to_csv("..\\saidas\\BKAssimetrico\\cenarios.csv", index=False)
#df_arvore = pd.read_csv(arquivo_estrutura_feixes)
#df_arvore.to_csv("..\\saidas\\BKAssimetrico\\arvore_estudo.csv", index=False)
#df_arvore_original = df_arvore.copy()
#Simetrica = False
#df_arvore, df_vazoes = backwardReduction(mapa_reducao_estagio, df_arvore, df_vazoes, Simetrica)
#df_arvore.to_csv("..\\saidas\\BKAssimetrico\\arvore.csv", index=False)
#df_vazoes.to_csv("..\\saidas\\BKAssimetrico\\cenarios.csv", index=False)
#exit(1)


###Estatisticas
#for est in sorted(df_arvore["PER"].unique()):
#    nos = df_arvore.loc[df_arvore["PER"] == est]["NO"].unique()
#    nos_original = df_arvore_original.loc[df_arvore_original["PER"] == est]["NO"].unique()
#    print("NOS ESTAGIO: ", est, " DE: ", len(nos_original), " PARA: ", len(nos))
#
### TESTE ESTATISTICO USINAS
#usinas = [17, 66, 275, 156, 211, 22, 25, 292]
#lista_df = []
#for est in sorted(df_arvore["PER"].unique())[1:]:
#    nos = df_arvore.loc[df_arvore["PER"] == est]["NO"].unique()
#    nos_original = df_arvore_original.loc[df_arvore_original["PER"] == est]["NO"].unique()
#
#    vazao = df_vazoes.loc[df_vazoes["NO"].isin(nos)].copy().reset_index(drop = True)
#    vazao_orig = df_vazoes.loc[df_vazoes["NO"].isin(nos_original)].copy().reset_index(drop = True)
#    print("EST: ", est, " vazao_red: ", vazao)
#    print("EST: ", est, " vazao_orig: ", vazao_orig)
#
#    for usi in usinas:
#        vaz_red_usi = vazao.loc[(vazao["NOME_UHE"] == usi).reset_index(drop = True)]
#        vaz_orig_usi = vazao_orig.loc[(vazao_orig["NOME_UHE"] == usi).reset_index(drop = True)]
#        print("MEDIA EST ", est, " USINA: ", usi)
#        mean_reduzida = vaz_red_usi["VAZAO"].mean()
#        mean_original = vaz_orig_usi["VAZAO"].mean()
#        std_reduzida = vaz_red_usi["VAZAO"].std()
#        std_original = vaz_orig_usi["VAZAO"].std()
#        skew_reduzida = skew(vaz_red_usi["VAZAO"], bias=False)
#        skew_original = skew(vaz_orig_usi["VAZAO"], bias=False)
#        print("REDUZIDA: Média =", mean_reduzida, " Desvio Padrão =", std_reduzida, " Assimetria =", skew_reduzida)
#        print("ORIGINAL: Média =", mean_original, " Desvio Padrão =", std_original, " Assimetria =", skew_original)
#        df = pd.DataFrame({ "posto":[usi], 
#                            "estagio":[est],
#                            "media_reduzida":[round(mean_reduzida,2)],
#                            "media_original":[round(mean_original,2)],
#                            "desvio_reduzido":[round(std_reduzida,2)],
#                            "desvio_original":[round(std_original,2)],
#                            })
#        lista_df.append(df)
#
#df_result = pd.concat(lista_df).reset_index(drop = True)
#df_result.to_csv("BKAssimetrico\\estatisticas_Arv_red.csv", index=False)
#
#
#
#printaArvore("BKAssimetrico\\arvoreAssimetrica\\Arvore_reduzida", df_arvore)
#print(df_arvore)