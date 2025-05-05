include("DefStructs.jl")
using JSON
using CSV
using DataFrames
#using Graphs
using LightGraphs
using SparseArrays
using DataStructures
using LinearAlgebra
using JuMP, GLPK, Plots, Measures, Plots, SparseArrays, DataFrames, Dates

function getFilhos(no, df_arvore)
    filhos = df_arvore[df_arvore.NO_PAI .== no, :NO]
    return filhos
end

function buscaPai(no, df_arvore)
    pai =  (df_arvore[(df_arvore.NO .== no), "NO_PAI"][1])
    return pai
end

function retornaListaCaminho(no, df_arvore)
    lista = []
    push!(lista,no)
    no_inicial = no
    periodo_no = (df_arvore[(df_arvore.NO .== no), "PER"][1])
    for est in 1:(periodo_no-1)
        pai = buscaPai(no_inicial, df_arvore)
        push!(lista,pai)
        no_inicial = pai
    end
    return lista
end




function calculaDistanciaAninhada(df_arvore_original, df_cenarios_original, df_arvore_reduzida, df_cenarios_reduzida)
    estagios = unique(df_arvore_reduzida[!, "PER"])
    distancia_aninhada = Dict{Tuple{String, String}, Float64}()
    solucao_planoTransporte = Dict{Tuple{String, String}, Float64}()
    solucao_planoTransporteCondicional = Dict{Tuple{String, String}, Float64}()
    probabilidade_condicional_no = Dict{Int32, Float64}()
    #for estagio in sort(estagios, rev=true)
    for estagio in estagios
        nos_originais_estagios = unique(df_arvore_original[df_arvore_original[:, "PER"] .== estagio, "NO"])
        nos_reduzido_estagio   = unique(df_arvore_reduzida[df_arvore_reduzida[:, "PER"] .== estagio, "NO"])
        for no_orig in nos_originais_estagios
            probabilidade_condicional_no[no_orig] = 0
            for no_red in nos_reduzido_estagio
                distancia_aninhada[("o" * string(no_orig), "r" * string(no_red))] = 0
                solucao_planoTransporte[("o" * string(no_orig), "r" * string(no_red))] = 0
                
                #if(no_orig == 3)
                #    println("o:", no_orig, " r: ", no_red, " val: ", solucao_planoTransporte[("o" * string(no_orig), "r" * string(no_red))])
                #end
                
                solucao_planoTransporteCondicional[("o" * string(no_orig), "r" * string(no_red))] = 0
                
            end
        end
    end
    estagios_otimizacao = copy(estagios)
    deleteat!(estagios_otimizacao, findfirst(==(maximum(estagios_otimizacao)), estagios_otimizacao))


    for estagio in sort(estagios_otimizacao, rev=true)
        nos_originais_estagios = unique(df_arvore_original[df_arvore_original[:, "PER"] .== estagio, "NO"])
        nos_reduzido_estagio   = unique(df_arvore_reduzida[df_arvore_reduzida[:, "PER"] .== estagio, "NO"])
        #println("ORIG: ", nos_originais_estagios)
        #println("RED: ", nos_reduzido_estagio)
        for no_orig in nos_originais_estagios
            for no_red in nos_reduzido_estagio
                filhos_originais = getFilhos(no_orig, df_arvore_original)
                filhos_red = getFilhos(no_red, df_arvore_reduzida)
                #println("no_orig: ", no_orig, " no_red: ", no_red)
                #println("FIlhos Orig: ", filhos_originais, " Filhos_red: ", filhos_red)
                planoTransporte = Dict{Tuple{String, String}, JuMP.VariableRef}()
                distancia = Dict{Tuple{String, String}, Float64}()
                constraint_dict = Dict{String, JuMP.ConstraintRef}()
                global m = Model(GLPK.Optimizer)
                for no_filho_orig in filhos_originais
                    #caminho_no_orig = retornaListaCaminho(no_filho_orig, df_arvore_original)
                    #prob_cond = 1
                    #lista_probs_caminho = []
                    #for node in caminho_no_orig
                    #    prob_no = (df_arvore_original[(df_arvore_original.NO .== node), "PROB"][1])
                    #    push!(lista_probs_caminho, prob_no)
                    #    prob_cond = prob_cond*prob_no
                    #end

                    for no_filho_red in filhos_red
                        #caminho_no_red = retornaListaCaminho(no_filho_red, df_arvore_reduzida)
                        #prob_cond = 1
                        #lista_probs_caminho = []
                        #for node in caminho_no_red
                        #    prob_no = (df_arvore_reduzida[(df_arvore_reduzida.NO .== node), "PROB"][1])
                        #    push!(lista_probs_caminho, prob_no)
                        #    prob_cond = prob_cond*prob_no
                        #end

                        vazoes_no_filho_orig = df_cenarios_original[df_cenarios_original[:, "NO"] .== no_filho_orig, :]
                        vazoes_no_filho_red  = df_cenarios_reduzida[df_cenarios_reduzida[:, "NO"] .== no_filho_red, :]
                        #print("no_filho_orig: ", no_filho_orig, " no_filho_red: ", no_filho_red)
                        #println("vazoes_no_filho_orig: ", vazoes_no_filho_orig, " vazoes_no_filho_red: ", vazoes_no_filho_red)
                        #sorted_orig = sort(vazoes_no_filho_orig, :NOME_UHE)
                        #sorted_red  = sort(vazoes_no_filho_red,  :NOME_UHE)
                        #println("sorted_orig: ", sorted_orig, " sorted_red: ", sorted_red)
                        ## Extract VAZAO as vectors
                        #vazao_orig = sorted_orig[:, "VAZAO"]
                        #vazao_red  = sorted_red[:, "VAZAO"]
                        #println("vazao_orig: ", vazao_orig, " vazao_red: ", vazao_red)
                        #@assert length(unique(vazoes_no_filho_orig[:, "NOME_UHE"])) == nrow(vazoes_no_filho_orig)
                        #@assert length(unique(vazoes_no_filho_red[:, "NOME_UHE"])) == nrow(vazoes_no_filho_red)
                        joined = innerjoin(vazoes_no_filho_orig, vazoes_no_filho_red, on="NOME_UHE", makeunique=true)
                        #println("joined: ", joined)
                        vazao_orig = joined[:, "VAZAO"]
                        vazao_red  = joined[:, "VAZAO_1"]
                        #println("vazao_orig: ", vazao_orig, " vazao_red: ", vazao_red)
                        dist = norm(vazao_orig .- vazao_red)
                        #println("no_filho_orig: ", no_filho_orig, " vazoes_no_filho_orig: ", vazao_orig, " no_filho_red: ", no_filho_red, " vazoes_no_filho_red: ", vazao_red , " dist: ",dist)  # This will give the Euclidean distance
                        planoTransporte[("o" * string(no_filho_orig), "r" * string(no_filho_red))] = @variable(m, base_name="pi_o$(no_filho_orig)_r$(no_filho_red)")
                        distancia[("o" * string(no_filho_orig), "r" * string(no_filho_red))] = round(dist, digits=2)
                    end
                end

                #@objective(m, Min, sum( (distancia[("o" * string(no_filho_orig), "r" * string(no_filho_red))]^2 + distancia_aninhada[("o" * string(no_filho_orig), "r" * string(no_filho_red))]) * planoTransporte[("o" * string(no_filho_orig), "r" * string(no_filho_red))] for no_filho_orig in filhos_originais, no_filho_red in filhos_red))
                @objective(m, Min, sum( (distancia[("o" * string(no_filho_orig), "r" * string(no_filho_red))] + (distancia_aninhada[("o" * string(no_filho_orig), "r" * string(no_filho_red))]) ) * planoTransporte[("o" * string(no_filho_orig), "r" * string(no_filho_red))] for no_filho_orig in filhos_originais, no_filho_red in filhos_red))
                ## ADICIONAR RESTRICOES
                for no_filho_orig in filhos_originais
                    #print("est: ", est, " no: ", no.codigo, " etapa: ", etapa)
                    prob_filho_orig = df_arvore_original[df_arvore_original[:, "NO"] .== no_filho_orig, "PROB"][1]
                    constraint_dict["o" * string(no_filho_orig)] = @constraint(m, sum(planoTransporte[("o" * string(no_filho_orig), "r" * string(no_filho_red))] for no_filho_red in filhos_red) == prob_filho_orig) 
                end
                
                for no_filho_red in filhos_red
                    prob_filho_red = df_arvore_reduzida[df_arvore_reduzida[:, "NO"] .== no_filho_red, "PROB"][1]
                    constraint_dict["r" * string(no_filho_red)] = @constraint(m, sum(planoTransporte[("o" * string(no_filho_orig), "r" * string(no_filho_red))] for no_filho_orig in filhos_originais) == prob_filho_red) 
                end

                for no_filho_orig in filhos_originais
                    for no_filho_red in filhos_red
                        @constraint(  m, planoTransporte[("o" * string(no_filho_orig), "r" * string(no_filho_red))]  >= 0 ) 
                        
                    end
                end
                #println("no_orig: ", no_orig, " filhos_originais: ", filhos_originais, " no_red: ", no_red, " filhos_red: ", filhos_red)
                #println(m)


                JuMP.optimize!(m) 
                status = JuMP.termination_status(m)
                if status == MOI.INFEASIBLE || status == MOI.INFEASIBLE_OR_UNBOUNDED
                    #error("Optimization problem is infeasible. Stopping execution.")
                    #println("Optimization problem is infeasible. Stopping execution.")
                end
                

                dist_aninhada = JuMP.objective_value(m)
                distancia_aninhada[("o"*string(no_orig), "r"*string(no_red))] = round(dist_aninhada, digits=2)
                #println("Total FOB value: ", dist_aninhada)
                for no_filho_orig in filhos_originais
                    for no_filho_red in filhos_red
                        solucao_planoTransporte[("o" * string(no_filho_orig), "r" * string(no_filho_red))] = JuMP.value(planoTransporte[("o" * string(no_filho_orig), "r" * string(no_filho_red))])
                        #println(no_filho_orig, " ", no_filho_red, " : ", solucao_planoTransporte[("o" * string(no_filho_orig), "r" * string(no_filho_red))])
                    end
                end


            end
        end
    end


    estagios_pos_otimizacao = copy(estagios)
    deleteat!(estagios_pos_otimizacao, findfirst(==(minimum(estagios_pos_otimizacao)), estagios_pos_otimizacao))
    #println(estagios_pos_otimizacao)
    for estagio in sort(estagios_pos_otimizacao, rev=true)
        nos_originais_estagios = unique(df_arvore_original[df_arvore_original[:, "PER"] .== estagio, "NO"])
        nos_reduzido_estagio   = unique(df_arvore_reduzida[df_arvore_reduzida[:, "PER"] .== estagio, "NO"])
        #println("estagio: ", estagio, " ORIG: ", nos_originais_estagios, " RED: ", nos_reduzido_estagio)
        for no_orig in nos_originais_estagios
            for no_red in nos_reduzido_estagio
                
                caminho_orig = retornaListaCaminho(no_orig, df_arvore_original)
                deleteat!(caminho_orig, findfirst(==(minimum(caminho_orig)), caminho_orig))
                caminho_orig = filter(!=(no_orig), caminho_orig)
                caminho_red =  retornaListaCaminho(no_red, df_arvore_reduzida)
                deleteat!(caminho_red, findfirst(==(minimum(caminho_red)), caminho_red))
                caminho_red = filter(!=(no_red), caminho_red)
                #println("est: ", estagio, " no_orig: ", no_orig, " no_red: ", no_red)
                pi = solucao_planoTransporte[("o" * string(no_orig), "r" * string(no_red))] 
                pi_cond = pi
                #println("caminho_orig: ", caminho_orig, " caminho_red: ", caminho_red, " pi: ", pi)
                #exit(1)
                for est in eachindex(caminho_orig)
                    pi_pai = solucao_planoTransporte[("o" * string(caminho_orig[est]), "r" * string(caminho_red[est]))] 
                    pi_cond = pi_cond*pi_pai
                    #println(" est_otim: ", est, " orig: ", caminho_orig[est], " red: ", caminho_red[est], " pi: ", pi_pai, " pi_filho: ", pi, " cond: ", pi_cond)
                end
                solucao_planoTransporteCondicional[("o" * string(no_orig), "r" * string(no_red))] = round(pi_cond, digits = 2)
                #println("no_orig: ", no_orig, " no_red: ", no_red, " pi: ", pi, " pi_cond: ", pi_cond,  " caminho_orig: ", caminho_orig, " caminho_red: ", caminho_red)
            end
        end
    end
    #println(solucao_planoTransporteCondicional)
    return (distancia_aninhada,solucao_planoTransporteCondicional, solucao_planoTransporte )
