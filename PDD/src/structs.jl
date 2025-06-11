
#using SparseArrays
using DataStructures, DataFrames
mutable struct BarraConfig
    codigo::Int32
    potenciaGerada::Dict{Tuple{Int, Int}, Float64} #varia por nó
    carga::Vector{Float64}
    estadoDeOperacao::Dict{Int, Int}
    tipo::Int32
    potenciaLiquida::Dict{Tuple{Int, Int}, Float64}#varia por nó
    area::Int32
    deficitBarra::Dict{Tuple{Int, Int}, Float64}#varia por nó
    
    # Custom constructor with default values
    function BarraConfig()
        #new(0, [0.0], [0.0], [0], 0, [0.0], 0)  # Default values for fields
        new(0, 
        Dict{Tuple{Int, Int, Int}, Float64}(), 
        [0.0], 
        Dict{Int, Int}(), 
        0,
        Dict{Tuple{Int, Int, Int}, Float64}(), 
        0, 
        Dict{Tuple{Int, Int, Int}, Float64}()
        )  # Default values for fields
    end
end

mutable struct ResultadosOtimizacao
    df_intercambio::DataFrame
    df_balanco_energetico_SIN::DataFrame
    df_balanco_energetico_SBM::DataFrame
    df_eolicas::DataFrame
    df_termicas::DataFrame
    df_hidreletricas::DataFrame
    df_convergencia::DataFrame
    df_cortes::DataFrame
    df_cortes_equivalentes::DataFrame
    df_parcelasCustoPresente::DataFrame
    df_folga_vazmin::DataFrame
    df_folga_MetaVol::DataFrame

    function ResultadosOtimizacao()
        new(
            DataFrame(etapa = String[], iter = Int[], est = Int[], node = Int[], prob = Float64[], SubmercadoDE = Int[], SubmercadoPARA = Int[], Valor = Float64[]),
            DataFrame(etapa = String[], iter = Int[], est = Int[], node = Int[], prob = Float64[], Demanda = Float64[], GT = Float64[], GH = Float64[], EOL = Float64[], Deficit = Float64[], Excesso = Float64[], AFL = Float64[], Vini = Float64[], VolArm = Float64[], Earm = Float64[], Turb = Float64[], Vert = Float64[], CustoPresente = Float64[], CustoFuturo = Float64[]),
            DataFrame(etapa = String[], iter = Int[], est = Int[], node = Int[], prob = Float64[], Submercado = Int[], Demanda = Float64[], GT = Float64[], GH = Float64[], EOL = Float64[], Deficit = Float64[], Excesso = Float64[], AFL = Float64[], Vini = Float64[], VolArm = Float64[], Earm = Float64[], Turb = Float64[], Vert = Float64[], CustoPresente = Float64[], CMO = Float64[]),
            DataFrame(etapa = String[], iter = Int[], est = Int[], node = Int[], prob = Float64[], Submercado = Int[], nome = String[], usina = Int[], generation = Float64[], folgaPositiva = Float64[], folgaNegativa = Float64[]),
            DataFrame(etapa = String[], iter = Int[], est = Int[], node = Int[], prob = Float64[], Submercado = Int[], nome = String[], usina = Int[], generation = Float64[], custo = Float64[], custoTotal = Float64[], GerMin = Float64[], GerMax = Float64[]),
            DataFrame(etapa = String[], iter = Int[], est = Int[], node = Int[], prob = Float64[], Submercado = Int[], nome = String[], usina = Int[], generation = Float64[], VI = Float64[], AFL = Float64[], TURB = Float64[], VERT = Float64[], VF = Float64[]),
            DataFrame(iter = Int[], ZINF = Float64[], ZSUP = Float64[], GAP = Float64[], MIN = Float64[], SEC = Float64[], MIN_TOT = Float64[], SEC_TOT = Float64[]),
            DataFrame(iter = Int[], est = Int[], no = Int[], usina = Int[], Indep = Float64[], Coef = Float64[]),
            DataFrame(iter = Int[], est = Int[], noUso = Int[], usina = String[], Indep = Float64[], Coef = Float64[]),
            DataFrame(etapa = String[], iter = Int[], est = Int[], node = Int[], prob = Float64[], Submercado = Int[], usina = String[], codigo = Int[], geracao = Float64[], Custo = Float64[], CustoPresente = Float64[], CustoPresenteAcum = Float64[]),
            DataFrame(etapa = String[], iter = Int[], est = Int[], node = Int[], prob = Float64[], nome = String[], usina = Int[], Vazmin = Float64[], Qdef = Float64[], FolgaPosit = Float64[], FolgaNeg = Float64[]),
            DataFrame(etapa = String[], iter = Int[], est = Int[], node = Int[], prob = Float64[], nome = String[], usina = Int[], Meta = Float64[], VolF = Float64[], FolgaPosit = Float64[], FolgaNeg = Float64[])
        )
    end
