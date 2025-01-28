module Main

    using JuMP, GLPK, Plots, Measures, Plots, SparseArrays, DataFrames

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

    FCF_coef = zeros(caso.n_est,caso.n_uhes, caso.n_iter)
    FCF_indep = zeros(caso.n_est, caso.n_iter)
    zinf = zeros(caso.n_iter)
    zsup = zeros(caso.n_iter)

    balanco_energetico = DataFrame(etapa = [], iter = Int[], est = Int[], node = Int[], GT = Float64[], GH = Float64[], Deficit = Float64[], CustoPresente = Float64[], CustoFuturo = Float64[])
    termicas           = DataFrame(etapa = [], iter = Int[], est = Int[], node = Int[], usina = Int[], generation = Float64[])
    hidreletricas      = DataFrame(etapa = [], iter = Int[], est = Int[], node = Int[], usina = Int[], generation = Float64[], VI = Float64[], AFL = Float64[], TURB = Float64[], VERT = Float64[], VF = Float64[])

    #arq_00 = open("forward2.txt","w")
    #arq_01 = open("backward2.txt","w")
    #arq_02 = open("hidreletricas.txt", "w")
    #arq_03 = open("demanda.txt", "w")

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

    function imprimePolitica(m, text, est, it, no)
        converte_m3s_hm3 = (conversao_m3_hm3*dat_horas[(dat_horas.PERIODO .== no.periodo), "HORAS"][1])

        balanco_energetico

        #if est == 1 && it == 1
        #    write(arq, string(text, "\n"))
        #end
        #write(arq, string("Estagio: ", est, " No: ", no.codigo, " Iteracao: ", it, " \n"))
        GT_TOT = 0
        for i in 1:n_term
            geracao = JuMP.value(m[:gt][i])
            #[write(arq, string(" Térmica: ",i, " Geração: ",geracao, "\n")) ]
            push!(termicas, (etapa = text, iter = it, est = est, node = no.codigo, usina = i, generation = geracao))
            GT_TOT += geracao
        end
        GH_TOT = 0

        for i in 1:caso.n_uhes
            geracao = JuMP.value(m[:gh][i])
            push!(hidreletricas, (etapa = text, iter = it, est = est, node = no.codigo, usina = i, generation = geracao,
                            VI = Vi[no.codigo,i], AFL = (dat_vaz[(dat_vaz.NOME_UHE .== i) .& (dat_vaz.NO .== no.codigo), "VAZAO"][1]),
                            TURB = JuMP.value(m[:Turb][i]), VERT = JuMP.value(m[:Vert][i]), VF = JuMP.value(m[:Vf][i])))
            #[write(arq, string(" Hidro: ",i, " Geração: ", geracao," VI: ",Vi[no.codigo,i], " AFL: ", (dat_vaz[(dat_vaz.NOME_UHE .== i) .& (dat_vaz.NO .== no.codigo), "VAZAO"][1]),
            #" Turb: ",  JuMP.value(m[:Turb][i]), " Vert: ", JuMP.value(m[:Vert][i]), " Vf: ", JuMP.value(m[:Vf][i]), "\n")) for i in 1:caso.n_uhes]
            GH_TOT += geracao
        end
        Deficit =  JuMP.value(m[:deficit])

        push!(balanco_energetico,  (etapa = text, iter = it, est = est, node = no.codigo, GT = GT_TOT, GH = GH_TOT, Deficit = Deficit, CustoPresente = retornaCustoPresente(m), CustoFuturo = JuMP.value(m[:alpha])))
        #write(arq,string("    GH_TOT: $GH_TOT GT_TOT: $GT_TOT DEF: $Deficit Custo Imediato: ", retornaCustoPresente(m), " Custo Futuro: ", JuMP.value(m[:alpha]), "\n"))
        #write(arq, string("--------------------------------------------------------------- \n"))
    end

    #function imprimeBalancoHidrico(arq, m, text, est, it, no)
    #    converte_m3s_hm3 = (conversao_m3_hm3*dat_horas[(dat_horas.PERIODO .== no.periodo), "HORAS"][1])
    #    if est == 1 && it == 1
    #        write(arq, string(text, "\n"))
    #    end
    #    write(arq, string("Estagio: ", est, " No: ", no.codigo, " Iteracao: ", it, " \n"))
    #    for i in 1:caso.n_uhes
    #        geracao = JuMP.value(m[:gh][i])
    #        [write(arq, string("    Hidro: ",i, " Geração: ", geracao," VI: ",Vi[no.codigo,i], " AFL: ", (dat_vaz[(dat_vaz.NOME_UHE .== i) .& (dat_vaz.NO .== no.codigo), "VAZAO"][1]),
    #        " Turb: ",  JuMP.value(m[:Turb][i]), " Vert: ", JuMP.value(m[:Vert][i]), " Vf: ", JuMP.value(m[:Vf][i]), "\n")) for i in 1:caso.n_uhes]
    #    end
    #end

    #function imprimeBalancoDemanda(arq, m, text, est, it, no)
    #    if est == 1 && it == 1
    #        write(arq, string(text, "\n"))
    #    end
    #    write(arq, string("Estagio: ", est, " No: ", no.codigo, " Iteracao: ", it, " \n"))
    #    GT_TOT = 0
    #    for i in 1:n_term
    #        GT_TOT +=  JuMP.value(m[:gt][i])
    #    end
    #    GH_TOT = 0
    #    for i in 1:caso.n_uhes
    #        GH_TOT += JuMP.value(m[:gh][i])
    #    end
    #    Deficit =  JuMP.value(m[:deficit])
    #    write(arq,string("    GH_TOT: $GH_TOT GT_TOT: $GT_TOT DEF: $Deficit Custo Imediato: ", retornaCustoPresente(m), " Custo Futuro: ", JuMP.value(m[:alpha]), "\n"))
    #end


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
                imprimePolitica(m, "FORWARD ", est, it, i_no)
                #imprimeBalancoHidrico(arq_02, m, "FORWARD ", est, it, i_no)
                #imprimeBalancoDemanda(arq_03, m, "FORWARD ", est, it, i_no)
            end
        end 
        println("zinf: ", zinf, " zsup: ", zsup)

        if abs(zinf[it]-zsup[it]) < 0.1 
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
                    imprimePolitica(m, "BACKWARD ", est, it, i_no)
                end
            end 
        end
    end
    
    fig = plot(1:caso.n_iter, [zinf,zsup],size=(800,400), margin=10mm)
    savefig(fig, "myplot.png")
    #close(arq_00)
    #close(arq_01)
   

    CSV.write("df_balanco_energetico.csv", balanco_energetico)
    CSV.write("df_termicas.csv", termicas)
    CSV.write("df_hidreletricas.csv", hidreletricas)
end