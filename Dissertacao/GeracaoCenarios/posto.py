import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px

class Posto:
    def __init__(self):
        pass
    
    def setHistorico(self, df_hist):
        self.historico = df_hist

    def setCoefs(self, df_coefs):
        self.coefs = df_coefs

    def setResiduos(self, df_residuos):
        self.residuos = df_residuos

    def setCodigo(self, codigo):
        self.codigo = codigo