end







function atualizaArvoreDistanciaAninhada(df_arvore_original, df_cenarios_original, df_arvore_reduzida, df_cenarios_reduzida, solucao_planoTransporteCondicional)

    ######## ATUALIZACAO DAS REALIZACOES
    estagios = unique(df_arvore_reduzida[!, "PER"])
    estagios_altera_realizacoes = copy(estagios)
    deleteat!(estagios_altera_realizacoes, findfirst(==(minimum(estagios_altera_realizacoes)), estagios_altera_realizacoes))
    for estagio in sort(estagios_altera_realizacoes, rev=true)
        nos_originais_estagios = unique(df_arvore_original[df_arvore_original[:, "PER"] .== estagio, "NO"])
        nos_reduzido_estagio   = unique(df_arvore_reduzida[df_arvore_reduzida[:, "PER"] .== estagio, "NO"])
        #println("est: ", estagio)
        for no_red in nos_reduzido_estagio
            soma_pis = 0
            
            idxs = findall(df_cenarios_reduzida[:, "NO"] .== no_red)
            sorted_idxs = sort(idxs, by = i -> df_cenarios_reduzida[i, "NOME_UHE"])
            vazoes_no = df_cenarios_reduzida[idxs, "VAZAO"]
            #println("antes: ", vazoes_no)
            parcelas = zeros(length(sorted_idxs))
            for no_orig in nos_originais_estagios
                df_orig = df_cenarios_original[df_cenarios_original[:, "NO"] .== no_orig, :]
                #println(df_orig)
                #sorted_orig = sort(df_orig, by = row -> row["NOME_UHE"])  # Ensure consistent hydro order
                #sorted_orig = sort(df_orig, by = :NOME_UHE)# Ensure consistent hydro order
                #sorted_orig = sort(df_orig, cols = :NOME_UHE)  # ← aqui está a mudança!
                #sorted_orig = sort(df_orig, by = :NOME_UHE, rev = false)
                #vazoes_no_orig = sorted_orig[:, "VAZAO"]
                vazoes_no_orig = df_orig[:, "VAZAO"]
                pi_alteracao = solucao_planoTransporteCondicional[("o" * string(no_orig), "r" * string(no_red))]
                soma_pis += pi_alteracao
                parcelas .+= pi_alteracao .* vazoes_no_orig
                #println("parcelas: ", parcelas, " soma_pis: ", soma_pis, " pi_alteracao: ", pi_alteracao, " vazoes_no_orig: ", vazoes_no_orig, " no_orig: ", no_orig, " no_red: ", no_red)
            end
            #if(no_red == 4)
            #    println("parcelas: ", parcelas, " soma_pis: ", soma_pis)
            #end
            if soma_pis == 0
                println("⚠️ Ignorando atualização para no_red = $no_red no estágio $estagio (soma_pis = 0)")
                distancia_aninhada = Dict()
                distancia_aninhada[("o1", "r1")] = 99999999999999999999999999999
                return (0,0,distancia_aninhada,0)
                #continue
            end
            parcelas = parcelas/soma_pis
            #df_cenarios_reduzida[sorted_idxs, "VAZAO"] .= parcelas
            df_cenarios_reduzida[sorted_idxs, "VAZAO"] .= round.(parcelas, digits=2)
            #novo_vazoes_no = df_cenarios_reduzida[idxs, "VAZAO"]
            #println("depois: ", novo_vazoes_no)
        end

    end

    #println(df_cenarios_reduzida)
    ############# ATUALIZACAO DAS PROBABILIDADES


    estagios = unique(df_arvore_reduzida[!, "PER"])
    distancia_aninhada = Dict{Tuple{String, String}, Float64}()
    solucao_planoTransporte = Dict{Tuple{String, String}, Float64}()
    solucao_planoTransporteCondicional = Dict{Tuple{String, String}, Float64}()
    solucaoProbabilidade = Dict{String, Float64}()
    for estagio in sort(estagios, rev=true)
        nos_originais_estagios = unique(df_arvore_original[df_arvore_original[:, "PER"] .== estagio, "NO"])
        nos_reduzido_estagio   = unique(df_arvore_reduzida[df_arvore_reduzida[:, "PER"] .== estagio, "NO"])
        for no_orig in nos_originais_estagios
            for no_red in nos_reduzido_estagio
                distancia_aninhada[("o" * string(no_orig), "r" * string(no_red))] = 0
                solucao_planoTransporte[("o" * string(no_orig), "r" * string(no_red))] = 0
                solucao_planoTransporteCondicional[("o" * string(no_orig), "r" * string(no_red))] = 0
                solucaoProbabilidade["r" * string(no_red)] = 0
            end
        end
    end

    estagios = unique(df_arvore_reduzida[!, "PER"])
    estagios_otimizacao = copy(estagios)
    deleteat!(estagios_otimizacao, findfirst(==(minimum(estagios_otimizacao)), estagios_otimizacao))
    for estagio in sort(estagios_otimizacao, rev=true)
        nos_originais_estagios = unique(df_arvore_original[df_arvore_original[:, "PER"] .== estagio, "NO"])
        nos_reduzido_estagio   = unique(df_arvore_reduzida[df_arvore_reduzida[:, "PER"] .== estagio, "NO"])
        #println("EST: ", estagio, " ORIG: ", nos_originais_estagios, " RED: ", nos_reduzido_estagio)
        planoTransporte = Dict{Tuple{String, String}, JuMP.VariableRef}()
        variavelProbabilidade = Dict{String, JuMP.VariableRef}()
        distancia = Dict{Tuple{String, String}, Float64}()
        constraint_dict = Dict{String, JuMP.ConstraintRef}()
        global m = Model(GLPK.Optimizer)
        for no_orig in nos_originais_estagios
            for no_red in nos_reduzido_estagio
                vazoes_no_orig = df_cenarios_original[df_cenarios_original[:, "NO"] .== no_orig, :]
                vazoes_no_red  = df_cenarios_reduzida[df_cenarios_reduzida[:, "NO"] .== no_red, :]
                #@assert length(unique(vazoes_no_orig[:, "NOME_UHE"])) == nrow(vazoes_no_orig)
                #@assert length(unique(vazoes_no_red[:, "NOME_UHE"])) == nrow(vazoes_no_red)
                joined = innerjoin(vazoes_no_orig, vazoes_no_red, on="NOME_UHE", makeunique=true)
                #println("joined: ", joined)
                vazao_orig = joined[:, "VAZAO"]
                vazao_red  = joined[:, "VAZAO_1"]
                #println("vazao_orig: ", vazao_orig, " vazao_red: ", vazao_red)
                dist = norm(vazao_orig .- vazao_red)
                #println(dist)  # This will give the Euclidean distance
                planoTransporte[("o" * string(no_orig), "r" * string(no_red))] = @variable(m, base_name="pi_o$(no_orig)_r$(no_red)")
                #distancia[("o" * string(no_orig), "r" * string(no_red))] = dist
                distancia[("o" * string(no_orig), "r" * string(no_red))] = round(dist, digits=2)
                #if no_orig == 4 && no_red in [4, 7]
                #    println(joined)
                #    println(vazoes_no_orig)
                #    println(vazoes_no_red)
                #    println("no_orig: ", no_orig, " no_red: ", no_red, " dist: ", distancia[("o" * string(no_orig), "r" * string(no_red))])
                #end
            end
        end#+ distancia_aninhada[("o" * string(no_filho_orig), "r" * string(no_filho_red))]

        @objective(m, Min, sum( (round(distancia[("o" * string(no_orig), "r" * string(no_red))]^2, digits=2) + distancia_aninhada[("o" * string(no_orig), "r" * string(no_red))]) * planoTransporte[("o" * string(no_orig), "r" * string(no_red))] for no_orig in nos_originais_estagios, no_red in nos_reduzido_estagio))
        #@objective(m, Min, sum( (round(distancia[("o" * string(no_orig), "r" * string(no_red))], digits=2) + distancia_aninhada[("o" * string(no_orig), "r" * string(no_red))]) * planoTransporte[("o" * string(no_orig), "r" * string(no_red))] for no_orig in nos_originais_estagios, no_red in nos_reduzido_estagio))
        
        nos_estagio_anterior_red = unique(df_arvore_reduzida[df_arvore_reduzida[:, "PER"] .== estagio-1, "NO"])
        nos_estagio_anterior_orig = unique(df_arvore_original[df_arvore_original[:, "PER"] .== estagio-1, "NO"])
        ## ADICIONAR RESTRICOES
        for no_orig in nos_originais_estagios
            #print("est: ", est, " no: ", no.codigo, " etapa: ", etapa)
            prob_orig = df_arvore_original[df_arvore_original[:, "NO"] .== no_orig, "PROB"][1]
            for no_anterior in nos_estagio_anterior_red
                filhos = getFilhos(no_anterior, df_arvore_reduzida)
                constraint_dict["o" * string(no_orig)] = @constraint(m, sum(planoTransporte[("o" * string(no_orig), "r" * string(no_red))] for no_red in filhos) == prob_orig) 
            end
        end
        for no_orig in nos_originais_estagios
            for no_red in nos_reduzido_estagio
                @constraint(  m, planoTransporte[("o" * string(no_orig), "r" * string(no_red))]  >= 0 ) 
            end
        end
        for no_red in nos_reduzido_estagio
            variavelProbabilidade["r"*string(no_red)] = @variable(m, base_name="Prob_r$(no_red)")
            for no_anterior in nos_estagio_anterior_orig
                filhos = getFilhos(no_anterior, df_arvore_original)
                #println("no_anterior: ", no_anterior, " filhos: ", filhos)
                constraint_dict["r" * string(no_red)] = @constraint(m, sum(planoTransporte[("o" * string(no_orig), "r" * string(no_red))] for no_orig in filhos) == variavelProbabilidade["r"*string(no_red)]) 
            end        
        end
        for no_anterior in nos_estagio_anterior_red
            filhos = getFilhos(no_anterior, df_arvore_reduzida)
            constraint_dict["P_r" * string(no_anterior)] = @constraint(m, sum(variavelProbabilidade["r"*string(no_red)] for no_red in filhos) == 1) 
        end

        println(m)



        JuMP.optimize!(m) 
        status = JuMP.termination_status(m)
        if status == MOI.INFEASIBLE || status == MOI.INFEASIBLE_OR_UNBOUNDED
            #error("Optimization problem is infeasible. Stopping execution.")
            #println("Optimization problem is infeasible. Stopping execution.")
        end
        


        for no_orig in nos_originais_estagios
            for no_red in nos_reduzido_estagio
                solucao_planoTransporte[("o" * string(no_orig), "r" * string(no_red))] = round(JuMP.value(planoTransporte[("o" * string(no_orig), "r" * string(no_red))]),digits=2)
                #println(no_orig, " ", no_red, " : ", solucao_planoTransporte[("o" * string(no_orig), "r" * string(no_red))])
            end
        end
        for no_red in nos_reduzido_estagio
            solucaoProbabilidade[("r" * string(no_red))] =  round(JuMP.value(variavelProbabilidade["r"*string(no_red)]), digits=2)
            #println("no_red: ", no_red, " sol: ", solucaoProbabilidade["r"*string(no_red)])
        end
        
        for no_anterior_orig in nos_estagio_anterior_orig
            for no_anterior_red in nos_estagio_anterior_red
                filhos_originais = getFilhos(no_anterior_orig, df_arvore_original)
                filhos_red = getFilhos(no_anterior_red, df_arvore_reduzida)
                aux_distancia_aninhada = 0
                for no_filho_orig in filhos_originais
                    for no_filho_red in filhos_red
                        dist = distancia[("o" * string(no_filho_orig), "r" * string(no_filho_red))]
                        pi = solucao_planoTransporte[("o" * string(no_filho_orig), "r" * string(no_filho_red))]
                        aux_distancia_aninhada += (dist^2)*pi
                    end
                end
                distancia_aninhada[("o" * string(no_anterior_orig), "r" * string(no_anterior_red))] = round(aux_distancia_aninhada,digits=2)
                #println("no_anterior_orig: ", no_anterior_orig, " no_anterior_red: ", no_anterior_red, " dis: ", round(aux_distancia_aninhada,digits=2))
            end
        end

        if length(nos_estagio_anterior_orig) == 1 && length(nos_estagio_anterior_red) == 1
            dist_aninhada = round(JuMP.objective_value(m), digits=2)
            distancia_aninhada[("o" * string(nos_estagio_anterior_orig[1]), "r" * string(nos_estagio_anterior_red[1]))] = dist_aninhada
            #println("Total FOB value: ", dist_aninhada)
        end
    end

    #print(df_arvore_reduzida)

    ###### ATUALIZA PROBABILIDADES ARVORE
    for estagio in sort(estagios_otimizacao, rev=true)
        nos_reduzido_estagio = unique(df_arvore_reduzida[df_arvore_reduzida[:, "PER"] .== estagio, "NO"])
        for no_red in nos_reduzido_estagio
            prob = solucaoProbabilidade[("r" * string(no_red))]
            if no_red != 1
                idxs = findall(df_arvore_reduzida[:, "NO"] .== no_red)
                df_arvore_reduzida[idxs, "PROB"] .= prob
            end
        end
    end
    #print(df_arvore_reduzida)

    #### CALCULA PLANO DE TRANSPORTE CONDICIONAL
    estagios_pos_otimizacao = copy(estagios)
    deleteat!(estagios_pos_otimizacao, findfirst(==(minimum(estagios_pos_otimizacao)), estagios_pos_otimizacao))
    #println(estagios_pos_otimizacao)
    for estagio in sort(estagios_pos_otimizacao, rev=true)
        nos_originais_estagios = unique(df_arvore_original[df_arvore_original[:, "PER"] .== estagio, "NO"])
        nos_reduzido_estagio   = unique(df_arvore_reduzida[df_arvore_reduzida[:, "PER"] .== estagio, "NO"])
        #println("estagio: ", estagio, " ORIG: ", nos_originais_estagios, " RED: ", nos_reduzido_estagio)
        for no_orig in nos_originais_estagios
            for no_red in nos_reduzido_estagio
                pi = solucao_planoTransporte[("o" * string(no_orig), "r" * string(no_red))] 
                caminho_orig = retornaListaCaminho(no_orig, df_arvore_original)
                deleteat!(caminho_orig, findfirst(==(minimum(caminho_orig)), caminho_orig))
                caminho_orig = filter(!=(no_orig), caminho_orig)
                caminho_red =  retornaListaCaminho(no_red, df_arvore_reduzida)
                deleteat!(caminho_red, findfirst(==(minimum(caminho_red)), caminho_red))
                caminho_red = filter(!=(no_red), caminho_red)
                pi_cond = pi
                for est in eachindex(caminho_orig)
                    pi_pai = solucao_planoTransporte[("o" * string(caminho_orig[est]), "r" * string(caminho_red[est]))] 
                    pi_cond = pi_cond*pi_pai
                    #println(" est_otim: ", est, " orig: ", caminho_orig[est], " red: ", caminho_red[est], " pi: ", pi_pai, " pi_filho: ", pi, " cond: ", pi_cond)
                end
                solucao_planoTransporteCondicional[("o" * string(no_orig), "r" * string(no_red))] = round(pi_cond, digits=2)
                #println("no_orig: ", no_orig, " no_red: ", no_red, " pi: ", pi, " pi_cond: ", pi_cond,  " caminho_orig: ", caminho_orig, " caminho_red: ", caminho_red)
            end
        end
    end
    return (df_arvore_reduzida, df_cenarios_reduzida, distancia_aninhada, solucao_planoTransporteCondicional)
