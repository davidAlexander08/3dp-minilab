import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px
from dadosTabela import DadosMensais
from dadosSemanais import DadosSemanais
import numpy as np
from ParPGevazp import *
from ParPAGevazp import *
from matrizCarga import *
from ruidos import *
from posto import Posto
from log3p import *
#df_parp = DadosSemanais().dados

ordemMaxima = 6
arq = "/home/david/git/3dp-minilab/CenariosSemanais/vazoesMensaisCamargos.csv"
df_camargos = DadosMensais(arq).dados
#arq = "/home/david/git/3dp-minilab/CenariosSemanais/vazoesDiariasCamargos.csv"
#df_camargos = DadosSemanais(arq).dados


coef_residuos_camargos = exec_PARP(df_camargos, ordemMaxima)
posto_camargos = Posto()
posto_camargos.historico = df_camargos
posto_camargos.codigo = 1
posto_camargos.coefs = coef_residuos_camargos[0]
posto_camargos.residuos = coef_residuos_camargos[1]


arq = "/home/david/git/3dp-minilab/CenariosSemanais/vazoesMensaisFurnas.csv"
df_furnas = DadosMensais(arq).dados
#arq = "/home/david/git/3dp-minilab/CenariosSemanais/vazoesDiariasFurnas.csv"
#df_furnas = DadosSemanais(arq).dados

coef_residuos_furnas = exec_PARP(df_furnas, ordemMaxima)
#coef_residuos_furnas = exec_PARPA(df_furnas, ordemMaxima)
posto_furnas = Posto()
posto_furnas.historico = df_furnas
posto_furnas.codigo = 2
posto_furnas.coefs = coef_residuos_furnas[0]
posto_furnas.residuos = coef_residuos_furnas[1]



mapaCodigoPosto = {}
mapaCodigoPosto[posto_camargos.codigo] = posto_camargos
mapaCodigoPosto[posto_furnas.codigo] = posto_furnas

lista_postos = []
lista_postos.append(posto_camargos)
lista_postos.append(posto_furnas)

mapaMatrizCorrelacoesPer = retornaMatrizCarga(lista_postos)
print(mapaMatrizCorrelacoesPer)

arq = "/home/david/git/3dp-minilab/CenariosSemanais/mapaPeriodoEstudo.csv"
df_mapaPeriodoEstudo = pd.read_csv(arq)

arq = "/home/david/git/3dp-minilab/CenariosSemanais/arvore_julia.csv"
df_arvore = pd.read_csv(arq)
print(df_arvore)

arq = "/home/david/git/3dp-minilab/CenariosSemanais/tendencia.csv"
df_tendencia = pd.read_csv(arq)
print(df_tendencia)


mapa_df_CenarioPosto = {}
for posto in lista_postos:
    mapa_df_CenarioPosto[posto.codigo] = df_arvore.copy()

def getPaiTendencia(no, df_tendencia):
    pai = df_tendencia.loc[df_tendencia["NO"] == no]["NO_PAI"].reset_index(drop = True).iloc[0]
    return pai

def getPai(no, dfArvore):
    pai = dfArvore.loc[dfArvore["NO"] == no]["NO_PAI"].reset_index(drop = True).iloc[0]
    return pai

def getFilhos(no, dfArvore):
    df_filhos = dfArvore.loc[dfArvore["NO_PAI"] == no]["NO"]
    return df_filhos.tolist()

def retornaNoPassado(no, df_arvore , df_tendencia):
    if(no <= 0):
        return getPaiTendencia(no, df_tendencia)
    else:
        return getPai(no, df_arvore)
     
def retornaVazaoNo(no, df_arvore , df_tendencia, codigo):
    if(no <= 1):
        return df_tendencia.loc[(df_tendencia["NO"] == no) & (df_tendencia["POSTO"] == codigo)]["VAZAO"].reset_index(drop = True).iloc[0]
    else:
        return df_arvore.loc[df_arvore["NO"] == no]["VAZAO"].reset_index(drop = True).iloc[0]

def percorrePassado(no_aux, df_arvore, df_tendencia, posto, df_coef_periodo):
    parteDeterministica = 0
    for periodo_anterior in df_coef_periodo["per_anterior"].unique():
        media_Anterior = posto.historico.loc[(posto.historico["periodo"] == periodo_anterior)].reset_index(drop = True)["vazao"].mean()
        desvio_Anterior = posto.historico.loc[(posto.historico["periodo"] == periodo_anterior)].reset_index(drop = True)["vazao"].std(ddof=0)
        coef = df_coef_periodo.loc[(df_coef_periodo["per_anterior"] == periodo_anterior)]["coef"].reset_index(drop = True).iloc[0]
        pai = retornaNoPassado(no_aux, df_arvore , df_tendencia)
        vazao_passada = retornaVazaoNo(pai, df_arvore, df_tendencia, posto.codigo)
        #print("pai: ", pai, " vazao: ", vazao_passada)
        parteDeterministica += ((vazao_passada-media_Anterior)/desvio_Anterior)*coef
        #print(" parteDeterministica: " , parteDeterministica , " periodo_anterior: " , periodo_anterior ," media: " , media_Anterior , " desvio: " , desvio_Anterior , " vazao_passada: " , vazao_passada , " coef: " , coef )             
        no_aux = pai
    return parteDeterministica

