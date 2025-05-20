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
from plotly.subplots import make_subplots
import json



def encontraUsinaJusante(codigo_usi, df_uhe):
        #print("codigo_usi: ", codigo_usi, " df: ", df_uhe)
        df_conf_uhe = df_uhe.loc[(df_uhe["CODIGO"] == int(codigo_usi))].reset_index(drop = True)
        #print("codigo_usi: ", codigo_usi, " df: ", df_conf_uhe)
        return df_conf_uhe["JUSANTE"].iloc[0]
    
def calcula_prodt_acum(codigo_usi, df_uhe):
        #print(df_uhe)
        df_uhe_usi = df_uhe.loc[(df_uhe["CODIGO"] == codigo_usi)].reset_index(drop = True)
        
        usi_jusante = codigo_usi
        prodt = df_uhe_usi["PRODT"].iloc[0]
        #print("codigo_usi: ", codigo_usi, " prodt: ", prodt)
        while (usi_jusante != ""):
                
                usi_jusante = encontraUsinaJusante(usi_jusante, df_uhe)
                #print("usina_jusante: ", usi_jusante)
                if(usi_jusante != ""):
                        prodt_jusante = df_uhe.loc[(df_uhe["CODIGO"] == int(usi_jusante))]["PRODT"].iloc[0]
                        #print("usi_jusante: ", usi_jusante, " prodt: ", prodt_jusante)
                        prodt += prodt_jusante
                
        return prodt



caminho = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\Dissertacao\\apresentacaoCarmen_Gevazp\\caso_mini\\exercicioGevazp\\4Estagios\\3Aberturas\\Red_2Aberturas_2\\BKAssimetrico\\saidas\\PDD\\oper\\df_cortes_equivalentes.csv"
caminho = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\Dissertacao\\apresentacaoCarmen_Gevazp\\caso_mini\\exercicioGevazp\\4Estagios\\3Aberturas\\Deterministico_mediaProb\\saidas\\PDD\\oper\\df_cortes_equivalentes.csv"
caminho = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\Dissertacao\\apresentacaoCarmen_Gevazp\\caso_mini\\exercicioGevazp\\4Estagios\\3Aberturas\\Arvore_GVZP\\saidas\\PDD\\oper\\df_cortes_equivalentes.csv"
#######
caso1 = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\caso_mini_500Cen_cluster_semanais\avaliaArvoresRepresentativo\GTMIN\Deterministico\saidas\PDD\oper"
caso2 = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\caso_mini_500Cen_cluster_semanais\avaliaArvoresRepresentativo\GTMIN\Vassoura\saidas\PDD\oper"
caso3 = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\caso_mini_500Cen_cluster_semanais\avaliaArvoresRepresentativo\GTMIN\Pente\saidas\PDD\oper"
caso4 = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\caso_mini_500Cen_cluster_semanais\avaliaArvoresRepresentativo\GTMIN\A_25_125_250\KMeansAssimetricoProb\saidas\PDD\oper"
caso5 = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\caso_mini_500Cen_cluster_semanais\avaliaArvoresRepresentativo\GTMIN\A_100_100_100\BKAssimetrico\saidas\PDD\oper"

caso1 = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\caso_mini_500Cen_cluster_semanais\Dissertacao\Final_TOL001\Pente\saidas\PDD\oper"
caso2 = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\caso_mini_500Cen_cluster_semanais\Dissertacao\Final_TOL001\Detrm\saidas\PDD\oper"
caso3 = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\caso_mini_500Cen_cluster_semanais\Dissertacao\Final_TOL001\Vassoura\KMeansAssimetricoProbPente\saidas\PDD\oper"
caso4 = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\caso_mini_500Cen_cluster_semanais\Dissertacao\Final_TOL001\A_100x1x1\KMeansPente\saidas\PDD\oper"
caso5 = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\caso_mini_500Cen_cluster_semanais\Dissertacao\Final_TOL001\A_25x3x2\KMeansAssimetricoProbPente\saidas\PDD\oper"
caso6 = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\caso_mini_500Cen_cluster_semanais\Dissertacao\Final_TOL001\A_25x3x2\KMeansSimetricoProbQuadPente\saidas\PDD\oper"
caminho_saida = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\Capitulo_5\\caso_mini_500Cen_cluster_semanais\\Dissertacao\\Final_TOL001"

casos = {}
casos["Pente"] = caso1
casos["Detrm"] = caso2
casos["Vassoura"] = caso3
casos["A_100x1x1"] = caso4
casos["A_25x3x2"] = caso5
casos["A_25x3x2Simetrico"] = caso6
cores = {
        "Detrm":"green",
        "Vassoura":"purple",
        "Pente":"black",
        "A_25x3x2":"red",
        "A_25x3x2Simetrico":"pink",
        "A_100x1x1":"blue"
}

usina = 6
periodo = 1
no_usado = 1
fig = make_subplots(rows=2, cols=2, subplot_titles=(" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "))
linha = 1
coluna = 1
contador_titulo = 0
caminho_json = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\caso_mini_500Cen_cluster_semanais\dadosEntrada.json"
with open(caminho_json, "r") as f:
    data = json.load(f)
