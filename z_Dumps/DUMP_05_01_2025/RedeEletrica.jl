include("LeituraEntrada.jl")
using JSON
using CSV
using DataFrames
#using Graphs
using LightGraphs
using SparseArrays
using DataStructures
using LinearAlgebra
using IterativeSolvers


dicionario_indiceVertice_Barra = OrderedDict()
dicionario_Barra_indiceVertice = OrderedDict()
mapaLinhaFluxo = OrderedDict()
g = SimpleGraph()

for (contador_graph,barra) in enumerate(lista_barras)
    add_vertex!(g)
    dicionario_indiceVertice_Barra[contador_graph] = barra
    dicionario_Barra_indiceVertice[barra] = contador_graph
#    contador_graph = contador_graph +  1
end

for linha in lista_linhas
    if linha.indice == 1 
        #add_edge!(g, linha.de.codigo, linha.para.codigo)
        add_edge!(g, dicionario_Barra_indiceVertice[linha.de], dicionario_Barra_indiceVertice[linha.para])
    end
end

edges_list = collect(edges(g))  # Collect edges into a list


function encontra_adjacentes_acrescenta_lista(lista_barras_da_ilha, grafoDaRede, indice_barra_slack)
    # Iterate over adjacent vertices
    auxiliar = []
    for vd in neighbors(grafoDaRede, indice_barra_slack)
        push!(lista_barras_da_ilha, dicionario_indiceVertice_Barra[vd])  # Add to vetorCodigoBarrasDaIlha
        push!(auxiliar, vd)  # Add to auxiliar
    end

    for idVertice in auxiliar
        edges_list = collect(edges(g))  # Collect edges into a list
        vertices_list = collect(vertices(g))
        rem_edge!(grafoDaRede, indice_barra_slack, idVertice)
        edges_list = collect(edges(g))  # Collect edges into a list
        vertices_list = collect(vertices(g))
    end

    for idVertice in auxiliar
        encontra_adjacentes_acrescenta_lista(lista_barras_da_ilha,grafoDaRede, idVertice)
    end
end

@info "Definindo as ilhas elétricas da rede"

function calculaIlhasEletricas(lista_barras_slack)
    lista_ilhas = []
    indiceIlhaEletrica = 0
    
    for slack in lista_barras_slack
        
        indiceIlhaEletrica += 1
        lista_barras_da_ilha = []
        lista_linhas_da_ilha = []
        lista_linhas_nao_ativas = []
        push!(lista_barras_da_ilha, slack)
        encontra_adjacentes_acrescenta_lista(lista_barras_da_ilha, g, dicionario_Barra_indiceVertice[slack])
        #println(lista_barras_da_ilha)

        lista_barras_da_ilha = unique(lista_barras_da_ilha)
        sort!(lista_barras_da_ilha, by = b -> b.codigo)

        for barra in lista_barras_da_ilha
            mapaCodigoBarra[barra.codigo] = barra
            if haskey(dicionario_barraDE_linha, barra.codigo)
                for linha_barra in dicionario_barraDE_linha[barra.codigo]
                    push!(lista_linhas_da_ilha, linha_barra)
                end
            end
        end


        #ilha = IlhaConfig(indiceIlhaEletrica , slack , lista_barras_da_ilha, lista_linhas_da_ilha, matrizSusceptancia, matrizDiagonalDeSusceptancia, matrizIncidencia, fluxo_linhas, [], [], mapaCodigoBarra)
        ilha = IlhaConfig()
        ilha.codigo = indiceIlhaEletrica
        ilha.slack = slack
        ilha.barras =lista_barras_da_ilha
        ilha.linhas = lista_linhas_da_ilha
        push!(lista_ilhas, ilha)
    end
    return lista_ilhas
end



function calculaParametrosDaIlha(ilha,est)
    ## CALCULANDO A MATRIZ SUSCEPTANCIA
    barras_semSlack = []
    mapaSusceptanciaDiagonalPrincipal = OrderedDict()
    for barra in ilha.barras
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

    matrizSusceptancia = spzeros(length(ilha.barras)-1, length(ilha.barras)-1)

    matrizIncidencia = spzeros(length(ilha.linhas), length(ilha.barras)-1)

    matrizDiagonalDeSusceptancia = spzeros(length(ilha.linhas), length(ilha.linhas))
    contador = 1
    for linha in ilha.linhas
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

    ilha.matrizSusceptancia = matrizSusceptancia
    ilha.mapaSusceptanciaDiagonalPrincipal = mapaSusceptanciaDiagonalPrincipal
    ilha.matrizIncidencia = matrizIncidencia


    #matrizSensibilidade = spzeros(length(ilha.linhas), length(ilha.barras)-1)
    contador = 1
    for linha in ilha.linhas
        if det(matrizSusceptancia) != 0
            linhaMatrizSensibilidade = matrizSusceptancia \ Array(matrizB[contador,:])
            #println("Determinante Matriz Suscep: ", det(matrizSusceptancia))
        else
            linhaMatrizSensibilidade = pinv(Matrix(matrizSusceptancia)) * Array(matrizB[contador, :])
            #linhaMatrizSensibilidade = lsqr(matrizSusceptancia, Array(matrizB[contador, :]))
            #println("Determinante Matriz Suscep: ", det(matrizSusceptancia))
        end
        linha.linhaMatrizSensibilidade = round.(linhaMatrizSensibilidade, digits=4)
        contador = contador + 1
    end

    vetorPotenciaCarga = []
    for barra in ilha.barras
        if barra.codigo != ilha.slack.codigo
            push!(vetorPotenciaCarga,  barra.carga[est]) ## PEGANDO O PRIMEIRO VALOR DA CARGA, MAS NA VERDADE É TEMPORAL
        end
    end
    #println("INverso: ", inv(Matrix(matrizSusceptancia)))
    for linha in ilha.linhas
        RHS = linha.Capacidade[est] +transpose(linha.linhaMatrizSensibilidade)*vetorPotenciaCarga
        #println("RHS: ",  RHS, " linhaMatrizSensibilidade: ", Array(linhaMatrizSensibilidade))
        linha.RHS[est] = round(RHS, digits=4)
        linha.coeficienteDemanda[est] = round(transpose(linha.linhaMatrizSensibilidade)*vetorPotenciaCarga, digits=4)
    end
