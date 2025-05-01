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
pasta_arvores = "\\avaliaArvoresRepresentativo"
caminho_pente = "\\Pente"
df_arvore_original = pd.read_csv(camino_caso_orig+pasta_arvores+caminho_pente+"\\arvore.csv")
df_vazoes = pd.read_csv(camino_caso_orig+pasta_arvores+caminho_pente+"\\cenarios.csv")

analises = [("A_125_2_2",3), ("A_125_2_2",2), ("A_50_5_2",2), ("A_25_10_2",2) ]
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
#fig = make_subplots(rows=6, cols=3, subplot_titles=([" "] * 18))  # 6x3 grid
def truncate_to_2_decimals(x):
    return math.floor(x * 100) / 100
#usinas = [271, 285, 6]
for caso in mapa_casos:

    fig = make_subplots(rows=2, cols=2, subplot_titles=(" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "))
    linha = 1
    coluna = 1
    contador = 0
    for analise in analises:
        caminho_red = camino_caso_orig+"\\"+analise[0]+"\\"+caso+"\\"
        df_arvore_reduzida = pd.read_csv(camino_caso_orig+pasta_arvores+"\\"+analise[0]+"\\"+caso+"\\arvore.csv")
        df_vazoes_reduzida = pd.read_csv(camino_caso_orig+pasta_arvores+"\\"+analise[0]+"\\"+caso+"\\cenarios.csv")

        prob_original = []
        prob_red = []
        df_orig_est = df_arvore_original.loc[(df_arvore_original["PER"] == analise[1])].reset_index(drop = True)
        for no in df_orig_est["NO"].unique():
            prob = 1
            lista_caminho = retorna_lista_caminho(no, df_arvore_original)[:-1]
            for elemento in lista_caminho:
                prob_elemento = df_arvore_original.loc[(df_arvore_original["NO"] == elemento)]["PROB"].iloc[0]
                prob = prob*prob_elemento
            prob_original.append(prob)    
        
        df_red_est = df_arvore_reduzida.loc[(df_arvore_reduzida["PER"] == analise[1])].reset_index(drop = True)
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
        mapa_correl_orig_usi = {}
        mapa_correl_red_usi = {}
        lista_correl_orig = []
        lista_correl_red = []
        for i, usi_x in enumerate(usinas):
            mapa_correl_orig_usi[usi_x] = []
            mapa_correl_red_usi[usi_x] = []
            for j, usi_y in enumerate(usinas):
                #if i < j:  # Ensure only the upper triangular part is considered
                try:
                    
                    corr_orig = weighted_correlation(dict_atributos_original[usi_x], dict_atributos_original[usi_y], prob_original)
                    
                    corr_red = weighted_correlation(dict_atributos_reduzida[usi_x], dict_atributos_reduzida[usi_y], prob_red)
                    dicionario_correlacao_original[(usi_x, usi_y)] = corr_orig
                    dicionario_correlacao_reduzida[(usi_x, usi_y)] = corr_red
                    mapa_correl_orig_usi[usi_x].append(corr_orig)
                    mapa_correl_red_usi[usi_x].append(corr_red)
                    #if( abs(corr_orig - corr_red) > 0.1 or math.isnan(corr_orig) or math.isnan(corr_red)):
                    #    
                    lista_correl_orig.append(corr_orig)
                    lista_correl_red.append(corr_red)
                except Exception as e:
                    print(f"Error calculating correlation for {usi_x} and {usi_y}: {e}")

        print(len(lista_correl_orig))
        print(len(lista_correl_red))
        lista_correl_orig = [x for x in lista_correl_orig if not math.isnan(x)]
        lista_correl_red =  [x for x in lista_correl_red if not math.isnan(x)]

        contador = 0
        print("Caso: " + mapa_casos[caso] + " A "+analise[0]+" Est: "+str(analise[1]))
        for i, usi_x in enumerate(usinas):
            x = np.array(mapa_correl_orig_usi[usi_x])  # original correlation
            y = np.array(mapa_correl_red_usi[usi_x])   # reduced correlation

            x = [a for a in x if not math.isnan(a)]
            y =  [a for a in y if not math.isnan(a)]

            x = np.array(x)  # original correlation
            y = np.array(y)   # reduced correlation

            # Force the model y = a * x
            slope = np.sum(x * y) / np.sum(x * x)
            y_pred = slope * x
            # Compute residual sum of squares (SQ_res)
            SQ_res = np.sum((y - y_pred) ** 2)
            # Compute total sum of squares (SQ_tot)
            y_mean = np.mean(y)
            SQ_tot = np.sum((y - y_mean) ** 2)
            # Compute R²
            r_squared = 1 - (SQ_res / SQ_tot)

            r_squared = truncate_to_2_decimals(r_squared)
            slope = truncate_to_2_decimals(slope)
            if(slope < 0.9 or slope> 1.1):
                contador+= 1
                #print("Usi: ", usi_x, " R-squared (manual):", r_squared)
                print("Usi: ", usi_x, " slope (manual):", slope)
        print("N: ", contador, " usinas de: ", len(usinas), " perc: ", 100*(contador/len(usinas)), " falharam")
        x = np.array(lista_correl_orig)  # original correlation
        y = np.array(lista_correl_red)   # reduced correlation

        # Force the model y = a * x
        slope = np.sum(x * y) / np.sum(x * x)
        y_pred = slope * x
        # Compute residual sum of squares (SQ_res)
        SQ_res = np.sum((y - y_pred) ** 2)
        # Compute total sum of squares (SQ_tot)
        y_mean = np.mean(y)
        SQ_tot = np.sum((y - y_mean) ** 2)
        # Compute R²
        r_squared = 1 - (SQ_res / SQ_tot)
        threshold = 0.0015


        #print("R-squared (manual):", r_squared)
        #print("slope (manual):", slope)
        r_squared = truncate_to_2_decimals(r_squared)
        slope = truncate_to_2_decimals(slope)
        print("R-squared (manual):", r_squared)
        print("slope (manual):", slope)
        #print(len(lista_correl_orig))
        #print(len(lista_correl_red))
        #print(lista_correl_orig)
        #print(lista_correl_red)
        #fig.add_trace(go.Scatter(
        #    x=lista_correl_orig, 
        #    y=lista_correl_red, 
        #    mode='markers',
        #    name=f' {mapa_casos[caso]} {str(analise[1])} (R² = {r_squared:.2f})',
        #    showlegend=False,
        #    marker=dict(size=10, color='blue')
        #), row=linha, col=coluna)
