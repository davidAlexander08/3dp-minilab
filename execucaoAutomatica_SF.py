import json
import subprocess

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
##########################################
caminho_arvores = [ "Caso_SF_Final_TOL001\\A_25x3x2Simetrico\\" ]#"Caso_SF_Final_TOL001\\A_200x1x1_Kmeans\\",  "Caso_SF_Final_TOL001\\A_300x1x1_Kmeans\\",]
#"Caso_SF_Final_TOL001\\Pente\\",  "Caso_SF_Final_TOL001\\A_25x3x2\\",  "Caso_SF_Final_TOL001\\A_100x1x1_Kmeans\\",
#  "Caso_SF_Final_TOL001\\A_25x3x2Simetrico\\",  "Caso_SF_Final_TOL001\\A_50x1x1_Kmeans\\" ,"Caso_SF_Final_TOL001\\Vassoura\\", 
#"Caso_SF_Final_TOL001\\A_25x2x2\\",  "Caso_SF_Final_TOL001\\Determ\\",   "Caso_SF_Final_TOL001\\A_25x2x2Simetrico\\" ] 


mapa_caminho_cortes ={
    "Caso_SF_Final_TOL001\\A_25x3x2\\": "Final_TOL001\\A_25x3x2\\KMeansAssimetricoProbPente\\saidas\\PDD\\oper\\",
    "Caso_SF_Final_TOL001\\A_25x3x2Simetrico\\": "Final_TOL001\\A_25x3x2\\KMeansSimetricoProbQuadPente\\saidas\\PDD\\oper\\",
    "Caso_SF_Final_TOL001\\A_25x2x2\\": "Final_TOL001\\A_25x2x2\\KMeansAssimetricoProbPente\\saidas\\PDD\\oper\\",
    "Caso_SF_Final_TOL001\\A_25x2x2Simetrico\\": "Final_TOL001\\A_25x2x2\\KMeansSimetricoProbQuadPente\\saidas\\PDD\\oper\\",
    "Caso_SF_Final_TOL001\\A_100x1x1_Kmeans\\":"Final_TOL001\\A_100x1x1\\KMeansPente\\saidas\\PDD\\oper\\",
    "Caso_SF_Final_TOL001\\A_200x1x1_Kmeans\\":"Final_TOL001\\A_200x1x1\\KMeansPente\\saidas\\PDD\\oper\\",
    "Caso_SF_Final_TOL001\\A_300x1x1_Kmeans\\":"Final_TOL001\\A_300x1x1\\KMeansPente\\saidas\\PDD\\oper\\",
    "Caso_SF_Final_TOL001\\A_50x1x1_Kmeans\\":"Final_TOL001\\A_50x1x1\\KMeansPente\\saidas\\PDD\\oper\\",
    "Caso_SF_Final_TOL001\\A_25x1x1_Kmeans\\":"Final_TOL001\\A_25x1x1\\KMeansPente\\saidas\\PDD\\oper\\",
    "Caso_SF_Final_TOL001\\A_5x1x1_Kmeans\\":"Final_TOL001\\A_5x1x1\\KMeansPente\\saidas\\PDD\\oper\\",
    "Caso_SF_Final_TOL001\\Determ\\":   "Final_TOL001\\Detrm\\saidas\\PDD\\oper\\",
    "Caso_SF_Final_TOL001\\Vassoura\\": "Final_TOL001\\Vassoura\\KMeansAssimetricoProbPente\\saidas\\PDD\\oper\\",
    "Caso_SF_Final_TOL001\\Pente\\": "Final_TOL001\\Pente\\saidas\\PDD\\oper\\",
}
mapa_caminho_avaliacao = {
    "Caso_SF_Final_TOL001\\A_25x3x2\\":          ["Determ\\","Determ_06\\","Determ_08\\","Determ_12\\","Determ_14\\","Pente\\"],
    "Caso_SF_Final_TOL001\\A_25x3x2Simetrico\\": ["Determ\\","Determ_06\\","Determ_08\\","Determ_12\\","Determ_14\\","Pente\\"],
    "Caso_SF_Final_TOL001\\A_25x2x2\\":          ["Determ\\","Determ_06\\","Determ_08\\","Determ_12\\","Determ_14\\","Pente\\"],
    "Caso_SF_Final_TOL001\\A_25x2x2Simetrico\\": ["Determ\\","Determ_06\\","Determ_08\\","Determ_12\\","Determ_14\\","Pente\\"],
    "Caso_SF_Final_TOL001\\A_5x1x1_Kmeans\\": ["Determ\\","Determ_06\\","Determ_08\\","Determ_12\\","Determ_14\\","Pente\\"],
    "Caso_SF_Final_TOL001\\A_25x1x1_Kmeans\\": ["Determ\\","Determ_06\\","Determ_08\\","Determ_12\\","Determ_14\\","Pente\\"],
    "Caso_SF_Final_TOL001\\A_50x1x1_Kmeans\\": ["Determ\\","Determ_06\\","Determ_08\\","Determ_12\\","Determ_14\\","Pente\\"],
    "Caso_SF_Final_TOL001\\A_100x1x1_Kmeans\\":  ["Determ\\","Determ_06\\","Determ_08\\","Determ_12\\","Determ_14\\","Pente\\"],
    "Caso_SF_Final_TOL001\\A_200x1x1_Kmeans\\":  ["Determ\\","Determ_06\\","Determ_08\\","Determ_12\\","Determ_14\\","Pente\\"],
    "Caso_SF_Final_TOL001\\A_300x1x1_Kmeans\\":  ["Determ\\","Determ_06\\","Determ_08\\","Determ_12\\","Determ_14\\","Pente\\"],
    "Caso_SF_Final_TOL001\\Determ\\":            ["Determ\\","Determ_06\\","Determ_08\\","Determ_12\\","Determ_14\\","Pente\\"],
    "Caso_SF_Final_TOL001\\Vassoura\\":          ["Determ\\","Determ_06\\","Determ_08\\","Determ_12\\","Determ_14\\","Pente\\"],
    "Caso_SF_Final_TOL001\\Pente\\":          ["Determ\\","Determ_06\\","Determ_08\\","Determ_12\\","Determ_14\\","Pente\\"],
    }
