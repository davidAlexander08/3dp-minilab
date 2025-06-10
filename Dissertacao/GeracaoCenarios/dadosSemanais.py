import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px

class DadosSemanais:
    def __init__(self, arq):
        df = pd.read_csv(arq)
        df["Data"] = pd.to_datetime(df["Data"], dayfirst=True)
        df_week = df
        df_week.set_index("Data", inplace=True)
        df_week = df_week.resample("W").mean()
        df_week.reset_index(inplace=True)
        #print(df_week)
        lista_df_52_semanas = []
        listaPeriodo = list(range(1, 53))
        fig  = go.Figure()
        for i in range(1933,2024):
            df_temp = df_week.loc[(df_week["Data"].dt.year == i)].reset_index(drop = True)
            #print(len(df_temp["Data"].unique()))
            if(len(df_temp["Data"].unique()) == 53):
                df_temp = df_temp.iloc[:-1]
            df_temp["periodo"] = listaPeriodo
            lista_df_52_semanas.append(df_temp)
            fig.add_trace( go.Scatter(x = df_temp["periodo"].tolist(), y = df_temp["vazao"].tolist(),  line = dict(color = "blue") )  )
        fig.write_html("/home/david/git/3dp-minilab/CenariosSemanais/historico.html", include_plotlyjs='cdn',  config={"modeBarButtonsToAdd": ["drawline", "eraseshape", "sendDataToCloud"]})
        df_parp = pd.concat(lista_df_52_semanas).reset_index(drop = True)
        self.dados = df_parp