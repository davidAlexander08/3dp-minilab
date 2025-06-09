import pandas as pd
import numpy as np
import plotly.graph_objects as go
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
caminho_deck = "Capitulo_5\\caso_mini_500Cen_cluster_semanais\\Dissertacao\\"
caminho_arvores = ""
caminho_resultados = "\\saidas\\PDD\\oper\\"
caminho_subarvores = ""
caminhosaida = "Caso_SF_Final_Allcut\\graficosSFEstocastica"


casos = {
        #"Eol_dem\\SFINAL_25x3x2_KM_semEol\\Pente":"red",
        #"Eol_cen\\SFINAL_25x3x2_KM_Eol\\Pente":"gold",
        
        "Caso_SF_Final_Allcut\\Pente\\Pente":"black",
        "Caso_SF_Final_Allcut\\Vassoura\\Pente":"purple",
        #"Caso_SF_Final\\A_300x1x1_Kmeans\\Pente":"gray",
        #"Caso_SF_Final\\A_200x1x1_Kmeans\\Pente":"darkblue",
        "Caso_SF_Final_Allcut\\A_100x1x1_Kmeans\\Pente":"blue",
        #"Caso_SF_Final\\A_100x1x1_BK\\Pente":"lightblue",
        #"Caso_SF_Final\\A_50x1x1_Kmeans\\Pente":"lightblue",
        #"Caso_SF_Final\\A_25x1x1_Kmeans\\Pente":"cyan",
        #"Caso_SF_Final\\A_5x1x1_Kmeans\\Pente":"cyan",
        #"Caso_SF_Final\\Determ\\Pente":"green",
        "Caso_SF_Final_Allcut\\A_25x3x2\\Pente":"red",
        #"SF_FINAL\\A_25x3x2_KM_Gran\\Pente":"gold",
        #"Caso_SF_Final\\A_25x3x2\\Pente":"gold",
        "Caso_SF_Final_Allcut\\A_25x3x2Simetrico\\Pente":"pink",
        #"Caso_SF_Final\\A_25x2x2\\Pente":"gold",
        #"Caso_SF_Final\\A_25x2x2Simetrico\\Pente":"orange",
        }