end
#str_caso = "C:/Users/testa/Documents/git/3dp-minilab/Carmen/exercicio_27cen_1D/27_Aberturas_Equiprovavel"
str_caso = "C:/Users/testa/Documents/git/3dp-minilab/Capitulo_5/caso_mini_500Cen_cluster_semanais/avaliaArvoresRepresentativo/Rodada_Final"
#str_caso = "C:/Users/testa/Documents/git/3dp-minilab/Dissertacao/teste_simples/caso_mini_60"
#Path_orig = str_caso*"/Pente_GVZP"
Path_orig = str_caso*"/Pente"
#Path_orig = str_caso*"/Arvore_GVZP"
PATH_ARVORE_ORIGINAL = Path_orig*"/arvore.csv"
df_arvore_original = CSV.read(PATH_ARVORE_ORIGINAL, DataFrame)
PATH_CENARIOS_ORIGINAL = Path_orig*"/cenarios.csv"
df_cenarios_original = CSV.read(PATH_CENARIOS_ORIGINAL, DataFrame)

#lista_paths_red = ["A_2_2_2", "A_4_2_1"]
#lista_casos = ["BKAssimetrico", "KMeansAssimetricoProb"]
#lista_paths_red = ["Pente_8cen"]
#lista_casos = ["BKAssimetrico", "KMeansPente"]
lista_paths_red = ["Deterministico","Vassoura"]
lista_paths_red = ["A_25_125_250"]
lista_casos = ["KMeansAssimetricoProb"]
lista_paths_red = ["A_100_100_100" ]
lista_casos = ["KMeansPente"]
#lista_casos = [""]
for path_red in lista_paths_red
    for caso in lista_casos
        global Path_red = str_caso*"/"*path_red*"/"*caso
        global PATH_ARVORE_REDUZIDA = Path_red*"/arvore.csv"
        global df_arvore_reduzida = CSV.read(PATH_ARVORE_REDUZIDA, DataFrame)
        global PATH_CENARIOS_REDUZIDA = Path_red*"/cenarios.csv"
        global df_cenarios_reduzida = CSV.read(PATH_CENARIOS_REDUZIDA, DataFrame)
        (distancia_aninhada,solucao_planoTransporteCondicional , solucao_planoTransporte ) = calculaDistanciaAninhada(df_arvore_original, df_cenarios_original, df_arvore_reduzida, df_cenarios_reduzida)
        println(Path_red, ": ", distancia_aninhada[("o1","r1")])        
    end
