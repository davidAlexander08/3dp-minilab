import json
import subprocess

caminho_arvores = [ "Pente_GVZP\\", "Pente_8cen\\", "A_2_2_2\\", "A_4_2_1\\" ] 
caminho_arvores = [ "Rodada_Final\\A_125_125_125\\"] 
mapa_caminho_avaliacao = {
    "Pente_GVZP\\":[""],
    "Pente_8cen\\":["BKAssimetrico\\", "KMeansPente\\"],
    "A_2_2_2\\":["BKAssimetrico\\", "KMeansAssimetricoProb\\"],
    "A_2_3_4\\":["BKAssimetrico\\", "KMeansAssimetricoProb\\"],
    "A_4_2_1\\":["BKAssimetrico\\", "KMeansAssimetricoProb\\"],
    "Rodada_Final\\A_125_125_125\\":["BKAssimetrico\\"],
    }
caminho_base = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\"
caminho_caso = "Capitulo_5\\caso_mini_500Cen_cluster_semanais\\"
caminho_caso_arvores = "avaliaArvoresRepresentativo\\"

#caminho_caso = "Carmen\\exercicio_27cen_20D\\"
#caminho_caso_arvores = "27_Aberturas_Equiprovavel\\"
json_path = caminho_base+caminho_caso+"dadosEntrada.json"  # <-- Update if needed
julia_script = "src\\PDD.jl"

for caminho_arvore in caminho_arvores:
    for avaliacao in mapa_caminho_avaliacao[caminho_arvore]:
        new_arvore_path = caminho_base+caminho_caso+caminho_caso_arvores+caminho_arvore+avaliacao+"arvore.csv"
        new_cenarios_path = caminho_base+caminho_caso+caminho_caso_arvores+caminho_arvore+avaliacao+"cenarios.csv"
        new_arvore_path = new_arvore_path.replace("\\", "/")
        new_cenarios_path = new_cenarios_path.replace("\\", "/")
        print("EXECUTANDO: ",new_arvore_path )
        # Step 1: Load and update JSON
        with open(json_path, "r") as file:
            config = json.load(file)
        config["CAMINHO_ARVORE_EXTERNA"] = new_arvore_path
        config["CAMINHO_VAZAO_EXTERNA"] = new_cenarios_path
        with open(json_path, "w") as file:
            json.dump(config, file, indent=4)
        print("✅ JSON updated!")
        # Step 2: Run Julia script
        subprocess.run(["julia", julia_script])