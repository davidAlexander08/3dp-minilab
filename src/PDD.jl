module Main

    using JuMP, GLPK, Plots, Measures, Plots, SparseArrays, DataFrames

    include("arvore.jl")
    include("FluxoDC.jl")

    #for ilha in lista_ilhas
    #    #calculaFluxosIlhaMetodoDeltaDC(ilha)
    #    calculaFluxosIlhaMetodoSensibilidadeDC(ilha)
    #    println("EXECUTANDO FLUXO DC")
    #    for fluxo in ilha.fluxo_linhas
    #        println("De: ", fluxo.linha.de.codigo, " Para: ", fluxo.linha.para.codigo, " Fluxo: ", fluxo.fluxoDePara)
    #    end
    #end
    println("codigo: ", no1.codigo, " codigo_intero: ", no1.index, " nivel: ", no1.periodo , " pai: ", no1.pai)
    printa_nos(no1)
    #println(dat_horas)
    println(dat_vaz)

    conversao_m3_hm3 = (60*60)/1000000
    global Vi = zeros(length(lista_total_de_nos) ,caso.n_uhes)
    [Vi[1,i] = lista_uhes[i].v0 for i in 1:caso.n_uhes]

    FCF_coef = zeros(caso.n_est,caso.n_uhes, caso.n_iter)
    FCF_indep = zeros(caso.n_est, caso.n_iter)
    zinf = zeros(caso.n_iter)
    zsup = zeros(caso.n_iter)

    balanco_energetico = DataFrame(etapa = String[], iter = Int[], est = Int[], node = Int[], Demanda = Float64[], GT = Float64[], GH = Float64[], Deficit = Float64[], CustoPresente = Float64[], CustoFuturo = Float64[])
    termicas           = DataFrame(etapa = String[], iter = Int[], est = Int[], node = Int[], nome = String[] , usina = Int[], generation = Float64[])
    hidreletricas      = DataFrame(etapa = String[], iter = Int[], est = Int[], node = Int[], nome = String[] ,usina = Int[], generation = Float64[], VI = Float64[], AFL = Float64[], TURB = Float64[], VERT = Float64[], VF = Float64[])
    df_convergencia    = DataFrame(iter = Int[], ZINF = Float64[], ZSUP = Float64[])
    df_cortes          = DataFrame(est = Int[], iter = Int[], usina = Int[], Indep = Float64[], Coef = Float64[])

    function retornaModelo(est, no)
        #converte_m3s_hm3 = (conversao_m3_hm3*dat_horas[(dat_horas.PERIODO .== no.periodo), "HORAS"][1])
        global m = Model(GLPK.Optimizer)
        @variable(m, 0 <= gt[1:caso.n_term])
        @variable(m, 0 <= gh[1:caso.n_uhes])
        @variable(m, 0 <= Turb[1:caso.n_uhes])
        @variable(m, 0 <= Vert[1:caso.n_uhes])
        @variable(m, 0 <= Vf[1:caso.n_uhes])
        @variable(m, 0 <= deficit )
        @variable(m, 0 <= alpha )
        @constraint(m, [i = 1:caso.n_uhes], Vf[i] <= lista_uhes[i].vmax) #linha, coluna
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
        GT_TOT = 0
        for i in 1:n_term
            geracao = JuMP.value(m[:gt][i])
            push!(termicas, (etapa = text, iter = it, est = est, node = no.codigo, nome = lista_utes[i].nome, usina = i, generation = geracao))
            GT_TOT += geracao
        end
        GH_TOT = 0
        for i in 1:caso.n_uhes
            geracao = JuMP.value(m[:gh][i])
            push!(hidreletricas, (etapa = text, iter = it, est = est, node = no.codigo, nome = lista_uhes[i].nome, usina = i, generation = geracao,
                            VI = Vi[no.codigo,i], AFL = (dat_vaz[(dat_vaz.NOME_UHE .== i) .& (dat_vaz.NO .== no.codigo), "VAZAO"][1]),
                            TURB = JuMP.value(m[:Turb][i]), VERT = JuMP.value(m[:Vert][i]), VF = JuMP.value(m[:Vf][i])))
            GH_TOT += geracao
        end
        Deficit =  JuMP.value(m[:deficit])
        push!(balanco_energetico,  (etapa = text, iter = it, est = est, node = no.codigo, Demanda = sistema.demanda[est], GT = GT_TOT, GH = GH_TOT, Deficit = Deficit, CustoPresente = retornaCustoPresente(m), CustoFuturo = JuMP.value(m[:alpha])))
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
                #print(m)
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
                imprimePolitica(m, "FORWARD", est, it, i_no)
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
                        @constraint(m, [iter = 1:caso.n_iter], m[:alpha] -sum(m[:Vf][i]*FCF_coef[est+1,i,iter] for i in 1:caso.n_uhes) >= FCF_indep[est+1,iter] ) #linha, coluna
                    end
                    #print(m)
                    JuMP.optimize!(m)     
                    custo_presente = retornaCustoPresente(m)
                    custo_futuro = JuMP.value(m[:alpha])
                    probabilidade_no = (dat_prob[(dat_prob.NO .== i_no.codigo), "PROBABILIDADE"][1])
                    FCF_indep[est, it] = FCF_indep[est, it] + (custo_presente + custo_futuro)*probabilidade_no
                    for i in 1:caso.n_uhes
                        dual_balanco_hidrico = JuMP.shadow_price( m[:c_hidr][i])
                        FCF_coef[est,i, it]  = FCF_coef[est,i, it] + dual_balanco_hidrico*probabilidade_no
                        FCF_indep[est, it] = FCF_indep[est, it] - dual_balanco_hidrico*Vi[i_no.codigo,i]*probabilidade_no
                        println("est: ", est, " iter: ", it, " no: ", i_no.codigo," usi: ", i, " dual bal: ", dual_balanco_hidrico, " c_pres: ", custo_presente, " c_fut: ", custo_futuro, " Vi[i_no.codigo,i]: ", Vi[i_no.codigo,i], "FCF_coef[est,i, it]: ", FCF_coef[est,i, it], "FCF_indep[est, it]: ", FCF_indep[est, it])

                    end
                    #println("FCF_coef: ", FCF_coef)
                    #println("FCF_indep: ", FCF_indep)
                    imprimePolitica(m, "BACKWARD", est, it, i_no)
                    

                end
                for usi in 1:caso.n_uhes
                    push!(df_cortes, (est = est, iter = it, usina = usi, Indep = FCF_indep[est, it], Coef = FCF_coef[est,usi, it]))
                end
            end 
        end
    end
    
    fig = plot(1:caso.n_iter, [zinf,zsup],size=(800,400), margin=10mm)
    savefig(fig, "myplot.png")

    balanco_energetico_fw = balanco_energetico[(balanco_energetico.etapa .== "FORWARD"), :]
    balanco_energetico_bk = balanco_energetico[(balanco_energetico.etapa .== "BACKWARD"), :]

    max_iter = maximum(balanco_energetico.iter)
    balanco_energetico_sf = balanco_energetico[(balanco_energetico.etapa .== "FORWARD") .& (balanco_energetico.iter .== max_iter), :]

    termicas_fw = termicas[(termicas.etapa .== "FORWARD"), :]
    termicas_bk = termicas[(termicas.etapa .== "BACKWARD"), :]
    termicas_sf = termicas[(termicas.etapa .== "FORWARD") .&& (termicas.iter .== max_iter), :]

    hidreletricas_fw = hidreletricas[(hidreletricas.etapa .== "FORWARD"), :]
    hidreletricas_bk = hidreletricas[(hidreletricas.etapa .== "BACKWARD"), :]
    hidreletricas_sf = hidreletricas[(hidreletricas.etapa .== "FORWARD") .&& (hidreletricas.iter .== max_iter), :]

    CSV.write("balanco_energetico_fw.csv", balanco_energetico_fw)
    CSV.write("balanco_energetico_bk.csv", balanco_energetico_bk)
    CSV.write("balanco_energetico_sf.csv", balanco_energetico_sf)
    CSV.write("termicas_fw.csv", termicas_fw)
    CSV.write("termicas_bk.csv", termicas_bk)
    CSV.write("termicas_sf.csv", termicas_sf)
    CSV.write("hidreletricas_fw.csv", hidreletricas_fw)
    CSV.write("hidreletricas_bk.csv", hidreletricas_bk)
    CSV.write("hidreletricas_sf.csv", hidreletricas_sf)
    CSV.write("convergencia.csv", df_convergencia)
    CSV.write("df_cortes.csv", df_cortes)
end