end


lista_ilhas_function = calculaIlhasEletricas(lista_barras_slack)
for ilha in lista_ilhas_function    
    for est in caso.n_est
        calculaParametrosDaIlha(ilha,est)
    end
end


mapa_linha_valorMinimoCapacidadeLinha = OrderedDict()
for ilha in lista_ilhas_function 
    for linha in ilha.linhas
        lista_variaveis = []
        for barra in ilha.barras
            if barra.codigo != ilha.slack.codigo
                usi = get(mapa_codigoBARRA_nomeUSINA,barra.codigo,0)
                #println("Barra: ", barra.codigo, " NOME_USI: ", usi)
                UHE = get(mapa_nome_UHE,usi,0)
                UTE = get(mapa_nome_UTE,usi,0)
                if UHE != 0 push!(lista_variaveis, UHE) end
                if UTE != 0   push!(lista_variaveis, UTE) end
                if UHE == 0 && UTE == 0 push!(lista_variaveis,0) end                        
            end
        end
        valorMinimo = 0
        for i in 1:length(lista_variaveis)
            valor = 0
            if linha.linhaMatrizSensibilidade[i] < 0
                if  lista_variaveis[i] != 0 valor = lista_variaveis[i].gmax else 0 end
                valorMinimo += linha.linhaMatrizSensibilidade[i]*valor
            else
                if  lista_variaveis[i] != 0 valor = lista_variaveis[i].gmin else 0 end
                valorMinimo += linha.linhaMatrizSensibilidade[i]*valor
            end
        end

        for est in caso.n_est
            valorMinimo = valorMinimo - linha.coeficienteDemanda[est]
            #valorMinimo = sum(fator*fluxo.linhaMatrizSensibilidade[i]*lista_variaveis[i] for i in 1:length(lista_variaveis) ) 
            println("DE: $(fluxo.de.codigo) PARA: $(fluxo.para.codigo) valorMaximoCapacidadeLinha: $valorMinimo  CoefDEM: $(fluxo.coeficienteDemanda) RHS:  $(fluxo.RHS)")
            mapa_linha_valorMinimoCapacidadeLinha[(fluxo.de.codigo, fluxo.para.codigo,est)] = valorMinimo
            #@constraint(  m, sum(fator*fluxo.linhaMatrizSensibilidade[i]*lista_variaveis[i] for i in 1:length(lista_variaveis) ) + fator*folga_rede[(est, i_no.codigo, fluxo.linha)] == fator*fluxo.RHS   )    
        end
    end
end


##REDUCAO DE REDE
# A Redução de rede tem por objetivo desativar linhas que conectam barras geradoras com barras geradoras.
funcionalidade_Reduz_rede = 1
lista_linhas_ativas = []
linha_linhas_nao_ativas = []
if funcionalidade_Reduz_rede == 1
    for ilha in lista_ilhas_function
        for linha in ilha.linhas
            if mapa_linha_valorMinimoCapacidadeLinha[(linha.de.codigo, linha.para.codigo, est)] >= 0
                push!(lista_linhas_ativas, linha)
            else
                push!(linha_linhas_nao_ativas, linha)
            end
        end

        #ECO
        for linha in lista_linhas_ativas
            println("LINHA ATIVA: BARRA DE $(linha.de.codigo) BARRA PARA: $(linha.para.codigo)")
        end
        #ECO
        for linha in linha_linhas_nao_ativas
            println("LINHA NAO ATIVA: BARRA DE $(linha.de.codigo) BARRA PARA: $(linha.para.codigo)")
        end
    end

    ilha.linhas = lista_linhas_ativas
    ilha.linhasNaoAtivas = linha_linhas_nao_ativas
    calculaParametrosDaIlha(ilha)
end







###REDUCAO DE REDE
## A Redução de rede tem por objetivo desativar linhas que conectam barras geradoras com barras geradoras.
#funcionalidade_Reduz_rede = 1
#lista_linhas_ativas = []
#linha_linhas_nao_ativas = []
#if funcionalidade_Reduz_rede == 1
#    lista_barras_geracao = []
#    for barra in lista_barras_da_ilha
#        for uhe in lista_uhes
#            push!(lista_barras_geracao, uhe.barra.codigo)
#        end
#        for ute in lista_utes
#            push!(lista_barras_geracao, ute.barra.codigo)
#        end
#    end
#
#    for linha in lista_linhas_da_ilha
#        if linha.de.codigo in lista_barras_geracao && linha.para.codigo in lista_barras_geracao
#            push!(linha_linhas_nao_ativas, linha)
#        else
#            push!(lista_linhas_ativas, linha)
#        end
#    end
#
#    lista_linhas_da_ilha = lista_linhas_ativas
#
#    #ECO
#    for linha in lista_linhas_da_ilha
#        println("LINHA ATIVA: BARRA DE $(linha.de.codigo) BARRA PARA: $(linha.para.codigo)")
#    end
#    #ECO
#    for linha in linha_linhas_nao_ativas
#        println("LINHA NAO ATIVA: BARRA DE $(linha.de.codigo) BARRA PARA: $(linha.para.codigo)")
#    end
#end
#
#### FIM DA REDUCAO DE RE