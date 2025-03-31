import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time
from sklearn.cluster import KMeans
from scipy.spatial.distance import cdist

def printaArvore(texto, df_arvore):
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
    plt.savefig(texto+".png", format="png", dpi=100, bbox_inches="tight")
    plt.title("Tree Visualization")
    #plt.show()

def getFilhos(no, df_arvore):
    filhos = df_arvore[df_arvore["NO_PAI"] == no]["NO"].values
    return filhos

def busca_pai(no, df_arvore):
    pai = df_arvore[df_arvore["NO"] == no]["NO_PAI"].values[0]
    return pai





class NeuralGas:
    def __init__(self, n_units, max_iter=100, lr0=0.5, lr_decay=0.99, epsilon0=0.5, epsilon_decay=0.95):
        self.n_units = n_units
        self.max_iter = max_iter
        self.lr0 = lr0
        self.lr_decay = lr_decay
        self.epsilon0 = epsilon0
        self.epsilon_decay = epsilon_decay
        
    def fit(self, data):
        indices = np.random.choice(len(data), self.n_units, replace=False)
        self.units = data[indices].copy()
        #print(indices)
        #print(self.units)
        for iteration in range(self.max_iter):
            data = data[np.random.permutation(data.shape[0])]
            lr = self.lr0 * (self.lr_decay ** iteration)
            epsilon = self.epsilon0 * (self.epsilon_decay ** iteration)
            for point in data:
                distances = np.linalg.norm(self.units - point, axis=1)
                ranking = np.argsort(distances)
                for k, rank in enumerate(ranking):
                    adaptation = lr * np.exp(-k / epsilon)
                    self.units[rank] += adaptation * (point - self.units[rank])
        return self.units


    def predict(self, data):
        """Assign each data point to its nearest unit"""
        if self.units is None:
            raise ValueError("Model not fitted yet. Call fit() first.")
        distances = cdist(data, self.units)
        assignments = np.argmin(distances, axis=1)
        return assignments


def percorreArvoreNeuralGas(no_analise, df_arvore, df_vazoes, mapa_clusters_estagio, postos, Simetrica):

    filhos = getFilhos(no_analise, df_arvore)
    est = df_arvore.loc[(df_arvore["NO"] == no_analise)]["PER"].iloc[0]
    if(len(filhos) > mapa_clusters_estagio[est]):
        matriz_valores = np.zeros((len(filhos), len(postos)))
        mapa_linha_no = {}
        for linha, no in enumerate(filhos):  # FIXED: Use enumerate() to track row index
            mapa_linha_no[linha] = no
            prob = df_arvore.loc[df_arvore["NO"] == no]["PROB"].iloc[0]
            for coluna, posto in enumerate(postos):  # FIXED: Same for column index
                vazao = df_vazoes[(df_vazoes["NOME_UHE"] == posto) & (df_vazoes["NO"] == no)]["VAZAO"].iloc[0]
                matriz_valores[linha, coluna] = vazao
        #print(matriz_valores)

        k = mapa_clusters_estagio[est]

        ng = NeuralGas(n_units=k, max_iter=10000)
        representatives = ng.fit(matriz_valores)
        clusters = ng.predict(matriz_valores)
        #print("representatives: ", representatives, " len: ", len(representatives))
        #print(clusters)
        new_matrix = np.zeros((len(representatives), len(postos)))
        maior_no = max(df_arvore["NO"].unique())
        for i in range(k):
            novo_no = maior_no + i + 1
            lista_linhas_matriz = np.where(clusters == i)[0]
            lista_nos_cluster = [mapa_linha_no[key] for key in lista_linhas_matriz]


            
            ########## WEIGHTED AVERAGE OF CLUSTERS
            matriz_cluster = matriz_valores[lista_linhas_matriz,:]
            save_lines = matriz_cluster*0
            soma_probs = 0
            for i, no in enumerate(lista_nos_cluster):
                prob = df_arvore.loc[df_arvore["NO"] == no]["PROB"].iloc[0]
                soma_probs += prob
            for i, no in enumerate(lista_nos_cluster):
                prob = df_arvore.loc[df_arvore["NO"] == no]["PROB"].iloc[0]/soma_probs
                linha = matriz_cluster[i,:]
                #print("linha: ", linha, " prob: ", prob, " mult: ", linha*prob)
                save_lines[i,:] = linha*prob  
            novas_realizacoes = np.sum(save_lines, axis=0)
            ########################################

            df_nos_excluidos = df_arvore[df_arvore["NO"].isin(lista_nos_cluster)].reset_index(drop = True)
            df_arvore = df_arvore[~df_arvore["NO"].isin(lista_nos_cluster)]

            prob_novo_no = df_nos_excluidos["PROB"].sum()
            media_probs = df_nos_excluidos["PROB"].mean()
            pai_novo_no = df_nos_excluidos["NO_PAI"].unique()[0]
            per_novo_no = df_nos_excluidos["PER"].unique()[0]
            abertura = i+1
            for coluna, posto in enumerate(postos):
                df_vaz = pd.DataFrame({"NOME_UHE":[posto], "NO":[novo_no], "VAZAO":[representatives[i][coluna]]}) #### CLASSIC NEURAL GAS
                #df_vaz = pd.DataFrame({"NOME_UHE":[posto], "NO":[novo_no], "VAZAO":[novas_realizacoes[coluna]]}) #### CLUSTER NEURAL GAS, UTILIZA A MEDIA PONDERADA DOS ELEMENTOS DO CLUSTER
                df_vazoes = pd.concat([df_vazoes, df_vaz]).reset_index(drop = True)
            ### COMENTE ESSA LINHA PARA IMPRIMIR TAMBEM NO CADASTRO DE VAZOES OS NOS ELIMINADOS ALEM DO NO RESULTANTE
            df_vazoes = df_vazoes[~df_vazoes["NO"].isin(lista_nos_cluster)] 

            df_novo_no = pd.DataFrame({"NO_PAI":[pai_novo_no], "NO":[novo_no], "Abertura":[abertura], "PER":[per_novo_no], "PROB":[prob_novo_no]})
            novos_filhos = df_arvore[(df_arvore["NO_PAI"].isin(df_nos_excluidos["NO"].tolist()))].reset_index(drop = True)
            #Repassa probabilidade para frente
            prob_soma = 0
            for idx, row in df_nos_excluidos.iterrows():
                no_excluido = row.NO
                filhos = df_arvore.loc[(df_arvore["NO_PAI"] == no_excluido)].reset_index(drop = True)["NO"].tolist()
                for filho in filhos:
                    prob_old_pai = df_nos_excluidos.loc[df_nos_excluidos["NO"] == no_excluido]["PROB"].iloc[0]
                    df_arvore.loc[df_arvore["NO"] == filho, "PROB"] = prob_old_pai
                    prob_soma += prob_old_pai

            for idx, row in df_nos_excluidos.iterrows():
                no_excluido = row.NO
                filhos = df_arvore.loc[(df_arvore["NO_PAI"] == no_excluido)].reset_index(drop = True)["NO"].tolist()
                for filho in filhos:
                    df_arvore.loc[df_arvore["NO"] == filho, "NO_PAI"] = novo_no
                    df_arvore.loc[df_arvore["NO"] == filho, "PROB"] = round(df_arvore.loc[df_arvore["NO"] == filho, "PROB"]/prob_soma,4)
            df_arvore = pd.concat([df_arvore, df_novo_no]).reset_index(drop = True)
            
    return (df_arvore, df_vazoes)






