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


caminho = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\Academico\\exercicio_10D\\128_Aberturas_Equiprovavel\\"
caminho = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\Capitulo_5\\caso_mini_500Cen_cluster_semanais\\avaliaArvoresRepresentativo\\"
#caminho = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\Capitulo_5\\caso_mini_500Cen\\"
#caminho = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\Capitulo_5\\caso_mini_300Cen_sorteio\\"
### VAZOES_FEIXES_INCR_SIN
#arquivo = "avaliaArvores\\A_50_5_2_Teste\\estatisticasArvores"
#arquivo = "avaliaArvoresSIN\\A_50_5_2_Teste\\estatisticasArvores"
#arquivo = "avaliaArvoresRepresentativo\\Reducao_ENA\\A_25_250_500\\estatisticasArvores"
#arquivo = "avaliaArvoresRepresentativo\\Reducao_ENA\\A_25_250_500\\estatisticasArvores"
#arquivo = "avaliaArvores\\A_125_2_2_Teste\\estatisticasArvores"
#arquivo = "avaliaArvores\\A_50_5_2\\estatisticasArvores_50_5_2"
#arquivo = "avaliaArvores\\A_25_10_2\\estatisticasArvores_25_10_2"
#arquivo = "avaliaArvores\\A_5_50_2\\estatisticasArvores_5_50_2"
#arquivo = "avaliaArvores\\A_125_2_2\\BKAssimetrico_ENA\\estatisticasArvores_ENA"
#arquivo = "avaliaArvores\\A_50_5_2\\BKAssimetrico_ENA\\estatisticasArvores_ENA"
arquivo = "avaliaArvores\\A_25_10_2\\BKAssimetrico_ENA\\estatisticasArvores_ENA"
arquivo = "Academicos\\A_4x4x2\\estatisticasArvores"
arquivo = "revisaoDebora\\A_25x3x2\\estatisticasArvores"
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

df_vazoes = pd.read_csv(caminho+"GTMIN\\Pente\\cenarios.csv")
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
                            "TNP":[round(len(posto_aoMenosUmaFalha),2)],
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
                            "TNP":[round(len(posto_aoMenosUmaFalha),2)],

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
                        "TNP":[round(len(posto_aoMenosUmaFalha),2)],

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
                            "TNP":[round(len(posto_aoMenosUmaFalha),2)],

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
                        "TNP":[round(len(posto_aoMenosUmaFalha),2)],

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
