import pandas as pd
path_pente = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\cenarios_500Cen_cluster_semanais_EOL\EOL_4\Eol_cen\Pente"
path_saida = r"C:\Users\testa\Documents\git\3dp-minilab\Capitulo_5\cenarios_500Cen_cluster_semanais_EOL\EOL_4\comEOL\Eol_granularizado\Pente"
df_pente = pd.read_csv(path_pente+"\\cenarios.csv")
df_arvore = pd.read_csv(path_pente+"\\arvore.csv")
print(df_pente)
estagios = df_arvore["PER"].unique()
df_usinas_eolicas = df_pente.loc[(df_pente["NOME_UHE"].isin([993,992]))]
print(df_usinas_eolicas)
usinas_eolicas = df_usinas_eolicas["NOME_UHE"].unique()
#print(usinas_eolicas)
df_new_cenarios = df_pente.copy()
df_new_cenarios = df_new_cenarios.loc[(df_new_cenarios["NOME_UHE"] != 993)]
df_new_cenarios = df_new_cenarios.loc[(df_new_cenarios["NOME_UHE"] != 992)].reset_index(drop = True)
lista_df = []
lista_df.append(df_new_cenarios)
total_nodes = df_arvore["NO"].unique()
novas_usinas = {
    992:[1000,1001,1002,1003,1004],            
    993:[1005,1006,1007,1008,1009]
    }

for usi in novas_usinas:
    df_usi = df_usinas_eolicas.loc[(df_usinas_eolicas["NOME_UHE"] == usi)].reset_index(drop = True)
    for est in estagios:
        df_arvore_est = df_arvore.loc[(df_arvore["PER"] == est)]
        nodes_est = df_arvore_est["NO"].unique()
        df_usi_est = df_usi.loc[(df_usi["NO"].isin(nodes_est))]
        media = df_usi_est["VAZAO"].mean()
        desvio = df_usi_est["VAZAO"].std()
        print("USI: ", usi, " EST: ", est, " MEDIA: ", media, " DESVIO: ", desvio)
exit(1)
for usi in usinas_eolicas:
    df_usi = df_usinas_eolicas.loc[(df_usinas_eolicas["NOME_UHE"] == usi)].reset_index(drop = True)
    #print(df_usi)
    for nova_usi in novas_usinas[usi]:
        for node in total_nodes:
            df_pente_node = df_usi.loc[(df_usi["NO"] == node) ]
            cenario_orig = df_pente_node["VAZAO"].iloc[0]
            lista_df.append(
                pd.DataFrame(
                    {
                        "NOME_UHE":nova_usi,
                        "NO":[node],
                        "VAZAO":[df_pente_node["VAZAO"].iloc[0]/len(novas_usinas[usi])]
                    }
                )
            )


df_result = pd.concat(lista_df).reset_index(drop = True)
for usi in novas_usinas:
    for usina in novas_usinas[usi]:
        df_usi = df_result.loc[(df_result["NOME_UHE"] == usina)].reset_index(drop = True)
        for est in estagios:
            df_arvore_est = df_arvore.loc[(df_arvore["PER"] == est)]
            nodes_est = df_arvore_est["NO"].unique()
            df_usi_est = df_usi.loc[(df_usi["NO"].isin(nodes_est))]
            media = df_usi_est["VAZAO"].mean()
            desvio = df_usi_est["VAZAO"].std()
            print("USI: ", usina, " EST: ", est, " MEDIA: ", media, " DESVIO: ", desvio)
    #print(df_usi)
#df_result.to_csv(path_saida+"\\cenarios.csv", index = False)
#df_arvore.to_csv(path_saida+"\\arvore.csv", index = False)