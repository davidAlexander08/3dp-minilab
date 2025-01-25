import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px
from dadosTabela import DadosMensais
from dadosSemanais import DadosSemanais
import numpy as np
from scipy.linalg import solve
from scipy.linalg import svd
import math
from ParPGevazp import *
from ParPAGevazp import *
from matrizCarga import *
from ruidos import *
from posto import Posto
#df_parp = DadosSemanais().dados

ordemMaxima = 6
arq = "/home/david/git/3dp-minilab/CenariosSemanais/vazoesMensaisCamargos.csv"

df_camargos = DadosMensais(arq).dados
coef_residuos_camargos = exec_PARP(df_camargos, ordemMaxima)
posto_camargos = Posto()
posto_camargos.historico = df_camargos
posto_camargos.coefs = coef_residuos_camargos[0]
posto_camargos.residuos = coef_residuos_camargos[1]

arq = "/home/david/git/3dp-minilab/CenariosSemanais/vazoesMensaisFurnas.csv"
df_furnas = DadosMensais(arq).dados
coef_residuos_furnas = exec_PARP(df_furnas, ordemMaxima)
#coef_residuos_furnas = exec_PARPA(df_furnas, ordemMaxima)
posto_furnas = Posto()
posto_furnas.historico = df_furnas
posto_furnas.coefs = coef_residuos_furnas[0]
posto_furnas.residuos = coef_residuos_furnas[1]


mapaCodigoPosto = {}
mapaCodigoPosto[1] = posto_camargos
mapaCodigoPosto[2] = posto_furnas





mapaCodigoCoef = {}
mapaCodigoCoef[1] = coef_residuos_camargos[0]
mapaCodigoCoef[2] = coef_residuos_furnas[0]

mapaCodigoResiduos = {}
mapaCodigoResiduos[1] = coef_residuos_camargos[1]
mapaCodigoResiduos[2] = coef_residuos_furnas[1]

mapaCodigoDataFramePosto = {}
mapaCodigoDataFramePosto[1] = df_camargos
mapaCodigoDataFramePosto[2] = df_furnas

lista_postos = []
lista_postos.append(df_camargos)
lista_postos.append(df_furnas)
mapaMatrizCorrelacoesPer = retornaMatrizCarga(lista_postos)
print(mapaMatrizCorrelacoesPer)

##SORTEIO DOS RUIDOS
#periodoInicial = 11
#numeroDeAberturasPeriodo = 3
#matrizRuidos = geraMatrizRuidosPostos(lista_postos)
#tupla = agregaRuidosKmeansMatriz(numeroDeAberturasPeriodo, matrizRuidos, lista_postos)
###Clusteriza ruidos pelo método do GEVAZP
#matrizRuidosAgregados = tupla[0]
#probabilidades = tupla[1]
#matrizCargaPer = mapaMatrizCorrelacoesPer[periodoInicial]
#ruidosCorrelacinados = np.dot(matrizCargaPer, matrizRuidosAgregados.T).T
#print("ruidosCorrelacinados: ", ruidosCorrelacinados)

def calculaVazaoMinima(dfTemporal):
 # Step 1: Set eas to assimetriaSerie or 0.05 if it is <= 0
    eas = dfTemporal["vazao"].skew()
    mediaSerie = dfTemporal["vazao"].mean()
    desviopadraoSerie = dfTemporal["vazao"].std(ddof = 0)
    if eas <= 0:
        eas = 0.05
    
    # Step 2: Calculate A, B, C, and FI
    A = 1 + (eas ** 2) / 2
    B = math.sqrt((eas ** 2) / 2 + (eas ** 4) / 4)
    C = 1 / 3
    FI = (A + B) ** C + (A - B) ** C - 1
    
    # Step 3: Calculate deslocamento
    deslocamento = (mediaSerie - math.sqrt((desviopadraoSerie ** 2) / (FI - 1)))
    vazaoMinima = min(dfTemporal["vazao"])
    D = mediaSerie - (3 * desviopadraoSerie)
    if vazaoMinima >= 0:
        Z = 0
        D = max(Z, D)
    if D < 0:
        if eas >= 4:
            vazaoMinima = max(D, vazaoMinima * 1.4)
        elif eas >= 2:
            if deslocamento >= 0:
                A = min(D, vazaoMinima)
                vazaoMinima = max(D, A * 1.5)
            else:
                vazaoMinima = max(D, vazaoMinima * 1.5)
        elif eas >= 1:
            vazaoMinima = max(D, vazaoMinima * 1.65)
        else:
            vazaoMinima = max(D, vazaoMinima * 1.85)
    else:
        if eas >= 4:
            vazaoMinima = max(D, vazaoMinima * 0.6)
        elif eas >= 2:
            if deslocamento >= 0:
                A = min(D, vazaoMinima)
                vazaoMinima = max(D, A * 0.5)
            else:
                vazaoMinima = max(D, vazaoMinima * 0.5)
        elif eas >= 1:
            vazaoMinima = max(D, vazaoMinima * 0.35)
        else:
            vazaoMinima = max(D, vazaoMinima * 0.15)
    
    # Return the final vazaoMinima
    return vazaoMinima