mapa_nome_caso = {
        "Caso_SF_Final_Allcut\\Vassoura\\Pente":"Vassoura",
        "Caso_SF_Final_Allcut\\Pente\\Pente":"Pente",
        "Caso_SF_Final_Allcut\\A_25x3x2Simetrico\\Pente":"A-25x3x2-S",
        "Caso_SF_Final_Allcut\\A_25x3x2\\Pente":"A_25x3x2",
        "Caso_SF_Final_Allcut\\A_100x1x1_Kmeans\\Pente":"P-100x1x1",


        "Eol_cen\\SFINAL_25x3x2_KM_Eol\\Pente":"25x3x2_EOL",
        "Eol_dem\\SFINAL_25x3x2_KM_semEol\\Pente":"25x3x2",
        "Caso_SF_Final\\A_25x3x2\\Pente":"A_25x3x2",
        "SF_FINAL\\A_25x3x2_KM_Gran\\Pente":"A_25x3x2_Eol",
        caminho_subarvores+"\\A_25x3x2\\KMeansAssimetricoProbPente":"A_25x3x2",
        caminho_subarvores+"\\A_100x1x1\\BKAssimetrico":"A_100x1x1",
        "Detrm":"Deterministico",
        "Vassoura\\KMeansAssimetricoProb":"Vassoura",
        "Pente":"Pente",
        caminho_subarvores+"\\Pente":"Pente Original",
        caminho_subarvores+"\\A_25_250_250\\KMeansAssimetricoProb":"A_25_250_250",
        caminho_subarvores+"\\A_25_125_250\\KMeansAssimetricoProb":"A_25_125_250",
        caminho_subarvores+"\\A_25_125_250_Teste\\KMeansAssimetricoProb":"A_25_125_250_Teste",
        caminho_subarvores+"\\A_25_125_250_Teste\\KMeansAssimetricoProbPenteFolha":"A_25_125_250_Teste_Pente",
        caminho_subarvores+"\\A_25_125_250_Teste\\KMeansAssimetricoProbPenteFolha":"A_25_125_250_Teste_Pente",
        "Caso_SF_Final\\A_25x3x2\\Pente":"A-25x3x2",
        "Caso_SF_Final\\A_25x2x2Simetrico\\Pente":"A_25x2x2Simetrico",
        "Caso_SF_Final\\A_5x1x1_Kmeans\\Pente":"A_5x1x1_Kmeans",
        "Caso_SF_Final\\A_25x1x1_Kmeans\\Pente":"A_25x1x1_Kmeans",
        "Caso_SF_Final\\A_50x1x1_Kmeans\\Pente":"A_50x1x1_Kmeans",
        "Caso_SF_Final\\A_300x1x1_Kmeans\\Pente":"A_300x1x1_Kmeans",
        "Caso_SF_Final\\A_200x1x1_Kmeans\\Pente":"A_200x1x1_Kmeans",
        "Caso_SF_Final\\A_100x1x1_BK\\Pente":"A_100x1x1_BK",
        "Caso_SF_Final\\Determ":"Determ",

        caminho_subarvores+"\\Determ\\Pente":"Determ"
}
grandezas = ["GT", "CustoPresente","EarmP", "Deficit",  "GH",  "CustoFuturo", "VolArm","AFL","CMO","VERT", "Earm","CustoTotal", ]
#grandezas = [ "GT","CMO"]
#grandezas = ["VERT"]
#grandezas = ["CMO"]
mapa_grandezas = {
    "GT":" Geração Térmica",
    "GH":" Geração Hidrelétrica",
    "Deficit":" Déficit",
    "CustoPresente":" Custo Operação",
    "CustoFuturo":" Custo Futuro",
    "CustoTotal":" Custo Total",
    "VolArm":" Volume Armazenado Final",
    "AFL":" Afluencia",
    "CMO":" Custo Marginal de Operação",
    "VERT":" Vertimento",
    "Earm":"Energia Armazenada",
    "EarmP":"Energia Armazenada Perc."
}
mapa_arquivos = {
    "GT":["balanco_energetico_final.csv","balanco_energetico_SIN_sf.csv"],
    "Deficit":["balanco_energetico_final.csv","balanco_energetico_SIN_sf.csv"],
    "GH":["balanco_energetico_final.csv","balanco_energetico_SIN_sf.csv"],
    "CustoPresente":["balanco_energetico_final.csv","balanco_energetico_SIN_sf.csv"],
    "CustoFuturo":["balanco_energetico_final.csv","balanco_energetico_SIN_sf.csv"],
    "CustoTotal":["balanco_energetico_final.csv","balanco_energetico_SIN_sf.csv"],
    "VolArm":["balanco_energetico_final.csv","balanco_energetico_SIN_sf.csv"],
    "AFL":["balanco_energetico_final.csv","balanco_energetico_SIN_sf.csv"],
    "CMO":["balanco_energetico_final_sbm.csv","balanco_energetico_SBM_sf.csv"],
    "VERT":["hidreletricas_sf.csv",""],
    "Earm":["balanco_energetico_final.csv","balanco_energetico_SIN_sf.csv"],
    "EarmP":["balanco_energetico_final.csv","balanco_energetico_SIN_sf.csv"],
}
mapa_unidades = {
    "GT":"MW",
    "GH":"MW",
    "Deficit":"MW",
    "CustoPresente":"R$",
    "CustoFuturo":"R$",
    "CustoTotal":"R$",
    "VolArm":"hm3",
    "AFL":"m3/s",
    "CMO":"R$/MWh",
    "VERT":"m3/s",
    "Earm":"MW",
    "EarmP":"%"
}
colors = ["black", "red", "blue", "green", "purple", "orange", "pink", "yellow", "lightblue",
         "salmon", "darkred", "darkblue", "darkgreen","lightgreen", ""]