#
#
        #fig.add_trace(go.Scatter(
        #    x=[-0.5, 1], 
        #    y=[slope * -0.5, slope * 1],  # or simply [0, slope]
        #    mode='lines', 
        #    line=dict(color='red', width=2),
        #    showlegend=False
        #), row=linha, col=coluna)
#
        ## Add R² annotation
        ##axis_index = (linha - 1) * 3 + coluna  # Correct axis index for 6x3 grid
        #axis_index = (linha - 1) * 2 + coluna  # Correct axis index for 6x3 grid
        #fig.add_annotation(
        #    x=1.0,  # X position (relative to subplot domain)
        #    y=-0.3,  # Y position (relative to subplot domain)
        #    xref=f"x{axis_index}",  # Dynamic x-axis reference
        #    yref=f"y{axis_index}",  # Dynamic y-axis reference
        #    text=f"a = {slope:.2f}",
        #    showarrow=False,
        #    font=dict(size=20, color="black"),
        #    align="right"
        #)
#
        ## Add R² annotation
        ##axis_index = (linha - 1) * 3 + coluna  # Correct axis index for 6x3 grid
        #axis_index = (linha - 1) * 2 + coluna  # Correct axis index for 6x3 grid
        #fig.add_annotation(
        #    x=1.0,  # X position (relative to subplot domain)
        #    y=0,  # Y position (relative to subplot domain)
        #    xref=f"x{axis_index}",  # Dynamic x-axis reference
        #    yref=f"y{axis_index}",  # Dynamic y-axis reference
        #    text=f"R² = {r_squared:.2f}",
        #    showarrow=False,
        #    font=dict(size=20, color="black"),
        #    align="right"
        #)
#
#
        #titulo =  "Caso: " + mapa_casos[caso] + " A "+analise[0]+" Est: "+str(analise[1])
        #fig.layout.annotations[contador].update(text=titulo, font=dict(size=20)) 
        #contador += 1
        ##print("linha: ", linha, " coluna: ", coluna, " anotation: ", contador, " axis_index: ", axis_index)
        #coluna = coluna + 1
        #if(coluna == 3):
        #    coluna = 1
        #    linha = linha + 1
#
        #print(f" Caso {mapa_casos[caso]} Est {analise[1]} R²: {r_squared:.2f} Slope:{slope}")
        #    # Print the results
        #    #print("ORIGINAL: ")
        #    #print(dicionario_correlacao_original)
        #    #print("REDUZIDA")
        #    #print(dicionario_correlacao_reduzida)
        ## Customize layout
        #fig.update_layout(
        #    title="Correlações Árvore Original x Construída",
        #    title_font=dict(size=24, family="Arial", color="black"),
        #    xaxis_title="Correl. Orig.",
        #    yaxis_title="Correl. Red.",
        #    font=dict(size=20), 
        #    xaxis=dict(title_font=dict(size=20)),  
        #    yaxis=dict(title_font=dict(size=20)),
        #    showlegend=False
        #)
    #fig.write_html(camino_caso_orig+pasta_arvores+f"\\{mapa_casos[caso]}_correlacaoEspacialArvores_b0.html")
        # Print R² value





