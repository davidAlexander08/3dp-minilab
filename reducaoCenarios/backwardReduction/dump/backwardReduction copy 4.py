import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from anytree import Node, RenderTree
import time
from joblib import Parallel, delayed, parallel_backend
from numba import jit
from itertools import combinations  # Efficiently generate unique (i, j) pairs

start_time = time.time()

tempo_Total = time.time()

caso = "..\\..\\Mestrado\\caso_1D"
caso = "..\\..\\Mestrado\\caso_2D"
caso = "..\\..\\Mestrado\\caso_construcaoArvore"
caso = "..\\..\\Mestrado\\caso_construcaoArvore_SIN"
#caso = "..\\..\\Mestrado\\caso_construcaoArvore_SIN_2000cen"
caso = "..\\..\\Mestrado\\caso_construcaoArvore_SIN_1000cen"
#caso = "..\\..\\Mestrado\\caso_construcaoArvore_SIN_50cen"
#caso = "..\\..\\Mestrado\\teste_wellington"

arquivo_vazoes = caso+"\\vazao_feixes.csv"
df_vazoes = pd.read_csv(arquivo_vazoes)
print(df_vazoes)
df_vazoes.to_csv("vazoes_estudo.csv")

arquivo_probabilidades = caso+"\\probabilidades_feixes.csv"
df_probs = pd.read_csv(arquivo_probabilidades)
arquivo_estrutura_feixes = caso+"\\arvore_julia.csv"
df_arvore = pd.read_csv(arquivo_estrutura_feixes)
df_arvore["PROB"] = df_probs["PROBABILIDADE"]
df_arvore = df_arvore.drop(columns = "VAZAO")
print(df_arvore)
df_arvore.to_csv("arvore_estudo.csv")

df_arvore_original = df_arvore.copy()




################## FLAG TOLERANCIA PARA EXCLUSAO DE CENARIOS COM BASE NO LIM SUP (MAXIMA DIFF DAS ARVORES) #################
flag_criterio_de_parada_por_tolerancia = 1
########################################################################################################################

##################  ACELERADOR DE CONVERGENCIA, STEP DA EXCLUSAO DE CENARIOS ##############
flag_acelerador_exclusao_cenarios = 0 #Exclui sempre uma % dos cenários juntos
parametro_exclusao_cenarios = 0.1 #1% dos meores cenários para serem excluídos a cara iteração
NumeroIteracoesAcelerador = 50
###########################################################################################

################### CORES PROCESSAMENTO PARALELO ##########################
cores = -1
###################################
numeroCenariosReducao = 2
mapa_reducao_estagio = {
    2:2,
    3:2,
    4:2
}
mapa_tolerancia_estagio = {
    2:0.1,
    3:0.1,
    4:0.1
}













def printaArvore(texto, df_arvore):
    df_arvore.loc[df_arvore["NO_PAI"] == 0, "NO_PAI"] = 1
    #df_arvore.loc[df_arvore["NO_PAI"] == 0, "NO_PAI"] = -1  # You can use any value that is not part of the graph
    G = nx.DiGraph()
    for _, row in df_arvore.iterrows():
        if row['NO_PAI'] != row['NO']:
            G.add_edge(row['NO_PAI'], row['NO'], weight=row['PROB'])
    pos = nx.drawing.nx_pydot.pydot_layout(G, prog='dot')
    plt.figure(figsize=(10, 8))
    nx.draw(G, pos, with_labels=True, node_size=10, node_color='lightblue', font_size=1, font_weight='bold', arrows=True)
    
    #edge_labels = nx.get_edge_attributes(G, 'weight')
    #nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    plt.savefig(texto+".png", format="png", dpi=100, bbox_inches="tight")
    plt.title("Tree Visualization")
    #plt.show()

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

def retornaMenorValor(no_base, no_foco, dicionario_distancias, Q):
    return min(
        dicionario_distancias[(no_foco, no_analisado)] 
        for no_analisado in Q if no_analisado != no_base
    )

