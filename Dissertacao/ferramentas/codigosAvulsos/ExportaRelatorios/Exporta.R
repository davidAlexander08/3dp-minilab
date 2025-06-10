library(kSamples)
library(RVAideMemoire)
library(Hmisc)
library(matrixStats)
library(Weighted.Desc.Stat)
library(e1071)
library(boot)
library(weights)
library(emdist)
library(transport)
library(plotly)
library(ggplot2)
library(htmlwidgets)
library(webshot)
library(car)
library(ggplot2)
library(gridExtra)
library(grid)  # Load grid package for gpar()
library(dplyr)
library(Ecume)



# Function to get the children of a node
getFilhos <- function(no, df_arvore) {
  filhos <- df_arvore[df_arvore$NO_PAI == no, "NO"]
  return(filhos)
}

# Function to get the parent of a node
busca_pai <- function(no, df_arvore) {
  pai <- df_arvore[df_arvore$NO == no, "NO_PAI"][1]
  return(pai)
}

# Function to return the path of nodes (from current node to the root)
retorna_lista_caminho <- function(no, df_arvore) {
  lista <- list(no)
  no_inicial <- no
  periodo_no <- df_arvore[df_arvore$NO == no, "PER"][1]
  
  for (i in 1:(periodo_no - 1)) {
    pai <- busca_pai(no_inicial, df_arvore)
    lista <- c(lista, pai)  # Append the parent to the list
    no_inicial <- pai
  }
  
  return(lista)
}

df_arvore_original <- read.csv("C:/Users/testa/Documents/mestrado/ComparacaoArvoresBackwardReduction/arvore_estudo.csv")
df_vazoes <- read.csv("C:/Users/testa/Documents/mestrado/ComparacaoArvoresBackwardReduction/vazoes_estudo.csv")


# Set the parameters

tipo <- "ENAAgregado/"  # "VazaoIncrementalMultidimensional\\"
tipo <- "VazaoIncrementalMultidimensional/"
casos <- c("Arvore1", "Arvore2", "Arvore3", "Arvore4", "Arvore5", "Arvore6")
#casos <- c("Arvore1", "Arvore6" )
#casos <- c("Arvore6")
usinas <- unique(df_vazoes$NOME_UHE)
print(usinas)
lista_df_final <- list()
estagios <- c(4,3,2)


df <- data.frame(Value = numeric(), stringsAsFactors = FALSE)

data_list <- list()
df <- data.frame(TIPO = character(), CASO = character(), NOS = integer(), EST = integer(), POSTO = integer(), 
                 mediaOrig = numeric(), mediaRed = numeric(),
                 limT = numeric(), error_media = numeric(),
                 mediaLimInf = numeric(), mediaLimSup = numeric(),
                 stdOrig = numeric(), stdRed = numeric(),
                 stdLimInf = numeric(), stdLimSup = numeric(),
                 chi2_lower = numeric(), chi2_upper = numeric(),
                 assimOrig = numeric(), assimRed = numeric(),
                 kurtOrig = numeric(), kurtRed = numeric(),
                 DWasserstein = numeric(),
                 KS_Test = numeric(), KS_p_valor = numeric(),
                 T_Test = numeric(), T_p_valor = numeric(),
                 Welch_Test = numeric(), Welch_p_valor = numeric(), 
                 F_Test = numeric(), F_p_valor = numeric(),
                 Wilcoxon_Test = numeric(), Wilcoxon_p_valor = numeric(), stringsAsFactors = FALSE)


