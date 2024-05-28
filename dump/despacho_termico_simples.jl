
using JuMP, GLPK

m = Model(GLPK.Optimizer)
@variable(m, 0<= gt1_1 <= 15)
@variable(m, 0<= gt2_1 <= 10)
@variable(m, 0<= gt1_2 <= 20)
@variable(m, 0<= gt2_2 <= 30)

@variable(m, 0<= deficit_1 <=5000)
@variable(m, 0<= deficit_2 <=5000)

@objective(m, Min, 10gt1_1 + 25gt2_1 + 50gt1_2 + 100gt2_2 + 5000deficit_1 + 5000deficit_2)

@constraint(m, constraint1, gt1_1 + gt2_1 + deficit_1 + gh1_1 == 20)
@constraint(m, constraint2, gt1_2 + gt2_2 + deficit_2 + gh1_2 == 60)

print(m)
JuMP.optimize!(m)
println("Optimal Solutions:")
println("gt1 est1= ", JuMP.value(gt1_1))
println("gt2 est1= ", JuMP.value(gt2_1))
println("gt1 est2 = ", JuMP.value(gt1_2))
println("gt2 est2= ", JuMP.value(gt2_2))



println("def est1 = ", JuMP.value(deficit_1))
println("def est2= ", JuMP.value(deficit_2))
println("Dual Variables:")
println("dual1 = ", JuMP.shadow_price(constraint1))