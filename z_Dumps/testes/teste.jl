#using JuMP, HiGHS
using JuMP, GLPK
using Statistics

# Problem Data
T = 2  # Two-stage problem
d = [50, 60]  # Demand in each stage
c = 10  # Cost of thermal generation
x_max = 80  # Max hydro generation
y_max = 100  # Max thermal generation
s_max = 100  # Max reservoir storage

# Uncertain inflows (two scenarios)
w_scenarios = [30, 50]  # Possible inflow values at t=1
p_scenarios = [0.5, 0.5]  # Probabilities of each scenario

# Create JuMP Model
model = Model(GLPK.Optimizer)

# Decision variables: LDR coefficients
@variable(model, alpha[1:T] >= 0)  # Constant term
@variable(model, beta[1:T] >= 0)   # Coefficient for inflow

# Stage 1 Storage Balance
@constraint(model, s1_balance,  alpha[1] <= s_max)

# Stage 2 Constraints for each scenario
for (w, p) in zip(w_scenarios, p_scenarios)
    x1 = alpha[1] + beta[1] * w  # LDR Hydro Dispatch (t=1)
    s2 = s_max + w - x1  # Reservoir storage at t=2
    
    @constraint(model, 0 <= x1 <= x_max)  # Hydro generation limit
    @constraint(model, 0 <= s2 <= s_max)  # Reservoir limit
    
    x2 = alpha[2] + beta[2] * w  # LDR Hydro Dispatch (t=2)
    y2 = d[2] - x2  # Thermal generation at t=2
    
    @constraint(model, 0 <= x2 <= x_max)  # Hydro limits at t=2
    @constraint(model, 0 <= y2 <= y_max)  # Thermal limits at t=2
end

# Objective: Minimize Expected Cost
@objective(model, Min, c * (d[2] - (alpha[2] + beta[2] * mean(w_scenarios))))

# Solve
optimize!(model)

# Print results
println("Optimal α values: ", value.(alpha))
println("Optimal β values: ", value.(beta))