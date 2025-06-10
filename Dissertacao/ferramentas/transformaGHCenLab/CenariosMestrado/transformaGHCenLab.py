import pandas as pd

caminho = "cenariosClusterizadosMedia\\"
df = pd.read_parquet(caminho+"media_cenarios_GhcenSemanais_4.parquet", engine = "pyarrow")
print(df)
exit(1)
numeroCenarios = 500
df = df.loc[df["serie"] <= numeroCenarios]
estagios = df["data_previsao"].unique()
estagios = estagios[estagios != pd.to_datetime("2020-01-01")]
postos = df["posto"].unique()
print(postos)
print("NUMERO POSTOS: ", len(postos))

#postos2 = [1,2,211,6,7,8,9,10,11,12,14,15,16,17,18,22,251,24,25,206,207,28,205,209,31,32,33,34,237,238,239,240,242,243,245,246,47,48,49,50,51,52,57,61,62,63,266,71,72,73,74,76,77,78,222,81,215,89,216,217,92,93,220,286,98,97,284,102,103,94,161,104,109,110,111,112,113,114,115,117,301,120,121,122,123,202,125,197,198,129,130,134,263,149,141,148,144,255,154,188,155,156,158,169,168,172,173,175,178,201,203,254,190,262,183,295,296,23,204,101,196,227,228,229,230,241,249,270,191,253,257,273,294,271,277,275,145,269,278,279,280,281,283,297,285,290,287,99,259,291,247,248,288,261]
#print(postos2)
#print("NUMERO POSTOS: ", len(postos2))

set1 = set(postos)
set2 = set(postos2)

only_in_list1 = set1 - set2
only_in_list2 = set2 - set1
print("Elements only in list1:", sorted(only_in_list1))
print("Elements only in list2:", sorted(only_in_list2))


##########POSTOS DO CASO REDUZIDO
#postos = [6,8,11,12,17,18,34,66,156,227,229,270,257,273,285,287,279,24,25,31,32,33,37,40,42,43,45,46,47,49,50,61,62,63,74,215,217,92,93,94,115,75,77,222,169,172,178,271,275,302,292]
postos = [6,8,11,12,17,18,34,266,156,227,229,270,257,273,285,287,279,24,25,31,32,33,237,240,242,243,245,246,47,49,50,61,62,63,74,215,217,92,93,94,115,76,77,222,169,271,275,288] ## POSTOS 172 e 178 viraram postos nulos como no GEVAZP
print("postos: ", postos)
print("NUMERO POSTOS: ", len(postos))

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
df_final.to_csv(caminho+"vazao_feixes_cen_"+str(numeroCenarios)+".csv", index = False)
print(df_final)
    


### Criando árvore de probabilidades
lista_df = []
df_posto = df.loc[df["posto"] == 6  ].reset_index(drop = True)
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
df_final.to_csv(caminho+"probabilidades_feixes_cen_"+str(numeroCenarios)+".csv", index = False)
print(df_final)