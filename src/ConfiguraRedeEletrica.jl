include("DefineIlhasEletricas.jl")
using JSON
using CSV
using DataFrames
#using Graphs
using LightGraphs
using SparseArrays
using DataStructures
using LinearAlgebra
using IterativeSolvers
using JuMP, GLPK, Plots, Measures, Plots, SparseArrays

#lista_ilhas_eletricas


function calculaParametrosDaIlha(ilha,est)
    ## CALCULANDO A MATRIZ SUSCEPTANCIA
    barras_semSlack = []
    mapaSusceptanciaDiagonalPrincipal = OrderedDict()
    for barra in ilha.barrasAtivas[est]
        mapaSusceptanciaDiagonalPrincipal[barra.codigo] = 0
        if barra.codigo != ilha.slack.codigo
            push!(barras_semSlack,barra)
        end
    end

    global indice = 1
    mapaPosicaoBarras = OrderedDict()
    for barra in barras_semSlack
        mapaPosicaoBarras[barra.codigo] = indice
        indice = indice + 1
    end

    matrizSusceptancia = spzeros(length(ilha.barrasAtivas[est])-1, length(ilha.barrasAtivas[est])-1)

    matrizIncidencia = spzeros(length(ilha.linhasAtivas[est]), length(ilha.barrasAtivas[est])-1)

    matrizDiagonalDeSusceptancia = spzeros(length(ilha.linhasAtivas[est]), length(ilha.linhasAtivas[est]))
    contador = 1
    for linha in ilha.linhasAtivas[est]
        if linha.de.codigo != ilha.slack.codigo
            matrizIncidencia[contador, mapaPosicaoBarras[linha.de.codigo]] = 1
        end
        if linha.para.codigo != ilha.slack.codigo
            matrizIncidencia[contador, mapaPosicaoBarras[linha.para.codigo]] = -1
        end

        matrizDiagonalDeSusceptancia[contador, contador] = matrizDiagonalDeSusceptancia[contador, contador]  + 1/linha.X

        contador = contador + 1


        codigo_de = linha.de.codigo
        codigo_para = linha.para.codigo
        susceptancia = 1/linha.X
        if codigo_de != ilha.slack.codigo && codigo_para != ilha.slack.codigo
            indiceDE = mapaPosicaoBarras[codigo_de]
            indicePARA = mapaPosicaoBarras[codigo_para]
            matrizSusceptancia[indiceDE, indicePARA] += -susceptancia
            matrizSusceptancia[indicePARA, indiceDE] += -susceptancia
        end
        mapaSusceptanciaDiagonalPrincipal[codigo_de] += susceptancia
        mapaSusceptanciaDiagonalPrincipal[codigo_para] += susceptancia
    
    end

    for barra in ilha.barras
        codigo = barra.codigo
        if codigo != ilha.slack.codigo
            indice = mapaPosicaoBarras[codigo]
            matrizSusceptancia[indice,indice] = mapaSusceptanciaDiagonalPrincipal[codigo]
        end
    end

    matrizB = matrizDiagonalDeSusceptancia*matrizIncidencia
    #println("matrizB: ", Matrix(matrizB))

    ilha.matrizSusceptancia[est] = matrizSusceptancia
    ilha.matrizIncidencia[est] = matrizIncidencia


    #matrizSensibilidade = spzeros(length(ilha.linhas), length(ilha.barras)-1)
    contador = 1
    for linha in ilha.linhasAtivas[est]
        if det(matrizSusceptancia) != 0
            linhaMatrizSensibilidade = matrizSusceptancia \ Array(matrizB[contador,:])
            #println("Determinante Matriz Suscep: ", det(matrizSusceptancia))
        else
            linhaMatrizSensibilidade = pinv(Matrix(matrizSusceptancia)) * Array(matrizB[contador, :])
            #linhaMatrizSensibilidade = lsqr(matrizSusceptancia, Array(matrizB[contador, :]))
            #println("Determinante Matriz Suscep: ", det(matrizSusceptancia))
        end

        linha.linhaMatrizSensibilidade[est] = round.(linhaMatrizSensibilidade, digits=4)
        contador = contador + 1
        
    end

    vetorPotenciaCarga = []
    for barra in ilha.barrasAtivas[est]
        if barra.codigo != ilha.slack.codigo
            push!(vetorPotenciaCarga,  barra.carga[est]) ## PEGANDO O PRIMEIRO VALOR DA CARGA, MAS NA VERDADE É TEMPORAL
        end
    end

    #println("INverso: ", inv(Matrix(matrizSusceptancia)))
    for linha in ilha.linhasAtivas[est]
        RHS = linha.Capacidade[est] +transpose(linha.linhaMatrizSensibilidade[est])*vetorPotenciaCarga
        #println("RHS: ",  RHS, " linhaMatrizSensibilidade: ", Array(linhaMatrizSensibilidade))
        linha.RHS[est] = round(RHS, digits=4)
        linha.coeficienteDemanda[est] = round(transpose(linha.linhaMatrizSensibilidade[est])*vetorPotenciaCarga, digits=4)
    end
end

for ilha in lista_ilhas_eletricas    
    for est in 1:caso.n_est
        calculaParametrosDaIlha(ilha,est)
    end
end







function realizaReducaoDeRedePeloMetodoDoValorMinimoDeCapacidadeDasLinhas(ilha, est)
    lista_linhas_ativas = []
    linha_linhas_nao_ativas = []
    lista_barras_existentes = []
    lista_barras_invativas = []
    lista_barras_ativas = []
    for linha in ilha.linhasAtivas[est]
        #if mapa_linha_valorMinimoCapacidadeLinha[(linha.de.codigo, linha.para.codigo, est)] >= 0
        if linha.valorMinimoCapacidade[est] >= 0
            push!(lista_linhas_ativas, linha)
            println("LINHA ATIVA: BARRA DE $(linha.de.codigo) BARRA PARA: $(linha.para.codigo)")
            push!(lista_barras_existentes,linha.de.codigo)
            push!(lista_barras_existentes,linha.para.codigo)
        else
            push!(linha_linhas_nao_ativas, linha)
            println("LINHA NAO ATIVA: BARRA DE $(linha.de.codigo) BARRA PARA: $(linha.para.codigo)")
        end
    end
    for barra in ilha.barrasAtivas[est]
        if barra.codigo in lista_barras_existentes
            println("BARRA ATIVA: ", barra.codigo)
            push!(lista_barras_ativas, barra)
        else
            println("BARRA INATIVA: ", barra.codigo)
            push!(lista_barras_invativas, barra)
        end
    end
    ilha.linhasAtivas[est] = lista_linhas_ativas
    ilha.linhasNaoAtivas[est] = linha_linhas_nao_ativas
    ilha.barrasAtivas[est] = lista_barras_ativas
    ilha.barrasNaoAtivas[est] = lista_barras_invativas
end