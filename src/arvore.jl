
include("LeituraEntrada.jl")

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
    #println("estagio: ", periodo.estagio)
    mapa_periodos[i] = periodo
end

for no in lista_total_de_nos
    #println(" codigo: ", no.codigo, " periodo: ", no.periodo)
    push!(mapa_periodos[no.periodo].nos, no)
end
df_arvore = DataFrame(NO_PAI = Int[], NO = Int[], Abertura = [] , PER = Int[], VAZAO = Float64[], PROB = Float64[])

function printa_nos(no)
    for elemento in no.filhos
        println("codigo: ", elemento.codigo, " periodo: ", elemento.periodo, " codigo_intero: ", elemento.index, " pai: ", elemento.pai.codigo)
        push!(df_arvore, (NO_PAI = elemento.pai.codigo, NO = elemento.codigo, Abertura = elemento.index, PER = elemento.periodo,  VAZAO = 0, PROB = 0))
        printa_nos(elemento)
    end
end


println("codigo: ", no1.codigo, " periodo: ", no1.periodo, " codigo_intero: ", no1.index, " pai: ", no1.pai)
push!(df_arvore, (NO = no1.codigo, PER = no1.periodo, Abertura = no1.index, NO_PAI = no1.pai, VAZAO = 0, PROB = 0))
printa_nos(no1)

println(df_arvore)
CSV.write("CenariosSemanais/arvore_julia.csv", df_arvore)