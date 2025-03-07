import pandas as pd

df = pd.read_csv("previsaoM_inc_semTV_2020_01.csv", sep=";")
print(df)
postos = df["postos"].unique()
print(postos)
df = df.loc[df["cenario"] <= 10]
columns_to_keep = ["cenario", "postos", "1/2020", "2/2020", "3/2020"]
df = df[columns_to_keep]
print(df)
cenarios = df["cenario"].unique()
print(cenarios)
lista_df = []
for posto in postos:
    df_posto = df.loc[df["postos"] == posto  ].reset_index(drop = True)
    print(df_posto)
    contador_no = 2
    lista_df.append(pd.DataFrame({"NOME_UHE":[posto], "NO":[1], "VAZAO":[0]}))
    for i, row in df_posto.iterrows():
        for col in df_posto.columns:
            if col not in ["cenario", "postos"]:  # Ignore these columns
                value = row[col]
                lista_df.append(pd.DataFrame({"NOME_UHE":[posto], "NO":[contador_no], "VAZAO":[value]}))
                #print(f"Posto: {posto}, Coluna: {col}, Valor: {value} No: {contador_no}")
                contador_no += 1

df_final = pd.concat(lista_df).reset_index(drop = True)
df_final.to_csv("vazao_feixes.csv", index = False)
print(df_final)
    
