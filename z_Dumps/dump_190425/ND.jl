include("DefStructs.jl")
using JSON
using CSV
using DataFrames
#using Graphs
using LightGraphs
using SparseArrays
using DataStructures
using LinearAlgebra
using JuMP, GLPK, Plots, Measures, Plots, SparseArrays, DataFrames, Dates

function getFilhos(no, df_arvore)
    filhos = df_arvore[df_arvore.NO_PAI .== no, :NO]
    return filhos
end

function buscaPai(no)
    pai =  (df_arvore[(df_arvore.NO .== no), "NO_PAI"][1])
    return pai
end

function retornaListaCaminho(no)
    lista = []
    push!(lista,no)
    no_inicial = no
    periodo_no = (df_arvore[(df_arvore.NO .== no), "PER"][1])
    for est in 1:(periodo_no-1)
        pai = buscaPai(no_inicial)
        push!(lista,pai)
        no_inicial = pai
    end
    return lista
end

function montaArvore(no_pai, df_arvore, lista_total_de_nos)
    
    periodo = df_arvore[df_arvore.NO .== no_pai.codigo, :PER][1]  # Extract first element
    codigo_interno = 1
    lista_filhos = []
    #println("pai cod: ", no_pai.codigo)
    filhos = getFilhos(no_pai.codigo)
    for filho in filhos
        no_filho = no(filho, periodo + 1, codigo_interno, no_pai, [])
        push!(lista_total_de_nos, no_filho)
        push!(no_pai.filhos, no_filho)
        push!(lista_filhos, no_filho)
        codigo_interno += 1
        montaArvore(no_filho, df_arvore, lista_total_de_nos)
    end
end

str_caso = "C:/Users/testa/Documents/git/3dp-minilab/Carmen/teste_ND"
Path_orig = str_caso*"/Original"
Path_red = str_caso*"/Reduzida"
PATH_ARVORE_ORIGINAL = Path_orig*"/arvore.csv"
PATH_ARVORE_REDUZIDA = Path_red*"/arvore.csv"
df_arvore_original = CSV.read(PATH_ARVORE_ORIGINAL, DataFrame)
df_arvore_reduzida = CSV.read(PATH_ARVORE_REDUZIDA, DataFrame)
PATH_CENARIOS_ORIGINAL = Path_orig*"/cenarios.csv"
PATH_CENARIOS_REDUZIDA = Path_red*"/cenarios.csv"
df_cenarios_original = CSV.read(PATH_CENARIOS_ORIGINAL, DataFrame)
df_cenarios_reduzida = CSV.read(PATH_CENARIOS_REDUZIDA, DataFrame)




#mapaProbCondicionalNo = Dict{Int, Float64}()
#for no in lista_total_de_nos
#    mapaProbCondicionalNo[no.codigo] = 1
#    for no_caminho in retornaListaCaminho(no.codigo)
#        mapaProbCondicionalNo[no.codigo] *= (dat_prob[(dat_prob.NO .== no_caminho), "PROBABILIDADE"][1])
#    end
#end
#println(mapaProbCondicionalNo)

println(df_arvore_original)
println(df_arvore_reduzida)
println(df_cenarios_original)
println(df_cenarios_reduzida)

estagios = unique(df_arvore_reduzida[!, "PER"])


distancia_aninhada = Dict{Tuple{String, String}, Float64}()
planoTransporte = Dict{Tuple{String, String}, JuMP.VariableRef}()
solucao_planoTransporte = Dict{Tuple{String, String}, Float64}()
for estagio in sort(estagios, rev=true)
    nos_originais_estagios = unique(df_arvore_original[df_arvore_original[:, "PER"] .== estagio, "NO"])
    nos_reduzido_estagio   = unique(df_arvore_reduzida[df_arvore_reduzida[:, "PER"] .== estagio, "NO"])
    for no_orig in nos_originais_estagios
        for no_red in nos_reduzido_estagio
            distancia_aninhada[("o" * string(no_orig), "r" * string(no_red))] = 0
            solucao_planoTransporte[("o" * string(no_orig), "r" * string(no_red))] = 0
            planoTransporte[("o" * string(no_orig), "r" * string(no_red))] = @variable(m, base_name="pi_o$(no_filho_orig)_r$(no_filho_red)")
        end
    end
end

deleteat!(estagios, findfirst(==(maximum(estagios)), estagios))
println(estagios)

