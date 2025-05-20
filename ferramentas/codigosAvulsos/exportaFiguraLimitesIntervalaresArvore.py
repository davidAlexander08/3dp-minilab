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
caminho = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\Academico\\exercicio_5D\\128_Aberturas_Equiprovavel\\Academicos\\"
caminho = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\Carmen\\exercicio_27cen_36D\\27_Aberturas_Equiprovavel\\"
caminho = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\Capitulo_5\\caso_mini_500Cen_cluster_semanais\\Dissertacao\\Final_TOL001\\"
#caminho = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\Capitulo_5\\caso_mini_500Cen_cluster_semanais\\avaliaArvoresRepresentativo\\revisaoDebora\\"
casos = ["BKAssimetrico", "KMeansAssimetricoProbPente", "KMeansSimetricoProbQuadPente", "NeuralGas"]
casos = ["BKAssimetrico", "KMeansAssimetricoProbPente"]
casos = ["BKAssimetrico", "KMeansAssimetricoProbPente", "KMeansSimetricoProbQuadPente"]
casos = ["KMeansPente"]

mapaNomeCaso = {
    "BKAssimetrico":"Redução Regressiva",
    "KMeansAssimetricoProbPente":"K-Means",
    "KMeansSimetricoProbQuadPente":"K-Means Simétrico",
    "NeuralGas":"Neural Gas",
    "KMeansPente":"K-Means",
}


analises = [("A_125_2_2",3, "250"), ("A_125_2_2",2, "125"), ("A_50_5_2",2, "50"), ("A_25_10_2",2, "25") ]
analises = [("A_4x4x2",4, "32"), ("A_4x4x2",3, "16"), ("A_4x4x2",2, "4")]
analises = [("A_25x3x2",4, "150"), ("A_25x3x2",3, "75"), ("A_25x3x2",2, "25")]
analises = [("A_4x2x1",4, "8"), ("A_4x2x1",3, "8"), ("A_4x2x1",2, "4")]
analises = [("A_25x3x2",4, "150"), ("A_25x3x2",3, "75"), ("A_25x3x2",2, "25")]
analises = [("A_100x1x1",4, "100"), ("A_100x1x1",3, "100"), ("A_100x1x1",2, "100")]

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

        lista_meanOriginal =    lista_mediaOriginal     /lista_mediaOriginal
        limSupMean =            lista_medialimSupOrig   /lista_mediaOriginal
        lista_meanReduzida =    lista_mediaReduzida     /lista_mediaOriginal
        lista_meanlimInfOrig =  lista_medialimInfOrig   /lista_mediaOriginal
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
            y=lista_meanReduzida, 
            mode='lines',
            name=f'reduzido',
            legendgroup='reduzido',        # <- Group lines in the same legend group
            showlegend=show,
            line=dict(color='red')  # ← dashed red line
        ), row=linha, col=coluna)

        fig_mean.add_trace(go.Scatter(
            x=lista_postos, 
            y=lista_meanOriginal, 
            mode='lines',
            name=f'original',
            legendgroup='original',        # <- Group lines in the same legend group
            showlegend=show,
            line=dict(color='blue', dash='dot')  # ← dashed red line
        ), row=linha, col=coluna)




        lista_varOriginal_plot = lista_varOriginal/lista_varOriginal
        limSupVar_plot  = lista_varlimSupOrig/lista_varOriginal
        lista_varReduzida_plot  = lista_varReduzida/lista_varOriginal
        lista_varlimInfOrig_plot  = lista_varlimInfOrig/lista_varOriginal

        fig_var.add_trace(go.Scatter(
            x=lista_postos, 
            y=limSupVar_plot, 
            mode='lines',
            name=f'limSup',
            legendgroup='limSup',        # <- Group lines in the same legend group
            showlegend=show,
            line=dict(color='black', dash='dash')  # ← dashed red line
        ), row=linha, col=coluna)

        fig_var.add_trace(go.Scatter(
            x=lista_postos, 
            y=lista_varlimInfOrig_plot, 
            mode='lines',
            name=f'limInf',
            legendgroup='limInf',        # <- Group lines in the same legend group
            showlegend=show,
            line=dict(color='black', dash='dash')  # ← dashed red line
        ), row=linha, col=coluna)

        fig_var.add_trace(go.Scatter(
            x=lista_postos, 
            y=lista_varOriginal_plot, 
            mode='lines',
            name=f'original',
            legendgroup='original',        # <- Group lines in the same legend group
            showlegend=show,
            line=dict(color='blue')  # ← dashed red line
        ), row=linha, col=coluna)

        fig_var.add_trace(go.Scatter(
            x=lista_postos, 
            y=lista_varReduzida_plot, 
            mode='lines',
            name=f'reduzido',
            legendgroup='reduzido',        # <- Group lines in the same legend group
            showlegend=show,
            line=dict(color='red')  # ← dashed red line
        ), row=linha, col=coluna)


        #titulo =  + " Árvore: "+analise[0]+ " Est: "+ str(analise[1])+ " Cen. "+ analise[2] 
        titulo =  " Est: "+ str(analise[1])+ " No. de nós "+ analise[2] 
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
        title="Limites intervalares de média "+mapaNomeCaso[caso] ,
        title_font=dict(size=24, family="Arial", color="black"),
        xaxis_title="Postos",
        yaxis_title="Média",
        font=dict(size=20), 
        xaxis=dict(title_font=dict(size=20)),  
        yaxis=dict(title_font=dict(size=20),range=[0.7, 1.2]),
        yaxis1=dict(range=[0.5, 1.3]),     # subplot (1,2)
        yaxis2=dict(range=[0.5, 1.3]),     # subplot (1,2)
        yaxis3=dict(range=[0.5, 1.3]),     # subplot (2,1)
        yaxis4=dict(range=[0.5, 1.3]),      # subplot (2,2)
        showlegend=True
    )
    fig_var.update_layout(
        title="Limites intervalares de variância "+mapaNomeCaso[caso] ,
        title_font=dict(size=24, family="Arial", color="black"),
        xaxis_title="Postos",
        yaxis_title="Variância",
        font=dict(size=20), 
        xaxis=dict(title_font=dict(size=20)),  
        yaxis=dict(title_font=dict(size=20)),
        #yaxis=dict(title_font=dict(size=20),range=[0.6, 1.1]),
        yaxis1=dict(range=[0, 1.3]),     # subplot (1,2)
        yaxis2=dict(range=[0, 1.3]),     # subplot (1,2)
        yaxis3=dict(range=[0, 1.3]),     # subplot (2,1)
        yaxis4=dict(range=[0, 1.3]),      # subplot (2,2)
        showlegend=True
    )
    fig_mean.write_html(f"{caminho}\\Caso_{caso}_{analise}_limitesIntervalaresMedia.html")
    fig_var.write_html(f"{caminho}\\Caso_{caso}_{analise}_limitesIntervalaresVariancia.html")
    # Print R² value





