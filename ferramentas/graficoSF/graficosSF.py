import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math

caminhoSF = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\Capitulo_5\\caso_mini_500Cen_cluster_semanais\\Dissertacao\\Caso_SF_Final_TOL001\\"
pasta_saida = "ResultadosDeterm\\"
mapaNomeCaso = {
    "Pente":"Pente",
    "Vassoura":"Vassoura",
    #"A_300x1x1_Kmeans":"A_300x1x1_Kmeans", 
    #"A_200x1x1_Kmeans":"A_200x1x1_Kmeans", 
    "A_100x1x1_Kmeans":"A_100x1x1_Kmeans", 
    #"A_50x1x1_Kmeans":"A_50x1x1_Kmeans", 
    #"A_5x1x1_Kmeans":"A_5x1x1_Kmeans", 
    #"Determ":"Determ", 
    "A_25x3x2": "A_25x3x2 K-Means", 
    "A_25x3x2Simetrico":"A_25x3x2 K-Means S", 
    #"A_25x2x2": "A_25x2x2 K-Means", 
    #"A_25x2x2Simetrico":"A_25x2x2 K-Means S", 
    
}
mapaGrandezas = {
    "AFL_mean"              :["Afluência Média"      ,  "m3/s"], 
    "Deficit_mean"          :["Déficit Médio"        ,  "MW"  ], 
    "GT_mean"               :["Geração Térmica Média",  "MW"  ], 
    "GH_mean"               :["Geração Hidrelétrica Média",  "MW"  ], 
    "VolArm_mean"          :["Vol. Armazenado Médio",  "hm3"  ], 
    "Vert_mean"             :["Vertimento Médio"     ,  "m3/s"  ], 
    "CustoPresente_mean"   :["Custo Presente Médio" ,  "R$"   ],
    "CustoTotal_mean":["Custo Total Médio","R$"],
    "CustoFuturo_mean"   :["Custo Futuro Médio" ,  "R$"   ],
    "Earm_mean"   :["Energ. Armaz. Média" ,  "MW"   ],
    "CMO_mean"   :["Custo Marginal" ,  "R$/MWh"   ],
}
#mapaGrandezas = {
#    "CustoTotal_mean":["Custo Total Médio","R$"],
#}
mapaEixoX = {
    "Determ_06":"H60", 
    "Determ_08":"H80", 
    "Determ":"HM", 
    "Determ_12":"H120", 
    #"Determ_14":"H140"
}

cores = {
    "CustoTotal":"R$",
    "A_25x3x2":"red", 
    "A_25x3x2Simetrico":"salmon", 
    "A_25x2x2":"gold", 
    "A_25x2x2Simetrico":"yellow", 
    "A_100x1x1_Kmeans":"blue",
    "A_200x1x1_Kmeans":"darkblue",
    "A_300x1x1_Kmeans":"gray",
    "A_50x1x1_Kmeans":"lightblue",
    "A_5x1x1_Kmeans":"cyan",
    "Vassoura":"purple",
    "Determ":"green",
    "Pente":"black"
}


