
using SparseArrays

mutable struct BarraConfig
    codigo::Int32
    potenciaGerada::Float64
    carga::Float64
    estadoDeOperacao::Int32
    tipo::Int32
    potenciaLiquida::Float64
    area::Int32
    
    # Custom constructor with default values
    function BarraConfig()
        new(0, 0.0, 0.0, 0, 0, 0.0, 0)  # Default values for fields
    end

end




mutable struct LinhaConfig
    de::BarraConfig
    para::BarraConfig
    indice::Int32
    X::Float64
    MVAR::Float64
    defasador::Float64
    function LinhaConfig()
        default_barra = BarraConfig()
        new(default_barra, default_barra, 0, 0.0, 0.0, 0.0)  # Default values for fields
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


