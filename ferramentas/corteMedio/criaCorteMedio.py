import pandas as pd

def getFilhos(no, df_arvore):
    filhos = df_arvore[df_arvore["NO_PAI"] == no]["NO"].values
    return filhos

def busca_pai(no, df_arvore):
    pai = df_arvore[df_arvore["NO"] == no]["NO_PAI"].values[0]
    return pai
def retorna_lista_caminho(no, df_arvore):
    lista = [no]
    no_inicial = no
    periodo_no = df_arvore[df_arvore["NO"] == no]["PER"].values[0]
    for _ in range(periodo_no - 1):
        pai = busca_pai(no_inicial, df_arvore)
        lista.append(pai)
        no_inicial = pai
    return lista


caminho_caso = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\Capitulo_5\\caso_mini_500Cen_cluster_semanais\\avaliaArvoresRepresentativo\\"
caso_arvore = "revisaoDebora\\A_50x2x2_S39_255\\KMeansAssimetricoProbPente\\"
caso_arvore = "GTMIN\\Pente\\"
caso_arvore = "revisaoDebora\\A_100x1x1_42_20\\KMeansPente\\"
caso_arvore = "revisaoDebora\\Detrm\\KMeansPente\\"
caso_arvore = "revisaoDebora\\A_25x3x2\\KMeansAssimetricoProbPente\\"
caso_arvore = "revisaoDebora\\A_25x3x2\\KMeansSimetricoProbQuadPente\\"

caso_arvore = "GTMIN\\A_100_100_100\\BKAssimetrico\\"
caso_arvore = "GTMIN\\A_100_100_100\\KMeansPente\\"
caso_arvore = "GTMIN\\A_100_100_100\\KMeansPente\\"
caso_arvore = "revisaoDebora\\A_25x3x2\\BKAssimetrico\\"
caso_arvore = "revisaoDebora\\A_50x2x2_S39_255\\KMeansAssimetricoProbPente\\"

saidas = "saidas\\PDD\\oper\\"
arquivo = "df_cortes_equivalentes.csv"
df = pd.read_csv(caminho_caso+caso_arvore+saidas+arquivo)
df_arvore = pd.read_csv(caminho_caso+caso_arvore+"arvore.csv")
print(df_arvore)
print(df)
estagios = df["est"].unique()
usinas = df["usina"].unique()
print(estagios)
print(usinas)
lista_df = []
df_cortes_est = df.loc[(df["est"] == 1)].reset_index(drop = True)
df_cortes_est = df_cortes_est[
    ~((df_cortes_est['Indep'] == 0.0) & (df_cortes_est['Coef'] == 0.0))
]
lista_df.append(df_cortes_est)
for est in [2,3]:
    df_cortes_est = df.loc[(df["est"] == est)].reset_index(drop = True)
    nos_est = df_cortes_est["noUso"].unique()
    #print(nos_est)
    print("est: ", est)
    for usi in usinas:
        df_cortes_est_usi = df_cortes_est.loc[(df_cortes_est["usina"] == usi)].reset_index(drop = True)
        df_mask = df_cortes_est_usi.loc[(df_cortes_est_usi["noUso"] == nos_est[0])].reset_index(drop = True)

        df_mask["Indep"] = df_mask["Indep"]*0.0
        df_mask["Coef"] = df_mask["Coef"]*0.0
        df_mask["noUso"] = est
        
        for node in nos_est:
            df_cortes_est_usi_node = df_cortes_est_usi.loc[(df_cortes_est_usi["noUso"] == node)].reset_index(drop = True)

            caminho_node = retorna_lista_caminho(node, df_arvore)
            #print(df_cortes_est_usi_node)
            prob_cond = 1
            for elemento in caminho_node:
                prob_elemento = df_arvore.loc[(df_arvore["NO"] == elemento)]["PROB"].iloc[0]
                prob_cond = prob_cond*prob_elemento
            #print("caminho_node: ", caminho_node, " probc: ", prob_cond)
            df_mask["Indep"] += df_cortes_est_usi_node["Indep"]*prob_cond
            df_mask["Coef"] += df_cortes_est_usi_node["Coef"]*prob_cond
        df_mask = df_mask[
            ~((df_mask['Indep'] == 0.0) & (df_mask['Coef'] == 0.0))
        ]
        #print(df_mask)
        lista_df.append(df_mask)

df_final = pd.concat(lista_df).reset_index(drop = True)
df_final.to_csv(caminho_caso+caso_arvore+saidas+"cortes_est.csv", index = False)