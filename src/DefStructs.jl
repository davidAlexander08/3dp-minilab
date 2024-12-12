
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


