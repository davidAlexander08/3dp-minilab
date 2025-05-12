import pandas as pd

caminho_arquivo_cenarios = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\Capitulo_5\\caso_mini_500Cen_cluster_semanais\\"
caminho_complementar = "avaliaArvoresRepresentativo\\Caso_SF\\A_25x4x2\\"
df = pd.read_csv(caminho_arquivo_cenarios+caminho_complementar+"Determ\\cenarios.csv")

mapa_casos_saida = {
    "Determ_06":0.6,
    "Determ_08":0.8,
    "Determ_12":1.2,
    "Determ_14":1.4
}
print(df)
for caso in mapa_casos_saida:
    df_caso = df.copy()
    df_caso["VAZAO"] = df_caso["VAZAO"]*mapa_casos_saida[caso]
    print(df_caso)
    df_caso.to_csv(caminho_arquivo_cenarios+caminho_complementar+caso+"\\cenarios.csv", index = False)