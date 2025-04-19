import numpy as np
import pandas as pd
import re
# Read the file

caminho = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\ferramentas\\transformaGevazpLab\\"
pasta = "2Aberturas_3Est\\"
pasta = "3Aberturas_4Est_Equiprovavel\\"
pasta = "3_Aberturas_3Est\\"
pasta = "2Aberturas_4Est_Assim\\"
pasta = "3Aberturas_4Est_teste\\"
pasta = "3D\\Estagios_4\\Aberturas_3\\"
pasta = "1D\\6_Aberturas\\"
pasta = "5D\\4Estagios\\3_3_3\\"
pasta = "4D\\4Estagios\\3_3_3_Teste\\"
#pasta = "2Aberturas\\"
caminho_caso = caminho+pasta
df_cenarios = pd.read_csv(caminho_caso+"fort.156", sep=";", skipinitialspace=True)
arquivoDADGER = caminho_caso+"DADGER.RV0"
# Ler o arquivo ignorando cabeçalhos
with open(arquivoDADGER, "r", encoding="latin1") as f:
    linhas = f.readlines()
    for line in linhas:
        if("ESTRUTURA DA ARVORE" in line):
            estruturaArvore = re.findall(r'\d+', line)  # Extracts all consecutive digit sequences
            estruturaArvore = [int(num) for num in estruturaArvore]  # Convert to integers


# Nome do arquivo
arquivo = caminho_caso+"PROBVAZ.REL"
# Ler o arquivo ignorando cabeçalhos
with open(arquivo, "r", encoding="latin1") as f:
    linhas = f.readlines()

# Filtrar linhas relevantes
dados1 = []
dados2 = []
read_table = False
read_table_pente = False
lista_df = []
lista_df_pente = []
for linha in linhas:
    linha = linha.strip()
    if(read_table):
        if(len(linha.split(" ")) != 1):
            dados = linha.split(",")
            lista_df.append(
                pd.DataFrame(
                    {
                        "CENARIO":[dados[0]],
                        "MES_1":[dados[1]],
                        "MES_2":[dados[2]],
                        "MES_3":[dados[3]],
                        "MES_4":[dados[4]],
                        "MES_5":[dados[5]],
                        "MES_6":[dados[6]],
                        "MES_7":[dados[7]],
                        "MES_8":[dados[8]],
                        "MES_9":[dados[9]],
                        "MES_10":[dados[10]],
                        "MES_11":[dados[11]],
                        "MES_12":[dados[12]]
                    }
                )
            )
        else:
            read_table = False


    if(read_table_pente):
        if(len(linha.split(" ")) != 1):
            dados = linha.split(",")
            lista_df_pente.append(
                pd.DataFrame(
                    {
                        "CENARIO":[dados[0]],
                        "PROBABILIDADE":[dados[1]],
                    }
                )
            )
        else:
            read_table_pente = False


    if("CENARIO,     1," in linha):
        read_table = True

    if("CENARIO,  PROBABILIDADE," in linha):
        read_table_pente = True

df_probabilidadesArvore = pd.concat(lista_df).reset_index(drop =True)
df_probabilidadesPente = pd.concat(lista_df_pente).reset_index(drop =True)

print("REALIZACOES CENARIOS:")
print(df_cenarios)

print("DF PROBABILIDADE ARVORE: ")
print(df_probabilidadesArvore)

print("DF PROBABILIDADE PENTE: ")
print(df_probabilidadesPente)

#estruturaArvore = [3, 3, 3]

def criaFilhos(no, est, aberturas, listaNos, lista_df):
    if(est < len(aberturas)):
        for abertura in range(aberturas[est]):
            no_filho = max(listaNos) + 1
            listaNos.append(no_filho)
            lista_df.append(pd.DataFrame({
                "NO_PAI":[no],
                "NO":[no_filho],
                "Abertura":[abertura],
                "PER":[est+2],
                "PROB":[1]
            }))
            criaFilhos(no_filho, est + 1,aberturas, listaNos, lista_df)

def getPai(no, df_arvore):
    no_pai = df_arvore.loc[(df_arvore["NO"] == no)]["NO_PAI"].iloc[0]
    return no_pai

def getFilhos(no, df_arvore):
    filhos = df_arvore.loc[(df_arvore["NO_PAI"] == no)]["NO"].unique()
    return filhos

def getCaminho(no, df_arvore):
    lista_caminho = []
    lista_caminho.append(no)
    no_raiz = no
    while no_raiz != 1:
        pai = getPai(no_raiz, df_arvore)
        lista_caminho.append(pai)
        no_raiz = pai
    return lista_caminho

no = 1
listaNos = []
lista_df = []
listaNos.append(no)
lista_df.append(pd.DataFrame({
    "NO_PAI":[0],
    "NO":[no],
    "Abertura":[1],
    "PER":[1],
    "PROB":[1]
}))

criaFilhos(no, 0, estruturaArvore, listaNos, lista_df) ## ARVORE DE CENARIOS
df_arvore_externa_gevazp = pd.concat(lista_df).reset_index(drop = True)