#mapa_caminho_avaliacao = {
#    "Caso_SF_Final_TOL001\\A_25x3x2\\":["Pente\\"],
#    "Caso_SF_Final_TOL001\\A_25x3x2Simetrico\\":["Pente\\"],
#    "Caso_SF_Final_TOL001\\A_25x2x2\\":["Pente\\"],
#    "Caso_SF_Final_TOL001\\A_25x2x2Simetrico\\":["Pente\\"],
#    "Caso_SF_Final_TOL001\\A_100x1x1_Kmeans\\":["Pente\\"],
#    "Caso_SF_Final_TOL001\\A_50x1x1_Kmeans\\":["Pente\\"],
#    "Caso_SF_Final_TOL001\\Determ\\":["Pente\\"],
#    "Caso_SF_Final_TOL001\\Vassoura\\":["Pente\\"],
#    "Caso_SF_Final_TOL001\\Pente\\":["Pente\\"],
#    }
caminho_base = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\"
caminho_caso = "Capitulo_5\\caso_mini_500Cen_cluster_semanais\\"
caminho_caso_arvores = "Dissertacao\\"
JSON_PDD = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\PDD\\src\\caminho.json"
json_path = caminho_base+caminho_caso+"dadosEntrada.json"  # <-- Update if needed
julia_script = "PDD\\src\\PDD.jl"
sysimage_path = "PDDApp.dll"  # Update this with your actual sysimage path

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

        with open(JSON_PDD, "r") as file_PDD:
            config_PDD = json.load(file_PDD)
        config_PDD["CAMINHO_CASO"] = caminho_base+caminho_caso
        config_PDD["TOLERANCIA"] = 0.001
        with open(JSON_PDD, "w") as file_PDD:
            json.dump(config_PDD, file_PDD, indent=4)
        print("✅ JSON PDD updated!")


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
        subprocess.run(["julia", f"--sysimage={sysimage_path}", julia_script])
        #subprocess.run(["julia", julia_script])