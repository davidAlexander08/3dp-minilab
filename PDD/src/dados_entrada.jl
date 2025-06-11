
include("structs.jl")

using JSON, CSV, DataFrames, DataStructures
cd(joinpath(@__DIR__, "..",".."))
dict_str_caso = JSON.parsefile("PDD/src/caminho.json"; use_mmap=false)
folder_path = dict_str_caso["CAMINHO_CASO"]
tolerancia = dict_str_caso["TOLERANCIA"]

CONFIG_PATH = folder_path*"/dadosEntrada.json"


@info "Lendo arquivo de configuração $(CONFIG_PATH)"
dict = JSON.parsefile(CONFIG_PATH; use_mmap=false)
caso = CaseData()
caso.n_iter = dict["MAX_ITERACOES"]
caso.n_iter_min = dict["MIN_ITERACOES"]
caso.n_est = dict["ESTAGIOS"]
rede_eletrica = dict["REDE"]
limites_intercambio = dict["LIMITES_INTERCAMBIO"]
vazao_minima = dict["VAZAO_MINIMA"]
penalidVazMin = dict["PENALIDADE_VAZAO_MINIMA"]
volume_minimo = dict["VOLUME_MINIMO"]
volume_espera = dict["VOLUME_ESPERA"]
simfinal = dict["SIMFINAL"]
CAMINHO_CORTES = dict["CAMINHO_CORTES"]
cortes_externos_fim_de_mundo = dict["CORTES_EXTERNOS"]
caminho_cortes_externos_fim_de_mundo = dict["CAMINHO_CORTES_EXTERNOS"]
arvore_externa = dict["ARVORE_EXTERNA"]
caminho_arvore_externa = dict["CAMINHO_ARVORE_EXTERNA"]
vazao_externa = dict["VAZAO_EXTERNA"]
caminho_vazao_externa = dict["CAMINHO_VAZAO_EXTERNA"]
periodos_fim_de_mundo = dict["PERIODOS_FIM_DE_MUNDO"]
restricaoVolumeFimMundo = dict["FIM_DE_MUNDO_VOLUMES"]


if vazao_externa == 1
    @info "Lendo arquivo de vazoes externas $(caminho_vazao_externa)"
    dat_vaz = CSV.read(caminho_vazao_externa, DataFrame)
    dados_saida = splitdir(caminho_vazao_externa)[1]
end

include("arvore.jl")





if(simfinal == 1)
    dat_cortes_ext = CSV.read(CAMINHO_CORTES, DataFrame)
    cortes_filtrados = filter(row -> row.est == 2, dat_cortes_ext)
    mex_iter_est = maximum(cortes_filtrados.iter)
    caso.n_iter = 1
    @info "EXECUTANDO SIMULACAO FINAL"
end


############ CORTES DA FCF EXTERNA PARA FIM DE MUNDO DO PRIMEIRO ESTÀGIO DOS CORTES
if(cortes_externos_fim_de_mundo == 1)
    PATH_CORTES_EXTERNOS_FIM_MUNDO = caminho_cortes_externos_fim_de_mundo
    dat_cortes_externos_fim_mundo = CSV.read(PATH_CORTES_EXTERNOS_FIM_MUNDO, DataFrame)
    cortes_filtrados = filter(row -> row.est == 1, dat_cortes_externos_fim_mundo)
    mex_iter_est_cortes_externos = maximum(cortes_filtrados.iter)
    @info "Executando com Cortes Externos Fim de Mundo"
end



if(limites_intercambio == 1)
    PATH_RESTR_INTERCAMBIOS = folder_path*"/OPERACAO/restr_limite_Intercambio.csv"
    @info "Lendo arquivo de intercambios $(PATH_RESTR_INTERCAMBIOS)"
    dat_interc = CSV.read(PATH_RESTR_INTERCAMBIOS, DataFrame)
end

if(volume_minimo == 1)
    PATH_RESTR_VOLUME_MINIMO = folder_path*"/OPERACAO/restr_vol_min.csv"
    @info "Lendo arquivo de vazao minima $(PATH_RESTR_VOLUME_MINIMO)"
    dat_volmin = CSV.read(PATH_RESTR_VOLUME_MINIMO, DataFrame)
end

if(volume_espera == 1)
    PATH_RESTR_VOLUME_ESPERA = folder_path*"/OPERACAO/restr_vol_max.csv"
    @info "Lendo arquivo de volume maximo $(PATH_RESTR_VOLUME_ESPERA)"
    dat_volmax = CSV.read(PATH_RESTR_VOLUME_ESPERA, DataFrame)
end


if(vazao_minima == 1)
    PATH_RESTR_VAZAO_MINIMA = folder_path*"/OPERACAO/restr_vazao_minima.csv"
    @info "Lendo arquivo de vazao minima $(PATH_RESTR_VAZAO_MINIMA)"
    dat_vazmin = CSV.read(PATH_RESTR_VAZAO_MINIMA, DataFrame)
