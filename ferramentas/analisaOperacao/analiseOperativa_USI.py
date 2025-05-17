import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math
import warnings
warnings.filterwarnings("ignore")

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



def weighted_quantile(values, quantiles, sample_weight=None):
    values = np.array(values)
    quantiles = np.atleast_1d(quantiles)
    if sample_weight is None:
        sample_weight = np.ones(len(values))
    else:
        sample_weight = np.array(sample_weight)

    sorter = np.argsort(values)
    values = values[sorter]
    sample_weight = sample_weight[sorter]

    weighted_cdf = np.cumsum(sample_weight) - 0.5 * sample_weight
    weighted_cdf /= np.sum(sample_weight)

    return np.interp(quantiles, weighted_cdf, values)


caminho_base = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\"
caminho_deck = "Capitulo_5\\caso_mini_500Cen_cluster_semanais\\"
caminho_arvores = "avaliaArvoresRepresentativo\\"
caminho_subarvores = "Caso_SF"
caminho_resultados = "\\saidas\\PDD\\oper\\"
caminhosaida = "Caso_SF"

casos = [caminho_subarvores+"\\Pente",
        "revisaoDebora\\A_25x3x2\\KMeansAssimetricoProbPenteSemente200K12",
        caminho_subarvores+"\\A_100_100_100\\BKAssimetrico",
        #"Rodada_Final\\A_100_100_100\\BKAssimetrico",
        caminho_subarvores+"\\Deterministico",
        caminho_subarvores+"\\Vassoura"
        ]
mapa_nome_caso = {
        caminho_subarvores+"\\Pente":"Pente Original",
        caminho_subarvores+"\\A_25_250_250\\KMeansAssimetricoProb":"A_25_250_250",
        caminho_subarvores+"\\A_25_125_250\\KMeansAssimetricoProb":"A_25_125_250",
        caminho_subarvores+"\\A_125_125_125\\BKAssimetrico":"A_125_125_125",
        caminho_subarvores+"\\A_100_100_100\\BKAssimetrico":"A_100x1x1",
        caminho_subarvores+"\\Deterministico":"Deterministico",
        caminho_subarvores+"\\Vassoura":"Vassoura",
        "revisaoDebora\\A_25x3x2\\KMeansAssimetricoProbPenteSemente200K12":"A_25x3x2",
}

casos = [caminho_subarvores+"\\A_25x3x2\\Determ_12",
        caminho_subarvores+"\\A_25x3x2Simetrico\\Determ_12",
        caminho_subarvores+"\\A_100x1x1\\Determ_12",
        caminho_subarvores+"\\Vassoura\\Determ_12"
        ]
mapa_nome_caso = {
        caminho_subarvores+"\\A_25x3x2\\Determ_12":"A_25x3x2",
        caminho_subarvores+"\\A_25x3x2Simetrico\\Determ_12":"A_25x3x2Simetrico",
        caminho_subarvores+"\\A_100x1x1\\Determ_12":"A_100x1x1",
        caminho_subarvores+"\\Vassoura\\Determ_12":"Vassoura",
}

grandezas = ["VERT","generation","AFL","VF","TURB","QDEF"]
#grandezas = ["CMO"]
mapa_grandezas = {
    "VF":" Volume Armazenado Final",
    "AFL":" Afluencia",
    "VERT":" Vertimento",
    "generation":"Geração Hidrelétrica",
    "TURB":"Turbinamento",
    "QDEF":"Defluência",
}
mapa_arquivos = {
    "VF":["hidreletricas_sf.csv",""],
    "AFL":["hidreletricas_sf.csv",""],
    "VERT":["hidreletricas_sf.csv",""],
    "VF":["hidreletricas_sf.csv",""],
    "generation":["hidreletricas_sf.csv",""],
    "TURB":["hidreletricas_sf.csv",""],
    "QDEF":["hidreletricas_sf.csv",""],
}
mapa_unidades = {
    "VolArm":"hm3",
    "AFL":"m3/s",
    "VF":"hm3",
    "VERT":"m3/s",
    "generation":"MW",
    "TURB":"m3/s",
    "QDEF":"m3/s",
}
colors = ["black", "red", "blue", "green", "purple", "orange", "pink", "yellow", "lightblue",
         "salmon", "darkred", "darkblue", "darkgreen","lightgreen", ""]
arquivo = "balanco_energetico_final.csv"

mapaNomeUsinas = {
        6:"FURNAS",
        17:"MARIMBONDO",
        #18:"AGUA VERMELHA",
        33:"SÃO SIMÃO",
        34:"ILHA SOLTEIRA",
        #45:"JUPIA",
        #46:"PORTO PRIMAVERA",
        #66:"ITAIPU",
        45:"JUPIA",
        169:"SOBRADINHO",
        172:"ITAPARICA",
        91:"MACHADINHO",
        #115:"GP SOUZA", 
        77:"SALTO SANTIAGO",
        275:"TUCURUI",
        227:"SINOP",
        288:"BELO MONTE",
        
}


#mapaNomeUsinas = {
#        6:"FURNAS",
#        17:"MARIMBONDO",
#        #18:"AGUA VERMELHA",
#        34:"I. SOLTEIRA",
#        25:"NOVA PONTE",
#        24:"EMBORCACAO",
#        #45:"JUPIA",
#        #46:"PORTO PRIMAVERA",
#        #66:"ITAIPU",
#        33:"SAO SIMAO",
#        251:"SERRA MESA",
#        257:"PEIXE ANGIC",
#        275:"TUCURUI",
#        74:"G.B. MUNHOZ",
#        #115:"GP SOUZA", 
#        76:"SEGREDO",
#        77:"SALTO SANTIAGO",
#        
#        #74:"G.B. MUNHOZ",
#        
#}

