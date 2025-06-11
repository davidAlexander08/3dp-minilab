function exportar_resultados(saida_otimizacao)

    df_balanco_energetico_SBM_fw = saida_otimizacao.df_balanco_energetico_SBM[(saida_otimizacao.df_balanco_energetico_SBM.etapa .== "FW"), :]
    df_balanco_energetico_SBM_bk = saida_otimizacao.df_balanco_energetico_SBM[(saida_otimizacao.df_balanco_energetico_SBM.etapa .== "BK"), :]
    max_iter = maximum(saida_otimizacao.df_balanco_energetico_SBM.iter)
    df_balanco_energetico_SBM_sf = saida_otimizacao.df_balanco_energetico_SBM[(saida_otimizacao.df_balanco_energetico_SBM.etapa .== "FW") .& (saida_otimizacao.df_balanco_energetico_SBM.iter .== max_iter), :]

    df_balanco_energetico_SIN_fw = saida_otimizacao.df_balanco_energetico_SIN[(saida_otimizacao.df_balanco_energetico_SIN.etapa .== "FW"), :]
    df_balanco_energetico_SIN_bk = saida_otimizacao.df_balanco_energetico_SIN[(saida_otimizacao.df_balanco_energetico_SIN.etapa .== "BK"), :]
    df_balanco_energetico_SIN_sf = saida_otimizacao.df_balanco_energetico_SIN[(saida_otimizacao.df_balanco_energetico_SIN.etapa .== "FW") .& (saida_otimizacao.df_balanco_energetico_SIN.iter .== max_iter), :]

    df_intercambio_SIN_fw = saida_otimizacao.df_intercambio[(saida_otimizacao.df_intercambio.etapa .== "FW"), :]
    df_intercambio_SIN_bk = saida_otimizacao.df_intercambio[(saida_otimizacao.df_intercambio.etapa .== "BK"), :]
    df_intercambio_SIN_sf = saida_otimizacao.df_intercambio[(saida_otimizacao.df_intercambio.etapa .== "FW") .& (saida_otimizacao.df_intercambio.iter .== max_iter), :]

    df_folga_vazmin_fw = saida_otimizacao.df_folga_vazmin[(saida_otimizacao.df_folga_vazmin.etapa .== "FW"), :]
    df_folga_vazmin_bk = saida_otimizacao.df_folga_vazmin[(saida_otimizacao.df_folga_vazmin.etapa .== "BK"), :]
    df_folga_vazmin_sf = saida_otimizacao.df_folga_vazmin[(saida_otimizacao.df_folga_vazmin.etapa .== "FW") .& (saida_otimizacao.df_folga_vazmin.iter .== max_iter), :]


    df_folga_MetaVol_fw = saida_otimizacao.df_folga_MetaVol[(saida_otimizacao.df_folga_MetaVol.etapa .== "FW"), :]
    df_folga_MetaVol_bk = saida_otimizacao.df_folga_MetaVol[(saida_otimizacao.df_folga_MetaVol.etapa .== "BK"), :]
    df_folga_MetaVol_sf = saida_otimizacao.df_folga_MetaVol[(saida_otimizacao.df_folga_MetaVol.etapa .== "FW") .& (saida_otimizacao.df_folga_MetaVol.iter .== max_iter), :]


    df_termicas_fw = saida_otimizacao.df_termicas[(saida_otimizacao.df_termicas.etapa .== "FW"), :]
    df_termicas_bk = saida_otimizacao.df_termicas[(saida_otimizacao.df_termicas.etapa .== "BK"), :]
    df_termicas_sf = saida_otimizacao.df_termicas[(saida_otimizacao.df_termicas.etapa .== "FW") .&& (saida_otimizacao.df_termicas.iter .== max_iter), :]


    
    df_eolica_fw = saida_otimizacao.df_eolicas[(saida_otimizacao.df_eolicas.etapa .== "FW"), :]
    df_eolica_bk = saida_otimizacao.df_eolicas[(saida_otimizacao.df_eolicas.etapa .== "BK"), :]
    df_eolica_sf = saida_otimizacao.df_eolicas[(saida_otimizacao.df_eolicas.etapa .== "FW") .&& (saida_otimizacao.df_eolicas.iter .== max_iter), :]

    df_hidreletricas_fw = saida_otimizacao.df_hidreletricas[(saida_otimizacao.df_hidreletricas.etapa .== "FW"), :]
    df_hidreletricas_bk = saida_otimizacao.df_hidreletricas[(saida_otimizacao.df_hidreletricas.etapa .== "BK"), :]
    df_hidreletricas_sf = saida_otimizacao.df_hidreletricas[(saida_otimizacao.df_hidreletricas.etapa .== "FW") .&& (saida_otimizacao.df_hidreletricas.iter .== max_iter), :]

    df_parcelasCustoPresente_fw = saida_otimizacao.df_parcelasCustoPresente[(saida_otimizacao.df_parcelasCustoPresente.etapa .== "FW"), :]
    df_parcelasCustoPresente_bk = saida_otimizacao.df_parcelasCustoPresente[(saida_otimizacao.df_parcelasCustoPresente.etapa .== "BK"), :]
    df_parcelasCustoPresente_sf = saida_otimizacao.df_parcelasCustoPresente[(saida_otimizacao.df_parcelasCustoPresente.etapa .== "FW") .&& (saida_otimizacao.df_parcelasCustoPresente.iter .== max_iter), :]





    output_dir_oper = dados_saida*"/saidas/PDD/oper"
    mkpath(output_dir_oper)
    CSV.write(output_dir_oper*"/balanco_energetico_SBM_fw.csv", df_balanco_energetico_SBM_fw)
    CSV.write(output_dir_oper*"/balanco_energetico_SBM_bk.csv", df_balanco_energetico_SBM_bk)
    CSV.write(output_dir_oper*"/balanco_energetico_SBM_sf.csv", df_balanco_energetico_SBM_sf)
    CSV.write(output_dir_oper*"/balanco_energetico_SIN_fw.csv", df_balanco_energetico_SIN_fw)
    CSV.write(output_dir_oper*"/balanco_energetico_SIN_bk.csv", df_balanco_energetico_SIN_bk)
    CSV.write(output_dir_oper*"/balanco_energetico_SIN_sf.csv", df_balanco_energetico_SIN_sf)
    CSV.write(output_dir_oper*"/intercambio_SIN_fw.csv", df_intercambio_SIN_fw)
    CSV.write(output_dir_oper*"/intercambio_SIN_bk.csv", df_intercambio_SIN_bk)
    CSV.write(output_dir_oper*"/intercambio_SIN_sf.csv", df_intercambio_SIN_sf)
    #CSV.write(output_dir_oper*"/termicas_fw.csv", df_termicas_fw)
    #CSV.write(output_dir_oper*"/termicas_bk.csv", df_termicas_bk)
    CSV.write(output_dir_oper*"/termicas_sf.csv", df_termicas_sf)
    #CSV.write(output_dir_oper*"/eolicas_fw.csv", df_eolicas_fw)
    #CSV.write(output_dir_oper*"/eolicas_bk.csv", df_eolicas_bk)
    CSV.write(output_dir_oper*"/eolicas_sf.csv", df_eolica_sf)
    #CSV.write(output_dir_oper*"/hidreletricas_fw.csv", df_hidreletricas_fw)
    #CSV.write(output_dir_oper*"/hidreletricas_bk.csv", df_hidreletricas_bk)
    CSV.write(output_dir_oper*"/hidreletricas_sf.csv", df_hidreletricas_sf)
    CSV.write(output_dir_oper*"/parcelaCustoPresente_sf.csv", df_parcelasCustoPresente_sf)
    #CSV.write(output_dir_oper*"/folgaVazmin_fw.csv", df_folga_vazmin_fw)
    #CSV.write(output_dir_oper*"/folgaVazmin_bk.csv", df_folga_vazmin_bk)
    CSV.write(output_dir_oper*"/folgaVazmin_sf.csv", df_folga_vazmin_sf)
    CSV.write(output_dir_oper*"/df_folga_MetaVol_sf.csv", df_folga_MetaVol_sf)
    CSV.write(output_dir_oper*"/convergencia.csv", saida_otimizacao.df_convergencia)
    CSV.write(output_dir_oper*"/df_cortes.csv", saida_otimizacao.df_cortes)
    CSV.write(output_dir_oper*"/df_cortes_equivalentes.csv", saida_otimizacao.df_cortes_equivalentes)


    df_per_balanco_energetico = DataFrame(etapa = String[], iter = Int[],  est = Int[], Demanda = Float64[], GT = Float64[], GH = Float64[], EOL = Float64[], Deficit = Float64[], Excesso =Float64[], AFL = Float64[], Vini = Float64[], VolArm = Float64[], Earm = Float64[], Turb = Float64[], Vert = Float64[], CustoPresente = Float64[], CustoFuturo = Float64[])
    for est_value in unique(saida_otimizacao.df_balanco_energetico_SIN.est)
        subset = df_balanco_energetico_SIN_sf[df_balanco_energetico_SIN_sf.est .== est_value, :]
        for iteracao in unique(subset.iter)
            subsubset = subset[(subset.iter .== iteracao), :]
            ProbGT = 0
            ProbVarm = 0
            ProbAFL = 0
            ProbVini = 0
            ProbGH = 0
            ProbEOL = 0
            ProbVert = 0
            ProbTurb = 0
            ProbEarm = 0
            ProbDeficit = 0
            ProbCustoPresente = 0
            ProbCustoFuturo = 0
            ProbExcesso = 0
            Demanda = 0
            for no in unique(subsubset.node)
                ProbGT += (subsubset[(subsubset.node .== no), "GT"][1])*(mapaProbCondicionalNo[no])
                ProbGH += (subsubset[(subsubset.node .== no), "GH"][1])*(mapaProbCondicionalNo[no])
                ProbEOL += (subsubset[(subsubset.node .== no), "EOL"][1])*(mapaProbCondicionalNo[no])
                ProbAFL += (subsubset[(subsubset.node .== no), "AFL"][1])*(mapaProbCondicionalNo[no])
                ProbVarm += (subsubset[(subsubset.node .== no), "VolArm"][1])*(mapaProbCondicionalNo[no])
                ProbVert += (subsubset[(subsubset.node .== no), "Vert"][1])*(mapaProbCondicionalNo[no])
                ProbTurb += (subsubset[(subsubset.node .== no), "Turb"][1])*(mapaProbCondicionalNo[no])
                ProbEarm += (subsubset[(subsubset.node .== no), "Earm"][1])*(mapaProbCondicionalNo[no])
                ProbVini += (subsubset[(subsubset.node .== no), "Vini"][1])*(mapaProbCondicionalNo[no])
                ProbDeficit += (subsubset[(subsubset.node .== no), "Deficit"][1])*(mapaProbCondicionalNo[no])
                ProbExcesso += (subsubset[(subsubset.node .== no), "Excesso"][1])*(mapaProbCondicionalNo[no])
                ProbCustoPresente += (subsubset[(subsubset.node .== no), "CustoPresente"][1])*(mapaProbCondicionalNo[no])
                ProbCustoFuturo += (subsubset[(subsubset.node .== no), "CustoFuturo"][1])*(mapaProbCondicionalNo[no])
                Demanda += (subsubset[(subsubset.node .== no), "Demanda"][1])*(mapaProbCondicionalNo[no])
                #println("ProbGT: ", ProbGT, " No: ", no, " GT: ", (subsubset[(subsubset.node .== no), "GT"][1]), " prob: ", (mapaProbCondicionalNo[no]))
            end
            
            dem = (subset[(subset.est .== est_value), "Demanda"][1])
            push!(df_per_balanco_energetico, (etapa = "SF", iter = iteracao, est = est_value, Demanda = dem, GT = round(ProbGT, digits = 0), GH = round(ProbGH, digits = 0), EOL = round(ProbEOL, digits = 0),Deficit = round(ProbDeficit, digits = 0), Excesso = round(ProbExcesso,digits = 0), AFL = round(ProbAFL, digits= 0), Vini = round(ProbVini, digits = 0), VolArm = round(ProbVarm, digits = 0), Earm = round(ProbEarm, digits= 0 ), Turb = round(ProbTurb, digits= 0 ), Vert = round(ProbVert, digits= 0 ), CustoPresente = round(ProbCustoPresente, digits = 0) , CustoFuturo = round(ProbCustoFuturo, digits = 0)))
        end
    end
    df_per_balanco_energetico = sort(df_per_balanco_energetico, :iter)
    CSV.write(output_dir_oper*"/balanco_energetico_final.csv", df_per_balanco_energetico)

    #println(df_per_balanco_energetico)
    show(IOContext(stdout, :compact => false), df_per_balanco_energetico)

    means = combine(df_per_balanco_energetico, names(df_per_balanco_energetico, Number) .=> mean)
    println(means)
    CSV.write(output_dir_oper*"/media_SIN.csv", means)
    

    df_per_balanco_energetico_SBM = DataFrame(etapa = String[], iter = Int[],  Submercado = Int[], est = Int[], Demanda = Float64[], GT = Float64[], GH = Float64[], EOL = Float64[], Deficit = Float64[], Excesso =Float64[], AFL = Float64[], Vini = Float64[], VolArm = Float64[], Earm = Float64[], Turb = Float64[], Vert = Float64[], CustoPresente = Float64[], CMO = Float64[])
    sbms = unique(df_balanco_energetico_SBM_sf.Submercado)
    for sbm in sbms
        subsubset_1 = df_balanco_energetico_SBM_sf[(df_balanco_energetico_SBM_sf.Submercado .== sbm), :]
        for est_value in unique(subsubset_1.est)
            subset = subsubset_1[subsubset_1.est .== est_value, :]
            for iteracao in unique(subset.iter)
                subsubset = subset[(subset.iter .== iteracao), :]
                ProbGT = 0
                ProbVarm = 0
                ProbAFL = 0
                ProbVini = 0
                ProbGH = 0
                ProbEOL = 0
                ProbVert = 0
                ProbTurb = 0
                ProbEarm = 0
                ProbDeficit = 0
                ProbCustoPresente = 0
                ProbCMO = 0
                ProbExcesso = 0
                Demanda = 0
                for no in unique(subsubset.node)
                    ProbGT += (subsubset[(subsubset.node .== no), "GT"][1])*(mapaProbCondicionalNo[no])
                    ProbGH += (subsubset[(subsubset.node .== no), "GH"][1])*(mapaProbCondicionalNo[no])
                    ProbEOL += (subsubset[(subsubset.node .== no), "EOL"][1])*(mapaProbCondicionalNo[no])
                    ProbAFL += (subsubset[(subsubset.node .== no), "AFL"][1])*(mapaProbCondicionalNo[no])
                    ProbVarm += (subsubset[(subsubset.node .== no), "VolArm"][1])*(mapaProbCondicionalNo[no])
                    ProbVert += (subsubset[(subsubset.node .== no), "Vert"][1])*(mapaProbCondicionalNo[no])
                    ProbTurb += (subsubset[(subsubset.node .== no), "Turb"][1])*(mapaProbCondicionalNo[no])
                    ProbEarm += (subsubset[(subsubset.node .== no), "Earm"][1])*(mapaProbCondicionalNo[no])
                    ProbVini += (subsubset[(subsubset.node .== no), "Vini"][1])*(mapaProbCondicionalNo[no])
                    ProbDeficit += (subsubset[(subsubset.node .== no), "Deficit"][1])*(mapaProbCondicionalNo[no])
                    ProbExcesso += (subsubset[(subsubset.node .== no), "Excesso"][1])*(mapaProbCondicionalNo[no])
                    ProbCustoPresente += (subsubset[(subsubset.node .== no), "CustoPresente"][1])*(mapaProbCondicionalNo[no])
                    ProbCMO += (subsubset[(subsubset.node .== no), "CMO"][1])*(mapaProbCondicionalNo[no])
                    Demanda += (subsubset[(subsubset.node .== no), "Demanda"][1])*(mapaProbCondicionalNo[no])
                    #println("ProbGT: ", ProbGT, " No: ", no, " GT: ", (subsubset[(subsubset.node .== no), "GT"][1]), " prob: ", (mapaProbCondicionalNo[no]))
                end
                dem = (subset[(subset.est .== est_value), "Demanda"][1])
                push!(df_per_balanco_energetico_SBM, (etapa = "SF", iter = iteracao, Submercado = sbm, est = est_value, Demanda = dem, GT = round(ProbGT, digits = 0), GH = round(ProbGH, digits = 0), EOL = round(ProbEOL, digits = 0),Deficit = round(ProbDeficit, digits = 0), Excesso = round(ProbExcesso,digits = 0), AFL = round(ProbAFL, digits= 0), Vini = round(ProbVini, digits = 0), VolArm = round(ProbVarm, digits = 0), Earm = round(ProbEarm, digits = 0), Turb = round(ProbTurb, digits = 0), Vert = round(ProbVert, digits= 0 ), CustoPresente = round(ProbCustoPresente, digits = 0) , CMO = round(ProbCMO, digits = 0)))
            end
        end
    end
    df_per_balanco_energetico_SBM = sort(df_per_balanco_energetico_SBM, :iter)
    CSV.write(output_dir_oper*"/balanco_energetico_final_sbm.csv", df_per_balanco_energetico_SBM)
    show(IOContext(stdout, :compact => false), df_per_balanco_energetico_SBM)

    means_sbm = combine(df_per_balanco_energetico_SBM, names(df_per_balanco_energetico_SBM, Number) .=> mean)
    println(means_sbm)
    CSV.write(output_dir_oper*"/media_SBM.csv", means_sbm)


    df_per_balanco_energetico_USIH = DataFrame(etapa = String[], iter = Int[],  usina = Int[], est = Int[], Submercado = Int[], nome = String[] , usinaJusante = String[], generation = Float64[], VI = Float64[], AFL = Float64[], TURB = Float64[], VERT = Float64[], QDEF = Float64[], VAZMIN = Float64[], VF = Float64[])
    for uhe in lista_uhes
        subsubset_1 = df_hidreletricas_sf[(df_hidreletricas_sf.usina .== uhe.codigo), :]
        for est_value in unique(subsubset_1.est)
            subset = subsubset_1[subsubset_1.est .== est_value, :]
            for iteracao in unique(subset.iter)
                subsubset = subset[(subset.iter .== iteracao), :]
                Probgeneration = 0
                ProbVI = 0
                ProbAFL = 0
                ProbTURB = 0
                ProbVERT = 0
                ProbVF = 0
                for no in unique(subsubset.node)
                    Probgeneration += (subsubset[(subsubset.node .== no), "generation"][1])*(mapaProbCondicionalNo[no])
                    ProbVI += (subsubset[(subsubset.node .== no), "VI"][1])*(mapaProbCondicionalNo[no])
                    ProbAFL += (subsubset[(subsubset.node .== no), "AFL"][1])*(mapaProbCondicionalNo[no])
                    ProbTURB += (subsubset[(subsubset.node .== no), "TURB"][1])*(mapaProbCondicionalNo[no])
                    ProbVERT += (subsubset[(subsubset.node .== no), "VERT"][1])*(mapaProbCondicionalNo[no])
                    ProbVF += (subsubset[(subsubset.node .== no), "VF"][1])*(mapaProbCondicionalNo[no])
                    #println("ProbGT: ", ProbGT, " No: ", no, " GT: ", (subsubset[(subsubset.node .== no), "GT"][1]), " prob: ", (mapaProbCondicionalNo[no]))
                end
                prob_defluencia = ProbVERT+ProbTURB
                vazao_minima_uhe = 0
                if(vazao_minima == 1)
                    matching_rows = dat_vazmin[dat_vazmin.USI .== uhe.nome, :vazmin]
                    vazao_minima_uhe = isempty(matching_rows) ? NaN : first(matching_rows)
                    if !isnan(vazao_minima_uhe)
                        vazao_minima_uhe = vazao_minima_uhe
                    else
                        vazao_minima_uhe = 0
                    end
                end
                submercado = (subset[(subset.est .== est_value), "Submercado"][1])
                push!(df_per_balanco_energetico_USIH, (etapa = "SF", iter = iteracao, usina = uhe.codigo, est = est_value, Submercado = submercado,nome = uhe.nome, usinaJusante = uhe.jusante, generation = round(Probgeneration, digits = 0), VI = round(ProbVI, digits = 0), AFL = round(ProbAFL, digits = 0), TURB = round(ProbTURB,digits = 0), VERT = round(ProbVERT, digits= 0), QDEF = round(prob_defluencia, digits= 0), VAZMIN = round(vazao_minima_uhe, digits= 0), VF = round(ProbVF, digits = 0)))
            end
        end
    end
    df_per_balanco_energetico_USIH = sort(df_per_balanco_energetico_USIH, :iter)
    CSV.write(output_dir_oper*"/balanco_energetico_final_UHE.csv", df_per_balanco_energetico_USIH)
    #show(IOContext(stdout, :compact => false), df_per_balanco_energetico_USIH)

    means_uhe = combine(df_per_balanco_energetico_USIH, names(df_per_balanco_energetico_USIH, Number) .=> mean)
    #println(means_uhe)
    CSV.write(output_dir_oper*"/media_UHE.csv", means_uhe)

    df_per_balanco_energetico_USIT = DataFrame(etapa = String[], iter = Int[],  usina = Int[], est = Int[], Submercado = Int[], nome = String[], generation = Float64[], custo = Float64[], custoTotal = Float64[], GerMin = Float64[], GerMax = Float64[])
    for ute in lista_utes
        subsubset_1 = df_termicas_sf[(df_termicas_sf.usina .== ute.codigo), :]
        for est_value in unique(subsubset_1.est)
            subset = subsubset_1[subsubset_1.est .== est_value, :]
            for iteracao in unique(subset.iter)
                subsubset = subset[(subset.iter .== iteracao), :]
                Probgeneration = 0
                ProbcustoTotal = 0
                for no in unique(subsubset.node)
                    Probgeneration += (subsubset[(subsubset.node .== no), "generation"][1])*(mapaProbCondicionalNo[no])
                    ProbcustoTotal += (subsubset[(subsubset.node .== no), "custoTotal"][1])*(mapaProbCondicionalNo[no])
                    #println("ProbGT: ", ProbGT, " No: ", no, " GT: ", (subsubset[(subsubset.node .== no), "GT"][1]), " prob: ", (mapaProbCondicionalNo[no]))
                end
                submercado = (subset[(subset.est .== est_value), "Submercado"][1])
                push!(df_per_balanco_energetico_USIT, (etapa = "SF", iter = iteracao, usina = ute.codigo, est = est_value, Submercado = submercado,nome = ute.nome, generation = round(Probgeneration, digits = 0), custo = ute.custo_geracao, custoTotal = round(ProbcustoTotal, digits= 0), GerMin = ute.gmin, GerMax = ute.gmax))
            end
        end
    end
    df_per_balanco_energetico_USIT = sort(df_per_balanco_energetico_USIT, :iter)
    CSV.write(output_dir_oper*"/balanco_energetico_final_UTE.csv", df_per_balanco_energetico_USIT)
    #show(IOContext(stdout, :compact => false), df_per_balanco_energetico_USIT)

    means_ute = combine(df_per_balanco_energetico_USIT, names(df_per_balanco_energetico_USIT, Number) .=> mean)
    #println(means_ute)
    CSV.write(output_dir_oper*"/media_UTE.csv", means_ute)

    df_per_balanco_energetico_EOL = DataFrame(etapa = String[], iter = Int[],  usina = Int[], est = Int[], Submercado = Int[], nome = String[], generation = Float64[], folgaPositiva = Float64[], folgaNegativa = Float64[])
    for eol in lista_eols
        subsubset_1 = df_eolica_sf[(df_eolica_sf.usina .== eol.codigo), :]
        for est_value in unique(subsubset_1.est)
            subset = subsubset_1[subsubset_1.est .== est_value, :]
            for iteracao in unique(subset.iter)
                subsubset = subset[(subset.iter .== iteracao), :]
                Probgeneration = 0
                ProbFolgaPos = 0
                ProbFolgaNeg = 0
                for no in unique(subsubset.node)
                    Probgeneration += (subsubset[(subsubset.node .== no), "generation"][1])*(mapaProbCondicionalNo[no])
                    ProbFolgaPos += (subsubset[(subsubset.node .== no), "folgaPositiva"][1])*(mapaProbCondicionalNo[no])
                    ProbFolgaNeg += (subsubset[(subsubset.node .== no), "folgaNegativa"][1])*(mapaProbCondicionalNo[no])
                    #println("ProbGT: ", ProbGT, " No: ", no, " GT: ", (subsubset[(subsubset.node .== no), "GT"][1]), " prob: ", (mapaProbCondicionalNo[no]))
                end
                submercado = (subset[(subset.est .== est_value), "Submercado"][1])
                push!(df_per_balanco_energetico_EOL, (etapa = "SF", iter = iteracao, usina = eol.codigo, est = est_value, Submercado = submercado,nome = eol.nome, generation = round(Probgeneration, digits = 0), folgaPositiva = round(ProbFolgaPos, digits= 0), folgaNegativa = round(ProbFolgaNeg, digits= 0),))
            end
        end
    end
    df_per_balanco_energetico_EOL = sort(df_per_balanco_energetico_EOL, :iter)
    CSV.write(output_dir_oper*"/balanco_energetico_final_EOL.csv", df_per_balanco_energetico_EOL)
    #show(IOContext(stdout, :compact => false), df_per_balanco_energetico_USIT)

    means_eol = combine(df_per_balanco_energetico_EOL, names(df_per_balanco_energetico_EOL, Number) .=> mean)
    #println(means_ute)
    CSV.write(output_dir_oper*"/media_EOL.csv", means_eol)
    
    df_per_parcelaCustoPresente_sf = DataFrame(etapa = String[], iter = Int[], est = Int[], Submercado = Int[], usina = String[], codigo = Int[], geracao = Float64[], Custo = Float64[], CustoPresente = Float64[], CustoPresenteAcum = Float64[])
    for usi in unique(df_parcelasCustoPresente_sf.usina)
        subsubset_1 = df_parcelasCustoPresente_sf[(df_parcelasCustoPresente_sf.usina .== usi), :]
        for est_value in unique(subsubset_1.est)
            subset = subsubset_1[subsubset_1.est .== est_value, :]
            for iteracao in unique(subset.iter)
                subsubset = subset[(subset.iter .== iteracao), :]
                Probgeneration = 0
                Probcusto = 0
                ProbcustoPresente = 0
                ProbcustoPresenteAcum = 0
                for no in unique(subsubset.node)
                    Probgeneration += (subsubset[(subsubset.node .== no), "geracao"][1])*(mapaProbCondicionalNo[no])
                    Probcusto += (subsubset[(subsubset.node .== no), "Custo"][1])*(mapaProbCondicionalNo[no])
                    ProbcustoPresente += (subsubset[(subsubset.node .== no), "CustoPresente"][1])*(mapaProbCondicionalNo[no])
                    ProbcustoPresenteAcum += (subsubset[(subsubset.node .== no), "CustoPresenteAcum"][1])*(mapaProbCondicionalNo[no])
                    #println("ProbGT: ", ProbGT, " No: ", no, " GT: ", (subsubset[(subsubset.node .== no), "GT"][1]), " prob: ", (mapaProbCondicionalNo[no]))
                end
                submercado = (subset[(subset.est .== est_value), "Submercado"][1])
                codigo_usi = (subset[(subset.est .== est_value), "codigo"][1])
                push!(df_per_parcelaCustoPresente_sf, (etapa = "SF", iter = iteracao, usina = usi, codigo = codigo_usi, est = est_value, Submercado = submercado,geracao = round(Probgeneration, digits = 0), Custo = Probcusto, CustoPresente = round(ProbcustoPresente, digits= 0), CustoPresenteAcum = round(ProbcustoPresenteAcum, digits= 0)))
            end
        end
    end
    df_per_parcelaCustoPresente_sf = sort(df_per_parcelaCustoPresente_sf, :iter)
    CSV.write(output_dir_oper*"/balanco_energetico_final_Parcelas_CP.csv", df_per_parcelaCustoPresente_sf)
    #show(IOContext(stdout, :compact => false), df_per_parcelaCustoPresente_sf)

    means_CustoPresente = combine(df_per_parcelaCustoPresente_sf, names(df_per_parcelaCustoPresente_sf, Number) .=> mean)
    #println(means_CustoPresente)
    CSV.write(output_dir_oper*"/media_CustoPresente.csv", means_CustoPresente)



    df_corte_est = DataFrame(iter = Int[], est = Int[], usina = String[], Indep = Float64[], Coef = Float64[])
    # Lista de DataFrames
    lista_df = DataFrame[]
    estagios = sort(unique(saida_otimizacao.df_cortes_equivalentes.est))
    # Estágios 2 e 3
    #println("it: ", maxIteration)
    #print("estagios: ", estagios)

    for est in estagios
        df_cortes_est = filter(:est => ==(est), saida_otimizacao.df_cortes_equivalentes)
        df_cortes_est = filter(:iter => <(maxIteration), df_cortes_est)
        #println(df_cortes_est)
        if est == 1
            #df_cortes_est = filter(row -> !(row.Indep == 0.0 && row.Coef == 0.0), df_cortes_est)
            #println(df_cortes_est)
            push!(lista_df, df_cortes_est)

        else
            nos_est = unique(df_cortes_est.noUso)
            #println("est: ", est)
            for usi in lista_uhes
                df_cortes_est_usi = filter(:usina => ==(usi.nome), df_cortes_est)
                #println("df_cortes_est_usi: ", df_cortes_est_usi)
                #println(df_cortes_est_usi)
                df_mask = filter(:noUso => ==(nos_est[1]), df_cortes_est_usi)
                #println("df_mask: ", df_mask)
                df_mask.Indep .= 0.0
                df_mask.Coef .= 0.0
                df_mask.noUso .= est
                for node in nos_est
                    #println("node: ", node)
                    df_cortes_est_usi_node = filter(:noUso => ==(node), df_cortes_est_usi)
                    #df_mask = filter(row -> !(row.Indep == 0.0 && row.Coef == 0.0), df_mask)
                    #println("df_cortes_est_usi_node: ", df_cortes_est_usi_node)
                    caminho_node = retornaListaCaminho(node)  # You must define this in Julia
                    
                    prob_cond = 1.0
                    for elemento in caminho_node
                        prob_elemento = df_arvore[df_arvore.NO .== elemento, :PROB][1]
                        prob_cond *= prob_elemento
                    end
                    #println("caminho_node: ", caminho_node, " prob: ", prob_cond)
                    df_mask.Indep .+= df_cortes_est_usi_node.Indep .* prob_cond
                    df_mask.Coef .+= df_cortes_est_usi_node.Coef .* prob_cond
                end
                #println(df_mask)
                push!(lista_df, df_mask)
            end
            
        end
    end
    df_final = vcat(lista_df...)
    #println(df_final)
    CSV.write(output_dir_oper*"/cortes_est.csv", df_final)
end