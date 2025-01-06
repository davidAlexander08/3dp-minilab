using DataFrames
using CSV
using Statistics  # Import the Statistics module for cor()
using LinearAlgebra
using GLM





using DataFrames

# Provided observed data (x values)
lista = [0.551490969, 0.954627642, -0.641793584, 0.567616436, -1.431941463]

# Provided predicted data
predicted = [0.102663752, 0.013920509, -0.038281399, -0.064382353, -0.013920509]

# Create a DataFrame with the observed and predicted values
data = DataFrame(x = lista, predicted = predicted)

# Calculate residuals (difference between observed values and predicted values)
#residuals = data.predicted .- lista  # Residuals = predicted - observed
residuals = lista .- data.predicted

# Calculate the variance of residuals (σ^2)
σ² = var(residuals)

# Calculate the log-likelihood (assuming Gaussian distribution)
n = length(residuals)
log_likelihood = -n/2 * log(2 * π * σ²) - sum(residuals.^2) / (2 * σ²)
println("SOMA RESIDUOS: ", sum(residuals.^2))
println("log_likelihood: ", log_likelihood)
println("n: ", n )
println("σ²: ", σ²)
# Number of parameters (for a simple linear model, we have 2 parameters: intercept and slope)
k = 2

# Calculate the AIC
AIC = 2 * k - 2 * log_likelihood

println("AIC: ", AIC)


exit(1)



arq_vaz = "vazao_teste_red.txt"
@info "Lendo arquivo de horas $(arq_vaz)"
df_read = CSV.read(arq_vaz, DataFrame)
df_vazoes = select(df_read, Not([1, 2])) 
println(df_vazoes)

##AUTOCORRELACAO
ordem_max = 2
df_FAC = DataFrame(zeros(12, ordem_max), :auto)
for mes in range(1,12)
    vetor_correl = []
    for ord in range(1,ordem_max)
        mes_past = 0
        if mes > ord
            mes_past = mes - ord
            correlation = cor(df_vazoes[:,mes_past][2:end], df_vazoes[:,mes][2:end])
        else
            mes_past = mes - ord + 12
            correlation = cor(df_vazoes[:,mes_past][1:end-1], df_vazoes[:,mes][2:end])
        end
        push!(vetor_correl, correlation)
        #correlation = cor(df_vazoes.DEZ[1:end-1], df_vazoes.JAN[2:end])
        df_FAC[mes,ord] = correlation
        println("ORD: ", ord, " Mes: ", mes, " mes_past: ", mes_past, " correl: ", correlation)
    end
    println("Mes: ", mes, " vetor_correl: ", vetor_correl)
end
println(df_FAC)

##CONSTROI YULE-WALKER
for mes in range(1,12)
    var2 =0
    matrix = zeros(ordem_max, ordem_max)
    B = zeros(ordem_max, 1)
    # Set the diagonal elements to 1
    for i in 1:min(size(matrix)...)
        matrix[i, i] = 1
    end

    for lin in range(1, ordem_max)
        for col in range(1, ordem_max-lin)
            println("lin: ", lin, " col: ", col)
            var2 = mes - lin;
            if var2 <= 0
                var2 = mes - lin + 12;
            end
                matrix[lin,col+lin] = df_FAC[var2, col]
                matrix[lin+col,lin] = df_FAC[var2, col]
        end
    end

    for col in range(1,ordem_max)
        B[col,1] = df_FAC[mes, col]
    end

    println(matrix)
    println(B)

    coeficientes = matrix \ B
    println("COEF: ", coeficientes)
end