#new_row <- data.frame(TIPO = tipo, CASO = caso, EST = est, POSTO = usi, 
#                      mediaOrig = weighted_mean_Orig, mediaRed = weighted_mean_Red,
#                      limT = t_value, error_media = error_margin,
#                      mediaLimInf = limInf, mediaLimSup = limSup,
#                      stdOrig = weighted_sd_Orig, stdRed = weighted_sd_Red,
#                      stdLimInf = sd_lower, stdLimSup = sd_upper,
#                      chi2_lower = chi2_lower, chi2_upper = chi2_upper,
#                      assimOrig = Wskew_Orig, assimRed = Wskew_Red,
#                      kurtOrig = WKurto_Orig, kurtRed = WKurto_Red,
#                      DWasserstein = wasserstein_dist,
#                      KS_Test = ks_stat$statistic, KS_p_valor = ks_stat$p.value,
#                      T_Test = t_testWeightened$coefficients["t.value"], T_p_valor = t_testWeightened$coefficients["p.value"],
#                      Welch_Test = welch$statistic, Welch_p_valor = welch$p.value, 
#                      F_Test = f_test_result$statistic, F_p_valor = f_test_result$p.value,
#                      Wilcoxon_Test = wilcoxon$statistic, Wilcoxon_p_valor = wilcoxon$p.value)



