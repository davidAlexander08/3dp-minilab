import numpy as np
import pandas as pd
from scipy.stats import wasserstein_distance
from scipy.stats import ksone
from scipy.stats import ks_2samp
import plotly.graph_objects as go
from scipy.stats import chisquare
from scipy.stats import mannwhitneyu
from statsmodels.stats.weightstats import DescrStatsW
import plotly.graph_objects as go
from scipy.stats import linregress
from sklearn.metrics import r2_score
from plotly.subplots import make_subplots
from inewave.newave import Confhd
from inewave.newave import Hidr
pd.set_option('display.max_rows', None)

def calcula_prodt_65(codigo_usi, df_hidr):
    df_hidr_uhe = df_hidr.loc[(df_hidr["codigo_usina"] == codigo_usi)]
    vol_65 = (df_hidr_uhe["volume_maximo"].iloc[0] - df_hidr_uhe["volume_minimo"].iloc[0])*0.65 + df_hidr_uhe["volume_minimo"].iloc[0]
    vol_cota_A0 = df_hidr_uhe["a0_volume_cota"].iloc[0]
    vol_cota_A1 = df_hidr_uhe["a1_volume_cota"].iloc[0]*vol_65
    vol_cota_A2 = df_hidr_uhe["a2_volume_cota"].iloc[0]*vol_65**2
    vol_cota_A3 = df_hidr_uhe["a3_volume_cota"].iloc[0]*vol_65**3
    vol_cota_A4 = df_hidr_uhe["a4_volume_cota"].iloc[0]*vol_65**4
    cota_med_fuga = df_hidr_uhe["canal_fuga_medio"].iloc[0]
    perdas = df_hidr_uhe["perdas"].iloc[0]
    prodt_esp = df_hidr_uhe["produtibilidade_especifica"].iloc[0]
    cota_65 = vol_cota_A0 + vol_cota_A1 + vol_cota_A2 + vol_cota_A3 + vol_cota_A4
    fprodt_65 = (cota_65 - cota_med_fuga - perdas)*prodt_esp
    return fprodt_65

def encontraUsinaJusante(codigo_usi, df_confhd):
    df_conf_uhe = df_confhd.loc[(df_confhd["codigo_usina"] == codigo_usi)].reset_index(drop = True)
    return df_conf_uhe["codigo_usina_jusante"].iloc[0]
    
def calcula_prodt_acum_65(codigo_usi, df_confhd, df_hidr):
    usi_jusante = codigo_usi
    prodt = calcula_prodt_65(codigo_usi, df_hidr)
    #print("codigo_usi: ", codigo_usi, " prodt: ", prodt)
    while (usi_jusante != 0):
        usi_jusante = encontraUsinaJusante(usi_jusante, df_confhd)
        if(usi_jusante != 0):
            prodt += calcula_prodt_65(usi_jusante, df_hidr)
            #print("usi_jusante: ", usi_jusante, " prodt: ", prodt)
    return prodt


caminho = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\Capitulo_5\\caso_mini_500Cen_cluster_semanais\\"
#caminho = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\Capitulo_5\\caso_mini_500Cen\\"
#caminho = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\Capitulo_5\\caso_mini_300Cen_sorteio\\"
### VAZOES_FEIXES_INCR_SIN
#arquivo = "avaliaArvores\\A_50_5_2_Teste\\estatisticasArvores"
arquivo = "avaliaArvores\\A_25_10_2_Teste\\estatisticasArvores"
#arquivo = "avaliaArvores\\A_125_2_2_Teste\\estatisticasArvores"
#arquivo = "avaliaArvores\\A_50_5_2\\estatisticasArvores_50_5_2"
#arquivo = "avaliaArvores\\A_25_10_2\\estatisticasArvores_25_10_2"
#arquivo = "avaliaArvores\\A_5_50_2\\estatisticasArvores_5_50_2"
#arquivo = "avaliaArvores\\A_125_2_2\\BKAssimetrico_ENA\\estatisticasArvores_ENA"
#arquivo = "avaliaArvores\\A_50_5_2\\BKAssimetrico_ENA\\estatisticasArvores_ENA"
#arquivo = "avaliaArvores\\A_25_10_2\\BKAssimetrico_ENA\\estatisticasArvores_ENA"
#df = pd.read_csv("estatisticasArvores.csv", sep=";")
df = pd.read_csv(caminho+arquivo+".csv", sep=";")
df = df.dropna().reset_index(drop = True)
print(df)
print(df.columns)

#df = df.loc[ df["mediaOrig"].str.replace(",", ".").astype(float) > 30].reset_index(drop = True)
#df = df.loc[ df["stdOrig"].str.replace(",", ".").astype(float) > 30].reset_index(drop = True)
tipos = df["TIPO"].unique()
casos = df["CASO"].unique()
estagios = df["EST"].unique()
postos = df["POSTO"].unique()

