include("structs.jl")
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

function buscaPai(no, df_arvore)
    pai =  (df_arvore[(df_arvore.NO .== no), "NO_PAI"][1])
    return pai
end

function retornaListaCaminho(no, df_arvore)
    lista = []
    push!(lista,no)
    no_inicial = no
    periodo_no = (df_arvore[(df_arvore.NO .== no), "PER"][1])
    for est in 1:(periodo_no-1)
        pai = buscaPai(no_inicial, df_arvore)
        push!(lista,pai)
        no_inicial = pai
    end
    return lista
end




function calculaDistanciaDR(df_arvore_original, df_cenarios_original, df_arvore_reduzida, df_cenarios_reduzida)
    estagios = unique(df_arvore_reduzida[!, "PER"])
    estagios_rev = sort(unique(df_arvore_reduzida[!, "PER"]), rev=true)

    DR = 0
    for estagio in estagios_rev
        nos_originais_estagios = unique(df_arvore_original[df_arvore_original[:, "PER"] .== estagio, "NO"])
        nos_reduzido_estagio   = unique(df_arvore_reduzida[df_arvore_reduzida[:, "PER"] .== estagio, "NO"])
        for no_red in nos_reduzido_estagio
            for no_orig in nos_originais_estagios
                caminho_no_orig = retornaListaCaminho(no_orig, df_arvore_original)
                prob_cond = 1
                lista_probs_caminho = []
                for node in caminho_no_orig
                    prob_no = (df_arvore_original[(df_arvore_original.NO .== node), "PROB"][1])
                    push!(lista_probs_caminho, prob_no)
                    prob_cond = prob_cond*prob_no
                end
            
                vazoes_no_orig = df_cenarios_original[df_cenarios_original[:, "NO"] .== no_orig, :]
                vazoes_no_red  = df_cenarios_reduzida[df_cenarios_reduzida[:, "NO"] .== no_red, :]
                joined = innerjoin(vazoes_no_orig, vazoes_no_red, on="NOME_UHE", makeunique=true)
                #println("joined: ", joined)
                vazao_orig = joined[:, "VAZAO"]
                vazao_red  = joined[:, "VAZAO_1"]
                dist = norm(vazao_orig .- vazao_red)
                DR += dist*prob_cond
                #println("dist: ", dist)
            end
        end
    end

    return DR
end

str_caso = "C:/Users/testa/Documents/git/3dp-minilab/Carmen/exercicio_27cen_1D/27_Aberturas_Equiprovavel"
#str_caso = "C:/Users/testa/Documents/git/3dp-minilab/Capitulo_5/caso_mini_500Cen_cluster_semanais/avaliaArvoresRepresentativo"
#str_caso = "C:/Users/testa/Documents/git/3dp-minilab/Dissertacao/teste_simples/caso_mini_60"
Path_orig = str_caso*"/Pente_GVZP"
#Path_orig = str_caso*"/Arvore_GVZP"
PATH_ARVORE_ORIGINAL = Path_orig*"/arvore.csv"
df_arvore_original = CSV.read(PATH_ARVORE_ORIGINAL, DataFrame)
PATH_CENARIOS_ORIGINAL = Path_orig*"/cenarios.csv"
df_cenarios_original = CSV.read(PATH_CENARIOS_ORIGINAL, DataFrame)

lista_paths_red = ["Pente_8cen"]
lista_casos = ["A_8cen_1", "A_8cen_2", "Amostrado_C_1", "Amostrado_C_2", "Amostrado_C_3", "Amostrado_C_4"]
for path_red in lista_paths_red
    for caso in lista_casos
        global Path_red = str_caso*"/"*path_red*"/"*caso
        global PATH_ARVORE_REDUZIDA = Path_red*"/arvore.csv"
        global df_arvore_reduzida = CSV.read(PATH_ARVORE_REDUZIDA, DataFrame)
        global PATH_CENARIOS_REDUZIDA = Path_red*"/cenarios.csv"
        global df_cenarios_reduzida = CSV.read(PATH_CENARIOS_REDUZIDA, DataFrame)
        DR = calculaDistanciaDR(df_arvore_original, df_cenarios_original, df_arvore_reduzida, df_cenarios_reduzida)
        println(Path_red, ": ", DR)        
    end
end



#Path_red = str_caso*"/Arvore"
#Path_red = str_caso*"/Arvore_GVZP"
#PATH_ARVORE_REDUZIDA = Path_red*"/arvore.csv"
#df_arvore_reduzida = CSV.read(PATH_ARVORE_REDUZIDA, DataFrame)
#PATH_CENARIOS_REDUZIDA = Path_red*"/cenarios.csv"
#df_cenarios_reduzida = CSV.read(PATH_CENARIOS_REDUZIDA, DataFrame)
#(distancia_aninhada,solucao_planoTransporteCondicional , solucao_planoTransporte ) = calculaDistanciaAninhada(df_arvore_original, df_cenarios_original, df_arvore_reduzida, df_cenarios_reduzida)
#println(Path_red, ": ", distancia_aninhada[("o1","r1")])  



Path_red = str_caso*"/Pente"
Path_red = str_caso*"/Pente_GVZP"
PATH_ARVORE_REDUZIDA = Path_red*"/arvore.csv"
df_arvore_reduzida = CSV.read(PATH_ARVORE_REDUZIDA, DataFrame)
PATH_CENARIOS_REDUZIDA = Path_red*"/cenarios.csv"
df_cenarios_reduzida = CSV.read(PATH_CENARIOS_REDUZIDA, DataFrame)
DR = calculaDistanciaDR(df_arvore_original, df_cenarios_original, df_arvore_reduzida, df_cenarios_reduzida)
println(Path_red, ": ", DR)  
exit(1)
