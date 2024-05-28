
using JuMP, GLPK

m = Model(GLPK.Optimizer)
@variable(m, 0<= gt1_1 <= 15)
@variable(m, 0<= gt2_1 <= 10)
@variable(m, 0<= gt1_2 <= 20)
@variable(m, 0<= gt2_2 <= 30)

@variable(m, 0<= gh1_1 <= 10)
@variable(m, 0<= gh1_2 <= 15)

@variable(m, 0<= turb1_1 <= 20)
@variable(m, 0<= turb1_2 <= 20)
@variable(m, 0<= vert1_1 <= 20)
@variable(m, 0<= vert1_2 <= 20)
@variable(m, 0<= Vi1_2 <= 20)
@variable(m, 0<= Vf1_2 <= 20)


@variable(m, 0<= deficit_1 <=5000)
@variable(m, 0<= deficit_2 <=5000)

@objective(m, Min, 0.1vert1_1 + 0.1vert1_2 + 10gt1_1 + 25gt2_1 + 50gt1_2 + 100gt2_2 + 5000deficit_1 + 5000deficit_2)

@constraint(m, balanco_1, Vi1_2 + turb1_1 + vert1_1 == 10 + 5)
@constraint(m, balanco_2, Vf1_2 + turb1_2 + vert1_2 == Vi1_2 + 5)

@constraint(m,  gh1_1 == turb1_1)
@constraint(m,  gh1_2 == turb1_2)

@constraint(m, constraint1, gt1_1 + gt2_1 + deficit_1 + gh1_1 == 20)
@constraint(m, constraint2, gt1_2 + gt2_2 + deficit_2 + gh1_2 == 60)

print(m)
JuMP.optimize!(m)
println("Optimal Solutions:")
println("gt1 est1= ", JuMP.value(gt1_1))
println("gt2 est1= ", JuMP.value(gt2_1))
println("gh1 est1= ", JuMP.value(gh1_1))
println("turb1_1= ", JuMP.value(turb1_1))
println("vert1_1= ", JuMP.value(vert1_1))
println("Vi1_1= ", 10)
println("Vf1_2= ", JuMP.value(Vi1_2))


println("gt1 est2 = ", JuMP.value(gt1_2))
println("gt2 est2= ", JuMP.value(gt2_2))
println("gh1 est2= ", JuMP.value(gh1_2))
println("turb1_2= ", JuMP.value(turb1_2))
println("vert1_2= ", JuMP.value(vert1_2))
println("Vi1_2= ", JuMP.value(Vi1_2))
println("Vf1_2= ", JuMP.value(Vf1_2))


println("def est1 = ", JuMP.value(deficit_1))
println("def est2= ", JuMP.value(deficit_2))
println("Dual Variables:")
println("dual1 = ", JuMP.shadow_price(constraint1))