nos_ultimoEstagio = df_arvore_externa_gevazp.loc[(df_arvore_externa_gevazp["PER"] == max(df_arvore_externa_gevazp["PER"]))]["NO"].unique()
df_arvore_externa_gevazp_resultante  = df_arvore_externa_gevazp.reset_index(drop = True)
colunas = list(df_probabilidadesArvore.columns)


caminhos_arvore = {}
for i, row in df_probabilidadesArvore.iterrows():
    print("i: ", i, row)
    caminho = getCaminho(nos_ultimoEstagio[i], df_arvore_externa_gevazp_resultante)
    caminhos_arvore[i] = sorted(caminho[:-1])
    for idx, no in enumerate(sorted(caminho)):
        print("idx: ", idx, " no: ", no, " prob: ", row[colunas[idx+1]])
        df_arvore_externa_gevazp_resultante.loc[(df_arvore_externa_gevazp_resultante["NO"] == no), ["PROB"]] = round(float(row[colunas[idx+1]].strip()),4)




def calculaProbCaminho(caminho, df_arvore):
    prob = 1
    for no in caminho:
        prob_no = df_arvore.loc[(df_arvore["NO"] == no)]["PROB"].iloc[0]
        prob = prob*float(prob_no)
    prob = round(prob,4)
    return prob
print(caminhos_arvore)
print(df_arvore_externa_gevazp_resultante)
lista_df_pente = []
## FAZ ARVORE PENTE COM BASE NA ARVORE COMPLETA FEITA PELO GEVAZP
contador = 2
current_columns = df_cenarios.columns
new_columns = ['POSTO', 'CENARIO'] + [str(i) for i in range(2, len(current_columns) )]
df_cenarios.columns = new_columns
postos = df_cenarios["POSTO"].unique()
lista_df_vazoes_pente = []
lista_df_vazoes_arvore = []
#for idx_cen, row in df_cenarios.iterrows():

lista_df_pente.append(
    pd.DataFrame(
        {
            "NO_PAI":[0],
            "NO":[1],
            "Abertura":[1],
            "PER":[1],
            "PROB":[1]
        }
    )
)

for posto in postos:
    lista_df_vazoes_pente.append(
        pd.DataFrame(
            {
                "NOME_UHE":[posto],
                "NO":[1],
                "VAZAO":[0]
            }
        )
    )

    lista_df_vazoes_arvore.append(
        pd.DataFrame(
            {
                "NOME_UHE":[posto],
                "NO":[1],
                "VAZAO":[0]
            }
        )
    )


for idx_cen in caminhos_arvore:
    #print("indice: ", idx_cen)
    caminho = caminhos_arvore[idx_cen]
    #print(row)
    contador_anterior = 0
    for idx, no_arvore in enumerate(caminho):
        pai = 1 if idx == 0 else contador_anterior
        probabilidade_no_2 = calculaProbCaminho(caminho, df_arvore_externa_gevazp_resultante) if(idx == 0) else 1
        lista_df_pente.append(
            pd.DataFrame(
                {
                    "NO_PAI":[pai],
                    "NO":[contador],
                    "Abertura":[idx_cen+1],
                    "PER":[idx+2],
                    "PROB":[probabilidade_no_2]
                }
            )
        )
        contador_anterior = contador
        
        estagio = idx+2
        for posto in postos:
            df_posto_cen = df_cenarios.loc[(df_cenarios["POSTO"] == posto) & (df_cenarios["CENARIO"] == idx_cen+1)].reset_index(drop = True)
            vazao_cen = df_posto_cen[str(estagio)].iloc[0]
            vazao_cen = round(vazao_cen,0)
            #print(df_posto_cen)
            #print(vazao_cen)
            lista_df_vazoes_pente.append(
                pd.DataFrame(
                    {
                        "NOME_UHE":[posto],
                        "NO":[contador],
                        "VAZAO":[vazao_cen]
                    }
                )
            )

            lista_df_vazoes_arvore.append(
                pd.DataFrame(
                    {
                        "NOME_UHE":[posto],
                        "NO":[no_arvore],
                        "VAZAO":[vazao_cen]
                    }
                )
            )
        contador += 1


df_pente = pd.concat(lista_df_pente).reset_index(drop = True)
df_vazoes_pente = pd.concat(lista_df_vazoes_pente).reset_index(drop = True)
df_vazoes_arvore = pd.concat(lista_df_vazoes_arvore).drop_duplicates().reset_index(drop = True)
print(df_arvore_externa_gevazp_resultante)
print(df_pente)
print(df_vazoes_pente)
print(df_vazoes_arvore)

df_arvore_externa_gevazp_resultante.to_csv(caminho_caso+"arvore_gevazp.csv", index = False)
df_pente.to_csv(caminho_caso+"pente_gevazp.csv", index = False)
df_vazoes_pente.to_csv(caminho_caso+"cenarios_pente_gevazp.csv", index = False)
df_vazoes_arvore.to_csv(caminho_caso+"cenarios_arvore_gevazp.csv", index = False)

