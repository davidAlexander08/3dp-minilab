
function imprimePolitica(saida_otimizacao, otm_config, etapa, it, no)
    #println("ETAPA: ", etapa, " est: ", est, " it: ", it, " miniIter: ", miniIter, " no: ", no.codigo)
    #converte_m3s_hm3 = (conversao_m3_hm3*dat_horas[(dat_horas.PERIODO .== no.periodo), "HORAS"][1])
    probabilidadeNo = (dat_prob[(dat_prob.NO .== no.codigo), "PROBABILIDADE"][1])
    GeracaoHidreletricaSIN = 0
    GeracaoTermicaSIN = 0
    GeracaoEolicaSIN = 0
    DemandaTotalSIN = 0
    DeficitSIN = 0
    excesso_SIN = 0
    CustoPresenteSIN = 0
    VolumeArmazenadoSIN = 0
    AfluenciaSIN = 0
    VolumeArmazenadoInicialSIN = 0
    VertimentoSIN = 0
    TurbinamentoSIN = 0
    EnergiaArmazenadaSIN = 0
    for sbm in lista_submercados
        GeracaoHidreletricaTotal = 0
        GeracaoEolicaTotal = 0
        VolumeArmazenadoTotal = 0
        AfluenciaTotal = 0
        VolumeArmazenadoInicialTotal = 0
        GeracaoTermicaTotal = 0
        VertimentoTotal = 0
        TurbinamentoTotal = 0
        EnergiaArmazenadaTotal = 0

        for eol in cadastroUsinasEolicasSubmercado[sbm.codigo]
            geracaoEol = JuMP.value(otm_config.ge_vars[(no.codigo, eol.nome, etapa)])
            folgaPositivaEol = JuMP.value(otm_config.folga_positiva_eolica_vars[(no.codigo, eol.nome, etapa)])
            folgaNegativaEol = JuMP.value(otm_config.folga_negativa_eolica_vars[(no.codigo, eol.nome, etapa)])
            push!(saida_otimizacao.df_eolicas, (etapa = etapa, iter = it, est = no.periodo, node = no.codigo, prob = probabilidadeNo, Submercado = sbm.codigo, nome = eol.nome, usina = eol.codigo, generation = round(geracaoEol, digits = 2), folgaPositiva = round(folgaPositivaEol, digits = 2), folgaNegativa = round(folgaNegativaEol, digits = 2)))
            GeracaoEolicaSIN += geracaoEol
            GeracaoEolicaTotal += geracaoEol
            # println("geracaoEol: ", geracaoEol, "folgaPositivaEol: ", folgaPositivaEol, "folgaNegativaEol: ", folgaNegativaEol)
        end


        for term in cadastroUsinasTermicasSubmercado[sbm.codigo]
            geracao = JuMP.value(otm_config.gt_vars[(no.codigo, term.nome, etapa)])
            push!(saida_otimizacao.df_termicas, (etapa = etapa, iter = it, est = no.periodo, node = no.codigo, prob = probabilidadeNo, Submercado = sbm.codigo, nome = term.nome, usina = term.codigo, generation = round(geracao, digits = 2) , custo = term.custo_geracao, custoTotal = round(geracao, digits = 1)*term.custo_geracao , GerMin = term.gmin, GerMax = term.gmax))
            GeracaoTermicaTotal += geracao
            GeracaoTermicaSIN += geracao
            
        end
        for uhe in cadastroUsinasHidreletricasSubmercado[sbm.codigo]
            geracao = JuMP.value(otm_config.gh_vars[(no.codigo, uhe.nome, etapa)])
            turbinamento = JuMP.value(otm_config.turb_vars[(no.codigo, uhe.nome, etapa)]) 
            vertimento = JuMP.value(otm_config.vert_vars[(no.codigo, uhe.nome, etapa)]) 
            volumeFinal = JuMP.value(otm_config.vf_vars[(no.codigo, uhe.nome, etapa)]) 
            volumeInicial = Vi[(no.codigo, uhe.codigo, etapa)]
            earm_usi = volumeFinal*mapaUsinaProdtAcum[uhe.nome]/converte_m3s_hm3
            Afluencia = 0
            if( uhe.posto == 999)
                Afluencia = 0
            else
                Afluencia = (dat_vaz[(dat_vaz.NOME_UHE .== uhe.posto) .& (dat_vaz.NO .== no.codigo), "VAZAO"][1])
            end
            #Afluencia = (dat_vaz[(dat_vaz.NOME_UHE .== uhe.posto) .& (dat_vaz.NO .== no.codigo), "VAZAO"][1])
            if(vazao_minima == 1)

                matching_rows = dat_vazmin[dat_vazmin.USI .== uhe.nome, :vazmin]
                vazao_minima_uhe = isempty(matching_rows) ? NaN : first(matching_rows)
                if !isnan(vazao_minima_uhe)
                    folga_positiva_vazmin = JuMP.value(otm_config.folga_positiva_vazmin_vars[(no.codigo, uhe.nome, etapa)])
                    folga_negativa_vazmin = JuMP.value(otm_config.folga_negativa_vazmin_vars[(no.codigo, uhe.nome, etapa)])
                else
                    vazao_minima_uhe = 0
                    folga_positiva_vazmin = 0
                    folga_negativa_vazmin = 0
                end
            end

            if(restricaoVolumeFimMundo == 1 && no.periodo == caso.n_est)
                dat_meta_armazenamento.USI = string.(dat_meta_armazenamento.USI)
                matching_rows = dat_meta_armazenamento[dat_meta_armazenamento.USI .== uhe.nome, :meta]
                vol_meta = isempty(matching_rows) ? NaN : first(matching_rows)
                vol_meta = vol_meta/100
                if !isnan(vol_meta)
                    folga_positiva_volFimMundo = JuMP.value(otm_config.folga_positiva_volFimMundo_vars[(no.codigo, uhe.nome, etapa)])
                    folga_negativa_volFimMundo = JuMP.value(otm_config.folga_negativa_volFimMundo_vars[(no.codigo, uhe.nome, etapa)])
                else
                    vol_meta = 0
                    folga_positiva_volFimMundo = 0
                    folga_negativa_volFimMundo = 0
                end

            end

            push!(saida_otimizacao.df_hidreletricas, (etapa = etapa, iter = it, est = no.periodo, node = no.codigo, prob = probabilidadeNo, Submercado = sbm.codigo, nome = uhe.nome, usina = uhe.codigo, generation = round(geracao, digits = 2),
                            VI = Vi[(no.codigo,uhe.codigo, etapa)], 
                            AFL = round(Afluencia, digits = 2),
                            TURB = round(turbinamento, digits = 2), 
                            VERT = round(vertimento, digits = 2), 
                            VF = round(volumeFinal, digits = 2)))
            if(vazao_minima == 1)
                defluencia = turbinamento + vertimento
                push!(saida_otimizacao.df_folga_vazmin, (etapa = etapa, iter = it, est = no.periodo, node = no.codigo, prob = probabilidadeNo, 
                nome = uhe.nome, usina = uhe.codigo, Vazmin = vazao_minima_uhe, Qdef = round(defluencia, digits = 2), 
                FolgaPosit = round(folga_positiva_vazmin, digits = 2), FolgaNeg = round(folga_negativa_vazmin, digits = 2) ))
            end

            if(restricaoVolumeFimMundo == 1 && no.periodo == caso.n_est)
                dat_meta_armazenamento.USI = string.(dat_meta_armazenamento.USI)
                matching_rows = dat_meta_armazenamento[dat_meta_armazenamento.USI .== uhe.nome, :meta]
                vol_meta = isempty(matching_rows) ? NaN : first(matching_rows)
                vol_meta = vol_meta/100
                if !isnan(vol_meta)
                    folga_positiva_volFimMundo = JuMP.value(otm_config.folga_positiva_volFimMundo_vars[(no.codigo, uhe.nome, etapa)])
                    folga_negativa_volFimMundo = JuMP.value(otm_config.folga_negativa_volFimMundo_vars[(no.codigo, uhe.nome, etapa)])
                else
                    vol_meta = 0
                    folga_positiva_volFimMundo = 0
                    folga_negativa_volFimMundo = 0
                end
                push!(saida_otimizacao.df_folga_MetaVol, (etapa = etapa, iter = it, est = no.periodo, node = no.codigo, prob = probabilidadeNo, 
                nome = uhe.nome, usina = uhe.codigo, Meta = vol_meta, VolF = round(volumeFinal, digits = 2), 
                FolgaPosit = round(folga_positiva_volFimMundo, digits = 2), FolgaNeg = round(folga_negativa_volFimMundo, digits = 2) ))
            end

            GeracaoHidreletricaTotal += geracao
            GeracaoHidreletricaSIN += geracao
            VolumeArmazenadoTotal += volumeFinal
            VolumeArmazenadoSIN += volumeFinal
            AfluenciaTotal += Afluencia
            AfluenciaSIN += Afluencia
            VolumeArmazenadoInicialTotal += volumeInicial
            VolumeArmazenadoInicialSIN += volumeInicial
            VertimentoTotal += vertimento
            VertimentoSIN += vertimento
            TurbinamentoTotal += turbinamento
            TurbinamentoSIN += turbinamento
            EnergiaArmazenadaTotal += earm_usi
            EnergiaArmazenadaSIN += earm_usi
        end
        custo_presente = 0
        for term in cadastroUsinasTermicasSubmercado[sbm.codigo]
            custo_presente += JuMP.value.(otm_config.gt_vars[(no.codigo, term.nome, etapa)])*term.custo_geracao
        end
        def = 0
        excesso_sbm = 0
        def = JuMP.value(otm_config.deficit_vars[(no.codigo, sbm.nome, etapa)])
        excesso_sbm = JuMP.value(otm_config.excesso_vars[(no.codigo, sbm.nome, etapa)])
        custo_presente += def*sbm.deficit_cost
        DemandaTotalSIN += sbm.demanda[no.periodo]
        DeficitSIN += def
        excesso_SIN += excesso_sbm
        CustoPresenteSIN += custo_presente
        valor_CMO = -JuMP.shadow_price( otm_config.constraint_balancDem_dict[(no.codigo, sbm.nome, etapa)])
        push!(saida_otimizacao.df_balanco_energetico_SBM,  (etapa = etapa, iter = it, est = no.periodo, node = no.codigo, prob = probabilidadeNo, Submercado = sbm.codigo, Demanda = sbm.demanda[no.periodo], GT = GeracaoTermicaTotal, GH = GeracaoHidreletricaTotal, EOL = GeracaoEolicaTotal, AFL = AfluenciaTotal, Vini = VolumeArmazenadoInicialTotal, VolArm = VolumeArmazenadoTotal, Earm = EnergiaArmazenadaTotal, Turb = TurbinamentoTotal, Vert = VertimentoTotal, Deficit = def, Excesso = excesso_sbm, CustoPresente = custo_presente, CMO = round(valor_CMO, digits = 2)))
        for sbm_2 in lista_submercados
            if sbm.codigo != sbm_2.codigo
                interc = JuMP.value(otm_config.intercambio_vars[(no.codigo, sbm.nome, sbm_2.nome, etapa)])
                push!(saida_otimizacao.df_intercambio,  (etapa = etapa, iter = it, est = no.periodo, node = no.codigo, prob = probabilidadeNo, SubmercadoDE = sbm.codigo, SubmercadoPARA = sbm_2.codigo, Valor = round(interc, digits = 2)))
            end
        end
    end
    push!(saida_otimizacao.df_balanco_energetico_SIN,  (etapa = etapa, iter = it, est = no.periodo, node = no.codigo, prob = probabilidadeNo, Demanda = DemandaTotalSIN, GT = GeracaoTermicaSIN, GH = GeracaoHidreletricaSIN, EOL = GeracaoEolicaSIN, Deficit = DeficitSIN, Excesso = excesso_SIN, AFL = AfluenciaSIN, Vini = VolumeArmazenadoInicialSIN, VolArm = VolumeArmazenadoSIN, Earm = EnergiaArmazenadaSIN, Turb = TurbinamentoSIN, Vert = VertimentoSIN, CustoPresente = CustoPresenteSIN, CustoFuturo = JuMP.value(otm_config.alpha_vars[no.codigo, etapa])))
end