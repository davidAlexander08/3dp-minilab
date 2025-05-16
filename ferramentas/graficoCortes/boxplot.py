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

caminho = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\Dissertacao\\apresentacaoCarmen_Gevazp\\caso_mini\\exercicioGevazp\\4Estagios\\3Aberturas\\Red_2Aberturas_2\\BKAssimetrico\\saidas\\PDD\\oper\\df_cortes_equivalentes.csv"
caminho = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\Dissertacao\\apresentacaoCarmen_Gevazp\\caso_mini\\exercicioGevazp\\4Estagios\\3Aberturas\\Deterministico_mediaProb\\saidas\\PDD\\oper\\df_cortes_equivalentes.csv"
caminho = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\Dissertacao\\apresentacaoCarmen_Gevazp\\caso_mini\\exercicioGevazp\\4Estagios\\3Aberturas\\Arvore_GVZP\\saidas\\PDD\\oper\\df_cortes_equivalentes.csv"
#######
caso1 = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\caso_mini_500Cen_cluster_semanais\avaliaArvoresRepresentativo\GTMIN\Deterministico\saidas\PDD\oper"
caso2 = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\caso_mini_500Cen_cluster_semanais\avaliaArvoresRepresentativo\GTMIN\Vassoura\saidas\PDD\oper"
caso3 = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\caso_mini_500Cen_cluster_semanais\avaliaArvoresRepresentativo\GTMIN\Pente\saidas\PDD\oper"
caso4 = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\caso_mini_500Cen_cluster_semanais\avaliaArvoresRepresentativo\GTMIN\A_25_125_250\KMeansAssimetricoProb\saidas\PDD\oper"
caso5 = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\caso_mini_500Cen_cluster_semanais\avaliaArvoresRepresentativo\GTMIN\A_100_100_100\BKAssimetrico\saidas\PDD\oper"

caminho_saida = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\Capitulo_5\\caso_mini_500Cen_cluster_semanais\\avaliaArvoresRepresentativo\\GTMIN"

caso1 = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\caso_mini_500Cen_cluster_semanais\avaliaArvoresRepresentativo\GTMIN\Deterministico\saidas\PDD\oper"
caso2 = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\caso_mini_500Cen_cluster_semanais\avaliaArvoresRepresentativo\revisaoDebora\Vassoura\KMeansAssimetricoProbPente\saidas\PDD\oper"
caso3 = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\caso_mini_500Cen_cluster_semanais\avaliaArvoresRepresentativo\GTMIN\Pente\saidas\PDD\oper"
caso4 = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\caso_mini_500Cen_cluster_semanais\avaliaArvoresRepresentativo\revisaoDebora\A_25x3x2\KMeansAssimetricoProbPente\saidas\PDD\oper"
caso5 = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\caso_mini_500Cen_cluster_semanais\avaliaArvoresRepresentativo\revisaoDebora\A_100x1x1_42_20\KMeansPente\saidas\PDD\oper"
caminho_saida = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\Capitulo_5\\caso_mini_500Cen_cluster_semanais\\avaliaArvoresRepresentativo\\revisaoDebora"

casos = {}
casos["Deterministico"] = caso1
casos["Vassoura"] = caso2
casos["Pente"] = caso3
casos["A_25x3x2"] = caso4
casos["A_100x1x1"] = caso5
cores = {
        "Deterministico":"green",
        "Vassoura":"purple",
        "Pente":"black",
        "A_25x3x2":"red",
        "A_100x1x1":"blue"
}

mapa_nome_caso = {
        "Deterministico":"Determ.",
        "Vassoura":"Vass.",
        "Pente":"Pente",
        "A_25x3x2":"A_25x3x2",
        "A_100x1x1":"A_100x1x1",
}


usina = 6
periodo = 1
no_usado = 1
fig = make_subplots(rows=4, cols=3, subplot_titles=(" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "))
linha = 1
coluna = 1
contador_titulo = 0
mapaNome = {
        6:"FURNAS",
        275:"TUCURUI",
        17:"MARIMBONDO",
        288:"BELO MONTE",
        18:"AGUA VERMELHA",
        91:"MACHADINHO",
        169:"SOBRADINHO",
        66:"ITAIPU",
        46:"PORTO PRIMAVERA",
        45:"JUPIA",
        43:"3 IRMAOS",
        33:"SÃO SIMÃO",
        115:"GP SOUZA",
        47:"A. A. LAYDNER",
        178:"XINGO",
        34:"ILHA SOLTEIRA",
}

