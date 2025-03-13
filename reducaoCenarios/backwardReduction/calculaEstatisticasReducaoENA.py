import pandas as pd
from scipy.stats import skew

caso = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\Mestrado\\caso_construcaoArvore_SIN_500cen\\"
df_vazoes = pd.read_csv(caso+"\\vazao_feixes.csv")

df_arvore_original = pd.read_csv("saidas\\arvore_estudo.csv")
df_arvore = pd.read_csv("saidas\\df_arvore_reduzida.csv")

print(df_arvore)
## TESTE ESTATISTICO USINAS
usinas = [17, 66, 275, 156, 211, 22, 25, 292]
lista_df = []
for est in sorted(df_arvore["PER"].unique())[1:]:
    nos = df_arvore.loc[df_arvore["PER"] == est]["NO"].unique()
    nos_original = df_arvore_original.loc[df_arvore_original["PER"] == est]["NO"].unique()

    vazao = df_vazoes.loc[df_vazoes["NO"].isin(nos)].copy().reset_index(drop = True)
    vazao_orig = df_vazoes.loc[df_vazoes["NO"].isin(nos_original)].copy().reset_index(drop = True)
    print("EST: ", est, " vazao_red: ", vazao)
    print("EST: ", est, " vazao_orig: ", vazao_orig)

    for usi in usinas:
        vaz_red_usi = vazao.loc[(vazao["NOME_UHE"] == usi).reset_index(drop = True)]
        vaz_orig_usi = vazao_orig.loc[(vazao_orig["NOME_UHE"] == usi).reset_index(drop = True)]
        print("MEDIA EST ", est, " USINA: ", usi)
        mean_reduzida = vaz_red_usi["VAZAO"].mean()
        mean_original = vaz_orig_usi["VAZAO"].mean()
        std_reduzida = vaz_red_usi["VAZAO"].std()
        std_original = vaz_orig_usi["VAZAO"].std()
        skew_reduzida = skew(vaz_red_usi["VAZAO"], bias=False)
        skew_original = skew(vaz_orig_usi["VAZAO"], bias=False)
        print("REDUZIDA: Média =", mean_reduzida, " Desvio Padrão =", std_reduzida, " Assimetria =", skew_reduzida)
        print("ORIGINAL: Média =", mean_original, " Desvio Padrão =", std_original, " Assimetria =", skew_original)
        df = pd.DataFrame({ "posto":[usi], 
                            "estagio":[est],
                            "media_reduzida":[round(mean_reduzida,2)],
                            "media_original":[round(mean_original,2)],
                            "desvio_reduzido":[round(std_reduzida,2)],
                            "desvio_original":[round(std_original,2)],
                            })
        lista_df.append(df)

df_result = pd.concat(lista_df).reset_index(drop = True)
df_result.to_csv("saidas\\estatisticas_Arv_red.csv", index=False)