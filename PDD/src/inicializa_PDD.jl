conversao_m3_to_hm3 = 60*60/1000000
etapas = ["FW", "BK"]
Vi = Dict{Tuple{Int,Int, String}, Float64}()
for etapa in etapas
    for no in lista_total_de_nos
        for uhe in lista_uhes
            if no.codigo == 1 
                Vi[(no.codigo, uhe.codigo, etapa)] = uhe.v0 
            else
                Vi[(no.codigo, uhe.codigo, etapa)] = 0
            end
        end
    end
end

horas_periodo = dat_horas[(dat_horas.PERIODO .== 1), "HORAS"][1]    
converte_m3s_hm3 = horas_periodo*conversao_m3_to_hm3
global EARM_INI_SIN = 0
global EARM_MIN_SIN = 0
global EARM_MAX_SIN = 0
global V_MIN_SIN = 0
global V_INI_SIN = 0
global V_MAX_SIN = 0
for sbm in lista_submercados
    EARM_INI = 0
    EARM_MAX = 0
    EARM_MIN = 0
    VOL_INI = 0
    VOL_MAX = 0
    VOL_MIN = 0
    for uhe in cadastroUsinasHidreletricasSubmercado[sbm.codigo]
        #println("UHE: ", uhe.codigo, " EARM: ", uhe.v0*uhe.prodt)
        EARM_INI += uhe.v0*mapaUsinaProdtAcum[uhe.nome]/converte_m3s_hm3
        EARM_MAX += uhe.vmax*mapaUsinaProdtAcum[uhe.nome]/converte_m3s_hm3
        EARM_MIN += uhe.vmin*mapaUsinaProdtAcum[uhe.nome]/converte_m3s_hm3
        VOL_INI  += uhe.v0
        VOL_MAX  += uhe.vmax
        VOL_MIN  += uhe.vmin
    end
    global EARM_INI_SIN += EARM_INI
    global EARM_MAX_SIN += EARM_MAX
    global EARM_MIN_SIN += EARM_MIN
    global V_MIN_SIN += VOL_MIN
    global V_INI_SIN += VOL_INI
    global V_MAX_SIN += VOL_MAX
    #println("SUBM: ", sbm.nome, " EARMI: ", EARM_INI)
end
println("SIN EARM_INI_SIN: ", EARM_INI_SIN,  " EARM_MAX_SIN: ", EARM_MAX_SIN, " EARM MIN: ", EARM_MIN_SIN)
println("SIN V_INI_SIN: ", V_INI_SIN,  " V_MAX_SIN: ", V_MAX_SIN, " V_MIN_SIN: ", V_MIN_SIN)

#println("GERACAO TERMICA MINIMA E MAXIMA -----------")
GTER_MIN_SIN = 0
GTER_MAX_SIN = 0
for sbm in lista_submercados
    GTER_MIN = 0
    GTER_MAX = 0
    for ute in cadastroUsinasTermicasSubmercado[sbm.codigo]
        #println("UHE: ", uhe.codigo, " EARM: ", uhe.v0*uhe.prodt)
        GTER_MIN += ute.gmin
        GTER_MAX += ute.gmax
    end
    global GTER_MIN_SIN += GTER_MIN  # 🔹 Adicione `global`
    global GTER_MAX_SIN += GTER_MAX  # 🔹 Adicione `global`
    #println("SUBM: ", sbm.nome, " GTMIN: ", GTER_MIN,  " GTMAX: ", GTER_MAX)
end
println("SIN GTMIN: ", GTER_MIN_SIN,  " GTMAX: ", GTER_MAX_SIN)

FCF_coef = OrderedDict{Tuple{Int, Int,Int}, Float64}()
FCF_indep = OrderedDict{Tuple{Int,Int}, Float64}()


for it in 1:caso.n_iter, est in 1:caso.n_est, no in lista_total_de_nos ,uhe in lista_uhes
    FCF_coef[(it, no.codigo, uhe.codigo)] = 0.0
end

for it in 1:caso.n_iter, no in lista_total_de_nos
    FCF_indep[(it, no.codigo)] = 0.0
end

lista_zinf = OrderedDict{Int, Float64}()
lista_zsup = OrderedDict{Int, Float64}()
lista_gap = OrderedDict{Int, Float64}()
for it in 1:caso.n_iter
    lista_zinf[it] = 0.0
    lista_zsup[it] = 0.0
    lista_gap[it] = 0.0
end


CustoI = OrderedDict{Tuple{Int, Int, String}, Float64}()
CustoF = OrderedDict{Tuple{Int, Int, String}, Float64}()
for it in 1:caso.n_iter, no in lista_total_de_nos, etapa in etapas
    CustoI[(it, no.codigo, etapa)] = 0.0
    CustoF[(it,no.codigo, etapa)] = 0.0
end
println("NUMERO DE USINAS HIDRELETRICAS: ", length(lista_uhes))
println("NUMERO DE USINAS TERMICAS: ", length(lista_utes))
println("NUMERO DE USINAS EOLICAS: ", length(lista_eols))