import numpy as np
import pandas as pd
from scipy.stats import wasserstein_distance
from scipy.stats import ksone
from scipy.stats import ks_2samp
import plotly.graph_objects as go
from scipy.stats import chisquare
from scipy.stats import mannwhitneyu
from statsmodels.stats.weightstats import DescrStatsW
import plotly.graph_objects as go
from scipy.stats import linregress
from sklearn.metrics import r2_score
from plotly.subplots import make_subplots
import math
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


# Function to calculate weighted mean
def weighted_mean(data, weights):
    return np.sum(weights * data) 

# Function to calculate weighted variance
def weighted_variance(data, weights):
    mean = weighted_mean(data, weights)
    variance = np.sum(weights * (data - mean)**2) 
    return variance

# Function to calculate weighted covariance between two datasets
def weighted_covariance(data_x, data_y, weights):
    mean_x = np.average(data_x, weights=weights)
    mean_y = np.average(data_y, weights=weights)
    covariance = np.sum(weights * (data_x - mean_x) * (data_y - mean_y)) 
    return covariance

def weighted_correlation(data_x, data_y, weights):
    covariance = weighted_covariance(data_x, data_y, weights)
    var_x = weighted_variance(data_x, weights)
    var_y = weighted_variance(data_y, weights)
    correlation = covariance / np.sqrt(var_x * var_y)
    return correlation


camino_caso_orig = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\Capitulo_5\\caso_mini_500Cen_cluster_semanais"

df_arvore_original = pd.read_csv(camino_caso_orig+"\\arvore.csv")
#print(df_arvore_original)
df_vazoes = pd.read_csv(camino_caso_orig+"\\cenarios.csv")
#print(df_vazoes)
tipo = "avaliaArvores\\A_125_2_2_Teste\\"
#tipo = "VazaoIncrementalMultidimensional\\"
mapa_casos = {
    "BKAssimetrico":"Redução Regressiva",
    "KMeansAssimetricoProb":"K-Means Assimetrico", 
    "KMeansSimetricoProbQuad":"K-Means Simetrico", 
    "NeuralGas":"NeuralGas"
}
casos = ["BKAssimetrico", "KMeansAssimetricoProb", "KMeansSimetricoProbQuad", "NeuralGas"]
#casos = ["Arvore6"]
lista_df_final = []
usinas = df_vazoes["NOME_UHE"].unique()


print(len(usinas))
print(usinas)
#usinas = [17, 275, 266, 1] #, 275, 266, 1, 49, 57, 123, 12, 205, 121
#usinas = [66,	45,	46,	285,	292,	275,	172,	176,	6,	169,	33,	74,	75,	40,	25,	42,	39,	229,	178,
#                43,	38,	227,	37,	17,	271,	47,	270,	24,	209,	31,	211,	215,	34,	204,	1,	18,	126,	291,
#                61,	7,	247,	294,	49,	57,	123,	12,	205,	121]
fig = make_subplots(rows=4, cols=2, subplot_titles=(" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "))
#fig = make_subplots(rows=6, cols=3, subplot_titles=([" "] * 18))  # 6x3 grid

