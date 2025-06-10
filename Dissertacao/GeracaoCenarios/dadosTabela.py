import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px

class DadosMensais:
    def __init__(self, arquivo):
        df = pd.read_csv(arquivo)
        # Reshape the DataFrame
        df_melted = pd.melt(df, id_vars=["ANO"], var_name="MES", value_name="vazao")
        month_map = {
            "JANEIRO": 1, "FEVEREIRO": 2, "MARCO": 3, "ABRIL": 4, "MAIO": 5, "JUNHO": 6,
            "JULHO": 7, "AGOSTO": 8, "SETEMBRO": 9, "OUTUBRO": 10, "NOVEMBRO": 11, "DEZEMBRO": 12
        }
        df_melted["MES"] = df_melted["MES"].map(month_map)
        df_melted["Data"] = pd.to_datetime(df_melted["ANO"].astype(str) + "-" + df_melted["MES"].astype(str))
        df_month = df_melted[["Data", "vazao"]]
        df_month = df_month.sort_values(by="Data").reset_index(drop = True)

        lista_anos = df_month["Data"].dt.year.unique()
        lista_meses = list(range(1, 13))
        lista_dfs = []
        for ano in lista_anos:
            df_temp = df_month.loc[df_month["Data"].dt.year == ano]
            df_temp["periodo"] = lista_meses
            lista_dfs.append(df_temp)
        df_mensal = pd.concat(lista_dfs)
        self.dados = df_mensal