arquivo = "balanco_energetico_final.csv"
for grandeza in grandezas:
    fig = make_subplots(rows=1, cols=1, subplot_titles=(" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "))
    fig2 = make_subplots(rows=1, cols=1, subplot_titles=(" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "))
    fig3 = make_subplots(rows=1, cols=1, subplot_titles=(" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "))
    fig4 = make_subplots(rows=1, cols=1, subplot_titles=(" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "))
    fig5 = make_subplots(rows=1, cols=1, subplot_titles=(" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "))

    linha = 1
    coluna = 1
    contador = 0
    arquivo = mapa_arquivos[grandeza][0]
    arquivo_cenarios = mapa_arquivos[grandeza][1]
    mostra_legendaLimites = True
    for caso in casos:


        if(grandeza == "CustoTotal"):
            df = pd.read_csv(caminho_base+caminho_deck+caminho_arvores+caso+caminho_resultados+arquivo)
            df["CustoTotal"] = df["CustoPresente"]+df["CustoFuturo"]
            df_cen = pd.read_csv(caminho_base+caminho_deck+caminho_arvores+caso+caminho_resultados+arquivo_cenarios)
            df_cen["CustoTotal"] = df_cen["CustoPresente"]+df_cen["CustoFuturo"]
            df_arvore = pd.read_csv(caminho_base+caminho_deck+caminho_arvores+caso+"\\arvore.csv")
        if(grandeza == "EarmP"):
            df = pd.read_csv(caminho_base+caminho_deck+caminho_arvores+caso+caminho_resultados+arquivo)
            df["EarmP"] = 100*(df["Earm"]/931025)
            df_cen = pd.read_csv(caminho_base+caminho_deck+caminho_arvores+caso+caminho_resultados+arquivo_cenarios)
            df_cen["EarmP"] = 100*(df_cen["Earm"]/931025)
            df_arvore = pd.read_csv(caminho_base+caminho_deck+caminho_arvores+caso+"\\arvore.csv")


        elif(grandeza == "VERT"):
            #df = pd.read_csv(caminho_base+caminho_deck+caminho_arvores+caso+caminho_resultados+arquivo)
            df_cen_usi = pd.read_csv(caminho_base+caminho_deck+caminho_arvores+caso+caminho_resultados+arquivo)
            df_arvore = pd.read_csv(caminho_base+caminho_deck+caminho_arvores+caso+"\\arvore.csv")
            usinas = df_cen_usi["usina"].unique()
            estagios = df_cen_usi["est"].unique()
            lista_df  = []
            for est in estagios:
                df_cen_est_temp = df_cen_usi.loc[(df_cen_usi["est"] == est)]
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
                    vertimento_SIN =  df_cen_est_temp_node["VERT"].sum()
                    prob_node =  df_cen_est_temp_node["prob"].iloc[0]
                    #print("node:" , node , " vert_sin: ", vertimento_SIN)
                    lista_df.append(
                        pd.DataFrame(
                            {
                                "est":[est],
                                "node":[node],
                                "prob":[prob_node],
                                "PROB_COND":[prob_cond],
                                "VERT":[vertimento_SIN]
                            }
                        )
                    )
            df_cen = pd.concat(lista_df).reset_index(drop = True)
            lista_media_SIN = []
            for est in estagios:
                df_SIN_est = df_cen.loc[(df_cen["est"] == est)].reset_index(drop = True)
                df_SIN_est["weighted_Vert"] = df_SIN_est["VERT"] * df_SIN_est["PROB_COND"]
                vertimento = df_SIN_est["weighted_Vert"].sum()
                lista_media_SIN.append(
                    pd.DataFrame(
                        {
                            "est":[est],
                            "VERT":[vertimento]
                        }
                    )
                )
            #print(nodes)
            #print(usinas)
            #print(df_cen)
            df = pd.concat(lista_media_SIN).reset_index(drop = True)
            print(df_cen)
            print(df)
        else:
            df = pd.read_csv(caminho_base+caminho_deck+caminho_arvores+caso+caminho_resultados+arquivo)
            df_cen = pd.read_csv(caminho_base+caminho_deck+caminho_arvores+caso+caminho_resultados+arquivo_cenarios)
            df_arvore = pd.read_csv(caminho_base+caminho_deck+caminho_arvores+caso+"\\arvore.csv")

        if(grandeza == "CMO"):
            sbm = "SUDESTE"
            df = df.loc[(df["Submercado"] == 1)]
            df_cen = df_cen.loc[(df_cen["Submercado"] == 1)]
            #sbm = "NORDESTE"
            #df = df.loc[(df["Submercado"] == 3)]
            #df_cen = df_cen.loc[(df_cen["Submercado"] == 3)]

        fig3.add_trace(go.Bar(
            x=[mapa_nome_caso[caso]],
            y=[df[grandeza].sum()],  # or simply [0, slope]
            #y=lista_media,  # or simply [0, slope]
            name = mapa_nome_caso[caso],
            legendgroup  = mapa_nome_caso[caso],
            #line=dict(color=colors[contador], width=2),
            marker_color=casos[caso],
            opacity=0.6,
            showlegend=True
        ), row=linha, col=coluna)        
        fig4.add_trace(go.Bar(
            x=[mapa_nome_caso[caso]],
            y=[df[grandeza].mean()],  # or simply [0, slope]
            #y=lista_media,  # or simply [0, slope]
            name = mapa_nome_caso[caso],
            legendgroup  = mapa_nome_caso[caso],
            #line=dict(color=colors[contador], width=2),
            marker_color=casos[caso],
            opacity=0.6,
            showlegend=True
        ), row=linha, col=coluna) 

        print("caso: ", mapa_nome_caso[caso], " grandeza: ", df[grandeza].reset_index(drop =True).iloc[0])     
        fig5.add_trace(go.Bar(
            x=[mapa_nome_caso[caso]],
            y=[df[grandeza].reset_index(drop =True).iloc[0]],  # or simply [0, slope]
            #y=lista_media,  # or simply [0, slope]
            name = mapa_nome_caso[caso],
            legendgroup  = mapa_nome_caso[caso],
            #line=dict(color=colors[contador], width=2),
            marker_color=casos[caso],
            opacity=0.6,
            showlegend=True
        ), row=linha, col=coluna)  
        dados_x = []
        dados_y = []
        estagios = df_cen["est"].unique()
        lista_p25_est = []
        lista_p75_est = []
        lista_media = []
        for est in estagios:
            print("est: ", est)
            df_arvore_est = df_arvore.loc[(df_arvore["PER"] == est)]
            df_cen_est = df_cen.loc[(df_cen["est"] == est)]
            dados_x = dados_x + [est]*len(df_cen_est[grandeza].tolist())
            dados_y = dados_y + df_cen_est[grandeza].tolist()
            df_cen_est["PROB_COND"] = 0
            for node in df_arvore_est["NO"].unique():
                prob_cond = 1
                caminho  = retorna_lista_caminho(node, df_arvore)
                for elemento in caminho:
                    prob_elemento = df_arvore.loc[(df_arvore["NO"] == elemento)]["PROB"].iloc[0]
                    prob_cond = prob_cond*prob_elemento
                #print("node: ", node, " caminho: ", caminho, " prob_cond: ", prob_cond)
                df_cen_est.loc[(df_cen_est["node"] == node), "PROB_COND"] = prob_cond
            #print(df_arvore_est)
            #print(df_cen_est)            
            p25 = df_cen_est[grandeza].quantile(0.25)
            p75 = df_cen_est[grandeza].quantile(0.75)
            #print(f"P25 (25th percentile): {p25}")
            #print(f"P75 (75th percentile): {p75}")
            p25, p75 = weighted_quantile(df_cen_est[grandeza], [0.25, 0.75], sample_weight=df_cen_est["PROB_COND"])
            #print(f"P25 (25th percentile): {p25}")
            #print(f"P75 (75th percentile): {p75}")
            media = df_cen_est[grandeza].quantile(0.75)
            #print(df_cen_est)
            #print(caso)
            lista_p25_est.append(p25)
            lista_p75_est.append(p75)
            lista_media.append(media)
            #somaProb = df_cen_est["prob"].sum()
            #print("caso: ", caso, " est: ", est, " somaProb: ", somaProb)
        #print("lista_p25_est: ", lista_p25_est)
        #print("lista_p75_est: ", lista_p75_est)
        print(len(dados_x))
        print(len(dados_y))
        #exit(1)
        #print(df_cen)

        fig2.add_trace(go.Box(
            x=dados_x,
            y=dados_y,  # or simply [0, slope]
            #y=lista_media,  # or simply [0, slope]
            name = mapa_nome_caso[caso],
            legendgroup  = mapa_nome_caso[caso],
            #line=dict(color=colors[contador], width=2),
            marker_color = casos[caso],
            #boxpoints="suspectedoutliers",
            boxpoints=False,
            showlegend=True,
        ), row=linha, col=coluna)



        fig.add_trace(go.Scatter(
            x=df["est"], 
            y=df[grandeza],  # or simply [0, slope]
            #y=lista_media,  # or simply [0, slope]
            mode='lines', 
            name = mapa_nome_caso[caso],
            legendgroup  = mapa_nome_caso[caso],
            #line=dict(color=colors[contador], width=2),
            line=dict(color=casos[caso], width=2),
            showlegend=True
        ), row=linha, col=coluna)
        #fig.add_trace(go.Scatter(
        #    x=df["est"], 
        #    y=lista_p25_est,  # or simply [0, slope]
        #    mode='lines', 
        #    name = "p25",
        #    legendgroup  = "p25",
        #    #line=dict(color=colors[contador], width=2, dash='dot'),
        #    line=dict(color=casos[caso], width=2, dash='dot'),
        #    showlegend=mostra_legendaLimites
        #), row=linha, col=coluna)
        #fig.add_trace(go.Scatter(
        #    x=df["est"], 
        #    y=lista_p75_est,  # or simply [0, slope]
        #    mode='lines', 
        #    name = "p75",
        #    legendgroup  = "p75",
        #    #line=dict(color=colors[contador], width=2, dash='dash'),
        #    line=dict(color=casos[caso], width=2, dash='dash'),
        #    showlegend=mostra_legendaLimites
        #), row=linha, col=coluna)
        contador += 1
        mostra_legendaLimites = False
    titulo = "Comparação Entre Árvores de Cenários - "+mapa_grandezas[grandeza]
    nome_figura = f"{mapa_grandezas[grandeza]}_operacao"
    if(grandeza == "CMO"):
        titulo = "Comparação Entre Árvores de Cenários - "+mapa_grandezas[grandeza] + " Submercado: " + sbm
        nome_figura = f"{mapa_grandezas[grandeza]}_operacao"+"_sbm_" + sbm
    fig.update_layout(
        title=titulo,
        title_font=dict(size=30, family="Arial", color="black"),
        xaxis_title="estágios",
        yaxis_title=mapa_unidades[grandeza],
        font=dict(size=30), 
        xaxis=dict(title_font=dict(size=30)),  
        yaxis=dict(title_font=dict(size=30)),
        showlegend=True
    )
    fig.write_html(f"{caminho_base+caminho_deck+caminho_arvores+caminhosaida}\\{nome_figura}.html")
    fig2.update_layout(
        title=titulo,
        title_font=dict(size=30, family="Arial", color="black"),
        xaxis_title="estágios",
        yaxis_title=mapa_unidades[grandeza],
        font=dict(size=30), 
        xaxis=dict(title_font=dict(size=30)),  
        yaxis=dict(title_font=dict(size=30)),
        boxmode='group',
        showlegend=True
    )
    fig2.write_html(f"{caminho_base+caminho_deck+caminho_arvores+caminhosaida}\\BOX_{nome_figura}.html")

    fig3.update_layout(
        title="Valores Totais "+titulo,
        title_font=dict(size=30, family="Arial", color="black"),
        xaxis_title="casos",
        yaxis_title=mapa_unidades[grandeza],
        font=dict(size=30), 
        xaxis=dict(title_font=dict(size=30)),  
        yaxis=dict(title_font=dict(size=30)),
        showlegend=True
    )
    fig3.write_html(f"{caminho_base+caminho_deck+caminho_arvores+caminhosaida}\\BAR_Sum_{nome_figura}.html")

    
    fig4.update_layout(
        title="Valores Médios "+titulo,
        title_font=dict(size=30, family="Arial", color="black"),
        xaxis_title="casos",
        yaxis_title=mapa_unidades[grandeza],
        font=dict(size=30), 
        xaxis=dict(title_font=dict(size=30)),  
        yaxis=dict(title_font=dict(size=30)),
        showlegend=True
    )
    fig4.write_html(f"{caminho_base+caminho_deck+caminho_arvores+caminhosaida}\\BAR_Mean_{nome_figura}.html")
    fig5.update_layout(
        title="Valores 1o Estágio "+titulo,
        title_font=dict(size=30, family="Arial", color="black"),
        xaxis_title="casos",
        yaxis_title=mapa_unidades[grandeza],
        font=dict(size=30), 
        xaxis=dict(title_font=dict(size=30)),  
        yaxis=dict(title_font=dict(size=30)),
        showlegend=True
    )
    fig5.write_html(f"{caminho_base+caminho_deck+caminho_arvores+caminhosaida}\\BAR_1oEst_{nome_figura}.html")
