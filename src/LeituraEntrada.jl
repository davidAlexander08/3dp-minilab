
include("DefStructs.jl")

using JSON
using CSV
using DataFrames
#using Graphs
using LightGraphs
using SparseArrays
using DataStructures

#CONFIG_PATH = "caso_deterministico/dadosEntrada.json"
#PATH_VAZOES = "caso_deterministico/vazao.csv"
#PATH_PROBABILIDADES = "caso_deterministico/probabilidades.csv"

#CONFIG_PATH = "caso_arvore/dadosEntrada.json"
#PATH_VAZOES = "caso_arvore/vazao.csv"
#PATH_PROBABILIDADES = "caso_arvore/probabilidades.csv"



CONFIG_PATH = "caso_decomp_pente/dadosEntrada.json"
PATH_VAZOES = "caso_decomp_pente/vazao.csv"
PATH_PROBABILIDADES = "caso_decomp_pente/probabilidades.csv"
PATH_HORAS = "caso_decomp_pente/horas.csv"




CONFIG_PATH = "caso_decomp_arvore/dadosEntrada.json"
PATH_VAZOES = "caso_decomp_arvore/vazao.csv"
PATH_PROBABILIDADES = "caso_decomp_arvore/probabilidades.csv"
PATH_HORAS = "caso_decomp_arvore/horas.csv"









#CONFIG_PATH = "caso_decomp_deterministico_4Barras_3UTEs_1EST/dadosEntrada.json"
#PATH_VAZOES = "caso_decomp_deterministico_4Barras_3UTEs_1EST/vazao.csv"
#PATH_PROBABILIDADES = "caso_decomp_deterministico_4Barras_3UTEs_1EST/probabilidades.csv"
#PATH_HORAS = "caso_decomp_deterministico_4Barras_3UTEs_1EST/horas.csv"








CONFIG_PATH = "caso_decomp_deterministico_24Barras_1EST/dadosEntrada.json"
PATH_VAZOES = "caso_decomp_deterministico_24Barras_1EST/vazao.csv"
PATH_PROBABILIDADES = "caso_decomp_deterministico_24Barras_1EST/probabilidades.csv"
PATH_HORAS = "caso_decomp_deterministico_24Barras_1EST/horas.csv"








CONFIG_PATH = "caso_decomp_deterministico_6Barras_3UTEs_1EST/dadosEntrada.json"
PATH_VAZOES = "caso_decomp_deterministico_6Barras_3UTEs_1EST/vazao.csv"
PATH_PROBABILIDADES = "caso_decomp_deterministico_6Barras_3UTEs_1EST/probabilidades.csv"
PATH_HORAS = "caso_decomp_deterministico_6Barras_3UTEs_1EST/horas.csv"


CONFIG_PATH = "caso_decomp_deterministico_24Barras_1EST/dadosEntrada.json"
PATH_VAZOES = "caso_decomp_deterministico_24Barras_1EST/vazao.csv"
PATH_PROBABILIDADES = "caso_decomp_deterministico_24Barras_1EST/probabilidades.csv"
PATH_HORAS = "caso_decomp_deterministico_24Barras_1EST/horas.csv"


CONFIG_PATH = "caso_decomp_pente/dadosEntrada.json"
PATH_VAZOES = "caso_decomp_pente/vazao.csv"
PATH_PROBABILIDADES = "caso_decomp_pente/probabilidades.csv"
PATH_HORAS = "caso_decomp_pente/horas.csv"

CONFIG_PATH = "caso_decomp_deterministico_6Barras_2UTEs_1UHE_2EST/dadosEntrada.json"
PATH_VAZOES = "caso_decomp_deterministico_6Barras_2UTEs_1UHE_2EST/vazao.csv"
PATH_PROBABILIDADES = "caso_decomp_deterministico_6Barras_2UTEs_1UHE_2EST/probabilidades.csv"
PATH_HORAS = "caso_decomp_deterministico_6Barras_2UTEs_1UHE_2EST/horas.csv"





CONFIG_PATH = "caso_decomp_pente_testeCen/dadosEntrada.json"
PATH_VAZOES = "caso_decomp_pente_testeCen/vazao.csv"
PATH_PROBABILIDADES = "caso_decomp_pente_testeCen/probabilidades.csv"
PATH_HORAS = "caso_decomp_pente_testeCen/horas.csv"

