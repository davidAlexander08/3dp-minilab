function retornaCustoPresente(otm_config, no,etapa)
    custo_presente = 0
    for term in lista_utes
        geracao = JuMP.value(otm_config.gt_vars[(no.codigo, term.nome, etapa)])
        custo_presente += geracao*term.custo_geracao
    end
    for hydro in lista_uhes 
        vertimento = JuMP.value(otm_config.vert_vars[(no.codigo, hydro.nome, etapa)])
        custo_presente += vertimento*0.01
        if(vazao_minima == 1)
            penalidadePositivaVazmin = JuMP.value(otm_config.folga_positiva_vazmin_vars[(no.codigo, hydro.nome, etapa)])
            custo_presente += penalidadePositivaVazmin*penalidVazMin
        end
        if(restricaoVolumeFimMundo == 1)
            penalidadePositivavolFimMundo = JuMP.value(otm_config.folga_positiva_volFimMundo_vars[(no.codigo, hydro.nome, etapa)])
            custo_presente += penalidadePositivavolFimMundo*penalidVazMin
        end


    end

    for sbm in lista_submercados
        custo_presente += JuMP.value(otm_config.deficit_vars[(no.codigo, sbm.nome, etapa)])*sbm.deficit_cost
    end


    return custo_presente
end