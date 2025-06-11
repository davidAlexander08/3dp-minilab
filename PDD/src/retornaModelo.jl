function retornaModelo(m, otm_config, no, etapa)
    horas_periodo = dat_horas[(dat_horas.PERIODO .== no.periodo), "HORAS"][1]
    converte_m3s_hm3 = horas_periodo*conversao_m3_to_hm3
    for term in lista_utes
        otm_config.gt_vars[(no.codigo, term.nome, etapa)] = @variable(m, base_name="gt_$(no.codigo)_$(term.codigo)_$(etapa)")
    end
    for uhe in lista_uhes
        otm_config.gh_vars[(no.codigo, uhe.nome, etapa)] = @variable(m, base_name="gh_$(no.codigo)_$(uhe.codigo)_$(etapa)")
        otm_config.turb_vars[(no.codigo, uhe.nome, etapa)] = @variable(m, base_name="turb_$(no.codigo)_$(uhe.codigo)_$(etapa)")
        otm_config.vert_vars[(no.codigo, uhe.nome, etapa)] = @variable(m, base_name="vert_$(no.codigo)_$(uhe.codigo)_$(etapa)")
        otm_config.vf_vars[(no.codigo, uhe.nome, etapa)] = @variable(m, base_name="vf_$(no.codigo)_$(uhe.codigo)_$(etapa)")
        otm_config.folga_positiva_vazmin_vars[(no.codigo, uhe.nome, etapa)] = @variable(m, base_name="spdefmin_$(no.codigo)_$(uhe.codigo)_$(etapa)")
        otm_config.folga_negativa_vazmin_vars[(no.codigo, uhe.nome, etapa)] = @variable(m, base_name="sndefmin_$(no.codigo)_$(uhe.codigo)_$(etapa)")

        otm_config.folga_positiva_volFimMundo_vars[(no.codigo, uhe.nome, etapa)] = @variable(m, base_name="sPVfmundo_$(no.codigo)_$(uhe.codigo)_$(etapa)")
        otm_config.folga_negativa_volFimMundo_vars[(no.codigo, uhe.nome, etapa)] = @variable(m, base_name="sPVfmundo_$(no.codigo)_$(uhe.codigo)_$(etapa)")
    end
    for eol in lista_eols
        otm_config.ge_vars[(no.codigo, eol.nome, etapa)] = @variable(m, base_name="gh_$(no.codigo)_$(eol.codigo)_$(etapa)")
        otm_config.folga_positiva_eolica_vars[(no.codigo, eol.nome, etapa)] = @variable(m, base_name="spdefmin_$(no.codigo)_$(eol.codigo)_$(etapa)")
        otm_config.folga_negativa_eolica_vars[(no.codigo, eol.nome, etapa)] = @variable(m, base_name="sndefmin_$(no.codigo)_$(eol.codigo)_$(etapa)")

    end
    for sbm in lista_submercados
        otm_config.deficit_vars[(no.codigo, sbm.nome, etapa)] = @variable(m, base_name="def_$(no.codigo)_$(sbm.codigo)_$(etapa)")
        otm_config.excesso_vars[(no.codigo, sbm.nome, etapa)] = @variable(m, base_name="exc_$(no.codigo)_$(sbm.codigo)_$(etapa)")
        for sbm_2 in lista_submercados
            if sbm.codigo != sbm_2.codigo
                otm_config.intercambio_vars[(no.codigo, sbm.nome, sbm_2.nome, etapa)] = @variable(m, base_name="interc_$(no.codigo)_$(sbm.codigo)_$(sbm_2.codigo)_$(etapa)")
                @constraint(m, otm_config.intercambio_vars[(no.codigo, sbm.nome, sbm_2.nome, etapa)] >= 0 )
            end
        end
    end


    ############### RESTRICOES

    ## DEFINE LIMITES DE INTERCAMBIO
    if(limites_intercambio == 1)
        for sbm in lista_submercados
            for sbm_2 in lista_submercados
                if(sbm.codigo != sbm_2.codigo)
                    #print("codigo_de: ", sbm.codigo, " codigo_para: ", sbm_2.codigo)
                    limite_intercambio = (dat_interc[(dat_interc.SUMERCADO1 .== sbm.codigo) .& (dat_interc.SUBMERCADO2 .== sbm_2.codigo), "VALOR"][1])
                    @constraint(m, otm_config.intercambio_vars[(no.codigo, sbm.nome, sbm_2.nome, etapa)] <= limite_intercambio)
                end
            end
        end
    end

    otm_config.alpha_vars[(no.codigo,etapa)] = @variable(m, base_name="alpha_$(no.codigo)_$(etapa)")
    @constraint(m, otm_config.alpha_vars[(no.codigo, etapa)] >= 0 )

    for eol in lista_eols
        cenario_eolica = 0
        if(eol.posto != 999)
            cenario_eolica = (dat_vaz[(dat_vaz.NOME_UHE .== eol.posto) .& (dat_vaz.NO .== no.codigo), "VAZAO"][1])
        else
            cenario_eolica = 0
        end
        @constraint(  m, otm_config.ge_vars[(no.codigo, eol.nome, etapa)] >= 0 ) 
        @constraint(  m, otm_config.folga_positiva_eolica_vars[(no.codigo, eol.nome, etapa)] >= 0 ) 
        @constraint(  m, otm_config.folga_negativa_eolica_vars[(no.codigo, eol.nome, etapa)] >= 0 ) 
        @constraint(m, otm_config.ge_vars[(no.codigo, eol.nome, etapa)] 
        +otm_config.folga_positiva_eolica_vars[(no.codigo, eol.nome, etapa)]  == cenario_eolica) #linha, coluna      /converte_m3s_hm3
        #@constraint(m, ge_vars[(no.codigo, eol.nome, etapa)] <= cenario_eolica) #linha, coluna      /converte_m3s_hm3
    end


    for uhe in lista_uhes
        @constraint(  m, otm_config.gh_vars[(no.codigo, uhe.nome, etapa)] >= 0 ) 
        @constraint(  m, otm_config.turb_vars[(no.codigo, uhe.nome, etapa)] >= 0 ) 
        @constraint(  m, otm_config.vert_vars[(no.codigo, uhe.nome, etapa)] >= 0 ) 
        @constraint(  m, otm_config.vf_vars[(no.codigo, uhe.nome, etapa)] >= 0 ) 
        @constraint(  m, otm_config.folga_positiva_vazmin_vars[(no.codigo, uhe.nome, etapa)] >= 0 ) 
        @constraint(  m, otm_config.folga_negativa_vazmin_vars[(no.codigo, uhe.nome, etapa)] >= 0 ) 
        
        @constraint(  m, otm_config.folga_positiva_volFimMundo_vars[(no.codigo, uhe.nome, etapa)] >= 0 ) 
        @constraint(  m, otm_config.folga_negativa_volFimMundo_vars[(no.codigo, uhe.nome, etapa)] >= 0 ) 

        @constraint(m, otm_config.gh_vars[(no.codigo, uhe.nome, etapa)] - uhe.prodt*otm_config.turb_vars[(no.codigo, uhe.nome, etapa)] == 0) #linha, coluna      /converte_m3s_hm3
        @constraint(m, otm_config.turb_vars[(no.codigo, uhe.nome, etapa)] <= uhe.turbmax) #linha, coluna
        @constraint(m, otm_config.gh_vars[(no.codigo, uhe.nome, etapa)] <= uhe.gmax ) 
        @constraint(m, otm_config.vf_vars[(no.codigo, uhe.nome, etapa)] <=  uhe.vmax) #linha, coluna
        @constraint(m, otm_config.vf_vars[(no.codigo, uhe.nome, etapa)] >=  uhe.vmin) #linha, coluna

        #print("est: ", est, " no: ", no.codigo, " etapa: ", etapa)
        vazao_afluente = 0
        if(uhe.posto != 999)
            #println("nome: ", uhe.nome, " node: ", no.codigo, " posto: ", uhe.posto)
            vazao_afluente = (dat_vaz[(dat_vaz.NOME_UHE .== uhe.posto) .& (dat_vaz.NO .== no.codigo), "VAZAO"][1])
        else
            vazao_afluente = 0
        end
        
        #############BALANCO HIDRICO


        #constraint_dict[(no.codigo, uhe.nome, etapa)] = @constraint(m, 
        #vf_vars[(no.codigo, uhe.nome, etapa)]
        #+ turb_vars[(no.codigo, uhe.nome, etapa)]
        #+ vert_vars[(no.codigo, uhe.nome, etapa)] == Vi[no.codigo,uhe.codigo, etapa] + (vazao_afluente)
        #+ sum(turb_vars[(no.codigo, nomeUsiMont, etapa)] for nomeUsiMont in mapa_montantesUsina[uhe.nome])
        #+ sum(vert_vars[(no.codigo, nomeUsiMont, etapa)] for nomeUsiMont in mapa_montantesUsina[uhe.nome])) #linha, colun * converte_m3s_hm3
        #println(constraint_dict)
        otm_config.constraint_dict[(no.codigo, uhe.nome, etapa)] = @constraint(m, 
        otm_config.vf_vars[(no.codigo, uhe.nome, etapa)]
        + otm_config.turb_vars[(no.codigo, uhe.nome, etapa)]*converte_m3s_hm3
        + otm_config.vert_vars[(no.codigo, uhe.nome, etapa)]*converte_m3s_hm3
        == Vi[no.codigo,uhe.codigo, etapa] + (vazao_afluente)*converte_m3s_hm3
        + sum(otm_config.turb_vars[(no.codigo, nomeUsiMont, etapa)]*converte_m3s_hm3 for nomeUsiMont in mapa_montantesUsina[uhe.nome])
        + sum(otm_config.vert_vars[(no.codigo, nomeUsiMont, etapa)]*converte_m3s_hm3 for nomeUsiMont in mapa_montantesUsina[uhe.nome])) #linha, colun * converte_m3s_hm3
        #println(constraint_dict)

        
    end

    ## DEFINE RESTRICAO DE VAZAO minima, VOLUME MINIMO E VOLUME ESPERA
    for uhe in lista_uhes

        #DEFINE RESTRICOES DE VAZAO MINIMA
        #println(uhe.nome)
        if(vazao_minima == 1)
            dat_vazmin.USI = string.(dat_vazmin.USI)
            matching_rows = dat_vazmin[dat_vazmin.USI .== uhe.nome, :vazmin]
            vazao_minima_uhe = isempty(matching_rows) ? NaN : first(matching_rows)
            if !isnan(vazao_minima_uhe)
                @constraint(m, otm_config.turb_vars[(no.codigo, uhe.nome, etapa)] + otm_config.vert_vars[(no.codigo, uhe.nome, etapa)] 
                + otm_config.folga_positiva_vazmin_vars[(no.codigo, uhe.nome, etapa)]
                - otm_config.folga_negativa_vazmin_vars[(no.codigo, uhe.nome, etapa)]
                    == vazao_minima_uhe)
            else
                #println("No vazmin found for ", uhe.nome, " - Skipping constraint.")
            end
        end

        if restricaoVolumeFimMundo == 1 && est == caso.n_est
            #println(" est == caso.n_est ",  caso.n_est)
            dat_meta_armazenamento.USI = string.(dat_meta_armazenamento.USI)
            #print(dat_meta_armazenamento)
            matching_rows = dat_meta_armazenamento[dat_meta_armazenamento.USI .== uhe.nome, :meta]
            #print(matching_rows)
            vol_meta = isempty(matching_rows) ? NaN : first(matching_rows)
            vol_meta = vol_meta/100
            #println("volmeta: ", vol_meta, " uhe.vmax: ", uhe.vmax, " uhe.vmin: ", uhe.vmin)
            if !isnan(vol_meta)
                @constraint(m, otm_config.vf_vars[(no.codigo, uhe.nome, etapa)] 
                + otm_config.folga_positiva_volFimMundo_vars[(no.codigo, uhe.nome, etapa)]
                - otm_config.folga_negativa_volFimMundo_vars[(no.codigo, uhe.nome, etapa)]
                ==  (uhe.vmax - uhe.vmin)*vol_meta ) #linha, coluna
                #print(m)
            else
                #println("No vazmin found for ", uhe.nome, " - Skipping constraint.")
            end
        end

        #DEFINE RESTRICOES DE VOLUME MINIMO
        if(volume_minimo == 1)
            dat_volmin.USI = string.(dat_volmin.USI)
            matching_rows = dat_volmin[dat_volmin.USI .== uhe.nome, :vmin]
            vol_min_uhe = isempty(matching_rows) ? NaN : first(matching_rows)
            vol_min_uhe = vol_min_uhe/100
            #println("vol_min_uhe: ", vol_min_uhe)
            if !isnan(vol_min_uhe)
                @constraint(m, otm_config.vf_vars[(no.codigo, uhe.nome, etapa)] >= vol_min_uhe*(uhe.vmax - uhe.vmin) + uhe.vmin)
            else
                #println("No vazmin found for ", uhe.nome, " - Skipping constraint.")
            end
        end

        #DEFINE RESTRICOES DE   VOLUME ESPERA
        if(volume_espera == 1)
            dat_volmax.USI = string.(dat_volmax.USI)
            matching_rows = dat_volmax[dat_volmax.USI .== uhe.nome, :vmax]
            vol_max_uhe = isempty(matching_rows) ? NaN : first(matching_rows)
            vol_max_uhe = vol_max_uhe/100
            #println("vol_max_uhe: ", vol_max_uhe)
            if !isnan(vol_max_uhe) 
                @constraint(m, otm_config.vf_vars[(no.codigo, uhe.nome, etapa)] <= vol_max_uhe*uhe.vmax)
            else
                #println("No vazmin found for ", uhe.nome, " - Skipping constraint.")
            end
        end

    end

    #write_to_file(m, "saidas/PDD/model_output.txt", format = MOI.FileFormats.FORMAT_LP)
    #exit(1)
    for term in lista_utes
        @constraint(m, otm_config.gt_vars[(no.codigo, term.nome, etapa)] >= 0)
        @constraint(m, otm_config.gt_vars[(no.codigo, term.nome, etapa)] <= term.gmax) #linha, coluna
        @constraint(m, otm_config.gt_vars[(no.codigo, term.nome, etapa)] >= term.gmin) #linha, coluna
    end
    for sbm in lista_submercados
        @constraint(  m, otm_config.deficit_vars[(no.codigo, sbm.nome, etapa)] >= 0 ) 
        @constraint(  m, otm_config.excesso_vars[(no.codigo, sbm.nome, etapa)] >= 0 ) 
    end
    
    @objective(m, Min, sum(term.custo_geracao * otm_config.gt_vars[(no.codigo, term.nome, etapa)] for term in lista_utes) 
    + sum(0.01 * otm_config.vert_vars[(no.codigo, uhe.nome, etapa)] for uhe in lista_uhes)
    + sum(penalidVazMin * otm_config.folga_positiva_vazmin_vars[(no.codigo, uhe.nome, etapa)] for uhe in lista_uhes)
    + sum(penalidVazMin * otm_config.folga_positiva_volFimMundo_vars[(no.codigo, uhe.nome, etapa)] for uhe in lista_uhes)
    + sum(0.001 * otm_config.folga_positiva_eolica_vars[(no.codigo, eol.nome, etapa)] for eol in lista_eols)
    + sum(0.01 * otm_config.intercambio_vars[(no.codigo, sbm.nome, sbm_2.nome, etapa)] for sbm in lista_submercados, sbm_2 in lista_submercados if sbm != sbm_2)
    + sum(sbm.deficit_cost * otm_config.deficit_vars[(no.codigo, sbm.nome, etapa)] for sbm in lista_submercados)
    + otm_config.alpha_vars[(no.codigo, etapa)])
    
    for sbm in lista_submercados
        otm_config.constraint_balancDem_dict[(no.codigo, sbm.nome, etapa)] = @constraint(  m, sum(otm_config.gh_vars[(no.codigo, uhe.nome, etapa)] for uhe in cadastroUsinasHidreletricasSubmercado[sbm.codigo]) 
        + sum(otm_config.gt_vars[(no.codigo, term.nome, etapa)] for term in cadastroUsinasTermicasSubmercado[sbm.codigo]) 
        + sum(otm_config.ge_vars[(no.codigo, eol.nome, etapa)] for eol in cadastroUsinasEolicasSubmercado[sbm.codigo]) 
        + sum(otm_config.intercambio_vars[(no.codigo, sbm_2.nome, sbm.nome, etapa)] for sbm_2 in lista_submercados if sbm != sbm_2)
        - sum(otm_config.intercambio_vars[(no.codigo, sbm.nome, sbm_2.nome, etapa)] for sbm_2 in lista_submercados if sbm != sbm_2)
        + otm_config.deficit_vars[(no.codigo, sbm.nome, etapa)] 
        #- excesso_vars[(no.codigo, sbm.nome, etapa)] 
        == sbm.demanda[no.periodo]   )
    end
end