def retornaTuplaRuidosCorrelacionados(lista_postos, periodo_arvore, periodoHistorico, aberturas):
    matrizRuidos = geraMatrizRuidosPostos(lista_postos, periodo_arvore, periodoHistorico)
    tupla = agregaRuidosKmeansMatriz(len(aberturas), matrizRuidos, lista_postos)
    matrizRuidosAgregados = tupla[0]
    probabilidades = tupla[1]
    matrizCargaPer = mapaMatrizCorrelacoesPer[periodoHistorico]
    ruidosCorrelacinados = np.dot(matrizCargaPer, matrizRuidosAgregados.T).T
    turpla_correl = [ruidosCorrelacinados , probabilidades]
    return turpla_correl

def percorreArvore(lista_inicio, df_arvore, df_tendencia, lista_postos, df_mapaPeriodoEstudo, mapaMatrizCorrelacoesPer, mapa_df_CenarioPosto, lista_df_caminho):
    for no_inicial in lista_inicio:
        aberturas = getFilhos(no_inicial, df_arvore)
        if(len(aberturas) == 0):
            lista_caminho = []
            lista_caminho.append(no_inicial)
            no_aux = no_inicial
            while(no_aux != 1):
                pai = retornaNoPassado(no_aux, df_arvore , df_tendencia)
                lista_caminho.append(pai)
                no_aux = pai
            ordem = 1
            
            lista_caminho = [int(item) for item in lista_caminho]
            #print(lista_caminho)
            for elemento in list(reversed(lista_caminho)):
                lista_df_caminho.append(pd.DataFrame({"NoFinal":[no_inicial], "Ordem":[ordem], "Caminho":[elemento]}))
                ordem += 1
        if(len(aberturas) != 0):
            periodo_arvore = df_arvore.loc[(df_arvore["NO"] == aberturas[0])].reset_index(drop = True)["PER"].iloc[0]
            #print(periodo_arvore)
            #print(df_mapaPeriodoEstudo)
            #print(df_mapaPeriodoEstudo.loc[(df_mapaPeriodoEstudo["PERIODO"] == periodo_arvore)].reset_index(drop = True))
            periodoHistorico = df_mapaPeriodoEstudo.loc[(df_mapaPeriodoEstudo["PERIODO"] == periodo_arvore)].reset_index(drop = True)["HISTORICO"].iloc[0]
            tupla  = retornaTuplaRuidosCorrelacionados(lista_postos, periodo_arvore, periodoHistorico, aberturas)
            ruidosCorrelacinados = tupla[0]
            probabilidades = tupla[1]
            for posto in lista_postos:               
                ruidosCorrelacinados_posto = ruidosCorrelacinados[:,posto.codigo-1]
                df_coef_periodo = posto.coefs.loc[(posto.coefs["periodo"] == periodoHistorico)].reset_index(drop = True)
                df_residuos_periodo = posto.residuos.loc[(posto.residuos["periodo"] == periodoHistorico)].reset_index(drop = True)
                df_posto_per = posto.historico.loc[(posto.historico["periodo"] == periodoHistorico)].reset_index(drop = True)
                desvio = df_posto_per["vazao"].std(ddof=0)
                media = df_posto_per["vazao"].mean()
                determ = percorrePassado(aberturas[0], mapa_df_CenarioPosto[posto.codigo], df_tendencia, posto, df_coef_periodo)
                determ += determ*desvio + media
                ruidoslog3p = transformaLog3P(ruidosCorrelacinados_posto, df_posto_per, df_residuos_periodo, determ)
                contador = 0
                for no in aberturas: 
                    print("codigo: ", posto.codigo, " no: ", no, " periodoHistorico: ", periodoHistorico)
                    #mapa_df_CenarioPosto[posto.codigo].loc[mapa_df_CenarioPosto[posto.codigo]["NO"] == no,"VAZAO"] = determ + ruidoslog3p[contador]*desvio
                    mapa_df_CenarioPosto[posto.codigo].loc[mapa_df_CenarioPosto[posto.codigo]["NO"] == no,"PROB"] = probabilidades[contador]
                    mapa_df_CenarioPosto[posto.codigo].loc[mapa_df_CenarioPosto[posto.codigo]["NO"] == no,"VAZAO"] = df_posto_per["vazao"].sample(n=1).reset_index(drop =True).iloc[0]
                    mapa_df_CenarioPosto[posto.codigo].loc[mapa_df_CenarioPosto[posto.codigo]["NO"] == no,"PROB"] = 1/len(aberturas)
                    contador += 1
        if(len(aberturas) != 0):
            percorreArvore(aberturas , df_arvore, df_tendencia, lista_postos, df_mapaPeriodoEstudo, mapaMatrizCorrelacoesPer, mapa_df_CenarioPosto, lista_df_caminho)
