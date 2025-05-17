
#using SparseArrays
using DataStructures 
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
end



struct contexto
    estagio::Int32
    codigo_no::Int32
    iteracao::Int32
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

struct SystemConfigData
    deficit_cost::Float64
    demanda::Vector{Float64}
end

mutable struct CaseData
    n_iter::Int32
    n_iter_min::Int32
    n_est::Int32
    n_term::Int32
    n_uhes::Int32
    estrutura_arvore::Vector
    function CaseData()
        new(0,0, 0,0,[]) 
    end
end


struct UTEConfigData
    nome::String
    gmin::Float64
    gmax::Float64
    custo_geracao::Float64
    barra::BarraConfig
    codigo::Int32
end

struct UHEConfigData
    nome::String
    jusante::String #Jusante
    gmin::Float64
    gmax::Float64
    turbmax::Float64
    vmin::Float64
    vmax::Float64
    v0::Float64
    barra::BarraConfig
    codigo::Int32
    prodt::Float64
    posto::Int32
end

struct Forward
    ger_hidr_fw::Vector
    vf_hidr_fw::Vector
    vi_hidr_fw::Vector
    turb_hidr_fw::Vector
    vert_hidr_fw::Vector
    ger_term_fw::Vector
    ger_def_fw::Vector
end

struct Backward

end