df_vazoes = pd.read_csv(caminho+"cenarios.csv")
caminho_deck = "deck_newave_2020_01"
#caminho_deck = "deck_newave_2020_01_reduzido_180325"
#caminho_deck = "deck_newave_2020_01_reduzido_180325_postosAlterados"
df_confhd = Confhd.read(caminho_deck+"\\CONFHD.dat").usinas
df_hidr = Hidr.read(caminho_deck+"\\HIDR.dat").cadastro
df_hidr = df_hidr.reset_index()

lista_df_ena = []
for uhe in postos:
    df_conf_uhe = df_confhd.loc[(df_confhd["posto"] == uhe)].reset_index(drop = True)
    if(not df_conf_uhe.empty):
        codigo_usi = df_conf_uhe["codigo_usina"].iloc[0]
        fprodt_acum_65 = calcula_prodt_acum_65(codigo_usi, df_confhd,  df_hidr)
        df_uhe = df_vazoes.loc[(df_vazoes["NOME_UHE"] == uhe)].reset_index(drop = True)
        df_ena = df_uhe.copy()
        df_ena["VAZAO"] = fprodt_acum_65*df_uhe["VAZAO"]
        df_ena["VAZAO"] = df_ena["VAZAO"].round(0)
        lista_df_ena.append(df_ena)
        #print("uhe: ", uhe, " fprodt_acum_65: ", fprodt_acum_65)


df_ena_result = pd.concat(lista_df_ena)
df_ena_result_mean = df_ena_result.groupby('NOME_UHE')['VAZAO'].mean().reset_index(drop = False)
df_ena_result_mean = df_ena_result_mean.rename(columns={'VAZAO': 'ENA'})
df_ena_result_mean["ENA"] = df_ena_result_mean["ENA"].round(2)
ENA_SIN = round(df_ena_result_mean["ENA"].sum(),2)
print(df_ena_result_mean)
print(ENA_SIN)

print("Calculo de contribuição dos postos na ENA do SIN, OK.")


def representacaoNaEnaDOSIN(listaPostos, df_ena):
    valor = 0
    ENA_SIN = round(df_ena["ENA"].sum(),2)
    for posto in listaPostos:
        ena = df_ena.loc[(df_ena["NOME_UHE"] == posto), "ENA"]
        if not ena.empty and pd.notna(ena.iloc[0]):
            valor += ena.iloc[0]
    representacao_ena_sin = round((valor/ENA_SIN)*100,2)
    return representacao_ena_sin

def retornaDF_Resultado(listaPostos, texto):
    lista_df_temp = []
    for posto in listaPostos:
        df_resultado = pd.DataFrame(
            {
                "TIPO":[tipo],
                "CASO":[caso],
                "EST":[est],
                "FALHA":[texto],
                "POSTO":[posto]
            }
        )
        lista_df_temp.append(df_resultado)
    return pd.concat(lista_df_temp)

dicionarioFalhas = {
    "FALHA_T_TEST":["FALHA_T_TEST"],
    "FALHA_W-TEST":["FALHA_W-TEST"],
    "FALHA_F_TEST":["FALHA_F-TEST"],
    "FALHA_L_TEST":["FALHA_L-TEST"],
    "FALHA_P_Boot_mean":["FALHA_P_Boot_mean"],
    "FALHA_P_Boot_Variance":["FALHA_P_Boot_Variance"],
    "mean_limite":["Média Viol. LimInf", "Média Viol. LimSup"],
    "std_limite":["Std Viol. LimInf", "Std Viol. LimSup"],
    "distribution":["FALHA_KS-TEST"]
}

dicionarioFalhasGerais = {
    "hypotesis_mean":["FALHA_T_TEST"], # "FALHA_T_TEST", "FALHA_W-TEST" ,"FALHA_P_Boot_mean"
    "hypotesis_variance":["FALHA_L-TEST"], # "FALHA_F-TEST", , "FALHA_P_Boot_Variance"
    "mean_limite":["Média Viol. LimInf", "Média Viol. LimSup"],
    "std_limite":["Std Viol. LimInf", "Std Viol. LimSup"],
    "distribution":["FALHA_KS-TEST"]
}

dicionarioFalhasGlobais = {
    "fail_mean":[ "FALHA_T_TEST", "Média Viol. LimInf", "Média Viol. LimSup"], # "FALHA_T_TEST", "FALHA_P_Boot_mean", ,
    "fail_variance":["FALHA_L-TEST", "Std Viol. LimInf", "Std Viol. LimSup"], # "FALHA_F-TEST", "FALHA_P_Boot_Variance", 
    "distribution":["FALHA_KS-TEST"]
}


