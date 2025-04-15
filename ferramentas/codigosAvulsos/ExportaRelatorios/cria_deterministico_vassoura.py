import numpy as np
import pandas as pd
from scipy.stats import wasserstein_distance
from scipy.stats import ksone
from scipy.stats import ks_2samp
import plotly.graph_objects as go
from scipy.stats import chisquare
from scipy.stats import mannwhitneyu
from statsmodels.stats.weightstats import DescrStatsW
import plotly.graph_objects as go
from scipy.stats import linregress
from sklearn.metrics import r2_score
from plotly.subplots import make_subplots
from inewave.newave import Confhd
from inewave.newave import Hidr



caminho_relatorio = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\Capitulo_5\\caso_mini_500Cen_sorteio_mensais\\avaliaArvores\\A_125_2_2\\estatisticasArvores_75_2_2.csv"
caso_saida = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\Capitulo_5\\caso_mini_500Cen_sorteio_mensais\\avaliaArvores"
df_estatistica = pd.read_csv(caminho_relatorio, sep=";")
df_estatistica = df_estatistica.dropna().reset_index(drop = True)
print(df_estatistica)

caminho_pente = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\Capitulo_5\\caso_mini_500Cen_sorteio_mensais"
df_vazoes = pd.read_csv(caminho_pente+"\\cenarios.csv", sep = ",")
print(df_vazoes)

df_arvore_orig = pd.read_csv(caminho_pente+"\\arvore.csv", sep = ",")
print(df_arvore_orig)

postos = df_estatistica["POSTO"].unique()
#print(postos)
estagios = df_estatistica["EST"].unique()
#print(estagios)
#print(sorted(estagios))

lista_df_vazoes_deterministico = []
lista_df_arvore_deterministica = []
df_no_1 = df_vazoes.loc[(df_vazoes["NO"] == 1)]
lista_df_vazoes_deterministico.append(df_no_1)

lista_df_arvore_deterministica.append(
    pd.DataFrame(
        {
            "NO_PAI":[0],
            "NO":[1],
            "Abertura":[1],
            "PER":[1],
            "PROB":[1.0]
        }
    )
)
for est in sorted(estagios):
    df_est = df_estatistica.loc[(df_estatistica["EST"] == est)]
    #print(df_est["mediaOrig"].reset_index(drop = True))
    #print(df_est["POSTO"].reset_index(drop = True))
    #print(df_est.columns)
    df_temp = pd.DataFrame()
    df_temp["NOME_UHE"] = df_est["POSTO"].reset_index(drop = True)
    df_temp["NO"] = est
    df_temp["VAZAO"] = df_est["mediaOrig"].reset_index(drop = True).astype(str).str.replace(",", ".").astype(float)
    #print(df_temp)
    lista_df_vazoes_deterministico.append(df_temp)
    lista_df_arvore_deterministica.append(
        pd.DataFrame(
            {
                "NO_PAI":[est-1],
                "NO":[est],
                "Abertura":[1],
                "PER":[est],
                "PROB":[1.0]
            }
        )
    )
df_vazoes_determinitico = pd.concat(lista_df_vazoes_deterministico).reset_index(drop = True)
df_vazoes_determinitico.to_csv(caso_saida+"\\Deterministico"+f"\\cenarios.csv", index = False)
print(df_vazoes_determinitico)

df_arvore_determinitico = pd.concat(lista_df_arvore_deterministica).reset_index(drop = True)
df_arvore_determinitico.to_csv(caso_saida+"\\Deterministico"+f"\\arvore.csv", index = False)
print(df_arvore_determinitico)


################### CRIA VASSOURA
lista_df_vazoes_vassoura = []
lista_df_arvore_vassoura = []
df_no_1 = df_vazoes.loc[(df_vazoes["NO"] == 1)]
lista_df_vazoes_vassoura.append(df_no_1)
lista_df_arvore_vassoura.append(
    pd.DataFrame(
        {
            "NO_PAI":[0],
            "NO":[1],
            "Abertura":[1],
            "PER":[1],
            "PROB":[1.0]
        }
    )
)
ultimo_estagio = max(estagios)
estagios = estagios[estagios != ultimo_estagio]
for est in sorted(estagios):
    df_est = df_estatistica.loc[(df_estatistica["EST"] == est)]
    #print(df_est["mediaOrig"].reset_index(drop = True))
    #print(df_est["POSTO"].reset_index(drop = True))
    #print(df_est.columns)
    df_temp = pd.DataFrame()
    df_temp["NOME_UHE"] = df_est["POSTO"].reset_index(drop = True)
    df_temp["NO"] = est
    df_temp["VAZAO"] = df_est["mediaOrig"].reset_index(drop = True).astype(str).str.replace(",", ".").astype(float)
    #print(df_temp)
    lista_df_vazoes_vassoura.append(df_temp)
    lista_df_arvore_vassoura.append(
        pd.DataFrame(
            {
                "NO_PAI":[est-1],
                "NO":[est],
                "Abertura":[1],
                "PER":[est],
                "PROB":[1.0]
            }
        )
    )


nos_ultimo_estagio = df_arvore_orig.loc[(df_arvore_orig["PER"] == ultimo_estagio)]["NO"].unique()
print(nos_ultimo_estagio)
contador_no = ultimo_estagio
contador_aberturas = 1
for no_ultimo_estagio in nos_ultimo_estagio:
    vazoes_no = df_vazoes.loc[(df_vazoes["NO"] == no_ultimo_estagio)].reset_index(drop = True)
    vazoes_no["NO"] = contador_no
    #print(vazoes_no)
    lista_df_vazoes_vassoura.append(vazoes_no)
    lista_df_arvore_vassoura.append(
        pd.DataFrame(
            {
                "NO_PAI":[ultimo_estagio-1],
                "NO":[contador_no],
                "Abertura":[contador_aberturas],
                "PER":[ultimo_estagio],
                "PROB":[1.0/len(nos_ultimo_estagio)]
            }
        )
    )
    
    
    
    contador_no += 1
    contador_aberturas += 1
    
    #lista_df_vazoes_vassoura

df_vazoes_vassoura = pd.concat(lista_df_vazoes_vassoura).reset_index(drop = True)
df_vazoes_vassoura.to_csv(caso_saida+"\\Vassoura"+f"\\cenarios.csv", index = False)
print(df_vazoes_vassoura)

df_arvore_vassoura = pd.concat(lista_df_arvore_vassoura).reset_index(drop = True)
df_arvore_vassoura.to_csv(caso_saida+"\\Vassoura"+f"\\arvore.csv", index = False)
print(df_arvore_vassoura)

