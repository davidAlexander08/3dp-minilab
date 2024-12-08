
include("DefStructs.jl")

using JSON
using CSV
using DataFrames
#using Graphs
using LightGraphs
using SparseArrays
using DataStructures

#CONFIG_PATH = "caso_deterministico/dadosEntrada.json"
#PATH_VAZOES = "caso_deterministico/vazao.csv"
#PATH_PROBABILIDADES = "caso_deterministico/probabilidades.csv"

#CONFIG_PATH = "caso_arvore/dadosEntrada.json"
#PATH_VAZOES = "caso_arvore/vazao.csv"
#PATH_PROBABILIDADES = "caso_arvore/probabilidades.csv"

CONFIG_PATH = "caso_decomp/dadosEntrada.json"
PATH_VAZOES = "caso_decomp/vazao.csv"
PATH_PROBABILIDADES = "caso_decomp/probabilidades.csv"
PATH_HORAS = "caso_decomp/horas.csv"

@info "Lendo arquivo de configuração $(CONFIG_PATH)"
dict = JSON.parsefile(CONFIG_PATH; use_mmap=false)

# UTEs
usinas = dict["UTEs"]
lista_utes = []
for usi in usinas
    usina = UTEConfigData(usi["NOME"],usi["GTMIN"], usi["GTMAX"], usi["CUSTO_GERACAO"])
    push!(lista_utes,usina)
end
println(lista_utes)


@info "Lendo arquivo de vazoes $(PATH_VAZOES)"
dat_vaz = CSV.read(PATH_VAZOES, DataFrame)

@info "Lendo arquivo de probabilidades $(PATH_PROBABILIDADES)"
dat_prob = CSV.read(PATH_PROBABILIDADES, DataFrame)
#print(dat_vaz[(dat_vaz.NOME_UHE .== 1) .& (dat_vaz.PERIODO .== 1), :])
#print(dat_vaz[(dat_vaz.NOME_UHE .== 1) .& (dat_vaz.PERIODO .== 1), "VAZAO"][1])

@info "Lendo arquivo de horas $(PATH_HORAS)"
dat_horas = CSV.read(PATH_HORAS, DataFrame)

# UHEs
usinas = dict["UHEs"]
lista_uhes = []
for usi in usinas
    usina = UHEConfigData(usi["NOME"],usi["JUSANTE"],usi["GHMIN"], usi["GHMAX"], usi["TURBMAX"], usi["VOLUME_MINIMO"], usi["VOLUME_MAXIMO"], usi["VOLUME_INICIAL"])
    push!(lista_uhes,usina)
end
println(lista_uhes)

n_iter = dict["MAX_ITERACOES"]
n_est = dict["ESTAGIOS"]
n_term = size(lista_utes)[1]
n_uhes = size(lista_uhes)[1]
estrutura_arvore = dict["ARVORE"]
caso = CaseData(n_iter, n_est, n_term, n_uhes, estrutura_arvore)
println(caso)

#SISTEMA
sist = dict["SISTEMA"]
sistema = SystemConfigData(sist["CUSTO_DEFICIT"], sist["DEMANDA"])
println(sistema)