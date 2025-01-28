module Main

    using JuMP, GLPK, Plots, Measures, Plots, SparseArrays

    include("arvore.jl")
    include("FluxoDC.jl")

    lista_ilhas_teste = mapa_estagio_ilha[1]
    for ilha in lista_ilhas_teste
        #calculaFluxosIlhaMetodoDeltaDC(ilha,1)
        calculaFluxosIlhaMetodoSensibilidadeDC(ilha,1)
        println("EXECUTANDO FLUXO DC")
        for fluxo in ilha.fluxo_linhas
            println("De: ", fluxo.linha.de.codigo, " Para: ", fluxo.linha.para.codigo, " Fluxo: ", fluxo.fluxoDePara)
        end
    end

    global m = Model(GLPK.Optimizer)
    gt_vars = Dict{Tuple{Int, Int}, Vector{JuMP.VariableRef}}()
    gh_vars = Dict{Tuple{Int, Int}, Vector{JuMP.VariableRef}}()
    turb_vars = Dict{Tuple{Int, Int}, Vector{JuMP.VariableRef}}()
    vert_vars = Dict{Tuple{Int, Int}, Vector{JuMP.VariableRef}}()
    vf_vars = Dict{Tuple{Int, Int}, Vector{JuMP.VariableRef}}()
    deficit_vars = Dict{Tuple{Int, Int}, JuMP.VariableRef}()
    folga_rede = Dict{Tuple{Int, Int, LinhaConfig}, JuMP.VariableRef}()

    function montaProblemaOtimizacaoBase()

        #println("codigo: ", no1.codigo, " codigo_intero: ", no1.index, " nivel: ", no1.periodo , " pai: ", no1.pai)
        #printa_nos(no1)
    
        #print(dat_horas)
        conversao_m3_hm3 = (60*60)/1000000
        global Vi = zeros(length(lista_total_de_nos) ,caso.n_uhes)
        [Vi[1,i] = lista_uhes[i].v0 for i in 1:caso.n_uhes]
    

        ## METODO PL UNICO
        for est in 1:caso.n_est
            for i_no in mapa_periodos[est].nos
                #println("i_no: ", i_no.codigo, " est: ", est)
                gt_vars[(est, i_no.codigo)] = @variable(m, [1:caso.n_term], base_name="gt_$(est)_$(i_no.codigo)")
                gh_vars[(est, i_no.codigo)] = @variable(m, [1:caso.n_uhes], base_name="gh_$(est)_$(i_no.codigo)")
                turb_vars[(est, i_no.codigo)] = @variable(m, [1:caso.n_uhes], base_name="turb_$(est)_$(i_no.codigo)")
                vert_vars[(est, i_no.codigo)] = @variable(m, [1:caso.n_uhes], base_name="vert_$(est)_$(i_no.codigo)")
                vf_vars[(est, i_no.codigo)] = @variable(m, [1:caso.n_uhes], base_name="vf_$(est)_$(i_no.codigo)")
                deficit_vars[(est, i_no.codigo)] = @variable(m, base_name="def_$(est)_$(i_no.codigo)")
            end
        end
        @objective( m, Min, sum(lista_utes[i].custo_geracao * gt_vars[(est, i_no.codigo)][i] for est in 1:caso.n_est, i_no in mapa_periodos[est].nos, i in 1:caso.n_term)
        + sum(0.01 * vert_vars[(est, i_no.codigo)][i] for est in 1:caso.n_est, i_no in mapa_periodos[est].nos, i in 1:caso.n_uhes)+
        sum(sistema.deficit_cost * deficit_vars[(est, i_no.codigo)] for est in 1:caso.n_est, i_no in mapa_periodos[est].nos))
        
        #@constraint(m, balanco, sum(m[:gh][i] for i in 1:caso.n_uhes) + sum(m[:gt][i] for i in 1:caso.n_term) + m[:deficit] == sistema.demanda[est])
        #@constraint(m, c_hidr[i = 1:caso.n_uhes], Vf[i] + Turb[i] + Vert[i] == Vi[no.codigo,i] + (dat_vaz[(dat_vaz.NOME_UHE .== i) .& (dat_vaz.NO .== no.codigo), "VAZAO"][1])) #linha, colun * converte_m3s_hm3

        for est in 1:caso.n_est
            for i_no in mapa_periodos[est].nos
                if rede_eletrica == 1
                    carga_estagio_ilha = 0
                    for ilha in mapa_estagio_ilha[est] ##QUESTAO AQUI, ESTA DECLARANDO TODOS OS GERADORES NA RESTRICAO DA ILHA, CONSIDERANDO QUE SO EXISTE UMA ILHA. CASO EXISTA MAIS DE UMA, E NECESSARIO CADASTRAR APENAS OS GERADORES DAQUELA ILHA NA RESTRICAO DE DEMANDA
                        for barra in ilha.barras
                            carga_estagio_ilha += barra.carga[est]
                        end
                        @constraint(  m, sum(gh_vars[(est, i_no.codigo)][i] for i in 1:caso.n_uhes) + sum(gt_vars[(est, i_no.codigo)][i] for i in 1:caso.n_term) + deficit_vars[(est, i_no.codigo)] == carga_estagio_ilha   )
                    end
                else
                    @constraint(  m, sum(gh_vars[(est, i_no.codigo)][i] for i in 1:caso.n_uhes) + sum(gt_vars[(est, i_no.codigo)][i] for i in 1:caso.n_term) + deficit_vars[(est, i_no.codigo)] == sistema.demanda[est]   )
                end
                    @constraint(  m, deficit_vars[(est, i_no.codigo)] >= 0 ) 
                for term in 1:caso.n_term
                    @constraint(m, gt_vars[(est, i_no.codigo)][term] >= 0)
                    @constraint(m, gt_vars[(est, i_no.codigo)][term] <= lista_utes[term].gtmax) #linha, coluna
                end
                
                for i in 1:caso.n_uhes
    
                    @constraint(  m, gh_vars[(est, i_no.codigo)][i] >= 0 ) 
                    @constraint(  m, turb_vars[(est, i_no.codigo)][i] >= 0 ) 
                    @constraint(  m, vert_vars[(est, i_no.codigo)][i] >= 0 ) 
                    @constraint(  m, vf_vars[(est, i_no.codigo)][i] >= 0 ) 
    
                    @constraint(m, gh_vars[(est, i_no.codigo)][i] == turb_vars[(est, i_no.codigo)][i]) #linha, coluna      /converte_m3s_hm3
                    @constraint(m, turb_vars[(est, i_no.codigo)][i] <= lista_uhes[i].turbmax) #linha, coluna
                    @constraint(m, vf_vars[(est, i_no.codigo)][i] <= lista_uhes[i].vmax) #linha, coluna
    
    
                    inflow = dat_vaz[(dat_vaz.NOME_UHE .== i) .& (dat_vaz.NO .== i_no.codigo), "VAZAO"][1]
                    #println("Hydro Plant: ", i, " Stage: ", est, " Node: ", i_no.codigo, " Inflow: ", inflow)
                    
                    if est == 1
                        @constraint(
                            m, 
                            vf_vars[(est, i_no.codigo)][i] + 
                            turb_vars[(est, i_no.codigo)][i] + 
                            vert_vars[(est, i_no.codigo)][i] == 
                            Vi[i_no.codigo, i] + inflow
                        )
                    else
                        @constraint(
                            m, 
                            vf_vars[(est, i_no.codigo)][i] + 
                            turb_vars[(est, i_no.codigo)][i] + 
                            vert_vars[(est, i_no.codigo)][i] == 
                            vf_vars[(est-1, i_no.pai.codigo)][i] + inflow
                        )
                    end
                end
            end
        end    

        return m
        
    end


    function imprimeResultadosModelo(m)
        # Print results
        for est in 1:caso.n_est
            for i_no in mapa_periodos[est].nos
                GeracaoHidreletricaTotal = 0
                GeracaoTermicaTotal = 0
                for i in 1:caso.n_uhes
                    vf = JuMP.value(vf_vars[(est, i_no.codigo)][i])
                    turb = JuMP.value(turb_vars[(est, i_no.codigo)][i])
                    vert = JuMP.value(vert_vars[(est, i_no.codigo)][i])
                    gh = JuMP.value(gh_vars[(est, i_no.codigo)][i])
                    GeracaoHidreletricaTotal += gh
                    #println("Stage: $est, Node: $(i_no.codigo), Hydro Plant: $i, VF: $vf, Turb: $turb, Vert: $vert, Generation: $gh")
                end
                    
                for term in 1:caso.n_term
                    gt = JuMP.value(gt_vars[(est, i_no.codigo)][term])
                    GeracaoTermicaTotal += gt
                    #println("Térmica: $term, Generation: ", gt," est: ", est, " node: ", i_no.codigo)
                end
                def = JuMP.value(deficit_vars[(est, i_no.codigo)])

                custo_presente = 0
                for term in 1:caso.n_term
                    custo_presente += JuMP.value.(gt_vars[(est, i_no.codigo)])[term]*lista_utes[term].custo_geracao
                end
                custo_presente += JuMP.value(deficit_vars[(est, i_no.codigo)])*sistema.deficit_cost
                Demanda = sistema.demanda[est]
                codigo_no = i_no.codigo
                println("Est: $est No: $codigo_no Demanda: $Demanda GTTOT: $GeracaoTermicaTotal GHTOT: $GeracaoHidreletricaTotal Deficit = ", def, " Custo Presente: ", custo_presente)
            end
        end
    end






    numero_iteracoes =  2
    mapa_ilha_fluxos_violados = OrderedDict()
    for ilha in lista_ilhas_teste
        mapa_ilha_fluxos_violados[ilha] = []
    end

    for iter in 1:numero_iteracoes
        println("ITERACAO: ", iter)


        m = montaProblemaOtimizacaoBase()
        #println(m)

        if iter > 1
            for est in 1:caso.n_est
                for i_no in mapa_periodos[est].nos
                    for ilha in lista_ilhas_teste
                        for fluxo in mapa_ilha_fluxos_violados[ilha]
                            linha = fluxo.linha
                            lista_variaveis = []
                            for barra in ilha.barras
                                if barra.codigo != ilha.slack.codigo
                                    usi = get(mapa_codigoBARRA_nomeUSINA,barra.codigo,0)
                                    println("NOME_USI: ", usi)
                                    UHE = get(mapa_nome_UHE,usi,0)
                                    UTE = get(mapa_nome_UTE,usi,0)
                                    if UHE != 0
                                        push!(lista_variaveis, gh_vars[(est, i_no.codigo)][UHE.codigo])
                                    end

                                    if UTE != 0
                                        push!(lista_variaveis, gt_vars[(est, i_no.codigo)][UTE.codigo])
                                    end

                                    if UHE == 0 && UTE == 0
                                        push!(lista_variaveis,0)
                                    end
                                    
                                    
                                end
                            end
                            #gh_vars[(est, i_no.codigo)][i]
                            if fluxo.RHS <= 0
                                fator = -1
                            else
                                fator = 1
                            end
                            
                            folga_rede[(est, i_no.codigo, fluxo.linha)] = @variable(m, base_name="sFluxo_$(est)_$(i_no.codigo)_$(fluxo.de.codigo)_$(fluxo.para.codigo)")
                            @constraint(m, folga_rede[(est, i_no.codigo, fluxo.linha)] >= 0)
                            println(folga_rede[(est, i_no.codigo, fluxo.linha)])
                            @constraint(m, folga_rede[(est, i_no.codigo, fluxo.linha)] <= 2*fluxo.linha.Capacidade[est])
                            
                                
                            @constraint(  m, sum(fator*fluxo.linhaMatrizSensibilidade[i]*lista_variaveis[i] for i in 1:length(lista_variaveis) ) + fator*folga_rede[(est, i_no.codigo, fluxo.linha)] == fator*fluxo.RHS   )
                            println(lista_variaveis)
                            println("LInha Matriz Sensib: ", fluxo.linhaMatrizSensibilidade,  " RHS: ", fluxo.RHS)
                            #@constraint(  m, gh_vars[(est, i_no.codigo)][i] >= 0 ) 
                        end
                    end
                end
            end
        end

        println("OTIMIZANDO")
        println(m)
        JuMP.optimize!(m) 
        imprimeResultadosModelo(m)


        for est in 1:caso.n_est
            for i_no in mapa_periodos[est].nos
                for i in 1:caso.n_uhes
                    uhe = lista_uhes[i]
                    gh = JuMP.value(gh_vars[(est, i_no.codigo)][i])
                    uhe.barra.potenciaGerada[est] = gh
                    println("Stage: $est, Node: $(i_no.codigo), Hydro Plant: $i, Generation: $gh")
                end
                    
                for term in 1:caso.n_term
                    ute = lista_utes[term]
                    gt = JuMP.value(gt_vars[(est, i_no.codigo)][term])
                    ute.barra.potenciaGerada[est] = gt
                    println("Térmica: $term, Generation: ", gt," est: ", est, " node: ", i_no.codigo)
                end
    
                for ilha in lista_ilhas_teste
                    for barra in ilha.barras
                        println("Ilha: " , ilha.codigo, " Barra: ", barra.codigo, " GerBarra: ", barra.potenciaGerada )
                    end
                    calculaFluxosIlhaMetodoSensibilidadeDC(ilha,est)
                    println("EXECUTANDO FLUXO DC PARA O ESTAGIO  $est Node: $(i_no.codigo)")
                    
                    for fluxo in ilha.fluxo_linhas
                        println("De: ", fluxo.linha.de.codigo, " Para: ", fluxo.linha.para.codigo, " Fluxo: ", fluxo.fluxoDePara, " Capacidade: ", fluxo.linha.Capacidade[est])
                        if abs(fluxo.fluxoDePara) > fluxo.linha.Capacidade[est] && fluxo.violado != true
                            println("ENTROU AQUI FLUXO VIOLADO")
                            #push!(fluxos_violados, fluxo)
                            fluxo.violado = true
                            push!(mapa_ilha_fluxos_violados[ilha], fluxo)
                        end
                    end
                end
            end
        end

    end

    #lista_ilhas_teste = mapa_estagio_ilha[1]
    #for ilha in lista_ilhas_teste
    #    #calculaFluxosIlhaMetodoDeltaDC(ilha,1)
    #    calculaFluxosIlhaMetodoSensibilidadeDC(ilha,1)
    #    println("EXECUTANDO FLUXO DC")
    #    for fluxo in ilha.fluxo_linhas
    #        println("De: ", fluxo.linha.de.codigo, " Para: ", fluxo.linha.para.codigo, " Fluxo: ", fluxo.fluxoDePara)
    #    end
    #end


    ##TRANSFERE RESULTADO DAS USINAS PARA AS BARRAS

    ##EXECUTA FLUXO DC

    ##VERIFICA VIOLACOES

    ##ADICIONA VIOLACOES NO PL 
    #m = montaProblemaOtimizacaoBase()
    #FUNCAO PARA ADICIONAR RESTRICOES NO PL 
    #adicionaRestricoesDeFluxo(m)

    #OTIMIZA NOVAMENTE
    #JuMP.optimize!(m) 

    #imprimeResultadosModelo(m)


end