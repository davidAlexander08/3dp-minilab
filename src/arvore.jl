
function percorre_abertura(no_pai, lista_Arvore, periodo, lista_total_de_nos)
    codigo_interno = 1
    lista_filhos = []
    if periodo != length(lista_Arvore)
        periodo += 1
        for i in 1:lista_Arvore[periodo]
            codigo = maximum(codigos)+1
            i_no = no(codigo, no_pai.periodo + 1, codigo_interno, no_pai, [])
            push!(lista_total_de_nos,i_no)
            push!(no_pai.filhos, i_no)
            push!(lista_filhos, i_no)
            push!(codigos, codigo)
            codigo_interno+= 1
            percorre_abertura(i_no, lista_Arvore, periodo,lista_total_de_nos)
        end
    end
end

lista_total_de_nos = []
no1 = no(1, 1, 1, 0, [])
global codigos = [no1.codigo]
push!(lista_total_de_nos, no1)
percorre_abertura(no1, caso.estrutura_arvore, 0, lista_total_de_nos)
mapa_periodos = OrderedDict()
for i in 1:length(caso.estrutura_arvore)+1
    periodo = tipo_periodo(i,[])
    mapa_periodos[i] = periodo
end

for no in lista_total_de_nos
    push!(mapa_periodos[no.periodo].nos, no)
end

df_arvore = DataFrame(NO_PAI = Int[], NO = Int[], Abertura = [] , PER = Int[], PROB = Float64[])

function printa_nos(no)
    for elemento in no.filhos
        #println("codigo: ", elemento.codigo, " periodo: ", elemento.periodo, " codigo_intero: ", elemento.index, " pai: ", elemento.pai.codigo)
        probabilidade = dat_prob[(dat_prob.NO .== elemento.codigo), "PROBABILIDADE"][1]
        push!(df_arvore, (NO_PAI = elemento.pai.codigo, NO = elemento.codigo, Abertura = elemento.index, PER = elemento.periodo,  PROB = probabilidade))
        printa_nos(elemento)
    end
end


#println("codigo: ", no1.codigo, " periodo: ", no1.periodo, " codigo_intero: ", no1.index, " pai: ", no1.pai)
probabilidade = dat_prob[(dat_prob.NO .== no1.codigo), "PROBABILIDADE"][1]
push!(df_arvore, (NO = no1.codigo, PER = no1.periodo, Abertura = no1.index, NO_PAI = no1.pai, PROB = probabilidade))
printa_nos(no1)
#println(df_arvore)
CSV.write("cenarios/CenariosSemanais/arvore_julia.csv", df_arvore)
CSV.write(str_caso*"/arvore_julia.csv", df_arvore)





function getFilhos(no)
    filhos = df_arvore[df_arvore.NO_PAI .== no, :NO]
    return filhos
end


function buscaPai(no)
    pai =  (df_arvore[(df_arvore.NO .== no), "NO_PAI"][1])
    return pai
end

function retornaListaCaminho(no)
    lista = []
    push!(lista,no)
    no_inicial = no
    periodo_no = (df_arvore[(df_arvore.NO .== no), "PER"][1])
    for est in 1:(periodo_no-1)
        pai = buscaPai(no_inicial)
        push!(lista,pai)
        no_inicial = pai
    end
    return lista
end

function montaArvore(no_pai, df_arvore, lista_total_de_nos)
    
    periodo = df_arvore[df_arvore.NO .== no_pai.codigo, :PER][1]  # Extract first element
    codigo_interno = 1
    lista_filhos = []
    #println("pai cod: ", no_pai.codigo)
    filhos = getFilhos(no_pai.codigo)
    for filho in filhos
        no_filho = no(filho, periodo + 1, codigo_interno, no_pai, [])
        push!(lista_total_de_nos, no_filho)
        push!(no_pai.filhos, no_filho)
        push!(lista_filhos, no_filho)
        codigo_interno += 1
        montaArvore(no_filho, df_arvore, lista_total_de_nos)
    end
end

if arvore_externa == 1

    println(caminho_arvore_externa)
    df_arvore = CSV.read(caminho_arvore_externa, DataFrame)
    lista_total_de_nos = []
    no1 = no(1, 1, 1, 0, [])
    push!(lista_total_de_nos, no1)
    montaArvore(no1, df_arvore, lista_total_de_nos)
    println(dat_prob)
    println(df_arvore)
    dat_prob = df_arvore[:, [:NO, :PROB]]
    rename!(dat_prob, :PROB => :PROBABILIDADE)
    println(dat_prob)
    #exit(1)
    mapa_periodos = OrderedDict()
    for est in unique(df_arvore.PER)
        periodo = tipo_periodo(est,[])
        mapa_periodos[est] = periodo
    end
    for no_alvo in lista_total_de_nos
        push!(mapa_periodos[no_alvo.periodo].nos, no_alvo)
    end
end





















mapaProbCondicionalNo = Dict{Int, Float64}()
for no in lista_total_de_nos
    mapaProbCondicionalNo[no.codigo] = 1
    for no_caminho in retornaListaCaminho(no.codigo)
        mapaProbCondicionalNo[no.codigo] *= (dat_prob[(dat_prob.NO .== no_caminho), "PROBABILIDADE"][1])
    end
end
#println(mapaProbCondicionalNo)
