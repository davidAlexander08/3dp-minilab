import pandas as pd

lista_df_cen = []

arquivos = {
    "500_cenarios_NE":993,
    "500_cenarios_S":992
}
for arquivo in arquivos:
    df = pd.read_csv(arquivo+".csv")
    df_small = df[["1_S1", "1_S2","1_S3", "1_S4"]]
    print(df_small)
    print(df_small.mean())
    print(df_small.std())
    cenario_no_1 = df_small["1_S1"].mean()
    print("cenario_no_1: ", cenario_no_1)

    colunas = ["1_S2","1_S3", "1_S4"]
    lista_df_cen.append(
        pd.DataFrame({
            "NOME_UHE":[arquivos[arquivo]],
            "NO":[1],
            "VAZAO":[round(cenario_no_1,0)]
        })
    )
    contador_nodes = 2
    for coluna in colunas:
        pilha_de_dados = df_small[coluna].tolist()
        for dado in pilha_de_dados:
            lista_df_cen.append(
                pd.DataFrame({
                    "NOME_UHE":[arquivos[arquivo]],
                    "NO":[contador_nodes],
                    "VAZAO":[round(dado,0)]
                })
            )
            contador_nodes += 1

resultado = pd.concat(lista_df_cen).reset_index(drop = True)
print(resultado)
resultado.to_csv("cenarios_eol.csv", index = False)