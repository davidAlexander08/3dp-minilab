import pandas as pd
caminho = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\Capitulo_5\\caso_mini_500Cen_cluster_semanais\\avaliaArvoresRepresentativo\\Pente\\"


df = pd.read_csv(caminho+"cenarios.csv")
lista_postos_reduzido = [
    6,8,11,12,17,18,34,266,156,227,229,270,257,273,285,287,
    279,24,25,31,32,33,237,240,242,243,245,246,47,49,50,61,62,63,
    74,215,217,92,93,94,115,76,77,222,169,271,275,288
]
print(lista_postos_reduzido)
print(df)
print(df["NOME_UHE"].unique())
df_red = df.loc[df["NOME_UHE"].isin(lista_postos_reduzido)].reset_index(drop = True)
print(df_red)
print(df_red["NOME_UHE"].unique())
print(len(df_red["NOME_UHE"].unique()))
#df_red.to_csv(caminho+"cenarios_representativo.csv", index = False)