for estagio in sort(estagios, rev=true)
    nos_originais_estagios = unique(df_arvore_original[df_arvore_original[:, "PER"] .== estagio, "NO"])
    nos_reduzido_estagio   = unique(df_arvore_reduzida[df_arvore_reduzida[:, "PER"] .== estagio, "NO"])
    println("ORIG: ", nos_originais_estagios)
    println("RED: ", nos_reduzido_estagio)
    for no_orig in nos_originais_estagios
        for no_red in nos_reduzido_estagio
            filhos_originais = getFilhos(no_orig, df_arvore_original)
            filhos_red = getFilhos(no_red, df_arvore_reduzida)
            println("no_orig: ", no_orig, " no_red: ", no_red)
            println("FIlhos Orig: ", filhos_originais, " Filhos_red: ", filhos_red)
            distancia = Dict{Tuple{String, String}, Float64}()
            constraint_dict = Dict{String, JuMP.ConstraintRef}()
            global m = Model(GLPK.Optimizer)
            for no_filho_orig in filhos_originais
                for no_filho_red in filhos_red
                    vazoes_no_filho_orig = df_cenarios_original[df_cenarios_original[:, "NO"] .== no_filho_orig, :]
                    vazoes_no_filho_red  = df_cenarios_reduzida[df_cenarios_reduzida[:, "NO"] .== no_filho_red, :]
                    #print("no_filho_orig: ", no_filho_orig, " no_filho_red: ", no_filho_red)
                    #println("vazoes_no_filho_orig: ", vazoes_no_filho_orig, " vazoes_no_filho_red: ", vazoes_no_filho_red)
                    #sorted_orig = sort(vazoes_no_filho_orig, :NOME_UHE)
                    #sorted_red  = sort(vazoes_no_filho_red,  :NOME_UHE)
                    #println("sorted_orig: ", sorted_orig, " sorted_red: ", sorted_red)
                    ## Extract VAZAO as vectors
                    #vazao_orig = sorted_orig[:, "VAZAO"]
                    #vazao_red  = sorted_red[:, "VAZAO"]
                    #println("vazao_orig: ", vazao_orig, " vazao_red: ", vazao_red)
                    @assert length(unique(vazoes_no_filho_orig[:, "NOME_UHE"])) == nrow(vazoes_no_filho_orig)
                    @assert length(unique(vazoes_no_filho_red[:, "NOME_UHE"])) == nrow(vazoes_no_filho_red)
                    joined = innerjoin(vazoes_no_filho_orig, vazoes_no_filho_red, on="NOME_UHE", makeunique=true)
                    #println("joined: ", joined)
                    vazao_orig = joined[:, "VAZAO"]
                    vazao_red  = joined[:, "VAZAO_1"]
                    #println("vazao_orig: ", vazao_orig, " vazao_red: ", vazao_red)
                    dist = norm(vazao_orig .- vazao_red)
                    #println(dist)  # This will give the Euclidean distance
                    distancia[("o" * string(no_filho_orig), "r" * string(no_filho_red))] = dist
                end
            end

            @objective(m, Min, sum( (distancia[("o" * string(no_filho_orig), "r" * string(no_filho_red))] + distancia_aninhada[("o" * string(no_filho_orig), "r" * string(no_filho_red))]) * planoTransporte[("o" * string(no_filho_orig), "r" * string(no_filho_red))] for no_filho_orig in filhos_originais, no_filho_red in filhos_red))
            ## ADICIONAR RESTRICOES
            for no_filho_orig in filhos_originais
                #print("est: ", est, " no: ", no.codigo, " etapa: ", etapa)
                prob_filho_orig = df_arvore_original[df_arvore_original[:, "NO"] .== no_filho_orig, "PROB"][1]
                constraint_dict["o" * string(no_filho_orig)] = @constraint(m, sum(planoTransporte[("o" * string(no_filho_orig), "r" * string(no_filho_red))] for no_filho_red in filhos_red) == prob_filho_orig) 
            end
            
            for no_filho_red in filhos_red
                prob_filho_red = df_arvore_reduzida[df_arvore_reduzida[:, "NO"] .== no_filho_red, "PROB"][1]
                constraint_dict["r" * string(no_filho_red)] = @constraint(m, sum(planoTransporte[("o" * string(no_filho_orig), "r" * string(no_filho_red))] for no_filho_orig in filhos_originais) == prob_filho_red) 
            end

            for no_filho_orig in filhos_originais
                for no_filho_red in filhos_red
                    @constraint(  m, planoTransporte[("o" * string(no_filho_orig), "r" * string(no_filho_red))]  >= 0 ) 
                    
                end
            end
            println(m)


            JuMP.optimize!(m) 
            status = JuMP.termination_status(m)
            if status == MOI.INFEASIBLE || status == MOI.INFEASIBLE_OR_UNBOUNDED
                #error("Optimization problem is infeasible. Stopping execution.")
                println("Optimization problem is infeasible. Stopping execution.")
            end
            

            dist_aninhada = JuMP.objective_value(m)
            distancia_aninhada[("o"*string(no_orig), "r"*string(no_red))] = dist_aninhada
            println("Total FOB value: ", dist_aninhada)
            for no_filho_orig in filhos_originais
                for no_filho_red in filhos_red
                    solucao_planoTransporte[("o" * string(no_filho_orig), "r" * string(no_filho_red))] = JuMP.value(planoTransporte[("o" * string(no_filho_orig), "r" * string(no_filho_red))])
                    println(no_filho_orig, " ", no_filho_red, " : ", solucao_planoTransporte[("o" * string(no_filho_orig), "r" * string(no_filho_red))])
                end
            end
        end
    end
end






exit(1)
lista_total_de_nos = []
no1 = no(1, 1, 1, 0, [])
push!(lista_total_de_nos, no1)
montaArvore(no1, df_arvore, lista_total_de_nos)
#println(dat_prob)
#println(df_arvore)
dat_prob = df_arvore[:, [:NO, :PROB]]
rename!(dat_prob, :PROB => :PROBABILIDADE)
#println(dat_prob)
#exit(1)
mapa_periodos = OrderedDict()
for est in unique(df_arvore.PER)
    periodo = tipo_periodo(est,[])
    mapa_periodos[est] = periodo
end
for no_alvo in lista_total_de_nos
    push!(mapa_periodos[no_alvo.periodo].nos, no_alvo)
end



