end

mutable struct OtimizacaoConfig
    model::Model
    gt_vars::Dict{Tuple{Int, String, String}, VariableRef}
    gh_vars::Dict{Tuple{Int, String, String}, VariableRef}
    ge_vars::Dict{Tuple{Int, String, String}, VariableRef}
    turb_vars::Dict{Tuple{Int, String, String}, VariableRef}
    vert_vars::Dict{Tuple{Int, String, String}, VariableRef}
    vf_vars::Dict{Tuple{Int, String, String}, VariableRef}
    alpha_vars::Dict{Tuple{Int, String}, VariableRef}
    deficit_vars::Dict{Tuple{Int, String, String}, VariableRef}
    excesso_vars::Dict{Tuple{Int, String, String}, VariableRef}
    intercambio_vars::Dict{Tuple{Int, String, String, String}, VariableRef}
    constraint_dict::Dict{Tuple{Int, String, String}, ConstraintRef}
    constraint_balancDem_dict::Dict{Tuple{Int, String, String}, ConstraintRef}
    folga_positiva_vazmin_vars::Dict{Tuple{Int, String, String}, VariableRef}
    folga_negativa_vazmin_vars::Dict{Tuple{Int, String, String}, VariableRef}
    folga_positiva_volFimMundo_vars::Dict{Tuple{Int, String, String}, VariableRef}
    folga_negativa_volFimMundo_vars::Dict{Tuple{Int, String, String}, VariableRef}
    folga_positiva_eolica_vars::Dict{Tuple{Int, String, String}, VariableRef}
    folga_negativa_eolica_vars::Dict{Tuple{Int, String, String}, VariableRef}

    function OtimizacaoConfig()
        new(
            Model(),  # or pass an optimizer if you like: Model(GLPK.Optimizer)
            Dict(), Dict(), Dict(), Dict(), Dict(), Dict(),
            Dict(), Dict(), Dict(), Dict(),
            Dict(), Dict(),
            Dict(), Dict(), Dict(), Dict(),
            Dict(), Dict()
        )
    end
end




mutable struct LinhaConfig
    de::BarraConfig
    para::BarraConfig
    indice::Int32
    X::Float64
    Capacidade::Vector{Float64}
    defasador::Float64
    estadoDeOperacao::Dict{Int, Int}
    anguloBarraDe::Float64
    anguloBarraPara::Float64
    fluxoDePara::Dict{Tuple{Int, Int}, Float64}
    linhaMatrizSensibilidade::Dict{Int, Vector{Float64}}
    RHS::Dict{Int, Float64}
    coeficienteDemanda::Dict{Int, Float64}
    valorMinimoCapacidade::Dict{Int, Float64}
    codigo::Int32
    function LinhaConfig()
        default_barra = BarraConfig()
        #new(default_barra, default_barra, 0, 0.0, [0.0], 0.0, [0])  # Default values for fields
        new(default_barra, 
        default_barra, 
        0, 
        0.0, 
        [0.0], 
        0.0, 
        Dict{Int,Int}(), 
        0, 
        0, 
        Dict{Tuple{Int, Int, Int}, Float64}(), 
        Dict{Int, Vector{Float64}}(), 
        Dict{Int, Float64}(), 
        Dict{Int, Float64}(), 
        Dict{Int, Float64}(),
        0)  # Default values for fields
        
    end
end

