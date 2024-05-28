module Main

    using JuMP, GLPK, Plots, Measures
    include("LeituraEntrada.jl")

    global afluencia = [20;
                20;
                15]

    global Vi = zeros(caso.n_est,caso.n_uhes)
    [Vi[1,i] = lista_uhes[i].v0 for i in 1:caso.n_uhes]
    FCF_coef = zeros(caso.n_est*caso.n_iter,caso.n_uhes, caso.n_iter)
    FCF_indep = zeros(caso.n_est*caso.n_iter,1, caso.n_iter)
    zinf = zeros(caso.n_iter)
    zsup = zeros(caso.n_iter)

    arq_00 = open("forward.txt","w")
    arq_01 = open("backward.txt","w")

    function retornaModelo(est)
        global m = Model(GLPK.Optimizer)
        @variable(m, 0 <= gt[1:caso.n_term])
        @variable(m, 0 <= gh[1:caso.n_uhes])
        @variable(m, 0 <= Turb[1:caso.n_uhes])
        @variable(m, 0 <= Vert[1:caso.n_uhes])
        @variable(m, 0 <= Vf[1:caso.n_uhes])
        @variable(m, 0 <= deficit )
        @variable(m, 0 <= alpha )
        @constraint(m, [i = 1:caso.n_uhes], Turb[i] <= lista_uhes[i].turbmax) #linha, coluna
        @constraint(m, [i = 1:caso.n_uhes], gh[i] == Turb[i]) #linha, coluna
        @constraint(m, [i = 1:caso.n_term], gt[i] <= lista_utes[i].gtmax) #linha, coluna
        @objective(m, Min, sum(Vert[i]*0.01 for i in 1:caso.n_uhes) + sum(lista_utes[i].custo_geracao*gt[i] for i in 1:caso.n_term) + sistema.deficit_cost*deficit + alpha)
        @constraint(m, balanco, sum(m[:gh][i] for i in 1:caso.n_uhes) + sum(m[:gt][i] for i in 1:caso.n_term) + m[:deficit] == sistema.demanda[est])
        @constraint(m, c_hidr[i = 1:caso.n_uhes], Vf[i] + Turb[i] + Vert[i] == Vi[est,i] + afluencia[est, i]) #linha, colun
        return m
    end

    function imprimePolitica(arq, m, text, est, it)
        write(arq, string(text, "\n"))
        write(arq, string(" Estagio: ", est, " Iteracao: ", it, " \n"))
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
        [write(arq, string(" Turb",i, ": ",JuMP.value(m[:Turb][i]), "\n")) for i in 1:caso.n_uhes]
        [write(arq, string(" Vert",i, ": ",JuMP.value(m[:Vert][i]), "\n")) for i in 1:caso.n_uhes]
        [write(arq, string(" Vf",i, ": ",JuMP.value(m[:Vf][i]), "\n")) for i in 1:caso.n_uhes]
        write(arq, string("--------------------------------------------------------------- \n"))
    end

    function retornaCustoPresente(m)
        custo_presente = 0
        [custo_presente = custo_presente + JuMP.value(m[:gt][i])*lista_utes[i].custo_geracao for i in 1:caso.n_term]
        custo_presente = custo_presente + JuMP.value(m[:deficit])*sistema.deficit_cost
        return custo_presente
    end


    for it in 1:caso.n_iter
        #ETAPA FORWARD
        for est in 1:caso.n_est
            m = retornaModelo(est)
            if est < caso.n_est
                @constraint(m, [iter = 1:caso.n_iter], m[:alpha] -m[:Vf][1]*FCF_coef[est+1,1,iter] >= FCF_indep[est+1,1,iter] ) #linha, coluna
            end
            JuMP.optimize!(m)         
            if est < caso.n_est ; [Vi[est+1,i] = JuMP.value(m[:Vf][i]) for i in 1:caso.n_uhes] end

            custo_presente = retornaCustoPresente(m)
            custo_futuro = JuMP.value(m[:alpha])
            zsup[it] = zsup[it] + custo_presente
            if est == 1 zinf[it] = custo_presente+custo_futuro end
            imprimePolitica(arq_00, m, "FORWARD ", est, it)
        end 
        println("zinf: ", zinf, " zsup: ", zsup)

        if(abs(zinf[it]-zsup[it]) < 0.1)
            println("CONVERGIU")
            break
        end

        # ETAPA BACKWARD
        if it != caso.n_iter
            for est in caso.n_est:-1:1            
                m = retornaModelo(est)
                if est < caso.n_est && est > 1
                    @constraint(m, [iter = 1:caso.n_iter], m[:alpha] -m[:Vf][1]*FCF_coef[est+1,1,iter] >= FCF_indep[est+1,1,iter] ) #linha, coluna
                end
                JuMP.optimize!(m)     
                custo_presente = retornaCustoPresente(m)
                custo_futuro = JuMP.value(m[:alpha])
                [FCF_coef[est,i, it]  = JuMP.shadow_price( m[:c_hidr][i]) for i in 1:caso.n_uhes]
                FCF_indep[est,1, it] = custo_presente + custo_futuro
                [FCF_indep[est,1, it] = FCF_indep[est,1, it] - FCF_coef[est,i, it]*Vi[est,i] for i in 1:caso.n_uhes]
                imprimePolitica(arq_01, m, "BACKWARD ", est, it)
            end 
        end
    end

    fig = plot(1:caso.n_iter, [zinf,zsup],size=(800,400), margin=10mm)
    savefig(fig, "myplot.png")
    close(arq_00)
    close(arq_01)

