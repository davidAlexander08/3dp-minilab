using JuMP, GLPK, DataFrames
include("src/PDD.jl")  # Adjust the path to where PDD.jl is located

# Explicitly precompile critical methods without running them
function precompile_workload()
    #executaModelo()  # Chamada direta
end

precompile_workload()