linha = 1
coluna = 1
contador = 0
for caso in mapa_casos:
    caminho_red = camino_caso_orig+"\\"+tipo+"\\"+caso+"\\"
    df_arvore_reduzida = pd.read_csv(caminho_red+"arvore.csv")
    df_vazoes_reduzida = pd.read_csv(caminho_red+"cenarios.csv")
    #estagios = [2,3,4]
    #estagios = [4,3,2]
    estagios = [3,2]
    for est in estagios:
        prob_original = []
        prob_red = []
        df_orig_est = df_arvore_original.loc[(df_arvore_original["PER"] == est)].reset_index(drop = True)
        for no in df_orig_est["NO"].unique():
            prob = 1
            lista_caminho = retorna_lista_caminho(no, df_arvore_original)[:-1]
            for elemento in lista_caminho:
                prob_elemento = df_arvore_original.loc[(df_arvore_original["NO"] == elemento)]["PROB"].iloc[0]
                prob = prob*prob_elemento
            prob_original.append(prob)    
        
        df_red_est = df_arvore_reduzida.loc[(df_arvore_reduzida["PER"] == est)].reset_index(drop = True)
        for no in df_red_est["NO"].unique():
            prob = 1
            lista_caminho = retorna_lista_caminho(no, df_arvore_reduzida)[:-1]
            for elemento in lista_caminho:
                prob_elemento = df_arvore_reduzida.loc[(df_arvore_reduzida["NO"] == elemento)]["PROB"].iloc[0]
                prob = prob*prob_elemento
            prob_red.append(prob)   
        prob_original = prob_original / np.sum(prob_original)
        prob_red = prob_red / np.sum(prob_red)
        dict_atributos_original = {}
        dict_atributos_reduzida = {}
        for usi in usinas:
            lista_original = []
            lista_red = []
            for no in df_orig_est["NO"].unique():
                vazao = df_vazoes.loc[(df_vazoes["NOME_UHE"] == usi) & (df_vazoes["NO"] == no)].reset_index(drop = True)["VAZAO"].iloc[0]
                lista_original.append(vazao)            
            for no in df_red_est["NO"].unique():
                vazao = df_vazoes_reduzida.loc[(df_vazoes_reduzida["NOME_UHE"] == usi) & (df_vazoes_reduzida["NO"] == no)].reset_index(drop = True)["VAZAO"].iloc[0]
                lista_red.append(vazao)
            lista_original = np.array(lista_original)
            lista_red = np.array(lista_red)
            dict_atributos_original[usi] = lista_original
            dict_atributos_reduzida[usi] = lista_red

        # Initialize dictionaries for storing correlations
        dicionario_correlacao_original = {}
        dicionario_correlacao_reduzida = {}
        # Calculate correlation between all pairs of usinas
        lista_correl_orig = []
        lista_correl_red = []
        for i, usi_x in enumerate(usinas):
            for j, usi_y in enumerate(usinas):
                if i < j:  # Ensure only the upper triangular part is considered
                    try:
                        
                        corr_orig = weighted_correlation(dict_atributos_original[usi_x], dict_atributos_original[usi_y], prob_original)
                        
                        corr_red = weighted_correlation(dict_atributos_reduzida[usi_x], dict_atributos_reduzida[usi_y], prob_red)
                        dicionario_correlacao_original[(usi_x, usi_y)] = corr_orig
                        dicionario_correlacao_reduzida[(usi_x, usi_y)] = corr_red
                        #if( abs(corr_orig - corr_red) > 0.1 or math.isnan(corr_orig) or math.isnan(corr_red)):
                        #    print("usi_x: ", usi_x, " usi_y: ", usi_y, " corr_orig: ", corr_orig, " corr_red: ", corr_red)
                        lista_correl_orig.append(corr_orig)
                        lista_correl_red.append(corr_red)
                    except Exception as e:
                        print(f"Error calculating correlation for {usi_x} and {usi_y}: {e}")

        print(len(lista_correl_orig))
        print(len(lista_correl_red))
        lista_correl_orig = [x for x in lista_correl_orig if not math.isnan(x)]
        lista_correl_red =  [x for x in lista_correl_red if not math.isnan(x)]
        # Compute R^2 using linear regression
        slope, intercept, r_value, p_value, std_err = linregress(lista_correl_orig, lista_correl_red)
        #print(slope)
        #print(intercept)
        #print(r_value)
        #print(r_value**2)
        #print(p_value)
        #print(std_err)
        r_squared = r_value**2
        print("R-squared 1:", r_squared)
        r_squared = r2_score(lista_correl_orig, lista_correl_red)
        print("R-squared 2:", r_squared)
        print(len(lista_correl_orig))
        print(len(lista_correl_red))
        #print(lista_correl_orig)
        #print(lista_correl_red)
        fig.add_trace(go.Scatter(
            x=lista_correl_orig, 
            y=lista_correl_red, 
            mode='markers',
            name=f' {mapa_casos[caso]} {str(est)} (R² = {r_squared:.2f})',
            showlegend=False,
            marker=dict(size=10, color='blue')
        ), row=linha, col=coluna)

        # Add line of best fit
        fig.add_trace(go.Scatter(
            x=lista_correl_orig, 
            y=slope * np.array(lista_correl_orig) + intercept, 
            mode='lines', 
            line=dict(color='red', width=2),
            showlegend=False
        ), row=linha, col=coluna)

        # Add R² annotation
        #axis_index = (linha - 1) * 3 + coluna  # Correct axis index for 6x3 grid
        axis_index = (linha - 1) * 2 + coluna  # Correct axis index for 6x3 grid
        fig.add_annotation(
            x=1.0,  # X position (relative to subplot domain)
            y=1.0,  # Y position (relative to subplot domain)
            xref=f"x{axis_index}",  # Dynamic x-axis reference
            yref=f"y{axis_index}",  # Dynamic y-axis reference
            text=f"R² = {r_squared:.2f}",
            showarrow=False,
            font=dict(size=20, color="black"),
            align="right"
        )


        titulo =  "Caso: " + mapa_casos[caso] + " Est: "+str(est)
        fig.layout.annotations[contador].update(text=titulo, font=dict(size=20)) 
        contador += 1
        #print("linha: ", linha, " coluna: ", coluna, " anotation: ", contador, " axis_index: ", axis_index)
        coluna = coluna + 1
        if(coluna == 3):
            coluna = 1
            linha = linha + 1

        print(f" Caso {mapa_casos[caso]} Est {est} R²: {r_squared:.2f}")
        # Print the results
        #print("ORIGINAL: ")
        #print(dicionario_correlacao_original)
        #print("REDUZIDA")
        #print(dicionario_correlacao_reduzida)
    # Customize layout
    fig.update_layout(
        title="Correlações Árvore Original x Construída",
        title_font=dict(size=24, family="Arial", color="black"),
        xaxis_title="Correl. Orig.",
        yaxis_title="Correl. Red.",
        font=dict(size=20), 
        xaxis=dict(title_font=dict(size=20)),  
        yaxis=dict(title_font=dict(size=20)),
        showlegend=False
    )
fig.write_html(camino_caso_orig+"\\"+tipo+tipo.split("\\")[0]+"_correlacaoEspacialArvores.html")
    # Print R² value





