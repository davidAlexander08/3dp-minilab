import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from anytree import Node, RenderTree

caso = "..\\..\\Mestrado\\caso_1D"
caso = "..\\..\\Mestrado\\caso_2D"
caso = "..\\..\\Mestrado\\caso_construcaoArvore"
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
    usinas = df_vazoes["NOME_UHE"].unique()
    matriz = np.zeros((len(usinas), len(caminho)))
    for i, usi in enumerate(usinas):
        for j, no in enumerate(reversed(caminho)):
            matriz[i,j] = df_vazoes.loc[(df_vazoes["NOME_UHE"] == usi) & (df_vazoes["NO"] == no)]["VAZAO"].iloc[0]
    return matriz

def retornaMenorValor(no_base, no_foco, dicionario_distancias, Q):
    menor_valor = float('inf')
    for j, no_analisado in enumerate(Q):
        if(no_analisado != no_base):
            dist = dicionario_distancias[(no_foco, no_analisado)]
            menor_valor = dist if dist < menor_valor else menor_valor
    return menor_valor
    
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

def calcular_dist_kantorovich(no_foco, J, Q, dicionario_distancias, dicionarioDeProbabilidades):
    print(f"NO: {no_foco}, prob: {dicionarioDeProbabilidades[no_foco]}, menorValor: {retornaMenorValor(no_foco, no_foco, dicionario_distancias, Q)}")
    dist_kantorovich = dicionarioDeProbabilidades[no_foco] * retornaMenorValor(no_foco, no_foco, dicionario_distancias, Q)
    for no_excluido in J:
        dist_kantorovich += dicionarioDeProbabilidades[no_excluido] * retornaMenorValor(no_foco, no_excluido, dicionario_distancias, Q)
        print(f"no_excluido: {no_excluido}, prob: {dicionarioDeProbabilidades[no_excluido]}, menorValor: {retornaMenorValor(no_foco, no_excluido, dicionario_distancias, Q)}")
    return dist_kantorovich

dicionario_distancias = {}
#MONTANDO A MATRIZ DE DISTANCIAS ENTRE OS NOS DE TERMINADO ESTAGIO
estagios_estocasticos = df_arvore["PER"].unique()[1:]
numeroCenariosReducao = 2