def transformaLog3P(ruidosCorrelacinados_posto, df_posto_per, df_residuos_periodo, parteDeterministica):
    desvio = df_posto_per["vazao"].std(ddof = 0)
    media = df_posto_per["vazao"].mean()
    desvioResiduos = df_residuos_periodo["residuo"].std(ddof = 0)
    mediaResiduos = df_residuos_periodo["residuo"].mean()

    vazaoMinima = calculaVazaoMinima(df_posto_per)
    print("vazaoMinima: ", vazaoMinima , " parteDeterministica: ", parteDeterministica , " desvio: ", desvio)
    deslocamento = (vazaoMinima - parteDeterministica)/desvio
    # Calculate BFI, BMEDN, BDPADN, NI, and EXC
    BFI = 1 + (desvioResiduos ** 2) / ((mediaResiduos - deslocamento) ** 2)
    BMEDN = 0.5 * np.log((desvioResiduos ** 2) / (BFI ** 2 - BFI))
    BDPADN = np.sqrt(np.log(BFI))
    NI = np.sqrt(np.exp(BDPADN ** 2) - 1)
    EXC = (NI ** 8 + 6 * NI ** 6 + 15 * NI ** 4 + 16 * NI ** 2)

    ruidoslog3p = np.zeros_like(ruidosCorrelacinados_posto)

    for abertura in range(0, ruidosCorrelacinados_posto.shape[0]):
        ruidoslog3p[abertura] = np.exp(BMEDN + ruidosCorrelacinados_posto[abertura] * BDPADN) + deslocamento
        print("BMEDN: ", BMEDN , " ruidosCorrelacinados_posto[abertura]: ", ruidosCorrelacinados_posto[abertura], " BDPADN: ", BDPADN , " deslocamento: ", deslocamento)
    return ruidoslog3p


arq = "/home/david/git/3dp-minilab/CenariosSemanais/mapaPeriodoEstudo.csv"
df_mapaPeriodoEstudo = pd.read_csv(arq)

arq = "/home/david/git/3dp-minilab/CenariosSemanais/arvore_julia.csv"
df_arvore = pd.read_csv(arq)
print(df_arvore)


arq = "/home/david/git/3dp-minilab/CenariosSemanais/tendencia.csv"
df_tendencia = pd.read_csv(arq)
print(df_tendencia)


mapa_df_CenarioPosto = {}
for codigo in mapaCodigoDataFramePosto:
    mapa_df_CenarioPosto[codigo] = df_arvore.copy()

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

def percorrePassado(no_aux, df_arvore, df_tendencia, codigo, df_coef_periodo, df_posto):
    parteDeterministica = 0
    for periodo_anterior in df_coef_periodo["per_anterior"].unique():
        media_Anterior = df_posto.loc[(df_posto["periodo"] == periodo_anterior)].reset_index(drop = True)["vazao"].mean()
        desvio_Anterior = df_posto.loc[(df_posto["periodo"] == periodo_anterior)].reset_index(drop = True)["vazao"].std(ddof=0)
        coef = df_coef_periodo.loc[(df_coef_periodo["per_anterior"] == periodo_anterior)]["coef"].reset_index(drop = True).iloc[0]
        pai = retornaNoPassado(no_aux, df_arvore , df_tendencia)
        vazao_passada = retornaVazaoNo(pai, df_arvore, df_tendencia, codigo)
        print("pai: ", pai, " vazao: ", vazao_passada)
        parteDeterministica += ((vazao_passada-media_Anterior)/desvio_Anterior)*coef
        print(" parteDeterministica: " , parteDeterministica , " periodo_anterior: " , periodo_anterior ," media: " , media_Anterior , " desvio: " , desvio_Anterior , " vazao_passada: " , vazao_passada , " coef: " , coef )             
        no_aux = pai
    return parteDeterministica