significancia = 0.05
lista_relatorio = []
for tipo in tipos:
    df_1 = df.loc[(df["TIPO"] == tipo)]

    for caso in casos:
        df_2 = df_1.loc[(df_1["CASO"] == caso)]
        for est in estagios:
            print("CASO: ", caso, " EST: ", est)
            df_est = df_2.loc[(df_2["EST"] == est)]
            df_est = df_est.replace(",", ".", regex=True)
            df_est = df_est.apply(pd.to_numeric, errors='ignore')
            
            df_falha_FTest = df_est.loc[(df_est["F_p_valor"] < significancia)]["POSTO"].tolist()
            print("Falha F-TEST: ", df_falha_FTest)
            if(len(df_falha_FTest) != 0):
                df_resultado = retornaDF_Resultado(df_falha_FTest, "FALHA_F-TEST")
                lista_relatorio.append(df_resultado)
            
            df_falha_TTest = df_est.loc[(df_est["T_p_valor"] < significancia)]["POSTO"].tolist()
            print("Falha T-TEST: ", df_falha_TTest)
            if(len(df_falha_TTest) != 0):
                df_resultado = retornaDF_Resultado(df_falha_TTest, "FALHA_T_TEST")
                lista_relatorio.append(df_resultado)

            df_falha_KSTest = df_est.loc[(df_est["KS_p_valor"] < significancia)]["POSTO"].tolist()
            print("Falha KS-TEST: ", df_falha_KSTest)
            if(len(df_falha_KSTest) != 0):
                df_resultado = retornaDF_Resultado(df_falha_KSTest, "FALHA_KS-TEST")
                lista_relatorio.append(df_resultado)

            df_falha_Levene = df_est.loc[(df_est["L_p_valor"] < significancia)]["POSTO"].tolist()
            print("Falha L-TEST: ", df_falha_Levene)
            if(len(df_falha_Levene) != 0):
                df_resultado = retornaDF_Resultado(df_falha_Levene, "FALHA_L-TEST")
                lista_relatorio.append(df_resultado)

            df_falha_Wilcoxon = df_est.loc[(df_est["Wilcoxon_p_valor"] < significancia)]["POSTO"].tolist()
            print("Falha W-TEST: ", df_falha_Wilcoxon)
            if(len(df_falha_Wilcoxon) != 0):
                df_resultado = retornaDF_Resultado(df_falha_Wilcoxon, "FALHA_W-TEST")
                lista_relatorio.append(df_resultado)

            df_falha_Bootstrap_mean = df_est.loc[(df_est["P_Boot_mean"] < significancia)]["POSTO"].tolist()
            print("Falha P_Boot_mean: ", df_falha_Bootstrap_mean)
            if(len(df_falha_Bootstrap_mean) != 0):
                df_resultado = retornaDF_Resultado(df_falha_Bootstrap_mean, "FALHA_P_Boot_mean")
                lista_relatorio.append(df_resultado)

            df_falha_Bootstrap_variance = df_est.loc[(df_est["P_Boot_Variance"] < significancia)]["POSTO"].tolist()
            print("Falha P_Boot_Variance: ", df_falha_Bootstrap_variance)
            if(len(df_falha_Bootstrap_variance) != 0):
                df_resultado = retornaDF_Resultado(df_falha_Bootstrap_variance, "FALHA_P_Boot_Variance")
                lista_relatorio.append(df_resultado)

            #folga_inf = 0.95
            #folga_sup  = 1.05
            folga_inf = 1
            folga_sup  = 1
            #print("Low_ci_95_var_red: ", np.sqrt(df_est["Low_ci_95_var_orig"]))
            #print("Low_ci_95_var_red: ", df_est["stdLimInf95"])
            #exit(1)
            #df_est["mean_violLimInf"] = df_est["mediaRed"] < df_est["mediaLimInf95"]*folga_inf
            #df_est["mean_violLimSup"] = df_est["mediaRed"] > df_est["mediaLimSup95"]*folga_sup
            #df_est["std_violLimInf"] = df_est["stdRed"] < df_est["stdLimInf95"]*folga_inf
            #df_est["std_violLimSup"] = df_est["stdRed"] > df_est["stdLimSup95"]*folga_sup
            df_est["mean_violLimInf"] = df_est["mediaRed"] < df_est["Low_ci_95_mean_orig"]*folga_inf
            df_est["mean_violLimSup"] = df_est["mediaRed"] > df_est["Sup_ci_95_mean_orig"]*folga_sup
            df_est["std_violLimInf"] = df_est["stdRed"] < np.sqrt(df_est["Low_ci_95_var_orig"])*folga_inf
            df_est["std_violLimSup"] = df_est["stdRed"] > np.sqrt(df_est["Sup_ci_95_var_orig"])*folga_sup            
            
            df_mean_violLimInf = df_est.loc[(df_est["mean_violLimInf"]== True)]["POSTO"].tolist()
            #print("Mean Viol LimInf: ", df_mean_violLimInf)
            if(len(df_mean_violLimInf) != 0):
                df_resultado = retornaDF_Resultado(df_mean_violLimInf, "Média Viol. LimInf")
                lista_relatorio.append(df_resultado)

            df_mean_violLimSup = df_est.loc[(df_est["mean_violLimSup"]== True)]["POSTO"].tolist()
            #print("Mean Viol LimSup: ", df_mean_violLimSup)
            if(len(df_mean_violLimSup) != 0):
                df_resultado = retornaDF_Resultado(df_mean_violLimSup, "Média Viol. LimSup")
                lista_relatorio.append(df_resultado)

            df_std_violLimInf = df_est.loc[(df_est["std_violLimInf"]== True)]["POSTO"].tolist()
            #print("Std Viol LimInf: ", df_std_violLimInf)
            if(len(df_std_violLimInf) != 0):
                df_resultado = retornaDF_Resultado(df_std_violLimInf, "Std Viol. LimInf")
                lista_relatorio.append(df_resultado)

            df_std_violLimSup = df_est.loc[(df_est["std_violLimSup"]== True)]["POSTO"].tolist()
            #print("Std Viol LimSup: ", df_std_violLimSup)
            if(len(df_std_violLimSup) != 0):
                df_resultado = retornaDF_Resultado(df_std_violLimSup, "Std Viol. LimSup")
                lista_relatorio.append(df_resultado)

            #print(df_est.columns)
            
