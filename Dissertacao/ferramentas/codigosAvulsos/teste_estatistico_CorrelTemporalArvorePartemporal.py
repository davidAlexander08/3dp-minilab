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
pasta_arvores = "\\Dissertacao"
pasta_adicional_casos = "Final_TOL001\\"
#pasta_arvores = "\\avaliaArvoresSIN"
caminho_pente = "\\Pente"
df_arvore_original = pd.read_csv(camino_caso_orig+pasta_arvores+caminho_pente+"\\arvore.csv")
#print(df_arvore_original)
df_vazoes = pd.read_csv(camino_caso_orig+pasta_arvores+caminho_pente+"\\cenarios.csv")

tipo = "Dissertacao\\"
#tipo = "avaliaArvoresSIN\\"
#tipo = "VazaoIncrementalMultidimensional\\"
mapa_casos = {
    #"BKAssimetrico":"Redução Regressiva",
    #"KMeansPente":"K-Means", 
    "KMeansAssimetricoProbPente":"K-Means", 
    #"KMeansAssimetricoProb":"K-Means Assimetrico", 
    "KMeansSimetricoProbQuadPente":"K-Means Simetrico", 
    #"NeuralGas":"NeuralGas"
}
analises = ["A_125_2_2", "A_125_2_2", "A_50_5_2", "A_25_10_2"]
analise = "A_25x3x2"
#analise = "A_100x1x1"
#casos = ["BKAssimetrico", "KMeansAssimetrico", "KMeansSimetrico", "NeuralGas"]
#casos = ["Arvore1"]
lista_df_final = []
usinas = df_vazoes["NOME_UHE"].unique() 
#print(usinas)
#usinas = [17, 275, 266]

paresCorrelacaoTemporal = [
    (4,3), #LAG 1 Estágio 4
    (4,2), #LAG 2 Estágio 4
    (3,2)  #LAG 1 Estágio 3
]
estagio_folhas = 4
mapa_estagio_index ={
    4:0,
    3:1,
    2:2
}
def truncate_to_2_decimals(x):
    return math.floor(x * 100) / 100