def percorreArvore(lista_inicio, df_arvore, df_tendencia, lista_postos, df_mapaPeriodoEstudo, mapaMatrizCorrelacoesPer, mapaCodigoDataFramePosto, mapa_df_CenarioPosto, mapaCodigoCoef, mapaCodigoResiduos):
    for no_inicial in lista_inicio:
        aberturas = getFilhos(no_inicial, df_arvore)

        if(len(aberturas) != 0):
            matrizRuidos = geraMatrizRuidosPostos(lista_postos)
            tupla = agregaRuidosKmeansMatriz(len(aberturas), matrizRuidos, lista_postos)
            matrizRuidosAgregados = tupla[0]
            probabilidades = tupla[1]
            periodo_arvore = df_arvore.loc[(df_arvore["NO"] == aberturas[0])].reset_index(drop = True)["PER"].iloc[0]
            periodoHistorico = df_mapaPeriodoEstudo.loc[(df_mapaPeriodoEstudo["PERIODO"] == periodo_arvore)]["HISTORICO"].iloc[0]
            matrizCargaPer = mapaMatrizCorrelacoesPer[periodoHistorico]
            ruidosCorrelacinados = np.dot(matrizCargaPer, matrizRuidosAgregados.T).T
            print("matrizRuidosAgregados: ", matrizRuidosAgregados)
            print("probabilidades: ", probabilidades)
            print("periodo_arvore: ", periodo_arvore)
            print("periodoHistorico: ", periodoHistorico)
            print("matrizCargaPer: ", matrizCargaPer)
            print("ruidosCorrelacinados: ", ruidosCorrelacinados)
            for codigo in mapaCodigoDataFramePosto:               
                ruidosCorrelacinados_posto = ruidosCorrelacinados[:,codigo-1]
                df_coef_periodo = mapaCodigoCoef[codigo].loc[(mapaCodigoCoef[codigo]["periodo"] == periodoHistorico)].reset_index(drop = True)
                df_residuos_periodo = mapaCodigoResiduos[codigo].loc[(mapaCodigoResiduos[codigo]["periodo"] == periodoHistorico)].reset_index(drop = True)
                df_posto = mapaCodigoDataFramePosto[codigo]
                df_posto_per = df_posto.loc[(df_posto["periodo"] == periodoHistorico)].reset_index(drop = True)
                desvio = df_posto_per["vazao"].std(ddof=0)
                media = df_posto_per["vazao"].mean()
                print("df_coef_periodo: ", df_coef_periodo)
                print("df_residuos_periodo: ", df_residuos_periodo)
                determ = percorrePassado(aberturas[0], mapa_df_CenarioPosto[codigo], df_tendencia, codigo, df_coef_periodo, df_posto)
                determ += determ*desvio + media
                ruidoslog3p = transformaLog3P(ruidosCorrelacinados_posto, df_posto_per, df_residuos_periodo, determ)
                print("ruidoslog3p: ", ruidoslog3p)
                contador = 0
                for no in aberturas: 
                    print("codigo: ", codigo, " no: ", no)
                    mapa_df_CenarioPosto[codigo].loc[mapa_df_CenarioPosto[codigo]["NO"] == no,"VAZAO"] = determ + ruidoslog3p[contador]*desvio
                    mapa_df_CenarioPosto[codigo].loc[mapa_df_CenarioPosto[codigo]["NO"] == no,"PROB"] = probabilidades[contador]#
                    contador += 1
                print(mapa_df_CenarioPosto[codigo])
        if(len(aberturas) != 0):
            percorreArvore(aberturas , df_arvore, df_tendencia, lista_postos, df_mapaPeriodoEstudo, mapaMatrizCorrelacoesPer, mapaCodigoDataFramePosto, mapa_df_CenarioPosto, mapaCodigoCoef, mapaCodigoResiduos)
lista_inicio = [1]
for codigo in mapaCodigoDataFramePosto:
    vazao_primeiro_estagio = df_tendencia.loc[(df_tendencia["POSTO"] == codigo) & (df_tendencia["NO"] == 1)].reset_index(drop = True)["VAZAO"].iloc[0]
    mapa_df_CenarioPosto[codigo].loc[(mapa_df_CenarioPosto[codigo]["NO"] == 1), "VAZAO"] = vazao_primeiro_estagio

percorreArvore(lista_inicio, df_arvore, df_tendencia, lista_postos, df_mapaPeriodoEstudo, mapaMatrizCorrelacoesPer, mapaCodigoDataFramePosto, mapa_df_CenarioPosto, mapaCodigoCoef, mapaCodigoResiduos)
exit(1)


