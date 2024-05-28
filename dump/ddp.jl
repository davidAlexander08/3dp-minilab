using JuMP, GLPK

struct UHEConfigData
    name::String
    downstream::String #Jusante
    ghmin::Float64
    ghmax::Float64
    vmin::Float64
    vmax::Float64
    v0::Float64
    spill_penal::Float64
end

struct UTEConfigData
    gtmin::Float64
    gtmax::Float64
    generation_cost::Float64
end

struct SystemConfigData
    deficit_cost::Float64
    demand::Float64
end

struct ConfigData
    uhe::UHEConfigData
    ute::UTEConfigData
    system::SystemConfigData
end




# Preparing an optimization model
n_iter = 1;
n_est = 3;
n_term = 2
n_uhes = 1
limites_termicas = [15  10;  
                    15  10;
                    15  10]
custo_termicas = [10  25;  
                  10  25;
                  10  25]
demanda = [50, 50, 50]
c_def = 500
custo_deficit = [c_def c_def c_def]


afluencia = [20;
             20;
             15]

Turb_max = [60;
            60;
            60]


ger_hidr = zeros(n_est,n_uhes)
Vi = zeros(n_est,n_uhes)
vf_hidr = zeros(n_est,n_uhes)
turb_hidr = zeros(n_est,n_uhes)
vert_hidr = zeros(n_est,n_uhes)
ger_term = zeros(n_est,n_term)
ger_def = zeros(n_est,1)

Vi[1,1] = 65

n_iter = 1
FCF_coef = zeros(n_est*n_iter,n_uhes)
FCF_indep = zeros(n_est*n_iter,1)
zinf = zeros(n_iter)
zsup = zeros(n_iter)

# ETAPA FORWARD
for est in 1:n_est
    m = Model(GLPK.Optimizer)
    @variable(m, 0 <= gt[1:n_term])
    @variable(m, 0 <= gh[1:n_uhes])
    @variable(m, 0 <= Turb[1:n_uhes])
    @variable(m, 0 <= Vert[1:n_uhes])
    @variable(m, 0 <= Vf[1:n_uhes])
    @variable(m, 0 <= deficit )
    @variable(m, 0 <= alpha )
    @constraint(m, [i = 1:n_term], gt[i] <= limites_termicas[est,i]) #linha, coluna
    @constraint(m, [i = 1:n_uhes], Turb[i] <= Turb_max[i]) #linha, coluna
    @constraint(m, [i = 1:n_uhes], gh[i] == Turb[i]) #linha, coluna
    @constraint(m, [i = 1:n_uhes], Vf[i] + Turb[i] + Vert[i] == Vi[est,i] + afluencia[est, i]) #linha, colun
    @constraint(m, balanco, sum(gh[i] for i in 1:n_uhes) + sum(gt[i] for i in 1:n_term) + deficit == demanda[est])
    @objective(m, Min, sum(Vert[i]*0.01 for i in 1:n_uhes) + sum(custo_termicas[est, i]*gt[i] for i in 1:n_term) + custo_deficit[est]*deficit + alpha)
    JuMP.optimize!(m)    #println(m) 
    println("FORWARD Solucao Otima Estagio:", est)
    [print(" gt",i, ": ",JuMP.value(gt[i])) for i in 1:n_term]
    [print(" gh",i, ": ",JuMP.value(gh[i])) for i in 1:n_uhes]
    print(" deficit = ", JuMP.value(deficit))
    println("")
    [print(" Vi",i, ": ",JuMP.value(Vi[est,i])) for i in 1:n_uhes]
    [print(" Vf",i, ": ",JuMP.value(Vf[i])) for i in 1:n_uhes]
    [print(" Turb",i, ": ",JuMP.value(Turb[i])) for i in 1:n_uhes]
    [print(" Vert",i, ": ",JuMP.value(Vert[i])) for i in 1:n_uhes]
    println("")
    println(" alpha: ",JuMP.value(alpha))
    
    if est < n_est
        [Vi[est+1,i] = JuMP.value(Vf[i]) for i in 1:n_uhes]
    end
    [ger_hidr[est,i] = JuMP.value(gh[i]) for i in 1:n_uhes]
    [vf_hidr[est,i] = JuMP.value(Vf[i]) for i in 1:n_uhes]
    [turb_hidr[est,i] = JuMP.value(Turb[i]) for i in 1:n_uhes]
    [vert_hidr[est,i] = JuMP.value(Vert[i]) for i in 1:n_uhes]
    [ger_term[est,i] = JuMP.value(gt[i]) for i in 1:n_term]
    ger_def[est,1] = JuMP.value(deficit)

    print("gh: ", ger_hidr)
    print("gt: ", ger_term)
    print("def: ", ger_def)
    print("vi: ", Vi)
    print("vf: ", vf_hidr)
    print("qt: ", turb_hidr)
    print("qv: ", vert_hidr)
    custo_presente = 0
    [custo_presente = custo_presente + JuMP.value(gt[i])*custo_termicas[est,i] for i in 1:n_term]
    custo_presente = custo_presente + JuMP.value(deficit)*custo_deficit[est]
    custo_futuro = JuMP.value(alpha)
    custo_presente_futuro = custo_presente + custo_futuro
    zsup[1] = zsup[1] + custo_presente
    if est == 1
        zinf[1] = custo_presente_futuro
    end
    println("")
    println("################################################################")
