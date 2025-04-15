import pandas as pd

df = pd.read_parquet("cenarios_semanais_sorteio_4sem_8cen.parquet", engine = "pyarrow")
print(df)

numeroCenarios = 8
df = df.loc[df["serie"] <= numeroCenarios]
estagios = df["data_previsao"].unique()
estagios = estagios[estagios != pd.to_datetime("2020-01-01")]
postos = df["posto"].unique()
series = df["serie"].unique()
print("postos: ", postos)
print("estagios: ", estagios)

lista_df = []
for posto in postos:
    print("realizando posto: ", posto)
    df_posto = df.loc[df["posto"] == posto  ].reset_index(drop = True)
    #print(df_posto)
    valor_no_1 = df_posto.loc[(df_posto["data_previsao"].dt.day == 1)]["previsao_incremental"].mean()
    lista_df.append(pd.DataFrame({"NOME_UHE":[posto], "NO":[1], "VAZAO":[valor_no_1]}))
    contador_no = 2
    for serie in series:
        for estagio in estagios:
            df_est = df_posto.loc[(df_posto["data_previsao"] == estagio) & (df_posto["serie"] == serie) ]
            #print(df_est)
            #print("posto: ", posto, " estagio: ", estagio, " serie: ", serie, " no: ", contador_no, " cenario: ", df_est["cenario"].iloc[0])
            value = df_est["previsao_incremental"].iloc[0]
            lista_df.append(pd.DataFrame({"NOME_UHE":[posto], "NO":[contador_no], "VAZAO":[round(value,0)]}))
            #print(f"Posto: {posto}, Coluna: {col}, Valor: {value} No: {contador_no}")
            contador_no += 1
    print("realizado, total nos: ", contador_no)
df_final = pd.concat(lista_df).reset_index(drop = True)
df_final.to_csv("vazao_feixes_cen_"+str(numeroCenarios)+".csv", index = False)
print(df_final)
    


### Criando árvore de probabilidades
lista_df = []
df_posto = df.loc[df["posto"] == 1  ].reset_index(drop = True)
print(df_posto)
contador_no = 2
lista_df.append(pd.DataFrame({"NO":[1], "PROBABILIDADE":[1]}))
for serie in series:
    for estagio in estagios:
        probabilidade = 0
        if(estagio == min(estagios)):
            probabilidade = 1/numeroCenarios
        else:
            probabilidade = 1
        lista_df.append(pd.DataFrame({"NO":[contador_no], "PROBABILIDADE":[probabilidade]}))
        #print(f"Posto: {posto}, Coluna: {col}, Valor: {value} No: {contador_no}")
        contador_no += 1

df_final = pd.concat(lista_df).reset_index(drop = True)
df_final.to_csv("probabilidades_feixes_cen_"+str(numeroCenarios)+".csv", index = False)
print(df_final)