lista_inicio = [1]
for posto in lista_postos:
    vazao_primeiro_estagio = df_tendencia.loc[(df_tendencia["POSTO"] == posto.codigo) & (df_tendencia["NO"] == 1)].reset_index(drop = True)["VAZAO"].iloc[0]
    mapa_df_CenarioPosto[posto.codigo].loc[(mapa_df_CenarioPosto[posto.codigo]["NO"] == 1), "VAZAO"] = vazao_primeiro_estagio
    mapa_df_CenarioPosto[posto.codigo].loc[(mapa_df_CenarioPosto[posto.codigo]["NO"] == 1), "PROB"] = 1.0

lista_df_caminho = []
percorreArvore(lista_inicio, df_arvore, df_tendencia, lista_postos, df_mapaPeriodoEstudo, mapaMatrizCorrelacoesPer, mapa_df_CenarioPosto, lista_df_caminho)
print(mapa_df_CenarioPosto)

df_caminhos = pd.concat(lista_df_caminho).reset_index(drop = True)
for posto in lista_postos:
    fig = go.Figure()
    df = mapa_df_CenarioPosto[posto.codigo]
    df.to_csv("cenarios_"+str(posto.codigo)+".csv")
    for caminho in list(df_caminhos["NoFinal"].unique()):
        df_caminho_singular = df_caminhos.loc[(df_caminhos["NoFinal"] == caminho)].reset_index(drop = True)
        #print(df_caminho_singular)
        lista_valores_caminho = []
        lista_periodos_caminho = []
        for no in df_caminho_singular["Caminho"].unique():
            df_no = df.loc[(df["NO"] == no)].reset_index(drop = True)
            valor_vazao = df_no["VAZAO"].iloc[0]
            valor_temporal = df_no["PER"].iloc[0]
            lista_valores_caminho.append(valor_vazao)
            lista_periodos_caminho.append(valor_temporal)
        fig.add_trace(go.Scatter(
                        x=lista_periodos_caminho,
                        y=lista_valores_caminho,
                        mode="lines", name="cenarios", showlegend=False,legendgroup="cenarios",
                        marker=dict(size=6, color="blue")))
    fig.update_layout(title_text="Teste Cenários Sintéticos Posto "+str(posto.codigo))
    fig.write_html("Teste Cenários Sintéticos Posto "+ str(posto.codigo)+".html",include_plotlyjs='cdn')
    for per in df["PER"].unique():
        mean = df.loc[(df["PER"] == per)].reset_index(drop = True)["VAZAO"].mean()
        desv = df.loc[(df["PER"] == per)].reset_index(drop = True)["VAZAO"].std(ddof = 0)
        print("Sintetico Periodo: ", per, " Média: ", mean, " Desvio: ", desv)




    fig = go.Figure()
    posto.historico.to_csv("historico_"+str(posto.codigo)+".csv")
    #print(posto.historico)
    for ano in posto.historico["Data"].dt.year.unique():
        df_ano = posto.historico.loc[(posto.historico["Data"].dt.year == ano)].reset_index(drop = True)
        fig.add_trace(go.Scatter(
                        x=df_ano["periodo"],
                        y=df_ano["vazao"],
                        mode="lines", name="cenarios", showlegend=False,legendgroup="cenarios",
                        marker=dict(size=6, color="blue")))
    fig.update_layout(title_text="Histórico Posto "+str(posto.codigo))
    fig.write_html("Histórico Posto "+ str(posto.codigo)+".html",include_plotlyjs='cdn')
    for per in posto.historico["periodo"].unique():
        mean = posto.historico.loc[(posto.historico["periodo"] == per)].reset_index(drop = True)["vazao"].mean()
        desv = posto.historico.loc[(posto.historico["periodo"] == per)].reset_index(drop = True)["vazao"].std(ddof = 0)
        asim = posto.historico.loc[(posto.historico["periodo"] == per)].reset_index(drop = True)["vazao"].skew()
        print("Historico Periodo: ", per, " Média: ", mean, " Desvio: ", desv, " Assimetria: ", asim)
    print("Geral Média: ", posto.historico["vazao"].mean(), " Desvio: ", posto.historico["vazao"].std(ddof = 0), " Assimetria: ", posto.historico["vazao"].skew(), " Max: ", posto.historico["vazao"].max(), " Min: ", posto.historico["vazao"].min())

for posto in lista_postos:
    mapa_df_CenarioPosto[posto.codigo]["NOME_UHE"] = posto.codigo

df_final = pd.concat(mapa_df_CenarioPosto).reset_index(drop = True)
print(df_final)
arq = "/home/david/git/3dp-minilab/cenarios/out/vazao.csv"
df_final.to_csv(arq, index=False)

arq = "/home/david/git/3dp-minilab/cenarios/out/probabilidades.csv"
df_prob = pd.DataFrame()
df_prob["NO"] = df_final["NO"]
df_prob["PROBABILIDADE"] = df_final["PROB"]
df_prob.to_csv(arq, index=False)

#print(df_parp.head(25))