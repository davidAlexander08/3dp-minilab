import pandas as pd
import plotly.figure_factory as ff
import numpy as np

caminho = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\cenarios_500Cen_cluster_semanais_EOL\EOL_4\Eol_cen\Pente"
# Example data
arvore  = pd.read_csv(caminho+r"\arvore.csv")
cenarios  = pd.read_csv(caminho+r"\cenarios.csv")
arvore_est = arvore.loc[(arvore["PER"] == 2)]
nodes_est = arvore_est["NO"].unique()
lista_prob = arvore_est["PROB"].tolist()
lista_cenarios = cenarios.loc[(cenarios["NO"].isin(nodes_est)) & (cenarios["NOME_UHE"] == 993)]["VAZAO"].tolist()

x = np.random.normal(0, 1, 500)
y = np.random.normal(2, 0.5, 500)

print(lista_prob)
print(lista_cenarios)
# Create KDE plot

fig = ff.create_distplot(
    [lista_cenarios], 
    group_labels=["Y"], 
    show_hist=False  # Set to True to add histogram
)

fig.update_layout(
    title="Probability Density Distribution for X and Y",
    xaxis_title='Value',
    yaxis_title='Density'
)

fig.write_html(f"smooth.html")

