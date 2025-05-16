
include("DefStructs.jl")

using JSON
using CSV
using DataFrames
#using Graphs
using LightGraphs
using SparseArrays
using DataStructures


str_caso = "Dissertacao/apresentacaoCarmen_Gevazp/caso_mini"
#str_caso = "Carmen/caso_mini"
#str_caso = "Carmen/exercicio_27cen"
#str_caso = "Carmen/exercicio_27cen_2D"
#str_caso = "Carmen/exercicio_27cen_3D"
#str_caso = "Carmen/exercicio_27cen_4D_Teste"
##str_caso = "Carmen/exercicio_27cen_4D"
#str_caso = "Carmen/exercicio_27cen_5D"
#str_caso = "Carmen/exercicio_27cen_4D"
##str_caso = "Capitulo_5/caso_mini_500Cen_sorteio_mensais"
str_caso = "Capitulo_5/caso_mini_500Cen_cluster_semanais"
#str_caso = "Carmen/exercicio_27cen_1D"
#str_caso = "Carmen/exercicio_27cen_2D"
#str_caso = "Carmen/exercicio_27cen_3D"
#str_caso = "Carmen/exercicio_27cen_4D_Teste"
#str_caso = "Carmen/exercicio_27cen_1D"
#str_caso = "Carmen/exercicio_27cen_10D"
#str_caso = "Carmen/exercicio_27cen_20D"
#str_caso = "Academico/exercicio_5D" 
str_caso = "Academico/exercicio_1D"
#str_caso = "Academico/exercicio_1D_Debora"
#str_caso = "Carmen/exercicio_27cen_36D"
#str_caso = "Carmen/exercicio_27cen_3D"
##str_caso = "Dissertacao/teste_simples_3est_2A/caso_dissertacao"
#str_caso = "Dissertacao/exercicioDebora/caso_mini"
#str_caso = "Carmen/exercicio_27cen_1D"
CONFIG_PATH = str_caso*"/dadosEntrada.json"
PATH_HORAS = str_caso*"/horas.csv"


#@info "Lendo arquivo de configuração $(CONFIG_PATH)"
dict = JSON.parsefile(CONFIG_PATH; use_mmap=false)



caso = CaseData()
caso.n_iter = dict["MAX_ITERACOES"]
caso.n_est = dict["ESTAGIOS"]
rede_eletrica = dict["REDE"]
limites_intercambio = dict["LIMITES_INTERCAMBIO"]
vazao_minima = dict["VAZAO_MINIMA"]
penalidVazMin = dict["PENALIDADE_VAZAO_MINIMA"]
volume_minimo = dict["VOLUME_MINIMO"]
volume_espera = dict["VOLUME_ESPERA"]
simfinal = dict["SIMFINAL"]
if(simfinal == 1)
    CAMINHO_CORTES = dict["CAMINHO_CORTES"]
    #@info "Lendo arquivo de vazao minima $(PATH_RESTR_VOLUME_MINIMO)"
    dat_cortes_ext = CSV.read(CAMINHO_CORTES, DataFrame)
    cortes_filtrados = filter(row -> row.est == 2, dat_cortes_ext)
    mex_iter_est = maximum(cortes_filtrados.iter)
    caso.n_iter = 1
    #println(dat_cortes_ext)
    println("mex_iter_est: ", mex_iter_est)
    println("EXECUTANDO SIMULACAO FINAL")
end


############ CORTES DA FCF EXTERNA PARA FIM DE MUNDO DO PRIMEIRO ESTÀGIO DOS CORTES
cortes_externos_fim_de_mundo = dict["CORTES_EXTERNOS"]
caminho_cortes_externos_fim_de_mundo = dict["CAMINHO_CORTES_EXTERNOS"]
if(cortes_externos_fim_de_mundo == 1)
    PATH_CORTES_EXTERNOS_FIM_MUNDO = caminho_cortes_externos_fim_de_mundo
    #@info "Lendo arquivo de vazao minima $(PATH_RESTR_VOLUME_MINIMO)"
    dat_cortes_externos_fim_mundo = CSV.read(PATH_CORTES_EXTERNOS_FIM_MUNDO, DataFrame)
    cortes_filtrados = filter(row -> row.est == 1, dat_cortes_externos_fim_mundo)
    mex_iter_est_cortes_externos = maximum(cortes_filtrados.iter)
    println("ENTORU AQUI, MAXITER: ", mex_iter_est_cortes_externos)
end

arvore_externa = dict["ARVORE_EXTERNA"]
caminho_arvore_externa = dict["CAMINHO_ARVORE_EXTERNA"]
vazao_externa = dict["VAZAO_EXTERNA"]
caminho_vazao_externa = dict["CAMINHO_VAZAO_EXTERNA"]
caso.estrutura_arvore = dict["ARVORE"]


