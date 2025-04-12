import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time
from sklearn.cluster import KMeans
from scipy.spatial.distance import cdist
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.utils.extmath import row_norms, squared_norm, stable_cumsum
import plotly.graph_objects as go
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import pairwise_distances

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
    def __init__(self, n_units, max_iter=100, lr0=10, lrf=0.01, epsilon0=0.1, epsilonf=0.05):
        self.n_units = n_units
        self.max_iter = max_iter
        self.lr0 = lr0
        self.lrf = lrf
        self.epsilon0 = epsilon0
        self.epsilonf = epsilonf

    #def personalEuclidianDistance(self, X, Y): #X, Y=None, Y_norm_squared=None, squared=False,  X_norm_squared=None
    #    XX = row_norms(X, squared=True)[:, np.newaxis]
    #    YY = row_norms(Y, squared=True)[np.newaxis, :]
    #    distances = safe_sparse_dot(X, Y.T, dense_output=True)
    #    distances *= -2
    #    distances += XX
    #    distances += YY
    #    np.maximum(distances, 0, out=distances)
    #    return distances


    def _k_init(self, X, n_clusters, n_local_trials=None):
        """Init n_clusters seeds according to k-means++

        Parameters
        -----------
        X : array or sparse matrix, shape (n_samples, n_features)
            The data to pick seeds for. To avoid memory copy, the input data
            should be double precision (dtype=np.float64).

        n_clusters : integer
            The number of seeds to choose

        x_squared_norms : array, shape (n_samples,)
            Squared Euclidean norm of each data point.

        random_state : numpy.RandomState
            The generator used to initialize the centers.

        n_local_trials : integer, optional
            The number of seeding trials for each center (except the first),
            of which the one reducing inertia the most is greedily chosen.
            Set to None to make the number of trials depend logarithmically
            on the number of seeds (2+log(k)); this is the default.

        Notes
        -----
        Selects initial cluster centers for k-mean clustering in a smart way
        to speed up convergence. see: Arthur, D. and Vassilvitskii, S.
        "k-means++: the advantages of careful seeding". ACM-SIAM symposium
        on Discrete algorithms. 2007

        Version ported from http://www.stanford.edu/~darthur/kMeansppTest.zip,
        which is the implementation used in the aforementioned paper.
        """
        n_samples, n_features = X.shape

        centers = np.empty((n_clusters, n_features), dtype=X.dtype)
        # Set the number of local seeding trials if none is given
        if n_local_trials is None:
            # This is what Arthur/Vassilvitskii tried, but did not report
            # specific results for other than mentioning in the conclusion
            # that it helped.
            n_local_trials = 2 + int(np.log(n_clusters))

        # Pick first center randomly
        center_id = np.random.mtrand._rand.randint(n_samples)
        centers[0,:] = X[center_id, :]

        # Initialize list of closest distances and calculate current potential
        #closest_dist_sq = self.personalEuclidianDistance(centers[0, np.newaxis], X)
        #print(centers[0,:])
        
        closest_dist_sq = []
        for line in range(0,n_samples):
            distancias = np.linalg.norm(np.array(centers[0,:]) - np.array(X[line,:]))
            closest_dist_sq.append(distancias)

        closest_dist_sq = np.array(closest_dist_sq)
        current_pot = closest_dist_sq.sum()
        print(X)
        print("closest_dist_sq: ", closest_dist_sq, " current_pot: ", current_pot, " X[center_id, :]: ", X[center_id, :])
        # Pick the remaining n_clusters-1 points
        for c in range(1, n_clusters):
            list_trials = np.random.random(n_local_trials)
            rand_vals = list_trials * current_pot
            #print("list_trials: ", list_trials, " rand_vals: ", rand_vals)
            soma_probs = stable_cumsum(closest_dist_sq)
            candidate_ids = np.searchsorted(soma_probs, rand_vals)
            #print("soma_probs: ", soma_probs,  " candidate_ids: ", candidate_ids)

            # Compute distances to center candidates
            #print("X[candidate_ids]: ", X[candidate_ids])
            distance_to_candidates = np.zeros((len(candidate_ids), len(X[:, 0])))
            for candidato in range(0, len(candidate_ids)):
                for linhaMatriz in range(0, len(X[:,0])):
                    #print("candidato: ", candidato, " line: ", X[candidate_ids[candidato],:])
                    distance_to_candidates[candidato, linhaMatriz] = np.linalg.norm(np.array(X[candidate_ids[candidato],:]) - np.array(X[linhaMatriz,:]))
            
            
            #distance_to_candidates = self.euclidean_distances(X[candidate_ids], X)
            #print(distance_to_candidates)
            # Decide which candidate is the best
            best_candidate = None
            best_pot = None
            best_dist_sq = None
            for trial in range(n_local_trials):
                # Compute potential when including center candidate
                new_dist_sq = np.minimum(closest_dist_sq, distance_to_candidates[trial,:])
                new_pot = new_dist_sq.sum()
                #print(new_dist_sq)
                #print(new_pot)
                # Store result if it is the best local trial so far
                if (best_candidate is None) or (new_pot < best_pot):
                    best_candidate = candidate_ids[trial]
                    best_pot = new_pot
                    best_dist_sq = new_dist_sq

            #print(rand_vals)
            #print(candidate_ids)
            #print(distance_to_candidates)
            # Permanently add best center candidate found in local tries
            centers[c] = X[best_candidate]
            current_pot = best_pot
            closest_dist_sq = best_dist_sq
        return centers

    def fit(self, data, mapa_linha_posto, no_analise, est):
        ##### PRINT CLUSTERS
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data[:, mapa_linha_posto[275]],
            y=data[:, mapa_linha_posto[288]],
            marker=dict(color='blue', size=8),
            mode="markers",
            name="Points",
            showlegend=True  
        ))
        
        fig.update_layout(
            title='Scater Plot Centroides',
            xaxis_title='m3/s',
            yaxis_title='m3/s'
        )
        text_out = "NeuralGas"

        centros = self._k_init(data, self.n_units)
        #print("centros: ", centros[:,0:10])

        fig.add_trace(go.Scatter(
            x=centros[:, mapa_linha_posto[275]],
            y=centros[:, mapa_linha_posto[288]],
            marker=dict(color='green', size=8),
            mode="markers",
            name="Initial",
            showlegend=True  
        ))

        #indices = np.random.choice(len(data), self.n_units, replace=False)
        #self.units = data[indices].copy()
        #print(indices)
        self.units = centros.copy()
        print("Starting points: ", self.units[:,0:10])
        #exit(1)

        ##### NORMALIZANDO TESTE
        scaler = StandardScaler()
        #data = scaler.fit_transform(data)
        #self.units = scaler.fit_transform(self.units)
        print("data: ", data[:,0:10])
        print("self.units: ", self.units[:,0:10])
        ##### NORMALIZANDO

        units_antigo = self.units.copy()
        flag_teste_convergencia = False
        distancia_convergencia = 9999
        self.lr0 = 10   ## NEIGHBOUR RANGE
        self.lrf = 0.01
        self.epsilon0 = 0.5  ### LEARNING RATE
        self.epsilonf = 0.05
        self.max_iter = 40000
        [n_samples, _] = data.shape
        self.rng = np.random.RandomState()
        for iteration in range(1, self.max_iter):
            lr = self.lr0 * ((self.lrf/self.lr0) ** (iteration/self.max_iter))
            epsilon = self.epsilon0 * ((self.epsilonf/self.epsilon0) ** (iteration/self.max_iter))
            random_index = np.random.randint(0, data.shape[0])
            sample = data[random_index, :]
            print("sample: ", sample)
            mapa_centroid_dist = {}
            for idx_k in range(0,self.n_units):
                distance = np.linalg.norm(self.units[idx_k,:] - sample)
                mapa_centroid_dist[idx_k] = distance
            sorted_centroids = sorted(mapa_centroid_dist.items(), key=lambda item: item[1])
            print(sorted_centroids)
            for order, (idx_k, distance) in enumerate(sorted_centroids):
                adaptation = epsilon * np.exp(-order / lr)
                self.units[idx_k,:] = self.units[idx_k,:] + adaptation*(sample  -  self.units[idx_k,:] )

                ##print(" realizacoes_linha: ", realizacoes_linha, " distance: ", distance)
                #sorted_items = sorted(mapa_linha_distancia.items(), key=lambda item: item[1])
                #for order, (key, distance) in enumerate(sorted_items):
                #    #adaptation = epsilon * np.exp(-order / lr)
                #    adaptation = epsilon * np.exp(-order / lr)
                #    if(adaptation > 0.00001):
                #        self.units[idx_k,:] = self.units[idx_k,:] + adaptation*(sample[key,:]  -  self.units[idx_k,:] )
                #        #print("order: ", order, " key: ", key, " distance: ", distance, " adaptation: ", adaptation, " epsilon: ", epsilon, " lr: ", lr, " dif: ", data[key,0:10]  -  self.units[idx_k,0:10] , " adap: ", adaptation*(data[key,0:10]  -  self.units[idx_k,0:10] ) )
                #        print("order: ", order, " key: ", key, " distance: ", distance, " adaptation: ", adaptation, " epsilon: ", epsilon, " lr: ", lr)
                #    #else:
                    #    print("order: ", order, " key: ", key, " adap menor que 0.000001")
                    #print("rank: ", order, " key: ", key, " distance: ", distance, " self.units: ", self.units[idx_k,:])
                #exit(1)
            if(iteration%1 == 0):
                print("iteration: ", iteration, " lr: ", lr, " epsilon: ", epsilon)
                print(self.units[:,0:10])

            if(iteration == 10):
                break
                #print(scaler.inverse_transform(self.units)[:,0:10])
            #exit(1)
            #for point in data:
            #    distances = np.linalg.norm(self.units - point, axis=1)
            #    #print(distances)
            #    ranking = np.argsort(distances)
            #    for k, rank in enumerate(ranking):
            #        adaptation = lr * np.exp(-k / epsilon)
            #        self.units[rank] += adaptation * (point - self.units[rank])
            #print("iter: ", iteration, " lr: ", lr, " epsilon: ", epsilon, " self.units: ", self.units)

            #if(lr < self.lrf or epsilon < self.epsilonf or iteration == 40000):
            #    break
        #self.units = scaler.inverse_transform(self.units)
        fig.add_trace(go.Scatter(
            x=self.units[:, mapa_linha_posto[275]],
            y=self.units[:, mapa_linha_posto[288]],
            marker=dict(color='red', size=8),
            mode="markers",
            name="Centroides",
            showlegend=True  
        ))
        fig.write_html("saidas\\"+text_out+"\\neuralGas_"+str(est)+"_"+str(no_analise)+'.html', auto_open=False)
        exit(1)

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
        mapa_linha_posto = {}
        for linha, no in enumerate(filhos):  # FIXED: Use enumerate() to track row index
            mapa_linha_no[linha] = no
            prob = df_arvore.loc[df_arvore["NO"] == no]["PROB"].iloc[0]
            for coluna, posto in enumerate(postos):  # FIXED: Same for column index
                vazao = df_vazoes[(df_vazoes["NOME_UHE"] == posto) & (df_vazoes["NO"] == no)]["VAZAO"].iloc[0]
                matriz_valores[linha, coluna] = vazao
                mapa_linha_posto[posto] = coluna

        k = mapa_clusters_estagio[est]
        maximo_iteracoes = 30000
        ng = NeuralGas(n_units=k, max_iter=maximo_iteracoes)
        representatives = ng.fit(matriz_valores, mapa_linha_posto, no_analise, est)
        clusters = ng.predict(matriz_valores)


        print("representatives: ", representatives, " len: ", len(representatives))
        print(clusters)
        new_matrix = np.zeros((len(representatives), len(postos)))
        maior_no = max(df_arvore["NO"].unique())






        for i in range(k):
            novo_no = maior_no + i + 1
            lista_linhas_matriz = np.where(clusters == i)[0]
            lista_nos_cluster = [mapa_linha_no[key] for key in lista_linhas_matriz]
            print("I: ", i , " lista : ", lista_nos_cluster)

            
            ########## WEIGHTED AVERAGE OF CLUSTERS
            matriz_cluster = matriz_valores[lista_linhas_matriz,:]
            save_lines = matriz_cluster*0
            soma_probs = 0
            for indice, no in enumerate(lista_nos_cluster):
                prob = df_arvore.loc[df_arvore["NO"] == no]["PROB"].iloc[0]
                soma_probs += prob
            for indice, no in enumerate(lista_nos_cluster):
                prob = df_arvore.loc[df_arvore["NO"] == no]["PROB"].iloc[0]/soma_probs
                linha = matriz_cluster[indice,:]
                #print("linha: ", linha, " prob: ", prob, " mult: ", linha*prob)
                save_lines[indice,:] = linha*prob  
            novas_realizacoes = np.sum(save_lines, axis=0)
            ########################################

            df_nos_excluidos = df_arvore[df_arvore["NO"].isin(lista_nos_cluster)].reset_index(drop = True)
            df_arvore = df_arvore[~df_arvore["NO"].isin(lista_nos_cluster)]

            prob_novo_no = df_nos_excluidos["PROB"].sum()
            media_probs = df_nos_excluidos["PROB"].mean()
            print("df_nos_excluidos[NO_PAI].unique(): ", df_nos_excluidos["NO_PAI"].unique())
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
    print(df_arvore)
    
    end_time = time.time()
    elapsed_time = end_time - start_time  # Calculate elapsed time
    print(f"Tempo de Exeucao do Neural Gas: {elapsed_time:.4f} seconds")
    start_time = time.time()
    ### COMENTE ESSA LINHA PARA IMPRIMIR TAMBEM NO CADASTRO DE VAZOES OS NOS ELIMINADOS ALEM DO NO RESULTANTE
    df_vazoes = df_vazoes[df_vazoes["NO"].isin(df_arvore["NO"].unique())].reset_index(drop = True)
    print(df_vazoes)
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


