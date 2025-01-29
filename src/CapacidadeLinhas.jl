include("FluxoDC.jl")
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

function atualizaValorMinimoCapacidadeLinhas(ilha,est, mapa_valores_minimos_geracoes, flagConsideraOutrasLinhas)
    for linha in ilha.linhasAtivas[est]
        lista_variaveis = []
        demanda_total = 0
        mapa_nomeUsina_CoefSensibilidade = OrderedDict()
        linha_matriz_sensibilidade = linha.linhaMatrizSensibilidade[est]
       
        gt_vars_capacidade = OrderedDict{String, JuMP.VariableRef}()
        gh_vars_capacidade = OrderedDict{String, JuMP.VariableRef}()
        deficit_barra = Dict{Int, JuMP.VariableRef}()
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
            UHE = get(mapa_nome_UHE,nome_usi,0)
            UTE = get(mapa_nome_UTE,nome_usi,0)
            if UHE != 0 
                gh_vars_capacidade[UHE.nome] = @variable(m_cap, base_name="gt_$(UHE.codigo)")
                @constraint(m_cap, gh_vars_capacidade[UHE.nome] >= mapa_valores_minimos_geracoes[UHE.nome])
                @constraint(m_cap, gh_vars_capacidade[UHE.nome] <= UHE.gmax) #linha, coluna
                push!(lista_uhes_cap, UHE)
            end
            if UTE != 0   
                gt_vars_capacidade[UTE.nome] = @variable(m_cap, base_name="gt_$(UTE.codigo)")
                @constraint(m_cap, gt_vars_capacidade[UTE.nome] >= mapa_valores_minimos_geracoes[UTE.nome])
                @constraint(m_cap, gt_vars_capacidade[UTE.nome] <= UTE.gmax) #linha, coluna
                push!(lista_utes_cap,UTE)
            end          
            
            deficit_barra[barra.codigo] = @variable(m_cap, base_name="deficitBarra_$(barra.codigo)")
            @constraint(m_cap, deficit_barra[barra.codigo] >= 0)
            demanda_total += barra.carga[est]
        end
        @constraint( m_cap, sum(gh_vars_capacidade[uhe.nome] for uhe in lista_uhes_cap) + sum(gt_vars_capacidade[term.nome] for term in lista_utes_cap) + sum(deficit_barra[barra.codigo] for barra in ilha.barrasAtivas[est])== demanda_total   )
                        
        @objective( m_cap, Min, sum(mapa_nomeUsina_CoefSensibilidade[term.nome] * gt_vars_capacidade[term.nome] for term in lista_utes_cap) 
        + sum(mapa_nomeUsina_CoefSensibilidade[uhe.nome] * gh_vars_capacidade[uhe.nome] for uhe in lista_uhes_cap)
        +sum(500000*deficit_barra[barra.codigo] for barra in ilha.barrasAtivas[est]) )

        ## FLAG Considera Outras Linhas Iterativamente também é possível
        if flagConsideraOutrasLinhas == 1
            
            folga_rede = Dict{LinhaConfig, JuMP.VariableRef}()
            for outrasLinhas in ilha.linhasAtivas[est]
                if linha.codigo != outrasLinhas.codigo
                    #println("PERCORRENDO LINHA: ", outrasLinhas.de.codigo, " - ", outrasLinhas.para.codigo)
                    lista_variaveis = []
                    for barra in ilha.barrasAtivas[est]
                        if barra.codigo != ilha.slack.codigo
                            usi = get(mapa_codigoBARRA_nomeUSINA,barra.codigo,0)
                            UHE = get(mapa_nome_UHE,usi,0)
                            UTE = get(mapa_nome_UTE,usi,0)
                            if UHE != 0 push!(lista_variaveis, gh_vars_capacidade[UHE.nome]) end
                            if UTE != 0   push!(lista_variaveis, gt_vars_capacidade[UTE.nome]) end
                            
                            if UHE == 0 && UTE == 0 
                                variavel = deficit_barra[barra.codigo]
                                push!(lista_variaveis,variavel) 
                            end
                        end
                    end

                    fator = ifelse(outrasLinhas.RHS[est] <= 0, -1 , 1)
                    folga_rede[outrasLinhas] = @variable(m_cap, base_name="sFluxo_$(outrasLinhas.de.codigo)_$(outrasLinhas.para.codigo)")
                    @constraint(m_cap, folga_rede[outrasLinhas] >= 0)
                    @constraint(m_cap, folga_rede[outrasLinhas] <= 2*outrasLinhas.Capacidade[est])
                    @constraint(m_cap, sum(fator*outrasLinhas.linhaMatrizSensibilidade[est][i]*lista_variaveis[i] for i in 1:length(lista_variaveis) ) + fator*folga_rede[outrasLinhas] == fator*outrasLinhas.RHS[est]   )
                end        
            end
        end


        JuMP.optimize!(m_cap) 
        status = termination_status(m_cap)
        #if status == MOI.INFEASIBLE
        #    println("The problem is infeasible.")
        #elseif status == MOI.OPTIMAL
        #    println("The problem is feasible and optimal.")
        #elseif status == MOI.FEASIBLE_POINT
        #    println("Solver returned a feasible point, but not necessarily optimal.")
        #else
        #    println("Solver returned status: ", status)
        #end
       #valorMinimo = 0
       #geracao_total = 0
        #if abs(linha.coeficienteDemanda[est]) > linha.Capacidade[est] # SE COEFDEM > CAP, RESULTA EM RHS NEGATIVO, FOLGA NEGATIVA
        
        #println(m_cap)



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
            #println(term.nome, " ", geracao)
            valorMinimo += geracao*mapa_nomeUsina_CoefSensibilidade[term.nome]
            geracao_total += geracao
        end

        for barra in ilha.barrasAtivas[est]
            valor_deficit = JuMP.value(deficit_barra[barra.codigo])
            #println("DEFICIT:  $(barra.codigo) valor: $valor_deficit")

        end 
        capacidadeMinima =    valorMinimo -linha.coeficienteDemanda[est] ##MENOR VALOR DE CAPACIDADE PARA EVITAR DEFICIT, CONSIDERANDO APENAS ESSA LINHA
        #end
        #println("EST: ", est, "DE: $(linha.de.codigo) PARA: $(linha.para.codigo) valorMaximoCapacidadeLinha: $capacidadeMinima ValMin: $valorMinimo CoefDEM: $(linha.coeficienteDemanda[est]) RHS:  $(linha.RHS[est]) CAP: $(linha.Capacidade[est]) GerTot: $geracao_total DemTot: $demanda_total")
        #mapa_linha_valorMinimoCapacidadeLinha[(linha.de.codigo, linha.para.codigo,est)] = valorMinimo
        linha.valorMinimoCapacidade[est] = capacidadeMinima
    end
end



flagConsideraOutrasLinhas = 1

mapa_valores_minimos_geracoes = OrderedDict()
for uhe in lista_uhes
    mapa_valores_minimos_geracoes[uhe.nome] = uhe.gmin
end
for term in lista_utes
    mapa_valores_minimos_geracoes[term.nome] = term.gmin
end



for ilha in lista_ilhas_eletricas   
    calculaFluxosIlhaMetodoSensibilidadeDC(ilha, 1, 1, lista_total_de_nos[1])
    #calculaFluxosIlhaMetodoDeltaDC(ilha, 1, 1, lista_total_de_nos[1])
    exit(1) 
    for est in 1:caso.n_est
        calculaParametrosDaIlha(ilha,est)
        atualizaValorMinimoCapacidadeLinhas(ilha,est, mapa_valores_minimos_geracoes, flagConsideraOutrasLinhas)
    end
end














#flag_reducao_rede = 0
#if flag_reducao_rede == 1
#    realizaReducaoDeRedePeloMetodoDoValorMinimoDeCapacidadeDasLinhas(ilha,est)
#    calculaParametrosDaIlha(ilha,est)
#end