resultado_final_analise = pd.concat(lista_relatorio).reset_index(drop = True)


print(resultado_final_analise)

falhas = resultado_final_analise["FALHA"].unique()
print(falhas)




lista_df_todosTestes = []
for tipo_falha in dicionarioFalhas:
    falhas_tipo = dicionarioFalhas[tipo_falha]
    resultado_final_analise_falhas = resultado_final_analise[resultado_final_analise["FALHA"].isin(falhas_tipo)]
    ## PERCORRE PRIMEIRO FALHAS DE MEDIA, DEPOIS FALHAS DE VARIANCIA E DEPOIS FALHAS DE DISTRIBUICAO PROBABILISTICA
    for est in estagios:
        df_resultados_est = resultado_final_analise_falhas.loc[(resultado_final_analise_falhas["EST"] == est) ].reset_index(drop = True)
        for tipo in tipos:
            df_tipo = df_resultados_est.loc[(df_resultados_est["TIPO"] == tipo)].reset_index(drop = True)
            for caso in casos:
                df_caso = df_tipo.loc[(df_tipo["CASO"] == caso)].reset_index(drop = True)
                counts = df_caso["POSTO"].value_counts()
                posto_aoMenosUmaFalha = df_caso["POSTO"].unique()
                print("FALHA: ", tipo_falha, " EST: ", est, " tipo: ", tipo, " caso: ", caso, " ENA: ", representacaoNaEnaDOSIN(posto_aoMenosUmaFalha, df_ena_result_mean))
                print(" postos: ", df_caso["POSTO"].tolist())
                repeated_postos = counts[counts >= len(falhas)].index.tolist()
                lista_df_todosTestes.append(
                    pd.DataFrame(
                        {
                            "TIPO":[tipo],
                            "CASO":[caso],
                            "FALHA":[tipo_falha],
                            "EST":[est],
                            "TESTE":["FALHOU_AO_MENOS_UMTESTE"],
                            "NPOSTOS":[round(len(posto_aoMenosUmaFalha)/len(postos),2)*100],
                            "PERC.ENA":[representacaoNaEnaDOSIN(posto_aoMenosUmaFalha, df_ena_result_mean)]
                        }
                    )
                )
df_falhaTestesContagem = pd.concat(lista_df_todosTestes).reset_index(drop = True)
print(df_falhaTestesContagem)
df_falhaTestesContagem.to_csv(caminho+"\\"+arquivo+"_resultados.csv", index = False)

