import pandas as pd
import numpy as np

caso = "..\\..\\Mestrado\\2aberturas_ini"
caso = "..\\..\\Mestrado\\teste_wellington"

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
        for j, no in enumerate(caminho):
            matriz[i,j] = df_vazoes.loc[(df_vazoes["NOME_UHE"] == usi) & (df_vazoes["NO"] == no)]["VAZAO"].iloc[0]
    return matriz

def retornaMenorValor(no_foco, dicionario_distancias, Q):
    menor_valor = float('inf')
    for j, no_analisado in enumerate(Q):
        if(no_analisado != no_foco):
            dist = dicionario_distancias[(no_foco, no_analisado)]
            menor_valor = dist if dist < menor_valor else menor_valor
    return menor_valor

def calcular_dist_kantorovich(no_foco, J, Q, dicionario_distancias, dicionarioDeProbabilidades):
    dist_kantorovich = dicionarioDeProbabilidades[no_foco] * retornaMenorValor(no_foco, dicionario_distancias, Q)
    for no_excluido in J:
        dist_kantorovich += dicionarioDeProbabilidades[no_excluido] * retornaMenorValor(no_excluido, dicionario_distancias, Q)
    return dist_kantorovich

dicionario_distancias = {}
#MONTANDO A MATRIZ DE DISTANCIAS ENTRE OS NOS DE TERMINADO ESTAGIO
estagios_estocasticos = df_arvore["PER"].unique()[1:]
numeroCenariosReducao = 2

for est in estagios_estocasticos:
    nos_do_estagio = df_arvore.loc[df_arvore["PER"] == est]["NO"].tolist()
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
                matrizDistancias[i,j] = frobenius_norm
                dicionario_distancias[(no_foco, no_analisado)] = frobenius_norm

    # PASSO 2 -> INICIALIZAR O PROCESSO ITERATIVO. CALCULAR A DISTANCIA DE KANTOROVICH PARA CADA CENARIO E VERICICAR O QUE TEM MENOR PESO

    #CONSIDERANDO J = {}, avaliar o imacto de 
    J = []
    Q = nos_do_estagio
    for iter in range(1,numeroCenariosReducao+1):
            mapa_distancias = {}
            for i, no_foco in enumerate(Q):
                dist_kantorovich = calcular_dist_kantorovich(no_foco, J, Q, dicionario_distancias, dicionarioDeProbabilidades)
                mapa_distancias[no_foco] = dist_kantorovich
                #menor_valor = retornaMenorValor(no_foco, dicionario_distancias, Q)
                #dist_kantorovich = dicionarioDeProbabilidades[no_foco]*menor_valor
                #print("NO: ", no_foco, " menor dist: ", menor_valor, " prob: ", dicionarioDeProbabilidades[no_foco])
                #for no_excluido in J:
                #    menor_valor = retornaMenorValor(no_excluido, dicionario_distancias, Q)
                #    dist_kantorovich += dicionarioDeProbabilidades[no_excluido]*menor_valor
                #    print("no_excluido: ", no_excluido, " menor dist: ", menor_valor, " prob: ", dicionarioDeProbabilidades[no_excluido], "kantorovich: ", dist_kantorovich)
                #mapa_distancias[no_foco] = dist_kantorovich
            key_min_value = min(mapa_distancias, key=mapa_distancias.get)
            min_value = mapa_distancias[key_min_value]
            print("key_min_value: ", key_min_value, " min_value: ", min_value)

            J.append(key_min_value)
            Q.remove(key_min_value)
            print("FIM ITER: ", iter, " J: ", J, " Q: ", Q)


    print(dicionario_distancias)
    print(dicionarioDeProbabilidades)
    print(matrizDistancias)