end



PATH_HORAS = folder_path*"/OPERACAO/OPER_DURACAO.csv"
@info "Lendo arquivo de horas $(PATH_HORAS)"
dat_horas = CSV.read(PATH_HORAS, DataFrame)

PATH_CADASTRO_SBMs = folder_path*"/CADASTRO/CADASTRO_SBM.csv"
@info "Lendo arquivo de cadastro dos submercados"
dat_cadastro_sbms = CSV.read(PATH_CADASTRO_SBMs, DataFrame)

PATH_OPER_DEMANDA_SBM = folder_path*"/OPERACAO/OPER_DEMANDA_SBM.csv"
dat_oper_demanda_sbm = CSV.read(PATH_OPER_DEMANDA_SBM, DataFrame)

PATH_OPER_DEFICIT_SBM = folder_path*"/OPERACAO/OPER_DEFICIT_SBM.csv"
dat_oper_deficit_sbm = CSV.read(PATH_OPER_DEFICIT_SBM, DataFrame)

lista_submercados = []
mapa_nome_SBM = OrderedDict()
mapa_codigo_SBM = OrderedDict()
cadastroUsinasHidreletricasSubmercado = OrderedDict()
cadastroUsinasTermicasSubmercado = OrderedDict()
cadastroUsinasEolicasSubmercado = OrderedDict()

for row in eachrow(dat_cadastro_sbms)
    df_demanda_sbm = dat_oper_demanda_sbm[dat_oper_demanda_sbm.codigo_submercado .== row.codigo, :]
    vetor_demanda = df_demanda_sbm.valor
    df_deficit_sbm = dat_oper_deficit_sbm[dat_oper_deficit_sbm.codigo_submercado .== row.codigo, :]
    vetor_deficit = df_deficit_sbm.valor
        
    println(vetor_demanda)
    println(vetor_deficit)
    submercado = SubmercadoConfigData()
    submercado.nome = row.nome
    submercado.codigo = row.codigo
    submercado.deficit_cost = vetor_deficit[1]
    submercado.demanda = vetor_demanda
    push!(lista_submercados,submercado)
    mapa_nome_SBM[row.nome] = submercado
    mapa_codigo_SBM[row.codigo] = submercado
    cadastroUsinasHidreletricasSubmercado[row.codigo] = []
    cadastroUsinasTermicasSubmercado[row.codigo] = []
    cadastroUsinasEolicasSubmercado[row.codigo] = []
end


############# META DE ARMAZENAMENTO DO FIM DE MUNDO

if(restricaoVolumeFimMundo == 1)
    PATH_RESTR_META_VOLUME = folder_path*"/restr_meta_armazenamento.csv"
    @info "Executando caso com meta de armazenamento no fim de mundo"
    dat_meta_armazenamento = CSV.read(PATH_RESTR_META_VOLUME, DataFrame)
end




#@info "Lendo arquivo de rede elétrica"
#
#dicionario_codigo_barra = OrderedDict()
## BARRAS
#barras = dict["BARRAS"]
#lista_barras = []
#lista_barras_sem_slack = []
#lista_barras_slack = []
#mapaCodigoBarra = OrderedDict()
#for barra in barras
#    objeto = BarraConfig()
#    objeto.codigo = barra["CODIGO"]
#    for it in range(1, caso.n_iter)
#        for no in lista_total_de_nos
#            objeto.potenciaGerada[it, no.codigo] = barra["GERACAO"][1]
#            objeto.potenciaLiquida[it, no.codigo] = barra["GERACAO"][1]
#        end
#    end
#    objeto.carga = barra["CARGA"]
#    objeto.area = barra["AREA"]
#    lista_estado_operacao = barra["ESTADODEOPERACAO"]
#    for (est,elemento) in enumerate(lista_estado_operacao)
#        objeto.estadoDeOperacao[est] = elemento 
#    end
#    objeto.tipo = barra["TIPO"]
#    push!(lista_barras,objeto)
#    dicionario_codigo_barra[objeto.codigo] = objeto
#    if objeto.tipo == 2
#        push!(lista_barras_slack, objeto)
#    else
#        push!(lista_barras_sem_slack, objeto)
#    end
#    mapaCodigoBarra[objeto.codigo] = objeto
#end
#
## BARRAS
#linhas = dict["LINHAS"]
#lista_linhas = []
#for (contador,linha) in enumerate(linhas)
#    objeto = LinhaConfig()
#    objeto.de = dicionario_codigo_barra[linha["DE"]] 
#    objeto.para = dicionario_codigo_barra[linha["PARA"]] 
#    objeto.indice = linha["N_CIRCUITOS"]
#    objeto.X = linha["REATANCIA"]
#    objeto.Capacidade = linha["CAPACIDADE"]
#    lista_estado_operacao = linha["ESTADODEOPERACAO"]
#    for (est,elemento) in enumerate(lista_estado_operacao)
#        objeto.estadoDeOperacao[est] = elemento 
#    end
#    objeto.codigo = contador
#    objeto.defasador = linha["DEFASADOR"]
#    push!(lista_linhas,objeto)
#    contador = contador + 1
#end
#println(lista_linhas)

