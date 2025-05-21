import pandas as pd
from inewave.newave import Confhd
from inewave.newave import Hidr
import json
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import weibull_min
import numpy as np
import plotly.graph_objects as go


#df = pd.read_csv("Verif_NE.txt", sep=";", encoding="latin1")
df = pd.read_csv("Verif_NE.txt", sep=";", encoding="latin1")

## Realizar soma dos patamares
list_S = ["S1", "S2", "S3", "S4", "S5"]
variacoes = [" Pesada", " Media", " Leve"]
print(df)
for elemento in list_S:
    df[elemento] = df[elemento+variacoes[0]] + df[elemento+variacoes[1]] + df[elemento+variacoes[2]]
    df = df.drop(columns = [elemento+variacoes[0], elemento+variacoes[1], elemento+variacoes[2]])

df = df.drop(columns=["Fim_Sem"])
df['Ini_Sem'] = pd.to_datetime(df['Ini_Sem'], dayfirst=True)  # transforma a data corretamente
meses = [1,2,3,4,5,6,7,8,9,10,11,12]

unique_years = df["Ini_Sem"].dt.year.unique()
dicionario_anos = {}

for ano in unique_years:
    dicionario_anos[ano] = []
    lista_x = []
    for mes in meses:
        for semana in list_S:
            #print(df)
            valor = df.loc[(df["Ini_Sem"].dt.year == ano) & (df["Ini_Sem"].dt.month == mes)][semana].iloc[0]
            dicionario_anos[ano].append(valor)
            lista_x.append(str(mes)+"_"+semana)

#### MEDIA HISTORICO
dicionarioMedia_historico = {}
dicionarioDesvio_historico = {}
for mes in meses:
    for semana in list_S:
        df_temps = df.loc[(df["Ini_Sem"].dt.month == mes)].copy().reset_index(drop = True)
        media_3anos = df_temps[semana].mean()
        dicionarioMedia_historico[str(mes)+"_"+semana] = media_3anos
        dicionarioDesvio_historico[str(mes)+"_"+semana] = df_temps[semana].std()

#### MEDIA DOS ULTIMOS 3 ANOS
dicionarioMedia = {}
dicionarioDesvio = {}
df_aux = df.loc[(df["Ini_Sem"].dt.year >= 2022)].copy()
for mes in meses:
    for semana in list_S:
        df_temps = df_aux.loc[(df_aux["Ini_Sem"].dt.month == mes)].reset_index(drop = True)
        media_3anos = df_temps[semana].mean()
        dicionarioMedia[str(mes)+"_"+semana] = media_3anos
        dicionarioDesvio[str(mes)+"_"+semana] = df_temps[semana].std()



### PARAMETORS WEIBULL
weibull_params = {}
for mes in meses:
    for semana in list_S:
        df_temps = df_aux.loc[(df_aux["Ini_Sem"].dt.month == mes)].copy().reset_index(drop = True)
        data = df_temps[semana]
        c, loc, scale = weibull_min.fit(data, floc=0)  # Fix location to 0 for physical meaning
        weibull_params[str(mes)+"_"+semana] = (c, loc, scale)
print(dicionarioMedia)
print(weibull_params)


n_scenarios = 500
stochastic_scenarios = {}
for stage, (c, loc, scale) in weibull_params.items():
    samples = weibull_min.rvs(c, loc=loc, scale=scale, size=n_scenarios)
    #samples_norm = (samples - samples.min()) / (samples.max() - samples.min())
    #relative_noise = samples/samples.mean()
    #synthetic_wind = dicionarioMedia[stage] * (relative_noise)
    stochastic_scenarios[stage] = samples/5
scenario_df = pd.DataFrame(stochastic_scenarios).reset_index(drop = True)
print(scenario_df)

dicionario_media_cenarios = {}
dicionario_desvio_cenarios = {}
for mes in meses:
    for semana in list_S:
        df_temps = df_aux.loc[(df_aux["Ini_Sem"].dt.month == mes)].reset_index(drop = True)
        df_est_orig = df_temps[semana]
        df_cenarios = scenario_df[str(mes)+"_"+semana]

        dicionario_media_cenarios[str(mes)+"_"+semana] = df_cenarios.mean()
        dicionario_desvio_cenarios[str(mes)+"_"+semana] = df_cenarios.std()
        print("Media original: ", df_est_orig.mean(), " Media Cenarios: ", df_cenarios.mean(), "Desvio original: ", df_est_orig.std(), " Desvio Cenarios: ", df_cenarios.std())
scenario_df = pd.DataFrame(stochastic_scenarios)
print(scenario_df)
scenario_df.to_csv("500_cenarios_NE.csv", index = False)