for caso in mapa_casos: 
    fig = make_subplots(rows=2, cols=2, subplot_titles=(" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "))
    linha = 1
    coluna = 1
    contador = 0
    for parTemporal in paresCorrelacaoTemporal:
        caminho_red = camino_caso_orig+"\\"+tipo+"\\"+pasta_adicional_casos+"\\"+analise+"\\"+caso+"\\"
        df_arvore_reduzida = pd.read_csv(caminho_red+"arvore.csv")
        df_vazoes_reduzida = pd.read_csv(caminho_red+"cenarios.csv")
        df_orig_est = df_arvore_original.loc[(df_arvore_original["PER"] == estagio_folhas)].reset_index(drop = True)
        df_red_est = df_arvore_reduzida.loc[(df_arvore_reduzida["PER"] == estagio_folhas)].reset_index(drop = True)
        probabilidadeOriginal = []
        probabilidadeReduzida = []
        dicionarioNosEstagioCaminhosOriginal = {}
        dicionarioNosEstagioCaminhosReduzida = {}
        for est in parTemporal:
            dicionarioNosEstagioCaminhosOriginal[est] = []
            dicionarioNosEstagioCaminhosReduzida[est] = []
        for no in df_orig_est["NO"].unique():
            prob = 1
            lista_caminho = retorna_lista_caminho(no, df_arvore_original)[:-1]
            for est in parTemporal:
                dicionarioNosEstagioCaminhosOriginal[est].append(lista_caminho[mapa_estagio_index[est]])
            for elemento in lista_caminho:
                prob_elemento = df_arvore_original.loc[(df_arvore_original["NO"] == elemento)]["PROB"].iloc[0]
                prob = prob*prob_elemento
            probabilidadeOriginal.append(prob)
        
        for no in df_red_est["NO"].unique():
            prob = 1
            lista_caminho = retorna_lista_caminho(no, df_arvore_reduzida)[:-1]
            for est in parTemporal:
                dicionarioNosEstagioCaminhosReduzida[est].append(lista_caminho[mapa_estagio_index[est]])
            for elemento in lista_caminho:
                prob_elemento = df_arvore_reduzida.loc[(df_arvore_reduzida["NO"] == elemento)]["PROB"].iloc[0]
                prob = prob*prob_elemento
            probabilidadeReduzida.append(prob) 

        probabilidadeOriginal = np.array(probabilidadeOriginal)
        probabilidadeReduzida = np.array(probabilidadeReduzida)

        listaCorrelacaoTemporalOriginal = []
        listaCorrelacaoTemporalReduzida = []
        for usi in usinas:
            dicionarioVetorRealizacoesOriginal = {}
            dicionarioVetorRealizacoesReduzida = {}
            for est in parTemporal:
                dicionarioVetorRealizacoesOriginal[est] = []
                dicionarioVetorRealizacoesReduzida[est] = []

            for est in parTemporal:
                for no in dicionarioNosEstagioCaminhosOriginal[est]:
                    vazao = df_vazoes.loc[(df_vazoes["NOME_UHE"] == usi) & (df_vazoes["NO"] == no)].reset_index(drop = True)["VAZAO"].iloc[0]
                    dicionarioVetorRealizacoesOriginal[est].append(vazao)            
                for no in dicionarioNosEstagioCaminhosReduzida[est]:
                    vazao = df_vazoes_reduzida.loc[(df_vazoes_reduzida["NOME_UHE"] == usi) & (df_vazoes_reduzida["NO"] == no)].reset_index(drop = True)["VAZAO"].iloc[0]
                    dicionarioVetorRealizacoesReduzida[est].append(vazao)

            #print(dicionarioVetorRealizacoesOriginal)
            #print(dicionarioVetorRealizacoesReduzida[parTemporal[0]])
            #print(dicionarioVetorRealizacoesReduzida[parTemporal[1]])
            try: 
                corr_orig = weighted_correlation(dicionarioVetorRealizacoesOriginal[parTemporal[0]], 
                                                dicionarioVetorRealizacoesOriginal[parTemporal[1]], 
                                                probabilidadeOriginal)
                corr_red = weighted_correlation(dicionarioVetorRealizacoesReduzida[parTemporal[0]], 
                                                dicionarioVetorRealizacoesReduzida[parTemporal[1]], 
                                                probabilidadeReduzida)
                #print("corr_orig: ", corr_orig)
                #print("corr_red: ", corr_red)
                listaCorrelacaoTemporalOriginal.append(corr_orig)
                listaCorrelacaoTemporalReduzida.append(corr_red)
            except:
                print(f"Não foi possível calcular a correlação tempora para usina {usi} para o par {parTemporal}")

        #print("listaCorrelacaoTemporalOriginal: ", listaCorrelacaoTemporalOriginal)
        #print("listaCorrelacaoTemporalReduzida: ",listaCorrelacaoTemporalReduzida)
        # Compute R^2 using linear regression
        print(len(listaCorrelacaoTemporalOriginal))
        print(len(listaCorrelacaoTemporalReduzida))
        listaCorrelacaoTemporalOriginal = [x for x in listaCorrelacaoTemporalOriginal if not math.isnan(x)]
        listaCorrelacaoTemporalReduzida =  [x for x in listaCorrelacaoTemporalReduzida if not math.isnan(x)]
        #slope, intercept, r_value, p_value, std_err = linregress(listaCorrelacaoTemporalOriginal, listaCorrelacaoTemporalReduzida)
        #print(slope)
        #print(intercept)
        #print(r_value)
        #print(r_value**2)
        #print(p_value)
        #print(std_err)
        #r_squared = r_value**2
        #print("R-squared:", r_squared)
        #print(len(listaCorrelacaoTemporalOriginal))
        #print(len(listaCorrelacaoTemporalReduzida))
        #print(listaCorrelacaoTemporalOriginal)
        #print(listaCorrelacaoTemporalReduzida)
        x = np.array(listaCorrelacaoTemporalOriginal)  # original correlation
        y = np.array(listaCorrelacaoTemporalReduzida)   # reduced correlation

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

        print("R-squared (manual):", r_squared)
        print("slope (manual):", slope)
        #r_squared = truncate_to_2_decimals(r_squared)
        #slope = truncate_to_2_decimals(slope)
        #print("R-squared (manual):", r_squared)
        #print("slope (manual):", slope)


        fig.add_trace(go.Scatter(
            x=listaCorrelacaoTemporalOriginal, 
            y=listaCorrelacaoTemporalReduzida, 
            mode='markers',
            name=f' {mapa_casos[caso]} {str(est)} (R² = {r_squared:.2f})',
            showlegend=False,
            marker=dict(size=10, color='blue')
        ), row=linha, col=coluna)


        fig.add_trace(go.Scatter(
            x=[0, 1], 
            y=[slope * 0, slope * 1],  # or simply [0, slope]
            mode='lines', 
            line=dict(color='red', width=2),
            showlegend=False
        ), row=linha, col=coluna)

        # Add R² annotation
        axis_index = (linha - 1) * 2 + coluna  # Correct axis index for 6x3 grid
        fig.add_annotation(
            x=1.0,  # X position (relative to subplot domain)
            y=-0.3,  # Y position (relative to subplot domain)
            xref=f"x{axis_index}",  # Dynamic x-axis reference
            yref=f"y{axis_index}",  # Dynamic y-axis reference
            text=f"a = {slope:.2f}",
            showarrow=False,
            font=dict(size=20, color="black"),
            align="right"
        )

        # Add R² annotation
        #axis_index = (linha - 1) * 3 + coluna  # Correct axis index for 6x3 grid
        axis_index = (linha - 1) * 2 + coluna  # Correct axis index for 6x3 grid
        fig.add_annotation(
            x=1.0,  # X position (relative to subplot domain)
            y=0,  # Y position (relative to subplot domain)
            xref=f"x{axis_index}",  # Dynamic x-axis reference
            yref=f"y{axis_index}",  # Dynamic y-axis reference
            text=f"R² = {r_squared:.2f}",
            showarrow=False,
            font=dict(size=20, color="black"),
            align="right"
        )

        titulo =  "Caso: " + mapa_casos[caso] + " A: " + analise + " Par: " + str(parTemporal[0]) + "_" +str(parTemporal[1])
        fig.layout.annotations[contador].update(text=titulo, font=dict(size=20)) 
        contador += 1
        print("linha: ", linha, " coluna: ", coluna, " anotation: ", contador, " axis_index: ", axis_index)
        coluna = coluna + 1
        if(coluna == 3):
            coluna = 1
            linha = linha + 1
        print(parTemporal)
        print(f" Caso {mapa_casos[caso]} A {analise} R²: {r_squared:.2f} Slope: {slope:.2f}")
            # Print the results
            #print("ORIGINAL: ")
            #print(dicionario_correlacao_original)
            #print("REDUZIDA")
            #print(dicionario_correlacao_reduzida)
        # Customize layout
    fig.update_layout(
        title=f"Correlação Temporal Estagios {parTemporal[0]} {parTemporal[1]} Árvore Original x Construída",
        title_font=dict(size=24, family="Arial", color="black"),
        xaxis_title="Correl. Orig.",
        yaxis_title="Correl. Red.",
        font=dict(size=20), 
        xaxis=dict(title_font=dict(size=20)),  
        yaxis=dict(title_font=dict(size=20)),
        showlegend=False
    )
    fig.write_html(f"{camino_caso_orig}\\{tipo}\\{caso}_{parTemporal[0]}_{parTemporal[1]}_correlacaoEspacialArvores.html")
    # Print R² value