for per in df_arvore["PER"].unique(): ##Continuar depois
    lista_nos  = df_arvore.loc[df_arvore["PER"] == per]["NO"].unique()
    aberturas = len(lista_nos)
    
    matrizRuidos = geraMatrizRuidosPostos(lista_postos)
    tupla = agregaRuidosKmeansMatriz(aberturas, matrizRuidos, lista_postos)
    matrizRuidosAgregados = tupla[0]
    probabilidades = tupla[1]
    print("probabilidades: ", probabilidades)
    periodoHistorico = df_mapaPeriodoEstudo.loc[(df_mapaPeriodoEstudo["PERIODO"] == per)]["HISTORICO"].iloc[0]
    matrizCargaPer = mapaMatrizCorrelacoesPer[periodoHistorico]
    ruidosCorrelacinados = np.dot(matrizCargaPer, matrizRuidosAgregados.T).T
    print("ruidosCorrelacinados: ", ruidosCorrelacinados)
    for codigo in mapaCodigoDataFramePosto:
        ruidosCorrelacinados_posto = ruidosCorrelacinados[:,codigo-1]
        df_tendencia_posto = df_tendencia.loc[(df_tendencia["POSTO"] == codigo)]
        if(per == 1):
            mapa_df_CenarioPosto[codigo].loc[mapa_df_CenarioPosto[codigo]["NO"] ==1,"VAZAO"] = df_tendencia_posto.loc[(df_tendencia_posto["NO"] == 1),"VAZAO"].iloc[0]
            mapa_df_CenarioPosto[codigo].loc[mapa_df_CenarioPosto[codigo]["NO"] ==1,"PROB"] = 1.0
        else:
            contador = 0
            df_coef_periodo = mapaCodigoCoef[codigo].loc[(mapaCodigoCoef[codigo]["periodo"] == periodoHistorico)].reset_index(drop = True)
            df_residuos_periodo = mapaCodigoResiduos[codigo].loc[(mapaCodigoResiduos[codigo]["periodo"] == periodoHistorico)].reset_index(drop = True)
            df_posto = mapaCodigoDataFramePosto[codigo]
            df_posto_per = df_posto.loc[(df_posto["periodo"] == periodoHistorico)].reset_index(drop = True)
            desvio = df_posto_per["vazao"].std(ddof=0)
            media = df_posto_per["vazao"].mean()


            no_pai =  df_arvore.loc[df_arvore["NO"] == lista_nos[0]]["NO_PAI"].reset_index(drop = True).iloc[0]
            print("no_pai: ", no_pai)

            parteDeterministica = 0
            contador_no_anterior = no_pai
            for periodo_anterior in df_coef_periodo["per_anterior"].unique():
                media_Anterior = df_posto.loc[(df_posto["periodo"] == periodo_anterior)].reset_index(drop = True)["vazao"].mean()
                desvio_Anterior = df_posto.loc[(df_posto["periodo"] == periodo_anterior)].reset_index(drop = True)["vazao"].std(ddof=0)
                coef = df_coef_periodo.loc[(df_coef_periodo["per_anterior"] == periodo_anterior)]["coef"].reset_index(drop = True).iloc[0]
                if(contador_no_anterior <= 1):
                    tendencia = df_tendencia_posto.loc[(df_tendencia_posto["NO"] == contador_no_anterior)]["VAZAO"].reset_index(drop = True).iloc[0]
                else:
                    tendencia = mapa_df_CenarioPosto[codigo].loc[mapa_df_CenarioPosto[codigo]["NO"] ==contador_no_anterior,"VAZAO"].reset_index(drop = True).iloc[0]    
                parteDeterministica += ((tendencia-media_Anterior)/desvio_Anterior)*coef
                print(" no_anterior: " , contador_no_anterior, " parteDeterministica: " , parteDeterministica , " periodo_anterior: " , periodo_anterior ," media: " , media_Anterior , " desvio: " , desvio_Anterior , " tendencia: " , tendencia , " coef: " , coef )              
                contador_no_anterior -= 1
            parteDeterministica += parteDeterministica*desvio + media   
            ruidoslog3p = transformaLog3P(ruidosCorrelacinados_posto, df_posto_per, df_residuos_periodo, parteDeterministica)
            print("ruidoslog3p: ", ruidoslog3p)
            
            contador = 0
            for codigo_no in lista_nos:
                mapa_df_CenarioPosto[codigo].loc[mapa_df_CenarioPosto[codigo]["NO"] == codigo_no,"VAZAO"] = ruidoslog3p[contador]
                mapa_df_CenarioPosto[codigo].loc[mapa_df_CenarioPosto[codigo]["NO"] == codigo_no,"PROB"] = probabilidades[contador]#
                contador += 1
        print(mapa_df_CenarioPosto[codigo])
    if(per == 4):
        exit(1)
        #if(codigo_no in df_tendencia_posto["NO"].unique()):
        #    df_posto.loc[df_posto["NO"] ==codigo_no,"VAZAO"] = df_tendencia_posto.loc[df_tendencia_posto["NO"] == codigo_no,"VAZAO"].iloc[0]
        #else:
        #    print(df_posto.loc[df_posto["NO"] == codigo_no])
        #    per_otimizacao = df_posto.loc[df_posto["NO"] == codigo_no].reset_index(drop = True)["PER"].iloc[0]
        #    periodoHistorico = df_mapaPeriodoEstudo.loc[(df_mapaPeriodoEstudo["PERIODO"] == per_otimizacao)]["HISTORICO"].iloc[0]














#print(df_anual.head(25))
#print(df_parp.head(25))