for est in reversed(estagios_estocasticos):
    nos_do_estagio = df_arvore.loc[(df_arvore["PER"] == est) & (df_arvore["PROB"] != 0.0)]["NO"].tolist()
    matrizDistancias = np.zeros((len(nos_do_estagio), len(nos_do_estagio)))
    dicionarioDeProbabilidades = {}
    #print(nos_do_estagio)
    #PASSO 1 -> MONTAR MATRIZ DE DISTANCIAS ENTRE OS CENARIOS
    for i, no_foco in enumerate(nos_do_estagio):
        caminho = retorna_lista_caminho(no_foco, df_arvore)[:-1]
        #print("caminho no_foco: ", caminho)
        matrizAfluenciasFoco = retornaMatrizAfluenciasCaminho(caminho, df_vazoes)
        #print(matrizAfluenciasFoco)
        prob = df_arvore.loc[df_arvore["NO"] == min(caminho)]["PROB"]
        dicionarioDeProbabilidades[no_foco] = prob.iloc[0]
        for j, no_analisado in enumerate(nos_do_estagio):
            if(no_analisado != no_foco):
                caminho = retorna_lista_caminho(no_analisado, df_arvore)[:-1]
                #print("caminho no_analisado: ", caminho)
                matrizAfluenciasAnalise = retornaMatrizAfluenciasCaminho(caminho, df_vazoes)
                #print(matrizAfluenciasAnalise)
                #UTILIZANDO FROBENIUS_NORM PARA DISTANCIA ENTRE AS MATRIZES, DISTANCIA EUCLIDIANA
                frobenius_norm = np.linalg.norm(matrizAfluenciasFoco - matrizAfluenciasAnalise)
                #print(matrizAfluenciasFoco - matrizAfluenciasAnalise)
                #print("matrizAfluenciasFoco: ", matrizAfluenciasFoco, " matrizAfluenciasAnalise: ", matrizAfluenciasAnalise, " frobenius_norm: ", frobenius_norm)
                matrizDistancias[i,j] = frobenius_norm
                dicionario_distancias[(no_foco, no_analisado)] = frobenius_norm

    # PASSO 2 -> INICIALIZAR O PROCESSO ITERATIVO. CALCULAR A DISTANCIA DE KANTOROVICH PARA CADA CENARIO E VERICICAR O QUE TEM MENOR PESO
    print(dicionarioDeProbabilidades)
    print(matrizDistancias)
    #CONSIDERANDO J = {}, avaliar o imacto de 
    J = []
    Q = nos_do_estagio
    for iter in range(1,numeroCenariosReducao+1):
            mapa_distancias = {}
            for i, no_foco in enumerate(Q):
                dist_kantorovich = calcular_dist_kantorovich(no_foco, J, Q, dicionario_distancias, dicionarioDeProbabilidades)
                mapa_distancias[no_foco] = dist_kantorovich
                print(f"NO: {no_foco}, Kantorovich: {dist_kantorovich}")
            key_min_value = min(mapa_distancias, key=mapa_distancias.get)
            min_value = mapa_distancias[key_min_value]
            J.append(key_min_value)
            Q.remove(key_min_value)
            print("FIM ITER: ", iter, " J: ", J, " Q: ", Q)



    # PASSO I+1, REDISTRIBUIR AS PROBABILIDADES
    mapa_distancias = {}
    for i, no_excluido in enumerate(J):


        print(caminho)
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
            print("filho: ", filho, " prob: ", prob, " prob_total_filhos: ", prob_total_filhos)
            
        for filho in total_filhos:
            df_arvore.loc[df_arvore["NO"] == filho, "PROB"] = round(prob_temporaria_no[filho]/prob_total_filhos, 4)


        print("no_excluido filhos: ", filhos)
        for filho in filhos:
            if(df_arvore.loc[df_arvore["NO"] == filho]["PROB"].iloc[0] != 0):
                df_arvore.loc[df_arvore["NO"] == filho,"NO_PAI"] = no_mais_proximo
        

        
        caminho_no_mais_proximo = retorna_lista_caminho(no_mais_proximo, df_arvore)[:-1]

        df_arvore.loc[df_arvore["NO"] == caminho_no_mais_proximo[-1], "PROB"] = round((dicionarioDeProbabilidades[no_mais_proximo] + dicionarioDeProbabilidades[no_excluido]), 4)
        print("no_excluido: ", no_excluido, " proximidade: ", no_mais_proximo)
        print("caminho mais proximo: ", caminho_no_mais_proximo)

        caminho = retorna_lista_caminho(no_excluido, df_arvore)[:-1]
        for no_caminho in caminho:
            df_arvore.loc[df_arvore["NO"] == no_caminho, "PROB"] = 0
            df_arvore = df_arvore.loc[df_arvore["NO"] != no_caminho]
            

    #print(dicionarioDeProbabilidades)
    #print(matrizDistancias)
    print(df_arvore)




# Create a directed graph
G = nx.DiGraph()

# Add edges to the graph
for _, row in df_arvore.iterrows():
    G.add_edge(row['NO_PAI'], row['NO'], weight=row['PROB'])

# Use pydot_layout for a hierarchical tree layout
pos = nx.drawing.nx_pydot.pydot_layout(G, prog='dot')

# Plot the graph
plt.figure(figsize=(10, 8))
nx.draw(G, pos, with_labels=True, node_size=2000, node_color='lightblue', font_size=10, font_weight='bold', arrows=True)

# Draw edge labels (probabilities)
edge_labels = nx.get_edge_attributes(G, 'weight')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

# Show the plot
plt.title("Tree Visualization")
plt.show()