end



#Path_red = str_caso*"/Arvore"
Path_red = str_caso*"/Pente"
#Path_red = str_caso*"/Arvore_GVZP"
PATH_ARVORE_REDUZIDA = Path_red*"/arvore.csv"
df_arvore_reduzida = CSV.read(PATH_ARVORE_REDUZIDA, DataFrame)
PATH_CENARIOS_REDUZIDA = Path_red*"/cenarios.csv"
df_cenarios_reduzida = CSV.read(PATH_CENARIOS_REDUZIDA, DataFrame)
(distancia_aninhada,solucao_planoTransporteCondicional , solucao_planoTransporte ) = calculaDistanciaAninhada(df_arvore_original, df_cenarios_original, df_arvore_reduzida, df_cenarios_reduzida)
println(Path_red, ": ", distancia_aninhada[("o1","r1")])  



Path_red = str_caso*"/Pente_GVZP"
#Path_red = str_caso*"/Pente_GVZP"
PATH_ARVORE_REDUZIDA = Path_red*"/arvore.csv"
df_arvore_reduzida = CSV.read(PATH_ARVORE_REDUZIDA, DataFrame)
PATH_CENARIOS_REDUZIDA = Path_red*"/cenarios.csv"
df_cenarios_reduzida = CSV.read(PATH_CENARIOS_REDUZIDA, DataFrame)
(distancia_aninhada,solucao_planoTransporteCondicional , solucao_planoTransporte ) = calculaDistanciaAninhada(df_arvore_original, df_cenarios_original, df_arvore_reduzida, df_cenarios_reduzida)
println(Path_red, ": ", distancia_aninhada[("o1","r1")])  
exit(1)




