import pandas as pd

caminho_arquivo_cenarios = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\Capitulo_5\\caso_mini_500Cen_cluster_semanais\\"
caminho_complementar = "avaliaArvoresRepresentativo\\Caso_SF\\A_25x4x2\\"

caminho_arquivo_cenarios = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\Carmen\\exercicio_27cen_36D\\"
caminho_complementar = "27_Aberturas_Equiprovavel\\CasoSF\\A_4x2x1\\"
df = pd.read_csv(caminho_arquivo_cenarios+caminho_complementar+"Deterministico\\cenarios.csv")

mapa_casos_saida = {
    "Determ_06":0.6,
    "Determ_08":0.8,
    "Determ_12":1.2,
}
print(df)
for caso in mapa_casos_saida:
    df_caso = df.copy()
    df_caso["VAZAO"] = df_caso["VAZAO"]*mapa_casos_saida[caso]
    print(df_caso)
    df_caso.to_csv(caminho_arquivo_cenarios+caminho_complementar+caso+"\\cenarios.csv", index = False)