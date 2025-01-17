module Main

    using JuMP, GLPK, Plots, Measures, Plots, SparseArrays, DataFrames

    include("arvore.jl")
    include("CapacidadeLinhas.jl")

    #for ilha in lista_ilhas
    #    #calculaFluxosIlhaMetodoDeltaDC(ilha)
    #    calculaFluxosIlhaMetodoSensibilidadeDC(ilha)
    #    println("EXECUTANDO FLUXO DC")
    #    for fluxo in ilha.fluxo_linhas
    #        println("De: ", fluxo.linha.de.codigo, " Para: ", fluxo.linha.para.codigo, " Fluxo: ", fluxo.fluxoDePara)
    #    end
    #end

    #Inicializando variaveis da barra
    for ilha in lista_ilhas_eletricas
        for est in 1:caso.n_est
            for i_no in mapa_periodos[est].nos
                for barra in ilha.barras
                    barra.potenciaGerada[(est, i_no.codigo, barra.codigo) ] = 0
                    barra.potenciaLiquida[(est, i_no.codigo, barra.codigo) ] = 0
                    barra.deficitBarra[(est, i_no.codigo, barra.codigo) ] = 0
                end
            end
        end
    end


    println("codigo: ", no1.codigo, " codigo_intero: ", no1.index, " nivel: ", no1.periodo , " pai: ", no1.pai)
    printa_nos(no1)
    #println(dat_horas)
    println(dat_vaz)

    conversao_m3_hm3 = (60*60)/1000000

    Vi = Dict{Tuple{Int,Int}, Float64}()
    for no in lista_total_de_nos
        for uhe in lista_uhes
            if no.codigo == 1
                Vi[no.codigo, uhe.codigo] = uhe.v0
            else
                Vi[no.codigo, uhe.codigo] = 0
            end
        end
    end
    #println(Vi)
    #exit(1)
    #global Vi = zeros(length(lista_total_de_nos) ,caso.n_uhes)
    #[Vi[1,i] = lista_uhes[i].v0 for i in 1:caso.n_uhes]
    #println(Vi)
    #exit(1)
    #FCF_coef = zeros(caso.n_est,caso.n_uhes, caso.n_iter)
    #FCF_indep = zeros(caso.n_est, caso.n_iter)

    FCF_coef = OrderedDict{Tuple{Int,Int,Int}, Float64}()
    FCF_indep = OrderedDict{Tuple{Int,Int}, Float64}()
    for est in 1:caso.n_est, uhe in lista_uhes, it in 1:caso.n_iter
        FCF_coef[(est, uhe.codigo, it)] = 0.0
    end
    # Initialize FCF_indep with zeros
    for est in 1:caso.n_est, it in 1:caso.n_iter
        FCF_indep[(est, it)] = 0.0
    end

    #zinf = zeros(caso.n_iter) 
    #zsup = zeros(caso.n_iter)
    zinf = OrderedDict{Int, Float64}()
    zsup = OrderedDict{Int, Float64}()
    for it in 1:caso.n_iter
        zinf[it] = 0.0
        zsup[it] = 0.0
    end

    df_balanco_energetico = DataFrame(etapa = String[], iter = Int[], miniIter = [], est = Int[], node = Int[],  ilha = Int[], Demanda = Float64[], GT = Float64[], GH = Float64[], Deficit = Float64[], CustoPresente = Float64[], CustoFuturo = Float64[])
    df_termicas           = DataFrame(etapa = String[], iter = Int[], miniIter = [], est = Int[], node = Int[], nome = String[] , usina = Int[], generation = Float64[], custo = Float64[], custoTotal = Float64[])
    df_hidreletricas      = DataFrame(etapa = String[], iter = Int[], miniIter = [], est = Int[], node = Int[], nome = String[] ,usina = Int[], generation = Float64[], VI = Float64[], AFL = Float64[], TURB = Float64[], VERT = Float64[], VF = Float64[])
    df_convergencia    = DataFrame(iter = Int[], ZINF = Float64[], ZSUP = Float64[])
    df_cortes          = DataFrame(est = Int[], iter = Int[], usina = Int[], Indep = Float64[], Coef = Float64[])
    df_barras             = DataFrame(etapa = String[], iter = Int[], miniIter = [], est = Int[], node = Int[], ilha = Int[], codigoBarra = Int[], generation = Float64[], demanda = Float64[], potenciaLiquida = Float64[], deficit = Float64[])
    df_linhas             = DataFrame(etapa = String[], iter = Int[], miniIter = [], est = Int[], node = Int[], ilha = Int[], codigoBarraDE = Int[], codigoBarraPARA = Int[], capacidade = Float64[], fluxo = Float64[], folga = Float64[])

    ger_vars = Dict{Tuple{Int,Int, Int}, JuMP.VariableRef}()
    gt_vars = Dict{Tuple{Int, Int, String}, JuMP.VariableRef}()
    gh_vars = Dict{Tuple{Int, Int, String}, JuMP.VariableRef}()
    turb_vars = Dict{Tuple{Int, Int, String}, JuMP.VariableRef}()
    vert_vars = Dict{Tuple{Int, Int, String}, JuMP.VariableRef}()
    vf_vars = Dict{Tuple{Int, Int, String}, JuMP.VariableRef}()
    deficit_vars = Dict{Tuple{Int, Int}, JuMP.VariableRef}()
    folga_rede = Dict{Tuple{Int, Int, LinhaConfig}, JuMP.VariableRef}()
    deficit_barra = Dict{Tuple{Int, Int, Int}, JuMP.VariableRef}()
    folga_rede = Dict{Tuple{Int, Int, LinhaConfig}, JuMP.VariableRef}()
    function retornaModelo(est, no)
        #converte_m3s_hm3 = (conversao_m3_hm3*dat_horas[(dat_horas.PERIODO .== no.periodo), "HORAS"][1])
        global m = Model(GLPK.Optimizer)
        for term in lista_utes
            gt_vars[(est, no.codigo, term.nome)] = @variable(m, base_name="gt_$(est)_$(no.codigo)_$(term.codigo)")
        end
        for uhe in lista_uhes
            gh_vars[(est, no.codigo, uhe.nome)] = @variable(m, base_name="gh_$(est)_$(no.codigo)_$(uhe.codigo)")
            turb_vars[(est, no.codigo, uhe.nome)] = @variable(m, base_name="turb_$(est)_$(no.codigo)_$(uhe.codigo)")
            vert_vars[(est, no.codigo, uhe.nome)] = @variable(m, base_name="vert_$(est)_$(no.codigo)_$(uhe.codigo)")
            vf_vars[(est, no.codigo, uhe.nome)] = @variable(m, base_name="vf_$(est)_$(no.codigo)_$(uhe.codigo)")
        end
        deficit_vars[(est, no.codigo)] = @variable(m, base_name="def_$(est)_$(no.codigo)")
        for ilha in lista_ilhas_eletricas ##QUESTAO AQUI, ESTA DECLARANDO TODOS OS GERADORES NA RESTRICAO DA ILHA, CONSIDERANDO QUE SO EXISTE UMA ILHA. CASO EXISTA MAIS DE UMA, E NECESSARIO CADASTRAR APENAS OS GERADORES DAQUELA ILHA NA RESTRICAO DE DEMANDA
            for barra in ilha.barrasAtivas[est]
                deficit_barra[(est, no.codigo, barra.codigo)] = @variable(m, base_name="deficitBarra_$(est)_$(no.codigo)_$(barra.codigo)")
            end
        end

        @variable(m, 0 <= alpha )

        for uhe in lista_uhes
            @constraint(  m, gh_vars[(est, no.codigo, uhe.nome)] >= 0 ) 
            @constraint(  m, turb_vars[(est, no.codigo, uhe.nome)] >= 0 ) 
            @constraint(  m, vert_vars[(est, no.codigo, uhe.nome)] >= 0 ) 
            @constraint(  m, vf_vars[(est, no.codigo, uhe.nome)] >= 0 ) 

            @constraint(m, gh_vars[(est, no.codigo, uhe.nome)] == turb_vars[(est, no.codigo, uhe.nome)]) #linha, coluna      /converte_m3s_hm3
            @constraint(m, turb_vars[(est, no.codigo, uhe.nome)] <= uhe.turbmax) #linha, coluna
            @constraint(m, vf_vars[(est, no.codigo, uhe.nome)] <=  uhe.vmax) #linha, coluna


            @constraint(m, 
            c_hidr[i = 1:caso.n_uhes],
            vf_vars[(est, no.codigo, uhe.nome)] + 
            turb_vars[(est, no.codigo, uhe.nome)] + 
            vert_vars[(est, no.codigo, uhe.nome)]
            == Vi[no.codigo,uhe.codigo] + (dat_vaz[(dat_vaz.NOME_UHE .== uhe.codigo) .& (dat_vaz.NO .== no.codigo), "VAZAO"][1])) #linha, colun * converte_m3s_hm3
        end
        for term in lista_utes
            @constraint(m, gt_vars[(est, no.codigo, term.nome)] >= 0)
            @constraint(m, gt_vars[(est, no.codigo, term.nome)] <= term.gmax) #linha, coluna
        end
        @constraint(  m, deficit_vars[(est, no.codigo)] >= 0 ) 

        @objective(m, Min, sum(term.custo_geracao * gt_vars[(est, no.codigo, term.nome)] for term in lista_utes) 
        + sum(0.01 * vert_vars[(est, no.codigo, uhe.nome)] for uhe in lista_uhes)
        + sistema.deficit_cost*deficit_vars[(est, no.codigo)] 
        +sum(sistema.deficit_cost*deficit_barra[(est, no.codigo, barra.codigo)] for barra in lista_barras)
        + alpha)
        
        if rede_eletrica == 1
            carga_estagio_ilha = 0
            for ilha in lista_ilhas_eletricas ##QUESTAO AQUI, ESTA DECLARANDO TODOS OS GERADORES NA RESTRICAO DA ILHA, CONSIDERANDO QUE SO EXISTE UMA ILHA. CASO EXISTA MAIS DE UMA, E NECESSARIO CADASTRAR APENAS OS GERADORES DAQUELA ILHA NA RESTRICAO DE DEMANDA
                for barra in ilha.barrasAtivas[est]
                    carga_estagio_ilha += barra.carga[est]
                    @constraint(  m, deficit_barra[(est, no.codigo, barra.codigo)] >= 0 ) 
                end
                @constraint(  m, sum(deficit_barra[(est, no.codigo, barra.codigo)] for barra in ilha.barrasAtivas[est]) 
                + sum(gh_vars[(est, no.codigo, uhe.nome)] for uhe in lista_uhes) 
                + sum(gt_vars[(est, no.codigo, term.nome)] for term in lista_utes) == carga_estagio_ilha   )
            end
        else
            @constraint(  m, balanco,
            sum(gh_vars[(est, no.codigo, uhe.nome)] for uhe in lista_uhes) 
            + sum(gt_vars[(est, no.codigo, term.nome)] for term in lista_utes) 
            + deficit_vars[(est, no.codigo)] == sistema.demanda[est]   )
        end

        return m
    end

    function imprimePolitica(text, est, it, miniIter, no)
        converte_m3s_hm3 = (conversao_m3_hm3*dat_horas[(dat_horas.PERIODO .== no.periodo), "HORAS"][1])
        GeracaoHidreletricaTotal = 0
        GeracaoTermicaTotal = 0
        for term in lista_utes
            geracao = JuMP.value(gt_vars[(est, no.codigo, term.nome)])
            push!(df_termicas, (etapa = text, iter = it, miniIter = miniIter , est = est, node = no.codigo, nome = term.nome, usina = term.codigo, generation = round(geracao, digits = 1) , custo = term.custo_geracao, custoTotal = round(geracao, digits = 1)*term.custo_geracao))
            GeracaoTermicaTotal += geracao
        end
        for uhe in lista_uhes
            geracao = JuMP.value(gh_vars[(est, no.codigo, uhe.nome)])
            turbinamento = JuMP.value(turb_vars[(est, no.codigo, uhe.nome)]) 
            vertimento = JuMP.value(vert_vars[(est, no.codigo, uhe.nome)]) 
            volumeFinal = JuMP.value(vf_vars[(est, no.codigo, uhe.nome)]) 
            push!(df_hidreletricas, (etapa = text, iter = it, miniIter = miniIter , est = est, node = no.codigo, nome = uhe.nome, usina = uhe.codigo, generation = geracao,
                            VI = Vi[no.codigo,uhe.codigo], AFL = (dat_vaz[(dat_vaz.NOME_UHE .== uhe.codigo) .& (dat_vaz.NO .== no.codigo), "VAZAO"][1]),
                            TURB = turbinamento, 
                            VERT = vertimento, 
                            VF = volumeFinal))
            GeracaoHidreletricaTotal += geracao
        end
        custo_presente = 0
        for term in lista_utes
            custo_presente += JuMP.value.(gt_vars[(est, no.codigo, term.nome)])*term.custo_geracao
        end
        
        def = 0

        if rede_eletrica == 1
            carga_estagio_ilha = 0
            for ilha in lista_ilhas_eletricas ##QUESTAO AQUI, ESTA DECLARANDO TODOS OS GERADORES NA RESTRICAO DA ILHA, CONSIDERANDO QUE SO EXISTE UMA ILHA. CASO EXISTA MAIS DE UMA, E NECESSARIO CADASTRAR APENAS OS GERADORES DAQUELA ILHA NA RESTRICAO DE DEMANDA
                for barra in ilha.barrasAtivas[est]
                    carga_estagio_ilha += barra.carga[est]
                    valor_deficit = JuMP.value(deficit_barra[(est, no.codigo, barra.codigo)])
                    custo_presente += valor_deficit*sistema.deficit_cost
                    def += valor_deficit
                    push!(df_barras,  (etapa = text, iter = it, miniIter = miniIter , est = est, node = no.codigo, ilha = ilha.codigo, codigoBarra = barra.codigo, generation = round(get(barra.potenciaGerada, (it, est, no.codigo), 0), digits = 1), demanda = barra.carga[est], potenciaLiquida = round(get(barra.potenciaLiquida, (it, est, no.codigo), 0), digits = 1), deficit= round(valor_deficit, digits = 1)))
                end
                for linha in ilha.linhasAtivas[est]
                    folga_da_rede = get(folga_rede , (est, no.codigo, linha), 0)
                    if folga_da_rede != 0 
                        valor_folga_rede = JuMP.value(folga_da_rede)
                    else
                        valor_folga_rede = -9999
                    end
                    push!(df_linhas,  (etapa = text, iter = it, miniIter = miniIter , est = est, node = no.codigo, ilha = ilha.codigo, codigoBarraDE = linha.de.codigo, codigoBarraPARA = linha.para.codigo, capacidade = linha.Capacidade[est], fluxo = round(get(linha.fluxoDePara,(it, est, no.codigo),0), digits = 1) ,  folga = valor_folga_rede))
                end
                push!(df_balanco_energetico,  (etapa = text, iter = it, miniIter = miniIter ,est = est, node = no.codigo, ilha = ilha.codigo, Demanda = carga_estagio_ilha, GT = GeracaoTermicaTotal, GH = GeracaoHidreletricaTotal, Deficit = def, CustoPresente = custo_presente, CustoFuturo = JuMP.value(m[:alpha])))
            end
        else
            def = JuMP.value(deficit_vars[(est, no.codigo)])
            custo_presente += def*sistema.deficit_cost
            push!(df_balanco_energetico,  (etapa = text, iter = it, miniIter = miniIter ,est = est, node = no.codigo, ilha = 0, Demanda = sistema.demanda[est], GT = GeracaoTermicaTotal, GH = GeracaoHidreletricaTotal, Deficit = def, CustoPresente = custo_presente, CustoFuturo = JuMP.value(m[:alpha])))
        end
        #push!(df_balanco_energetico,  (etapa = text, iter = it, est = est, node = no.codigo, ilha = 0, Demanda = sistema.demanda[est], GT = GeracaoTermicaTotal, GH = GeracaoHidreletricaTotal, Deficit = Deficit, CustoPresente = retornaCustoPresente(m, est, no), CustoFuturo = JuMP.value(m[:alpha])))
    end


    function retornaCustoPresente(est, no)
        custo_presente = 0
        for term in lista_utes
            geracao = JuMP.value(gt_vars[(est, no.codigo, term.nome)])
            custo_presente += geracao*term.custo_geracao
        end
        if rede_eletrica == 1
            for ilha in lista_ilhas_eletricas 
                for barra in ilha.barrasAtivas[est]
                    valor_deficit = JuMP.value(deficit_barra[(est, no.codigo, barra.codigo)])
                    custo_presente += valor_deficit*sistema.deficit_cost
                end
            end
        else
            custo_presente += JuMP.value(deficit_vars[(est,no.codigo)])*sistema.deficit_cost
        end
        return custo_presente
    end


    function add_fluxo_constrains(m, est, i_no, ilha, mapa_ilha_fluxos_violados, folga_rede)
        for linha in mapa_ilha_fluxos_violados[est, i_no.codigo, ilha.codigo]
            lista_variaveis = []
            for barra in ilha.barrasAtivas[est]
                if barra.codigo != ilha.slack.codigo
                    usi = get(mapa_codigoBARRA_nomeUSINA,barra.codigo,0)
                    #println("Barra: ", barra.codigo, " NOME_USI: ", usi)
                    UHE = get(mapa_nome_UHE,usi,0)
                    UTE = get(mapa_nome_UTE,usi,0)
                    if UHE != 0 push!(lista_variaveis, gh_vars[(est, i_no.codigo, UHE.nome)]) end
                    if UTE != 0   push!(lista_variaveis, gt_vars[(est, i_no.codigo, UTE.nome)]) end
                    
                    if UHE == 0 && UTE == 0 
                        variavel = deficit_barra[(est, i_no.codigo, barra.codigo)]
                        push!(lista_variaveis,variavel)
                    end
                end
            end
            fator = ifelse(linha.RHS[est] <= 0, -1 , 1)
            folga_rede[(est, i_no.codigo, linha)] = @variable(m, base_name="sFluxo_$(est)_$(i_no.codigo)_$(linha.de.codigo)_$(linha.para.codigo)")
            @constraint(m, folga_rede[(est, i_no.codigo, linha)] >= 0)
            #@constraint(m, folga_rede[(est, i_no.codigo, fluxo.linha)] <= 2*fluxo.linha.Capacidade[est])
            @constraint(m, folga_rede[(est, i_no.codigo, linha)] <= 2*linha.Capacidade[est])
            #@constraint(m, folga_rede[(est, i_no.codigo, fluxo.linha)] <= fator*fluxo.RHS)
            @constraint(  m, sum(fator*linha.linhaMatrizSensibilidade[est][i]*lista_variaveis[i] for i in 1:length(lista_variaveis)) + fator*folga_rede[(est, i_no.codigo, linha)] == fator*linha.RHS[est]   )
        end
    end



    function transfere_resultados_para_Barras(ilha, iter, est, i_no)
        for barra in ilha.barrasAtivas[est]
            geracao = 0
            nome_usi = get(mapa_codigoBARRA_nomeUSINA, barra.codigo, 0) 
            variavel_gh = get(gh_vars, (est, i_no.codigo, nome_usi), 0)
            variavel_gt = get(gt_vars, (est, i_no.codigo, nome_usi), 0)
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

            barra.potenciaGerada[iter, est, i_no.codigo] = geracao

            def = JuMP.value(deficit_barra[(est, i_no.codigo, barra.codigo)])
            barra.deficitBarra[(iter, est, i_no.codigo)] = def
            println("Ilha: " , ilha.codigo, " Barra: ", barra.codigo, "GerBarra: ", barra.potenciaGerada[(iter, est, i_no.codigo)], " Carga: ", barra.carga[est], " Deficit: ", get(barra.deficitBarra,(iter, est, i_no.codigo),0), " PotLiq: ", get(barra.potenciaLiquida,(iter, est, i_no.codigo),0) )
        end
    end

    function verificaFluxosViolados(iter, est, i_no, ilha, mapa_ilha_fluxos_violados)
        #for barra in ilha.barras
        #    println("Ilha: " , ilha.codigo, " Barra: ", barra.codigo, " GerBarra: ", get(barra.potenciaGerada,(est, i_no.codigo, barra.codigo),0), " Carga: ", barra.carga[est], " Deficit: ", get(barra.deficitBarra,(est, i_no.codigo, barra.codigo),0), " PotLiq: ", get(barra.potenciaLiquida,(est, i_no.codigo, barra.codigo),0) )
        #end
        calculaFluxosIlhaMetodoSensibilidadeDC(ilha,iter, est, i_no)
        println("EXECUTANDO FLUXO DC PARA O ITERACAO $iter ESTAGIO  $est Node: $(i_no.codigo)")
        contador_violacao = 0
        for linha in ilha.linhasAtivas[est]
            println("De: ", linha.de.codigo, " Para: ", linha.para.codigo, " Fluxo: ", linha.fluxoDePara[iter,est,i_no.codigo], " Capacidade: ", linha.Capacidade[est], " Linha: ", linha.linhaMatrizSensibilidade[est], " RHS: ", linha.RHS[est])
            if abs(round(linha.fluxoDePara[iter,est,i_no.codigo], digits=1)) > linha.Capacidade[est] 
                println("VIOLADO: De: ", linha.de.codigo, " Para: ", linha.para.codigo, " Fluxo: ", round(linha.fluxoDePara[iter,est,i_no.codigo], digits=1), " Capacidade: ", linha.Capacidade[est], " Linha: ", linha.linhaMatrizSensibilidade[est], " RHS: ", linha.RHS[est])
                push!(mapa_ilha_fluxos_violados[est, i_no.codigo, ilha.codigo], linha)    
                contador_violacao = contador_violacao + 1
            end
        end
        return contador_violacao
    end


    mapa_ilha_fluxos_violados = OrderedDict{Tuple{Int, Int, Int}, Set{LinhaConfig}}()
    for est in 1:caso.n_est, i_no in mapa_periodos[est].nos, ilha in lista_ilhas_eletricas mapa_ilha_fluxos_violados[est, i_no.codigo, ilha.codigo] = Set() end

    
    for it in 1:caso.n_iter
        #ETAPA FORWARD
        for est in 1:caso.n_est
            for i_no in mapa_periodos[est].nos


                ###########################
                numerosViolacoes = Dict{Tuple{Int, Int, Int, Int}, Int}()
                for miniIt in 1:caso.n_iter
                    m = retornaModelo(est,i_no)
                    if est < caso.n_est && it > 1
                        #@constraint(m, [iter = 1:caso.n_iter], m[:alpha] - sum(m[:Vf][i]*FCF_coef[est+1,i,iter] for i in 1:caso.n_uhes)   >= FCF_indep[est+1,iter] ) #linha, coluna
                        @constraint(m, [iter = 1:caso.n_iter], m[:alpha] - sum(vf_vars[(est, i_no.codigo, lista_uhes[i].nome)]*FCF_coef[est+1,i,iter] for i in 1:caso.n_uhes)   >= FCF_indep[est+1,iter] ) #linha, coluna
                    end
                    for ilha in lista_ilhas_eletricas
                        add_fluxo_constrains(m, est, i_no, ilha, mapa_ilha_fluxos_violados, folga_rede)
                    end
                    JuMP.optimize!(m) 
                    println(m) 
                    
                    
                    contador = 0
                    for ilha in lista_ilhas_eletricas
                        transfere_resultados_para_Barras(ilha, it, est, i_no)
                        numerosViolacoes[miniIt, est, i_no.codigo, ilha.codigo] = verificaFluxosViolados(it, est, i_no, ilha, mapa_ilha_fluxos_violados)
                    end

                    imprimePolitica("FORWARD", est, it, miniIt, i_no)

                    iter_sum = sum(v for (k, v) in numerosViolacoes if k[1] == miniIt)
                    if iter_sum == 0
                        println("Mini-Iteração $miniIt: TERMINOU SEM MAIS VIOLAÇÕES DE FLUXO")
                        break
                    else
                        println("Mini-Iteração $miniIt: Continuando, ainda existem $iter_sum violações")
                    end
                end
                
                #########################


                if est < caso.n_est
                    i_filhos = i_no.filhos
                    for i_filho in i_filhos
                        for uhe in lista_uhes
                            Vi[i_filho.codigo,uhe.codigo] = JuMP.value(vf_vars[(est, i_no.codigo, uhe.nome)])
                        end
                    end
                end

                custo_presente = retornaCustoPresente(est, i_no)
                custo_futuro = JuMP.value(m[:alpha])
                zsup[it] = zsup[it] + custo_presente*(dat_prob[(dat_prob.NO .== i_no.codigo), "PROBABILIDADE"][1])
                if est == 1 zinf[it] = custo_presente+custo_futuro end
                
            end
        end 
        println("zinf: ", zinf, " zsup: ", zsup)
        push!(df_convergencia, (iter = it, ZINF = zinf[it], ZSUP = zsup[it]))
        if abs(zinf[it]-zsup[it]) < 1 
            println("CONVERGIU")
            break
        end

        # ETAPA BACKWARD
        if it != caso.n_iter
            for est in caso.n_est:-1:1 
                for i_no in mapa_periodos[est].nos  
                    m = retornaModelo(est, i_no)
                    if est < caso.n_est && est > 1
                        #@constraint(m, [iter = 1:caso.n_iter], m[:alpha] -sum(m[:Vf][i]*FCF_coef[est+1,i,iter] for i in 1:caso.n_uhes) >= FCF_indep[est+1,iter] ) #linha, coluna
                        @constraint(m, [iter = 1:caso.n_iter], m[:alpha] - sum(vf_vars[(est, i_no.codigo, lista_uhes[i].nome)]*FCF_coef[est+1,i,iter] for i in 1:caso.n_uhes)   >= FCF_indep[est+1,iter] ) #linha, coluna
                    end
                    

                    #for ilha in lista_ilhas_eletricas
                    #    add_fluxo_constrains(m, est, i_no, ilha, mapa_ilha_fluxos_violados, folga_rede)
                    #end
    
                    JuMP.optimize!(m) 
                    #println(m) 
                    
    
                    #for ilha in lista_ilhas_eletricas
                    #    transfere_resultados_para_Barras(ilha, it, est, i_no)
                    #    verificaFluxosViolados(it, est, i_no, ilha, mapa_ilha_fluxos_violados)
                    #end
    
                    #print(m)
                    #JuMP.optimize!(m)


                    custo_presente = retornaCustoPresente(est, i_no)
                    custo_futuro = JuMP.value(m[:alpha])
                    probabilidade_no = (dat_prob[(dat_prob.NO .== i_no.codigo), "PROBABILIDADE"][1])
                    FCF_indep[est, it] = FCF_indep[est, it] + (custo_presente + custo_futuro)*probabilidade_no
                    for i in 1:caso.n_uhes
                        dual_balanco_hidrico = JuMP.shadow_price( m[:c_hidr][i])
                        #FCF_coef[est,i, it]  = FCF_coef[est,i, it] + dual_balanco_hidrico*probabilidade_no
                        FCF_coef[est,i, it]  = FCF_coef[est,i, it] + dual_balanco_hidrico*probabilidade_no
                        FCF_indep[est, it] = FCF_indep[est, it] - dual_balanco_hidrico*Vi[i_no.codigo,i]*probabilidade_no
                        println("est: ", est, " iter: ", it, " no: ", i_no.codigo," usi: ", i, " dual bal: ", dual_balanco_hidrico, " c_pres: ", custo_presente, " c_fut: ", custo_futuro, " Vi[i_no.codigo,i]: ", Vi[i_no.codigo,i], "FCF_coef[est,i, it]: ", FCF_coef[est,i, it], "FCF_indep[est, it]: ", FCF_indep[est, it])

                    end
                    imprimePolitica("BACKWARD", est, it, 0, i_no)
                    

                end
                for usi in 1:caso.n_uhes
                    push!(df_cortes, (est = est, iter = it, usina = usi, Indep = FCF_indep[est, it], Coef = FCF_coef[est,usi, it]))
                end
            end 
        end
    end
    
    #fig = plot(1:caso.n_iter, [zinf,zsup],size=(800,400), margin=10mm)
    #savefig(fig, "myplot.png")

    df_balanco_energetico_fw = df_balanco_energetico[(df_balanco_energetico.etapa .== "FORWARD"), :]
    df_balanco_energetico_bk = df_balanco_energetico[(df_balanco_energetico.etapa .== "BACKWARD"), :]

    max_iter = maximum(df_balanco_energetico.iter)
    df_balanco_energetico_sf = df_balanco_energetico[(df_balanco_energetico.etapa .== "FORWARD") .& (df_balanco_energetico.iter .== max_iter), :]

    df_termicas_fw = df_termicas[(df_termicas.etapa .== "FORWARD"), :]
    df_termicas_bk = df_termicas[(df_termicas.etapa .== "BACKWARD"), :]
    df_termicas_sf = df_termicas[(df_termicas.etapa .== "FORWARD") .&& (df_termicas.iter .== max_iter), :]

    df_hidreletricas_fw = df_hidreletricas[(df_hidreletricas.etapa .== "FORWARD"), :]
    df_hidreletricas_bk = df_hidreletricas[(df_hidreletricas.etapa .== "BACKWARD"), :]
    df_hidreletricas_sf = df_hidreletricas[(df_hidreletricas.etapa .== "FORWARD") .&& (df_hidreletricas.iter .== max_iter), :]

    df_barras_fw = df_barras[(df_barras.etapa .== "FORWARD"), :]
    df_barras_bk = df_barras[(df_barras.etapa .== "BACKWARD"), :]
    df_barras_sf = df_barras[(df_barras.etapa .== "FORWARD") .&& (df_barras.iter .== max_iter), :]

    df_linhas_fw = df_linhas[(df_linhas.etapa .== "FORWARD"), :]
    df_linhas_bk = df_linhas[(df_linhas.etapa .== "BACKWARD"), :]
    df_linhas_sf = df_linhas[(df_linhas.etapa .== "FORWARD") .&& (df_linhas.iter .== max_iter), :]


    

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
end