lista_df_todosTestes = []
lista_df_todosTestesTodosEstagios = []
for tipo_falha in dicionarioFalhasGerais:
    falhas_tipo = dicionarioFalhasGerais[tipo_falha]
    resultado_final_analise_falhas = resultado_final_analise[resultado_final_analise["FALHA"].isin(falhas_tipo)]
    ## PERCORRE PRIMEIRO FALHAS DE MEDIA, DEPOIS FALHAS DE VARIANCIA E DEPOIS FALHAS DE DISTRIBUICAO PROBABILISTICA
    for est in estagios:
        df_resultados_est = resultado_final_analise_falhas.loc[(resultado_final_analise_falhas["EST"] == est) ].reset_index(drop = True)
        for tipo in tipos:
            df_tipo = df_resultados_est.loc[(df_resultados_est["TIPO"] == tipo)].reset_index(drop = True)
            for caso in casos:
                df_caso = df_tipo.loc[(df_tipo["CASO"] == caso)].reset_index(drop = True)
                counts = df_caso["POSTO"].value_counts()
                posto_aoMenosUmaFalha = df_caso["POSTO"].unique()
                print("FALHA: ", tipo_falha, " EST: ", est, " tipo: ", tipo, " caso: ", caso, " ENA: ", representacaoNaEnaDOSIN(posto_aoMenosUmaFalha, df_ena_result_mean))
                print(" postos: ", df_caso["POSTO"].tolist())
                repeated_postos = counts[counts >= len(falhas)].index.tolist()
                lista_df_todosTestes.append(
                    pd.DataFrame(
                        {
                            "TIPO":[tipo],
                            "CASO":[caso],
                            "FALHA":[tipo_falha],
                            "EST":[est],
                            "TESTE":["FALHOU_AO_MENOS_UMTESTE"],
                            "NPOSTOS":[round(len(posto_aoMenosUmaFalha)/len(postos),2)*100],
                            "PERC.ENA":[representacaoNaEnaDOSIN(posto_aoMenosUmaFalha, df_ena_result_mean)]
                        }
                    )
                )


    ## PERCORRE PRIMEIRO FALHAS DE MEDIA, DEPOIS FALHAS DE VARIANCIA E DEPOIS FALHAS DE DISTRIBUICAO PROBABILISTICA
    for tipo in tipos:
        df_tipo = resultado_final_analise_falhas.loc[(resultado_final_analise_falhas["TIPO"] == tipo)].reset_index(drop = True)
        for caso in casos:
            df_caso = df_tipo.loc[(df_tipo["CASO"] == caso)].reset_index(drop = True)
            counts = df_caso["POSTO"].value_counts()
            posto_aoMenosUmaFalha = df_caso["POSTO"].unique()
            print("FALHA: ", tipo_falha, " EST: ", est, " tipo: ", tipo, " caso: ", caso, " ENA: ", representacaoNaEnaDOSIN(posto_aoMenosUmaFalha, df_ena_result_mean))
            print(" postos: ", df_caso["POSTO"].tolist())
            repeated_postos = counts[counts >= len(falhas)].index.tolist()
            lista_df_todosTestesTodosEstagios.append(
                pd.DataFrame(
                    {
                        "TIPO":[tipo],
                        "CASO":[caso],
                        "FALHA":[tipo_falha],
                        "TESTE":["FALHOU_AO_MENOS_UMTESTE"],
                        "NPOSTOS":[round(len(posto_aoMenosUmaFalha)/len(postos),2)*100],
                        "PERC.ENA":[representacaoNaEnaDOSIN(posto_aoMenosUmaFalha, df_ena_result_mean)]
                    }
                )
            )

df_falhaTestesContagem = pd.concat(lista_df_todosTestes).reset_index(drop = True)
print(df_falhaTestesContagem)
df_falhaTestesContagem.to_csv(caminho+"\\"+arquivo+"_resultados_gerais.csv", index = False)
df_falhaTestesContagemGeralTodosEstagios = pd.concat(lista_df_todosTestesTodosEstagios).reset_index(drop = True)
df_falhaTestesContagemGeralTodosEstagios.to_csv(caminho+"\\"+arquivo+"_resultados_gerais_geral_todosEstagios.csv", index = False)
print(df_falhaTestesContagemGeralTodosEstagios)

