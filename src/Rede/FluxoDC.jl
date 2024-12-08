include("RedeEletrica.jl")
using JSON
using CSV
using DataFrames
#using Graphs
using LightGraphs
using SparseArrays
using DataStructures


function calculaVetorPotenciaLiquidaDaIlha(ilha)
    ## CALCULO DA POTENCIA LIQUIDA
    for barra in ilha.barras
        barra.potenciaLiquida = barra.potenciaGerada - barra.carga
        #println("Codigo Barra: ", barra.codigo, " Potencia Liquida: ", barra.potenciaLiquida)
    end
    # TRAFO DEFASADOR
    for fluxo in ilha.fluxo_linhas
        if fluxo.linha.defasador != 0
            valor_pi = 3.141593
            anguloDefasadorRad = fluxo.linha.defasador*valor_pi/180
            fatorDefasador = anguloDefasadorRad/linha.X

            potenciaLiquidaDe = fluxo.linha.de.potenciaLiquida
            potenciaLiquidaPara = fluxo.linha.para.potenciaLiquida

            fluxo.linha.de.potenciaLiquida = potenciaLiquidaDe - fatorDefasador
            fluxo.linha.para.potenciaLiquida = potenciaLiquidaPara + fatorDefasador
        end
    end
    #FIM TRAFO DEFASADOR
    vetorPotenciaLiquida = []
    for barra in ilha.barras
        if barra.codigo != ilha.slack.codigo
            println("Codigo Barra: ", barra.codigo, " Potencia Liquida: ", barra.potenciaLiquida)
            push!(vetorPotenciaLiquida, barra.potenciaLiquida)
        end
    end

    return vetorPotenciaLiquida
end



function calculaFluxosIlhaMetodoDeltaDC(ilha)
    vetorPotenciaLiquida = calculaVetorPotenciaLiquidaDaIlha(ilha)

    ## CALCULO DO FLUXO
    delta_sparse = ilha.matrizSusceptancia \ vetorPotenciaLiquida
    #println(delta_sparse)

    anguloCadaBarra = OrderedDict()
    contador = 1
    for barra in ilha.barras
        anguloCadaBarra[ilha.slack.codigo] = 0
        if barra.codigo != ilha.slack.codigo
            anguloCadaBarra[barra.codigo] = delta_sparse[contador]
            contador = contador + 1
        end
    end

    for barra in ilha.barras
        println("Barra: ", barra.codigo, " Angulo: ", anguloCadaBarra[barra.codigo])
    end


    lista_fluxos_linha = []
    for fluxo in ilha.fluxo_linhas
        anguloBarraDe = anguloCadaBarra[fluxo.linha.de.codigo]
        anguloBarraPara = anguloCadaBarra[fluxo.linha.para.codigo]
        valor_fluxo = (anguloBarraDe - anguloBarraPara)/fluxo.linha.X

        if(fluxo.linha.defasador != 0)
            valor_pi = 3.141593
            anguloDefasadorRad = fluxo.linha.X*valor_pi/180
            fatorDefasador = anguloDefasadorRad/fluxo.linha.X
            valor_fluxo = (anguloBarraDe - anguloBarraPara + anguloDefasadorRad)/fluxo.linha.X
        end
        fluxo.anguloBarraDe = anguloBarraDe
        fluxo.anguloBarraPara = anguloBarraPara
        fluxo.fluxoDePara = valor_fluxo
    end
end

function calculaFluxosIlhaMetodoSensibilidadeDC(ilha)
    vetorPotenciaLiquida = calculaVetorPotenciaLiquidaDaIlha(ilha)
    for fluxo in ilha.fluxo_linhas
        fluxo.fluxoDePara = transpose(fluxo.linhaMatrizSensibilidade)*vetorPotenciaLiquida
    end
end