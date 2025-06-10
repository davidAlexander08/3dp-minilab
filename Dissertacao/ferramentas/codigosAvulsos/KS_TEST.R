library(Ecume)
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

# Function to calculate kurtosis


trace_media <- list()
trace_std <- list()
trace_skew <- list()
trace_kurtosis <- list()




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
# Placeholder for the final list
lista_df_final <- list()
estagios <- c(4,3,2)

contador <- 1
for (caso in casos) {
  df_arvore_reduzida <- read.csv(paste0("C:/Users/testa/Documents/mestrado/ComparacaoArvoresBackwardReduction/",tipo,"/", caso, "/df_arvore_reduzida.csv"))
  for (est in estagios) {
    ## DEFINICAO DE LISTAS PARA PLOTAR
    
    
    ##FIM DA DEFINICAO

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
    
    usinas <- c(1, 17)
    
    eixoX <- c() #Lista Usinas
    mediaY <- c()
    mediaOrig <- c()
    mediaSup <- c()
    mediaInf <-c()
    
    stdaY <- c()
    stdOrig <- c()
    stdSup <- c()
    stdInf <-c()
    
    skewnwessY <- c()
    skewnwessOrig <- c()
    skewnwessSup <- c()
    skewnwessInf <-c()
    
    kurtosisY <- c()
    kurtosisOrig <- c()
    kurtosisSup <- c()
    kurtosisInf <-c()
    
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
      #print(lista_red)
      
      ks_stat <- ks_test(lista_original, lista_red, prob_original, prob_red, thresh = 0.01)
      ks_distance <- ks_stat$statistic
      p_value <- ks_stat$p_value
      #cat(sprintf("Pesos caso = %s , est = %d, usi = %d, dist = %.3f, p-value = %.4f\n", caso, est, usi, ks_stat$statistic, ks_stat$p.value))
      
      #ks_stat <- ks_test(lista_original, lista_red, thresh = 0.01)
      #ks_distance <- ks_stat$statistic
      #p_value <- ks_stat$p_value
      #cat(sprintf("Simpl caso = %s , est = %d, usi = %d, dist = %.3f, p-value = %.4f\n", caso, est, usi, ks_stat$statistic, ks_stat$p.value))

      # Create a contingency table
      table1 <- table(factor(lista_original, levels = unique(c(lista_original, lista_red))))
      table2 <- table(factor(lista_red, levels = unique(c(lista_original, lista_red))))
      contingency_table <- rbind(table1, table2)
      
      chi_square_result <- chisq.test(contingency_table)
      #print(chi_square_result)
      #cat(sprintf("Xi caso = %s , est = %d, usi = %d, squared = %.3f, p-value = %.4f\n", caso, est, usi, chi_square_result$statistic, chi_square_result$p.value))
      #cat(sprintf("caso = %s , est = %d, usi = %d, Dks = %.3f, p-value = %.4f, , Xi = %.3f, p-value = %.4f\n", caso, est, usi, ks_stat$statistic, ks_stat$p.value, chi_square_result$statistic, chi_square_result$p.value))
      
      f_test_result <- var.test(lista_original, lista_red)
      welch_test_result <- t.test(lista_original, lista_red, var.equal = FALSE)
      t_test_result <- t.test(lista_original, lista_red, var.equal = TRUE)
      mann_whitney_result <- wilcox.test(lista_original, lista_red, exact = TRUE)  # exact = FALSE for large samples
      levene_result <- leveneTest(c(lista_original, lista_red) ~ factor(rep(1:2, c(length(lista_original), length(lista_red)))))
      
      weighted_mean_Orig <- weighted.mean(lista_original, prob_original)
      weighted_mean_Red <- weighted.mean(lista_red, prob_red)
      
      mean_Orig <- mean(lista_original)
      mean_Red <- mean(lista_red)
      
      
      #print(lista_original)
      #print(prob_original)
      prob_original <- prob_original / sum(prob_original)
      prob_red <- prob_red / sum(prob_red)
      #weighted_sd_Orig <- sqrt(wtd.var(lista_original, prob_original, normwt = TRUE))
      #weighted_sd_Red <- sqrt(wtd.var(lista_red, prob_red, normwt = TRUE))
      weighted_sd_Orig <- sqrt(w.var(lista_original, prob_original))
      weighted_sd_Red <- sqrt(w.var(lista_red, prob_red))
      std_Orig <- sd(lista_original)
      std_Red  <- sd(lista_red)
      
      Wskew_Orig <- w.skewness(lista_original, prob_original)
      Wskew_Red <- w.skewness(lista_red, prob_red)
      skew_Orig <- skewness(lista_original)
      skew_Red <- skewness(lista_red)
      
      WKurto_Orig <- w.kurtosis(lista_original, prob_original)
      WKurto_Red <- w.kurtosis(lista_red, prob_red)
      Kurto_Orig <- kurtosis(lista_original)
      Kurto_Red <- kurtosis(lista_red)
    
      t_testWeightened <- wtd.t.test(lista_original, lista_red, weight = prob_original, weighty = prob_red)
      
      P_hist <- cbind(lista_original, prob_original)
      Q_hist <- cbind(lista_red, prob_red)
      wasserstein_dist <- wasserstein1d(lista_original, lista_red, p = 1, wa = prob_original, wb = prob_red)
      #cat("Wasserstein Distance: ", wasserstein_dist, "\n")
      
      
      # Calculate expected frequencies (weighted by P_probs)
      expected_freq <- sum(lista_original * prob_original)
      observed_freq <- sum(lista_red * prob_red)
      
      #weighted_ks_test <- function(x, y, wx, wy) {
      #  combined <- sort(unique(c(x, y)))
      #  cdf_x <- sapply(combined, function(v) sum(wx[x <= v]) / sum(wx))
      #  cdf_y <- sapply(combined, function(v) sum(wy[y <= v]) / sum(wy))
      #  ks_stat <- max(abs(cdf_x - cdf_y))
      #  n <- sum(wx)
      #  m <- sum(wy)
      #  p_value <- exp(-2 * (ks_stat^2) * (n * m) / (n + m))
      #  return(list(ks_stat = ks_stat, p_value = p_value))
      #}
      #result <- weighted_ks_test(lista_original, lista_red, prob_original, prob_red)
      #print(paste("Weighted KS test: KS statistic =", result$ks_stat, ", p-value =", result$p_value))
      
      #var_P <- weighted_variance(lista_original, prob_original)
      #var_Q <- weighted_variance(lista_red, prob_red)
      #F_stat <- var_P / var_Q
      #df1 <- length(lista_original) - 1
      #df2 <- length(lista_red) - 1
      #p_value <- 2 * min(pf(F_stat, df1, df2), 1 - pf(F_stat, df1, df2))
      #print(paste("Weighted F-test: F-statistic =", F_stat, ", p-value =", p_value))

      # Number of bootstrap samples
      n_bootstrap <- 1000
      bootstrap_diffs <- numeric(n_bootstrap)
      bootstrap_confiance_mean <- numeric(n_bootstrap)
      bootstrap_confiance_std <- numeric(n_bootstrap)
      bootstrap_confiance_skew <- numeric(n_bootstrap)
      bootstrap_confiance_kurtosis <- numeric(n_bootstrap)
      
      for (i in 1:n_bootstrap) {
        sampled_data  <- sample(lista_original, size = length(lista_original), replace = TRUE, prob = prob_original)
        bootstrap_confiance_mean[i] <- mean(sampled_data)
        bootstrap_confiance_std[i] <- sd(sampled_data)
        bootstrap_confiance_skew[i] <- skewness(sampled_data)
        bootstrap_confiance_kurtosis[i] <- kurtosis(sampled_data)
        
        #sampled_data_2 <- sample(lista_red, size = length(lista_original), replace = TRUE, prob = prob_red)
        #skewness2 <- skewness(sampled_data_2)  
        #bootstrap_diffs[i] <- skewness(sampled_data) - skewness2
      }
      #bootstrap_confiance_skew <- bootstrap_confiance_skew[!is.na(bootstrap_confiance_skew)]
      
      mean_ci_data <- quantile(bootstrap_confiance_mean, probs = c(0.025, 0.975), na.rm = TRUE)
      cat("P_realizations mean 95% CI: [", mean_ci_data[1], ", ", mean_ci_data[2], "]\n")
      std_ci_data <- quantile(bootstrap_confiance_std, probs = c(0.025, 0.975), na.rm = TRUE)
      cat("P_realizations std 95% CI: [", std_ci_data[1], ", ", std_ci_data[2], "]\n")
      skew_ci_data <- quantile(bootstrap_confiance_skew, probs = c(0.025, 0.975), na.rm = TRUE)
      cat("P_realizations skewness 95% CI: [", skew_ci_data[1], ", ", skew_ci_data[2], "]\n")
      kurt_ci_data <- quantile(bootstrap_confiance_kurtosis, probs = c(0.025, 0.975), na.rm = TRUE)
      cat("P_realizations kurtosis 95% CI: [", kurt_ci_data[1], ", ", kurt_ci_data[2], "]\n")
      #observed_diff <- w.skewness(lista_original, prob_original) - w.skewness(lista_red, prob_red)
      #p_value <- mean(abs(bootstrap_diffs) >= abs(observed_diff))
      #print(paste("Observed Difference in Skewness:", observed_diff))
      #print(paste("Bootstrap p-value:", p_value))
    
      mediaOrig <- c(mediaOrig, weighted_mean_Orig/unname(mean_ci_data[2]))
      mediaY    <- c(mediaY, weighted_mean_Red/unname(mean_ci_data[2]))
      mediaSup  <- c(mediaSup, unname(mean_ci_data[2])/unname(mean_ci_data[2]))
      mediaInf  <- c(mediaInf, unname(mean_ci_data[1])/unname(mean_ci_data[2]))
      
      stdaY     <- c(stdaY   , weighted_sd_Orig/unname(std_ci_data[2]))
      stdOrig   <- c(stdOrig , weighted_sd_Red/unname(std_ci_data[2]))
      stdSup    <- c(stdSup  , unname(std_ci_data[2])/unname(std_ci_data[2]))
      stdInf    <- c(stdInf  , unname(std_ci_data[1])/unname(std_ci_data[2]))
      
      skewnwessY    <- c(skewnwessY    , Wskew_Orig             )#/unname(skew_ci_data[2]))
      skewnwessOrig <- c(skewnwessOrig , Wskew_Red              )#/unname(skew_ci_data[2]))
      skewnwessSup  <- c(skewnwessSup  , unname(skew_ci_data[2]))#/unname(skew_ci_data[2]))
      skewnwessInf  <- c(skewnwessInf  , unname(skew_ci_data[1]))#/unname(skew_ci_data[2]))
      kurtosisY     <- c(kurtosisY    , WKurto_Orig             )#/unname(kurt_ci_data[2]))
      kurtosisOrig  <- c(kurtosisOrig , WKurto_Red              )#/unname(kurt_ci_data[2]))
      kurtosisSup   <- c(kurtosisSup  , unname(kurt_ci_data[2]) )#/unname(kurt_ci_data[2]))
      kurtosisInf   <- c(kurtosisInf  , unname(kurt_ci_data[1]) )#/unname(kurt_ci_data[2]))
      
      
      
      cat(sprintf("caso = %s , est = %d, usi = %d, 
                  Omean = %.3f,   Owmean = %.3f, Ostd = %.3f,   Owstd = %.3f, SkwO = %.3f,   WSkwO = %.3f,  KurtoO = %.3f,   WKurtoO = %.3f, WasserStein = %.3f, 
                  Rmean = %.3f,   Rwmean = %.3f, Rstd = %.3f,   Rwstd = %.3f, SkwR = %.3f,   WSkwR = %.3f,  KurtoR = %.3f,   WKurtoR = %.3f,
                  Dks = %.3f    , Xi = %.4f     , F = %.4f      ,  L = %.4f
                  p-value = %.4f, p-value = %.4f, p-value = %.4f, p-value = %.4f 
                  WT = %.3f  , T = %.3f  , W = %.4f  ,  M = %.4f  , 
                  p-value = %.4f , p-value = %.4f, p-value = %.4f, p-value = %.4f, \n",
                  caso, est, usi, 
                  mean_Orig, weighted_mean_Orig, std_Orig, weighted_sd_Orig, skew_Orig,Wskew_Orig, Kurto_Orig, WKurto_Orig, wasserstein_dist, 
                  mean_Red, weighted_mean_Red, std_Red, weighted_sd_Red, skew_Red, Wskew_Red, Kurto_Red, WKurto_Red,
                  ks_stat$statistic, chi_square_result$statistic, f_test_result$statistic, levene_result$`F value`[1],
                  ks_stat$p.value  , chi_square_result$p.value  , f_test_result$p.value  ,  levene_result$`Pr(>F)`[1],
                  t_testWeightened$coefficients["t.value"], t_test_result$statistic, welch_test_result$statistic, mann_whitney_result$statistic,
                  t_testWeightened$coefficients["p.value"],   t_test_result$p.value  ,  welch_test_result$p.value  ,   mann_whitney_result$p.value))
    }
    
    print(mediaOrig)
    print(mediaY)
    print(mediaSup)
    print(mediaInf)
    eixoX <- factor(eixoX, levels = eixoX)  # Explicitly define the order
    print(eixoX)
    # Create the plot and store it in the list
    trace_media[[contador]] <- ggplot(data.frame(
      eixoX = eixoX, 
      mediaY = mediaY,
      mediaOrig = mediaOrig,
      mediaSup = mediaSup, 
      mediaInf = mediaInf
    )) +
      geom_line(aes(x = eixoX, y = mediaOrig, group = 1), color = 'blue', size = 1) + 
      geom_line(aes(x = eixoX, y = mediaSup, group = 1), color = 'black', size = 1, linetype = "dashed") + 
      geom_line(aes(x = eixoX, y = mediaInf, group = 1), color = 'black', size = 1, linetype = "dashed") + 
      geom_line(aes(x = eixoX, y = mediaY, group = 1), color = 'red', size = 1) + 
      labs(title = paste("Caso: ", caso, " Estágio: ", est), x = "Postos", y = "m3/s") +
      theme(plot.title = element_text(size = 17))  # Reduced font size
    
    trace_std[[contador]] <- ggplot(data.frame(
      eixoX = eixoX, 
      stdaY = stdaY,
      stdOrig = stdOrig,
      stdSup = stdSup, 
      stdInf = stdInf
    )) +
      geom_line(aes(x = eixoX, y = stdOrig, group = 1), color = 'blue', size = 1) + 
      geom_line(aes(x = eixoX, y = stdSup, group = 1), color = 'black', size = 1, linetype = "dashed") + 
      geom_line(aes(x = eixoX, y = stdInf, group = 1), color = 'black', size = 1, linetype = "dashed") + 
      geom_line(aes(x = eixoX, y = stdaY, group = 1), color = 'red', size = 1) + 
      labs(title = paste("Caso: ", caso, " Estágio: ", est), x = "Postos", y = "m3/s") +
      theme(plot.title = element_text(size = 17))  # Reduced font size
    #geom_point
    
    trace_skew[[contador]] <- ggplot(data.frame(
      eixoX = eixoX, 
      skewnwessY = skewnwessY,
      skewnwessOrig = skewnwessOrig,
      skewnwessSup = skewnwessSup, 
      skewnwessInf = skewnwessInf
    )) +
      geom_line(aes(x = eixoX, y = skewnwessOrig, group = 1), color = 'blue', size = 1) + 
      geom_line(aes(x = eixoX, y = skewnwessSup, group = 1), color = 'black', size = 1, linetype = "dashed") + 
      geom_line(aes(x = eixoX, y = skewnwessInf, group = 1), color = 'black', size = 1, linetype = "dashed") + 
      geom_line(aes(x = eixoX, y = skewnwessY, group = 1), color = 'red', size = 1) + 
      labs(title = paste("Caso: ", caso, " Estágio: ", est), x = "Postos", y = "m3/s") +
      theme(plot.title = element_text(size = 17))  # Reduced font size
    
    trace_kurtosis[[contador]] <- ggplot(data.frame(
      eixoX = eixoX, 
      kurtosisY = kurtosisY,
      kurtosisOrig = kurtosisOrig,
      kurtosisSup = kurtosisSup, 
      kurtosisInf = kurtosisInf
    )) +
      geom_line(aes(x = eixoX, y = kurtosisOrig, group = 1), color = 'blue', size = 1) + 
      geom_line(aes(x = eixoX, y = kurtosisSup, group = 1), color = 'black', size = 1, linetype = "dashed") + 
      geom_line(aes(x = eixoX, y = kurtosisInf, group = 1), color = 'black', size = 1, linetype = "dashed") + 
      geom_line(aes(x = eixoX, y = kurtosisY, group = 1), color = 'red', size = 1) + 
      labs(title = paste("Caso: ", caso, " Estágio: ", est), x = "Postos", y = "m3/s") +
      theme(plot.title = element_text(size = 17))  # Reduced font size
    
    
    contador <- contador + 1
  }
}
path <- file.path("C:/Users/testa/Documents/mestrado/ComparacaoArvoresBackwardReduction/")
plot <- do.call(grid.arrange, c(trace_media, nrow = 6, ncol = 3, top = "Comparação Média Árvore de Cenários"))
png_path <- file.path(path, "media.png")
ggsave(png_path, plot, width = 30, height = 15)  # Adjust dimensions

plot <- do.call(grid.arrange, c(trace_std, nrow = 6, ncol = 3, top = "Comparação Desvio Árvore de Cenários"))
png_path <- file.path(path, "std.png")
ggsave(png_path, plot, width = 30, height = 15)  # Adjust dimensions

plot <- do.call(grid.arrange, c(trace_skew, nrow = 6, ncol = 3, top = "Comparação Assimetria Árvore de Cenários"))
png_path <- file.path(path, "skw.png")
ggsave(png_path, plot, width = 30, height = 15)  # Adjust dimensions

plot <- do.call(grid.arrange, c(trace_kurtosis, nrow = 6, ncol = 3, top = "Comparação Kurtosis Árvore de Cenários"))
png_path <- file.path(path, "kurt.png")
ggsave(png_path, plot, width = 30, height = 15)  # Adjust dimensions




pdf_path <- file.path(path, "my_plot.pdf")
ggsave(pdf_path, grid_plot, width = 30, height = 15)  # Adjust dimensions
cat("PNG file saved at:", png_path, "\n")
cat("PDF file saved at:", pdf_path, "\n")