lista_df_todosTestes = []
lista_df_todosTestesTodosEstagios = []
for tipo_falha in dicionarioFalhasGlobais:
    falhas_tipo = dicionarioFalhasGlobais[tipo_falha]
    resultado_final_analise_falhas = resultado_final_analise[resultado_final_analise["FALHA"].isin(falhas_tipo)]
    ## PERCORRE PRIMEIRO FALHAS DE MEDIA, DEPOIS FALHAS DE VARIANCIA E DEPOIS FALHAS DE DISTRIBUICAO PROBABILISTICA
    for est in estagios:
        df_resultados_est = resultado_final_analise_falhas.loc[(resultado_final_analise_falhas["EST"] == est) ].reset_index(drop = True)
        for tipo in tipos:
            df_tipo = df_resultados_est.loc[(df_resultados_est["TIPO"] == tipo)].reset_index(drop = True)
            for caso in casos:
                df_caso = df_tipo.loc[(df_tipo["CASO"] == caso)].reset_index(drop = True)
                counts = df_caso["POSTO"].value_counts()
                posto_aoMenosUmaFalha = df_caso["POSTO"].unique()
                #print("FALHA: ", tipo_falha, " EST: ", est, " tipo: ", tipo, " caso: ", caso, " ENA: ", representacaoNaEnaDOSIN(posto_aoMenosUmaFalha, df_ena_result_mean))
                #print(" postos: ", df_caso["POSTO"].tolist())
                repeated_postos = counts[counts >= len(falhas)].index.tolist()
                lista_df_todosTestes.append(
                    pd.DataFrame(
                        {
                            "TIPO":[tipo],
                            "CASO":[caso],
                            "FALHA":[tipo_falha],
                            "EST":[est],
                            "TESTE":["FALHOU_AO_MENOS_UMTESTE"],
                            "NPOSTOS":[round(len(posto_aoMenosUmaFalha)/len(postos),2)*100],
                            "PERC.ENA":[representacaoNaEnaDOSIN(posto_aoMenosUmaFalha, df_ena_result_mean)]
                        }
                    )
                )


    ## PERCORRE PRIMEIRO FALHAS DE MEDIA, DEPOIS FALHAS DE VARIANCIA E DEPOIS FALHAS DE DISTRIBUICAO PROBABILISTICA
    for tipo in tipos:
        df_tipo = resultado_final_analise_falhas.loc[(resultado_final_analise_falhas["TIPO"] == tipo)].reset_index(drop = True)
        for caso in casos:
            df_caso = df_tipo.loc[(df_tipo["CASO"] == caso)].reset_index(drop = True)
            counts = df_caso["POSTO"].value_counts()
            posto_aoMenosUmaFalha = df_caso["POSTO"].unique()
            #print("FALHA: ", tipo_falha, " EST: ", est, " tipo: ", tipo, " caso: ", caso, " ENA: ", representacaoNaEnaDOSIN(posto_aoMenosUmaFalha, df_ena_result_mean))
            #print(" postos: ", df_caso["POSTO"].tolist())
            repeated_postos = counts[counts >= len(falhas)].index.tolist()
            lista_df_todosTestesTodosEstagios.append(
                pd.DataFrame(
                    {
                        "TIPO":[tipo],
                        "CASO":[caso],
                        "FALHA":[tipo_falha],
                        "TESTE":["FALHOU_AO_MENOS_UMTESTE"],
                        "NPOSTOS":[round(len(posto_aoMenosUmaFalha)/len(postos),2)*100],
                        "PERC.ENA":[representacaoNaEnaDOSIN(posto_aoMenosUmaFalha, df_ena_result_mean)]
                    }
                )
            )

df_falhaTestesContagem = pd.concat(lista_df_todosTestes).reset_index(drop = True)
df_falhaTestesContagemTodosEstagios = pd.concat(lista_df_todosTestesTodosEstagios).reset_index(drop = True)
print(df_falhaTestesContagemTodosEstagios)
df_falhaTestesContagem.to_csv(caminho+"\\"+arquivo+"_resultados_gerais_globais.csv", index = False)
df_falhaTestesContagemTodosEstagios.to_csv(caminho+"\\"+arquivo+"_resultados_gerais_globais_todosEstagios.csv", index = False)





exit(1)
lista_df_testeArvores = []
with open(aquivo+".txt", "w") as report_file:
    report_file.write(f"=== RELATÓRIO DE CONSTRUÇÃO DA ÁRVORE DE CENÁRIOS ===\n")
    report_file.write("=" * 50 + "\n\n")
    report_file.write(f"Total de Postos {len(postos)}.\n")
    report_file.write(f"Total de Árvores {len(casos)}.\n")
    report_file.write(f"Total de Estágios {len(estagios)}.\n")
    report_file.write(f"ESTUDO: {tipo}\n")
    report_file.write("=" * 20 + "\n")
    for falha in falhas:
        report_file.write(f"TESTE: {falha}\n")
        report_file.write("=" * 20 + "\n")
        for est in estagios:
            report_file.write(f"=== ESTÁGIO: {est} ===\n")
            df_filtered_est = resultado_final_analise.loc[(resultado_final_analise["FALHA"] == falha)  & (resultado_final_analise["EST"] == est) ].reset_index(drop = True)
            
            for caso in casos:
                df_filtered = df_filtered_est.loc[(df_filtered_est["CASO"] == caso)].reset_index(drop = True)
                postos_analise = df_filtered["POSTO"].tolist()
                # Write results to file
                report_file.write(f"CASO: {caso}\n")
                report_file.write(f"Postos que falharam o teste   (%): {round(len(postos_analise)/len(postos),2)*100}.\n")
                report_file.write(f"Postos que falharam o teste   (N.): {len(postos_analise)}.\n")
                report_file.write(f"Representatividade ENA do SIN (%): {representacaoNaEnaDOSIN(postos_analise, df_ena_result_mean)}.\n")
                report_file.write(f"Postos que falharam o teste: {postos_analise}\n")
                report_file.write("=" * 20 + "\n")

        for caso in casos:
            lista_postos_falha_estagios = []
            df_filtered_caso = resultado_final_analise.loc[(resultado_final_analise["FALHA"] == falha)  & (resultado_final_analise["CASO"] == caso)].reset_index(drop = True)
            counts = df_filtered_caso["POSTO"].value_counts()
            posto_aoMenosUmaFalha = df_filtered_caso["POSTO"].unique()
            repeated_postos = counts[counts >= len(estagios)].index.tolist()
            lista_df_testeArvores.append(
                pd.DataFrame({
                    "CASO":[caso],
                    "FALHA":[falha],
                    "TESTE":["AO_MENOS_UMA_FALHA"],
                    "NPOSTOS":[round(len(posto_aoMenosUmaFalha)/len(postos),2)*100],
                    "PERC.ENA":[representacaoNaEnaDOSIN(posto_aoMenosUmaFalha, df_ena_result_mean)]
                })
            )
            lista_df_testeArvores.append(
                pd.DataFrame({
                    "CASO":[caso],
                    "FALHA":[falha],
                    "TESTE":["FALHA_TODOS_EST"],
                    "NPOSTOS":[round(len(repeated_postos)/len(postos),2)*100],
                    "PERC.ENA":[representacaoNaEnaDOSIN(repeated_postos, df_ena_result_mean)]
                })
            )

    

            print("POSTOs that appear more than twice:", repeated_postos)
            print("caso: ", caso, " df: ", df_filtered_caso)


