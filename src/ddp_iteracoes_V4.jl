module Main

    using JuMP, GLPK, Plots, Measures, Plots, SparseArrays

    include("arvore.jl")
    include("Rede/FluxoDC.jl")

    for ilha in lista_ilhas
        #calculaFluxosIlhaMetodoDeltaDC(ilha)
        calculaFluxosIlhaMetodoSensibilidadeDC(ilha)
        println("EXECUTANDO FLUXO DC")
        for fluxo in ilha.fluxo_linhas
            println("De: ", fluxo.linha.de.codigo, " Para: ", fluxo.linha.para.codigo, " Fluxo: ", fluxo.fluxoDePara)
        end
    end

    
    println("codigo: ", no1.codigo, " codigo_intero: ", no1.index, " nivel: ", no1.periodo , " pai: ", no1.pai)
    printa_nos(no1)

    print(dat_horas)
    conversao_m3_hm3 = (60*60)/1000000
    global Vi = zeros(length(lista_total_de_nos) ,caso.n_uhes)
    [Vi[1,i] = lista_uhes[i].v0 for i in 1:caso.n_uhes]

    #METODO PL UNICO



    global m = Model(GLPK.Optimizer)
    gt_vars = Dict{Tuple{Int, Int}, Vector{JuMP.VariableRef}}()
    gh_vars = Dict{Tuple{Int, Int}, Vector{JuMP.VariableRef}}()
    turb_vars = Dict{Tuple{Int, Int}, Vector{JuMP.VariableRef}}()
    vert_vars = Dict{Tuple{Int, Int}, Vector{JuMP.VariableRef}}()
    vf_vars = Dict{Tuple{Int, Int}, Vector{JuMP.VariableRef}}()
    deficit_vars = Dict{Tuple{Int, Int}, JuMP.VariableRef}()
    ## METODO PL UNICO
    for est in 1:caso.n_est
        for i_no in mapa_periodos[est].nos
            println("i_no: ", i_no.codigo, " est: ", est)
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
            @constraint(  m, sum(gh_vars[(est, i_no.codigo)][i] for i in 1:caso.n_uhes) + sum(gt_vars[(est, i_no.codigo)][i] for i in 1:caso.n_term) + deficit_vars[(est, i_no.codigo)] == sistema.demanda[est]   )
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

                inflow = dat_vaz[(dat_vaz.NOME_UHE .== i) .& (dat_vaz.NO .== i_no.codigo), "VAZAO"][1]
                println("Hydro Plant: ", i, " Stage: ", est, " Node: ", i_no.codigo, " Inflow: ", inflow)
                
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




    print(m)
    JuMP.optimize!(m)  

    # Print results
    for est in 1:caso.n_est
        for i_no in mapa_periodos[est].nos
            for i in 1:caso.n_uhes
                vf = JuMP.value(vf_vars[(est, i_no.codigo)][i])
                turb = JuMP.value(turb_vars[(est, i_no.codigo)][i])
                vert = JuMP.value(vert_vars[(est, i_no.codigo)][i])
                gh = JuMP.value(gh_vars[(est, i_no.codigo)][i])
                println("Stage: $est, Node: $(i_no.codigo), Hydro Plant: $i, VF: $vf, Turb: $turb, Vert: $vert, Generation: $gh")
            end
                
            for term in 1:caso.n_term
                gt = JuMP.value(gt_vars[(est, i_no.codigo)][term])
                println("GT: ", JuMP.value(gt)," est: ", est, " node: ", i_no.codigo)
            end
            def = JuMP.value(deficit_vars[(est, i_no.codigo)])
            println("Deficit = ", def)

        end
    end


    #@variable(m, 0 <= gt[1:caso.n_term])
    #@variable(m, 0 <= gh[1:caso.n_uhes])
    #@variable(m, 0 <= Turb[1:caso.n_uhes])
    #@variable(m, 0 <= Vert[1:caso.n_uhes])
    #@variable(m, 0 <= Vf[1:caso.n_uhes])
    #@variable(m, 0 <= deficit )
    #@variable(m, 0 <= alpha )
    #@constraint(m, [i = 1:caso.n_uhes], Turb[i] <= lista_uhes[i].turbmax) #linha, coluna
    #@constraint(m, [i = 1:caso.n_uhes], gh[i] == Turb[i]) #linha, coluna      /converte_m3s_hm3
    #@constraint(m, [i = 1:caso.n_term], gt[i] <= lista_utes[i].gtmax) #linha, coluna
    #@objective(m, Min, sum(Vert[i]*0.01 for i in 1:caso.n_uhes) + sum(lista_utes[i].custo_geracao*gt[i] for i in 1:caso.n_term) + sistema.deficit_cost*deficit + alpha)
    #@constraint(m, balanco, sum(m[:gh][i] for i in 1:caso.n_uhes) + sum(m[:gt][i] for i in 1:caso.n_term) + m[:deficit] == sistema.demanda[est])
    #@constraint(m, c_hidr[i = 1:caso.n_uhes], Vf[i] + Turb[i] + Vert[i] == Vi[no.codigo,i] + (dat_vaz[(dat_vaz.NOME_UHE .== i) .& (dat_vaz.NO .== no.codigo), "VAZAO"][1])) #linha, colun * converte_m3s_hm3


    exit(1)

    #METODO PDD

    FCF_coef = zeros(caso.n_est,caso.n_uhes, caso.n_iter)
    FCF_indep = zeros(caso.n_est, caso.n_iter)
    zinf = zeros(caso.n_iter)
    zsup = zeros(caso.n_iter)

    arq_00 = open("forward2.txt","w")
    arq_01 = open("backward2.txt","w")

    function retornaModelo(est, no)
        converte_m3s_hm3 = (conversao_m3_hm3*dat_horas[(dat_horas.PERIODO .== no.periodo), "HORAS"][1])
        global m = Model(GLPK.Optimizer)
        @variable(m, 0 <= gt[1:caso.n_term])
        @variable(m, 0 <= gh[1:caso.n_uhes])
        @variable(m, 0 <= Turb[1:caso.n_uhes])
        @variable(m, 0 <= Vert[1:caso.n_uhes])
        @variable(m, 0 <= Vf[1:caso.n_uhes])
        @variable(m, 0 <= deficit )
        @variable(m, 0 <= alpha )
        @constraint(m, [i = 1:caso.n_uhes], Turb[i] <= lista_uhes[i].turbmax) #linha, coluna
        @constraint(m, [i = 1:caso.n_uhes], gh[i] == Turb[i]) #linha, coluna      /converte_m3s_hm3
        @constraint(m, [i = 1:caso.n_term], gt[i] <= lista_utes[i].gtmax) #linha, coluna
        @objective(m, Min, sum(Vert[i]*0.01 for i in 1:caso.n_uhes) + sum(lista_utes[i].custo_geracao*gt[i] for i in 1:caso.n_term) + sistema.deficit_cost*deficit + alpha)
        @constraint(m, balanco, sum(m[:gh][i] for i in 1:caso.n_uhes) + sum(m[:gt][i] for i in 1:caso.n_term) + m[:deficit] == sistema.demanda[est])
        @constraint(m, c_hidr[i = 1:caso.n_uhes], Vf[i] + Turb[i] + Vert[i] == Vi[no.codigo,i] + (dat_vaz[(dat_vaz.NOME_UHE .== i) .& (dat_vaz.NO .== no.codigo), "VAZAO"][1])) #linha, colun * converte_m3s_hm3
        return m
    end

    function imprimePolitica(arq, m, text, est, it, no)
        converte_m3s_hm3 = (conversao_m3_hm3*dat_horas[(dat_horas.PERIODO .== no.periodo), "HORAS"][1])
        write(arq, string(text, "\n"))
        write(arq, string(" Estagio: ", est, " No: ", no.codigo, " Iteracao: ", it, " \n"))
        write(arq, string("--------------------------------------------------------------- \n"))
        write(arq, string("GERACAO \n"))
        write(arq, string("--------------------------------------------------------------- \n"))
        write(arq, string("TERMICAS \n"))
        [write(arq, string(" gt",i, ": ",JuMP.value(m[:gt][i]), "\n")) for i in 1:caso.n_term]
        write(arq, string("HIDRELETRICAS \n"))
        [write(arq, string(" gh",i, ": ",JuMP.value(m[:gh][i]), "\n")) for i in 1:caso.n_uhes]
        write(arq, string("DEFICIT \n"))
        write(arq, string("deficit: ", JuMP.value(m[:deficit]), "\n"))
        write(arq, string("--------------------------------------------------------------- \n"))
        write(arq, string("CUSTOS \n"))
        write(arq, string("--------------------------------------------------------------- \n"))
        write(arq,string(" Custo Imediato: ", retornaCustoPresente(m), "\n"))
        write(arq, string(" Custo Futuro: ", JuMP.value(m[:alpha]), "\n"))
        write(arq, string("--------------------------------------------------------------- \n"))
        write(arq, string("BALANCO HIDRICO \n"))
        write(arq, string("--------------------------------------------------------------- \n"))
        [write(arq, string(" AFL",i, ": ",(dat_vaz[(dat_vaz.NOME_UHE .== i) .& (dat_vaz.NO .== no.codigo), "VAZAO"][1]), "\n")) for i in 1:caso.n_uhes] #* converte_m3s_hm3
        [write(arq, string(" Vi",i, ": ",Vi[no.codigo,i], "\n")) for i in 1:caso.n_uhes]
        [write(arq, string(" Turb",i, ": ",JuMP.value(m[:Turb][i]), "\n")) for i in 1:caso.n_uhes]
        [write(arq, string(" Vert",i, ": ",JuMP.value(m[:Vert][i]), "\n")) for i in 1:caso.n_uhes]
        [write(arq, string(" Vf",i, ": ",JuMP.value(m[:Vf][i]), "\n")) for i in 1:caso.n_uhes]
        write(arq, string("--------------------------------------------------------------- \n"))
    end

    function retornaCustoPresente(m)
        custo_presente = 0
        [custo_presente += JuMP.value(m[:gt][i])*lista_utes[i].custo_geracao for i in 1:caso.n_term]
        custo_presente += JuMP.value(m[:deficit])*sistema.deficit_cost
        return custo_presente
    end


    for it in 1:caso.n_iter
        #ETAPA FORWARD
        for est in 1:caso.n_est
            for i_no in mapa_periodos[est].nos
                
                m = retornaModelo(est,i_no)
                if est < caso.n_est && it > 1
                    @constraint(m, [iter = 1:caso.n_iter], m[:alpha] - sum(m[:Vf][i]*FCF_coef[est+1,i,iter] for i in 1:caso.n_uhes)   >= FCF_indep[est+1,iter] ) #linha, coluna
                end
                #if(est == caso.n_est)
                #    @constraint(m, FCF, m[:alpha] -sum(m[:Vf][i]*-0.01 for i in 1:caso.n_uhes) >= 38524017.2 ) #linha, coluna
                #end
                JuMP.optimize!(m)         
                if est < caso.n_est
                    i_filhos = i_no.filhos
                    for i_filho in i_filhos
                        [Vi[i_filho.codigo,i] = JuMP.value(m[:Vf][i]) for i in 1:caso.n_uhes]   
                    end
                end

                custo_presente = retornaCustoPresente(m)
                custo_futuro = JuMP.value(m[:alpha])
                zsup[it] = zsup[it] + custo_presente*(dat_prob[(dat_prob.NO .== i_no.codigo), "PROBABILIDADE"][1])
                if est == 1 zinf[it] = custo_presente+custo_futuro end
                imprimePolitica(arq_00, m, "FORWARD ", est, it, i_no)
            end
        end 
        println("zinf: ", zinf, " zsup: ", zsup)

        if(abs(zinf[it]-zsup[it]) < 0.1)
            println("CONVERGIU")
            break
        end

        # ETAPA BACKWARD
        if it != caso.n_iter
            for est in caso.n_est:-1:1 
                for i_no in mapa_periodos[est].nos  
                    println(i_no.codigo)      
                    m = retornaModelo(est, i_no)
                    if est < caso.n_est && est > 1
                        @constraint(m, [iter = 1:caso.n_iter], m[:alpha] -sum(m[:Vf][i]*FCF_coef[est+1,i,iter] for i in 1:caso.n_uhes) >= FCF_indep[est+1,iter] ) #linha, coluna
                    end
                    #if(est == caso.n_est)
                    #    @constraint(m, FCF, m[:alpha] -sum(m[:Vf][i]*-0.01 for i in 1:caso.n_uhes) >= 38524017.2 ) #linha, coluna
                    #end
                    print(m)
                    JuMP.optimize!(m)     
                    custo_presente = retornaCustoPresente(m)
                    custo_futuro = JuMP.value(m[:alpha])
                    for i in 1:caso.n_uhes
                        FCF_coef[est,i, it]  = FCF_coef[est,i, it] + JuMP.shadow_price( m[:c_hidr][i])*(dat_prob[(dat_prob.NO .== i_no.codigo), "PROBABILIDADE"][1])
                        FCF_indep[est, it] = FCF_indep[est, it] + ((custo_presente + custo_futuro) - JuMP.shadow_price( m[:c_hidr][i])*Vi[i_no.codigo,i])*(dat_prob[(dat_prob.NO .== i_no.codigo), "PROBABILIDADE"][1]) 
                    end
                    println("FCF_coef: ", FCF_coef)
                    println("FCF_indep: ", FCF_indep)
                    imprimePolitica(arq_01, m, "BACKWARD ", est, it, i_no)
                end
            end 
        end
    end
    
    fig = plot(1:caso.n_iter, [zinf,zsup],size=(800,400), margin=10mm)
    savefig(fig, "myplot.png")
    close(arq_00)
    close(arq_01)

end