#str_caso = "C:/Users/testa/Documents/git/3dp-minilab/Carmen/teste_ND"
str_caso = "C:/Users/testa/Documents/git/3dp-minilab/Carmen/exercicio_27cen_1D/3Aberturas_Equiprovavel"
Path_orig = str_caso*"/Arvore_GVZP"
Path_red = str_caso*"/A_4_2_3/ClusterSimetrico"
#Path_orig = str_caso*"/Original"
#Path_red = str_caso*"/Reduzida"
PATH_ARVORE_ORIGINAL = Path_orig*"/arvore.csv"
PATH_ARVORE_REDUZIDA = Path_red*"/arvore.csv"
df_arvore_original = CSV.read(PATH_ARVORE_ORIGINAL, DataFrame)
df_arvore_reduzida = CSV.read(PATH_ARVORE_REDUZIDA, DataFrame)
PATH_CENARIOS_ORIGINAL = Path_orig*"/cenarios.csv"
PATH_CENARIOS_REDUZIDA = Path_red*"/cenarios.csv"
df_cenarios_original = CSV.read(PATH_CENARIOS_ORIGINAL, DataFrame)
df_cenarios_reduzida = CSV.read(PATH_CENARIOS_REDUZIDA, DataFrame)
(distancia_aninhada,solucao_planoTransporteCondicional , solucao_planoTransporte ) = calculaDistanciaAninhada(df_arvore_original, df_cenarios_original, df_arvore_reduzida, df_cenarios_reduzida)
global distancia_anterior = distancia_aninhada[("o1","r1")]
global iteracao = 1
global mapa_arvoreOtima = Dict{Int, Tuple{DataFrame, DataFrame}}()
mapa_arvoreOtima[0] = (df_arvore_reduzida, df_cenarios_reduzida)
#print(df_arvore_reduzida)
println("Dist ini: ", distancia_aninhada[("o1","r1")])
global distancia_nova = 9999999999999999999999999
global df_arvore_red = deepcopy(df_arvore_reduzida)
global df_cen_red = deepcopy(df_cenarios_reduzida)
global sol_tranporte_condicional = copy(solucao_planoTransporteCondicional)
while true
    global sol_tranporte_condicional 
    global df_arvore_red
    global df_cen_red
    global iteracao
    global mapa_arvoreOtima
    global distancia_anterior

    (arvore_red, cenarios_red, distancia_aninhada, sol_transporte_condi) = 
    atualizaArvoreDistanciaAninhada(
        df_arvore_original,
        df_cenarios_original,
        copy(df_arvore_reduzida),
        copy(df_cenarios_reduzida),
        sol_tranporte_condicional
    )
    #println(df_arvore_red)
    #println(distancia_aninhada)
    println("iter: ", iteracao, " dist: ", distancia_aninhada[("o1","r1")])
    #println(sol_tranporte_condicional)
    sol_tranporte_condicional = sol_transporte_condi
    df_cen_red =  deepcopy(cenarios_red)
    df_arvore_red = deepcopy(arvore_red)
    distancia_nova = distancia_aninhada[("o1", "r1")]
    
    
    if distancia_nova >= distancia_anterior
        break
    end
    mapa_arvoreOtima[iteracao] = (df_arvore_red, df_cen_red)
    distancia_anterior = distancia_nova
    iteracao += 1
