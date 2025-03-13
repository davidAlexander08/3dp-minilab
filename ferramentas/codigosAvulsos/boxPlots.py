import numpy as np
import pandas as pd
from scipy.stats import wasserstein_distance
from scipy.stats import ksone
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px
from plotly.subplots import make_subplots
#Estágio 4
df_arvore_original = pd.read_csv("arvore_estudo.csv")
df_vazoes = pd.read_csv("vazoes_estudo.csv")

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




tipo = "ENAAgregado\\"
#tipo = "VazaoIncrementalMultidimensional\\"
tipos = [("VazaoIncrementalMultidimensional\\", "QIcr"), ("ENAAgregado\\","Ena")]

casos = [("Arvore6","A6"), ("Arvore5","A5"), ("Arvore4","A4"), ("Arvore3","A3"), ("Arvore2","A2"),("Arvore1","A1")]
cor = [
    "red", "lightcoral",
    "blue", "lightskyblue",
    "green", "lightgreen",
    "darkorange", "gold",
    "purple", "orchid",
    "brown", "sandybrown",
    "darkcyan", "lightcyan",
    "navy", "cornflowerblue",
    "darkred", "salmon",
    "darkmagenta", "violet"]

usinas = [17, 156, 275]
estagios = [2,3,4]
lista_df_final = []
for usi in usinas:
    for est in estagios: 
        fig = go.Figure()
        lista_original = []
        df_orig_est = df_arvore_original.loc[(df_arvore_original["PER"] == est)].reset_index(drop = True)
        for no in df_orig_est["NO"].unique():
            vazao = df_vazoes.loc[(df_vazoes["NOME_UHE"] == usi) & (df_vazoes["NO"] == no)].reset_index(drop = True)["VAZAO"].iloc[0]
            lista_original.append(vazao)
        fig.add_trace(go.Box(x = ["Pente"]*len(lista_original), y = lista_original, name = "Pente", line = dict(color = "black"), boxpoints="outliers", showlegend = True))
        contador = 0
        for caso in casos:
            for tipo in tipos:
                df_arvore_reduzida = pd.read_csv(tipo[0]+caso[0]+"\\df_arvore_reduzida.csv")
                lista_red = []
                df_red_est = df_arvore_reduzida.loc[(df_arvore_reduzida["PER"] == est)].reset_index(drop = True)
                for no in df_red_est["NO"].unique():
                    vazao = df_vazoes.loc[(df_vazoes["NOME_UHE"] == usi) & (df_vazoes["NO"] == no)].reset_index(drop = True)["VAZAO"].iloc[0]
                    lista_red.append(vazao)
                titulo = tipo[1]+"_"+caso[1]
                fig.add_trace(go.Box(x = [titulo]*len(lista_red), y = lista_red, name = titulo, line = dict(color = cor[contador]) , boxpoints="outliers", showlegend = True))
                contador += 1
        text = f"Usina {usi} Estagio {est}"
        fig.update_layout(title= text, font=dict(size= 20))
        fig.write_html(f"{text}.html",
                include_plotlyjs='cdn',
                config={"modeBarButtonsToAdd": ["drawline", "eraseshape", "sendDataToCloud"]})
        #fig.write_image("C:\\Users\\testa\\Documents\\mestrado\\ComparacaoArvoresBackwardReduction\\"+text+".png",
        #    width=1000,
        #    height=800,
        #    engine = "kaleido")
