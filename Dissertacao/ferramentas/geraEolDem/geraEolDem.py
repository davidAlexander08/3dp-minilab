import pandas as pd
path_pente = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\cenarios_500Cen_cluster_semanais_EOL\EOL_5\Eol_gran\A_25x3x2\KMeansAssimetricoProbPente"
path_saida = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\cenarios_500Cen_cluster_semanais_EOL\EOL_5\Eol_dem\A_25x3x2\KMeansAssimetricoProbPente"
df_pente = pd.read_csv(path_pente+"\\cenarios.csv")
df_arvore = pd.read_csv(path_pente+"\\arvore.csv")
print(df_pente)
estagios = df_arvore["PER"].unique()
df_usinas_eolicas = df_pente.loc[(df_pente["NOME_UHE"].isin([1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009]))]
print(df_usinas_eolicas)
usinas_eolicas = df_usinas_eolicas["NOME_UHE"].unique()
#print(usinas_eolicas)
df_new_cenarios = df_pente.copy()
for usi in usinas_eolicas:
    df_usi = df_usinas_eolicas.loc[(df_usinas_eolicas["NOME_UHE"] == usi)].reset_index(drop = True)
    #print(df_usi)
    for est in estagios:
        df_arvore_est = df_arvore.loc[(df_arvore["PER"] == est)]
        nodes_est = df_arvore_est["NO"].unique()
        df_cenarios_est = df_usi.loc[(df_usi["NO"].isin(nodes_est))]
        media = df_cenarios_est["VAZAO"].mean()
        print("USI: ", usi, " EST: ", est, " MEDIA: ", media)
        for node in nodes_est:
            df_new_cenarios.loc[(df_new_cenarios["NOME_UHE"] == usi) & (df_new_cenarios["NO"] == node), "VAZAO"] = media

#print(df_new_cenarios)
df_new_cenarios.to_csv(path_saida+"\\cenarios.csv", index = False)
df_arvore.to_csv(path_saida+"\\arvore.csv", index = False)