end


println("FINALIZOU, ARVORE OTIMA, ITER: ", iteracao, " ACESSO: ", iteracao-1)
(df_arvore_otima, df_cenario_otimo) = mapa_arvoreOtima[iteracao-1]
#println("df_arvore_otima: ", df_arvore_otima)
#println("df_cenario_otimo: ", df_cenario_otimo)
if(iteracao-1 != 0)
    CSV.write(Path_red*"/arvore_ND.csv", df_arvore_otima)
    CSV.write(Path_red*"/cenarios_ND.csv", df_cenario_otimo)
end
exit(1)
#estagios_pos_otimizacao = copy(estagios)
#deleteat!(estagios_pos_otimizacao, findfirst(==(minimum(estagios_pos_otimizacao)), estagios_pos_otimizacao))
##println(estagios_pos_otimizacao)
#for estagio in sort(estagios_pos_otimizacao, rev=true)
#    nos_originais_estagios = unique(df_arvore_original[df_arvore_original[:, "PER"] .== estagio, "NO"])
#    nos_reduzido_estagio   = unique(df_arvore_reduzida[df_arvore_reduzida[:, "PER"] .== estagio, "NO"])
#    #println("estagio: ", estagio, " ORIG: ", nos_originais_estagios, " RED: ", nos_reduzido_estagio)
#    for no_orig in nos_originais_estagios
#        for no_red in nos_reduzido_estagio
#            pi = solucao_planoTransporte[("o" * string(no_orig), "r" * string(no_red))] 
#            caminho_orig = retornaListaCaminho(no_orig, df_arvore_original)
#            deleteat!(caminho_orig, findfirst(==(maximum(caminho_orig)), caminho_orig))
#            deleteat!(caminho_orig, findfirst(==(minimum(caminho_orig)), caminho_orig))
#            caminho_red =  retornaListaCaminho(no_red, df_arvore_reduzida)
#            deleteat!(caminho_red, findfirst(==(maximum(caminho_red)), caminho_red))
#            deleteat!(caminho_red, findfirst(==(minimum(caminho_red)), caminho_red))
#            pi_cond = pi
#            for est in eachindex(caminho_orig)
#                pi_pai = solucao_planoTransporte[("o" * string(caminho_orig[est]), "r" * string(caminho_red[est]))] 
#                pi_cond = pi_cond*pi_pai
#                #println(" est_otim: ", est, " orig: ", caminho_orig[est], " red: ", caminho_red[est], " pi: ", pi_pai, " pi_filho: ", pi, " cond: ", pi_cond)
#            end
#            solucao_planoTransporteCondicional[("o" * string(no_orig), "r" * string(no_red))] = pi_cond
#            #println("no_orig: ", no_orig, " no_red: ", no_red, " pi: ", pi, " pi_cond: ", pi_cond,  " caminho_orig: ", caminho_orig, " caminho_red: ", caminho_red)
#        end
#    end
#end
##println(solucao_planoTransporteCondicional)