CONFIG_PATH = "caso_decomp_deterministico_24Barras_2EST/dadosEntrada.json"
PATH_VAZOES = "caso_decomp_deterministico_24Barras_2EST/vazao.csv"
PATH_PROBABILIDADES = "caso_decomp_deterministico_24Barras_2EST/probabilidades.csv"
PATH_HORAS = "caso_decomp_deterministico_24Barras_2EST/horas.csv"



CONFIG_PATH = "caso_decomp_deterministico_3Barras_2UTEs_3EST/dadosEntrada.json"
PATH_VAZOES = "caso_decomp_deterministico_3Barras_2UTEs_3EST/vazao.csv"
PATH_PROBABILIDADES = "caso_decomp_deterministico_3Barras_2UTEs_3EST/probabilidades.csv"
PATH_HORAS = "caso_decomp_deterministico_3Barras_2UTEs_3EST/horas.csv"



CONFIG_PATH = "caso_decomp_deterministico_3Barras_2UHEs_3EST/dadosEntrada.json"
PATH_VAZOES = "caso_decomp_deterministico_3Barras_2UHEs_3EST/vazao.csv"
PATH_PROBABILIDADES = "caso_decomp_deterministico_3Barras_2UHEs_3EST/probabilidades.csv"
PATH_HORAS = "caso_decomp_deterministico_3Barras_2UHEs_3EST/horas.csv"


CONFIG_PATH = "caso_decomp_deterministico_5est_2UHE_2UTE/dadosEntrada.json"
PATH_VAZOES = "caso_decomp_deterministico_5est_2UHE_2UTE/vazao.csv"
PATH_PROBABILIDADES = "caso_decomp_deterministico_5est_2UHE_2UTE/probabilidades.csv"
PATH_HORAS = "caso_decomp_deterministico_5est_2UHE_2UTE/horas.csv"




CONFIG_PATH = "caso_decomp_deterministico_3Barras_1UTE_1UHE_3EST/dadosEntrada.json"
PATH_VAZOES = "caso_decomp_deterministico_3Barras_1UTE_1UHE_3EST/vazao.csv"
PATH_PROBABILIDADES = "caso_decomp_deterministico_3Barras_1UTE_1UHE_3EST/probabilidades.csv"
PATH_HORAS = "caso_decomp_deterministico_3Barras_1UTE_1UHE_3EST/horas.csv"


CONFIG_PATH = "caso_decomp_pente_2_Aberturas_3Barras_1UTE_1UHE_3EST/dadosEntrada.json"
PATH_VAZOES = "caso_decomp_pente_2_Aberturas_3Barras_1UTE_1UHE_3EST/vazao.csv"
PATH_PROBABILIDADES = "caso_decomp_pente_2_Aberturas_3Barras_1UTE_1UHE_3EST/probabilidades.csv"
PATH_HORAS = "caso_decomp_pente_2_Aberturas_3Barras_1UTE_1UHE_3EST/horas.csv"



CONFIG_PATH = "caso_sanidade_6Barras_2meses_2UHE_2UTE_PENTE_2_CEN/dadosEntrada.json"
PATH_VAZOES = "caso_sanidade_6Barras_2meses_2UHE_2UTE_PENTE_2_CEN/vazao.csv"
PATH_PROBABILIDADES = "caso_sanidade_6Barras_2meses_2UHE_2UTE_PENTE_2_CEN/probabilidades.csv"
PATH_HORAS = "caso_sanidade_6Barras_2meses_2UHE_2UTE_PENTE_2_CEN/horas.csv"
#
CONFIG_PATH = "caso_sanidade_6Barras_2meses_2UHE_2UTE_PENTE_100_CEN/dadosEntrada.json"
PATH_VAZOES = "caso_sanidade_6Barras_2meses_2UHE_2UTE_PENTE_100_CEN/vazao.csv"
PATH_PROBABILIDADES = "caso_sanidade_6Barras_2meses_2UHE_2UTE_PENTE_100_CEN/probabilidades.csv"
PATH_HORAS = "caso_sanidade_6Barras_2meses_2UHE_2UTE_PENTE_100_CEN/horas.csv"



CONFIG_PATH = "caso_sanidade_6Barras_2meses_2UHE_2UTE_ARVORE_3ABR/dadosEntrada.json"
PATH_VAZOES = "caso_sanidade_6Barras_2meses_2UHE_2UTE_ARVORE_3ABR/vazao.csv"
PATH_PROBABILIDADES = "caso_sanidade_6Barras_2meses_2UHE_2UTE_ARVORE_3ABR/probabilidades.csv"
PATH_HORAS = "caso_sanidade_6Barras_2meses_2UHE_2UTE_ARVORE_3ABR/horas.csv"