mapaNome = {
        8:"ESTREITO",
        11:"VOLTA GRANDE",
        12:"P. COLOMBIA",
        156:"3 MARIAS",
        227:"SINOP",
        229:"TELES PIRES",
        270:"SERRA MESA",
        257:"PEIXE ANGIC",
        273:"LAJEADO",
        285:"JIRAU",
        287:"STO ANTONIO",
        279:"SAMUEL",
        115:"GP SOUZA",
        24:"EMBORCAÇÃO",
        25:"NOVA PONTE",
        31:"ITUMBIARA",
}


mapaNome = {
        32:"CACH DOURADA",
        37:"BARRA BONITA",
        40:"PROMISSÃO",
        42:"NAVANHANDAVA",
        50:"L. N. GARCEZ",
        61:"CAPIVARA",
        62:"TAQUARUCU",
        63:"ROSANA",
        86:"BARRA GRANDE",
        92:"ITA",
        93:"P. FUNDO",
        103:"CHAPECO",
        76:"SEGREDO",
        77:"SLTO SANTIAGO",
        82:"SALTO CAXIAS",
        172:"ITAPARICA",
}

mapaNome = {
        267:"ESTREITO TOC",
        314:"PIMENTAL",
}

mapaNome = {
        6:"FURNAS",
        17:"MARIMBONDO",
        
        #18:"AGUA VERMELHA",
        18:"AGUA VERMELHA",
        33:"SÃO SIMÃO",
        8:"ESTREITO",
        34:"ILHA SOLTEIRA",
        #45:"JUPIA",
        #46:"PORTO PRIMAVERA",
        #66:"ITAIPU",
        169:"SOBRADINHO",
        #172:"ITAPARICA",
        91:"MACHADINHO",
        115:"GP SOUZA",
        77:"SALTO SANTIAGO",
        275:"TUCURUI",
        227:"SINOP",
        
        #288:"BELO MONTE",
        
}

#for usina in [6, 275, 17, 288]:#usinas:
for usina in mapaNome:#usinas:
        fig2 = go.Figure()
        for caso in casos:
                df_cortes = pd.read_csv(casos[caso]+"\df_cortes_equivalentes.csv")
                df_filtro = df_cortes.loc[(df_cortes["usina"] == usina)  & (df_cortes["est"] == periodo)  & (df_cortes["noUso"] == no_usado) & (df_cortes["Indep"] != 0) ]
                df_filtro = df_filtro.loc[(df_filtro["iter"] != 1)].reset_index(drop = True)
                #print(df_filtro)
                #exit(1)
                coefs = df_filtro["Coef"].tolist()
                fig2.add_trace(go.Box(
                x=[mapa_nome_caso[caso]]*len(coefs), 
                #x=[caso]*len(coefs), 
                y=coefs, 
                marker_color=cores[caso],  # or any valid color name or hex code like '#1f77b4'
                boxpoints=False,
                showlegend=True))

                fig.add_trace(go.Box(
                #x=[caso]*len(coefs), 
                x=[mapa_nome_caso[caso]]*len(coefs), 
                y=coefs, 
                marker_color=cores[caso],  # or any valid color name or hex code like '#1f77b4'
                boxpoints=False,
                showlegend=True), row=linha, col=coluna)

        titulo =  "Usina " + str(usina)
        titulo =  "Usina " + mapaNome[usina]
        fig.layout.annotations[contador_titulo].update(text=titulo, font=dict(size=40)) 
        contador_titulo += 1
        print("linha: ", linha, " coluna: ", coluna, " anotation: ", contador_titulo)
        coluna = coluna + 1
        if(coluna == 4):
                coluna = 1
                linha = linha + 1

        titulo = f"cortes_usina_{usina}_no_{no_usado}"
        fig2.update_layout(
            title=titulo,
            title_font=dict(size=24, family="Arial", color="black"),        
            xaxis_title="Caso",
            yaxis_title="$/hm3",
            showlegend=False,
            font=dict(size=25),  # General font (e.g., legend)
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
fig.write_html(f"{caminho_saida}\\{titulo}.html", auto_open=True)  # Opens in browser


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