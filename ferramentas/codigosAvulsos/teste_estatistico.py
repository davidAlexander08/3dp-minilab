import numpy as np
import pandas as pd
from scipy.stats import wasserstein_distance
from scipy.stats import ksone
from scipy.stats import ks_2samp
import plotly.graph_objects as go
from scipy.stats import chisquare
from scipy.stats import mannwhitneyu

def empirical_cdf(realizations, probabilities):
    """Calcula a CDF empírica a partir das realizações e probabilidades."""
    sorted_indices = np.argsort(realizations)
    sorted_realizations = np.array(realizations)[sorted_indices]
    sorted_probabilities = np.array(probabilities)[sorted_indices]
    cdf = np.cumsum(sorted_probabilities)
    return sorted_realizations, cdf

def ks_statistic(real1, prob1, real2, prob2):
    """Calcula o KS Statistic para duas distribuições discretas de tamanhos diferentes."""
    x1, cdf1 = empirical_cdf(real1, prob1)
    x2, cdf2 = empirical_cdf(real2, prob2)
    unique_values = np.unique(np.concatenate([x1, x2]))
    cdf1_interp = np.interp(unique_values, x1, cdf1, left=0, right=None)
    cdf2_interp = np.interp(unique_values, x2, cdf2, left=None, right=None)
    ks_stat = np.max(np.abs(cdf1_interp - cdf2_interp))
# Plot CDFs using Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=unique_values, y=cdf1_interp, mode='lines', name='CDF1', line=dict(color='blue', shape='hv')))
    fig.add_trace(go.Scatter(x=unique_values, y=cdf2_interp, mode='lines', name='CDF2', line=dict(color='red', shape='hv')))
    fig.update_layout(
        title='Empirical CDFs and KS Statistic',
        xaxis_title='Value',
        yaxis_title='CDF',
        showlegend=True
    )
    #fig.show()
    return ks_stat, cdf1_interp, cdf2_interp

def monte_carlo_p_value(real1, prob1, real2, prob2, n_permutations=1000):
    """Calcula o p-valor do KS Test para distribuições discretas com permutações."""
    # Calculando o KS Statistic observado
    D_obs, cdf1_interp, cdf2_interp = ks_statistic(real1, prob1, real2, prob2)
    #D_obs, _ = ks_2samp(real1, real2)

    # Contador de quantas vezes a distância das permutações é maior ou igual à observada
    N = 1000
    count = 0
    pooled_data = np.concatenate((real1, real2))
    pooled_prob = np.concatenate((prob1, prob2))
    
    # Normalize the pooled probabilities
    pooled_prob = pooled_prob / np.sum(pooled_prob)
    for _ in range(N):
        # Resample with weighted probabilities
        #sim_sample1 = np.random.choice(real1, size=len(pooled_data), p=prob1 / np.sum(prob1), replace=True)
        #sim_sample2 = np.random.choice(real2, size=len(pooled_data), p=prob2 / np.sum(prob2), replace=True)
        sim_sample1 = np.random.choice(cdf1_interp, size=len(pooled_data), replace=True)
        sim_sample2 = np.random.choice(cdf2_interp, size=len(pooled_data), replace=True)
        #print(sim_sample1)
        D_i, _ = ks_2samp(sim_sample1, sim_sample2)
        #D_i = ks_statistic(sim_sample1, prob1, sim_sample2, prob2)
        if D_i >= D_obs:
            count += 1
    # Estimar o p-valor
    p_value = count / N
    return D_obs, p_value


def wasserstein_test_discrete(values1, probs1, values2, probs2):
    """
    Compute the Wasserstein distance between two discrete distributions.

    Parameters:
        values1 (list or np.array): Values of the first distribution.
        probs1 (list or np.array): Probabilities corresponding to values1.
        values2 (list or np.array): Values of the second distribution.
        probs2 (list or np.array): Probabilities corresponding to values2.

    Returns:
        wasserstein_dist (float): The Wasserstein distance between the two distributions.
    """
    # Normalize probabilities to ensure they sum to 1
    probs1 = np.array(probs1) / np.sum(probs1)
    probs2 = np.array(probs2) / np.sum(probs2)

    # Compute the Wasserstein distance
    wasserstein_dist = wasserstein_distance(values1, values2, probs1, probs2)

    return wasserstein_dist

def wasserstein_discrete(valores1, probs1, valores2, probs2):
    # Create ordered unique support points
    valores_unicos = np.sort(np.unique(np.concatenate((valores1, valores2))))

    # Compute cumulative distribution functions (CDFs)
    cdf1, cdf2 = [], []
    acum1, acum2 = 0, 0
    for v in valores_unicos:
        if v in valores1:
            acum1 += probs1[np.where(valores1 == v)[0][0]]
        if v in valores2:
            acum2 += probs2[np.where(valores2 == v)[0][0]]
        cdf1.append(acum1)
        cdf2.append(acum2)

    # Compute Wasserstein distance
    wasserstein_dist = np.sum(np.abs(np.array(cdf1) - np.array(cdf2)) * np.diff(np.append(valores_unicos, valores_unicos[-1])))
    return wasserstein_dist