def calcular_dist_kantorovich(no_foco, J, Q, dicionario_distancias, dicionarioDeProbabilidades):
    dist_kantorovich = 0
    Exclude_Temp = J + [no_foco]
    #print("CALCULANDO: ", no_foco)
    for no_excluido in Exclude_Temp:
        dist_kantorovich += dicionarioDeProbabilidades[no_excluido] * retornaMenorValor(no_foco, no_excluido, dicionario_distancias, Q)
        #print(f"no_excluido: {no_excluido}, prob: {dicionarioDeProbabilidades[no_excluido]}, menorValor: {retornaMenorValor(no_foco, no_excluido, dicionario_distancias, Q)}")
    return dist_kantorovich


def compute_distance(i, j, matrizFoco, matrizAnalise):
    # Compute Frobenius norm efficiently
    #print("calculnado: ", i, " ", j)
    frobenius_norm = np.linalg.norm(matrizFoco - matrizAnalise, ord='fro')
    return i, j, frobenius_norm

def compute_caminho_probabilidade_matriz(no, df_arvore, df_vazoes):
    caminho = retorna_lista_caminho(no, df_arvore)[:-1]
    matrizAfluencias = retornaMatrizAfluenciasCaminho(caminho, df_vazoes)
    df_arvore_dict = df_arvore.set_index("NO")["PROB"].to_dict()
    prob_no = df_arvore_dict[min(caminho)]
    #prob_no = df_arvore.loc[df_arvore["NO"] == min(caminho)]["PROB"].iloc[0]
    #print("Computando parametros de: ", no)
    return no, caminho, matrizAfluencias, prob_no

dicionario_distancias = {}
#MONTANDO A MATRIZ DE DISTANCIAS ENTRE OS NOS DE TERMINADO ESTAGIO
estagios_estocasticos = df_arvore["PER"].unique()[1:]

#printaArvore("ArvoreInicial", df_arvore_original)
end_time = time.time()
elapsed_time = end_time - start_time  # Calculate elapsed time
print(f"Tempo de Inicialização: {elapsed_time:.4f} seconds")
start_time = time.time()