for grandeza in mapaGrandezas:
    fig = make_subplots(rows=1, cols=1, subplot_titles=(" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "))
    for caso in mapaNomeCaso:
        eixoy = []
        eixox = [] 
        for avaliacao in mapaEixoX:

            if(grandeza == "CustoTotal_mean"):
                df_media_SIN = pd.read_csv(caminhoSF+caso+"\\"+avaliacao+"\\saidas\\PDD\\oper\\media_SIN.csv")

                df_media_SIN["CustoTotal_mean"] = df_media_SIN["CustoPresente_mean"]+df_media_SIN["CustoFuturo_mean"]
                #print(df_media_SIN)
                #print( df_media_SIN["CustoPresente_mean"])
                #print( df_media_SIN["CustoFuturo_mean"])
                #print( df_media_SIN["CustoTotal_mean"])
                print( df_media_SIN)
                #exit(1)
                eixoy.append(df_media_SIN[grandeza].iloc[0])
            elif(grandeza == "EarmP"):
                df_media_SIN = pd.read_csv(caminhoSF+caso+"\\"+avaliacao+"\\saidas\\PDD\\oper\\media_SIN.csv")
                df_media_SIN["EarmP"] = 100*(df_media_SIN["Earm"]/931025)
                eixoy.append(df_media_SIN[grandeza].iloc[0])
            elif(grandeza == "CMO_mean"):
                df_media_SBM = pd.read_csv(caminhoSF+caso+"\\"+avaliacao+"\\saidas\\PDD\\oper\\media_SBM.csv")
                #print(df_media_SBM)
                eixoy.append(df_media_SBM[grandeza].iloc[0])
            else:
                #print("caso: ", caso)
                df_media_SIN = pd.read_csv(caminhoSF+caso+"\\"+avaliacao+"\\saidas\\PDD\\oper\\media_SIN.csv")
                #print(df_media_SIN)
                eixoy.append(df_media_SIN[grandeza].iloc[0])
            eixox.append(mapaEixoX[avaliacao])

        fig.add_trace(go.Bar(
            x=eixox,
            y=eixoy,
            name=mapaNomeCaso[caso],
            legendgroup=mapaNomeCaso[caso],
            marker=dict(color=cores[caso]),
            showlegend=True
        ), row=1, col=1)
    titulo = mapaGrandezas[grandeza][0]
    nome_figura = f"{grandeza}"
    fig.update_layout(
        title=titulo,
        title_font=dict(size=30, family="Arial", color="black"),
        #xaxis_title="",
        yaxis_title=mapaGrandezas[grandeza][1],
        font=dict(size=30), 
        xaxis=dict(title_font=dict(size=30)),  
        yaxis=dict(title_font=dict(size=30)),
        showlegend=True
    )
    fig.write_html(f"{caminhoSF+pasta_saida}{nome_figura}.html")








mapaGrandezas = {
    "GT_1_mes"      :["Geração Térmica 1o Est"      ,  "MW" , "GT" ], 
    "GH_1_mes"      :["Geração Hidrelétrica 1o Est" ,  "MW" , "GH" ], 
    "VolArm_1_mes"  :["Vol. Armazenado 1o Est"      ,  "hm3", "VolArm" ], 
    "Vert_1_mes"    :["Vertimento 1o Est"           ,  "MW" , "Vert" ], 
    "CMO_1_mes"     :["Custo Marginal 1o Est"       ,  "R$/MWh" , "CMO" ],
    "CP_1_mes"      :["Custo Presente 1o Est"       ,  "R$" , "CustoPresente" ],
    "Earm_1_mes"      :["Energ. Armazenada 1o Est"       ,  "MW" , "Earm" ],
}


for grandeza in mapaGrandezas:
    fig = make_subplots(rows=1, cols=1, subplot_titles=(" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "))
    for caso in mapaNomeCaso:
        eixoy = []
        eixox = []
        for avaliacao in mapaEixoX:
            if(grandeza == "CMO_1_mes"):
                df_media_SBM = pd.read_csv(caminhoSF+caso+"\\"+avaliacao+"\\saidas\\PDD\\oper\\balanco_energetico_final_sbm.csv")
                #print(df_media_SBM)
                eixoy.append(df_media_SBM[mapaGrandezas[grandeza][2]].iloc[0])
            else:
                df_media_SIN = pd.read_csv(caminhoSF+caso+"\\"+avaliacao+"\\saidas\\PDD\\oper\\balanco_energetico_final.csv")
                #print(df_media_SIN)
                eixoy.append(df_media_SIN[mapaGrandezas[grandeza][2]].iloc[0])
            eixox.append(mapaEixoX[avaliacao])

        fig.add_trace(go.Bar(
            x=eixox,
            y=eixoy,
            name=mapaNomeCaso[caso],
            legendgroup=mapaNomeCaso[caso],
            marker=dict(color=cores[caso]),
            showlegend=True
        ), row=1, col=1)
    titulo = mapaGrandezas[grandeza][0]
    nome_figura = f"{grandeza}"
    fig.update_layout(
        title=titulo,
        title_font=dict(size=30, family="Arial", color="black"),
        #xaxis_title="",
        yaxis_title=mapaGrandezas[grandeza][1],
        font=dict(size=30), 
        xaxis=dict(title_font=dict(size=30)),  
        yaxis=dict(title_font=dict(size=30)),
        showlegend=True
    )
    fig.write_html(f"{caminhoSF+pasta_saida}{nome_figura}.html")
    #fig.write_image(f"{caminhoSF}{nome_figura}.png")