#Estágio 4
df_arvore_original = pd.read_csv("arvore_estudo.csv")
#print(df_arvore_original)
df_vazoes = pd.read_csv("vazoes_estudo.csv")
#print(df_vazoes)


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


#usina = 17
usina = 156
usina = 275
tipo = "ENAAgregado\\"
#tipo = "VazaoIncrementalMultidimensional\\"
casos = ["Arvore1", "Arvore2", "Arvore3", "Arvore4", "Arvore5", "Arvore6"]
#casos = ["Arvore6"]
lista_df_final = []
for caso in casos:
    df_arvore_reduzida = pd.read_csv(tipo+caso+"\\df_arvore_reduzida.csv")
    estagios = [2,3,4]
    D_tot = 0
    for est in estagios:
        lista_original = []
        prob_original = []
        lista_red = []
        prob_red = []
        df_orig_est = df_arvore_original.loc[(df_arvore_original["PER"] == est)].reset_index(drop = True)
        for no in df_orig_est["NO"].unique():
            prob = 1
            lista_caminho = retorna_lista_caminho(no, df_arvore_original)[:-1]
            for elemento in lista_caminho:
                prob_elemento = df_arvore_original.loc[(df_arvore_original["NO"] == elemento)]["PROB"].iloc[0]
                prob = prob*prob_elemento
            vazao = df_vazoes.loc[(df_vazoes["NOME_UHE"] == usina) & (df_vazoes["NO"] == no)].reset_index(drop = True)["VAZAO"].iloc[0]
            lista_original.append(vazao)
            prob_original.append(prob)    
        
        df_red_est = df_arvore_reduzida.loc[(df_arvore_reduzida["PER"] == est)].reset_index(drop = True)
        for no in df_red_est["NO"].unique():
            prob = 1
            lista_caminho = retorna_lista_caminho(no, df_arvore_reduzida)[:-1]
            for elemento in lista_caminho:
                prob_elemento = df_arvore_reduzida.loc[(df_arvore_reduzida["NO"] == elemento)]["PROB"].iloc[0]
                prob = prob*prob_elemento
            vazao = df_vazoes.loc[(df_vazoes["NOME_UHE"] == usina) & (df_vazoes["NO"] == no)].reset_index(drop = True)["VAZAO"].iloc[0]
            lista_red.append(vazao)
            prob_red.append(prob)   
        #D_tot += ks_dist[0]
        #wasserstein_scipy = wasserstein_distance(lista_original, lista_red, prob_original, prob_red)
        #wasserstein_scipy = wasserstein_test_discrete(lista_original, prob_original, lista_red, prob_red)
        #ks_stat, p_value = discrete_ks_test(lista_original, prob_original, lista_red, prob_red)
        
        #alpha = 0.05  # Significance level
        #Passou = "Diferentes"
        #if p_value < alpha:
        #    Passou = "Diferentes"
        #else:
        #    Passou = "Aprovado"
        #print(f"Usi: {usina} Est: {est} Caso: {caso} Distância KS: {ks_stat} P:{p_value} Passou: {Passou}")

        ks_stat, p_value = monte_carlo_p_value(lista_original, prob_original, lista_red, prob_red)
        print(f"Est {est} Arvore {caso} KS Statistic: {ks_stat}, P-value: {p_value}")
        u_stat, p_value = mannwhitneyu(lista_original, lista_red, alternative='two-sided')

        print(f"U-statistic: {u_stat}, p-value: {p_value}")

        #print(f"Est: {est} Caso: {caso} Wasserstein Distance: {wasserstein_scipy}")
        #D_tot += wasserstein_scipy
        #lista_df_final.append(pd.DataFrame({"Tipo":{tipo},"Arv":{caso}, "est":[est], "dist"[]}))
    #print(f"Tipo: {tipo} Caso: {caso}, Soma: {D_tot}")





# Exemplo de uso
#valores1 = np.array([1, 2, 3, 4])
#probs1 = np.array([0.1, 0.3, 0.4, 0.2])  # Soma = 1

#valores2 = np.array([1, 2, 3, 4])
#probs2 = np.array([0.1, 0.27, 0.33, 0.2])  # Soma = 1

#ks_dist = kolmogorov_smirnov_discreto(valores1, probs1, valores2, probs2)
#print(f"Distância KS: {ks_dist}")