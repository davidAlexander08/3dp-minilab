include("ConfiguraRedeEletrica.jl")
using JSON
using CSV
using DataFrames
#using Graphs
using LightGraphs
using SparseArrays
using DataStructures


function calculaVetorPotenciaLiquidaDaIlha(ilha,iter,est, i_no)
    ## CALCULO DA POTENCIA LIQUIDA
    for barra in ilha.barrasAtivas[est]
        barra.potenciaLiquida[iter,i_no.codigo] = get(barra.potenciaGerada,(iter,i_no.codigo),0) - barra.carga[est] + get(barra.deficitBarra,(iter, i_no.codigo), 0)
        #println("Codigo Barra: ", barra.codigo, " Potencia Liquida: ", barra.potenciaLiquida[iter,est,i_no.codigo])
    end

    # TRAFO DEFASADOR
    for linha in ilha.linhasAtivas[est]
        if linha.defasador != 0
            valor_pi = 3.141593
            anguloDefasadorRad = linha.defasador*valor_pi/180
            fatorDefasador = anguloDefasadorRad/linha.X

            potenciaLiquidaDe = linha.de.potenciaLiquida[iter,i_no.codigo]
            potenciaLiquidaPara = linha.para.potenciaLiquida[iter,i_no.codigo]

            linha.de.potenciaLiquida[iter,i_no.codigo] = potenciaLiquidaDe - fatorDefasador
            linha.para.potenciaLiquida[iter,i_no.codigo] = potenciaLiquidaPara + fatorDefasador
        end
    end
    #FIM TRAFO DEFASADOR
    vetorPotenciaLiquida = []
    for barra in ilha.barras
        if barra.codigo != ilha.slack.codigo
            #println("Codigo Barra: ", barra.codigo, " Potencia Liquida: ", barra.potenciaLiquida[est])
            push!(vetorPotenciaLiquida, barra.potenciaLiquida[iter,i_no.codigo])
        end
    end

    return vetorPotenciaLiquida
end



function calculaFluxosIlhaMetodoDeltaDC(ilha,est)
    vetorPotenciaLiquida = calculaVetorPotenciaLiquidaDaIlha(ilha,est)

    ## CALCULO DO FLUXO
    delta_sparse = ilha.matrizSusceptancia[est] \ vetorPotenciaLiquida
    #println(delta_sparse)

    anguloCadaBarra = OrderedDict()
    contador = 1
    for barra in ilha.barrasAtivas[est]
        anguloCadaBarra[ilha.slack.codigo] = 0
        if barra.codigo != ilha.slack.codigo
            anguloCadaBarra[barra.codigo] = delta_sparse[contador]
            contador = contador + 1
        end
    end

    for barra in ilha.barrasAtivas[est]
        println("Barra: ", barra.codigo, " Angulo: ", anguloCadaBarra[barra.codigo])
    end

    for linha in ilha.linhasAtivas[est]
        anguloBarraDe = anguloCadaBarra[linha.de.codigo]
        anguloBarraPara = anguloCadaBarra[linha.para.codigo]
        valor_fluxo = (anguloBarraDe - anguloBarraPara)/linha.X

        if(linha.defasador != 0)
            valor_pi = 3.141593
            anguloDefasadorRad = linha.X*valor_pi/180
            fatorDefasador = anguloDefasadorRad/linha.X
            valor_fluxo = (anguloBarraDe - anguloBarraPara + anguloDefasadorRad)/linha.X
        end
        linha.anguloBarraDe = anguloBarraDe
        linha.anguloBarraPara = anguloBarraPara
        linha.fluxoDePara = valor_fluxo
    end
end

function calculaFluxosIlhaMetodoSensibilidadeDC(ilha, it, est, i_no)
    vetorPotenciaLiquida = calculaVetorPotenciaLiquidaDaIlha(ilha,it , est, i_no)
    for linha in ilha.linhasAtivas[est]
        linha.fluxoDePara[it, i_no.codigo] = transpose(linha.linhaMatrizSensibilidade[est])*vetorPotenciaLiquida
    end
end