for (caso in casos) {
  df_arvore_reduzida <- read.csv(paste0("C:/Users/testa/Documents/mestrado/ComparacaoArvoresBackwardReduction/",tipo,"/", caso, "/df_arvore_reduzida.csv"))
  for (est in estagios) {
    prob_original <- list()
    df_orig_est <- df_arvore_original[df_arvore_original$PER == est, ]
    for (no in unique(df_orig_est$NO)) {
      prob <- 1
      lista_caminho <- retorna_lista_caminho(no, df_arvore_original)[-length(retorna_lista_caminho(no, df_arvore_original))]
      lista_caminho = unlist(lista_caminho)
      for (elemento in lista_caminho) {
        prob_elemento <- df_arvore_original[df_arvore_original$NO == elemento, "PROB"][1]
        prob <- prob * prob_elemento
      }
      # Get the corresponding "VAZAO" for the node
      prob_original <- append(prob_original, prob)
    }
    prob_original <- unlist(prob_original)
    
    
    prob_red <- list()
    df_red_est <- df_arvore_reduzida[df_arvore_reduzida$PER == est, ]
    #print(df_red_est)
    for (no in unique(df_red_est$NO)) {
      #print(no)
      prob <- 1
      lista_caminho <- retorna_lista_caminho(no, df_arvore_reduzida)[-length(retorna_lista_caminho(no, df_arvore_reduzida))]
      lista_caminho = unlist(lista_caminho)
      for (elemento in lista_caminho) {
        prob_elemento <- df_arvore_reduzida[df_arvore_reduzida$NO == elemento, "PROB"][1]
        prob <- prob * prob_elemento
      }
      prob_red <- append(prob_red, prob)
    }
    prob_red <- unlist(prob_red)
    numeroNOS = length(unique(df_red_est$NO))
    #usinas <- c(17, 275)
    for (usi in usinas){
      eixoX <- c(eixoX, usi)
      lista_original <- list()
      for (no in unique(df_orig_est$NO)) {
        vazao <- df_vazoes[df_vazoes$NOME_UHE == usi & df_vazoes$NO == no, "VAZAO"][1]
        lista_original <- append(lista_original, vazao)
      }
      lista_original <- unlist(lista_original)
      
      lista_red <- list()
      for (no in unique(df_red_est$NO)) {
        vazao <- df_vazoes[df_vazoes$NOME_UHE == usi & df_vazoes$NO == no, "VAZAO"][1]
        lista_red <- append(lista_red, vazao)
      }
      lista_red <- unlist(lista_red)
      

      
      prob_original <- prob_original / sum(prob_original)
      prob_red <- prob_red / sum(prob_red)
      
      #MEDIA COM PESOS
      weighted_mean_Orig <- weighted.mean(lista_original, prob_original)
      weighted_mean_Red <- weighted.mean(lista_red, prob_red)
      
      #DESVIO PADRAO COM PESOS
      weighted_sd_Orig <- sqrt(w.var(lista_original, prob_original))
      weighted_sd_Red <- sqrt(w.var(lista_red, prob_red))
      
      #SKEWNESS
      Wskew_Orig <- w.skewness(lista_original, prob_original)
      Wskew_Red <- w.skewness(lista_red, prob_red)

      #KURTOSIS
      WKurto_Orig <- w.kurtosis(lista_original, prob_original)
      WKurto_Red <- w.kurtosis(lista_red, prob_red)

      #DISTANCIA WASSERSTEIN
      wasserstein_dist <- wasserstein1d(lista_original, lista_red, p = 1, wa = prob_original, wb = prob_red)
      
      #INTERVALO DE CONFIANçA DA MEDIA T 95
      # t-critical value for 95% CI with (n-1) degrees of freedom
      t_value <- qt(0.975, df = length(lista_original)-1)
      t_value <- qnorm(0.975)
      error_margin <- t_value * (weighted_sd_Orig / sqrt(length(lista_original)))
      limSup = weighted_mean_Orig+error_margin
      limInf = weighted_mean_Orig-error_margin
      
      #INTERVALO DE CONFIANCA DO DESVIO PADRAO 95
      alpha <- 0.05  # For 95% confidence interval
      chi2_lower <- qchisq(1 - alpha / 2, df = length(lista_original) - 1)  # Upper chi-square value
      chi2_upper <- qchisq(alpha / 2, df = length(lista_original) - 1)  # Lower chi-square value
      sd_lower <- sqrt((length(lista_original) - 1) * weighted_sd_Orig^2 / chi2_lower)
      sd_upper <- sqrt((length(lista_original) - 1) * weighted_sd_Orig^2 / chi2_upper)
      
      
      
      #TESTE KS
      ks_stat <- ks_test(lista_original, lista_red, prob_original, prob_red, thresh = 0.01)
      ks_distance <- ks_stat$statistic
      p_value <- ks_stat$p_value
      
      #TESTE F
      f_test_result <- var.test(lista_original, lista_red)
      
      #TESTE T
      t_testWeightened <- wtd.t.test(lista_original, lista_red, weight = prob_original, weighty = prob_red)
      
      #WELCH
      if (sd(lista_original) == 0 || sd(lista_red) == 0) {
        cat("Teste não aplicado Dataset Constante orig: ", sd(lista_original), " red: ", sd(lista_red), "\n")
      } else {
        # Apply the t-test if data is not constant
        t_test_result <- t.test(lista_original, lista_red, var.equal = FALSE)
      }
      
      #WILCOXON RANK SUM TEST
      wilcoxon <- wilcox.test(lista_original, lista_red, exact = FALSE)  # exact = FALSE for large samples

      new_row <- data.frame(TIPO = tipo, CASO = caso, EST = est, NOS = numeroNOS, POSTO = usi, 
                                   mediaOrig = weighted_mean_Orig, mediaRed = weighted_mean_Red,
                                   limT = t_value, error_media = error_margin,
                                   mediaLimInf = limInf, mediaLimSup = limSup,
                                   stdOrig = weighted_sd_Orig, stdRed = weighted_sd_Red,
                                   stdLimInf = sd_lower, stdLimSup = sd_upper,
                                   chi2_lower = chi2_lower, chi2_upper = chi2_upper,
                                   assimOrig = Wskew_Orig, assimRed = Wskew_Red,
                                   kurtOrig = WKurto_Orig, kurtRed = WKurto_Red,
                                   DWasserstein = wasserstein_dist,
                                   KS_Test = ks_stat$statistic, KS_p_valor = ks_stat$p.value,
                                   T_Test = as.numeric(t_testWeightened$coefficients["t.value"]), T_p_valor = as.numeric(t_testWeightened$coefficients["p.value"]),
                                   Welch_Test = as.numeric(welch$statistic), Welch_p_valor = welch$p.value, 
                                   F_Test = as.numeric(f_test_result$statistic), F_p_valor = f_test_result$p.value,
                                   Wilcoxon_Test = as.numeric(wilcoxon$statistic), Wilcoxon_p_valor = wilcoxon$p.value)
      
      df <- rbind(df, new_row)
      

      
      cat("caso: ", caso, " est: ", est, " nos: ", numeroNOS, " usi: ", usi, "\n")
    }
    
  }
}
df <- df %>% mutate(across(where(is.numeric), ~ round(., 3)))
write.csv2(df, "C:/Users/testa/Documents/mestrado/ComparacaoArvoresBackwardReduction/ExportaRelatorios/estatisticasArvores.csv", row.names = TRUE)

