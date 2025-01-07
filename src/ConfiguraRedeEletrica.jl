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


function atualizaValorMinimoCapacidadeLinhas(ilha,est, mapa_valores_minimos_geracoes)
    for linha in ilha.linhasAtivas[est]
        lista_variaveis = []
        demanda_total = 0
        mapa_nomeUsina_CoefSensibilidade = OrderedDict()
        linha_matriz_sensibilidade = linha.linhaMatrizSensibilidade[est]
       
        gt_vars_capacidade = OrderedDict{String, JuMP.VariableRef}()
        gh_vars_capacidade = OrderedDict{String, JuMP.VariableRef}()

        m_cap = Model(GLPK.Optimizer)
        lista_uhes_cap = []
        lista_utes_cap = []
        indice = 1
        for barra in ilha.barrasAtivas[est]
            nome_usi = get(mapa_codigoBARRA_nomeUSINA,barra.codigo,0)
            if barra.codigo == ilha.slack.codigo && nome_usi != 0
                mapa_nomeUsina_CoefSensibilidade[nome_usi] = 0
            else
                mapa_nomeUsina_CoefSensibilidade[nome_usi] = linha_matriz_sensibilidade[indice]
                indice += 1
            end
            #println("Barra: ", barra.codigo, " NOME_USI: ", usi)
            UHE = get(mapa_nome_UHE,nome_usi,0)
            UTE = get(mapa_nome_UTE,nome_usi,0)
            if UHE != 0 
                gh_vars_capacidade[UHE.nome] = @variable(m_cap, base_name="gt_$(UHE.codigo)")
                #@constraint(m_cap, gh_vars_capacidade[UHE.nome] >= UHE.gmin)
                @constraint(m_cap, gh_vars_capacidade[UHE.nome] >= mapa_valores_minimos_geracoes[UHE.nome])
                @constraint(m_cap, gh_vars_capacidade[UHE.nome] <= UHE.gmax) #linha, coluna
                #push!(lista_variaveis, UHE) 
                push!(lista_uhes_cap, UHE)
            end
            if UTE != 0   
                gt_vars_capacidade[UTE.nome] = @variable(m_cap, base_name="gt_$(UTE.codigo)")
                #@constraint(m_cap, gt_vars_capacidade[UTE.nome] >= UTE.gmin)
                @constraint(m_cap, gt_vars_capacidade[UTE.nome] >= mapa_valores_minimos_geracoes[UTE.nome])
                @constraint(m_cap, gt_vars_capacidade[UTE.nome] <= UTE.gmax) #linha, coluna
                #push!(lista_variaveis, UTE) 
                push!(lista_utes_cap,UTE)
            end                    
            demanda_total += barra.carga[est]
        end

        @constraint( m_cap, sum(gh_vars_capacidade[uhe.nome] for uhe in lista_uhes_cap) + sum(gt_vars_capacidade[term.nome] for term in lista_utes_cap) == demanda_total   )
                        
        @objective( m_cap, Min, sum(mapa_nomeUsina_CoefSensibilidade[term.nome] * gt_vars_capacidade[term.nome] for term in lista_utes_cap) 
        + sum(mapa_nomeUsina_CoefSensibilidade[uhe.nome] * gh_vars_capacidade[uhe.nome] for uhe in lista_uhes_cap) )

        JuMP.optimize!(m_cap) 

       #valorMinimo = 0
       #geracao_total = 0
        #if abs(linha.coeficienteDemanda[est]) > linha.Capacidade[est] # SE COEFDEM > CAP, RESULTA EM RHS NEGATIVO, FOLGA NEGATIVA
        println(m_cap)
        valorMinimo = 0
        geracao = 0
        geracao_total = 0
        for uhe in lista_uhes_cap
            geracao = JuMP.value(gh_vars_capacidade[uhe.nome])
            
            valorMinimo += geracao*mapa_nomeUsina_CoefSensibilidade[uhe.nome]
            geracao_total += geracao
        end                
        for term in lista_utes_cap
            geracao = JuMP.value(gt_vars_capacidade[term.nome])
            println(term.nome, geracao)
            valorMinimo += geracao*mapa_nomeUsina_CoefSensibilidade[term.nome]
            geracao_total += geracao
        end
        #println(valorMinimo)
        #println(valorMinimo -linha.coeficienteDemanda[est])     
        capacidadeMinima =    valorMinimo -linha.coeficienteDemanda[est] ##MENOR VALOR DE CAPACIDADE PARA EVITAR DEFICIT, CONSIDERANDO APENAS ESSA LINHA
        #end
        println("EST: ", est, "DE: $(linha.de.codigo) PARA: $(linha.para.codigo) valorMaximoCapacidadeLinha: $capacidadeMinima ValMin: $valorMinimo CoefDEM: $(linha.coeficienteDemanda[est]) RHS:  $(linha.RHS[est]) CAP: $(linha.Capacidade[est]) GerTot: $geracao_total DemTot: $demanda_total")
        #mapa_linha_valorMinimoCapacidadeLinha[(linha.de.codigo, linha.para.codigo,est)] = valorMinimo
        linha.valorMinimoCapacidade[est] = capacidadeMinima
    end
end


flag_reducao_rede = 0
mapa_valores_minimos_geracoes = OrderedDict()
for uhe in lista_uhes
    mapa_valores_minimos_geracoes[uhe.nome] = uhe.gmin
end
for term in lista_utes
    mapa_valores_minimos_geracoes[term.nome] = term.gmin
end
for ilha in lista_ilhas_eletricas    
    for est in caso.n_est
        calculaParametrosDaIlha(ilha,est)
        atualizaValorMinimoCapacidadeLinhas(ilha,est, mapa_valores_minimos_geracoes)
        
        if flag_reducao_rede == 1
            realizaReducaoDeRedePeloMetodoDoValorMinimoDeCapacidadeDasLinhas(ilha,est)
            calculaParametrosDaIlha(ilha,est)
        end
    end
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