def reducaoArvoreNeuralGas(mapa_clusters_estagio, df_vazoes, df_arvore, Simetrica):
    np.random.seed(42)
    start_time = time.time()
    tempo_Total = time.time()
    estagios = df_arvore["PER"].unique()
    estagios = sorted(estagios, reverse=False)[:-1]#[1:]
    postos = df_vazoes["NOME_UHE"].unique()
    postos = sorted(postos, reverse=False)
    for est in estagios:
        nos_estagio = df_arvore.loc[(df_arvore["PER"] == est)]["NO"].tolist()
        for no_cluster in nos_estagio:
            df_arvore, df_vazoes = percorreArvoreNeuralGas(no_cluster, df_arvore, df_vazoes, mapa_clusters_estagio, postos, Simetrica)
    df_arvore.loc[df_arvore["NO"] == 1, "NO_PAI"] = 0
    #print(df_arvore)
    #print(df_vazoes)
    end_time = time.time()
    elapsed_time = end_time - start_time  # Calculate elapsed time
    print(f"Tempo de Exeucao do Neural Gas: {elapsed_time:.4f} seconds")
    start_time = time.time()
    ### COMENTE ESSA LINHA PARA IMPRIMIR TAMBEM NO CADASTRO DE VAZOES OS NOS ELIMINADOS ALEM DO NO RESULTANTE
    df_vazoes = df_vazoes[df_vazoes["NO"].isin(df_arvore["NO"].unique())].reset_index(drop = True)
    return (df_arvore, df_vazoes)




#caso = "..\\casosTestesUnitarios\\3Estagios\\3AberturasAssim\\Pente_GVZP"
#mapa_aberturas_estagio = {1:3,    2:3}
#arquivo_vazoes = caso+"\\cenarios.csv"
#df_vazoes_original = pd.read_csv(arquivo_vazoes)
#arquivo_estrutura_feixes = caso+"\\arvore.csv"
#df_arvore_original = pd.read_csv(arquivo_estrutura_feixes)
#print(df_arvore_original)
#
#
#Simetrica = False
#df_arvore, df_vazoes = reducaoArvoreNeuralGas(mapa_aberturas_estagio, df_vazoes_original, df_arvore_original, Simetrica)


