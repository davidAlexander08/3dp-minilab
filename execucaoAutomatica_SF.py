import json
import subprocess


##########################################
caminho_arvores = [ "Caso_SF\\A_100x1x1\\","Caso_SF\\A_100x1x1_Kmeans\\","Caso_SF\\Vassoura\\", "Caso_SF\\A_25x3x2RedRegress\\", "Caso_SF\\A_25x3x2Simetrico\\", "Caso_SF\\A_25x3x2\\", "Caso_SF\\Determ\\",  ] #
#
#
#

mapa_caminho_cortes ={
    "Caso_SF\\A_25x3x2\\": "revisaoDebora\\A_25x3x2\\KMeansAssimetricoProbPente\\saidas\\PDD\\oper\\",
    "Caso_SF\\A_25x3x2Simetrico\\": "revisaoDebora\\A_25x3x2\\KMeansSimetricoProbQuadPente\\saidas\\PDD\\oper\\",
    "Caso_SF\\A_25x3x2RedRegress\\": "revisaoDebora\\A_25x3x2\\BKAssimetrico\\saidas\\PDD\\oper\\",
    "Caso_SF\\A_50x2x2KMeans\\": "revisaoDebora\\A_50x2x2_S39_255\\KMeansAssimetricoProbPente\\saidas\\PDD\\oper\\",
    "Caso_SF\\A_50x2x2RedRegress\\": "revisaoDebora\\A_50x2x2\\BKAssimetrico\\saidas\\PDD\\oper\\",
    "Caso_SF\\A_100x1x1\\":"GTMIN\\A_100_100_100\\BKAssimetrico\\saidas\\PDD\\oper\\",
    "Caso_SF\\A_100x1x1_Kmeans\\":"GTMIN\\A_100_100_100\\KMeansPente\\saidas\\PDD\\oper\\",
    "Caso_SF\\Determ\\":   "revisaoDebora\\Detrm\\KMeansPente\\saidas\\PDD\\oper\\",
    "Caso_SF\\Vassoura\\": "revisaoDebora\\Vassoura\\KMeansAssimetricoProbPente\\saidas\\PDD\\oper\\",
}
mapa_caminho_avaliacao = {
    "Caso_SF\\A_25x3x2\\":          ["Determ\\","Determ_06\\","Determ_08\\","Determ_12\\","Determ_14\\",],
    "Caso_SF\\A_25x3x2Simetrico\\": ["Determ\\","Determ_06\\","Determ_08\\","Determ_12\\","Determ_14\\",],
    "Caso_SF\\A_25x3x2RedRegress\\":["Determ\\","Determ_06\\","Determ_08\\","Determ_12\\","Determ_14\\",],
    "Caso_SF\\A_50x2x2KMeans\\":    ["Determ\\","Determ_06\\","Determ_08\\","Determ_12\\","Determ_14\\",],
    "Caso_SF\\A_50x2x2RedRegress\\":["Determ\\","Determ_06\\","Determ_08\\","Determ_12\\","Determ_14\\",],
    "Caso_SF\\A_100x1x1\\":         ["Determ\\","Determ_06\\","Determ_08\\","Determ_12\\","Determ_14\\",],
    "Caso_SF\\A_100x1x1_Kmeans\\":  ["Determ\\","Determ_06\\","Determ_08\\","Determ_12\\","Determ_14\\",],
    "Caso_SF\\Determ\\":            ["Determ\\","Determ_06\\","Determ_08\\","Determ_12\\","Determ_14\\",],
    "Caso_SF\\Vassoura\\":          ["Determ\\","Determ_06\\","Determ_08\\","Determ_12\\","Determ_14\\",],
    }
mapa_caminho_avaliacao = {
    "Caso_SF\\A_25x3x2\\":["Pente\\"],
    "Caso_SF\\A_25x3x2Simetrico\\":["Pente\\"],
    "Caso_SF\\A_25x3x2RedRegress\\":["Pente\\"],
    "Caso_SF\\A_50x2x2KMeans\\":["Pente\\"],
    "Caso_SF\\A_50x2x2RedRegress\\":["Pente\\"],
    "Caso_SF\\A_100x1x1\\":["Pente\\"],
    "Caso_SF\\A_100x1x1_Kmeans\\":["Pente\\"],
    "Caso_SF\\Determ\\":["Pente\\"],
    "Caso_SF\\Vassoura\\":["Pente\\"],
    }
caminho_base = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\"
caminho_caso = "Capitulo_5\\caso_mini_500Cen_cluster_semanais\\"
caminho_caso_arvores = "avaliaArvoresRepresentativo\\"
#######################################################################################################################################################################
###########################################
#caminho_arvores = [  "Caso_SF\\A_4x2x1\\", "Caso_SF\\Vassoura\\", "Caso_SF\\A_8x1x1\\"] #"Caso_SF\\A_25x3x2\\",
#mapa_caminho_cortes ={
#    "Caso_SF\\A_4x2x1\\": "A_4x2x1\\KMeansAssimetricoProbPente\\saidas\\PDD\\oper\\",
#    "Caso_SF\\A_8x1x1\\":   "A_8x1x1\\BKAssimetrico\\saidas\\PDD\\oper\\",
#    "Caso_SF\\Vassoura\\":  "Vassoura\\saidas\\PDD\\oper\\",
#}
#mapa_caminho_avaliacao = {
#    "Caso_SF\\A_4x2x1\\": ["Pente_GVZP\\"],#"Deterministico\\","Determ_06\\","Determ_08\\","Determ_12\\",
#    "Caso_SF\\A_8x1x1\\": ["Pente_GVZP\\"],#"Deterministico\\","Determ_06\\","Determ_08\\","Determ_12\\",
#    "Caso_SF\\Vassoura\\":["Pente_GVZP\\"],#"Deterministico\\","Determ_06\\","Determ_08\\","Determ_12\\",
#    }
#caminho_base = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\"
#caminho_caso = "Carmen\\exercicio_27cen_36D\\"
#caminho_caso_arvores = "27_Aberturas_Equiprovavel\\"

    
json_path = caminho_base+caminho_caso+"dadosEntrada.json"  # <-- Update if needed
julia_script = "src\\PDD.jl"

for caminho_arvore in caminho_arvores:
    cortes_externos_path = caminho_base+caminho_caso+caminho_caso_arvores+mapa_caminho_cortes[caminho_arvore]+"cortes_est.csv"
    cortes_externos_path = cortes_externos_path.replace("\\", "/")
    for avaliacao in mapa_caminho_avaliacao[caminho_arvore]:
        new_arvore_path = caminho_base+caminho_caso+caminho_caso_arvores+caminho_arvore+avaliacao+"arvore.csv"
        new_cenarios_path = caminho_base+caminho_caso+caminho_caso_arvores+caminho_arvore+avaliacao+"cenarios.csv"
        new_arvore_path = new_arvore_path.replace("\\", "/")
        new_cenarios_path = new_cenarios_path.replace("\\", "/")
        
        print("EXECUTANDO: ",new_arvore_path )
        print("EXECUTANDO SF: ",cortes_externos_path )
        
        # Step 1: Load and update JSON
        with open(json_path, "r") as file:
            config = json.load(file)
        config["SIMFINAL"] = 1
        config["CAMINHO_ARVORE_EXTERNA"] = new_arvore_path
        config["CAMINHO_VAZAO_EXTERNA"] = new_cenarios_path
        config["CAMINHO_CORTES"] = cortes_externos_path
        with open(json_path, "w") as file:
            json.dump(config, file, indent=4)
        print("✅ JSON updated!")
        # Step 2: Run Julia script
        subprocess.run(["julia", julia_script])