df_resultado_arvores = pd.concat(lista_df_testeArvores)
df_resultado_arvores.to_csv("resultadoTotalFalhasArvores.csv", index = False)
print(df_resultado_arvores)

print("Report generated: test_report.txt")
exit(1)

df_arvore_original = pd.read_csv("arvore_estudo.csv")
#print(df_arvore_original)
df_vazoes = pd.read_csv("vazoes_estudo.csv")
#print(df_vazoes)
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


# Function to calculate weighted mean
def weighted_mean(data, weights):
    return np.sum(weights * data) 

# Function to calculate weighted variance
def weighted_variance(data, weights):
    mean = weighted_mean(data, weights)
    variance = np.sum(weights * (data - mean)**2) 
    return variance

# Function to calculate weighted covariance between two datasets
def weighted_covariance(data_x, data_y, weights):
    mean_x = np.average(data_x, weights=weights)
    mean_y = np.average(data_y, weights=weights)
    covariance = np.sum(weights * (data_x - mean_x) * (data_y - mean_y)) 
    return covariance

def weighted_correlation(data_x, data_y, weights):
    covariance = weighted_covariance(data_x, data_y, weights)
    var_x = weighted_variance(data_x, weights)
    var_y = weighted_variance(data_y, weights)
    correlation = covariance / np.sqrt(var_x * var_y)
    return correlation

tipo = "ENAAgregado\\"
tipo = "VazaoIncrementalMultidimensional\\"
casos = ["Arvore1", "Arvore2", "Arvore3", "Arvore4", "Arvore5", "Arvore6"]
#casos = ["Arvore6"]
lista_df_final = []
usinas = df_vazoes["NOME_UHE"].unique()
print(usinas)
usinas = [17, 275, 66]
usinas = [66,	45,	46,	285,	292,	275,	172,	176,	6,	169,	33,	74,	75,	40,	25,	42,	39,	229,	178,
                43,	38,	227,	37,	17,	271,	47,	270,	24,	209,	31,	211,	215,	34,	204,	1,	18,	126,	291,
                61,	7,	247,	294,	49,	57,	123,	12,	205,	121]
