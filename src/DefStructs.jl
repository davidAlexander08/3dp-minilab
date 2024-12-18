
using SparseArrays

mutable struct BarraConfig
    codigo::Int32
    potenciaGerada::Vector{Float64}
    carga::Vector{Float64}
    estadoDeOperacao::Vector{Int32}
    tipo::Int32
    potenciaLiquida::Vector{Float64}
    area::Int32
    
    # Custom constructor with default values
    function BarraConfig()
        new(0, [0.0], [0.0], [0], 0, [0.0], 0)  # Default values for fields
    end

end




mutable struct LinhaConfig
    de::BarraConfig
    para::BarraConfig
    indice::Int32
    X::Float64
    Capacidade::Vector{Float64}
    defasador::Float64
    estadoDeOperacao::Vector{Int32}
    function LinhaConfig()
        default_barra = BarraConfig()
        new(default_barra, default_barra, 0, 0.0, [0.0], 0.0, [0])  # Default values for fields
    end
end

mutable struct FluxoNasLinhas
    de::BarraConfig
    para::BarraConfig
    anguloBarraDe::Float64
    anguloBarraPara::Float64
    fluxoDePara::Float64
    linhaMatrizSensibilidade::Vector{Float64}
    RHS::Float64
    linha::LinhaConfig
    # Constructor with default values
    function FluxoNasLinhas()
        default_barra = BarraConfig()  # Assuming BarraConfig has a default constructor
        default_linha = LinhaConfig()
        new(default_barra, default_barra, 0.0, 0.0, 0.0, [0], 0.0, default_linha)
    end
end

mutable struct IlhaConfig
    codigo::Int32
    slack::BarraConfig
    barras::Vector{BarraConfig}
    linhas::Vector{LinhaConfig}
    matrizSusceptancia::Union{SparseMatrixCSC{Float64, Int}, Nothing}
    mapaSusceptanciaDiagonalPrincipal::Union{SparseMatrixCSC{Float64, Int}, Nothing}
    matrizIncidencia::Union{SparseMatrixCSC{Float64, Int}, Nothing}
    fluxo_linhas::Vector{FluxoNasLinhas}
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

struct CaseData
    n_iter::Int32
    n_est::Int32
    n_term::Int32
    n_uhes::Int32
    estrutura_arvore::Vector
end


struct UTEConfigData
    nome::String
    gtmin::Float64
    gtmax::Float64
    custo_geracao::Float64
    barra::BarraConfig
end

struct UHEConfigData
    nome::String
    downstream::String #Jusante
    ghmin::Float64
    ghmax::Float64
    turbmax::Float64
    vmin::Float64
    vmax::Float64
    v0::Float64
    barra::BarraConfig
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