str_caso = "caso_decomp_deterministico_3Barras_1UTE_1UHE_3EST"

str_caso = "caso_sanidade_6Barras_2meses_2UHE_2UTE"
str_caso = "caso_sanidade_6Barras_2meses_2UHE_2UTE_PENTE_2_CEN"
str_caso = "caso_decomp_deterministico_24Barras_3EST"

str_caso = "caso_sanidade_6Barras_2meses_2UHE_2UTE_ARVORE_2ABR"
str_caso = "caso_decomp_deterministico_5est_2UHE_2UTE"
str_caso = "Teste_Fluxo_IEEE_14_Barras"
str_caso = "Teste_Fluxo_IEEE_30_Barras"
str_caso = "Teste_Fluxo_IEEE_57_Barras"
str_caso = "Teste_Fluxo_IEEE_118_Barras"
str_caso = "red_arv_nested_decomposition/3aberturas"
str_caso = "red_arv_decomposition/2aberturas_ARI"
str_caso = "red_arv_decomposition/2aberturas_ARO"

str_caso = "red_arv_fast_and_forward/2aberturas_ini"
str_caso = "red_arv_fast_and_forward/2aberturas_ffs"
str_caso = "red_arv_fast_and_forward/2aberturas_op1"
str_caso = "red_arv_fast_and_forward/2aberturas_op2"
str_caso = "red_arv_fast_and_forward/2aberturas_op3"

str_caso = "casos/marcato/caso_marcato_deterministico"

#str_caso = "red_arv_backReduction/2aberturas_ini"
#str_caso = "red_arv_backReduction/2aberturas_ini_Cen1"
#str_caso = "red_arv_backReduction/2aberturas_ini_Cen3"
#str_caso = "red_arv_backReduction/2aberturas_ini_Cen4"
#str_caso = "red_arv_backReduction/2aberturas_ini_Cen5"
#str_caso = "red_arv_backReduction/2aberturas_ini_Cen2_BK"

#str_caso = "Mestrado/2aberturas_ini"
#str_caso = "Mestrado/caso_construcaoArvore"
#str_caso = "Mestrado/caso_construcaoArvore_SIN_50cen"
#str_caso = "Mestrado/caso_construcaoArvore_SIN_2000cen"
#str_caso = "Mestrado/caso_construcaoArvore_SIN_1000cen"
#str_caso = "Mestrado/caso_construcaoArvore_SIN_1000cen_testeOtim"
#str_caso = "Mestrado/caso_construcaoArvore_SIN_500cen"
#str_caso = "Mestrado/caso_construcaoArvore_SIN_50cen"
str_caso = "Mestrado/caso_construcaoArvore_SIN"
str_caso = "Mestrado/caso_construcaoArvore_SIN_reduzido"
str_caso = "Dissertacao/caso_construcaoArvore_SIN_reduzido"
str_caso = "Dissertacao/caso_construcaoArvore_SIN_reduzido_arvore_Externa"
str_caso = "casos/Mestrado/caso_construcaoArvore_SIN"
str_caso = "Dissertacao/caso_construcaoArvore_SIN_reduzido_maior"
str_caso = "Dissertacao/caso_teste_submercados"
str_caso = "Dissertacao/caso_construcaoArvore_SIN_reduzido_maior_TesteConversor"
#str_caso = "Mestrado/caso_construcaoArvore_SIN_reduzido_2cen"
#str_caso = "Mestrado/caso_construcaoArvore_SIN_mini_2cen"
#str_caso = "Mestrado/caso_construcaoArvore_SIN_mini_2cen_2est"
#str_caso = "Mestrado/caso_construcaoArvore_SIN_mini_mini_2cen_2est"
#str_caso = "Mestrado/caso_construcaoArvore_SIN_mini_mini_min_2cen_2est"
#str_caso = "Mestrado/caso_construcaoArvore_SIN_mini_mini_min_mini_2cen_2est"
#str_caso = "Mestrado/caso_construcaoArvore_SIN_mini_mini_min_mini_2cen_2est_det"
#str_caso = "Teste_Fluxo_IEEE_5_Barras"
CONFIG_PATH = str_caso*"/dadosEntrada.json"
PATH_HORAS = str_caso*"/horas.csv"


@info "Lendo arquivo de configuração $(CONFIG_PATH)"
dict = JSON.parsefile(CONFIG_PATH; use_mmap=false)



