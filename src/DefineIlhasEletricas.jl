include("LeituraEntrada.jl")
using JSON
using CSV
using DataFrames
#using Graphs
using LightGraphs
using SparseArrays
using DataStructures
using LinearAlgebra
using IterativeSolvers

dicionario_barraDE_linha = OrderedDict()
for barra in lista_barras
    vetor_linhas = []
    dicionario_barraDE_linha[barra.codigo] = vetor_linhas
end

for linha in lista_linhas
    push!(dicionario_barraDE_linha[linha.de.codigo], linha)
end

dicionario_indiceVertice_Barra = OrderedDict()
dicionario_Barra_indiceVertice = OrderedDict()
mapaLinhaFluxo = OrderedDict()
g = SimpleGraph()

for (contador_graph,barra) in enumerate(lista_barras)
    add_vertex!(g)
    dicionario_indiceVertice_Barra[contador_graph] = barra
    dicionario_Barra_indiceVertice[barra] = contador_graph
#    contador_graph = contador_graph +  1
end

for linha in lista_linhas
    if linha.indice == 1 
        #add_edge!(g, linha.de.codigo, linha.para.codigo)
        add_edge!(g, dicionario_Barra_indiceVertice[linha.de], dicionario_Barra_indiceVertice[linha.para])
    end
end

edges_list = collect(edges(g))  # Collect edges into a list


function encontra_adjacentes_acrescenta_lista(lista_barras_da_ilha, grafoDaRede, indice_barra_slack)
    # Iterate over adjacent vertices
    auxiliar = []
    for vd in neighbors(grafoDaRede, indice_barra_slack)
        push!(lista_barras_da_ilha, dicionario_indiceVertice_Barra[vd])  # Add to vetorCodigoBarrasDaIlha
        push!(auxiliar, vd)  # Add to auxiliar
    end

    for idVertice in auxiliar
        edges_list = collect(edges(g))  # Collect edges into a list
        vertices_list = collect(vertices(g))
        rem_edge!(grafoDaRede, indice_barra_slack, idVertice)
        edges_list = collect(edges(g))  # Collect edges into a list
        vertices_list = collect(vertices(g))
    end

    for idVertice in auxiliar
        encontra_adjacentes_acrescenta_lista(lista_barras_da_ilha,grafoDaRede, idVertice)
    end
end

@info "Definindo as ilhas elétricas da rede"

function calculaIlhasEletricas(lista_barras_slack)
    lista_ilhas = []
    indiceIlhaEletrica = 0
    
    for slack in lista_barras_slack
        
        indiceIlhaEletrica += 1
        lista_barras_da_ilha = []
        lista_linhas_da_ilha = []
        lista_linhas_nao_ativas = []
        push!(lista_barras_da_ilha, slack)
        encontra_adjacentes_acrescenta_lista(lista_barras_da_ilha, g, dicionario_Barra_indiceVertice[slack])
        #println(lista_barras_da_ilha)

        lista_barras_da_ilha = unique(lista_barras_da_ilha)
        sort!(lista_barras_da_ilha, by = b -> b.codigo)

        for barra in lista_barras_da_ilha
            mapaCodigoBarra[barra.codigo] = barra
            if haskey(dicionario_barraDE_linha, barra.codigo)
                for linha_barra in dicionario_barraDE_linha[barra.codigo]
                    push!(lista_linhas_da_ilha, linha_barra)
                end
            end
        end


        #ilha = IlhaConfig(indiceIlhaEletrica , slack , lista_barras_da_ilha, lista_linhas_da_ilha, matrizSusceptancia, matrizDiagonalDeSusceptancia, matrizIncidencia, fluxo_linhas, [], [], mapaCodigoBarra)
        ilha = IlhaConfig()
        ilha.codigo = indiceIlhaEletrica
        ilha.slack = slack
        ilha.barras =lista_barras_da_ilha
        ilha.linhas = lista_linhas_da_ilha
        push!(lista_ilhas, ilha)
    end
    return lista_ilhas
end


lista_ilhas_eletricas = calculaIlhasEletricas(lista_barras_slack)
for ilha in lista_ilhas_eletricas
    for est in caso.n_est
        vetorBarrasAtivas= []
        vetorBarrasNaoAtivas =[]
        vetorLinhasAtivas = []
        vetorLinhasNaoAtivas = []
        for barra in ilha.barras
            if barra.estadoDeOperacao[est] == 1
                push!(vetorBarrasAtivas, barra)
            else
                push!(vetorBarrasNaoAtivas, barra)
            end
        end
        for linha in ilha.linhas
            if linha.estadoDeOperacao[est] == 1
                push!(vetorLinhasAtivas, linha)
            else
                push!(vetorLinhasNaoAtivas, linha)
            end
        end
        ilha.barrasAtivas[est]      =   vetorBarrasAtivas
        ilha.barrasNaoAtivas[est]   =   vetorBarrasNaoAtivas
        ilha.linhasAtivas[est]      =   vetorLinhasAtivas
        ilha.linhasNaoAtivas[est]   =   vetorLinhasNaoAtivas
    end
end