end








    #BACKLOG FORWARD
 #   ger_hidr_fw = zeros(caso.n_est,caso.n_uhes, caso.n_iter)
 #   vf_hidr_fw = zeros(caso.n_est,caso.n_uhes, caso.n_iter)
 #   vi_hidr_fw = zeros(caso.n_est,caso.n_uhes, caso.n_iter)
 #   turb_hidr_fw = zeros(caso.n_est,caso.n_uhes, caso.n_iter)
#    vert_hidr_fw = zeros(caso.n_est,caso.n_uhes, caso.n_iter)
#    ger_term_fw = zeros(caso.n_est,caso.n_term, caso.n_iter)
#    ger_def_fw = zeros(caso.n_est,1, caso.n_iter)

    #BACKLOG BACKWARD
#    ger_hidr_bk = zeros(caso.n_est,caso.n_uhes, caso.n_iter)
#    vf_hidr_bk = zeros(caso.n_est,caso.n_uhes, caso.n_iter)
#    vi_hidr_bk = zeros(caso.n_est,caso.n_uhes, caso.n_iter)
#    turb_hidr_bk = zeros(caso.n_est,caso.n_uhes, caso.n_iter)
#    vert_hidr_bk = zeros(caso.n_est,caso.n_uhes, caso.n_iter)
#    ger_term_bk = zeros(caso.n_est,caso.n_term, caso.n_iter)
#    ger_def_bk = zeros(caso.n_est,1, caso.n_iter)






function printaOperacao(m)
    print("OPER")
    
    [print(" gh",i, ": ",JuMP.value(m[:gh][i])) for i in 1:caso.n_uhes]
    print(" deficit = ", JuMP.value(m[:deficit]))
    println(" alpha: ",JuMP.value(m[:alpha]))
    println("")
    [print(" Turb",i, ": ",JuMP.value(m[:Turb][i])) for i in 1:caso.n_uhes]
    [print(" Vert",i, ": ",JuMP.value(m[:Vert][i])) for i in 1:caso.n_uhes]
    [print(" Vf",i, ": ",JuMP.value(m[:Vf][i])) for i in 1:caso.n_uhes]
end

function salva_forward(m, est, it)
    println("FORWARD Sol Otima estagio ", est)
    printaOperacao(m)
    [ger_hidr_fw[est,i, it] = JuMP.value(m[:gh][i]) for i in 1:caso.n_uhes]
    [vf_hidr_fw[est,i, it] = JuMP.value(m[:Vf][i]) for i in 1:caso.n_uhes]
    [vi_hidr_fw[est,i, it] = Vi[est,i] for i in 1:caso.n_uhes]
    [turb_hidr_fw[est,i, it] = JuMP.value(m[:Turb][i]) for i in 1:caso.n_uhes]
    [vert_hidr_fw[est,i, it] = JuMP.value(m[:Vert][i]) for i in 1:caso.n_uhes]
    [ger_term_fw[est,i, it] = JuMP.value(m[:gt][i]) for i in 1:caso.n_term]
    ger_def_fw[est,1, it] = JuMP.value(m[:deficit])
end

function salva_backward(m, est, it)
    println("BACKWARD Sol Otima estagio ", est)
    printaOperacao(m)
    [ger_hidr_bk[est,i, it] = JuMP.value(m[:gh][i]) for i in 1:caso.n_uhes]
    [vf_hidr_bk[est,i, it] = JuMP.value(m[:Vf][i]) for i in 1:caso.n_uhes]
    [vi_hidr_bk[est,i, it] = Vi[est,i] for i in 1:caso.n_uhes]
    [turb_hidr_bk[est,i, it] = JuMP.value(m[:Turb][i]) for i in 1:caso.n_uhes]
    [vert_hidr_bk[est,i, it] = JuMP.value(m[:Vert][i]) for i in 1:caso.n_uhes]
    [ger_term_bk[est,i, it] = JuMP.value(m[:gt][i]) for i in 1:caso.n_term]
    ger_def_bk[est,1, it] = JuMP.value(m[:deficit])
end