caso = CaseData()
caso.n_iter = dict["MAX_ITERACOES"]
caso.n_est = dict["ESTAGIOS"]
rede_eletrica = dict["REDE"]
arvore_externa = dict["ARVORE_EXTERNA"]
limites_intercambio = dict["LIMITES_INTERCAMBIO"]
vazao_minima = dict["VAZAO_MINIMA"]
penalidVazMin = dict["PENALIDADE_VAZAO_MINIMA"]
volume_minimo = dict["VOLUME_MINIMO"]
volume_espera = dict["VOLUME_ESPERA"]
caminho_arvore_externa = dict["CAMINHO_ARVORE_EXTERNA"]
caso.estrutura_arvore = dict["ARVORE"]

if(limites_intercambio == 1)
    PATH_RESTR_INTERCAMBIOS = str_caso*"/restr_limite_Intercambio.csv"
    @info "Lendo arquivo de intercambios $(PATH_RESTR_INTERCAMBIOS)"
    dat_interc = CSV.read(PATH_RESTR_INTERCAMBIOS, DataFrame)
    #print(dat_interc)
end

if(volume_minimo == 1)
    PATH_RESTR_VOLUME_MINIMO = str_caso*"/restr_vol_min.csv"
    @info "Lendo arquivo de vazao minima $(PATH_RESTR_VOLUME_MINIMO)"
    dat_volmin = CSV.read(PATH_RESTR_VOLUME_MINIMO, DataFrame)
    #print(dat_volmin)
end

if(volume_espera == 1)
    PATH_RESTR_VOLUME_ESPERA = str_caso*"/restr_vol_max.csv"
    @info "Lendo arquivo de vazao minima $(PATH_RESTR_VOLUME_ESPERA)"
    dat_volmax = CSV.read(PATH_RESTR_VOLUME_ESPERA, DataFrame)
    #print(dat_volmax)
end


if(vazao_minima == 1)
    PATH_RESTR_VAZAO_MINIMA = str_caso*"/restr_vazao_minima.csv"
    @info "Lendo arquivo de vazao minima $(PATH_RESTR_VAZAO_MINIMA)"
    dat_vazmin = CSV.read(PATH_RESTR_VAZAO_MINIMA, DataFrame)
    #print(dat_vazmin)
end


#caminho_vazao_externa = dict["CAMINHO_VAZAO_EXTERNA"]
#caminho_probabilidade_externa = dict["CAMINHO_PROBABILIDADE_EXTERNA"]
#if arvore_externa == 1
#    PATH_VAZOES = caminho_vazao_externa
#    PATH_PROBABILIDADES = caminho_probabilidade_externa
#else
#    PATH_VAZOES = str_caso*"/vazao.csv"
#    PATH_PROBABILIDADES = str_caso*"/probabilidades.csv"
#end
PATH_VAZOES = str_caso*"/vazao.csv"
PATH_PROBABILIDADES = str_caso*"/probabilidades.csv"



@info "Lendo arquivo de vazoes $(PATH_VAZOES)"
dat_vaz = CSV.read(PATH_VAZOES, DataFrame)
@info "Lendo arquivo de probabilidades $(PATH_PROBABILIDADES)"
dat_prob = CSV.read(PATH_PROBABILIDADES, DataFrame)
include("arvore.jl")







@info "Lendo arquivo de horas $(PATH_HORAS)"
dat_horas = CSV.read(PATH_HORAS, DataFrame)

#caso_teste_submercados
submercados = dict["SUBMERCADOs"]
lista_submercados = []
mapa_nome_SBM = OrderedDict()
mapa_codigo_SBM = OrderedDict()
cadastroUsinasHidreletricasSubmercado = OrderedDict()
cadastroUsinasTermicasSubmercado = OrderedDict()
for sbm in submercados
    submercado = SubmercadoConfigData(sbm["NOME"],sbm["CODIGO"], sbm["CUSTO_DEFICIT"], sbm["DEMANDA"])
    push!(lista_submercados,submercado)
    mapa_nome_SBM[sbm["NOME"]] = submercado
    mapa_codigo_SBM[sbm["CODIGO"]] = submercado
    cadastroUsinasHidreletricasSubmercado[sbm["CODIGO"]] = []
    cadastroUsinasTermicasSubmercado[sbm["CODIGO"]] = []
end

#SISTEMA
#sist = dict["SISTEMA"]
#sistema = SystemConfigData(sist["CUSTO_DEFICIT"], sist["DEMANDA"])
#println(sistema)


@info "Lendo arquivo de rede elétrica"

