module Main

    using JuMP, GLPK, Plots, Measures, Plots, SparseArrays, DataFrames
    include("CapacidadeLinhas.jl")


    #Inicializando variaveis da barra
    for ilha in lista_ilhas_eletricas
        for est in 1:caso.n_est
            for i_no in mapa_periodos[est].nos
                for barra in ilha.barras
                    barra.potenciaGerada[(i_no.codigo, barra.codigo) ] = 0
                    barra.potenciaLiquida[(i_no.codigo, barra.codigo) ] = 0
                    barra.deficitBarra[(i_no.codigo, barra.codigo) ] = 0
                end
            end
        end
    end

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

    df_balanco_energetico = DataFrame(etapa = String[], iter = Int[], miniIter = [], est = Int[], node = Int[], prob = [], ilha = Int[], Demanda = Float64[], GT = Float64[], GH = Float64[], Deficit = Float64[], CustoPresente = Float64[], CustoFuturo = Float64[])
    df_termicas           = DataFrame(etapa = String[], iter = Int[], miniIter = [], est = Int[], node = Int[], prob = [],nome = String[] , usina = Int[], generation = Float64[], custo = Float64[], custoTotal = Float64[])
    df_hidreletricas      = DataFrame(etapa = String[], iter = Int[], miniIter = [], est = Int[], node = Int[], prob = [],nome = String[] ,usina = Int[], generation = Float64[], VI = Float64[], AFL = Float64[], TURB = Float64[], VERT = Float64[], VF = Float64[])
    df_convergencia    = DataFrame(iter = Int[], ZINF = Float64[], ZSUP = Float64[])
    df_cortes          = DataFrame(iter = Int[], est = Int[], no = Int[],  usina = Int[], Indep = Float64[], Coef = Float64[])
    df_barras             = DataFrame(etapa = String[], iter = Int[], miniIter = [], est = Int[], node = Int[], prob = [],ilha = Int[], codigoBarra = Int[], generation = Float64[], demanda = Float64[], potenciaLiquida = Float64[], deficit = Float64[])
    df_linhas             = DataFrame(etapa = String[], iter = Int[], miniIter = [], est = Int[], node = Int[], prob = [],ilha = Int[], codigoBarraDE = Int[], codigoBarraPARA = Int[], capacidade = Float64[], fluxo = Float64[], folga = Float64[])

    ger_vars = Dict{Tuple{Int, Int, String}, JuMP.VariableRef}()
    gt_vars = Dict{Tuple{Int, String, String}, JuMP.VariableRef}()
    gh_vars = Dict{Tuple{Int, String, String}, JuMP.VariableRef}()
    turb_vars = Dict{Tuple{Int, String, String}, JuMP.VariableRef}()
    vert_vars = Dict{Tuple{Int, String, String}, JuMP.VariableRef}()
    vf_vars = Dict{Tuple{Int, String, String}, JuMP.VariableRef}()
    alpha_vars = Dict{Tuple{Int, String}, JuMP.VariableRef}()
    deficit_vars = Dict{Tuple{Int, String}, JuMP.VariableRef}()
    folga_rede = Dict{Tuple{Int, LinhaConfig, String}, JuMP.VariableRef}()
    deficit_barra = Dict{Tuple{Int, Int, String}, JuMP.VariableRef}()
    folga_rede = Dict{Tuple{Int, LinhaConfig, String}, JuMP.VariableRef}()
    constraint_dict = Dict{Tuple{Int, String, String}, JuMP.ConstraintRef}()

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
        end
        deficit_vars[(no.codigo, etapa)] = @variable(m, base_name="def_$(no.codigo)_$(etapa)")
        for ilha in lista_ilhas_eletricas ##QUESTAO AQUI, ESTA DECLARANDO TODOS OS GERADORES NA RESTRICAO DA ILHA, CONSIDERANDO QUE SO EXISTE UMA ILHA. CASO EXISTA MAIS DE UMA, E NECESSARIO CADASTRAR APENAS OS GERADORES DAQUELA ILHA NA RESTRICAO DE DEMANDA
            for barra in ilha.barrasAtivas[est]
                deficit_barra[(no.codigo, barra.codigo, etapa)] = @variable(m, base_name="deficitBarra_$(no.codigo)_$(barra.codigo)_$(etapa)")
            end
        end

        alpha_vars[(no.codigo,etapa)] = @variable(m, base_name="alpha_$(no.codigo)_$(etapa)")
        @constraint(m, alpha_vars[(no.codigo, etapa)] >= 0 )

        for uhe in lista_uhes
            @constraint(  m, gh_vars[(no.codigo, uhe.nome, etapa)] >= 0 ) 
            @constraint(  m, turb_vars[(no.codigo, uhe.nome, etapa)] >= 0 ) 
            @constraint(  m, vert_vars[(no.codigo, uhe.nome, etapa)] >= 0 ) 
            @constraint(  m, vf_vars[(no.codigo, uhe.nome, etapa)] >= 0 ) 

            @constraint(m, gh_vars[(no.codigo, uhe.nome, etapa)] - uhe.prodt*turb_vars[(no.codigo, uhe.nome, etapa)] == 0) #linha, coluna      /converte_m3s_hm3
            @constraint(m, turb_vars[(no.codigo, uhe.nome, etapa)] <= uhe.turbmax) #linha, coluna
            @constraint(m, vf_vars[(no.codigo, uhe.nome, etapa)] <=  uhe.vmax) #linha, coluna
            @constraint(m, vf_vars[(no.codigo, uhe.nome, etapa)] >=  uhe.vmin) #linha, coluna

            constraint_dict[(no.codigo, uhe.nome, etapa)] = @constraint(m, 
            vf_vars[(no.codigo, uhe.nome, etapa)]
            + turb_vars[(no.codigo, uhe.nome, etapa)]
            + vert_vars[(no.codigo, uhe.nome, etapa)]
            - sum(turb_vars[(no.codigo, nomeUsiMont, etapa)] for nomeUsiMont in mapa_montantesUsina[uhe.nome])
            - sum(vert_vars[(no.codigo, nomeUsiMont, etapa)] for nomeUsiMont in mapa_montantesUsina[uhe.nome])
            == Vi[no.codigo,uhe.codigo, etapa] + (dat_vaz[(dat_vaz.NOME_UHE .== uhe.codigo) .& (dat_vaz.NO .== no.codigo), "VAZAO"][1])) #linha, colun * converte_m3s_hm3
        end

        for term in lista_utes
            @constraint(m, gt_vars[(no.codigo, term.nome, etapa)] >= 0)
            @constraint(m, gt_vars[(no.codigo, term.nome, etapa)] <= term.gmax) #linha, coluna
        end
        @constraint(  m, deficit_vars[(no.codigo, etapa)] >= 0 ) 

        @objective(m, Min, sum(term.custo_geracao * gt_vars[(no.codigo, term.nome, etapa)] for term in lista_utes) 
        + sum(0.01 * vert_vars[(no.codigo, uhe.nome, etapa)] for uhe in lista_uhes)
        + sistema.deficit_cost*deficit_vars[(no.codigo, etapa)] 
        +sum(sistema.deficit_cost*deficit_barra[(no.codigo, barra.codigo, etapa)] for barra in lista_barras)
        + alpha_vars[(no.codigo, etapa)])
        
        if rede_eletrica == 1
            carga_estagio_ilha = 0
            for ilha in lista_ilhas_eletricas ##QUESTAO AQUI, ESTA DECLARANDO TODOS OS GERADORES NA RESTRICAO DA ILHA, CONSIDERANDO QUE SO EXISTE UMA ILHA. CASO EXISTA MAIS DE UMA, E NECESSARIO CADASTRAR APENAS OS GERADORES DAQUELA ILHA NA RESTRICAO DE DEMANDA
                for barra in ilha.barrasAtivas[est]
                    carga_estagio_ilha += barra.carga[est]
                    @constraint(  m, deficit_barra[(no.codigo, barra.codigo, etapa)] >= 0 ) 
                end
                @constraint(  m, sum(deficit_barra[(no.codigo, barra.codigo, etapa)] for barra in ilha.barrasAtivas[est]) 
                + sum(gh_vars[(no.codigo, uhe.nome, etapa)] for uhe in lista_uhes) 
                + sum(gt_vars[(no.codigo, term.nome, etapa)] for term in lista_utes) == carga_estagio_ilha   )
            end
        else
            @constraint(  m, balanco,
            sum(gh_vars[(no.codigo, uhe.nome, etapa)] for uhe in lista_uhes) 
            + sum(gt_vars[(no.codigo, term.nome, etapa)] for term in lista_utes) 
            + deficit_vars[(no.codigo, etapa)] == sistema.demanda[est]   )
        end

        return m
    end

    function imprimePolitica(etapa, est, it, miniIter, no)
        println("ETAPA: ", etapa, " est: ", est, " it: ", it, " miniIter: ", miniIter, " no: ", no.codigo)
        #converte_m3s_hm3 = (conversao_m3_hm3*dat_horas[(dat_horas.PERIODO .== no.periodo), "HORAS"][1])
        probabilidadeNo = (dat_prob[(dat_prob.NO .== no.codigo), "PROBABILIDADE"][1])
        GeracaoHidreletricaTotal = 0
        GeracaoTermicaTotal = 0
        for term in lista_utes
            geracao = JuMP.value(gt_vars[(no.codigo, term.nome, etapa)])
            push!(df_termicas, (etapa = etapa, iter = it, miniIter = miniIter , est = est, node = no.codigo, prob = probabilidadeNo, nome = term.nome, usina = term.codigo, generation = round(geracao, digits = 1) , custo = term.custo_geracao, custoTotal = round(geracao, digits = 1)*term.custo_geracao))
            GeracaoTermicaTotal += geracao
        end
        for uhe in lista_uhes
            geracao = JuMP.value(gh_vars[(no.codigo, uhe.nome, etapa)])
            turbinamento = JuMP.value(turb_vars[(no.codigo, uhe.nome, etapa)]) 
            vertimento = JuMP.value(vert_vars[(no.codigo, uhe.nome, etapa)]) 
            volumeFinal = JuMP.value(vf_vars[(no.codigo, uhe.nome, etapa)]) 
            push!(df_hidreletricas, (etapa = etapa, iter = it, miniIter = miniIter , est = est, node = no.codigo, prob = probabilidadeNo, nome = uhe.nome, usina = uhe.codigo, generation = geracao,
                            VI = Vi[(no.codigo,uhe.codigo, etapa)], AFL = (dat_vaz[(dat_vaz.NOME_UHE .== uhe.codigo) .& (dat_vaz.NO .== no.codigo), "VAZAO"][1]),
                            TURB = turbinamento, 
                            VERT = vertimento, 
                            VF = volumeFinal))
            GeracaoHidreletricaTotal += geracao
        end
        custo_presente = 0
        for term in lista_utes
            custo_presente += JuMP.value.(gt_vars[(no.codigo, term.nome, etapa)])*term.custo_geracao
        end
        
        def = 0

        if rede_eletrica == 1
            carga_estagio_ilha = 0
            for ilha in lista_ilhas_eletricas ##QUESTAO AQUI, ESTA DECLARANDO TODOS OS GERADORES NA RESTRICAO DA ILHA, CONSIDERANDO QUE SO EXISTE UMA ILHA. CASO EXISTA MAIS DE UMA, E NECESSARIO CADASTRAR APENAS OS GERADORES DAQUELA ILHA NA RESTRICAO DE DEMANDA
                for barra in ilha.barrasAtivas[est]
                    carga_estagio_ilha += barra.carga[est]
                    valor_deficit = JuMP.value(deficit_barra[(no.codigo, barra.codigo, etapa)])
                    custo_presente += valor_deficit*sistema.deficit_cost
                    def += valor_deficit
                    push!(df_barras,  (etapa = etapa, iter = it, miniIter = miniIter , est = est, node = no.codigo, prob = probabilidadeNo, ilha = ilha.codigo, codigoBarra = barra.codigo, generation = round(get(barra.potenciaGerada, (it, est, no.codigo), 0), digits = 1), demanda = barra.carga[est], potenciaLiquida = round(get(barra.potenciaLiquida, (it, est, no.codigo), 0), digits = 1), deficit= round(valor_deficit, digits = 1)))
                end
                for linha in ilha.linhasAtivas[est]
                    folga_da_rede = get(folga_rede , (no.codigo, linha, etapa), 0)
                    if folga_da_rede != 0 
                        valor_folga_rede = JuMP.value(folga_da_rede)
                    else
                        valor_folga_rede = -9999
                    end
                    push!(df_linhas,  (etapa = etapa, iter = it, miniIter = miniIter , est = est, node = no.codigo, prob = probabilidadeNo, ilha = ilha.codigo, codigoBarraDE = linha.de.codigo, codigoBarraPARA = linha.para.codigo, capacidade = linha.Capacidade[est], fluxo = round(get(linha.fluxoDePara,(it, est, no.codigo),0), digits = 1) ,  folga = valor_folga_rede))
                end
                push!(df_balanco_energetico,  (etapa = etapa, iter = it, miniIter = miniIter ,est = est, node = no.codigo, prob = probabilidadeNo, ilha = ilha.codigo, Demanda = carga_estagio_ilha, GT = GeracaoTermicaTotal, GH = GeracaoHidreletricaTotal, Deficit = def, CustoPresente = custo_presente, CustoFuturo = JuMP.value(alpha_vars[(no.codigo, etapa)])))
                print(df_balanco_energetico)
                #if etapa == "BK" && it == 5
                #    exit(1)
                #end
            end
        else
            def = JuMP.value(deficit_vars[(no.codigo, etapa)])
            custo_presente += def*sistema.deficit_cost
            push!(df_balanco_energetico,  (etapa = etapa, iter = it, miniIter = miniIter ,est = est, node = no.codigo, prob = probabilidadeNo, ilha = 0, Demanda = sistema.demanda[est], GT = GeracaoTermicaTotal, GH = GeracaoHidreletricaTotal, Deficit = def, CustoPresente = custo_presente, CustoFuturo = JuMP.value(alpha_vars[no.codigo, etapa])))
        end
        #push!(df_balanco_energetico,  (etapa = text, iter = it, est = est, node = no.codigo, ilha = 0, Demanda = sistema.demanda[est], GT = GeracaoTermicaTotal, GH = GeracaoHidreletricaTotal, Deficit = Deficit, CustoPresente = retornaCustoPresente(m, est, no), CustoFuturo = JuMP.value(m[:alpha])))
    end


    function retornaCustoPresente(est, no,etapa)
        custo_presente = 0
        for term in lista_utes
            geracao = JuMP.value(gt_vars[(no.codigo, term.nome, etapa)])
            custo_presente += geracao*term.custo_geracao
        end
        if rede_eletrica == 1
            for ilha in lista_ilhas_eletricas 
                for barra in ilha.barrasAtivas[est]
                    valor_deficit = JuMP.value(deficit_barra[(no.codigo, barra.codigo, etapa)])
                    custo_presente += valor_deficit*sistema.deficit_cost
                end
            end
        else
            custo_presente += JuMP.value(deficit_vars[(no.codigo, etapa)])*sistema.deficit_cost
        end
        return custo_presente
    end


    function add_fluxo_constrains(m, etapa, est, i_no, ilha, mapa_ilha_fluxos_violados, folga_rede)
        for linha in mapa_ilha_fluxos_violados[i_no.codigo, ilha.codigo]
            lista_variaveis = []
            for barra in ilha.barrasAtivas[est]
                if barra.codigo != ilha.slack.codigo
                    usi = get(mapa_codigoBARRA_nomeUSINA,barra.codigo,0)
                    #println("Barra: ", barra.codigo, " NOME_USI: ", usi)
                    UHE = get(mapa_nome_UHE,usi,0)
                    UTE = get(mapa_nome_UTE,usi,0)
                    if UHE != 0 push!(lista_variaveis, gh_vars[(i_no.codigo, UHE.nome, etapa)]) end
                    if UTE != 0   push!(lista_variaveis, gt_vars[(i_no.codigo, UTE.nome, etapa)]) end
                    
                    if UHE == 0 && UTE == 0 
                        variavel = deficit_barra[(i_no.codigo, barra.codigo, etapa)]
                        push!(lista_variaveis,variavel)
                    end
                end
            end
            fator = ifelse(linha.RHS[est] <= 0, -1 , 1)
            folga_rede[(i_no.codigo, linha, etapa)] = @variable(m, base_name="sFluxo_$(i_no.codigo)_$(linha.de.codigo)_$(linha.para.codigo)_$(etapa)")
            @constraint(m, folga_rede[(i_no.codigo, linha, etapa)] >= 0)
            @constraint(m, folga_rede[(i_no.codigo, linha, etapa)] <= 2*linha.Capacidade[est])
            @constraint(  m, sum(fator*linha.linhaMatrizSensibilidade[est][i]*lista_variaveis[i] for i in 1:length(lista_variaveis)) + fator*folga_rede[(i_no.codigo, linha, etapa)] == fator*linha.RHS[est]   )
        end
    end



    function transfere_resultados_para_Barras(ilha, iter, est, i_no)
        for barra in ilha.barrasAtivas[est]
            geracao = 0
            nome_usi = get(mapa_codigoBARRA_nomeUSINA, barra.codigo, 0) 
            variavel_gh = get(gh_vars, (i_no.codigo, nome_usi, etapa), 0)
            variavel_gt = get(gt_vars, (i_no.codigo, nome_usi, etapa), 0)
            if nome_usi != 0
                if variavel_gh != 0 
                    geracao = JuMP.value(variavel_gh) 
                elseif variavel_gt != 0
                    geracao = JuMP.value(variavel_gt)
                else
                    geracao = 0
                end
            else
                geracao = 0
            end

            barra.potenciaGerada[iter, i_no.codigo] = geracao
            def = JuMP.value(deficit_barra[(i_no.codigo, barra.codigo, etapa)])
            barra.deficitBarra[(iter, i_no.codigo)] = def
            #println("Ilha: " , ilha.codigo, " Barra: ", barra.codigo, "GerBarra: ", barra.potenciaGerada[(iter, est, i_no.codigo)], " Carga: ", barra.carga[est], " Deficit: ", get(barra.deficitBarra,(iter, est, i_no.codigo),0), " PotLiq: ", get(barra.potenciaLiquida,(iter, est, i_no.codigo),0) )
        end
    end

    function verificaFluxosViolados(iter, est, i_no, ilha, mapa_ilha_fluxos_violados)
        #for barra in ilha.barras
        #    println("Ilha: " , ilha.codigo, " Barra: ", barra.codigo, " GerBarra: ", get(barra.potenciaGerada,(est, i_no.codigo, barra.codigo),0), " Carga: ", barra.carga[est], " Deficit: ", get(barra.deficitBarra,(est, i_no.codigo, barra.codigo),0), " PotLiq: ", get(barra.potenciaLiquida,(est, i_no.codigo, barra.codigo),0) )
        #end
        calculaFluxosIlhaMetodoSensibilidadeDC(ilha,iter, est, i_no)
        #println("EXECUTANDO FLUXO DC PARA O ITERACAO $iter ESTAGIO  $est Node: $(i_no.codigo)")
        contador_violacao = 0
        for linha in ilha.linhasAtivas[est]
            #println("De: ", linha.de.codigo, " Para: ", linha.para.codigo, " Fluxo: ", linha.fluxoDePara[iter,est,i_no.codigo], " Capacidade: ", linha.Capacidade[est], " Linha: ", linha.linhaMatrizSensibilidade[est], " RHS: ", linha.RHS[est])
            #if abs(round(linha.fluxoDePara[iter,est,i_no.codigo], digits=1)) > linha.Capacidade[est] 
            if linha in mapa_ilha_fluxos_violados[i_no.codigo, ilha.codigo]
                #print("Violacao Já existe da linha de ", linha.de.codigo , " para ", linha.para.codigo)
            else
                #println("VIOLADO: De: ", linha.de.codigo, " Para: ", linha.para.codigo, " Fluxo: ", round(linha.fluxoDePara[iter,est,i_no.codigo], digits=1), " Capacidade: ", linha.Capacidade[est], " Linha: ", linha.linhaMatrizSensibilidade[est], " RHS: ", linha.RHS[est])
                push!(mapa_ilha_fluxos_violados[i_no.codigo, ilha.codigo], linha)    
                contador_violacao = contador_violacao + 1
            end
            #end
        end
        return contador_violacao
    end

    #println(df_arvore)

    mapa_ilha_fluxos_violados = OrderedDict{Tuple{Int, Int}, Set{LinhaConfig}}()
    for i_no in lista_total_de_nos, ilha in lista_ilhas_eletricas mapa_ilha_fluxos_violados[i_no.codigo, ilha.codigo] = Set() end

    @time begin
        for it in 1:caso.n_iter
            for est in 1:caso.n_est
                for i_no in mapa_periodos[est].nos    
                    etapa = "FW"     
                    numerosViolacoes = Dict{Tuple{Int, Int, Int}, Int}()
                    #for miniIt in 1:caso.n_iter
                    m = retornaModelo(est,i_no, etapa)
                    if est < caso.n_est && it > 1
                        #for iter in 1:caso.n_iter
                        #    for filho in i_no.filhos
                        #        @constraint(m, alpha_vars[(i_no.codigo,etapa)] - sum(vf_vars[(i_no.codigo, uhe.nome,etapa)]*FCF_coef[iter, filho.codigo, uhe.codigo] for uhe in lista_uhes)   >= FCF_indep[iter, filho.codigo] ) #linha, coluna
                        #    end
                        #end
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
                            @constraint(m, alpha_vars[(i_no.codigo,etapa)] - sum(vf_vars[(i_no.codigo, uhe.nome,etapa)]*dict_vfvars_coef[uhe.codigo] for uhe in lista_uhes)   >= indep_equivalente ) #linha, coluna
                            #for filho in i_no.filhos
                            #    @constraint(m, alpha_vars[(i_no.codigo,etapa)] - sum(vf_vars[(i_no.codigo, uhe.nome,etapa)]*FCF_coef[iter, filho.codigo, uhe.codigo] for uhe in lista_uhes)   >= FCF_indep[iter, filho.codigo] ) #linha, coluna
                            #end
                        end
                    end

                    #for ilha in lista_ilhas_eletricas
                    #    add_fluxo_constrains(m, est, i_no, ilha, mapa_ilha_fluxos_violados, folga_rede)
                    #end
                    JuMP.optimize!(m) 
                    #println(m) 
                    #for ilha in lista_ilhas_eletricas
                    #    transfere_resultados_para_Barras(ilha, it, est, i_no)
                    #    numerosViolacoes[miniIt, i_no.codigo, ilha.codigo] = verificaFluxosViolados(it, est, i_no, ilha, mapa_ilha_fluxos_violados)
                    #end
                    #println("est: ", est, " it: ", it, " miniIt: ", miniIt, " i_no: ", i_no.codigo)
                    imprimePolitica(etapa, est, it, 0, i_no)
                    #iter_sum = sum(v for (k, v) in numerosViolacoes if k[1] == miniIt)
                    #if iter_sum == 0
                    #    #println("Mini-Iteração $miniIt: TERMINOU SEM MAIS VIOLAÇÕES DE FLUXO")
                    #    break
                    #else
                    #    #println("Mini-Iteração $miniIt: Continuando, ainda existem $iter_sum violações")
                    #end
                    #end
                    #########################

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
            end 
            
            println(CustoF)
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
                    #println("no: ", no.codigo, " custo: ", CI_no)
                    for prob in lista_probs_caminho
                        CI_no = CI_no*prob
                    end
                    #println("no: ", no.codigo, " custo: ", CI_no)
                    zsup += CI_no
                end
                #print("est: ", est, " zsup: ", zsup)
            end
            
            gap = ((zsup-zinf)/zsup) 
            lista_zinf[it] = zinf
            lista_zsup[it] = zsup
            lista_gap[it] = gap
            println(" lista_zinf: ", lista_zinf )
            println(" lista_zsup: ", lista_zsup )
            println(" lista_gap: ", lista_gap )
            push!(df_convergencia, (iter = it, ZINF = zinf, ZSUP = zsup))
            if gap < 0.001
                println("CONVERGIU")
                break
            end

            # ETAPA BACKWARD
            if it != caso.n_iter
                for est in caso.n_est:-1:1 
                    println("est: ", est)
                    for i_no in mapa_periodos[est].nos 
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
                                @constraint(m, alpha_vars[(i_no.codigo,etapa)] - sum(vf_vars[(i_no.codigo, uhe.nome,etapa)]*dict_vfvars_coef[uhe.codigo] for uhe in lista_uhes)   >= indep_equivalente ) #linha, coluna
                                #for filho in i_no.filhos
                                #    @constraint(m, alpha_vars[(i_no.codigo,etapa)] - sum(vf_vars[(i_no.codigo, uhe.nome,etapa)]*FCF_coef[iter, filho.codigo, uhe.codigo] for uhe in lista_uhes)   >= FCF_indep[iter, filho.codigo] ) #linha, coluna
                                #end
                            end
                        end

                        #for ilha in lista_ilhas_eletricas
                        #    add_fluxo_constrains(m, est, i_no, ilha, mapa_ilha_fluxos_violados, folga_rede)
                        #end
                        JuMP.optimize!(m) 
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
                            dual_balanco_hidrico = JuMP.shadow_price( constraint_dict[(i_no.codigo, uhe.nome, etapa)])
                            FCF_coef[it, i_no.codigo, uhe.codigo]  = FCF_coef[it, i_no.codigo, uhe.codigo] + dual_balanco_hidrico#*probabilidade_no
                            FCF_indep[it, i_no.codigo] = FCF_indep[it, i_no.codigo] - dual_balanco_hidrico*Vi[(i_no.codigo,uhe.codigo, etapa)]#*probabilidade_no
                            println("est: ", est, " iter: ", it, " no: ", i_no.codigo," usi: ", uhe.codigo, " dual bal: ", dual_balanco_hidrico, " c_pres: ", custo_presente, " c_fut: ", custo_futuro, " Vi[i_no.codigo,i]: ", Vi[(i_no.codigo,uhe.codigo, etapa)], " FCF_coef: ", FCF_coef[it, i_no.codigo, uhe.codigo], " FCF_indep: ", FCF_indep[it, i_no.codigo])
                        end
                        imprimePolitica("BK", est, it, 0, i_no)
                        for usi in lista_uhes
                            push!(df_cortes, (est = est, no = i_no.codigo, iter = it, usina = usi.codigo, Indep = FCF_indep[it, i_no.codigo], Coef = FCF_coef[it, i_no.codigo, usi.codigo]))
                        end
                    end
                end 
            end
        end
    end
    #fig = plot(1:caso.n_iter, [zinf,zsup],size=(800,400), margin=10mm)
    #savefig(fig, "myplot.png")

    df_balanco_energetico_fw = df_balanco_energetico[(df_balanco_energetico.etapa .== "FW"), :]
    df_balanco_energetico_bk = df_balanco_energetico[(df_balanco_energetico.etapa .== "BK"), :]

    max_iter = maximum(df_balanco_energetico.iter)
    df_balanco_energetico_sf = df_balanco_energetico[(df_balanco_energetico.etapa .== "FW") .& (df_balanco_energetico.iter .== max_iter), :]

    df_termicas_fw = df_termicas[(df_termicas.etapa .== "FW"), :]
    df_termicas_bk = df_termicas[(df_termicas.etapa .== "BK"), :]
    df_termicas_sf = df_termicas[(df_termicas.etapa .== "FW") .&& (df_termicas.iter .== max_iter), :]

    df_hidreletricas_fw = df_hidreletricas[(df_hidreletricas.etapa .== "FW"), :]
    df_hidreletricas_bk = df_hidreletricas[(df_hidreletricas.etapa .== "BK"), :]
    df_hidreletricas_sf = df_hidreletricas[(df_hidreletricas.etapa .== "FW") .&& (df_hidreletricas.iter .== max_iter), :]

    df_barras_fw = df_barras[(df_barras.etapa .== "FW"), :]
    df_barras_bk = df_barras[(df_barras.etapa .== "BK"), :]
    df_barras_sf = df_barras[(df_barras.etapa .== "FW") .&& (df_barras.iter .== max_iter), :]

    df_linhas_fw = df_linhas[(df_linhas.etapa .== "FW"), :]
    df_linhas_bk = df_linhas[(df_linhas.etapa .== "BK"), :]
    df_linhas_sf = df_linhas[(df_linhas.etapa .== "FW") .&& (df_linhas.iter .== max_iter), :]


    
    df_per_balanco_energetico = DataFrame(etapa = String[], iter = Int[], miniIter = Int[], est = Int[], Demanda = Float64[], GT = Float64[], GH = Float64[], Deficit = Float64[], CustoPresente = Float64[], CustoFuturo = Float64[])
    for est_value in unique(df_balanco_energetico.est)
        subset = df_balanco_energetico_sf[df_balanco_energetico_sf.est .== est_value, :]
        for iteracao in unique(subset.iter)
            maximaMiniIteracao = maximum(subset[subset.iter .== iteracao, :miniIter]) 
            subsubset = subset[(subset.iter .== iteracao) .& (subset.miniIter .== maximaMiniIteracao), :]
            ProbGT = 0
            ProbGH = 0
            ProbDeficit = 0
            ProbCustoPresente = 0
            ProbCustoFuturo = 0
            Demanda = 0
            for no in unique(subsubset.node)
                ProbGT += (subsubset[(subsubset.node .== no), "GT"][1])*(mapaProbCondicionalNo[no])
                ProbGH += (subsubset[(subsubset.node .== no), "GH"][1])*(mapaProbCondicionalNo[no])
                ProbDeficit += (subsubset[(subsubset.node .== no), "Deficit"][1])*(mapaProbCondicionalNo[no])
                ProbCustoPresente += (subsubset[(subsubset.node .== no), "CustoPresente"][1])*(mapaProbCondicionalNo[no])
                ProbCustoFuturo += (subsubset[(subsubset.node .== no), "CustoFuturo"][1])*(mapaProbCondicionalNo[no])
                Demanda += (subsubset[(subsubset.node .== no), "Demanda"][1])*(mapaProbCondicionalNo[no])
            end
            dem = (subset[(subset.est .== est_value), "Demanda"][1])
            push!(df_per_balanco_energetico, (etapa = "SF", iter = iteracao, miniIter = maximaMiniIteracao, est = est_value, Demanda = dem, GT = ProbGT, GH = ProbGH, Deficit = ProbDeficit, CustoPresente = ProbCustoPresente , CustoFuturo = ProbCustoFuturo))
        end
    end
    df_per_balanco_energetico = sort(df_per_balanco_energetico, :iter)
    println(df_per_balanco_energetico)

    CSV.write("PDD/balanco_energetico_fw.csv", df_balanco_energetico_fw)
    CSV.write("PDD/balanco_energetico_bk.csv", df_balanco_energetico_bk)
    CSV.write("PDD/balanco_energetico_sf.csv", df_balanco_energetico_sf)
    CSV.write("PDD/termicas_fw.csv", df_termicas_fw)
    CSV.write("PDD/termicas_bk.csv", df_termicas_bk)
    CSV.write("PDD/termicas_sf.csv", df_termicas_sf)
    CSV.write("PDD/hidreletricas_fw.csv", df_hidreletricas_fw)
    CSV.write("PDD/hidreletricas_bk.csv", df_hidreletricas_bk)
    CSV.write("PDD/hidreletricas_sf.csv", df_hidreletricas_sf)
    CSV.write("PDD/convergencia.csv", df_convergencia)
    CSV.write("PDD/df_cortes.csv", df_cortes)
    CSV.write("PDD/barras_fw.csv", df_barras_fw)
    CSV.write("PDD/barras_bk.csv", df_barras_bk)
    CSV.write("PDD/barras_sf.csv", df_barras_sf)
    CSV.write("PDD/linhas_fw.csv", df_linhas_fw)
    CSV.write("PDD/linhas_bk.csv", df_linhas_bk)
    CSV.write("PDD/linhas_sf.csv", df_linhas_sf)
    CSV.write("PDD/eco/dat_prob.csv", dat_prob)
    CSV.write("PDD/eco/dat_vaz.csv", dat_vaz)
    CSV.write("PDD/eco/df_arvore.csv", df_arvore)

end