end 

println("zinf: ", zinf, " zsup: ", zsup)

# ETAPA BACKWARD
for est in n_est:-1:1
    m = Model(GLPK.Optimizer)
    @variable(m, 0 <= gt[1:n_term])
    @variable(m, 0 <= gh[1:n_uhes])
    @variable(m, 0 <= Turb[1:n_uhes])
    @variable(m, 0 <= Vert[1:n_uhes])
    @variable(m, 0 <= Vf[1:n_uhes])
    @variable(m, 0 <= deficit )
    @variable(m, 0 <= alpha )
    @constraint(m, [i = 1:n_term], gt[i] <= limites_termicas[est,i]) #linha, coluna
    @constraint(m, [i = 1:n_uhes], Turb[i] <= Turb_max[i]) #linha, coluna
    @constraint(m, [i = 1:n_uhes], gh[i] == Turb[i]) #linha, coluna
    if est < n_est
        @constraint(m, cut, -alpha +Vf[1]*FCF_coef[est+1,1] <= FCF_indep[est+1,1] ) #linha, coluna
    end

    #@constraint(m, [i = 1:n_uhes], Vf[i] + Turb[i] + Vert[i] == Vi[est,i] + afluencia[est, i]) #linha, coluna
    @constraint(m, c_hidr[i in 1:n_uhes], Vf[i] + Turb[i] + Vert[i] == Vi[est,i] + afluencia[est, i]) #linha, coluna
    @constraint(m, balanco, sum(gh[i] for i in 1:n_uhes) + sum(gt[i] for i in 1:n_term) + deficit == demanda[est])
    @objective(m, Min, sum(Vert[i]*0.01 for i in 1:n_uhes) + sum(custo_termicas[est, i]*gt[i] for i in 1:n_term) + custo_deficit[est]*deficit + alpha)
    println(m) 
    JuMP.optimize!(m)     
    println("BACKWARD Solucao Otima Estagio:", est)
    [print(" gt",i, ": ",JuMP.value(gt[i])) for i in 1:n_term]
    [print(" gh",i, ": ",JuMP.value(gh[i])) for i in 1:n_uhes]
    print(" deficit = ", JuMP.value(deficit))
    println("")
    [print(" Vi",i, ": ",JuMP.value(Vi[est,i])) for i in 1:n_uhes]
    [print(" Vf",i, ": ",JuMP.value(Vf[i])) for i in 1:n_uhes]
    [print(" Turb",i, ": ",JuMP.value(Turb[i])) for i in 1:n_uhes]
    [print(" Vert",i, ": ",JuMP.value(Vert[i])) for i in 1:n_uhes]
    println("")
    println(" alpha: ",JuMP.value(alpha))
    
    if est < n_est
        [Vi[est+1,i] = JuMP.value(Vf[i]) for i in 1:n_uhes]
    end
    [ger_hidr[est,i] = JuMP.value(gh[i]) for i in 1:n_uhes]
    [vf_hidr[est,i] = JuMP.value(Vf[i]) for i in 1:n_uhes]
    [turb_hidr[est,i] = JuMP.value(Turb[i]) for i in 1:n_uhes]
    [vert_hidr[est,i] = JuMP.value(Vert[i]) for i in 1:n_uhes]
    [ger_term[est,i] = JuMP.value(gt[i]) for i in 1:n_term]
    ger_def[est,1] = JuMP.value(deficit)

    print(ger_hidr)
    print(ger_term)
    print(ger_def)
    print(Vi)
    print(vf_hidr)
    print(turb_hidr)
    print(vert_hidr)

    custo_presente = 0
    [custo_presente = custo_presente + JuMP.value(gt[i])*custo_termicas[est,i] for i in 1:n_term]
    custo_presente = custo_presente + JuMP.value(deficit)*custo_deficit[est]
    
    custo_futuro = JuMP.value(alpha)
    custo_presente_futuro = custo_presente + custo_futuro



    println("")
    println("CUSTO PRESENTE: ", custo_presente)
    println("CUSTO FUTURO: ", custo_futuro)
    println("CUSTO PRESENTE + FUTURO: ", custo_presente_futuro)
    println("Dual Variables:")

    for i in 1:n_uhes
        constrain = c_hidr[i]
        FCF_coef[est,i]  = JuMP.shadow_price(constrain)
        print(" dual: ",JuMP.shadow_price(constrain))
    end

    rhs = custo_presente_futuro
    for i in 1:n_uhes
        rhs = rhs - FCF_coef[est,i]*Vi[est,i]
    end
    FCF_indep[est,1] = -rhs

    print(FCF_coef)
    print(FCF_indep)

    #nova restr
    # @constraint(m, [i = 1:n_cut], -alpha + pi*Vf[usi] >= -FCF_rhs) #linha, coluna

    println("")
    println("################################################################")
end 