for grandeza in grandezas:
    fig = make_subplots(rows=4, cols=3, subplot_titles=(" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "))
    linha = 1
    coluna = 1
    contador_titulo = 0
    arquivo = mapa_arquivos[grandeza][0]
    arquivo_cenarios = mapa_arquivos[grandeza][1]
    mostra_legendaLimites = True
    for usi in mapaNomeUsinas:
        contador_cores= 0
        for caso in casos:
            print("usi: ", usi, " caso: ", caso)
            df_cen = pd.read_csv(caminho_base+caminho_deck+caminho_arvores+caso+caminho_resultados+arquivo)
            if(grandeza == "QDEF"):
                df_cen["QDEF"] = df_cen["VERT"]+df_cen["TURB"]
            print(df_cen)
            df_cen_usi = df_cen.loc[(df_cen["usina"] == usi)].reset_index(drop = True)
            df_arvore = pd.read_csv(caminho_base+caminho_deck+caminho_arvores+caso+"\\arvore.csv")
            estagios = df_cen_usi["est"].unique()
            lista_df = []
            lista_p25_est = []
            lista_p75_est = []
            lista_media = []
            for est in estagios:
                df_cen_est_temp = df_cen_usi.loc[(df_cen_usi["est"] == est)]
                #print("df_cen_est_temp: ", df_cen_est_temp)
                nodes = df_cen_est_temp["node"].unique()
                df_cen_est_temp["PROB_COND"] = 0
                for node in nodes:
                    prob_cond = 1
                    caminho  = retorna_lista_caminho(node, df_arvore)
                    for elemento in caminho:
                        prob_elemento = df_arvore.loc[(df_arvore["NO"] == elemento)]["PROB"].iloc[0]
                        prob_cond = prob_cond*prob_elemento
                    #print("node: ", node, " caminho: ", caminho, " prob_cond: ", prob_cond)
                    df_cen_est_temp_node = df_cen_est_temp.loc[(df_cen_est_temp["node"] == node)]
                    df_cen_est_temp.loc[(df_cen_est_temp["node"] == node),"PROB_COND"] = prob_cond
                    prob_node =  df_cen_est_temp_node["prob"].iloc[0]
                df_arvore_est = df_arvore.loc[(df_arvore["PER"] == est)]
                p25, p75 = weighted_quantile(df_cen_est_temp[grandeza], [0.25, 0.75], sample_weight=df_cen_est_temp["PROB_COND"])
                #print(f"P25 (25th percentile): {p25}")
                #print(f"P75 (75th percentile): {p75}")
                weighted_mean = (df_cen_est_temp[grandeza] * df_cen_est_temp["PROB_COND"]).sum() / df_cen_est_temp["PROB_COND"].sum()
                #print(df_cen_est)
                #print(caso)
                lista_p25_est.append(p25)
                lista_p75_est.append(p75)
                lista_media.append(weighted_mean)
            print("lista_p25_est: ", lista_p25_est)
            print("lista_p75_est: ", lista_p75_est)
            print("lista_media: ", lista_media)
            #print(df_cen)
            fig.add_trace(go.Scatter(
                x=estagios, 
                y=lista_media,  # or simply [0, slope]
                #y=lista_media,  # or simply [0, slope]
                mode='lines', 
                name = mapa_nome_caso[caso],
                legendgroup  = mapa_nome_caso[caso],
                line=dict(color=colors[contador_cores], width=2),
                showlegend=mostra_legendaLimites
            ), row=linha, col=coluna)
            fig.add_trace(go.Scatter(
                x=estagios, 
                y=lista_p25_est,  # or simply [0, slope]
                mode='lines', 
                name = "p25",
                legendgroup  = "p25",
                line=dict(color=colors[contador_cores], width=2, dash='dot'),
                showlegend=mostra_legendaLimites
            ), row=linha, col=coluna)
            fig.add_trace(go.Scatter(
                x=estagios, 
                y=lista_p75_est,  # or simply [0, slope]
                mode='lines', 
                name = "p75",
                legendgroup  = "p75",
                line=dict(color=colors[contador_cores], width=2, dash='dash'),
                showlegend=mostra_legendaLimites
            ), row=linha, col=coluna)
            contador_cores += 1
        mostra_legendaLimites = False
            
        titulo =  f"Usina {mapaNomeUsinas[usi]}"
        fig.layout.annotations[contador_titulo].update(text=titulo, font=dict(size=35)) 
        
        print("linha: ", linha, " coluna: ", coluna, " anotation: ", contador_titulo)
        coluna = coluna + 1
        if(coluna == 4):
            coluna = 1
            linha = linha + 1
        contador_titulo += 1
    titulo = "Comparação Entre Árvores de Cenários - "+mapa_grandezas[grandeza]
    nome_figura = f"{mapa_grandezas[grandeza]}_usinas_operacao"
    fig.update_layout(
        title=titulo,
        title_font=dict(size=24, family="Arial", color="black"),
        xaxis_title="estágios",
        yaxis_title=mapa_unidades[grandeza],
        font=dict(size=20), 
        xaxis=dict(title_font=dict(size=20)),  
        yaxis=dict(title_font=dict(size=20)),
        showlegend=True
    )
    fig.write_html(f"{caminho_base+caminho_deck+caminho_arvores+caminhosaida}\\{nome_figura}.html")
    #exit(1)
