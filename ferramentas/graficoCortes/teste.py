# Codigo transforma ECO
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import MiniBatchKMeans
import math
import os
from datetime import timedelta  # <-- Add this import at the top of your script
import time
import plotly.graph_objects as go

caminho = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\Dissertacao\\apresentacaoCarmen_Gevazp\\caso_mini\\exercicioGevazp\\4Estagios\\3Aberturas\\Red_2Aberturas_2\\BKAssimetrico\\saidas\\PDD\\oper\\df_cortes_equivalentes.csv"
caminho = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\Dissertacao\\apresentacaoCarmen_Gevazp\\caso_mini\\exercicioGevazp\\4Estagios\\3Aberturas\\Deterministico_mediaProb\\saidas\\PDD\\oper\\df_cortes_equivalentes.csv"
caminho = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\Dissertacao\\apresentacaoCarmen_Gevazp\\caso_mini\\exercicioGevazp\\4Estagios\\3Aberturas\\Arvore_GVZP\\saidas\\PDD\\oper\\df_cortes_equivalentes.csv"
#caminho = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\caso_mini_500Cen_sorteio_mensais\avaliaArvores\Deterministico\saidas\PDD\oper"
#caminho = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\caso_mini_500Cen_sorteio_mensais\avaliaArvores\Vassoura\saidas\PDD\oper"
#caminho = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\caso_mini_500Cen_sorteio_mensais\avaliaArvores\A_25_10_2\BKAssimetrico\saidas\PDD\oper"
caminho = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\Academico_Dissertacao\\exercicio_1D\\Pente_GVZP_FCF\\saidas\\PDD\\oper"
df_cortes = pd.read_csv(caminho+"\\cortes_est.csv")
df_operUH = pd.read_csv(caminho+"\\hidreletricas_sf.csv")
print(df_cortes)
usina = 6
nos = df_cortes["noUso"].unique()
usinas = df_cortes["usina"].unique()
periodo = 4
no_usado = 4
#no_usado = 2
for usina in usinas:
    df_usi = df_operUH.loc[(df_operUH["usina"] == usina)]
    v_min = min(df_usi["VI"].min(), df_usi["VF"].min())
    v_max = max(df_usi["VI"].max(), df_usi["VF"].max())
    print(df_usi)
    print("vmin: ", v_min, " v_max: ", v_max*1.1)
#for no_usado in nos:
    if(int(v_min) != int(v_max)):
        fig2 = go.Figure()
        df_filtro = df_cortes.loc[(df_cortes["usina"] == usina)  & (df_cortes["est"] == periodo)  & (df_cortes["noUso"] == no_usado) & (df_cortes["Indep"] != 0) ]
        print(df_filtro)
        coefs = df_filtro["Coef"].tolist()

        fig = go.Figure()
        
        x = np.linspace(int(v_min), int(v_max), int(v_max))
        y_lines = []
        for idx, row in df_filtro.iterrows():
            y = row.Coef * x + row.Indep
            y_lines.append(y)
            fig.add_trace(go.Scatter(x=x, y=y, showlegend=False, mode='lines', line=dict(color='black'), name=f'y = {row.Coef}x + {row.Indep} Iter {row.iter}'))
#
        
        y_array = np.array(y_lines)
        y_max_envelope = np.max(y_array, axis=0)
        fig.add_trace(go.Scatter(
            x=x, y=y_max_envelope,
            mode='lines',
            name='FCF',
            line=dict(color='red', width=4)
        ))
#
        titulo = f"cortes_usina_{usina}_no_{no_usado}"
        fig.update_layout(
            title=titulo,
            xaxis_title="hm3",
            yaxis_title="$",
            showlegend=True
        )
#
        fig.write_html(f"htmls\\{titulo}.html", auto_open=True)  # Opens in browser

