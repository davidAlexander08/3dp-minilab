include("LeituraEntrada.jl")
using JSON
using CSV
using DataFrames
#using Graphs
using LightGraphs
using SparseArrays
using DataStructures


dicionario_barraDE_linha = OrderedDict()
for barra in lista_barras
    vetor_linhas = []
    dicionario_barraDE_linha[barra.codigo] = vetor_linhas
end

for linha in lista_linhas
    push!(dicionario_barraDE_linha[linha.de.codigo], linha)
end

global contador_graph
global indiceIlhaEletrica
mapa_estagio_ilha = OrderedDict()
for est in 1:caso.n_est
    
    dicionario_indiceVertice_Barra = OrderedDict()
    dicionario_Barra_indiceVertice = OrderedDict()
    g = SimpleGraph()
    contador_graph = 1
    for barra in lista_barras
        add_vertex!(g)
        dicionario_indiceVertice_Barra[contador_graph] = barra
        dicionario_Barra_indiceVertice[barra] = contador_graph
        contador_graph = contador_graph +  1
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
    
    #@info "Definindo as ilhas elétricas da rede $(file_path_rede)"
    lista_ilhas = []
    indiceIlhaEletrica = 0
    for slack in lista_barras_slack
        
        indiceIlhaEletrica += 1
        lista_barras_da_ilha = []
        lista_linhas_da_ilha = []
        push!(lista_barras_da_ilha, slack)
        encontra_adjacentes_acrescenta_lista(lista_barras_da_ilha, g, dicionario_Barra_indiceVertice[slack])
        #println(lista_barras_da_ilha)
        eliminaDuplicadas = OrderedDict()
        # ELIMINA DUPLICATAS
        for barra in lista_barras_da_ilha
            eliminaDuplicadas[barra] = barra
        end
        lista_barras_da_ilha = []
        for key in keys(eliminaDuplicadas)
            push!(lista_barras_da_ilha, key)
        end
        for barra in lista_barras_da_ilha
            if haskey(dicionario_barraDE_linha, barra.codigo)
                for linha_barra in dicionario_barraDE_linha[barra.codigo]
                    push!(lista_linhas_da_ilha, linha_barra)
                end
            end
        end
    
        ## CALCULANDO A MATRIZ SUSCEPTANCIA
    
    
        barras_semSlack = []
        mapaSusceptanciaDiagonalPrincipal = OrderedDict()
        for barra in lista_barras_da_ilha
            mapaSusceptanciaDiagonalPrincipal[barra.codigo] = 0
            if barra.codigo != slack.codigo
                push!(barras_semSlack,barra)
            end
        end
    
        global indice = 1
        mapaPosicaoBarras = OrderedDict()
        for barra in barras_semSlack
            mapaPosicaoBarras[barra.codigo] = indice
            indice = indice + 1
        end
        
        matrizSusceptancia = spzeros(length(lista_barras_da_ilha)-1, length(lista_barras_da_ilha)-1)
    
        matrizIncidencia = spzeros(length(lista_linhas_da_ilha), length(lista_barras_da_ilha)-1)
    
        matrizDiagonalDeSusceptancia = spzeros(length(lista_linhas_da_ilha), length(lista_linhas_da_ilha))
        contador = 1
        for linha in lista_linhas_da_ilha
            if linha.de.codigo != slack.codigo
                matrizIncidencia[contador, mapaPosicaoBarras[linha.de.codigo]] = 1
            end
            if linha.para.codigo != slack.codigo
                matrizIncidencia[contador, mapaPosicaoBarras[linha.para.codigo]] = -1
            end
    
            matrizDiagonalDeSusceptancia[contador, contador] = matrizDiagonalDeSusceptancia[contador, contador]  + 1/linha.X
    
            contador = contador + 1
    
    
            codigo_de = linha.de.codigo
            codigo_para = linha.para.codigo
            susceptancia = 1/linha.X
            if codigo_de != slack.codigo && codigo_para != slack.codigo
                indiceDE = mapaPosicaoBarras[codigo_de]
                indicePARA = mapaPosicaoBarras[codigo_para]
                matrizSusceptancia[indiceDE, indicePARA] += -susceptancia
                matrizSusceptancia[indicePARA, indiceDE] += -susceptancia
            end
            mapaSusceptanciaDiagonalPrincipal[codigo_de] += susceptancia
            mapaSusceptanciaDiagonalPrincipal[codigo_para] += susceptancia
        
        end
    
        for barra in lista_barras_da_ilha
            codigo = barra.codigo
            if codigo != slack.codigo
                indice = mapaPosicaoBarras[codigo]
                matrizSusceptancia[indice,indice] = mapaSusceptanciaDiagonalPrincipal[codigo]
            end
        end
    
        matrizB = matrizDiagonalDeSusceptancia*matrizIncidencia
        matrizSensibilidade = spzeros(length(lista_linhas_da_ilha), length(lista_barras_da_ilha)-1)
        
        vetorPotenciaCarga = []
        for barra in lista_barras_da_ilha
            if barra.codigo != slack.codigo
                push!(vetorPotenciaCarga,  barra.carga[est]) ## PEGANDO O PRIMEIRO VALOR DA CARGA, MAS NA VERDADE É TEMPORAL
            end
        end
        
        fluxo_linhas = []
        contador = 1
        for linha in lista_linhas_da_ilha
            linhaMatrizSensibilidade = matrizSusceptancia \ Array(matrizB[contador,:])
            RHS = linha.Capacidade[est] +transpose(linhaMatrizSensibilidade)*vetorPotenciaCarga
            #println("RHS: ",  RHS, " linhaMatrizSensibilidade: ", Array(linhaMatrizSensibilidade))
            fluxo = FluxoNasLinhas()
            fluxo.linhaMatrizSensibilidade = linhaMatrizSensibilidade
            fluxo.RHS = RHS
            fluxo.de = linha.de
            fluxo.para = linha.para
            fluxo.linha = linha
            push!(fluxo_linhas, fluxo)
            contador = contador + 1
        end
    
    
        ilha = IlhaConfig(indiceIlhaEletrica , slack , lista_barras_da_ilha, lista_linhas_da_ilha, matrizSusceptancia, matrizDiagonalDeSusceptancia, matrizIncidencia, fluxo_linhas)
        push!(lista_ilhas, ilha)
    
    end


    mapa_estagio_ilha[est] = lista_ilhas

end