#mapa_nomeUSINA_codigoBARRA = OrderedDict()
#mapa_codigoBARRA_nomeUSINA = OrderedDict()
#

PATH_CADASTRO_UEOLs = folder_path*"/CADASTRO/CADASTRO_UEOL.csv"
@info "Lendo arquivo de cadastro das Eólicas"
dat_cadastro_ueols = CSV.read(PATH_CADASTRO_UEOLs, DataFrame)
lista_eols = []
mapa_nome_EOL = OrderedDict()
for row in eachrow(dat_cadastro_ueols)
    usina = EOLConfigData()
    usina.nome = row.nome
    usina.codigo = row.codigo
    usina.gmin = row.pmin
    usina.gmax = row.pmax
    usina.posto = row.posto
    push!(lista_eols,usina)
    mapa_nome_EOL[usina.nome] = usina
    push!(cadastroUsinasEolicasSubmercado[row.codigo_submercado],usina)
end
#
#



PATH_CADASTRO_UTEs = folder_path*"/CADASTRO/CADASTRO_UTE.csv"
@info "Lendo arquivo de cadastro das térmicas"
dat_cadastro_utes = CSV.read(PATH_CADASTRO_UTEs, DataFrame)

lista_utes = []
mapa_nome_UTE = OrderedDict()
for row in eachrow(dat_cadastro_utes)
    usina = UTEConfigData()
    usina.nome = row.nome
    usina.gmin = row.pmin
    usina.gmax = row.pmax
    usina.custo_geracao = row.custo
    usina.codigo = row.codigo
    push!(lista_utes,usina)
    mapa_nome_UTE[usina.nome] = usina
    push!(cadastroUsinasTermicasSubmercado[row.codigo_submercado],usina)
end

PATH_CADASTRO_UHEs = folder_path*"/CADASTRO/CADASTRO_UHE.csv"
@info "Lendo arquivo de cadastro das hidrelétricas"
dat_cadastro_uhes = CSV.read(PATH_CADASTRO_UHEs, DataFrame)

PATH_CADASTRO_CONJ_UHE = folder_path*"/CADASTRO/CADASTRO_CONJ_UHE.csv"
dat_cadastro_conj_uhes = CSV.read(PATH_CADASTRO_CONJ_UHE, DataFrame)


# UHEs
lista_uhes = []
mapa_nome_UHE = OrderedDict()
for row in eachrow(dat_cadastro_uhes)
    df_unidades = dat_cadastro_conj_uhes[dat_cadastro_conj_uhes.nome .== row.nome, :]
    for unidade in eachrow(df_unidades )
        usina = UHEConfigData()
        usina.nome = string(row.nome)
        if row.jusante === missing
            usina.jusante = ""
        else
            usina.jusante = string(row.jusante)
        end
        
        usina.vmin = row.vmin
        usina.vmax = row.vmax
        usina.v0 = row.volume_inicial
        usina.codigo = row.codigo
        usina.gmin = unidade.pmin
        usina.gmax = unidade.pmax
        usina.turbmax = unidade.turbinamento_maximo
        usina.prodt = unidade.produtibilidade
        usina.posto = row.posto
        push!(lista_uhes,usina)
        mapa_nome_UHE[usina.nome] = usina
        push!(cadastroUsinasHidreletricasSubmercado[unidade.codigo_submercado], usina)
    end
end

caso.n_term =size(lista_utes)[1]
caso.n_uhes =size(lista_uhes)[1]

mapa_montantesUsina = Dict{String, Array{String, 1}}()
for uhe in lista_uhes
    if !haskey(mapa_montantesUsina, uhe.nome)
        mapa_montantesUsina[uhe.nome] = String[]  # Initialize an empty array if it doesn't exist
    end
    for candidata_montante in lista_uhes
        if uhe.nome == candidata_montante.jusante
            push!(mapa_montantesUsina[uhe.nome], candidata_montante.nome)
        end
    end
end


mapaUsinaProdtAcum = Dict{String, Float64}()
for uhe in lista_uhes
    if !haskey(mapa_montantesUsina, uhe.nome)
        mapa_montantesUsina[uhe.nome] = String[]  # Initialize an empty array if it doesn't exist
    end
    lista_cascata = String[]
    jusante = uhe.jusante
    usina = uhe
    while jusante != ""
        for usi_jus in lista_uhes
            if usi_jus.codigo == parse(Int, usina.jusante)
                push!(lista_cascata, usi_jus.nome)
                usina = usi_jus
                jusante = usina.jusante
                break
            end
        end
    end
    prodt_acum = uhe.prodt
    for usi_cascata in lista_cascata
        prodt_acum += mapa_nome_UHE[usi_cascata].prodt
    end
    mapaUsinaProdtAcum[uhe.nome] = prodt_acum
