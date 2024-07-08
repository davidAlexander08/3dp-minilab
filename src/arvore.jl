
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
mapa_periodos = Dict()
for i in 1:length(caso.estrutura_arvore)+1
    periodo = tipo_periodo(i,[])
    #println("estagio: ", periodo.estagio)
    mapa_periodos[i] = periodo
end

for no in lista_total_de_nos
    #println(" codigo: ", no.codigo, " periodo: ", no.periodo)
    push!(mapa_periodos[no.periodo].nos, no)
end

#for per in mapa_periodos
#    println("per: ", per[2].estagio)
#    for no in per[2].nos
#        print(no.codigo, " ")
#    end
#    println(" ")
#end




function printa_nos(no)
    for elemento in no.filhos
        println("codigo: ", elemento.codigo, " periodo: ", elemento.periodo, " codigo_intero: ", elemento.index, " pai: ", elemento.pai.codigo)
        printa_nos(elemento)
    end
end
println("codigo: ", no1.codigo, " periodo: ", no1.periodo, " codigo_intero: ", no1.index, " pai: ", no1.pai)
#printa_nos(no1)