#mutable struct FluxoNasLinhas
#    de::BarraConfig
#    para::BarraConfig
#    anguloBarraDe::Float64
#    anguloBarraPara::Float64
#    fluxoDePara::Dict{Tuple{Int, Int, Int}, Float64}
#    linhaMatrizSensibilidade::Vector{Float64}
#    RHS::Float64
#    linha::LinhaConfig
#    violado::Bool
#    coeficienteDemanda::Float64
#    # Constructor with default values
#    function FluxoNasLinhas()
#        default_barra = BarraConfig()  # Assuming BarraConfig has a default constructor
#        default_linha = LinhaConfig()
#        #new(default_barra, default_barra, 0.0, 0.0, 0.0, [0], 0.0, default_linha, false)
#        new(default_barra, default_barra, 0.0, 0.0, Dict{Tuple{Int, Int, Int}, Float64}(), [0], 0.0, default_linha, false, 0.0)
#    end
#end

#mutable struct IlhaConfig
#    codigo::Int32
#    slack::BarraConfig
#    barras::Vector{BarraConfig}
#    linhas::Vector{LinhaConfig}
#    matrizSusceptancia::Dict{Int, Union{SparseMatrixCSC{Float64, Int}, Nothing}}
#    matrizIncidencia::Dict{Int, Union{SparseMatrixCSC{Float64, Int}, Nothing}}
#    barrasAtivas::Dict{Int, Vector{BarraConfig}} #Chave EST
#    barrasNaoAtivas::Dict{Int, Vector{BarraConfig}} #Chave EST
#    linhasAtivas::Dict{Int, Vector{LinhaConfig}} #Chave EST
#    linhasNaoAtivas::Dict{Int, Vector{LinhaConfig}} #Chave EST
#
#    #mapaCodigoBarra::Dict{Int,BarraConfig}
#    function IlhaConfig()
#        default_barra = BarraConfig()  # Assuming BarraConfig has a default constructor
#        default_linha = LinhaConfig()
#        new(0,
#        default_barra, 
#        [default_barra], 
#        [default_linha], 
#        Dict{Int, Union{SparseMatrixCSC{Float64, Int}, Nothing}}(), 
#        Dict{Int, Union{SparseMatrixCSC{Float64, Int}, Nothing}}(),   
#        Dict{Int, BarraConfig}(),
#        Dict{Int, BarraConfig}(),
#        Dict{Int, LinhaConfig}(),
#        Dict{Int, LinhaConfig}()
#        )
#        #default_dict)
#    end
#end

mutable struct SubmercadoConfigData
    nome::String
    codigo::Int32
    deficit_cost::Float64
    demanda::Vector{Float64}
    function SubmercadoConfigData()
        new(
            "",
            0,
            0,
            [0]
        )  
    end
end

mutable struct no
    codigo::Int32
    periodo::Int32
    index::Int32
    pai::Any
    filhos::Vector{Any}
end

mutable struct tipo_periodo
    estagio::Int32
    nos::Vector
end

mutable struct CaseData
    n_iter::Int32
    n_iter_min::Int32
    n_est::Int32
    n_term::Int32
    n_uhes::Int32
    Rest_Canal_Term::Int32
    Rest_Canal_Hid::Int32
    Rest_Bal_Hid::Int32
    Rest_Hid::Int32
    Rest_Limites_Fluxo::Int32
    Rest_Ton_Toff_Term::Int32
    Rest_Ton_Toff_Hid::Int32
    RT::Int32
    Graficos::Int32
    function CaseData()
        new(0,0,0,0,0,0,0,0,0,0,0,0,0,0) 
    end
end



mutable struct UTEConfigData
    nome::String
    gmin::Float64
    gmax::Float64
    custo_geracao::Float64
    codigo::Int32
    function UTEConfigData()
        new(
        "",
        0,
        0,
        0,
        0
        ) 
    end
end

mutable struct UHEConfigData
    nome::String
    jusante::String #Jusante
    gmin::Float64
    gmax::Float64
    turbmax::Float64
    vmin::Float64
    vmax::Float64
    v0::Float64
    codigo::Int32
    prodt::Float64
    posto::Int32
    function UHEConfigData()
        new(
        "",
        "",
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0
        ) 
    end
end

mutable struct EOLConfigData
    nome::String
    posto::Int32
    gmin::Float64
    gmax::Float64
    codigo::Int32
    function EOLConfigData()
        new(
        "",
        0,
        0,
        0,
        0,
        ) 
    end
end