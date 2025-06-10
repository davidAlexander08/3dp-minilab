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
caminho_caso = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\Carmen\\exercicio_27cen_36D\\27_Aberturas_Equiprovavel\\"
caminho_caso = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\Academico\\exercicio_1D\\128_Aberturas_Equiprovavel\\"
caminho_caso = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\Capitulo_5\\caso_mini_500Cen_cluster_semanais\\Dissertacao\\Final\\"

caso_arvore = "revisaoDebora\\A_25x3x2\\BKAssimetrico\\"
caso_arvore = "A_4x2x1\\KMeansAssimetricoProbPente\\"
caso_arvore = "A_8x1x1\\BKAssimetrico\\"
caso_arvore = "Pente_GVZP\\"
caso_arvore = "A_25x3x2\\KMeansAssimetricoProbPente\\"
caso_arvore = "A_25x3x2\\KMeansSimetricoProbQuadPente\\"
caso_arvore = "A_100x1x1\\KMeansPente\\"
caso_arvore = "Vassoura\\KMeansAssimetricoProbPente\\"
caso_arvore = "Detrm\\"
caso_arvore = "Pente\\"

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
        for node in nos_est:
            df_mask = df_cortes_est_usi.loc[(df_cortes_est_usi["noUso"] == nos_est[0])].reset_index(drop = True)
            df_mask["Indep"] = df_mask["Indep"]*0.0
            df_mask["Coef"] = df_mask["Coef"]*0.0
            df_mask["noUso"] = est
            df_cortes_est_usi_node = df_cortes_est_usi.loc[(df_cortes_est_usi["noUso"] == node)].reset_index(drop = True)
            df_mask["Indep"] = df_cortes_est_usi_node["Indep"]
            df_mask["Coef"] = df_cortes_est_usi_node["Coef"]
            df_mask = df_mask[
                ~((df_mask['Indep'] == 0.0) & (df_mask['Coef'] == 0.0))
            ]
            #print(df_mask)
            lista_df.append(df_mask)
df_final = pd.concat(lista_df).reset_index(drop = True)
df_final.to_csv(caminho_caso+caso_arvore+saidas+"all_cut.csv", index = False)