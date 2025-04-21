# Codigo transforma ECO
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import MiniBatchKMeans
import math
import os
from datetime import timedelta  # <-- Add this import at the top of your script
import plotly.graph_objects as go

import time

# Marca o tempo de início
inicio = time.time()
os.environ["LOKY_MAX_CPU_COUNT"] = "4" 
resultado =      pd.read_parquet("cenarios_semanais.parquet", engine = "pyarrow")
print(resultado)
posto_uhe = 6
print(len(resultado["cenario"].unique()))

fig = go.Figure()
df_cen = resultado.loc[(resultado["posto"] == posto_uhe)].reset_index(drop = True)
print(df_cen)
fig.add_trace(
    go.Scatter(
        x=df_cen["cenario"],
        y=df_cen["valor"],
        mode='markers',  # or 'lines+markers'
        line=dict(color='black'),
        name=str(posto_uhe),  # Show scenario name in legend
        showlegend=False  # Changed to True to differentiate scenarios
    )
)
print(resultado)

# Update layout (optional but recommended)
fig.update_layout(
    title="Previsão Incremental por Cenário",
    xaxis_title="Data",
    yaxis_title="Previsão Incremental"
)

# Save to HTML (corrected from export_html to write_html)
fig.write_html("cenariosPente.html")



fig = go.Figure()
df_cen_furnas = resultado.loc[(resultado["posto"] == 6)].reset_index(drop = True)
df_cen_tucurui = resultado.loc[(resultado["posto"] == 275)].reset_index(drop = True)
print(df_cen)
fig.add_trace(
    go.Scatter(
        x=df_cen_tucurui["valor"],
        y=df_cen_furnas["valor"],
        mode='markers',  # or 'lines+markers'
        line=dict(color='black'),
        name=str(posto_uhe),  # Show scenario name in legend
        showlegend=False  # Changed to True to differentiate scenarios
    )
)
print(resultado)

# Update layout (optional but recommended)
fig.update_layout(
    title="Previsão Incremental por Cenário",
    xaxis_title="Data",
    yaxis_title="Previsão Incremental"
)

# Save to HTML (corrected from export_html to write_html)
fig.write_html("cenariosPente_FurnasXTucurui.html")