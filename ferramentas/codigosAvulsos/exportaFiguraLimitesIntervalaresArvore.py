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
from inewave.newave import Confhd
from inewave.newave import Hidr

caminho = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\Capitulo_5\\caso_mini_500Cen_cluster_semanais\\avaliaArvoresRepresentativo\\"
casos = ["BKAssimetrico", "KMeansAssimetricoProb", "KMeansSimetricoProbQuad", "NeuralGas"]



analises = [("A_125_2_2",3), ("A_125_2_2",2), ("A_50_5_2",2), ("A_25_10_2",2) ]

for caso in casos:
    fig_mean = make_subplots(rows=2, cols=2, subplot_titles=(" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "))
    fig_var = make_subplots(rows=2, cols=2, subplot_titles=(" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "))
    linha = 1
    coluna = 1
    contador = 0
    show = True
    for analise in analises:
        df_estatistica = pd.read_csv(caminho + analise[0]+"\\estatisticasArvores.csv", sep=';')
        df_caso = df_estatistica.loc[(df_estatistica["CASO"] == caso) & (df_estatistica["EST"] == analise[1])].reset_index(drop = True)
        lista_postos = df_caso["POSTO"].unique().astype(str)
        lista_medialimSupOrig = df_caso["Sup_ci_95_mean_orig"].astype(str).str.replace(',', '.', regex=False).astype(float).to_numpy()
        lista_mediaOriginal = df_caso["mediaOrig"].astype(str).str.replace(',', '.', regex=False).astype(float).to_numpy()
        lista_mediaReduzida = df_caso["mediaRed"].astype(str).str.replace(',', '.', regex=False).astype(float).to_numpy()
        lista_medialimInfOrig = df_caso["Low_ci_95_mean_orig"].astype(str).str.replace(',', '.', regex=False).astype(float).to_numpy()
        lista_medialimInfRed = df_caso["Low_ci_95_mean_red"].astype(str).str.replace(',', '.', regex=False).astype(float).to_numpy()
        lista_medialimSupRed = df_caso["Sup_ci_95_mean_red"].astype(str).str.replace(',', '.', regex=False).astype(float).to_numpy()
        
        lista_varlimSupOrig = df_caso["Sup_ci_95_var_orig"].astype(str).str.replace(',', '.', regex=False).astype(float).to_numpy()**(1/2)
        lista_varOriginal = df_caso["stdOrig"].astype(str).str.replace(',', '.', regex=False).astype(float).to_numpy()
        lista_varReduzida = df_caso["stdRed"].astype(str).str.replace(',', '.', regex=False).astype(float).to_numpy()
        lista_varlimInfOrig = df_caso["Low_ci_95_var_orig"].astype(str).str.replace(',', '.', regex=False).astype(float).to_numpy()**(1/2)
        lista_varlimInfRed = df_caso["Low_ci_95_var_red"].astype(str).str.replace(',', '.', regex=False).astype(float).to_numpy()
        lista_varlimSupRed = df_caso["Sup_ci_95_var_red"].astype(str).str.replace(',', '.', regex=False).astype(float).to_numpy()

        limSupMean =            lista_medialimSupOrig   /lista_medialimSupOrig
        lista_meanOriginal =    lista_mediaOriginal     /lista_medialimSupOrig
        lista_meanReduzida =    lista_mediaReduzida     /lista_medialimSupOrig
        lista_meanlimInfOrig =  lista_medialimInfOrig   /lista_medialimSupOrig
        print(lista_postos)
        fig_mean.add_trace(go.Scatter(
            x=lista_postos, 
            y=limSupMean, 
            mode='lines',
            name=f'limSup',
            legendgroup='limSup',        # <- Group lines in the same legend group
            showlegend=show,
            line=dict(color='black', dash='dash')  # ← dashed red line
        ), row=linha, col=coluna)

        fig_mean.add_trace(go.Scatter(
            x=lista_postos, 
            y=lista_meanlimInfOrig, 
            mode='lines',
            name=f'limInf',
            legendgroup='limInf',        # <- Group lines in the same legend group
            showlegend=show,
            line=dict(color='black', dash='dash')  # ← dashed red line
        ), row=linha, col=coluna)

        fig_mean.add_trace(go.Scatter(
            x=lista_postos, 
            y=lista_meanOriginal, 
            mode='lines',
            name=f'original',
            legendgroup='original',        # <- Group lines in the same legend group
            showlegend=show,
            line=dict(color='blue')  # ← dashed red line
        ), row=linha, col=coluna)

        fig_mean.add_trace(go.Scatter(
            x=lista_postos, 
            y=lista_meanReduzida, 
            mode='lines',
            name=f'reduzido',
            legendgroup='reduzido',        # <- Group lines in the same legend group
            showlegend=show,
            line=dict(color='red')  # ← dashed red line
        ), row=linha, col=coluna)



        limSupVar = lista_varlimSupOrig/lista_varlimSupOrig
        lista_varOriginal = lista_varOriginal/lista_varlimSupOrig
        lista_varReduzida = lista_varReduzida/lista_varlimSupOrig
        lista_varlimInfOrig = lista_varlimInfOrig/lista_varlimSupOrig

        fig_var.add_trace(go.Scatter(
            x=lista_postos, 
            y=limSupVar, 
            mode='lines',
            name=f'limSup',
            legendgroup='limSup',        # <- Group lines in the same legend group
            showlegend=show,
            line=dict(color='black', dash='dash')  # ← dashed red line
        ), row=linha, col=coluna)

        fig_var.add_trace(go.Scatter(
            x=lista_postos, 
            y=lista_varlimInfOrig, 
            mode='lines',
            name=f'limInf',
            legendgroup='limInf',        # <- Group lines in the same legend group
            showlegend=show,
            line=dict(color='black', dash='dash')  # ← dashed red line
        ), row=linha, col=coluna)

        fig_var.add_trace(go.Scatter(
            x=lista_postos, 
            y=lista_varOriginal, 
            mode='lines',
            name=f'original',
            legendgroup='original',        # <- Group lines in the same legend group
            showlegend=show,
            line=dict(color='blue')  # ← dashed red line
        ), row=linha, col=coluna)

        fig_var.add_trace(go.Scatter(
            x=lista_postos, 
            y=lista_varReduzida, 
            mode='lines',
            name=f'reduzido',
            legendgroup='reduzido',        # <- Group lines in the same legend group
            showlegend=show,
            line=dict(color='red')  # ← dashed red line
        ), row=linha, col=coluna)


        titulo =  "Caso: " + caso + " A: "+analise[0]+ "Est: "+ str(analise[1]) 
        fig_mean.layout.annotations[contador].update(text=titulo, font=dict(size=20)) 
        
        fig_var.layout.annotations[contador].update(text=titulo, font=dict(size=20)) 
        contador += 1
        #print("linha: ", linha, " coluna: ", coluna, " anotation: ", contador, " axis_index: ", axis_index)
        #print("linha: ", linha, " coluna: ", coluna)
        coluna = coluna + 1
        if(coluna == 3):
            coluna = 1
            linha = linha + 1
        show = False
    fig_mean.update_layout(
        title="Limites intervalares de média",
        title_font=dict(size=24, family="Arial", color="black"),
        xaxis_title="Postos",
        yaxis_title="Média",
        font=dict(size=20), 
        xaxis=dict(title_font=dict(size=20)),  
        yaxis=dict(title_font=dict(size=20),range=[0.6, 1.1]),
        yaxis2=dict(range=[0.6, 1.1]),     # subplot (1,2)
        yaxis3=dict(range=[0.6, 1.1]),     # subplot (2,1)
        yaxis4=dict(range=[0.6, 1.1]),      # subplot (2,2)
        showlegend=True
    )
    fig_var.update_layout(
        title="Limites intervalares de variância",
        title_font=dict(size=24, family="Arial", color="black"),
        xaxis_title="Postos",
        yaxis_title="Variância",
        font=dict(size=20), 
        xaxis=dict(title_font=dict(size=20)),  
        yaxis=dict(title_font=dict(size=20)),
        #yaxis=dict(title_font=dict(size=20),range=[0.6, 1.1]),
        #yaxis2=dict(range=[0.6, 1.1]),     # subplot (1,2)
        #yaxis3=dict(range=[0.6, 1.1]),     # subplot (2,1)
        #yaxis4=dict(range=[0.6, 1.1]),      # subplot (2,2)
        showlegend=True
    )
    fig_mean.write_html(f"{caminho}\\Caso_{caso}_{analise}_limitesIntervalaresMedia.html")
    fig_var.write_html(f"{caminho}\\Caso_{caso}_{analise}_limitesIntervalaresVariancia.html")
    # Print R² value





