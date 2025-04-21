import pandas as pd

df = pd.read_parquet("cenarios_semanais.parquet", engine = "pyarrow")
print(df)

numeroCenarios = 500
df = df.loc[df["serie"] <= numeroCenarios]
estagios = df["estagio"].unique()
estagios = estagios[estagios != pd.to_datetime("2020-01-01")]
postos = df["posto"].unique()
series = df["serie"].unique()
print("postos: ", postos)
print("estagios: ", estagios)
estagios_percorre = estagios.tolist()
estagios_percorre.remove(1)

lista_df = []
for posto in postos:
    print("realizando posto: ", posto)
    df_posto = df.loc[df["posto"] == posto  ].reset_index(drop = True)
    #print(df_posto)
    valor_no_1 = df_posto.loc[(df_posto["estagio"] == 1)]["valor"].mean()
    lista_df.append(pd.DataFrame({"NOME_UHE":[posto], "NO":[1], "VAZAO":[valor_no_1]}))
    #print(lista_df)
    contador_no = 2
    for serie in series:
        for estagio in sorted(estagios_percorre, reverse=False):
            df_est = df_posto.loc[(df_posto["estagio"] == estagio) & (df_posto["serie"] == serie) ]
            #print(df_est)
            #print("posto: ", posto, " estagio: ", estagio, " serie: ", serie, " no: ", contador_no, " cenario: ", df_est["cenario"].iloc[0])
            value = df_est["valor"].iloc[0]
            lista_df.append(pd.DataFrame({"NOME_UHE":[posto], "NO":[contador_no], "VAZAO":[round(value,0)]}))
            #print(f"Posto: {posto}, Coluna: {col}, Valor: {value} No: {contador_no}")
            contador_no += 1
    print("realizado, total nos: ", contador_no)
df_final = pd.concat(lista_df).reset_index(drop = True)
df_final.to_csv("cenarios"+str(numeroCenarios)+".csv", index = False)
print(df_final)
    


### Criando árvore de probabilidades
lista_df = []
df_posto = df.loc[df["posto"] == 1  ].reset_index(drop = True)
print(df_posto)
contador_no = 2
lista_df.append(pd.DataFrame({"NO":[1], "PROBABILIDADE":[1]}))
for serie in series:
    for estagio in sorted(estagios_percorre, reverse=False):
        probabilidade = 0
        if(estagio == min(estagios_percorre)):
            probabilidade = 1/numeroCenarios
        else:
            probabilidade = 1
        lista_df.append(pd.DataFrame({"NO":[contador_no], "PROBABILIDADE":[probabilidade]}))
        #print(f"Posto: {posto}, Coluna: {col}, Valor: {value} No: {contador_no}")
        contador_no += 1

df_final = pd.concat(lista_df).reset_index(drop = True)
df_final.to_csv("probs_"+str(numeroCenarios)+".csv", index = False)
print(df_final)