end







##########    ECO

df_eco_hidro  = DataFrame(codigo = Int[], nome = String[], posto = Int[], Jusante = String[], Submercado = Int[], PotInst = Int[], 
EngolMax = Int[], VolMin = Int[], VolMax = Int[], Prodt = Float64[], VolIni = Int[])
df_eco_termo  = DataFrame(codigo = Int[], nome = String[], Submercado = Int[], Gmin = Float64[], Gmax = Float64[])
df_eco_submercado = DataFrame(codigo = Int[], nome = String[], custoDeficit = Int[], Est = [], Demanda = [])

def_restr_RHQ = DataFrame(codigo = Int[], Vazmin = Int[] , PercVolmin = Float64[] , PercVolmax = Float64[])


for sbm in lista_submercados

    for est in 1:caso.n_est
        push!(df_eco_submercado, (codigo = sbm.codigo, nome = sbm.nome, 
        custoDeficit = sbm.deficit_cost, Est = est, Demanda = sbm.demanda[est]))
    end

    for uhe in cadastroUsinasHidreletricasSubmercado[sbm.codigo]
        usi_jusante = isempty(uhe.jusante) ? "-" : uhe.jusante
        push!(df_eco_hidro, (codigo = uhe.codigo, nome = uhe.nome, posto = uhe.posto, Jusante = usi_jusante, Submercado = sbm.codigo, 
        PotInst = uhe.gmax, EngolMax = uhe.turbmax, VolMin = uhe.vmin, VolMax = uhe.vmax, Prodt = uhe.prodt, VolIni = uhe.v0))
    
        vazao_minima_uhe = 0
        if(vazao_minima == 1)
            dat_vazmin.USI = string.(dat_vazmin.USI)
            matching_rows = dat_vazmin[dat_vazmin.USI .== uhe.nome, :vazmin]
            vazao_minima_uhe = isempty(matching_rows) ? NaN : first(matching_rows)
            if !isnan(vazao_minima_uhe)
                vazao_minima_uhe = vazao_minima_uhe
            else
                vazao_minima_uhe = 0
            end
        else
            vazao_minima_uhe = 0
        end
        vol_min_uhe = 0
        if(volume_minimo == 1)
            dat_volmin.USI = string.(dat_volmin.USI)
            matching_rows = dat_volmin[dat_volmin.USI .== uhe.nome, :vmin]
            vol_min_uhe = isempty(matching_rows) ? NaN : first(matching_rows)
            vol_min_uhe = vol_min_uhe/100
            if !isnan(vol_min_uhe)
                vol_min_uhe = vol_min_uhe
            else
                vol_min_uhe = 0
            end
        else
            vol_min_uhe = 0
        end

        vol_max_uhe = 0
        if(volume_espera == 1)
            dat_volmax.USI = string.(dat_volmax.USI)
            matching_rows = dat_volmax[dat_volmax.USI .== uhe.nome, :vmax]
            vol_max_uhe = isempty(matching_rows) ? NaN : first(matching_rows)
            vol_max_uhe = vol_max_uhe/100
            if !isnan(vol_max_uhe)
                vol_max_uhe = vol_max_uhe
            else
                vol_max_uhe = 0
            end
        end
        push!(def_restr_RHQ, (codigo = uhe.codigo , Vazmin = vazao_minima_uhe,
        PercVolmin = vol_min_uhe, PercVolmax = vol_max_uhe))
    end

    for ute in cadastroUsinasTermicasSubmercado[sbm.codigo]
        push!(df_eco_termo, (codigo = ute.codigo, nome = ute.nome, Submercado = sbm.codigo, Gmin = ute.gmin, Gmax = ute.gmax))
    end
end

output_dir_eco = dados_saida*"/saidas/PDD/eco"
println(output_dir_eco)
mkpath(output_dir_eco)
CSV.write(output_dir_eco*"/df_uhes.csv", df_eco_hidro)
CSV.write(output_dir_eco*"/df_utes.csv", df_eco_termo)
CSV.write(output_dir_eco*"/df_submercados.csv", df_eco_submercado)
CSV.write(output_dir_eco*"/df_RHQ.csv", def_restr_RHQ)
CSV.write(output_dir_eco*"/dat_prob.csv", dat_prob)
CSV.write(output_dir_eco*"/dat_vaz.csv", dat_vaz)
CSV.write(output_dir_eco*"/df_arvore.csv", df_arvore)
