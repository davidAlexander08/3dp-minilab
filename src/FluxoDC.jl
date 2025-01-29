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
    
    print(ilha.barrasAtivas[est])
    for barra in ilha.barrasAtivas[est]
        barra.potenciaLiquida[iter,i_no.codigo] = get(barra.potenciaGerada,(iter,i_no.codigo),0) - barra.carga[est] + get(barra.deficitBarra,(iter, i_no.codigo), 0)
        println("Codigo Barra: ", barra.codigo, " GER: ", barra.potenciaGerada[(iter,i_no.codigo)], " DEM: ", barra.carga[est], " DEF: ", get(barra.deficitBarra,(iter, i_no.codigo), 0), " PLIQ: ", barra.potenciaLiquida[iter,i_no.codigo])
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



function calculaFluxosIlhaMetodoDeltaDC(ilha, it, est, i_no)
    vetorPotenciaLiquida = calculaVetorPotenciaLiquidaDaIlha(ilha,it,est, i_no)

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
        linha.fluxoDePara[it, i_no.codigo] = valor_fluxo
        println("DE: ", linha.de.codigo, " A: ", anguloBarraDe,  " PARA: ", linha.para.codigo, " A: ", anguloBarraPara," FLUXO: ", linha.fluxoDePara[it, i_no.codigo]) 
    end
end

function calculaFluxosIlhaMetodoSensibilidadeDC(ilha, it, est, i_no)
    vetorPotenciaLiquida = calculaVetorPotenciaLiquidaDaIlha(ilha,it , est, i_no)
    for linha in ilha.linhasAtivas[est]
        #println(linha.linhaMatrizSensibilidade[est])
        #println(vetorPotenciaLiquida)
        linha.fluxoDePara[it, i_no.codigo] = transpose(linha.linhaMatrizSensibilidade[est])*vetorPotenciaLiquida
        println("DE: ", linha.de.codigo,  " PARA: ", linha.para.codigo, " FLUXO: ", linha.fluxoDePara[it, i_no.codigo]) 
        #" G_DE: ", linha.de.potenciaGerada[(it,i_no.codigo)], " C_DE: ", linha.de.carga[est],
        #" G_PARA: ", linha.para.potenciaGerada[(it,i_no.codigo)], " C_DE: ", linha.para.carga[est],
        #" PLIQ_DE: ", linha.de.potenciaLiquida[(it,i_no.codigo)], " PLIQ_PARA: ", linha.para.potenciaLiquida[(it,i_no.codigo)],
        #)
    end
end
