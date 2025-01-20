using CSV
using DataFrames

df = CSV.read("CenariosSemanais/vazoesDiariasCamargos.csv", DataFrame)
println(df)