if(limites_intercambio == 1)
    PATH_RESTR_INTERCAMBIOS = str_caso*"/restr_limite_Intercambio.csv"
    #@info "Lendo arquivo de intercambios $(PATH_RESTR_INTERCAMBIOS)"
    dat_interc = CSV.read(PATH_RESTR_INTERCAMBIOS, DataFrame)
    #print(dat_interc)
end

if(volume_minimo == 1)
    PATH_RESTR_VOLUME_MINIMO = str_caso*"/restr_vol_min.csv"
    #@info "Lendo arquivo de vazao minima $(PATH_RESTR_VOLUME_MINIMO)"
    dat_volmin = CSV.read(PATH_RESTR_VOLUME_MINIMO, DataFrame)
    #print(dat_volmin)
end

if(volume_espera == 1)
    PATH_RESTR_VOLUME_ESPERA = str_caso*"/restr_vol_max.csv"
    #@info "Lendo arquivo de vazao minima $(PATH_RESTR_VOLUME_ESPERA)"
    dat_volmax = CSV.read(PATH_RESTR_VOLUME_ESPERA, DataFrame)
    #print(dat_volmax)
end


if(vazao_minima == 1)
    PATH_RESTR_VAZAO_MINIMA = str_caso*"/restr_vazao_minima.csv"
    #@info "Lendo arquivo de vazao minima $(PATH_RESTR_VAZAO_MINIMA)"
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
PATH_VAZOES = str_caso*"/cenarios.csv"
PATH_PROBABILIDADES = str_caso*"/probabilidades.csv"
dados_saida = str_caso
#@info "Lendo arquivo de vazoes $(PATH_VAZOES)"
dat_vaz = CSV.read(PATH_VAZOES, DataFrame)

if vazao_externa == 1
    @info "Lendo arquivo de vazoes externas $(caminho_vazao_externa)"
    dat_vaz = CSV.read(caminho_vazao_externa, DataFrame)
    dados_saida = splitdir(caminho_vazao_externa)[1]
end

#@info "Lendo arquivo de horas $(PATH_HORAS)"
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


############# META DE ARMAZENAMENTO DO FIM DE MUNDO
periodos_fim_de_mundo = dict["PERIODOS_FIM_DE_MUNDO"]
restricaoVolumeFimMundo = dict["FIM_DE_MUNDO_VOLUMES"]
if(restricaoVolumeFimMundo == 1)
    PATH_RESTR_META_VOLUME = str_caso*"/restr_meta_armazenamento.csv"
    #@info "Lendo arquivo de vazao minima $(PATH_RESTR_VOLUME_MINIMO)"
    dat_meta_armazenamento = CSV.read(PATH_RESTR_META_VOLUME, DataFrame)
    #print(dat_volmin)
end





#SISTEMA
#sist = dict["SISTEMA"]
#sistema = SystemConfigData(sist["CUSTO_DEFICIT"], sist["DEMANDA"])
#println(sistema)

#@info "Lendo arquivo de probabilidades $(PATH_PROBABILIDADES)"
dat_prob = CSV.read(PATH_PROBABILIDADES, DataFrame)
include("arvore.jl")



#@info "Lendo arquivo de rede elétrica"

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
#mapa_nome_UHE
mapaUsinaProdtAcum = Dict{String, Float64}()
for uhe in lista_uhes
    if !haskey(mapa_montantesUsina, uhe.nome)
        mapa_montantesUsina[uhe.nome] = String[]  # Initialize an empty array if it doesn't exist
    end
    #println("UHE: ", uhe.nome)

    lista_cascata = String[]

    jusante = uhe.jusante
    usina = uhe

    while jusante != ""
        for usi_jus in lista_uhes
            if usi_jus.codigo == parse(Int, usina.jusante)
                #println("UHE JUS: ", usi_jus.nome)
                push!(lista_cascata, usi_jus.nome)
                usina = usi_jus
                jusante = usina.jusante
                break
            end
        end
    end
    prodt_acum = uhe.prodt
    for usi_cascata in lista_cascata
        #println("UHE: ", usi_cascata, " PRODT: ", mapa_nome_UHE[usi_cascata].prodt)
        prodt_acum += mapa_nome_UHE[usi_cascata].prodt
    end
    mapaUsinaProdtAcum[uhe.nome] = prodt_acum
    #println("UHE: ", uhe.nome, " PRODACUM: ", prodt_acum)
end
#exit(1)








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

#println(df_arvore)
#println(dat_vaz)

#for sbm in lista_submercados
#    println(sbm.demanda)
#end
#println("caso.n_est: ", caso.n_est)

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
