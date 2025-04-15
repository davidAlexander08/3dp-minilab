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
#######
caso1 = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\caso_mini_500Cen_sorteio_mensais\avaliaArvores\Deterministico\saidas\PDD\oper"
caso2 = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\caso_mini_500Cen_sorteio_mensais\avaliaArvores\Vassoura\saidas\PDD\oper"
caso3 = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\caso_mini_500Cen_sorteio_mensais\avaliaArvores\A_25_10_2\BKAssimetrico\saidas\PDD\oper"
casos = {}
casos["Deterministico"] = caso1
casos["Vassoura"] = caso2
casos["Arvore"] = caso3


usina = 6
periodo = 1
no_usado = 1
#no_usado = 2
for usina in [6, 275, 17]:#usinas:
        fig2 = go.Figure()
        for caso in casos:
                df_cortes = pd.read_csv(casos[caso]+"\df_cortes_equivalentes.csv")
                df_filtro = df_cortes.loc[(df_cortes["usina"] == usina)  & (df_cortes["est"] == periodo)  & (df_cortes["noUso"] == no_usado) & (df_cortes["Indep"] != 0) ]
                coefs = df_filtro["Coef"].tolist()
                fig2.add_trace(go.Box(x=[caso]*len(coefs), y=coefs, showlegend=True))
        titulo = f"cortes_usina_{usina}_no_{no_usado}"
        fig2.update_layout(
            title=titulo,
            xaxis_title="hm3",
            yaxis_title="$",
            showlegend=False
        )
        fig2.write_html(f"htmls\\{titulo}.html", auto_open=True)  # Opens in browser



        #df_filtro = df_cortes.loc[(df_cortes["usina"] == usina)  & (df_cortes["est"] == periodo)  & (df_cortes["noUso"] == no_usado) & (df_cortes["Indep"] != 0) ]
        #fig = go.Figure()
        #
        #x = np.linspace(int(v_min), int(v_max), int(v_max))
        #y_lines = []
        #for idx, row in df_filtro.iterrows():
        #    y = row.Coef * x + row.Indep
        #    y_lines.append(y)
        #    fig.add_trace(go.Scatter(x=x, y=y, showlegend=False, mode='lines', line=dict(color='black'), name=f'y = {row.Coef}x + {row.Indep} Iter {row.iter}'))
#
        #
        #y_array = np.array(y_lines)
        #y_max_envelope = np.max(y_array, axis=0)
        #fig.add_trace(go.Scatter(
        #    x=x, y=y_max_envelope,
        #    mode='lines',
        #    name='FCF',
        #    line=dict(color='red', width=4)
        #))
#
        #titulo = f"cortes_usina_{usina}_no_{no_usado}"
        #fig.update_layout(
        #    title=titulo,
        #    xaxis_title="hm3",
        #    yaxis_title="$",
        #    showlegend=True
        #)
#
        #fig.write_html(f"htmls\\{titulo}.html", auto_open=True)  # Opens in browser


exit(1)

df = pd.read_csv("previsaoM_inc_semTV_2020_01.csv", sep=";")
print(df)
postos = df["postos"].unique()
print(postos)
print("TOTAL POSTOS: ", len(postos))
print(df.loc[(df["postos"] == 266)])
print(df.loc[(df["postos"] == 66)])

df_2 = pd.read_parquet("CenariosMestrado\\cenarios_GhcenSemanais_4.parquet", engine = "pyarrow")
print(df_2)
postos_2 = df_2["posto"].unique()
print(postos_2)
print("TOTAL POSTOS: ", len(postos_2))
print(df_2.loc[(df_2["posto"] == 266)])
print(df_2.loc[(df_2["posto"] == 66)])
exit(1)

# Marca o tempo de início
inicio = time.time()
os.environ["LOKY_MAX_CPU_COUNT"] = "4" 
df_n =      pd.read_parquet("previsao_diaria/previsao_total_n.parquet", engine = "pyarrow")
df_ne =     pd.read_parquet("previsao_diaria/previsao_total_ne.parquet", engine = "pyarrow")
df_ose =    pd.read_parquet("previsao_diaria/previsao_total_ose.parquet", engine = "pyarrow")
df_parana = pd.read_parquet("previsao_diaria/previsao_total_parana.parquet", engine = "pyarrow")
df_sul =    pd.read_parquet("previsao_diaria/previsao_total_s.parquet", engine = "pyarrow")
print(df_n)
print(df_ne)
print(df_ose)
print(df_parana)
print(df_sul)

df_resultante = pd.concat([df_n, df_ne, df_ose, df_parana, df_sul]).reset_index(drop = True)
df_resultante = df_resultante.drop(columns=["data_rodada", "previsao_total", "previsao_total_sem_tv", "previsao_inc_tv", "nome"])
df_resultante['data_previsao'] = pd.to_datetime(df_resultante['data_previsao'])
data_inic = pd.to_datetime("2020-01-01")
print("data_ini: ", data_inic)
semanas = 5
lista_df_semanas = []
for i in range(0,semanas):
    
    print("data_inic: ", data_inic)
    df_data = df_resultante.loc[(df_resultante["data_previsao"] == data_inic)]
    data_inic = data_inic + timedelta(days=7)
    print(df_data)
    lista_df_semanas.append(df_data)

resultado = pd.concat(lista_df_semanas).reset_index(drop = True)
resultado.to_csv("cenarios_GhcenSemanais_"+str(semanas)+".csv", index = False)
resultado.to_parquet("cenarios_GhcenSemanais_"+str(semanas)+".parquet", index = False)

print(resultado)