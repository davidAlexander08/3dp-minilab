module Main

    using JuMP, GLPK, Plots, Measures, Plots, SparseArrays

    include("arvore.jl")
    include("FluxoDC.jl")

    #Inicializando variaveis da barra
    for est in caso.n_est
        for i_no in mapa_periodos[est].nos
            for ilha in mapa_estagio_ilha[est]
                for barra in ilha.barras
                    barra.potenciaGerada[(est, i_no.codigo, barra.codigo) ] = 0
                    barra.potenciaLiquida[(est, i_no.codigo, barra.codigo) ] = 0
                    barra.deficitBarra[(est, i_no.codigo, barra.codigo) ] = 0
                end
            end
        end
    end



    ger_vars = Dict{Tuple{Int,Int, Int}, JuMP.VariableRef}()
    gt_vars = Dict{Tuple{Int, Int, String}, JuMP.VariableRef}()
    gh_vars = Dict{Tuple{Int, Int, String}, JuMP.VariableRef}()
    turb_vars = Dict{Tuple{Int, Int, String}, JuMP.VariableRef}()
    vert_vars = Dict{Tuple{Int, Int, String}, JuMP.VariableRef}()
    vf_vars = Dict{Tuple{Int, Int, String}, JuMP.VariableRef}()
    deficit_vars = Dict{Tuple{Int, Int}, JuMP.VariableRef}()
    folga_rede = Dict{Tuple{Int, Int, LinhaConfig}, JuMP.VariableRef}()
    deficit_barra = Dict{Tuple{Int, Int, Int}, JuMP.VariableRef}()

    

    function montaProblemaOtimizacaoBase(m)

        conversao_m3_hm3 = (60*60)/1000000
        global Vi = zeros(length(lista_total_de_nos) ,caso.n_uhes)
        [Vi[1,i] = usi.v0 for usi in lista_uhes]
    

        ## METODO PL UNICO
        for est in 1:caso.n_est
            for i_no in mapa_periodos[est].nos
                #println("i_no: ", i_no.codigo, " est: ", est)
                for term in lista_utes
                    gt_vars[(est, i_no.codigo, term.nome)] = @variable(m, base_name="gt_$(est)_$(i_no.codigo)_$(term.codigo)")
                    ger_vars[(est, i_no.codigo, mapa_nomeUSINA_codigoBARRA[term.nome])] = @variable(m, base_name="gt_$(est)_$(i_no.codigo)_$(term.codigo)")
                    println("EST: ", est, " NO: ", i_no.codigo, " BARRA: ", mapa_nomeUSINA_codigoBARRA[term.nome], " VAR: ", ger_vars[(est, i_no.codigo, mapa_nomeUSINA_codigoBARRA[term.nome])])
                end
                for uhe in lista_uhes
                    gh_vars[(est, i_no.codigo, uhe.nome)] = @variable(m, base_name="gh_$(est)_$(i_no.codigo)_$(uhe.codigo)")
                    turb_vars[(est, i_no.codigo, uhe.nome)] = @variable(m, base_name="turb_$(est)_$(i_no.codigo)_$(uhe.codigo)")
                    vert_vars[(est, i_no.codigo, uhe.nome)] = @variable(m, base_name="vert_$(est)_$(i_no.codigo)_$(uhe.codigo)")
                    vf_vars[(est, i_no.codigo, uhe.nome)] = @variable(m, base_name="vf_$(est)_$(i_no.codigo)_$(uhe.codigo)")
                    ger_vars[(est, i_no.codigo, mapa_nomeUSINA_codigoBARRA[uhe.nome])] = @variable(m, base_name="gh_$(est)_$(i_no.codigo)_$(uhe.codigo)")
                    println("EST: ", est, " NO: ", i_no.codigo, " BARRA: ", mapa_nomeUSINA_codigoBARRA[uhe.nome], " VAR: ", ger_vars[(est, i_no.codigo, mapa_nomeUSINA_codigoBARRA[uhe.nome])])
                end
                deficit_vars[(est, i_no.codigo)] = @variable(m, base_name="def_$(est)_$(i_no.codigo)")
                for ilha in mapa_estagio_ilha[est] ##QUESTAO AQUI, ESTA DECLARANDO TODOS OS GERADORES NA RESTRICAO DA ILHA, CONSIDERANDO QUE SO EXISTE UMA ILHA. CASO EXISTA MAIS DE UMA, E NECESSARIO CADASTRAR APENAS OS GERADORES DAQUELA ILHA NA RESTRICAO DE DEMANDA
                    for barra in ilha.barras
                        deficit_barra[(est, i_no.codigo, barra.codigo)] = @variable(m, base_name="deficitBarra_$(est)_$(i_no.codigo)_$(barra.codigo)")
                    end
                end
            end
        end

        @objective( m, Min, sum(term.custo_geracao * gt_vars[(est, i_no.codigo, term.nome)] for est in 1:caso.n_est, i_no in mapa_periodos[est].nos, term in lista_utes)
        + sum(0.01 * vert_vars[(est, i_no.codigo, uhe.nome)] for est in 1:caso.n_est, i_no in mapa_periodos[est].nos, uhe in lista_uhes)+
        sum(sistema.deficit_cost*deficit_barra[(est, i_no.codigo, barra.codigo)] for est in 1:caso.n_est, i_no in mapa_periodos[est].nos, barra in lista_barras) +
        sum(sistema.deficit_cost * deficit_vars[(est, i_no.codigo)] for est in 1:caso.n_est, i_no in mapa_periodos[est].nos))
        
        for est in 1:caso.n_est
            for i_no in mapa_periodos[est].nos
                if rede_eletrica == 1
                    carga_estagio_ilha = 0
                    for ilha in mapa_estagio_ilha[est] ##QUESTAO AQUI, ESTA DECLARANDO TODOS OS GERADORES NA RESTRICAO DA ILHA, CONSIDERANDO QUE SO EXISTE UMA ILHA. CASO EXISTA MAIS DE UMA, E NECESSARIO CADASTRAR APENAS OS GERADORES DAQUELA ILHA NA RESTRICAO DE DEMANDA
                        for barra in ilha.barras
                            carga_estagio_ilha += barra.carga[est]
                            @constraint(  m, deficit_barra[(est, i_no.codigo, barra.codigo)] >= 0 ) 
                        end
                        @constraint(  m, sum(deficit_barra[(est, i_no.codigo, barra.codigo)] for barra in ilha.barras) + sum(gh_vars[(est, i_no.codigo, uhe.nome)] for uhe in lista_uhes) + sum(gt_vars[(est, i_no.codigo, term.nome)] for term in lista_utes) == carga_estagio_ilha   )
                    end
                else
                    @constraint(  m, sum(gh_vars[(est, i_no.codigo, uhe.nome)] for uhe in lista_uhes) + sum(gt_vars[(est, i_no.codigo, term.nome)] for term in lista_utes) + deficit_vars[(est, i_no.codigo)] == sistema.demanda[est]   )
                end
                    @constraint(  m, deficit_vars[(est, i_no.codigo)] >= 0 ) 
                for term in lista_utes
                    @constraint(m, gt_vars[(est, i_no.codigo, term.nome)] >= 0)
                    @constraint(m, gt_vars[(est, i_no.codigo, term.nome)] <= term.gmax) #linha, coluna
                end
                
                for uhe in lista_uhes
    
                    @constraint(  m, gh_vars[(est, i_no.codigo, uhe.nome)] >= 0 ) 
                    @constraint(  m, turb_vars[(est, i_no.codigo, uhe.nome)] >= 0 ) 
                    @constraint(  m, vert_vars[(est, i_no.codigo, uhe.nome)] >= 0 ) 
                    @constraint(  m, vf_vars[(est, i_no.codigo, uhe.nome)] >= 0 ) 
    
                    @constraint(m, gh_vars[(est, i_no.codigo, uhe.nome)] == turb_vars[(est, i_no.codigo, uhe.nome)]) #linha, coluna      /converte_m3s_hm3
                    @constraint(m, turb_vars[(est, i_no.codigo, uhe.nome)] <= uhe.turbmax) #linha, coluna
                    @constraint(m, vf_vars[(est, i_no.codigo, uhe.nome)] <=  uhe.vmax) #linha, coluna
    
    
                    inflow = dat_vaz[(dat_vaz.NOME_UHE .== i) .& (dat_vaz.NO .== i_no.codigo), "VAZAO"][1]
                    #println("Hydro Plant: ", i, " Stage: ", est, " Node: ", i_no.codigo, " Inflow: ", inflow)
                    
                    if est == 1
                        @constraint(
                            m, 
                            vf_vars[(est, i_no.codigo, uhe.nome)] + 
                            turb_vars[(est, i_no.codigo, uhe.nome)] + 
                            vert_vars[(est, i_no.codigo, uhe.nome)] == 
                            Vi[i_no.codigo, i] + inflow
                        )
                    else
                        @constraint(
                            m, 
                            vf_vars[(est, i_no.codigo, uhe.nome)] + 
                            turb_vars[(est, i_no.codigo, uhe.nome)] + 
                            vert_vars[(est, i_no.codigo, uhe.nome)] == 
                            vf_vars[(est-1, i_no.pai.codigo, uhe.nome)] + inflow
                        )
                    end
                end
            end
        end    

        return m
        
    end



    df_balanco_energetico = DataFrame(iter = Int[], est = Int[], node = Int[], ilha = Int[], Demanda = Float64[], GT = Float64[], GH = Float64[], Deficit = Float64[], CustoPresente = Float64[])
    df_termicas           = DataFrame(iter = Int[], est = Int[], node = Int[], nome = String[] , usina = Int[], generation = Float64[])
    df_hidreletricas      = DataFrame(iter = Int[], est = Int[], node = Int[], nome = String[] ,usina = Int[], generation = Float64[], VI = Float64[], AFL = Float64[], TURB = Float64[], VERT = Float64[], VF = Float64[])
    df_barras             = DataFrame(iter = Int[], est = Int[], node = Int[], ilha = Int[], codigoBarra = Int[], generation = Float64[], demanda = Float64[], potenciaLiquida = Float64[], deficit = Float64[])
    df_linhas             = DataFrame(iter = Int[], est = Int[], node = Int[], ilha = Int[], codigoBarraDE = Int[], codigoBarraPARA = Int[], capacidade = Float64[], fluxo = Float64[], folga = Float64[])



    function imprimeResultadosModelo(it, est, i_no)
        GeracaoHidreletricaTotal = 0
        GeracaoTermicaTotal = 0
        for uhe in lista_uhes
            vf = JuMP.value(vf_vars[(est, i_no.codigo, uhe.nome)])
            turb = JuMP.value(turb_vars[(est, i_no.codigo, uhe.nome)])
            vert = JuMP.value(vert_vars[(est, i_no.codigo, uhe.nome)])
            gh = JuMP.value(gh_vars[(est, i_no.codigo, uhe.nome)])
            GeracaoHidreletricaTotal += gh
            push!(df_hidreletricas,  (iter = it, est = est, node = i_no.codigo, nome = uhe.nome, usina = uhe.codigo, generation = gh, VI = 0 , AFL = 0, TURB = turb, VERT = vert, VF = vf))
        end
            
        for term in lista_utes
            gt = JuMP.value(gt_vars[(est, i_no.codigo, term.nome)])
            GeracaoTermicaTotal += gt
            push!(df_termicas,  (iter = it, est = est, node = i_no.codigo, nome = term.nome, usina = term.codigo, generation = round(gt, digits = 1)))
        end

        

        custo_presente = 0
        for term in lista_utes
            custo_presente += JuMP.value.(gt_vars[(est, i_no.codigo, term.nome)])*term.custo_geracao
        end
        
        def = 0
        if rede_eletrica == 1
            carga_estagio_ilha = 0
            for ilha in mapa_estagio_ilha[1] ##QUESTAO AQUI, ESTA DECLARANDO TODOS OS GERADORES NA RESTRICAO DA ILHA, CONSIDERANDO QUE SO EXISTE UMA ILHA. CASO EXISTA MAIS DE UMA, E NECESSARIO CADASTRAR APENAS OS GERADORES DAQUELA ILHA NA RESTRICAO DE DEMANDA
                for barra in ilha.barras
                    carga_estagio_ilha += barra.carga[est]
                    valor_deficit = JuMP.value(deficit_barra[(est, i_no.codigo, barra.codigo)])
                    custo_presente += valor_deficit*sistema.deficit_cost
                    def += valor_deficit
                    push!(df_barras,  (iter = it, est = est, node = i_no.codigo, ilha = ilha.codigo, codigoBarra = barra.codigo, generation = round(get(barra.potenciaGerada, (it, est, i_no.codigo), 0), digits = 1), demanda = barra.carga[est], potenciaLiquida = round(barra.potenciaLiquida[it, est, i_no.codigo], digits = 1), deficit= round(valor_deficit, digits = 1)))
                end
                for fluxo in ilha.fluxo_linhas
                    folga_da_rede = get(folga_rede , (est, i_no.codigo, fluxo.linha), 0)
                    if folga_da_rede != 0 
                        valor_folga_rede = JuMP.value(folga_da_rede)
                    else
                        valor_folga_rede = -9999
                    end
                    push!(df_linhas,  (iter = it, est = est, node = i_no.codigo, ilha = ilha.codigo, codigoBarraDE = fluxo.de.codigo, codigoBarraPARA = fluxo.para.codigo, capacidade = fluxo.linha.Capacidade[est], fluxo = round(fluxo.fluxoDePara[it, est, i_no.codigo], digits = 1) ,  folga = round(valor_folga_rede, digits = 1)))
                end
                push!(df_balanco_energetico,  (iter = it, est = est, node = i_no.codigo, ilha = ilha.codigo, Demanda = carga_estagio_ilha, GT = GeracaoTermicaTotal, GH = GeracaoHidreletricaTotal, Deficit = def, CustoPresente = custo_presente))
            end
        else
            def = JuMP.value(deficit_vars[(est, i_no.codigo)])
            push!(df_balanco_energetico,  (iter = it, est = est, node = i_no.codigo, ilha = 0, Demanda = sistema.demanda[est], GT = GeracaoTermicaTotal, GH = GeracaoHidreletricaTotal, Deficit = def, CustoPresente = custo_presente))
        end
    end

    numero_iteracoes =  5
    mapa_ilha_fluxos_violados = OrderedDict{Tuple{Int, Int, Int}, Set{FluxoNasLinhas}}()
    for est in 1:caso.n_est, i_no in mapa_periodos[est].nos, ilha in mapa_estagio_ilha[est] mapa_ilha_fluxos_violados[est, i_no.codigo, ilha.codigo] = Set() end
    function add_fluxo_constrains(m, est, i_no, ilha, mapa_ilha_fluxos_violados, folga_rede)
        for fluxo in mapa_ilha_fluxos_violados[est, i_no.codigo, ilha.codigo]
            lista_variaveis = []
            for barra in ilha.barras
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
            fator = ifelse(fluxo.RHS <= 0, -1 , 1)
            folga_rede[(est, i_no.codigo, fluxo.linha)] = @variable(m, base_name="sFluxo_$(est)_$(i_no.codigo)_$(fluxo.de.codigo)_$(fluxo.para.codigo)")
            @constraint(m, folga_rede[(est, i_no.codigo, fluxo.linha)] >= 0)
            #@constraint(m, folga_rede[(est, i_no.codigo, fluxo.linha)] <= 2*fluxo.linha.Capacidade[est])
            @constraint(m, folga_rede[(est, i_no.codigo, fluxo.linha)] <= fluxo.linha.Capacidade[est])
            #@constraint(m, folga_rede[(est, i_no.codigo, fluxo.linha)] <= fator*fluxo.RHS)
            @constraint(  m, sum(fator*fluxo.linhaMatrizSensibilidade[i]*lista_variaveis[i] for i in 1:length(lista_variaveis) ) + fator*folga_rede[(est, i_no.codigo, fluxo.linha)] == fator*fluxo.RHS   )
        end
    end
    


    function transfere_resultados_para_Barras(ilha, iter, est, i_no)
        for barra in ilha.barras
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
            #println("Ilha: " , ilha.codigo, " Barra: ", barra.codigo, "GerBarra: ", barra.potenciaGerada[(iter, est, i_no.codigo)], " Carga: ", barra.carga[est], " Deficit: ", get(barra.deficitBarra,(iter, est, i_no.codigo),0), " PotLiq: ", get(barra.potenciaLiquida,(iter, est, i_no.codigo),0) )
        end
        #for uhe in lista_uhes
        #    uhe.barra.potenciaGerada[iter, est, i_no.codigo] = JuMP.value(gh_vars[(est, i_no.codigo, uhe.nome)])
        #end
        #for ute in lista_utes
        #    ute.barra.potenciaGerada[iter, est, i_no.codigo] = JuMP.value(gt_vars[(est, i_no.codigo, ute.nome)])
        #end
    end

    function verificaFluxosViolados(iter, est, i_no, ilha, mapa_ilha_fluxos_violados)
        #for barra in ilha.barras
        #    println("Ilha: " , ilha.codigo, " Barra: ", barra.codigo, " GerBarra: ", get(barra.potenciaGerada,(est, i_no.codigo, barra.codigo),0), " Carga: ", barra.carga[est], " Deficit: ", get(barra.deficitBarra,(est, i_no.codigo, barra.codigo),0), " PotLiq: ", get(barra.potenciaLiquida,(est, i_no.codigo, barra.codigo),0) )
        #end
        calculaFluxosIlhaMetodoSensibilidadeDC(ilha,iter, est, i_no)
        println("EXECUTANDO FLUXO DC PARA O ITERACAO $iter ESTAGIO  $est Node: $(i_no.codigo)")
        contador_violacao = 0
        for fluxo in ilha.fluxo_linhas
            println("De: ", fluxo.linha.de.codigo, " Para: ", fluxo.linha.para.codigo, " Fluxo: ", fluxo.fluxoDePara[iter,est,i_no.codigo], " Capacidade: ", fluxo.linha.Capacidade[est], " Linha: ", fluxo.linhaMatrizSensibilidade, " RHS: ", fluxo.RHS)
            if abs(round(fluxo.fluxoDePara[iter,est,i_no.codigo], digits=1)) > fluxo.linha.Capacidade[est] 
                println("VIOLADO: De: ", fluxo.linha.de.codigo, " Para: ", fluxo.linha.para.codigo, " Fluxo: ", round(fluxo.fluxoDePara[iter,est,i_no.codigo], digits=1), " Capacidade: ", fluxo.linha.Capacidade[est], " Linha: ", fluxo.linhaMatrizSensibilidade, " RHS: ", fluxo.RHS)
                push!(mapa_ilha_fluxos_violados[est, i_no.codigo, ilha.codigo], fluxo)    
                contador_violacao = contador_violacao + 1
            end
        end
        return contador_violacao
    end

    for iter in 1:numero_iteracoes
        println("ITERACAO: ", iter)
        m = Model(GLPK.Optimizer)
        montaProblemaOtimizacaoBase(m)
        if iter > 1
            for est in 1:caso.n_est
                for i_no in mapa_periodos[est].nos
                    for ilha in mapa_estagio_ilha[est]
                        add_fluxo_constrains(m, est, i_no, ilha, mapa_ilha_fluxos_violados, folga_rede)
                    end
                end
            end
        end

        println("OTIMIZANDO")
        println(m)
        JuMP.optimize!(m) 

            # After optimizing the model
        status = termination_status(m)
        if status == MOI.INFEASIBLE
            println("The problem is infeasible.")
        elseif status == MOI.OPTIMAL
            println("The problem is feasible and optimal.")
        elseif status == MOI.FEASIBLE_POINT
            println("Solver returned a feasible point, but not necessarily optimal.")
        else
            println("Solver returned status: ", status)
        end
       
        contador_violacao = 0
        for est in 1:caso.n_est
            for i_no in mapa_periodos[est].nos
                for ilha in mapa_estagio_ilha[est]
                    transfere_resultados_para_Barras(ilha, iter, est, i_no)
                    contador_violacao = verificaFluxosViolados(iter, est, i_no, ilha, mapa_ilha_fluxos_violados)
                end
                no = i_no.codigo
                println("ITER  $iter ESTAGIO $est  NO  $no")
                imprimeResultadosModelo(iter, est, i_no)
            end
        end

        if contador_violacao == 0
            println("TERMINOU SEM MAIS VIOLACOES DE FLUXO")
            break
        end
    end

    println(df_balanco_energetico)
    println(df_termicas)
    println(df_hidreletricas)
    println(df_barras)
    println(df_linhas)
    df_linhas.fluxo .= round.(df_linhas.fluxo, digits=2)
    CSV.write("PLUNICO/df_balanco_energetico.csv", df_balanco_energetico)
    CSV.write("PLUNICO/df_termicas.csv", df_termicas)
    CSV.write("PLUNICO/df_hidreletricas.csv", df_hidreletricas)
    CSV.write("PLUNICO/df_barras.csv", df_barras)
    CSV.write("PLUNICO/df_linhas.csv", df_linhas)
end



