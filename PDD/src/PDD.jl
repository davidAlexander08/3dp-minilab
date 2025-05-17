module PDD 

    #using JuMP, GLPK, Plots, Measures, Plots, SparseArrays, DataFrames, Dates, Statistics
    using JuMP, GLPK, DataFrames, Statistics
    #include("CapacidadeLinhas.jl")
    include("LeituraEntrada.jl")
    conversao_m3_to_hm3 = 60*60/1000000
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

    #println("ENERGIA ARMAZENADA INICIAL-----")
    #print("est: ", est)
    horas_periodo = dat_horas[(dat_horas.PERIODO .== 1), "HORAS"][1]
    
    #println("est: ", est, " horas_periodo: ", horas_periodo)
    converte_m3s_hm3 = horas_periodo*conversao_m3_to_hm3
    global EARM_INI_SIN = 0
    global EARM_MIN_SIN = 0
    global EARM_MAX_SIN = 0
    global V_MIN_SIN = 0
    global V_INI_SIN = 0
    global V_MAX_SIN = 0
    for sbm in lista_submercados
        EARM_INI = 0
        EARM_MAX = 0
        EARM_MIN = 0
        VOL_INI = 0
        VOL_MAX = 0
        VOL_MIN = 0
        for uhe in cadastroUsinasHidreletricasSubmercado[sbm.codigo]
            #println("UHE: ", uhe.codigo, " EARM: ", uhe.v0*uhe.prodt)
            EARM_INI += uhe.v0*mapaUsinaProdtAcum[uhe.nome]/converte_m3s_hm3
            EARM_MAX += uhe.vmax*mapaUsinaProdtAcum[uhe.nome]/converte_m3s_hm3
            EARM_MIN += uhe.vmin*mapaUsinaProdtAcum[uhe.nome]/converte_m3s_hm3
            VOL_INI  += uhe.v0
            VOL_MAX  += uhe.vmax
            VOL_MIN  += uhe.vmin
        end
        global EARM_INI_SIN += EARM_INI
        global EARM_MAX_SIN += EARM_MAX
        global EARM_MIN_SIN += EARM_MIN
        global V_MIN_SIN += VOL_MIN
        global V_INI_SIN += VOL_INI
        global V_MAX_SIN += VOL_MAX
        #println("SUBM: ", sbm.nome, " EARMI: ", EARM_INI)
    end
    println("SIN EARM_INI_SIN: ", EARM_INI_SIN,  " EARM_MAX_SIN: ", EARM_MAX_SIN, " EARM MIN: ", EARM_MIN_SIN)
    println("SIN V_INI_SIN: ", V_INI_SIN,  " V_MAX_SIN: ", V_MAX_SIN, " V_MIN_SIN: ", V_MIN_SIN)

    #println("GERACAO TERMICA MINIMA E MAXIMA -----------")
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
        #println("SUBM: ", sbm.nome, " GTMIN: ", GTER_MIN,  " GTMAX: ", GTER_MAX)
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
    df_balanco_energetico_SIN = DataFrame(etapa = String[], iter = Int[], est = Int[], node = Int[], prob = [],                     Demanda = Float64[], GT = Float64[], GH = Float64[], Deficit = Float64[], Excesso = Float64[], AFL = [], Vini = Float64[], VolArm = Float64[], Earm = Float64[], Turb = Float64[], Vert = Float64[], CustoPresente = Float64[], CustoFuturo = Float64[])
    df_balanco_energetico_SBM = DataFrame(etapa = String[], iter = Int[], est = Int[], node = Int[], prob = [], Submercado = Int[], Demanda = Float64[], GT = Float64[], GH = Float64[], Deficit = Float64[], Excesso = Float64[], AFL = [], Vini = Float64[], VolArm = Float64[], Earm = Float64[], Turb = Float64[], Vert = Float64[], CustoPresente = Float64[], CMO = Float64[])
    
    df_termicas               = DataFrame(etapa = String[], iter = Int[], est = Int[], node = Int[], prob = [], Submercado = Int[], nome = String[] , usina = Int[], generation = Float64[], custo = Float64[], custoTotal = Float64[], GerMin = Float64[], GerMax = Float64[])
    df_hidreletricas          = DataFrame(etapa = String[], iter = Int[], est = Int[], node = Int[], prob = [], Submercado = Int[], nome = String[] , usina = Int[], generation = Float64[], VI = Float64[], AFL = Float64[], TURB = Float64[], VERT = Float64[], VF = Float64[])
    df_convergencia           = DataFrame(iter = Int[], ZINF = Float64[], ZSUP = Float64[], GAP = Float64[], MIN = Float64[], SEC = Float64[], MIN_TOT = Float64[], SEC_TOT = Float64[])
    df_cortes                 = DataFrame(iter = Int[], est = Int[], no = Int[],  usina = Int[], Indep = Float64[], Coef = Float64[])
    df_cortes_equivalentes    = DataFrame(iter = Int[], est = Int[], noUso = Int[],  usina = String[], Indep = Float64[], Coef = Float64[])
	df_parcelasCustoPresente = DataFrame(etapa = String[], iter = Int[], est = Int[], node = Int[], prob = [], Submercado = Int[], usina = String[], codigo = Int[], geracao = Float64[], Custo = Float64[], CustoPresente = Float64[], CustoPresenteAcum = Float64[])
    df_folga_vazmin           = DataFrame(etapa = String[], iter = Int[], est = Int[], node = Int[], prob = [], nome = String[], usina = Int[], Vazmin = Float64[], Qdef = Float64[], FolgaPosit = Float64[], FolgaNeg = Float64[])            
    df_folga_MetaVol          = DataFrame(etapa = String[], iter = Int[], est = Int[], node = Int[], prob = [], nome = String[], usina = Int[], Meta = Float64[], VolF = Float64[], FolgaPosit = Float64[], FolgaNeg = Float64[])            


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
    folga_positiva_volFimMundo_vars = Dict{Tuple{Int, String, String}, JuMP.VariableRef}()
    folga_negativa_volFimMundo_vars = Dict{Tuple{Int, String, String}, JuMP.VariableRef}()
    function retornaModelo(est, no, etapa)
        #print("est: ", est)
        horas_periodo = dat_horas[(dat_horas.PERIODO .== est), "HORAS"][1]
        
        #println("est: ", est, " horas_periodo: ", horas_periodo)
        converte_m3s_hm3 = horas_periodo*conversao_m3_to_hm3
        #println("est: ", est, " converte: ", converte_m3s_hm3)
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

            folga_positiva_volFimMundo_vars[(no.codigo, uhe.nome, etapa)] = @variable(m, base_name="sPVfmundo_$(no.codigo)_$(uhe.codigo)_$(etapa)")
            folga_negativa_volFimMundo_vars[(no.codigo, uhe.nome, etapa)] = @variable(m, base_name="sPVfmundo_$(no.codigo)_$(uhe.codigo)_$(etapa)")
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
            
            @constraint(  m, folga_positiva_volFimMundo_vars[(no.codigo, uhe.nome, etapa)] >= 0 ) 
            @constraint(  m, folga_negativa_volFimMundo_vars[(no.codigo, uhe.nome, etapa)] >= 0 ) 

            @constraint(m, gh_vars[(no.codigo, uhe.nome, etapa)] - uhe.prodt*turb_vars[(no.codigo, uhe.nome, etapa)] == 0) #linha, coluna      /converte_m3s_hm3
            @constraint(m, turb_vars[(no.codigo, uhe.nome, etapa)] <= uhe.turbmax) #linha, coluna
            @constraint(m, gh_vars[(no.codigo, uhe.nome, etapa)] <= uhe.gmax ) 
            @constraint(m, vf_vars[(no.codigo, uhe.nome, etapa)] <=  uhe.vmax) #linha, coluna
            @constraint(m, vf_vars[(no.codigo, uhe.nome, etapa)] >=  uhe.vmin) #linha, coluna

            #print("est: ", est, " no: ", no.codigo, " etapa: ", etapa)
            vazao_afluente = 0
            if(uhe.posto != 999)
                vazao_afluente = (dat_vaz[(dat_vaz.NOME_UHE .== uhe.posto) .& (dat_vaz.NO .== no.codigo), "VAZAO"][1])
            else
                vazao_afluente = 0
            end
            
            #############BALANCO HIDRICO


            #constraint_dict[(no.codigo, uhe.nome, etapa)] = @constraint(m, 
            #vf_vars[(no.codigo, uhe.nome, etapa)]
            #+ turb_vars[(no.codigo, uhe.nome, etapa)]
            #+ vert_vars[(no.codigo, uhe.nome, etapa)] == Vi[no.codigo,uhe.codigo, etapa] + (vazao_afluente)
            #+ sum(turb_vars[(no.codigo, nomeUsiMont, etapa)] for nomeUsiMont in mapa_montantesUsina[uhe.nome])
            #+ sum(vert_vars[(no.codigo, nomeUsiMont, etapa)] for nomeUsiMont in mapa_montantesUsina[uhe.nome])) #linha, colun * converte_m3s_hm3
            #println(constraint_dict)
            constraint_dict[(no.codigo, uhe.nome, etapa)] = @constraint(m, 
            vf_vars[(no.codigo, uhe.nome, etapa)]
            + turb_vars[(no.codigo, uhe.nome, etapa)]*converte_m3s_hm3
            + vert_vars[(no.codigo, uhe.nome, etapa)]*converte_m3s_hm3
            == Vi[no.codigo,uhe.codigo, etapa] + (vazao_afluente)*converte_m3s_hm3
            + sum(turb_vars[(no.codigo, nomeUsiMont, etapa)]*converte_m3s_hm3 for nomeUsiMont in mapa_montantesUsina[uhe.nome])
            + sum(vert_vars[(no.codigo, nomeUsiMont, etapa)]*converte_m3s_hm3 for nomeUsiMont in mapa_montantesUsina[uhe.nome])) #linha, colun * converte_m3s_hm3
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

            if restricaoVolumeFimMundo == 1 && est == caso.n_est
                #println(" est == caso.n_est ",  caso.n_est)
                dat_meta_armazenamento.USI = string.(dat_meta_armazenamento.USI)
                #print(dat_meta_armazenamento)
                matching_rows = dat_meta_armazenamento[dat_meta_armazenamento.USI .== uhe.nome, :meta]
                #print(matching_rows)
                vol_meta = isempty(matching_rows) ? NaN : first(matching_rows)
                vol_meta = vol_meta/100
                #println("volmeta: ", vol_meta, " uhe.vmax: ", uhe.vmax, " uhe.vmin: ", uhe.vmin)
                if !isnan(vol_meta)
                    @constraint(m, vf_vars[(no.codigo, uhe.nome, etapa)] 
                    + folga_positiva_volFimMundo_vars[(no.codigo, uhe.nome, etapa)]
                    - folga_negativa_volFimMundo_vars[(no.codigo, uhe.nome, etapa)]
                    ==  (uhe.vmax - uhe.vmin)*vol_meta ) #linha, coluna
                    #print(m)
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
            @constraint(m, gt_vars[(no.codigo, term.nome, etapa)] >= term.gmin) #linha, coluna
        end
        for sbm in lista_submercados
            @constraint(  m, deficit_vars[(no.codigo, sbm.nome, etapa)] >= 0 ) 
            @constraint(  m, excesso_vars[(no.codigo, sbm.nome, etapa)] >= 0 ) 
        end
        
        @objective(m, Min, sum(term.custo_geracao * gt_vars[(no.codigo, term.nome, etapa)] for term in lista_utes) 
        + sum(0.01 * vert_vars[(no.codigo, uhe.nome, etapa)] for uhe in lista_uhes)
        + sum(penalidVazMin * folga_positiva_vazmin_vars[(no.codigo, uhe.nome, etapa)] for uhe in lista_uhes)
        + sum(penalidVazMin * folga_positiva_volFimMundo_vars[(no.codigo, uhe.nome, etapa)] for uhe in lista_uhes)
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
        VertimentoSIN = 0
        TurbinamentoSIN = 0
        EnergiaArmazenadaSIN = 0
        for sbm in lista_submercados
            GeracaoHidreletricaTotal = 0
            VolumeArmazenadoTotal = 0
            AfluenciaTotal = 0
            VolumeArmazenadoInicialTotal = 0
            GeracaoTermicaTotal = 0
            VertimentoTotal = 0
            TurbinamentoTotal = 0
            EnergiaArmazenadaTotal = 0
            for term in cadastroUsinasTermicasSubmercado[sbm.codigo]
                geracao = JuMP.value(gt_vars[(no.codigo, term.nome, etapa)])
                push!(df_termicas, (etapa = etapa, iter = it, est = est, node = no.codigo, prob = probabilidadeNo, Submercado = sbm.codigo, nome = term.nome, usina = term.codigo, generation = round(geracao, digits = 2) , custo = term.custo_geracao, custoTotal = round(geracao, digits = 1)*term.custo_geracao , GerMin = term.gmin, GerMax = term.gmax))
                GeracaoTermicaTotal += geracao
                GeracaoTermicaSIN += geracao
            end
            for uhe in cadastroUsinasHidreletricasSubmercado[sbm.codigo]
                geracao = JuMP.value(gh_vars[(no.codigo, uhe.nome, etapa)])
                turbinamento = JuMP.value(turb_vars[(no.codigo, uhe.nome, etapa)]) 
                vertimento = JuMP.value(vert_vars[(no.codigo, uhe.nome, etapa)]) 
                volumeFinal = JuMP.value(vf_vars[(no.codigo, uhe.nome, etapa)]) 
                volumeInicial = Vi[(no.codigo, uhe.codigo, etapa)]
                earm_usi = volumeFinal*mapaUsinaProdtAcum[uhe.nome]/converte_m3s_hm3
                Afluencia = 0
                if( uhe.posto == 999)
                    Afluencia = 0
                else
                    Afluencia = (dat_vaz[(dat_vaz.NOME_UHE .== uhe.posto) .& (dat_vaz.NO .== no.codigo), "VAZAO"][1])
                end
                #Afluencia = (dat_vaz[(dat_vaz.NOME_UHE .== uhe.posto) .& (dat_vaz.NO .== no.codigo), "VAZAO"][1])
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

                if(restricaoVolumeFimMundo == 1 && est == caso.n_est)
                    dat_meta_armazenamento.USI = string.(dat_meta_armazenamento.USI)
                    matching_rows = dat_meta_armazenamento[dat_meta_armazenamento.USI .== uhe.nome, :meta]
                    vol_meta = isempty(matching_rows) ? NaN : first(matching_rows)
                    vol_meta = vol_meta/100
                    if !isnan(vol_meta)
                        folga_positiva_volFimMundo = JuMP.value(folga_positiva_volFimMundo_vars[(no.codigo, uhe.nome, etapa)])
                        folga_negativa_volFimMundo = JuMP.value(folga_negativa_volFimMundo_vars[(no.codigo, uhe.nome, etapa)])
                    else
                        vol_meta = 0
                        folga_positiva_volFimMundo = 0
                        folga_negativa_volFimMundo = 0
                    end

                end

                push!(df_hidreletricas, (etapa = etapa, iter = it, est = est, node = no.codigo, prob = probabilidadeNo, Submercado = sbm.codigo, nome = uhe.nome, usina = uhe.codigo, generation = round(geracao, digits = 2),
                                VI = Vi[(no.codigo,uhe.codigo, etapa)], 
                                AFL = round(Afluencia, digits = 2),
                                TURB = round(turbinamento, digits = 2), 
                                VERT = round(vertimento, digits = 2), 
                                VF = round(volumeFinal, digits = 2)))
                if(vazao_minima == 1)
                    defluencia = turbinamento + vertimento
                    push!(df_folga_vazmin, (etapa = etapa, iter = it, est = est, node = no.codigo, prob = probabilidadeNo, 
                    nome = uhe.nome, usina = uhe.codigo, Vazmin = vazao_minima_uhe, Qdef = round(defluencia, digits = 2), 
                    FolgaPosit = round(folga_positiva_vazmin, digits = 2), FolgaNeg = round(folga_negativa_vazmin, digits = 2) ))
                end

                if(restricaoVolumeFimMundo == 1 && est == caso.n_est)
                    dat_meta_armazenamento.USI = string.(dat_meta_armazenamento.USI)
                    matching_rows = dat_meta_armazenamento[dat_meta_armazenamento.USI .== uhe.nome, :meta]
                    vol_meta = isempty(matching_rows) ? NaN : first(matching_rows)
                    vol_meta = vol_meta/100
                    if !isnan(vol_meta)
                        folga_positiva_volFimMundo = JuMP.value(folga_positiva_volFimMundo_vars[(no.codigo, uhe.nome, etapa)])
                        folga_negativa_volFimMundo = JuMP.value(folga_negativa_volFimMundo_vars[(no.codigo, uhe.nome, etapa)])
                    else
                        vol_meta = 0
                        folga_positiva_volFimMundo = 0
                        folga_negativa_volFimMundo = 0
                    end
                    push!(df_folga_MetaVol, (etapa = etapa, iter = it, est = est, node = no.codigo, prob = probabilidadeNo, 
                    nome = uhe.nome, usina = uhe.codigo, Meta = vol_meta, VolF = round(volumeFinal, digits = 2), 
                    FolgaPosit = round(folga_positiva_volFimMundo, digits = 2), FolgaNeg = round(folga_negativa_volFimMundo, digits = 2) ))
                end

                GeracaoHidreletricaTotal += geracao
                GeracaoHidreletricaSIN += geracao
                VolumeArmazenadoTotal += volumeFinal
                VolumeArmazenadoSIN += volumeFinal
                AfluenciaTotal += Afluencia
                AfluenciaSIN += Afluencia
                VolumeArmazenadoInicialTotal += volumeInicial
                VolumeArmazenadoInicialSIN += volumeInicial
                VertimentoTotal += vertimento
                VertimentoSIN += vertimento
                TurbinamentoTotal += turbinamento
                TurbinamentoSIN += turbinamento
                EnergiaArmazenadaTotal += earm_usi
                EnergiaArmazenadaSIN += earm_usi
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
            push!(df_balanco_energetico_SBM,  (etapa = etapa, iter = it, est = est, node = no.codigo, prob = probabilidadeNo, Submercado = sbm.codigo, Demanda = sbm.demanda[est], GT = GeracaoTermicaTotal, GH = GeracaoHidreletricaTotal, AFL = AfluenciaTotal, Vini = VolumeArmazenadoInicialTotal, VolArm = VolumeArmazenadoTotal, Earm = EnergiaArmazenadaTotal, Turb = TurbinamentoTotal, Vert = VertimentoTotal, Deficit = def, Excesso = excesso_sbm, CustoPresente = custo_presente, CMO = round(valor_CMO, digits = 2)))
            for sbm_2 in lista_submercados
                if sbm.codigo != sbm_2.codigo
                    interc = JuMP.value(intercambio_vars[(no.codigo, sbm.nome, sbm_2.nome, etapa)])
                    push!(df_intercambio,  (etapa = etapa, iter = it, est = est, node = no.codigo, prob = probabilidadeNo, SubmercadoDE = sbm.codigo, SubmercadoPARA = sbm_2.codigo, Valor = round(interc, digits = 2)))
                end
            end
        end
        push!(df_balanco_energetico_SIN,  (etapa = etapa, iter = it, est = est, node = no.codigo, prob = probabilidadeNo, Demanda = DemandaTotalSIN, GT = GeracaoTermicaSIN, GH = GeracaoHidreletricaSIN, Deficit = DeficitSIN, Excesso = excesso_SIN, AFL = AfluenciaSIN, Vini = VolumeArmazenadoInicialSIN, VolArm = VolumeArmazenadoSIN, Earm = EnergiaArmazenadaSIN, Turb = TurbinamentoSIN, Vert = VertimentoSIN, CustoPresente = CustoPresenteSIN, CustoFuturo = JuMP.value(alpha_vars[no.codigo, etapa])))
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
            if(restricaoVolumeFimMundo == 1)
                penalidadePositivavolFimMundo = JuMP.value(folga_positiva_volFimMundo_vars[(no.codigo, hydro.nome, etapa)])
                custo_presente += penalidadePositivavolFimMundo*penalidVazMin
            end


        end

        for sbm in lista_submercados
            custo_presente += JuMP.value(deficit_vars[(no.codigo, sbm.nome, etapa)])*sbm.deficit_cost
        end


        return custo_presente
    end

    println("NUMERO DE USINAS HIDRELETRICAS: ", length(lista_uhes))
    println("NUMERO DE USINAS TERMICAS: ", length(lista_utes))
    global maxIteration = 0
    global tempo_acumulado = 0
    @time begin
        for it in 1:caso.n_iter
            global maxIteration = it
            start_time_iter = time()
            empty!(df_cortes_equivalentes)
            for est in 1:caso.n_est
                #println("Relizando FW - Iter ", it, " Est ", est)
                start_time = time()
                for i_no in mapa_periodos[est].nos  
                    #println("no ", i_no.codigo)  
                    etapa = "FW"     
                    m = retornaModelo(est,i_no, etapa)
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
                                    push!(df_cortes_equivalentes, (iter = iter, est = est, noUso = i_no.codigo,  usina = uhe.nome, Indep = indep_equivalente, Coef = dict_vfvars_coef[uhe.codigo] ))
                                end
                                @constraint(m, alpha_vars[(i_no.codigo,etapa)] - sum(vf_vars[(i_no.codigo, uhe.nome,etapa)]*dict_vfvars_coef[uhe.codigo] for uhe in lista_uhes)   >= indep_equivalente ) #linha, coluna
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
                            @constraint(m, alpha_vars[(i_no.codigo,etapa)] - sum(vf_vars[(i_no.codigo, uhe.nome,etapa)]*dict_vfvars_coef[uhe.codigo] for uhe in lista_uhes)   >= indep_equivalente ) #linha, coluna
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
            push!(df_convergencia, (iter = it, ZINF = zinf, ZSUP = valor_zsup, GAP = gap, MIN = minutes, SEC = seconds, MIN_TOT = minutes_acumulados, SEC_TOT = seconds_acumulados))
            #if gap < 0.00001
            if gap < tolerancia
            #if gap < 0.01 || minutes_acumulados > 120 || it == caso.n_iter
                println("CONVERGIU")
                break
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
                                @constraint(m, alpha_vars[(i_no.codigo,etapa)] - sum(vf_vars[(i_no.codigo, uhe.nome,etapa)]*dict_vfvars_coef[uhe.codigo] for uhe in lista_uhes)   >= indep_equivalente ) #linha, coluna
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


    df_folga_MetaVol_fw = df_folga_MetaVol[(df_folga_MetaVol.etapa .== "FW"), :]
    df_folga_MetaVol_bk = df_folga_MetaVol[(df_folga_MetaVol.etapa .== "BK"), :]
    df_folga_MetaVol_sf = df_folga_MetaVol[(df_folga_MetaVol.etapa .== "FW") .& (df_folga_MetaVol.iter .== max_iter), :]


    df_termicas_fw = df_termicas[(df_termicas.etapa .== "FW"), :]
    df_termicas_bk = df_termicas[(df_termicas.etapa .== "BK"), :]
    df_termicas_sf = df_termicas[(df_termicas.etapa .== "FW") .&& (df_termicas.iter .== max_iter), :]

    df_hidreletricas_fw = df_hidreletricas[(df_hidreletricas.etapa .== "FW"), :]
    df_hidreletricas_bk = df_hidreletricas[(df_hidreletricas.etapa .== "BK"), :]
    df_hidreletricas_sf = df_hidreletricas[(df_hidreletricas.etapa .== "FW") .&& (df_hidreletricas.iter .== max_iter), :]

    df_parcelasCustoPresente_fw = df_parcelasCustoPresente[(df_parcelasCustoPresente.etapa .== "FW"), :]
    df_parcelasCustoPresente_bk = df_parcelasCustoPresente[(df_parcelasCustoPresente.etapa .== "BK"), :]
    df_parcelasCustoPresente_sf = df_parcelasCustoPresente[(df_parcelasCustoPresente.etapa .== "FW") .&& (df_parcelasCustoPresente.iter .== max_iter), :]





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
    #CSV.write(output_dir_oper*"/termicas_fw.csv", df_termicas_fw)
    #CSV.write(output_dir_oper*"/termicas_bk.csv", df_termicas_bk)
    CSV.write(output_dir_oper*"/termicas_sf.csv", df_termicas_sf)
    #CSV.write(output_dir_oper*"/hidreletricas_fw.csv", df_hidreletricas_fw)
    #CSV.write(output_dir_oper*"/hidreletricas_bk.csv", df_hidreletricas_bk)
    CSV.write(output_dir_oper*"/hidreletricas_sf.csv", df_hidreletricas_sf)
    CSV.write(output_dir_oper*"/parcelaCustoPresente_sf.csv", df_parcelasCustoPresente_sf)
    #CSV.write(output_dir_oper*"/folgaVazmin_fw.csv", df_folga_vazmin_fw)
    #CSV.write(output_dir_oper*"/folgaVazmin_bk.csv", df_folga_vazmin_bk)
    CSV.write(output_dir_oper*"/folgaVazmin_sf.csv", df_folga_vazmin_sf)
    CSV.write(output_dir_oper*"/df_folga_MetaVol_sf.csv", df_folga_MetaVol_sf)
    CSV.write(output_dir_oper*"/convergencia.csv", df_convergencia)
    CSV.write(output_dir_oper*"/df_cortes.csv", df_cortes)
    CSV.write(output_dir_oper*"/df_cortes_equivalentes.csv", df_cortes_equivalentes)


    df_per_balanco_energetico = DataFrame(etapa = String[], iter = Int[],  est = Int[], Demanda = Float64[], GT = Float64[], GH = Float64[], Deficit = Float64[], Excesso =Float64[], AFL = Float64[], Vini = Float64[], VolArm = Float64[], Earm = Float64[], Turb = Float64[], Vert = Float64[], CustoPresente = Float64[], CustoFuturo = Float64[])
    for est_value in unique(df_balanco_energetico_SIN.est)
        subset = df_balanco_energetico_SIN_sf[df_balanco_energetico_SIN_sf.est .== est_value, :]
        for iteracao in unique(subset.iter)
            subsubset = subset[(subset.iter .== iteracao), :]
            ProbGT = 0
            ProbVarm = 0
            ProbAFL = 0
            ProbVini = 0
            ProbGH = 0
            ProbVert = 0
            ProbTurb = 0
            ProbEarm = 0
            ProbDeficit = 0
            ProbCustoPresente = 0
            ProbCustoFuturo = 0
            ProbExcesso = 0
            Demanda = 0
            for no in unique(subsubset.node)
                ProbGT += (subsubset[(subsubset.node .== no), "GT"][1])*(mapaProbCondicionalNo[no])
                ProbGH += (subsubset[(subsubset.node .== no), "GH"][1])*(mapaProbCondicionalNo[no])
                ProbAFL += (subsubset[(subsubset.node .== no), "AFL"][1])*(mapaProbCondicionalNo[no])
                ProbVarm += (subsubset[(subsubset.node .== no), "VolArm"][1])*(mapaProbCondicionalNo[no])
                ProbVert += (subsubset[(subsubset.node .== no), "Vert"][1])*(mapaProbCondicionalNo[no])
                ProbTurb += (subsubset[(subsubset.node .== no), "Turb"][1])*(mapaProbCondicionalNo[no])
                ProbEarm += (subsubset[(subsubset.node .== no), "Earm"][1])*(mapaProbCondicionalNo[no])
                ProbVini += (subsubset[(subsubset.node .== no), "Vini"][1])*(mapaProbCondicionalNo[no])
                ProbDeficit += (subsubset[(subsubset.node .== no), "Deficit"][1])*(mapaProbCondicionalNo[no])
                ProbExcesso += (subsubset[(subsubset.node .== no), "Excesso"][1])*(mapaProbCondicionalNo[no])
                ProbCustoPresente += (subsubset[(subsubset.node .== no), "CustoPresente"][1])*(mapaProbCondicionalNo[no])
                ProbCustoFuturo += (subsubset[(subsubset.node .== no), "CustoFuturo"][1])*(mapaProbCondicionalNo[no])
                Demanda += (subsubset[(subsubset.node .== no), "Demanda"][1])*(mapaProbCondicionalNo[no])
                #println("ProbGT: ", ProbGT, " No: ", no, " GT: ", (subsubset[(subsubset.node .== no), "GT"][1]), " prob: ", (mapaProbCondicionalNo[no]))
            end
            
            dem = (subset[(subset.est .== est_value), "Demanda"][1])
            push!(df_per_balanco_energetico, (etapa = "SF", iter = iteracao, est = est_value, Demanda = dem, GT = round(ProbGT, digits = 0), GH = round(ProbGH, digits = 0), Deficit = round(ProbDeficit, digits = 0), Excesso = round(ProbExcesso,digits = 0), AFL = round(ProbAFL, digits= 0), Vini = round(ProbVini, digits = 0), VolArm = round(ProbVarm, digits = 0), Earm = round(ProbEarm, digits= 0 ), Turb = round(ProbTurb, digits= 0 ), Vert = round(ProbVert, digits= 0 ), CustoPresente = round(ProbCustoPresente, digits = 0) , CustoFuturo = round(ProbCustoFuturo, digits = 0)))
        end
    end
    df_per_balanco_energetico = sort(df_per_balanco_energetico, :iter)
    CSV.write(output_dir_oper*"/balanco_energetico_final.csv", df_per_balanco_energetico)

    #println(df_per_balanco_energetico)
    show(IOContext(stdout, :compact => false), df_per_balanco_energetico)

    means = combine(df_per_balanco_energetico, names(df_per_balanco_energetico, Number) .=> mean)
    println(means)
    CSV.write(output_dir_oper*"/media_SIN.csv", means)
    

    df_per_balanco_energetico_SBM = DataFrame(etapa = String[], iter = Int[],  Submercado = Int[], est = Int[], Demanda = Float64[], GT = Float64[], GH = Float64[], Deficit = Float64[], Excesso =Float64[], AFL = Float64[], Vini = Float64[], VolArm = Float64[], Earm = Float64[], Turb = Float64[], Vert = Float64[], CustoPresente = Float64[], CMO = Float64[])
    sbms = unique(df_balanco_energetico_SBM_sf.Submercado)
    for sbm in sbms
        subsubset_1 = df_balanco_energetico_SBM_sf[(df_balanco_energetico_SBM_sf.Submercado .== sbm), :]
        for est_value in unique(subsubset_1.est)
            subset = subsubset_1[subsubset_1.est .== est_value, :]
            for iteracao in unique(subset.iter)
                subsubset = subset[(subset.iter .== iteracao), :]
                ProbGT = 0
                ProbVarm = 0
                ProbAFL = 0
                ProbVini = 0
                ProbGH = 0
                ProbVert = 0
                ProbTurb = 0
                ProbEarm = 0
                ProbDeficit = 0
                ProbCustoPresente = 0
                ProbCMO = 0
                ProbExcesso = 0
                Demanda = 0
                for no in unique(subsubset.node)
                    ProbGT += (subsubset[(subsubset.node .== no), "GT"][1])*(mapaProbCondicionalNo[no])
                    ProbGH += (subsubset[(subsubset.node .== no), "GH"][1])*(mapaProbCondicionalNo[no])
                    ProbAFL += (subsubset[(subsubset.node .== no), "AFL"][1])*(mapaProbCondicionalNo[no])
                    ProbVarm += (subsubset[(subsubset.node .== no), "VolArm"][1])*(mapaProbCondicionalNo[no])
                    ProbVert += (subsubset[(subsubset.node .== no), "Vert"][1])*(mapaProbCondicionalNo[no])
                    ProbTurb += (subsubset[(subsubset.node .== no), "Turb"][1])*(mapaProbCondicionalNo[no])
                    ProbEarm += (subsubset[(subsubset.node .== no), "Earm"][1])*(mapaProbCondicionalNo[no])
                    ProbVini += (subsubset[(subsubset.node .== no), "Vini"][1])*(mapaProbCondicionalNo[no])
                    ProbDeficit += (subsubset[(subsubset.node .== no), "Deficit"][1])*(mapaProbCondicionalNo[no])
                    ProbExcesso += (subsubset[(subsubset.node .== no), "Excesso"][1])*(mapaProbCondicionalNo[no])
                    ProbCustoPresente += (subsubset[(subsubset.node .== no), "CustoPresente"][1])*(mapaProbCondicionalNo[no])
                    ProbCMO += (subsubset[(subsubset.node .== no), "CMO"][1])*(mapaProbCondicionalNo[no])
                    Demanda += (subsubset[(subsubset.node .== no), "Demanda"][1])*(mapaProbCondicionalNo[no])
                    #println("ProbGT: ", ProbGT, " No: ", no, " GT: ", (subsubset[(subsubset.node .== no), "GT"][1]), " prob: ", (mapaProbCondicionalNo[no]))
                end
                dem = (subset[(subset.est .== est_value), "Demanda"][1])
                push!(df_per_balanco_energetico_SBM, (etapa = "SF", iter = iteracao, Submercado = sbm, est = est_value, Demanda = dem, GT = round(ProbGT, digits = 0), GH = round(ProbGH, digits = 0), Deficit = round(ProbDeficit, digits = 0), Excesso = round(ProbExcesso,digits = 0), AFL = round(ProbAFL, digits= 0), Vini = round(ProbVini, digits = 0), VolArm = round(ProbVarm, digits = 0), Earm = round(ProbEarm, digits = 0), Turb = round(ProbTurb, digits = 0), Vert = round(ProbVert, digits= 0 ), CustoPresente = round(ProbCustoPresente, digits = 0) , CMO = round(ProbCMO, digits = 0)))
            end
        end
    end
    df_per_balanco_energetico_SBM = sort(df_per_balanco_energetico_SBM, :iter)
    CSV.write(output_dir_oper*"/balanco_energetico_final_sbm.csv", df_per_balanco_energetico_SBM)
    show(IOContext(stdout, :compact => false), df_per_balanco_energetico_SBM)

    means_sbm = combine(df_per_balanco_energetico_SBM, names(df_per_balanco_energetico_SBM, Number) .=> mean)
    println(means_sbm)
    CSV.write(output_dir_oper*"/media_SBM.csv", means_sbm)


    df_per_balanco_energetico_USIH = DataFrame(etapa = String[], iter = Int[],  usina = Int[], est = Int[], Submercado = Int[], nome = String[] , usinaJusante = String[], generation = Float64[], VI = Float64[], AFL = Float64[], TURB = Float64[], VERT = Float64[], QDEF = Float64[], VAZMIN = Float64[], VF = Float64[])
    for uhe in lista_uhes
        subsubset_1 = df_hidreletricas_sf[(df_hidreletricas_sf.usina .== uhe.codigo), :]
        for est_value in unique(subsubset_1.est)
            subset = subsubset_1[subsubset_1.est .== est_value, :]
            for iteracao in unique(subset.iter)
                subsubset = subset[(subset.iter .== iteracao), :]
                Probgeneration = 0
                ProbVI = 0
                ProbAFL = 0
                ProbTURB = 0
                ProbVERT = 0
                ProbVF = 0
                for no in unique(subsubset.node)
                    Probgeneration += (subsubset[(subsubset.node .== no), "generation"][1])*(mapaProbCondicionalNo[no])
                    ProbVI += (subsubset[(subsubset.node .== no), "VI"][1])*(mapaProbCondicionalNo[no])
                    ProbAFL += (subsubset[(subsubset.node .== no), "AFL"][1])*(mapaProbCondicionalNo[no])
                    ProbTURB += (subsubset[(subsubset.node .== no), "TURB"][1])*(mapaProbCondicionalNo[no])
                    ProbVERT += (subsubset[(subsubset.node .== no), "VERT"][1])*(mapaProbCondicionalNo[no])
                    ProbVF += (subsubset[(subsubset.node .== no), "VF"][1])*(mapaProbCondicionalNo[no])
                    #println("ProbGT: ", ProbGT, " No: ", no, " GT: ", (subsubset[(subsubset.node .== no), "GT"][1]), " prob: ", (mapaProbCondicionalNo[no]))
                end
                prob_defluencia = ProbVERT+ProbTURB
                vazao_minima_uhe = 0
                if(vazao_minima == 1)
                    matching_rows = dat_vazmin[dat_vazmin.USI .== uhe.nome, :vazmin]
                    vazao_minima_uhe = isempty(matching_rows) ? NaN : first(matching_rows)
                    if !isnan(vazao_minima_uhe)
                        vazao_minima_uhe = vazao_minima_uhe
                    else
                        vazao_minima_uhe = 0
                    end
                end
                submercado = (subset[(subset.est .== est_value), "Submercado"][1])
                push!(df_per_balanco_energetico_USIH, (etapa = "SF", iter = iteracao, usina = uhe.codigo, est = est_value, Submercado = submercado,nome = uhe.nome, usinaJusante = uhe.jusante, generation = round(Probgeneration, digits = 0), VI = round(ProbVI, digits = 0), AFL = round(ProbAFL, digits = 0), TURB = round(ProbTURB,digits = 0), VERT = round(ProbVERT, digits= 0), QDEF = round(prob_defluencia, digits= 0), VAZMIN = round(vazao_minima_uhe, digits= 0), VF = round(ProbVF, digits = 0)))
            end
        end
    end
    df_per_balanco_energetico_USIH = sort(df_per_balanco_energetico_USIH, :iter)
    CSV.write(output_dir_oper*"/balanco_energetico_final_UHE.csv", df_per_balanco_energetico_USIH)
    #show(IOContext(stdout, :compact => false), df_per_balanco_energetico_USIH)

    means_uhe = combine(df_per_balanco_energetico_USIH, names(df_per_balanco_energetico_USIH, Number) .=> mean)
    #println(means_uhe)
    CSV.write(output_dir_oper*"/media_UHE.csv", means_uhe)

    df_per_balanco_energetico_USIT = DataFrame(etapa = String[], iter = Int[],  usina = Int[], est = Int[], Submercado = Int[], nome = String[], generation = Float64[], custo = Float64[], custoTotal = Float64[], GerMin = Float64[], GerMax = Float64[])
    for ute in lista_utes
        subsubset_1 = df_termicas_sf[(df_termicas_sf.usina .== ute.codigo), :]
        for est_value in unique(subsubset_1.est)
            subset = subsubset_1[subsubset_1.est .== est_value, :]
            for iteracao in unique(subset.iter)
                subsubset = subset[(subset.iter .== iteracao), :]
                Probgeneration = 0
                ProbcustoTotal = 0
                for no in unique(subsubset.node)
                    Probgeneration += (subsubset[(subsubset.node .== no), "generation"][1])*(mapaProbCondicionalNo[no])
                    ProbcustoTotal += (subsubset[(subsubset.node .== no), "custoTotal"][1])*(mapaProbCondicionalNo[no])
                    #println("ProbGT: ", ProbGT, " No: ", no, " GT: ", (subsubset[(subsubset.node .== no), "GT"][1]), " prob: ", (mapaProbCondicionalNo[no]))
                end
                submercado = (subset[(subset.est .== est_value), "Submercado"][1])
                push!(df_per_balanco_energetico_USIT, (etapa = "SF", iter = iteracao, usina = ute.codigo, est = est_value, Submercado = submercado,nome = ute.nome, generation = round(Probgeneration, digits = 0), custo = ute.custo_geracao, custoTotal = round(ProbcustoTotal, digits= 0), GerMin = ute.gmin, GerMax = ute.gmax))
            end
        end
    end
    df_per_balanco_energetico_USIT = sort(df_per_balanco_energetico_USIT, :iter)
    CSV.write(output_dir_oper*"/balanco_energetico_final_UTE.csv", df_per_balanco_energetico_USIT)
    #show(IOContext(stdout, :compact => false), df_per_balanco_energetico_USIT)

    means_ute = combine(df_per_balanco_energetico_USIT, names(df_per_balanco_energetico_USIT, Number) .=> mean)
    #println(means_ute)
    CSV.write(output_dir_oper*"/media_UTE.csv", means_ute)
    
    df_per_parcelaCustoPresente_sf = DataFrame(etapa = String[], iter = Int[], est = Int[], Submercado = Int[], usina = String[], codigo = Int[], geracao = Float64[], Custo = Float64[], CustoPresente = Float64[], CustoPresenteAcum = Float64[])
    for usi in unique(df_parcelasCustoPresente_sf.usina)
        subsubset_1 = df_parcelasCustoPresente_sf[(df_parcelasCustoPresente_sf.usina .== usi), :]
        for est_value in unique(subsubset_1.est)
            subset = subsubset_1[subsubset_1.est .== est_value, :]
            for iteracao in unique(subset.iter)
                subsubset = subset[(subset.iter .== iteracao), :]
                Probgeneration = 0
                Probcusto = 0
                ProbcustoPresente = 0
                ProbcustoPresenteAcum = 0
                for no in unique(subsubset.node)
                    Probgeneration += (subsubset[(subsubset.node .== no), "geracao"][1])*(mapaProbCondicionalNo[no])
                    Probcusto += (subsubset[(subsubset.node .== no), "Custo"][1])*(mapaProbCondicionalNo[no])
                    ProbcustoPresente += (subsubset[(subsubset.node .== no), "CustoPresente"][1])*(mapaProbCondicionalNo[no])
                    ProbcustoPresenteAcum += (subsubset[(subsubset.node .== no), "CustoPresenteAcum"][1])*(mapaProbCondicionalNo[no])
                    #println("ProbGT: ", ProbGT, " No: ", no, " GT: ", (subsubset[(subsubset.node .== no), "GT"][1]), " prob: ", (mapaProbCondicionalNo[no]))
                end
                submercado = (subset[(subset.est .== est_value), "Submercado"][1])
                codigo_usi = (subset[(subset.est .== est_value), "codigo"][1])
                push!(df_per_parcelaCustoPresente_sf, (etapa = "SF", iter = iteracao, usina = usi, codigo = codigo_usi, est = est_value, Submercado = submercado,geracao = round(Probgeneration, digits = 0), Custo = Probcusto, CustoPresente = round(ProbcustoPresente, digits= 0), CustoPresenteAcum = round(ProbcustoPresenteAcum, digits= 0)))
            end
        end
    end
    df_per_parcelaCustoPresente_sf = sort(df_per_parcelaCustoPresente_sf, :iter)
    CSV.write(output_dir_oper*"/balanco_energetico_final_Parcelas_CP.csv", df_per_parcelaCustoPresente_sf)
    #show(IOContext(stdout, :compact => false), df_per_parcelaCustoPresente_sf)

    means_CustoPresente = combine(df_per_parcelaCustoPresente_sf, names(df_per_parcelaCustoPresente_sf, Number) .=> mean)
    #println(means_CustoPresente)
    CSV.write(output_dir_oper*"/media_CustoPresente.csv", means_CustoPresente)



    df_corte_est = DataFrame(iter = Int[], est = Int[], usina = String[], Indep = Float64[], Coef = Float64[])
    # Lista de DataFrames
    lista_df = DataFrame[]
    estagios = sort(unique(df_cortes_equivalentes.est))
    # Estágios 2 e 3
    #println("it: ", maxIteration)
    #print("estagios: ", estagios)

    for est in estagios
        df_cortes_est = filter(:est => ==(est), df_cortes_equivalentes)
        df_cortes_est = filter(:iter => <(maxIteration), df_cortes_est)
        #println(df_cortes_est)
        if est == 1
            #df_cortes_est = filter(row -> !(row.Indep == 0.0 && row.Coef == 0.0), df_cortes_est)
            #println(df_cortes_est)
            push!(lista_df, df_cortes_est)

        else
            nos_est = unique(df_cortes_est.noUso)
            #println("est: ", est)
            for usi in lista_uhes
                df_cortes_est_usi = filter(:usina => ==(usi.nome), df_cortes_est)
                #println("df_cortes_est_usi: ", df_cortes_est_usi)
                #println(df_cortes_est_usi)
                df_mask = filter(:noUso => ==(nos_est[1]), df_cortes_est_usi)
                #println("df_mask: ", df_mask)
                df_mask.Indep .= 0.0
                df_mask.Coef .= 0.0
                df_mask.noUso .= est
                for node in nos_est
                    #println("node: ", node)
                    df_cortes_est_usi_node = filter(:noUso => ==(node), df_cortes_est_usi)
                    #df_mask = filter(row -> !(row.Indep == 0.0 && row.Coef == 0.0), df_mask)
                    #println("df_cortes_est_usi_node: ", df_cortes_est_usi_node)
                    caminho_node = retornaListaCaminho(node)  # You must define this in Julia
                    
                    prob_cond = 1.0
                    for elemento in caminho_node
                        prob_elemento = df_arvore[df_arvore.NO .== elemento, :PROB][1]
                        prob_cond *= prob_elemento
                    end
                    #println("caminho_node: ", caminho_node, " prob: ", prob_cond)
                    df_mask.Indep .+= df_cortes_est_usi_node.Indep .* prob_cond
                    df_mask.Coef .+= df_cortes_est_usi_node.Coef .* prob_cond
                end
                #println(df_mask)
                push!(lista_df, df_mask)
            end
            
        end
    end
    df_final = vcat(lista_df...)
    #println(df_final)
    CSV.write(output_dir_oper*"/cortes_est.csv", df_final)
end