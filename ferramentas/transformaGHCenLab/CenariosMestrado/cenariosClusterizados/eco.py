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
resultado =      pd.read_parquet("cenarios_semanais_4semanas.parquet", engine = "pyarrow")
data = resultado["data_previsao"].unique()
cenarios = resultado["cenario"].unique()
posto_uhe = 6

fig = go.Figure()
for cen in cenarios:
    df_cen = resultado.loc[(resultado["cenario"] == cen) & (resultado["posto"] == posto_uhe)].reset_index(drop = True)
    print(df_cen)
    fig.add_trace(
        go.Scatter(
            x=df_cen["data_previsao"],
            y=df_cen["previsao_incremental"],
            mode='lines',  # or 'lines+markers'
            line=dict(color='black'),
            name=str(cen),  # Show scenario name in legend
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