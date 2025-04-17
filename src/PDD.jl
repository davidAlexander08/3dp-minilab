module Main

    using JuMP, GLPK, Plots, Measures, Plots, SparseArrays, DataFrames, Dates
    #include("CapacidadeLinhas.jl")
    include("LeituraEntrada.jl")
    #conversao_m3_hm3 = (60*60)/1000000
    etapas = ["FW", "BK"]
    Vi = Dict{Tuple{Int,Int, String}, Float64}()
    for etapa in etapas
        for no in lista_total_de_nos
            for uhe in lista_uhes
                if no.codigo == 1 
                    Vi[(no.codigo, uhe.codigo, etapa)] = uhe.v0 
                else
                    Vi[(no.codigo, uhe.codigo, etapa)] = 0
                end
            end
        end
    end

    println("ENERGIA ARMAZENADA INICIAL-----")
    for sbm in lista_submercados
        EARM_INI = 0
        for uhe in cadastroUsinasHidreletricasSubmercado[sbm.codigo]
            #println("UHE: ", uhe.codigo, " EARM: ", uhe.v0*uhe.prodt)
            EARM_INI += uhe.v0*uhe.prodt
        end
        println("SUBM: ", sbm.nome, " EARMI: ", EARM_INI)
    end

    println("GERACAO TERMICA MINIMA E MAXIMA -----------")
    GTER_MIN_SIN = 0
    GTER_MAX_SIN = 0
    for sbm in lista_submercados
        GTER_MIN = 0
        GTER_MAX = 0
        for ute in cadastroUsinasTermicasSubmercado[sbm.codigo]
            #println("UHE: ", uhe.codigo, " EARM: ", uhe.v0*uhe.prodt)
            GTER_MIN += ute.gmin
            GTER_MAX += ute.gmax
        end
        global GTER_MIN_SIN += GTER_MIN  # 🔹 Adicione `global`
        global GTER_MAX_SIN += GTER_MAX  # 🔹 Adicione `global`
        println("SUBM: ", sbm.nome, " GTMIN: ", GTER_MIN,  " GTMAX: ", GTER_MAX)
    end
    println("SIN GTMIN: ", GTER_MIN_SIN,  " GTMAX: ", GTER_MAX_SIN)
    
    FCF_coef = OrderedDict{Tuple{Int, Int,Int}, Float64}()
    FCF_indep = OrderedDict{Tuple{Int,Int}, Float64}()


    for it in 1:caso.n_iter, est in 1:caso.n_est, no in lista_total_de_nos ,uhe in lista_uhes
        FCF_coef[(it, no.codigo, uhe.codigo)] = 0.0
    end

    for it in 1:caso.n_iter, no in lista_total_de_nos
        FCF_indep[(it, no.codigo)] = 0.0
    end

    lista_zinf = OrderedDict{Int, Float64}()
    lista_zsup = OrderedDict{Int, Float64}()
    lista_gap = OrderedDict{Int, Float64}()
    for it in 1:caso.n_iter
        lista_zinf[it] = 0.0
        lista_zsup[it] = 0.0
        lista_gap[it] = 0.0
    end


    CustoI = OrderedDict{Tuple{Int, Int, String}, Float64}()
    CustoF = OrderedDict{Tuple{Int, Int, String}, Float64}()
    for it in 1:caso.n_iter, no in lista_total_de_nos, etapa in etapas
        CustoI[(it, no.codigo, etapa)] = 0.0
        CustoF[(it,no.codigo, etapa)] = 0.0
    end
    df_intercambio            = DataFrame(etapa = String[], iter = Int[], est = Int[], node = Int[], prob = [], SubmercadoDE = Int[], SubmercadoPARA = Int[], Valor = Float64[])
    df_balanco_energetico_SIN = DataFrame(etapa = String[], iter = Int[], est = Int[], node = Int[], prob = [],                     Demanda = Float64[], GT = Float64[], GH = Float64[], Deficit = Float64[], Excesso = Float64[], AFL = [], Vini = Float64[], VolArm = Float64[], CustoPresente = Float64[], CustoFuturo = Float64[])
    df_balanco_energetico_SBM = DataFrame(etapa = String[], iter = Int[], est = Int[], node = Int[], prob = [], Submercado = Int[], Demanda = Float64[], GT = Float64[], GH = Float64[], Deficit = Float64[], Excesso = Float64[], AFL = [], Vini = Float64[], VolArm = Float64[], CustoPresente = Float64[], CMO = Float64[])
    df_termicas               = DataFrame(etapa = String[], iter = Int[], est = Int[], node = Int[], prob = [], Submercado = Int[], nome = String[] , usina = Int[], generation = Float64[], custo = Float64[], custoTotal = Float64[])
    df_hidreletricas          = DataFrame(etapa = String[], iter = Int[], est = Int[], node = Int[], prob = [], Submercado = Int[], nome = String[] , usina = Int[], generation = Float64[], VI = Float64[], AFL = Float64[], TURB = Float64[], VERT = Float64[], VF = Float64[])
    df_convergencia           = DataFrame(iter = Int[], ZINF = Float64[], ZSUP = Float64[])
    df_cortes                 = DataFrame(iter = Int[], est = Int[], no = Int[],  usina = Int[], Indep = Float64[], Coef = Float64[])
    df_cortes_equivalentes    = DataFrame(iter = Int[], est = Int[], noUso = Int[],  usina = String[], Indep = Float64[], Coef = Float64[])

    df_folga_vazmin           = DataFrame(etapa = String[], iter = Int[], est = Int[], node = Int[], prob = [], nome = String[], usina = Int[], Vazmin = Float64[], Qdef = Float64[], FolgaPosit = Float64[], FolgaNeg = Float64[])            


    ger_vars = Dict{Tuple{Int, Int, String}, JuMP.VariableRef}()
    gt_vars = Dict{Tuple{Int, String, String}, JuMP.VariableRef}()
    gh_vars = Dict{Tuple{Int, String, String}, JuMP.VariableRef}()
    turb_vars = Dict{Tuple{Int, String, String}, JuMP.VariableRef}()
    vert_vars = Dict{Tuple{Int, String, String}, JuMP.VariableRef}()
    vf_vars = Dict{Tuple{Int, String, String}, JuMP.VariableRef}()
    alpha_vars = Dict{Tuple{Int, String}, JuMP.VariableRef}()
    deficit_vars = Dict{Tuple{Int, String, String}, JuMP.VariableRef}()
    excesso_vars = Dict{Tuple{Int, String, String}, JuMP.VariableRef}()
    intercambio_vars = Dict{Tuple{Int, String, String, String}, JuMP.VariableRef}()
    constraint_dict = Dict{Tuple{Int, String, String}, JuMP.ConstraintRef}()
    constraint_balancDem_dict = Dict{Tuple{Int, String, String}, JuMP.ConstraintRef}()
    folga_positiva_vazmin_vars = Dict{Tuple{Int, String, String}, JuMP.VariableRef}()
    folga_negativa_vazmin_vars = Dict{Tuple{Int, String, String}, JuMP.VariableRef}()

    function retornaModelo(est, no, etapa)
        #converte_m3s_hm3 = (conversao_m3_hm3*dat_horas[(dat_horas.PERIODO .== no.periodo), "HORAS"][1])
        global m = Model(GLPK.Optimizer)
        for term in lista_utes
            gt_vars[(no.codigo, term.nome, etapa)] = @variable(m, base_name="gt_$(no.codigo)_$(term.codigo)_$(etapa)")
        end
        for uhe in lista_uhes
            gh_vars[(no.codigo, uhe.nome, etapa)] = @variable(m, base_name="gh_$(no.codigo)_$(uhe.codigo)_$(etapa)")
            turb_vars[(no.codigo, uhe.nome, etapa)] = @variable(m, base_name="turb_$(no.codigo)_$(uhe.codigo)_$(etapa)")
            vert_vars[(no.codigo, uhe.nome, etapa)] = @variable(m, base_name="vert_$(no.codigo)_$(uhe.codigo)_$(etapa)")
            vf_vars[(no.codigo, uhe.nome, etapa)] = @variable(m, base_name="vf_$(no.codigo)_$(uhe.codigo)_$(etapa)")
            folga_positiva_vazmin_vars[(no.codigo, uhe.nome, etapa)] = @variable(m, base_name="spdefmin_$(no.codigo)_$(uhe.codigo)_$(etapa)")
            folga_negativa_vazmin_vars[(no.codigo, uhe.nome, etapa)] = @variable(m, base_name="sndefmin_$(no.codigo)_$(uhe.codigo)_$(etapa)")
        end
        for sbm in lista_submercados
            deficit_vars[(no.codigo, sbm.nome, etapa)] = @variable(m, base_name="def_$(no.codigo)_$(sbm.codigo)_$(etapa)")
            excesso_vars[(no.codigo, sbm.nome, etapa)] = @variable(m, base_name="exc_$(no.codigo)_$(sbm.codigo)_$(etapa)")
            for sbm_2 in lista_submercados
                if sbm.codigo != sbm_2.codigo
                    intercambio_vars[(no.codigo, sbm.nome, sbm_2.nome, etapa)] = @variable(m, base_name="interc_$(no.codigo)_$(sbm.codigo)_$(sbm_2.codigo)_$(etapa)")
                    @constraint(m, intercambio_vars[(no.codigo, sbm.nome, sbm_2.nome, etapa)] >= 0 )
                end
            end
        end

        ## DEFINE LIMITES DE INTERCAMBIO
        if(limites_intercambio == 1)
            for sbm in lista_submercados
                for sbm_2 in lista_submercados
                    if(sbm.codigo != sbm_2.codigo)
                        #print("codigo_de: ", sbm.codigo, " codigo_para: ", sbm_2.codigo)
                        limite_intercambio = (dat_interc[(dat_interc.SUMERCADO1 .== sbm.codigo) .& (dat_interc.SUBMERCADO2 .== sbm_2.codigo), "VALOR"][1])
                        @constraint(m, intercambio_vars[(no.codigo, sbm.nome, sbm_2.nome, etapa)] <= limite_intercambio)
                    end
                end
            end
        end

        alpha_vars[(no.codigo,etapa)] = @variable(m, base_name="alpha_$(no.codigo)_$(etapa)")
        @constraint(m, alpha_vars[(no.codigo, etapa)] >= 0 )

        for uhe in lista_uhes
            @constraint(  m, gh_vars[(no.codigo, uhe.nome, etapa)] >= 0 ) 
            @constraint(  m, turb_vars[(no.codigo, uhe.nome, etapa)] >= 0 ) 
            @constraint(  m, vert_vars[(no.codigo, uhe.nome, etapa)] >= 0 ) 
            @constraint(  m, vf_vars[(no.codigo, uhe.nome, etapa)] >= 0 ) 
            @constraint(  m, folga_positiva_vazmin_vars[(no.codigo, uhe.nome, etapa)] >= 0 ) 
            @constraint(  m, folga_negativa_vazmin_vars[(no.codigo, uhe.nome, etapa)] >= 0 ) 

            @constraint(m, gh_vars[(no.codigo, uhe.nome, etapa)] - uhe.prodt*turb_vars[(no.codigo, uhe.nome, etapa)] == 0) #linha, coluna      /converte_m3s_hm3
            @constraint(m, turb_vars[(no.codigo, uhe.nome, etapa)] <= uhe.turbmax) #linha, coluna
            @constraint(m, gh_vars[(no.codigo, uhe.nome, etapa)] <= uhe.gmax ) 
            @constraint(m, vf_vars[(no.codigo, uhe.nome, etapa)] <=  uhe.vmax) #linha, coluna
            @constraint(m, vf_vars[(no.codigo, uhe.nome, etapa)] >=  uhe.vmin) #linha, coluna

            #print("est: ", est, " no: ", no.codigo, " etapa: ", etapa)
            constraint_dict[(no.codigo, uhe.nome, etapa)] = @constraint(m, 
            vf_vars[(no.codigo, uhe.nome, etapa)]
            + turb_vars[(no.codigo, uhe.nome, etapa)]
            + vert_vars[(no.codigo, uhe.nome, etapa)]
            == Vi[no.codigo,uhe.codigo, etapa] + (dat_vaz[(dat_vaz.NOME_UHE .== uhe.posto) .& (dat_vaz.NO .== no.codigo), "VAZAO"][1])
            + sum(turb_vars[(no.codigo, nomeUsiMont, etapa)] for nomeUsiMont in mapa_montantesUsina[uhe.nome])
            + sum(vert_vars[(no.codigo, nomeUsiMont, etapa)] for nomeUsiMont in mapa_montantesUsina[uhe.nome])) #linha, colun * converte_m3s_hm3
            #println(constraint_dict)
        end

        ## DEFINE RESTRICAO DE VAZAO minima, VOLUME MINIMO E VOLUME ESPERA
        for uhe in lista_uhes

            #DEFINE RESTRICOES DE VAZAO MINIMA
            #println(uhe.nome)
            if(vazao_minima == 1)
                dat_vazmin.USI = string.(dat_vazmin.USI)
                matching_rows = dat_vazmin[dat_vazmin.USI .== uhe.nome, :vazmin]
                vazao_minima_uhe = isempty(matching_rows) ? NaN : first(matching_rows)
                if !isnan(vazao_minima_uhe)
                    @constraint(m, turb_vars[(no.codigo, uhe.nome, etapa)] + vert_vars[(no.codigo, uhe.nome, etapa)] 
                    + folga_positiva_vazmin_vars[(no.codigo, uhe.nome, etapa)]
                    - folga_negativa_vazmin_vars[(no.codigo, uhe.nome, etapa)]
                     == vazao_minima_uhe)
                else
                    #println("No vazmin found for ", uhe.nome, " - Skipping constraint.")
                end
            end

            #DEFINE RESTRICOES DE VOLUME MINIMO
            if(volume_minimo == 1)
                dat_volmin.USI = string.(dat_volmin.USI)
                matching_rows = dat_volmin[dat_volmin.USI .== uhe.nome, :vmin]
                vol_min_uhe = isempty(matching_rows) ? NaN : first(matching_rows)
                vol_min_uhe = vol_min_uhe/100
                #println("vol_min_uhe: ", vol_min_uhe)
                if !isnan(vol_min_uhe)
                    @constraint(m, vf_vars[(no.codigo, uhe.nome, etapa)] >= vol_min_uhe*(uhe.vmax - uhe.vmin) + uhe.vmin)
                else
                    #println("No vazmin found for ", uhe.nome, " - Skipping constraint.")
                end
            end

            #DEFINE RESTRICOES DE   VOLUME ESPERA
            if(volume_espera == 1)
                dat_volmax.USI = string.(dat_volmax.USI)
                matching_rows = dat_volmax[dat_volmax.USI .== uhe.nome, :vmax]
                vol_max_uhe = isempty(matching_rows) ? NaN : first(matching_rows)
                vol_max_uhe = vol_max_uhe/100
                #println("vol_max_uhe: ", vol_max_uhe)
                if !isnan(vol_max_uhe) 
                    @constraint(m, vf_vars[(no.codigo, uhe.nome, etapa)] <= vol_max_uhe*uhe.vmax)
                else
                    #println("No vazmin found for ", uhe.nome, " - Skipping constraint.")
                end
            end

        end

        #write_to_file(m, "saidas/PDD/model_output.txt", format = MOI.FileFormats.FORMAT_LP)
        #exit(1)
        for term in lista_utes
            @constraint(m, gt_vars[(no.codigo, term.nome, etapa)] >= 0)
            @constraint(m, gt_vars[(no.codigo, term.nome, etapa)] <= term.gmax) #linha, coluna
            #@constraint(m, gt_vars[(no.codigo, term.nome, etapa)] >= term.gmin) #linha, coluna
        end
        for sbm in lista_submercados
            @constraint(  m, deficit_vars[(no.codigo, sbm.nome, etapa)] >= 0 ) 
            @constraint(  m, excesso_vars[(no.codigo, sbm.nome, etapa)] >= 0 ) 
        end
        
        @objective(m, Min, sum(term.custo_geracao * gt_vars[(no.codigo, term.nome, etapa)] for term in lista_utes) 
        + sum(0.01 * vert_vars[(no.codigo, uhe.nome, etapa)] for uhe in lista_uhes)
        + sum(penalidVazMin * folga_positiva_vazmin_vars[(no.codigo, uhe.nome, etapa)] for uhe in lista_uhes)
        + sum(0.01 * intercambio_vars[(no.codigo, sbm.nome, sbm_2.nome, etapa)] for sbm in lista_submercados, sbm_2 in lista_submercados if sbm != sbm_2)
        + sum(sbm.deficit_cost * deficit_vars[(no.codigo, sbm.nome, etapa)] for sbm in lista_submercados)
        + alpha_vars[(no.codigo, etapa)])
        
        for sbm in lista_submercados
            constraint_balancDem_dict[(no.codigo, sbm.nome, etapa)] = @constraint(  m, sum(gh_vars[(no.codigo, uhe.nome, etapa)] for uhe in cadastroUsinasHidreletricasSubmercado[sbm.codigo]) 
            + sum(gt_vars[(no.codigo, term.nome, etapa)] for term in cadastroUsinasTermicasSubmercado[sbm.codigo]) 
            + sum(intercambio_vars[(no.codigo, sbm_2.nome, sbm.nome, etapa)] for sbm_2 in lista_submercados if sbm != sbm_2)
            - sum(intercambio_vars[(no.codigo, sbm.nome, sbm_2.nome, etapa)] for sbm_2 in lista_submercados if sbm != sbm_2)
            + deficit_vars[(no.codigo, sbm.nome, etapa)] 
            #- excesso_vars[(no.codigo, sbm.nome, etapa)] 
            == sbm.demanda[est]   )
        end
        return m
    end

    function imprimePolitica(etapa, est, it, no)
        #println("ETAPA: ", etapa, " est: ", est, " it: ", it, " miniIter: ", miniIter, " no: ", no.codigo)
        #converte_m3s_hm3 = (conversao_m3_hm3*dat_horas[(dat_horas.PERIODO .== no.periodo), "HORAS"][1])
        probabilidadeNo = (dat_prob[(dat_prob.NO .== no.codigo), "PROBABILIDADE"][1])
        GeracaoHidreletricaSIN = 0
        GeracaoTermicaSIN = 0
        DemandaTotalSIN = 0
        DeficitSIN = 0
        excesso_SIN = 0
        CustoPresenteSIN = 0
        VolumeArmazenadoSIN = 0
        AfluenciaSIN = 0
        VolumeArmazenadoInicialSIN = 0
        for sbm in lista_submercados
            GeracaoHidreletricaTotal = 0
            VolumeArmazenadoTotal = 0
            AfluenciaTotal = 0
            VolumeArmazenadoInicialTotal = 0
            GeracaoTermicaTotal = 0
            for term in cadastroUsinasTermicasSubmercado[sbm.codigo]
                geracao = JuMP.value(gt_vars[(no.codigo, term.nome, etapa)])
                push!(df_termicas, (etapa = etapa, iter = it, est = est, node = no.codigo, prob = probabilidadeNo, Submercado = sbm.codigo, nome = term.nome, usina = term.codigo, generation = round(geracao, digits = 1) , custo = term.custo_geracao, custoTotal = round(geracao, digits = 1)*term.custo_geracao))
                GeracaoTermicaTotal += geracao
                GeracaoTermicaSIN += geracao
            end
            for uhe in cadastroUsinasHidreletricasSubmercado[sbm.codigo]
                geracao = JuMP.value(gh_vars[(no.codigo, uhe.nome, etapa)])
                turbinamento = JuMP.value(turb_vars[(no.codigo, uhe.nome, etapa)]) 
                vertimento = JuMP.value(vert_vars[(no.codigo, uhe.nome, etapa)]) 
                volumeFinal = JuMP.value(vf_vars[(no.codigo, uhe.nome, etapa)]) 
                volumeInicial = Vi[(no.codigo, uhe.codigo, etapa)]
                Afluencia = (dat_vaz[(dat_vaz.NOME_UHE .== uhe.posto) .& (dat_vaz.NO .== no.codigo), "VAZAO"][1])
                if(vazao_minima == 1)

                    matching_rows = dat_vazmin[dat_vazmin.USI .== uhe.nome, :vazmin]
                    vazao_minima_uhe = isempty(matching_rows) ? NaN : first(matching_rows)
                    if !isnan(vazao_minima_uhe)
                        folga_positiva_vazmin = JuMP.value(folga_positiva_vazmin_vars[(no.codigo, uhe.nome, etapa)])
                        folga_negativa_vazmin = JuMP.value(folga_negativa_vazmin_vars[(no.codigo, uhe.nome, etapa)])
                    else
                        vazao_minima_uhe = 0
                        folga_positiva_vazmin = 0
                        folga_negativa_vazmin = 0
                    end
                end

                push!(df_hidreletricas, (etapa = etapa, iter = it, est = est, node = no.codigo, prob = probabilidadeNo, Submercado = sbm.codigo, nome = uhe.nome, usina = uhe.codigo, generation = geracao,
                                VI = Vi[(no.codigo,uhe.codigo, etapa)], 
                                AFL = (dat_vaz[(dat_vaz.NOME_UHE .== uhe.posto) .& (dat_vaz.NO .== no.codigo), "VAZAO"][1]),
                                TURB = turbinamento, 
                                VERT = vertimento, 
                                VF = volumeFinal))
                if(vazao_minima == 1)
                    push!(df_folga_vazmin, (etapa = etapa, iter = it, est = est, node = no.codigo, prob = probabilidadeNo, 
                    nome = uhe.nome, usina = uhe.codigo, Vazmin = vazao_minima_uhe, Qdef = turbinamento + vertimento, 
                    FolgaPosit = folga_positiva_vazmin, FolgaNeg = folga_negativa_vazmin ))
                end

                GeracaoHidreletricaTotal += geracao
                VolumeArmazenadoTotal += volumeFinal
                AfluenciaTotal += Afluencia
                VolumeArmazenadoInicialTotal += volumeInicial
                GeracaoHidreletricaSIN += geracao
                VolumeArmazenadoSIN += volumeFinal
                AfluenciaSIN += Afluencia
                VolumeArmazenadoInicialSIN += volumeInicial
            end
            custo_presente = 0
            for term in cadastroUsinasTermicasSubmercado[sbm.codigo]
                custo_presente += JuMP.value.(gt_vars[(no.codigo, term.nome, etapa)])*term.custo_geracao
            end
            def = 0
            excesso_sbm = 0
            def = JuMP.value(deficit_vars[(no.codigo, sbm.nome, etapa)])
            excesso_sbm = JuMP.value(excesso_vars[(no.codigo, sbm.nome, etapa)])
            custo_presente += def*sbm.deficit_cost
            DemandaTotalSIN += sbm.demanda[est]
            DeficitSIN += def
            excesso_SIN += excesso_sbm
            CustoPresenteSIN += custo_presente
            valor_CMO = -JuMP.shadow_price( constraint_balancDem_dict[(no.codigo, sbm.nome, etapa)])
            push!(df_balanco_energetico_SBM,  (etapa = etapa, iter = it, est = est, node = no.codigo, prob = probabilidadeNo, Submercado = sbm.codigo, Demanda = sbm.demanda[est], GT = GeracaoTermicaTotal, GH = GeracaoHidreletricaTotal, AFL = AfluenciaTotal, Vini = VolumeArmazenadoInicialTotal, VolArm = VolumeArmazenadoTotal, Deficit = def, Excesso = excesso_sbm, CustoPresente = custo_presente, CMO = round(valor_CMO, digits = 2)))
            for sbm_2 in lista_submercados
                if sbm.codigo != sbm_2.codigo
                    interc = JuMP.value(intercambio_vars[(no.codigo, sbm.nome, sbm_2.nome, etapa)])
                    push!(df_intercambio,  (etapa = etapa, iter = it, est = est, node = no.codigo, prob = probabilidadeNo, SubmercadoDE = sbm.codigo, SubmercadoPARA = sbm_2.codigo, Valor = round(interc, digits = 2)))
                end
            end
        end
        push!(df_balanco_energetico_SIN,  (etapa = etapa, iter = it, est = est, node = no.codigo, prob = probabilidadeNo, Demanda = DemandaTotalSIN, GT = GeracaoTermicaSIN, GH = GeracaoHidreletricaSIN, Deficit = DeficitSIN, Excesso = excesso_SIN, AFL = AfluenciaSIN, Vini = VolumeArmazenadoInicialSIN, VolArm = VolumeArmazenadoSIN, CustoPresente = CustoPresenteSIN, CustoFuturo = JuMP.value(alpha_vars[no.codigo, etapa])))
    end


    function retornaCustoPresente(est, no,etapa)
        custo_presente = 0
        for term in lista_utes
            geracao = JuMP.value(gt_vars[(no.codigo, term.nome, etapa)])
            custo_presente += geracao*term.custo_geracao
        end
        for hydro in lista_uhes 
            vertimento = JuMP.value(vert_vars[(no.codigo, hydro.nome, etapa)])
            custo_presente += vertimento*0.01
            if(vazao_minima == 1)
                penalidadePositivaVazmin = JuMP.value(folga_positiva_vazmin_vars[(no.codigo, hydro.nome, etapa)])
                custo_presente += penalidadePositivaVazmin*penalidVazMin
            end

        end

        for sbm in lista_submercados
            custo_presente += JuMP.value(deficit_vars[(no.codigo, sbm.nome, etapa)])*sbm.deficit_cost
        end


        return custo_presente
    end

    println("NUMERO DE USINAS HIDRELETRICAS: ", length(lista_uhes))
    println("NUMERO DE USINAS TERMICAS: ", length(lista_utes))

    global tempo_acumulado = 0
    @time begin
        for it in 1:caso.n_iter
            start_time_iter = time()
            empty!(df_cortes_equivalentes)
            for est in 1:caso.n_est
                #println("Relizando FW - Iter ", it, " Est ", est)
                start_time = time()
                for i_no in mapa_periodos[est].nos  
                    #println("no ", i_no.codigo)  
                    etapa = "FW"     
                    m = retornaModelo(est,i_no, etapa)
                    if est < caso.n_est && it > 1
                        #for iter in 1:caso.n_iter
                        #    for filho in i_no.filhos
                        #        @constraint(m, alpha_vars[(i_no.codigo,etapa)] - sum(vf_vars[(i_no.codigo, uhe.nome,etapa)]*FCF_coef[iter, filho.codigo, uhe.codigo] for uhe in lista_uhes)   >= FCF_indep[iter, filho.codigo] ) #linha, coluna
                        #    end
                        #
                        
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
                                push!(df_cortes_equivalentes, (iter = iter, est = est, noUso = i_no.codigo,  usina = uhe.nome, Indep = indep_equivalente, Coef = dict_vfvars_coef[uhe.codigo] ))
                            end


                            @constraint(m, alpha_vars[(i_no.codigo,etapa)] - sum(vf_vars[(i_no.codigo, uhe.nome,etapa)]*dict_vfvars_coef[uhe.codigo] for uhe in lista_uhes)   >= indep_equivalente ) #linha, coluna
                            #for filho in i_no.filhos
                            #    @constraint(m, alpha_vars[(i_no.codigo,etapa)] - sum(vf_vars[(i_no.codigo, uhe.nome,etapa)]*FCF_coef[iter, filho.codigo, uhe.codigo] for uhe in lista_uhes)   >= FCF_indep[iter, filho.codigo] ) #linha, coluna
                            #end
                        end
                    end

                    JuMP.optimize!(m) 
                    status = JuMP.termination_status(m)
                    if status == MOI.INFEASIBLE || status == MOI.INFEASIBLE_OR_UNBOUNDED
                        #error("Optimization problem is infeasible. Stopping execution.")
                        println("Optimization problem is infeasible. Stopping execution.")
                    end
                    #println(m) 
                    imprimePolitica(etapa, est, it, i_no)

                    if est < caso.n_est
                        for filho in i_no.filhos
                            for uhe in lista_uhes
                                Vi[(filho.codigo,uhe.codigo,etapa)] = JuMP.value(vf_vars[(i_no.codigo, uhe.nome,etapa)])
                                Vi[(filho.codigo,uhe.codigo,"BK")] = JuMP.value(vf_vars[(i_no.codigo, uhe.nome,etapa)])
                            end
                        end
                    end
                    CustoI[(it, i_no.codigo,etapa)] = retornaCustoPresente(est, i_no, etapa)
                    CustoF[(it, i_no.codigo,etapa)] = JuMP.value(alpha_vars[(i_no.codigo,etapa)])
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
            push!(df_convergencia, (iter = it, ZINF = zinf, ZSUP = valor_zsup))
            if gap < 0.00001
                println("CONVERGIU")
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
                        m = retornaModelo(est, i_no, etapa)
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
                                @constraint(m, alpha_vars[(i_no.codigo,etapa)] - sum(vf_vars[(i_no.codigo, uhe.nome,etapa)]*dict_vfvars_coef[uhe.codigo] for uhe in lista_uhes)   >= indep_equivalente ) #linha, coluna
                                #for filho in i_no.filhos
                                #    @constraint(m, alpha_vars[(i_no.codigo,etapa)] - sum(vf_vars[(i_no.codigo, uhe.nome,etapa)]*FCF_coef[iter, filho.codigo, uhe.codigo] for uhe in lista_uhes)   >= FCF_indep[iter, filho.codigo] ) #linha, coluna
                                #end
                            end
                        end

                        JuMP.optimize!(m) 
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
                                    Vi[(filho.codigo,uhe.codigo,etapa)] = JuMP.value(vf_vars[(i_no.codigo, uhe.nome,etapa)])
                                end
                            end
                        end
                        
                        probabilidade_no = (dat_prob[(dat_prob.NO .== i_no.codigo), "PROBABILIDADE"][1])
                        custo_presente = retornaCustoPresente(est, i_no, etapa)
                        custo_futuro = JuMP.value(alpha_vars[(i_no.codigo, etapa)])
                        FCF_indep[it, i_no.codigo] = FCF_indep[it, i_no.codigo] + (custo_presente + custo_futuro)#*probabilidade_no
                        for uhe in lista_uhes
                            #println("i_no.codigo: ", i_no.codigo, " uhe: ", uhe.nome, " etapa: ", etapa)
                            dual_balanco_hidrico = JuMP.shadow_price( constraint_dict[(i_no.codigo, uhe.nome, etapa)])
                            #println("UHE: ", uhe.nome, " dual: ", dual_balanco_hidrico)
                            FCF_coef[it, i_no.codigo, uhe.codigo]  = FCF_coef[it, i_no.codigo, uhe.codigo] + dual_balanco_hidrico#*probabilidade_no
                            FCF_indep[it, i_no.codigo] = FCF_indep[it, i_no.codigo] - dual_balanco_hidrico*Vi[(i_no.codigo,uhe.codigo, etapa)]#*probabilidade_no
                            #println("est: ", est, " iter: ", it, " no: ", i_no.codigo," usi: ", uhe.codigo, " dual bal: ", dual_balanco_hidrico, " c_pres: ", custo_presente, " c_fut: ", custo_futuro, " Vi[i_no.codigo,i]: ", Vi[(i_no.codigo,uhe.codigo, etapa)], " FCF_coef: ", FCF_coef[it, i_no.codigo, uhe.codigo], " FCF_indep: ", FCF_indep[it, i_no.codigo])
                        end
                        imprimePolitica("BK", est, it, i_no)
                        for usi in lista_uhes
                            push!(df_cortes, (est = est, no = i_no.codigo, iter = it, usina = usi.codigo, Indep = FCF_indep[it, i_no.codigo], Coef = FCF_coef[it, i_no.codigo, usi.codigo]))
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
    #fig = plot(1:caso.n_iter, [zinf,zsup],size=(800,400), margin=10mm)
    #savefig(fig, "myplot.png")

    df_balanco_energetico_SBM_fw = df_balanco_energetico_SBM[(df_balanco_energetico_SBM.etapa .== "FW"), :]
    df_balanco_energetico_SBM_bk = df_balanco_energetico_SBM[(df_balanco_energetico_SBM.etapa .== "BK"), :]
    max_iter = maximum(df_balanco_energetico_SBM.iter)
    df_balanco_energetico_SBM_sf = df_balanco_energetico_SBM[(df_balanco_energetico_SBM.etapa .== "FW") .& (df_balanco_energetico_SBM.iter .== max_iter), :]

    df_balanco_energetico_SIN_fw = df_balanco_energetico_SIN[(df_balanco_energetico_SIN.etapa .== "FW"), :]
    df_balanco_energetico_SIN_bk = df_balanco_energetico_SIN[(df_balanco_energetico_SIN.etapa .== "BK"), :]
    df_balanco_energetico_SIN_sf = df_balanco_energetico_SIN[(df_balanco_energetico_SIN.etapa .== "FW") .& (df_balanco_energetico_SIN.iter .== max_iter), :]

    df_intercambio_SIN_fw = df_intercambio[(df_intercambio.etapa .== "FW"), :]
    df_intercambio_SIN_bk = df_intercambio[(df_intercambio.etapa .== "BK"), :]
    df_intercambio_SIN_sf = df_intercambio[(df_intercambio.etapa .== "FW") .& (df_intercambio.iter .== max_iter), :]

    df_folga_vazmin_fw = df_folga_vazmin[(df_folga_vazmin.etapa .== "FW"), :]
    df_folga_vazmin_bk = df_folga_vazmin[(df_folga_vazmin.etapa .== "BK"), :]
    df_folga_vazmin_sf = df_folga_vazmin[(df_folga_vazmin.etapa .== "FW") .& (df_folga_vazmin.iter .== max_iter), :]

    df_termicas_fw = df_termicas[(df_termicas.etapa .== "FW"), :]
    df_termicas_bk = df_termicas[(df_termicas.etapa .== "BK"), :]
    df_termicas_sf = df_termicas[(df_termicas.etapa .== "FW") .&& (df_termicas.iter .== max_iter), :]

    df_hidreletricas_fw = df_hidreletricas[(df_hidreletricas.etapa .== "FW"), :]
    df_hidreletricas_bk = df_hidreletricas[(df_hidreletricas.etapa .== "BK"), :]
    df_hidreletricas_sf = df_hidreletricas[(df_hidreletricas.etapa .== "FW") .&& (df_hidreletricas.iter .== max_iter), :]


    df_per_balanco_energetico = DataFrame(etapa = String[], iter = Int[],  est = Int[], Demanda = Float64[], GT = Float64[], GH = Float64[], Deficit = Float64[], Excesso =Float64[], AFL = Float64[], Vini = Float64[], VolArm = Float64[], CustoPresente = Float64[], CustoFuturo = Float64[])
    for est_value in unique(df_balanco_energetico_SIN.est)
        #println("est: ", est_value)
        subset = df_balanco_energetico_SIN_sf[df_balanco_energetico_SIN_sf.est .== est_value, :]
        for iteracao in unique(subset.iter)
            subsubset = subset[(subset.iter .== iteracao), :]
            ProbGT = 0
            ProbVarm = 0
            ProbAFL = 0
            ProbVini = 0
            ProbGH = 0
            ProbDeficit = 0
            ProbCustoPresente = 0
            ProbCustoFuturo = 0
            ProbExcesso = 0
            Demanda = 0
            #println("mapaProbCondicionalNo: ", mapaProbCondicionalNo)
            for no in unique(subsubset.node)
                ProbGT += (subsubset[(subsubset.node .== no), "GT"][1])*(mapaProbCondicionalNo[no])
                ProbGH += (subsubset[(subsubset.node .== no), "GH"][1])*(mapaProbCondicionalNo[no])
                ProbAFL += (subsubset[(subsubset.node .== no), "AFL"][1])*(mapaProbCondicionalNo[no])
                ProbVarm += (subsubset[(subsubset.node .== no), "VolArm"][1])*(mapaProbCondicionalNo[no])
                ProbVini += (subsubset[(subsubset.node .== no), "Vini"][1])*(mapaProbCondicionalNo[no])
                ProbDeficit += (subsubset[(subsubset.node .== no), "Deficit"][1])*(mapaProbCondicionalNo[no])
                ProbExcesso += (subsubset[(subsubset.node .== no), "Excesso"][1])*(mapaProbCondicionalNo[no])
                ProbCustoPresente += (subsubset[(subsubset.node .== no), "CustoPresente"][1])*(mapaProbCondicionalNo[no])
                ProbCustoFuturo += (subsubset[(subsubset.node .== no), "CustoFuturo"][1])*(mapaProbCondicionalNo[no])
                Demanda += (subsubset[(subsubset.node .== no), "Demanda"][1])*(mapaProbCondicionalNo[no])
                #println("ProbGT: ", ProbGT, " No: ", no, " GT: ", (subsubset[(subsubset.node .== no), "GT"][1]), " prob: ", (mapaProbCondicionalNo[no]))
            end
            
            dem = (subset[(subset.est .== est_value), "Demanda"][1])
            push!(df_per_balanco_energetico, (etapa = "SF", iter = iteracao, est = est_value, Demanda = dem, GT = round(ProbGT, digits = 0), GH = round(ProbGH, digits = 0), Deficit = round(ProbDeficit, digits = 0), Excesso = round(ProbExcesso,digits = 0), AFL = round(ProbAFL, digits= 0), Vini = round(ProbVini, digits = 0), VolArm = round(ProbVarm, digits = 0), CustoPresente = round(ProbCustoPresente, digits = 0) , CustoFuturo = round(ProbCustoFuturo, digits = 0)))
        end
    end
    df_per_balanco_energetico = sort(df_per_balanco_energetico, :iter)
    #println(df_per_balanco_energetico)
    show(IOContext(stdout, :compact => false), df_per_balanco_energetico)

    output_dir_oper = dados_saida*"/saidas/PDD/oper"
    mkpath(output_dir_oper)
    CSV.write(output_dir_oper*"/balanco_energetico_SBM_fw.csv", df_balanco_energetico_SBM_fw)
    CSV.write(output_dir_oper*"/balanco_energetico_SBM_bk.csv", df_balanco_energetico_SBM_bk)
    CSV.write(output_dir_oper*"/balanco_energetico_SBM_sf.csv", df_balanco_energetico_SBM_sf)
    CSV.write(output_dir_oper*"/balanco_energetico_SIN_fw.csv", df_balanco_energetico_SIN_fw)
    CSV.write(output_dir_oper*"/balanco_energetico_SIN_bk.csv", df_balanco_energetico_SIN_bk)
    CSV.write(output_dir_oper*"/balanco_energetico_SIN_sf.csv", df_balanco_energetico_SIN_sf)
    CSV.write(output_dir_oper*"/intercambio_SIN_fw.csv", df_intercambio_SIN_fw)
    CSV.write(output_dir_oper*"/intercambio_SIN_bk.csv", df_intercambio_SIN_bk)
    CSV.write(output_dir_oper*"/intercambio_SIN_sf.csv", df_intercambio_SIN_sf)
    CSV.write(output_dir_oper*"/termicas_fw.csv", df_termicas_fw)
    CSV.write(output_dir_oper*"/termicas_bk.csv", df_termicas_bk)
    CSV.write(output_dir_oper*"/termicas_sf.csv", df_termicas_sf)
    CSV.write(output_dir_oper*"/hidreletricas_fw.csv", df_hidreletricas_fw)
    CSV.write(output_dir_oper*"/hidreletricas_bk.csv", df_hidreletricas_bk)
    CSV.write(output_dir_oper*"/hidreletricas_sf.csv", df_hidreletricas_sf)
    CSV.write(output_dir_oper*"/folgaVazmin_fw.csv", df_folga_vazmin_fw)
    CSV.write(output_dir_oper*"/folgaVazmin_bk.csv", df_folga_vazmin_bk)
    CSV.write(output_dir_oper*"/folgaVazmin_sf.csv", df_folga_vazmin_sf)
    CSV.write(output_dir_oper*"/convergencia.csv", df_convergencia)
    CSV.write(output_dir_oper*"/df_cortes.csv", df_cortes)
    CSV.write(output_dir_oper*"/df_cortes_equivalentes.csv", df_cortes_equivalentes)


end