dicionario_codigo_barra = OrderedDict()
# BARRAS
barras = dict["BARRAS"]
lista_barras = []
lista_barras_sem_slack = []
lista_barras_slack = []
mapaCodigoBarra = OrderedDict()
for barra in barras
    objeto = BarraConfig()
    objeto.codigo = barra["CODIGO"]
    for it in range(1, caso.n_iter)
        for no in lista_total_de_nos
            objeto.potenciaGerada[it, no.codigo] = barra["GERACAO"][1]
            objeto.potenciaLiquida[it, no.codigo] = barra["GERACAO"][1]
        end
    end
    objeto.carga = barra["CARGA"]
    objeto.area = barra["AREA"]
    lista_estado_operacao = barra["ESTADODEOPERACAO"]
    for (est,elemento) in enumerate(lista_estado_operacao)
        objeto.estadoDeOperacao[est] = elemento 
    end
    objeto.tipo = barra["TIPO"]
    push!(lista_barras,objeto)
    dicionario_codigo_barra[objeto.codigo] = objeto
    if objeto.tipo == 2
        push!(lista_barras_slack, objeto)
    else
        push!(lista_barras_sem_slack, objeto)
    end
    mapaCodigoBarra[objeto.codigo] = objeto
end

# BARRAS
linhas = dict["LINHAS"]
lista_linhas = []
for (contador,linha) in enumerate(linhas)
    objeto = LinhaConfig()
    objeto.de = dicionario_codigo_barra[linha["DE"]] 
    objeto.para = dicionario_codigo_barra[linha["PARA"]] 
    objeto.indice = linha["N_CIRCUITOS"]
    objeto.X = linha["REATANCIA"]
    objeto.Capacidade = linha["CAPACIDADE"]
    lista_estado_operacao = linha["ESTADODEOPERACAO"]
    for (est,elemento) in enumerate(lista_estado_operacao)
        objeto.estadoDeOperacao[est] = elemento 
    end
    objeto.codigo = contador
    objeto.defasador = linha["DEFASADOR"]
    push!(lista_linhas,objeto)
    contador = contador + 1
end
#println(lista_linhas)

mapa_nomeUSINA_codigoBARRA = OrderedDict()
mapa_codigoBARRA_nomeUSINA = OrderedDict()

# UTEs
usinas = dict["UTEs"]
lista_utes = []
mapa_nome_UTE = OrderedDict()
for usi in usinas
    usina = UTEConfigData(usi["NOME"],usi["GTMIN"], usi["GTMAX"], usi["CUSTO_GERACAO"], dicionario_codigo_barra[usi["BARRA"]], usi["CODIGO"] )
    push!(lista_utes,usina)
    mapa_nome_UTE[usi["NOME"]] = usina
    mapa_nomeUSINA_codigoBARRA[usi["NOME"]] = usi["BARRA"]
    mapa_codigoBARRA_nomeUSINA[usi["BARRA"]] = usi["NOME"]
    push!(cadastroUsinasTermicasSubmercado[usi["SUBMERCADO"]],usina)
end
#println(lista_utes)


# UHEs
usinas = dict["UHEs"]
lista_uhes = []
mapa_nome_UHE = OrderedDict()

for usi in usinas
    usina = UHEConfigData(usi["NOME"],usi["JUSANTE"],usi["GHMIN"], usi["GHMAX"], usi["TURBMAX"], usi["VOLUME_MINIMO"], usi["VOLUME_MAXIMO"], usi["VOLUME_INICIAL"], dicionario_codigo_barra[usi["BARRA"]], usi["CODIGO"], usi["PRODT"], usi["POSTO"])
    push!(lista_uhes,usina)
    mapa_nome_UHE[usi["NOME"]] = usina
    mapa_nomeUSINA_codigoBARRA[usi["NOME"]] = usi["BARRA"]
    mapa_codigoBARRA_nomeUSINA[usi["BARRA"]] = usi["NOME"]
    push!(cadastroUsinasHidreletricasSubmercado[usi["SUBMERCADO"]], usina)
end
#println(lista_uhes)

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
#println(mapa_montantesUsina)

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
CSV.write("saidas/PDD/eco/df_uhes.csv", df_eco_hidro)
CSV.write("saidas/PDD/eco/df_utes.csv", df_eco_termo)
CSV.write("saidas/PDD/eco/df_submercados.csv", df_eco_submercado)
CSV.write("saidas/PDD/eco/df_RHQ.csv", def_restr_RHQ)

