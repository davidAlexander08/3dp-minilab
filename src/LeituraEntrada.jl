
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

str_caso = "marcato/caso_marcato_deterministico"
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


str_caso = "red_arv_backReduction/2aberturas_ini"
str_caso = "red_arv_backReduction/2aberturas_ini_Cen1"
#str_caso = "red_arv_backReduction/2aberturas_ini_Cen3"
#str_caso = "red_arv_backReduction/2aberturas_ini_Cen4"
str_caso = "red_arv_backReduction/2aberturas_ini_Cen5"
#str_caso = "red_arv_backReduction/2aberturas_ini_Cen2_BK"


#str_caso = "Teste_Fluxo_IEEE_5_Barras"
CONFIG_PATH = str_caso*"/dadosEntrada.json"
PATH_VAZOES = str_caso*"/vazao.csv"
PATH_PROBABILIDADES = str_caso*"/probabilidades.csv"
PATH_HORAS = str_caso*"/horas.csv"



@info "Lendo arquivo de configuração $(CONFIG_PATH)"
dict = JSON.parsefile(CONFIG_PATH; use_mmap=false)


@info "Lendo arquivo de vazoes $(PATH_VAZOES)"
dat_vaz = CSV.read(PATH_VAZOES, DataFrame)

@info "Lendo arquivo de probabilidades $(PATH_PROBABILIDADES)"
dat_prob = CSV.read(PATH_PROBABILIDADES, DataFrame)
#print(dat_vaz[(dat_vaz.NOME_UHE .== 1) .& (dat_vaz.PERIODO .== 1), :])
#print(dat_vaz[(dat_vaz.NOME_UHE .== 1) .& (dat_vaz.PERIODO .== 1), "VAZAO"][1])

@info "Lendo arquivo de horas $(PATH_HORAS)"
dat_horas = CSV.read(PATH_HORAS, DataFrame)


caso = CaseData()
caso.n_iter = dict["MAX_ITERACOES"]
caso.n_est = dict["ESTAGIOS"]
rede_eletrica = dict["REDE"]
caso.estrutura_arvore = dict["ARVORE"]
include("arvore.jl")

#SISTEMA
sist = dict["SISTEMA"]
sistema = SystemConfigData(sist["CUSTO_DEFICIT"], sist["DEMANDA"])
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
end
#println(lista_utes)


# UHEs
usinas = dict["UHEs"]
lista_uhes = []
mapa_nome_UHE = OrderedDict()

for usi in usinas
    usina = UHEConfigData(usi["NOME"],usi["JUSANTE"],usi["GHMIN"], usi["GHMAX"], usi["TURBMAX"], usi["VOLUME_MINIMO"], usi["VOLUME_MAXIMO"], usi["VOLUME_INICIAL"], dicionario_codigo_barra[usi["BARRA"]], usi["CODIGO"], usi["PRODT"])
    push!(lista_uhes,usina)
    mapa_nome_UHE[usi["NOME"]] = usina
    mapa_nomeUSINA_codigoBARRA[usi["NOME"]] = usi["BARRA"]
    mapa_codigoBARRA_nomeUSINA[usi["BARRA"]] = usi["NOME"]
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
println(mapa_montantesUsina)