df_uhe = pd.DataFrame(data["UHEs"])
#print(df_uhe)
submercados = df_uhe["SUBMERCADO"].unique()
print(submercados)

mapa_nome_sbm = {
        1:"SUDESTE",
        2:"SUL",
        3:"NORDESTE",
        4:"NORTE"
}


for sbm in submercados:
        df_usinas_sbm = df_uhe.loc[(df_uhe["SUBMERCADO"] == sbm)].reset_index(drop = True)        
        for caso in casos:
                soma_prodt_acum = 0
                df_cortes = pd.read_csv(casos[caso]+"\df_cortes_equivalentes.csv")
                lista_df = []
                for usi in df_usinas_sbm["CODIGO"].unique():
                        prodt_acum = calcula_prodt_acum(usi, df_uhe)
                        df_filtro = df_cortes.loc[(df_cortes["usina"] == usi)  & (df_cortes["est"] == periodo)  & (df_cortes["noUso"] == no_usado) & (df_cortes["Indep"] != 0) ]
                        df_filtro = df_filtro.loc[(df_filtro["iter"] != 1)].reset_index(drop = True)
                        #print(prodt_acum)
                        #print(df_filtro)
                        lista_df.append(df_filtro["Coef"]*prodt_acum)
                        soma_prodt_acum += prodt_acum
                
                df_result = pd.concat(lista_df, axis = 1)
                df_result["soma_total"] = df_result.sum(axis=1)
                coef_final = df_result["soma_total"]/soma_prodt_acum
                #print(coef_final)
                fig.add_trace(go.Box(x=[caso]*len(coef_final.tolist()), 
                y=coef_final, 
                marker_color=cores[caso],  # or any valid color name or hex code like '#1f77b4'
                boxpoints=False,
                showlegend=True), row=linha, col=coluna)
        titulo =  f"Submercado {mapa_nome_sbm[sbm]}"
        fig.layout.annotations[contador_titulo].update(text=titulo, font=dict(size=35)) 
        contador_titulo += 1
        print("linha: ", linha, " coluna: ", coluna, " anotation: ", contador_titulo)
        coluna = coluna + 1
        if(coluna == 3):
                coluna = 1
                linha = linha + 1
        print(df_usinas_sbm)

titulo = f"PIVs Médios Submercados"
fig.update_layout(
        title=titulo,
        xaxis_title="Caso",
        yaxis_title="$/hm3",
        showlegend=False,
        title_font=dict(size=30),  # Title font size
        font=dict(size=30),  # General font (e.g., legend)
)
fig.write_html(f"{caminho_saida}\\{titulo}.html", auto_open=True)  # Opens in browser
exit(1)
fig2 = go.Figure()
for caso in casos:
        df_cortes = pd.read_csv(casos[caso]+"\df_cortes_equivalentes.csv")
        df_filtro = df_cortes.loc[(df_cortes["usina"] == usina)  & (df_cortes["est"] == periodo)  & (df_cortes["noUso"] == no_usado) & (df_cortes["Indep"] != 0) ]
        df_filtro = df_filtro.loc[(df_filtro["iter"] != 1)].reset_index(drop = True)
        #print(df_filtro)
        #exit(1)
        coefs = df_filtro["Coef"].tolist()
        fig2.add_trace(go.Box(x=[caso]*len(coefs), 
        y=coefs, 
        marker_color=cores[caso],  # or any valid color name or hex code like '#1f77b4'
        boxpoints=False,
        showlegend=True))

        fig.add_trace(go.Box(x=[caso]*len(coefs), 
        y=coefs, 
        marker_color=cores[caso],  # or any valid color name or hex code like '#1f77b4'
        boxpoints=False,
        showlegend=True), row=linha, col=coluna)

titulo =  "Usina " + str(usina)
titulo =  "Usina " + mapaNome[usina]
fig.layout.annotations[contador_titulo].update(text=titulo, font=dict(size=20)) 
contador_titulo += 1
print("linha: ", linha, " coluna: ", coluna, " anotation: ", contador_titulo)
coluna = coluna + 1
if(coluna == 4):
        coluna = 1
        linha = linha + 1

titulo = f"cortes_usina_{usina}_no_{no_usado}"
fig2.update_layout(
        title=titulo,
        xaxis_title="Caso",
        yaxis_title="$/hm3",
        showlegend=False,
        font=dict(size=15),  # General font (e.g., legend)
)
#fig2.write_html(f"htmls\\{titulo}.html", auto_open=True)  # Opens in browser


titulo = f"PIVs Usinas"
fig.update_layout(
        title=titulo,
        xaxis_title="Caso",
        yaxis_title="$/hm3",
        showlegend=False,
        font=dict(size=25),  # General font (e.g., legend)
)
fig.write_html(f"htmls\\{titulo}.html", auto_open=True)  # Opens in browser


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