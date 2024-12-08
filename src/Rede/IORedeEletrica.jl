
include("StructsRede.jl")

using JSON
using CSV
using DataFrames
#using Graphs
using LightGraphs
using SparseArrays
using DataStructures


file_path_rede = "3barras.pwf"

@info "Lendo barras da rede $(file_path_rede)"
lista_barras = []
lista_barras_slack = []
lista_barras_sem_slack = []
dicionario_codigo_barra = OrderedDict()
contador_linha = 0
file_path_out = "out_barras.txt"
open(file_path_out, "w") do file_out
    open(file_path_rede, "r") do file
        in_dbar_section = false
        for line in eachline(file)

            if in_dbar_section && startswith(line, "99999")
                break
            end

            if in_dbar_section  
                if !occursin("(Num)", line)
                    codigo = isempty(strip(line[1:5])) ? 0 : Int32(parse(Int, line[1:5]) )
                    potenciaGeradaAtiva = isempty(strip(line[33:37])) ? 0 : Float64(parse(Float64, line[33:37]))
                    cargaAtiva = isempty(strip(line[59:63])) ? 0 : Float64(parse(Float64, line[59:63]))
                    area = isempty(strip(line[74:76])) ? 0 : Int32(parse(Int, line[74:76]) )
                    LigadaOuDesligada = line[7]
                    if LigadaOuDesligada == "L"
                        LigadaOuDesligada = 1
                    else
                        LigadaOuDesligada = 0
                    end
                    tipo = isempty(line[8]) ? 0 : Int32(parse(Int, line[8]) )
                    
                    barra = BarraConfig()
                    barra.codigo = codigo
                    barra.potenciaGerada = potenciaGeradaAtiva/100
                    barra.carga = cargaAtiva/100
                    barra.area = area
                    barra.estadoDeOperacao = LigadaOuDesligada
                    barra.tipo = tipo
                    println(file_out, " ", barra.codigo , "  ", barra.potenciaGerada, "   ", barra.carga, "    ", barra.area, "     ", barra.estadoDeOperacao, "    ", barra.tipo)
                    dicionario_codigo_barra[codigo] = barra
                    push!(lista_barras, barra)
                    if barra.tipo == 2
                        push!(lista_barras_slack,barra)
                    else
                        push!(lista_barras_sem_slack, barra)
                    end
                else
                    println(file_out, "Cod PotG  Carg  Area  Est  Tipo")
                end
            end

            if startswith(line, "DBAR")
                in_dbar_section = true
            end

        end
    end
end



@info "Lendo linhas da rede $(file_path_rede)"
lista_linhas = []

contador_linha = 0
file_path_out = "out_linhas.txt"
open(file_path_out, "w") do file_out
    open(file_path_rede, "r") do file
        in_dlin_section = false
        for line in eachline(file)

            if in_dlin_section && startswith(line, "99999")
                break
            end

            if in_dlin_section  
                if !occursin("(De )", line)
                    de = isempty(strip(line[1:5])) ? 0 : Int32(parse(Int, line[1:5]) )
                    para = isempty(strip(line[11:15])) ? 0 : Int32(parse(Int, line[11:15]) )
                    indice = isempty(strip(line[16:17])) ? 0 : Int32(parse(Int, line[16:17]) )
                    X = isempty(strip(line[27:32])) ? 0 : Float64(parse(Float64, line[27:32]))
                    MVAR = isempty(strip(line[33:38])) ? 0 : Float64(parse(Float64, line[33:38]))
                    defasador = isempty(strip(line[54:58])) ? 0 : Float64(parse(Float64, line[54:58]))

                    linha = LinhaConfig()
                    linha.de = dicionario_codigo_barra[de]
                    linha.para = dicionario_codigo_barra[para]
                    linha.indice = indice
                    linha.X = X/100
                    linha.MVAR = MVAR
                    linha.defasador = defasador
                    println(file_out, " ", linha.de.codigo , "  ", linha.para.codigo, "     ", linha.indice, "     ", linha.X/100, "     ", linha.MVAR, "    ", linha.defasador)
                    push!(lista_linhas, linha)
                else
                    println(file_out, "De Para  Indice   X     MVAR    Defasa")
                end
            end

            if startswith(line, "DLIN")
                in_dlin_section = true
            end

        end
    end
end