for est in reversed(estagios_estocasticos):
    nos_do_estagio = df_arvore.loc[(df_arvore["PER"] == est) & (df_arvore["PROB"] != 0.0)]["NO"].tolist()
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
    print(f"Tempo de Parâmetros Iniciais: {elapsed_time:.4f} seconds")
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

    end_time = time.time()
    elapsed_time = end_time - start_time  # Calculate elapsed time
    print(f"Tempo de Matriz Distância: {elapsed_time:.4f} seconds")
    start_time = time.time()
    
    #print(dicionarioDeProbabilidades)
    #print(matrizDistancias)
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
        print(f"NO: {no}, Kantorovich: {dist_kantorovich}, limSup:  {limSup}")
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
            for i, no_foco in enumerate(Q):
                dist_kantorovich = calcular_dist_kantorovich(no_foco, J, Q, dicionario_distancias, dicionarioDeProbabilidades)
                mapa_distancias[no_foco] = dist_kantorovich
                #print(f"NO: {no_foco}, Kantorovich: {dist_kantorovich} Degradacação: {dist_kantorovich/limSup}")

            ##Thread computation
            #with parallel_backend("threading"):  # Uses threads instead of processes
            #    results = Parallel(n_jobs=cores)(
            #        delayed(calcular_dist_kantorovich)(no_foco, J, Q, dicionario_distancias, dicionarioDeProbabilidades)
            #        for no_foco in Q
            #    )
            #mapa_distancias.update(zip(Q, results))


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
                print(" J: ", J)
                print(" Q: ", Q)
            else:
                key_min_value = min(mapa_distancias, key=mapa_distancias.get)
                min_value = mapa_distancias[key_min_value]
                J.append(key_min_value)
                Q.remove(key_min_value)
                erro = min_value/limSup
                print("EST: ", est , " FIM ITER: ", iteracao, " erro: ", erro)
                print(" J: ", J)
            #print("EST: ", est , " FIM ITER: ", iteracao, " J: ", J, " Q: ", Q, " erro: ", erro)                
            end_time = time.time()
            elapsed_time = end_time - start_time  # Calculate elapsed time
            print(f"Tempo Final Iteracao {iteracao}: Tempo {elapsed_time:.4f} seconds")
            start_time = time.time()
            iteracao += 1
    else:
        for iter in range(1,mapa_reducao_estagio[est]+1):
                mapa_distancias = {}
                for i, no_foco in enumerate(Q):
                    dist_kantorovich = calcular_dist_kantorovich(no_foco, J, Q, dicionario_distancias, dicionarioDeProbabilidades)
                    mapa_distancias[no_foco] = dist_kantorovich
                    print(f"NO: {no_foco}, Kantorovich: {dist_kantorovich} Degracação: {dist_kantorovich/limSup}")
                key_min_value = min(mapa_distancias, key=mapa_distancias.get)
                min_value = mapa_distancias[key_min_value]
                J.append(key_min_value)
                Q.remove(key_min_value)
                print("FIM ITER: ", iter, " J: ", J, " Q: ", Q)

    # PASSO I+1, REDISTRIBUIR AS PROBABILIDADES

    mapa_distancias = {}
    for i, no_excluido in enumerate(J):
        #print(caminho)
        no_mais_proximo = retornaNoMaisProximo(no_excluido, no_excluido, dicionario_distancias, Q)

        prob_total_filhos = 0
        filhos_no_proximo = getFilhos(no_mais_proximo, df_arvore)
        filhos = getFilhos(no_excluido, df_arvore)

        total_filhos = np.concatenate((filhos_no_proximo, filhos))
        prob_temporaria_no = {}
        for filho in total_filhos:
            caminho_no_mais_proximo = retorna_lista_caminho(filho, df_arvore)[:-1][-1]
            prob = df_arvore.loc[df_arvore["NO"] == caminho_no_mais_proximo, "PROB"].iloc[0]
            prob_temporaria_no[filho] = prob
            prob_total_filhos += prob
            #print("filho: ", filho, " prob: ", prob, " prob_total_filhos: ", prob_total_filhos)
            
        for filho in total_filhos:
            df_arvore.loc[df_arvore["NO"] == filho, "PROB"] = round(prob_temporaria_no[filho]/prob_total_filhos, 4)


        #print("no_excluido filhos: ", filhos)
        for filho in filhos:
            if(df_arvore.loc[df_arvore["NO"] == filho]["PROB"].iloc[0] != 0):
                df_arvore.loc[df_arvore["NO"] == filho,"NO_PAI"] = no_mais_proximo
        

        
        caminho_no_mais_proximo = retorna_lista_caminho(no_mais_proximo, df_arvore)[:-1]

        probabilidade_no_mais_proximo = df_arvore.loc[df_arvore["NO"] == caminho_no_mais_proximo[-1], "PROB"]
        df_arvore.loc[df_arvore["NO"] == caminho_no_mais_proximo[-1], "PROB"] = round((probabilidade_no_mais_proximo + dicionarioDeProbabilidades[no_excluido]), 4)
        #print("no_excluido: ", no_excluido, " proximidade: ", no_mais_proximo)
        #print("caminho mais proximo: ", caminho_no_mais_proximo)

        caminho = retorna_lista_caminho(no_excluido, df_arvore)[:-1]
        for no_caminho in caminho:
            df_arvore.loc[df_arvore["NO"] == no_caminho, "PROB"] = 0
            df_arvore = df_arvore.loc[df_arvore["NO"] != no_caminho]

    end_time = time.time()
    elapsed_time = end_time - start_time  # Calculate elapsed time
    print(f"Tempo Final Redistribuicao Probabilidades: {elapsed_time:.4f} seconds")
    start_time = time.time()

    #print(dicionarioDeProbabilidades)
    #print(matrizDistancias)
    #print(df_arvore)
    #printaArvore("Arvore_est_"+str(est), df_arvore)





    end_time = time.time()
    elapsed_time = end_time - start_time  # Calculate elapsed time
    print(f"Tempo Calculos Estagio: {est} Tempo: {elapsed_time:.4f} seconds")
    start_time = time.time()


tempo_final = time.time()
elapsed_time = tempo_final - tempo_Total  # Calculate elapsed time
print(f"Tempo Total: {elapsed_time:.4f} seconds")

df_arvore.to_csv("df_arvore_reduzida.csv")
##Estatisticas
for est in df_arvore["PER"].unique():
    nos = df_arvore.loc[df_arvore["PER"] == est]["NO"].unique()
    nos_original = df_arvore_original.loc[df_arvore_original["PER"] == est]["NO"].unique()
    print("NOS ESTAGIO: ", est, " DE: ", len(nos_original), " PARA: ", len(nos))