module PDD 

    #using JuMP, GLPK, Plots, Measures, Plots, SparseArrays, DataFrames, Dates, Statistics
    using JuMP, GLPK, DataFrames, Statistics
    #include("CapacidadeLinhas.jl")
    include("dados_entrada.jl")
    include("retornaModelo.jl")
    include("imprimePolitica.jl")
    include("exportar_resultados.jl")
    include("retornaCustoPresente.jl")
    include("inicializa_PDD.jl")

    saida_otimizacao = ResultadosOtimizacao()
    global maxIteration = 0
    global tempo_acumulado = 0
    @time begin
        for it in 1:caso.n_iter
            #println("it: ", it)
            global maxIteration = it
            start_time_iter = time()
            empty!(saida_otimizacao.df_cortes_equivalentes)
            for est in 1:caso.n_est
                #println("est: ", est)
                #println("Relizando FW - Iter ", it, " Est ", est)
                start_time = time()
                for i_no in mapa_periodos[est].nos  
                    #println("i_no: ", i_no.codigo)
                    #println("no ", i_no.codigo)  
                    etapa = "FW"  
                    otm_config = OtimizacaoConfig()   
                    global m = Model(GLPK.Optimizer)
                    retornaModelo(m, otm_config, i_no, etapa)
                    if simfinal != 1
                        if est < caso.n_est && it > 1
                            for iter in 1:caso.n_iter
                                indep_equivalente = 0
                                dict_vfvars_coef = OrderedDict{Int, Float64}()
                                for filho in i_no.filhos
                                    for uhe in lista_uhes
                                        dict_vfvars_coef[uhe.codigo] = 0
                                    end
                                end
                                for filho in i_no.filhos
                                    probabilidade_no = (dat_prob[(dat_prob.NO .== filho.codigo), "PROBABILIDADE"][1])
                                    indep_equivalente += FCF_indep[iter, filho.codigo]*probabilidade_no
                                    for uhe in lista_uhes
                                        coef_eq = FCF_coef[iter, filho.codigo, uhe.codigo]*probabilidade_no
                                        dict_vfvars_coef[uhe.codigo] += coef_eq
                                    end
                                end
                                for uhe in lista_uhes
                                    push!(saida_otimizacao.df_cortes_equivalentes, (iter = iter, est = est, noUso = i_no.codigo,  usina = uhe.nome, Indep = indep_equivalente, Coef = dict_vfvars_coef[uhe.codigo] ))
                                end
                                @constraint(m, otm_config.alpha_vars[(i_no.codigo,etapa)] - sum(otm_config.vf_vars[(i_no.codigo, uhe.nome,etapa)]*dict_vfvars_coef[uhe.codigo] for uhe in lista_uhes)   >= indep_equivalente ) #linha, coluna
                            end
                        end
                    end
                    if(est == caso.n_est && cortes_externos_fim_de_mundo == 1)
                        #print("ENTROU NOS CORTES EXTERNOS EST", est)
                        for iter_F in 1:mex_iter_est_cortes_externos
                            df_corte_iter = filter(row -> row.iter == iter_F && row.est == 4, dat_cortes_externos_fim_mundo)
                            #println(df_corte_iter)
                            indep_equivalente = df_corte_iter.Indep[1]
                            dict_vfvars_coef = OrderedDict{Int, Float64}()
                            for uhe in lista_uhes
                                linha = filter(row -> row.usina == uhe.codigo, df_corte_iter)
                                if nrow(linha) > 0
                                    dict_vfvars_coef[uhe.codigo] = linha.Coef[1]
                                else
                                    @warn "Coeficiente não encontrado para usina $(uhe.codigo) na iteração $iter_F"
                                    dict_vfvars_coef[uhe.codigo] = 0.0
                                end
                                #println("uhe: ", uhe.codigo, " coef: ", dict_vfvars_coef[uhe.codigo])
                            end
                            #println("IndeP: ", indep_equivalente)
                            @constraint(m, otm_config.alpha_vars[(i_no.codigo,etapa)] - sum(otm_config.vf_vars[(i_no.codigo, uhe.nome,etapa)]*dict_vfvars_coef[uhe.codigo] for uhe in lista_uhes)   >= indep_equivalente ) #linha, coluna
                        end
                    end
                    if simfinal == 1
                        if est < caso.n_est
                            for iter in 1:mex_iter_est
                                df_corte_iter = filter(row -> row.iter == iter && row.est == est, dat_cortes_ext)
                                #println(df_corte_iter)
                                indep_equivalente = df_corte_iter.Indep[1]
                                dict_vfvars_coef = OrderedDict{Int, Float64}()
                                for uhe in lista_uhes
                                    linha = filter(row -> row.usina == uhe.codigo, df_corte_iter)
                                    if nrow(linha) > 0
                                        dict_vfvars_coef[uhe.codigo] = linha.Coef[1]
                                    else
                                        @warn "Coeficiente não encontrado para usina $(uhe.codigo) na iteração $iter"
                                        dict_vfvars_coef[uhe.codigo] = 0.0
                                    end
                                    #println("uhe: ", uhe.codigo, " coef: ", dict_vfvars_coef[uhe.codigo])
                                end
                                #println("IndeP: ", indep_equivalente)
                                @constraint(m, alpha_vars[(i_no.codigo,etapa)] - sum(vf_vars[(i_no.codigo, uhe.nome,etapa)]*dict_vfvars_coef[uhe.codigo] for uhe in lista_uhes)   >= indep_equivalente ) #linha, coluna
                            end
                        end
                    end

                    JuMP.optimize!(m) 
                    status = JuMP.termination_status(m)
                    if status == MOI.INFEASIBLE || status == MOI.INFEASIBLE_OR_UNBOUNDED
                        #error("Optimization problem is infeasible. Stopping execution.")
                        println("Optimization problem is infeasible. Stopping execution.")
                    end
                    #if(est == 4)
                    #    println(m)
                    #end
                    imprimePolitica(saida_otimizacao, otm_config, etapa, it, i_no)

                    if est < caso.n_est
                        for filho in i_no.filhos
                            for uhe in lista_uhes
                                Vi[(filho.codigo,uhe.codigo,etapa)] = JuMP.value(otm_config.vf_vars[(i_no.codigo, uhe.nome,etapa)])
                                Vi[(filho.codigo,uhe.codigo,"BK")] = JuMP.value(otm_config.vf_vars[(i_no.codigo, uhe.nome,etapa)])
                            end
                        end
                    end
                    CustoI[(it, i_no.codigo,etapa)] = retornaCustoPresente(otm_config, i_no, etapa)
                    CustoF[(it, i_no.codigo,etapa)] = JuMP.value(otm_config.alpha_vars[(i_no.codigo,etapa)])
                end

                end_time = time()
                elapsed_time = end_time - start_time
                minutes = floor(Int, elapsed_time / 60)
                seconds = floor(Int, elapsed_time % 60)
                #println("FW - Iter ", it, " Est ", est, " Tempo: ", minutes, " min ", seconds, " sec")
            end 
            


            #println(CustoF)
            zinf = CustoI[(it, mapa_periodos[1].nos[1].codigo,"FW")] + CustoF[(it, mapa_periodos[1].nos[1].codigo,"FW")]
            nos_ultimo_estagio = mapa_periodos[caso.n_est].nos
            
            zsup = 0 
            if(cortes_externos_fim_de_mundo == 1)
                CustoFuturoFinal = 0
                for no_last_stage in nos_ultimo_estagio
                    lista = retornaListaCaminho(no_last_stage.codigo)
                    lista_probs_caminho = []
                    for no_caminho in lista
                        prob_no = (dat_prob[(dat_prob.NO .== no_caminho), "PROBABILIDADE"][1])
                        push!(lista_probs_caminho, prob_no)
                    end
                    CF_no = CustoF[(it, no_last_stage.codigo,"FW")]
                    CF_no = round(CF_no, digits = 5)
                    prob_resultante = 1
                    for prob in lista_probs_caminho
                        CF_no = CF_no*prob
                        prob_resultante = prob_resultante*prob
                    end
                    CustoFuturoFinal += CF_no
                end
                zsup = CustoFuturoFinal
            end

            for est in 1:caso.n_est 
                CI_no = 0
                for no in mapa_periodos[est].nos
                    lista = retornaListaCaminho(no.codigo)
                    lista_probs_caminho = []
                    for no_caminho in lista
                        prob_no = (dat_prob[(dat_prob.NO .== no_caminho), "PROBABILIDADE"][1])
                        push!(lista_probs_caminho, prob_no)
                    end
                    #println(lista_probs_caminho)
                    CI_no = CustoI[(it, no.codigo, "FW")]
                    #CI_no = round(CI_no, digits = 2)
                    CI_no = round(CI_no, digits = 5)
                    #println("no: ", no.codigo, " custo: ", CI_no)
                    prob_resultante = 1
                    for prob in lista_probs_caminho
                        CI_no = CI_no*prob
                        prob_resultante = prob_resultante*prob
                    end
                    #println("est: ", est, " no: ", no.codigo, " est ", est, " CI: ", CI_no, " prob: ", prob_resultante)
                    #println("no: ", no.codigo, " custo: ", CI_no)
                    zsup += CI_no
                end
                #print("est: ", est, " zsup: ", zsup)
            end
            
            zsup = round(zsup, digits=2)
            zinf = round(zinf, digits=2)
            valor_zsup = 0
            if it > 1
                valor_zsup = min(lista_zsup[it-1], zsup)
            else
                valor_zsup = zsup
            end
            gap = ((valor_zsup-zinf)/valor_zsup) 
            gap = round(gap, digits=7)
            lista_zinf[it] = zinf
            lista_zsup[it] = valor_zsup            
            lista_gap[it] = gap
            #println(" lista_zinf: ", lista_zinf )
            #println(" lista_zsup: ", lista_zsup )
            #println(" lista_gap: ", lista_gap )
            end_time_iter = time()
            elapsed_time = end_time_iter - start_time_iter
            minutes = floor(Int, elapsed_time / 60)
            seconds = floor(Int, elapsed_time % 60)
            global tempo_acumulado  # Ensure modification of the global variable
            tempo_acumulado += elapsed_time
            minutes_acumulados = floor(Int, tempo_acumulado / 60)
            seconds_acumulados = floor(Int, tempo_acumulado % 60)
            #println("BK - Iter ", it, " Est ", est, " Tempo: ", minutes, " min ", seconds, " sec")
            println("Iteração: ", it, " ZINF: ", zinf, " ZSUP: ", valor_zsup, " GAP: ", gap, " Tempo: ", minutes, " min ", seconds, "secs", 
            " Tempo Total: ", minutes_acumulados, " min ", seconds_acumulados, "secs")
            push!(saida_otimizacao.df_convergencia, (iter = it, ZINF = zinf, ZSUP = valor_zsup, GAP = gap, MIN = minutes, SEC = seconds, MIN_TOT = minutes_acumulados, SEC_TOT = seconds_acumulados))
            #if gap < 0.00001
            if gap < tolerancia || it == caso.n_iter 
                if it > caso.n_iter_min
            #if gap < 0.01 || minutes_acumulados > 120 || it == caso.n_iter
                    println("CONVERGIU")
                    break
                end
            end

            if(simfinal == 1)
                break
            end

            # ETAPA BACKWARD
            if it != caso.n_iter
                for est in caso.n_est:-1:1 
                    #println("Relizando BK - Iter ", it, " Est ", est)
                    start_time = time()
                    #println("est: ", est)
                    for i_no in mapa_periodos[est].nos 
                        #println("no: ", i_no.codigo)
                        etapa = "BK" 
                        otm_config = OtimizacaoConfig()   
                        global m = Model(GLPK.Optimizer)
                        retornaModelo(m, otm_config, i_no, etapa)
                        if est < caso.n_est 
                            for iter in 1:caso.n_iter
                                indep_equivalente = 0
                                dict_vfvars_coef = OrderedDict{Int, Float64}()
                                for filho in i_no.filhos
                                    for uhe in lista_uhes
                                        dict_vfvars_coef[uhe.codigo] = 0
                                    end
                                end
                                for filho in i_no.filhos
                                    probabilidade_no = (dat_prob[(dat_prob.NO .== filho.codigo), "PROBABILIDADE"][1])
                                    indep_equivalente += FCF_indep[iter, filho.codigo]*probabilidade_no
                                    for uhe in lista_uhes
                                        coef_eq = FCF_coef[iter, filho.codigo, uhe.codigo]*probabilidade_no
                                        dict_vfvars_coef[uhe.codigo] += coef_eq
                                    end
                                end
                                #println("i_no: ", i_no.codigo, " etapa: ", etapa)
                                @constraint(m, otm_config.alpha_vars[(i_no.codigo,etapa)] - sum(otm_config.vf_vars[(i_no.codigo, uhe.nome,etapa)]*dict_vfvars_coef[uhe.codigo] for uhe in lista_uhes)   >= indep_equivalente ) #linha, coluna
                                #for filho in i_no.filhos
                                #    @constraint(m, alpha_vars[(i_no.codigo,etapa)] - sum(vf_vars[(i_no.codigo, uhe.nome,etapa)]*FCF_coef[iter, filho.codigo, uhe.codigo] for uhe in lista_uhes)   >= FCF_indep[iter, filho.codigo] ) #linha, coluna
                                #end
                            end
                        end
                        if(est == caso.n_est && cortes_externos_fim_de_mundo == 1)
                            #print("ENTROU NOS CORTES EXTERNOS EST", est)
                            for iter_F in 1:mex_iter_est_cortes_externos
                                df_corte_iter = filter(row -> row.iter == iter_F && row.est == 4, dat_cortes_externos_fim_mundo)
                                #println(df_corte_iter)
                                indep_equivalente = df_corte_iter.Indep[1]
                                dict_vfvars_coef = OrderedDict{Int, Float64}()
                                for uhe in lista_uhes
                                    linha = filter(row -> row.usina == uhe.codigo, df_corte_iter)
                                    if nrow(linha) > 0
                                        dict_vfvars_coef[uhe.codigo] = linha.Coef[1]
                                    else
                                        @warn "Coeficiente não encontrado para usina $(uhe.codigo) na iteração $iter_F"
                                        dict_vfvars_coef[uhe.codigo] = 0.0
                                    end
                                    #println("uhe: ", uhe.codigo, " coef: ", dict_vfvars_coef[uhe.codigo])
                                end
                                #println("IndeP: ", indep_equivalente)
                                @constraint(m, otm_config.alpha_vars[(i_no.codigo,etapa)] - sum(otm_config.vf_vars[(i_no.codigo, uhe.nome,etapa)]*dict_vfvars_coef[uhe.codigo] for uhe in lista_uhes)   >= indep_equivalente ) #linha, coluna
                            end
                        end

                        JuMP.optimize!(m) 
                        #if(est == 4)
                        #    println(m)
                        #end
                        status = JuMP.termination_status(m)
                        if status == MOI.INFEASIBLE || status == MOI.INFEASIBLE_OR_UNBOUNDED
                            #error("Optimization problem is infeasible. Stopping execution.")
                            println("Optimization problem is infeasible. Stopping execution.")
                        end
                        #println("Backward: ", m)
                        #println("Solver status: ", termination_status(m))

                        if est < caso.n_est
                            for filho in i_no.filhos
                                for uhe in lista_uhes
                                    Vi[(filho.codigo,uhe.codigo,etapa)] = JuMP.value(otm_config.vf_vars[(i_no.codigo, uhe.nome,etapa)])
                                end
                            end
                        end
                        
                        probabilidade_no = (dat_prob[(dat_prob.NO .== i_no.codigo), "PROBABILIDADE"][1])
                        custo_presente = retornaCustoPresente(otm_config, i_no, etapa)
                        custo_futuro = JuMP.value(otm_config.alpha_vars[(i_no.codigo, etapa)])
                        FCF_indep[it, i_no.codigo] = FCF_indep[it, i_no.codigo] + (custo_presente + custo_futuro)#*probabilidade_no
                        for uhe in lista_uhes
                            #println("i_no.codigo: ", i_no.codigo, " uhe: ", uhe.nome, " etapa: ", etapa)
                            dual_balanco_hidrico = JuMP.shadow_price( otm_config.constraint_dict[(i_no.codigo, uhe.nome, etapa)])
                            #println("UHE: ", uhe.nome, " dual: ", dual_balanco_hidrico)
                            FCF_coef[it, i_no.codigo, uhe.codigo]  = FCF_coef[it, i_no.codigo, uhe.codigo] + dual_balanco_hidrico#*probabilidade_no
                            FCF_indep[it, i_no.codigo] = FCF_indep[it, i_no.codigo] - dual_balanco_hidrico*Vi[(i_no.codigo,uhe.codigo, etapa)]#*probabilidade_no
                            #println("est: ", est, " iter: ", it, " no: ", i_no.codigo," usi: ", uhe.codigo, " dual bal: ", dual_balanco_hidrico, " c_pres: ", custo_presente, " c_fut: ", custo_futuro, " Vi[i_no.codigo,i]: ", Vi[(i_no.codigo,uhe.codigo, etapa)], " FCF_coef: ", FCF_coef[it, i_no.codigo, uhe.codigo], " FCF_indep: ", FCF_indep[it, i_no.codigo])
                        end
                        imprimePolitica(saida_otimizacao, otm_config, "BK", it, i_no)
                        for usi in lista_uhes
                            push!(saida_otimizacao.df_cortes, (est = est, no = i_no.codigo, iter = it, usina = usi.codigo, Indep = FCF_indep[it, i_no.codigo], Coef = FCF_coef[it, i_no.codigo, usi.codigo]))
                        end
                    end
                    #exit(1)
                    end_time = time()
                    elapsed_time = end_time - start_time
                    minutes = floor(Int, elapsed_time / 60)
                    seconds = floor(Int, elapsed_time % 60)
                    #println("BK - Iter ", it, " Est ", est, " Tempo: ", minutes, " min ", seconds, " sec")
                end 

            end
        end
    end

    exportar_resultados(saida_otimizacao)

end