fig = make_subplots(rows=6, cols=3, subplot_titles=(" ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " "))
#fig = make_subplots(rows=6, cols=3, subplot_titles=([" "] * 18))  # 6x3 grid

linha = 1
coluna = 1
contador = 0
for caso in casos:
    df_arvore_reduzida = pd.read_csv(tipo+caso+"\\df_arvore_reduzida.csv")
    #estagios = [2,3,4]
    estagios = [4,3,2]
    for est in estagios:
        prob_original = []
        prob_red = []
        df_orig_est = df_arvore_original.loc[(df_arvore_original["PER"] == est)].reset_index(drop = True)
        for no in df_orig_est["NO"].unique():
            prob = 1
            lista_caminho = retorna_lista_caminho(no, df_arvore_original)[:-1]
            for elemento in lista_caminho:
                prob_elemento = df_arvore_original.loc[(df_arvore_original["NO"] == elemento)]["PROB"].iloc[0]
                prob = prob*prob_elemento
            prob_original.append(prob)    
        
        df_red_est = df_arvore_reduzida.loc[(df_arvore_reduzida["PER"] == est)].reset_index(drop = True)
        for no in df_red_est["NO"].unique():
            prob = 1
            lista_caminho = retorna_lista_caminho(no, df_arvore_reduzida)[:-1]
            for elemento in lista_caminho:
                prob_elemento = df_arvore_reduzida.loc[(df_arvore_reduzida["NO"] == elemento)]["PROB"].iloc[0]
                prob = prob*prob_elemento
            prob_red.append(prob)   
        prob_original = prob_original / np.sum(prob_original)
        prob_red = prob_red / np.sum(prob_red)
        dict_atributos_original = {}
        dict_atributos_reduzida = {}
        for usi in usinas:
            lista_original = []
            lista_red = []
            for no in df_orig_est["NO"].unique():
                vazao = df_vazoes.loc[(df_vazoes["NOME_UHE"] == usi) & (df_vazoes["NO"] == no)].reset_index(drop = True)["VAZAO"].iloc[0]
                lista_original.append(vazao)            
            for no in df_red_est["NO"].unique():
                vazao = df_vazoes.loc[(df_vazoes["NOME_UHE"] == usi) & (df_vazoes["NO"] == no)].reset_index(drop = True)["VAZAO"].iloc[0]
                lista_red.append(vazao)
            lista_original = np.array(lista_original)
            lista_red = np.array(lista_red)
            dict_atributos_original[usi] = lista_original
            dict_atributos_reduzida[usi] = lista_red

        # Initialize dictionaries for storing correlations
        dicionario_correlacao_original = {}
        dicionario_correlacao_reduzida = {}
        # Calculate correlation between all pairs of usinas
        lista_correl_orig = []
        lista_correl_red = []
        for i, usi_x in enumerate(usinas):
            for j, usi_y in enumerate(usinas):
                if i < j:  # Ensure only the upper triangular part is considered
                    try:
                        corr_orig = weighted_correlation(dict_atributos_original[usi_x], dict_atributos_original[usi_y], prob_original)
                        
                        corr_red = weighted_correlation(dict_atributos_reduzida[usi_x], dict_atributos_reduzida[usi_y], prob_red)
                        dicionario_correlacao_original[(usi_x, usi_y)] = corr_orig
                        dicionario_correlacao_reduzida[(usi_x, usi_y)] = corr_red

                        lista_correl_orig.append(corr_orig)
                        lista_correl_red.append(corr_red)
                    except Exception as e:
                        print(f"Error calculating correlation for {usi_x} and {usi_y}: {e}")
        
        # Compute R^2 using linear regression
        slope, intercept, r_value, p_value, std_err = linregress(lista_correl_orig, lista_correl_red)
        print(slope)
        print(intercept)
        print(r_value)
        print(r_value**2)
        print(p_value)
        print(std_err)
        r_squared = r_value**2

        r_squared = r2_score(lista_correl_orig, lista_correl_red)
        print("R-squared:", r_squared)



        fig.add_trace(go.Scatter(
            x=lista_correl_orig, 
            y=lista_correl_red, 
            mode='markers',
            name=f' {caso} {str(est)} (R² = {r_squared:.2f})',
            showlegend=False,
            marker=dict(size=10, color='blue')
        ), row=linha, col=coluna)

        # Add line of best fit
        fig.add_trace(go.Scatter(
            x=lista_correl_orig, 
            y=slope * np.array(lista_correl_orig) + intercept, 
            mode='lines', 
            line=dict(color='red', width=2),
            showlegend=False
        ), row=linha, col=coluna)

        # Add R² annotation
        axis_index = (linha - 1) * 3 + coluna  # Correct axis index for 6x3 grid
        fig.add_annotation(
            x=0.9,  # X position (relative to subplot domain)
            y=0.1,  # Y position (relative to subplot domain)
            xref=f"x{axis_index}",  # Dynamic x-axis reference
            yref=f"y{axis_index}",  # Dynamic y-axis reference
            text=f"R² = {r_squared:.2f}",
            showarrow=False,
            font=dict(size=20, color="black"),
            align="right"
        )


        titulo =  "Caso: " + caso + " Est: "+str(est)
        fig.layout.annotations[contador].update(text=titulo, font=dict(size=20)) 
        contador += 1
        #print("linha: ", linha, " coluna: ", coluna, " anotation: ", contador, " axis_index: ", axis_index)
        coluna = coluna + 1
        if(coluna == 4):
            coluna = 1
            linha = linha + 1

        print(f" Caso {caso} Est {est} R²: {r_squared:.2f}")
        # Print the results
        #print("ORIGINAL: ")
        #print(dicionario_correlacao_original)
        #print("REDUZIDA")
        #print(dicionario_correlacao_reduzida)
    # Customize layout
    fig.update_layout(
        title="Correlações Árvore Original x Construída",
        title_font=dict(size=24, family="Arial", color="black"),
        xaxis_title="Correl. Orig.",
        yaxis_title="Correl. Red.",
        font=dict(size=20), 
        xaxis=dict(title_font=dict(size=20)),  
        yaxis=dict(title_font=dict(size=20)),
        showlegend=False
    )
    fig.write_html(tipo.split("\\")[0]+"_correlacaoEspacialArvores.html")
    # Print R² value