#print(dicionario_media_cenarios)
#print(list(dicionario_media_cenarios.values()))
#print(list(dicionarioMedia.values()))
media_cenarios = np.array(list(dicionario_media_cenarios.values()))
desvio_cenarios = np.array(list(dicionario_desvio_cenarios.values()))
media_hist_3anos = np.array(list(dicionarioMedia.values()))
desvio_3anos = np.array(list(dicionarioDesvio.values()))
### PRINTA MEDIAS E DESVIOS
fig = go.Figure()

### MEDIA CENARIOS
fig.add_trace(go.Scatter(
    x=lista_x,
    y=media_cenarios,
    mode='lines',
    name="media_cenarios",
    showlegend = True,
    line=dict(color='black')
))

### DESVIO PADRAO POSITIVO
fig.add_trace(go.Scatter(
    x=lista_x,
    y=media_cenarios - desvio_cenarios,
    mode='lines',
    name="desv_pos",
    showlegend = False,
    line=dict(color='black', dash='dash')
))

fig.add_trace(go.Scatter(
    x=lista_x,
    y=media_cenarios + desvio_cenarios,
    mode='lines',
    name="desv_ned",
    showlegend = False,
    line=dict(color='black', dash='dash')
))


### MEDIA HISTORICO
fig.add_trace(go.Scatter(
    x=lista_x,
    y=media_hist_3anos,
    mode='lines',
    name="media_hist",
    showlegend = True,
    line=dict(color='red')
))

### DESVIO PADRAO POSITIVO
fig.add_trace(go.Scatter(
    x=lista_x,
    y=media_hist_3anos - desvio_3anos,
    mode='lines',
    name="desv_hist_pos",
    showlegend = False,
    line=dict(color='red', dash='dash')
))

fig.add_trace(go.Scatter(
    x=lista_x,
    y=media_hist_3anos + desvio_3anos,
    mode='lines',
    name="desv_hist_neg",
    showlegend = False,
    line=dict(color='red', dash='dash')
))

fig.write_html('medias_desvio.html', auto_open=False)







exit(1)
### PRINTA CENARIOS
fig = go.Figure()
for idx, row in scenario_df.iterrows():
    fig.add_trace(go.Scatter(
        x=lista_x,
        y=row.tolist(),
        mode='lines',
        name=str(ano),
        showlegend = False,
        #line=dict(color='black')
    ))

fig.update_layout(
    title="Cenários Sintéticos de Geração Eólica",
    xaxis_title="Semana Operativa",
    yaxis_title="MW",
)

#fig.show()


### PRINTA CENARIOS
fig = go.Figure()
for idx, row in scenario_df.iterrows():
    fig.add_trace(go.Scatter(
        x=lista_x,
        y=row.tolist(),
        mode='lines',
        name=str(ano),
        showlegend = False,
        line=dict(color='black')
    ))

fig.update_layout(
    title="Cenários Sintéticos de Geração Eólica",
    xaxis_title="Semana Operativa",
    yaxis_title="MW",
)

#fig.show()
fig.write_html('cenarios.html', auto_open=False)


### PRINTA HISTORICO
fig = go.Figure()
for ano in unique_years:
    fig.add_trace(go.Scatter(
        x=lista_x,
        y=dicionario_anos[ano],
        mode='lines',
        name=str(ano),
        #line=dict(color='black')
    ))

fig.update_layout(
    title="Histórico de Cenários de Geração Eólica",
    xaxis_title="Semana Operativa",
    yaxis_title="MW",
)
fig.write_html('historico.html', auto_open=False)





### PRINTA CENARIOS
fig = go.Figure()
for idx, row in scenario_df.iterrows():
    fig.add_trace(go.Scatter(
        x=lista_x,
        y=row.tolist(),
        mode='lines',
        name=str(ano),
        showlegend = False,
        line=dict(color='black')
    ))


for ano in unique_years:
    fig.add_trace(go.Scatter(
        x=lista_x,
        y=dicionario_anos[ano],
        mode='lines',
        name=str(ano),
        #line=dict(color='black')
    ))

fig.update_layout(
    title="Comparacao Histórico e Cenarios de Geração Eólica",
    xaxis_title="Semana Operativa",
    yaxis_title="MW",
)
fig.write_html('cenarios_historico.html', auto_open=False)
exit(1)


lista = df["S1"].tolist() + df["S2"].tolist() + df["S3"].tolist() + df["S4"].tolist() + df["S5"].tolist()
plt.figure(figsize=(8, 5))
sns.histplot(lista, kde=True, bins=30, color='skyblue', stat='density')
plt.title("Distribution of S1")
plt.xlabel("Value")
plt.ylabel("Density")
plt.grid(True)
plt.savefig("distribution_s1.png", dpi=300, bbox_inches='tight')  # optional: dpi and bbox

# Fit the Weibull distribution (MLE)
shape, loc, scale = weibull_min.fit(lista, floc=0)  # floc=0 forces location=0, common in reliability
print(f"Estimated shape (k): {shape:.4f}")
print(f"Estimated scale (λ): {scale:.4f}")