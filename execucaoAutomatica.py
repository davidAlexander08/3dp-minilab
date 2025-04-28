import json
import subprocess

# Paths
caminho_base = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\"
caminho_caso = "Carmen\\exercicio_27cen_2D\\"
json_path = caminho_base+caminho_caso+"dadosEntrada.json"  # <-- Update if needed
julia_script = "src\\PDD.jl"

caminho_caso_arvores = "3Aberturas_Equiprovavel\\"
caminho_arvores = ["A_2_2_2\\", "A_4_2_1\\","Pente_8cen\\"]
caminho_avaliacao = ["KMeansAssimetricoLinear\\", "KMeansAssimetricoLinearQuad\\", "KMeansAssimetricoPacote\\",
                    "KMeansAssimetricoProb\\", "KMeansAssimetricoProbQuad\\", "KMeansSimetricoLinear\\",
                    "KMeansSimetricoLinearQuad\\", "KMeansSimetricoPacote\\", "KMeansSimetricoProb\\", 
                    "KMeansSimetricoProbQuad\\"]
caminho_avaliacao = ["BKAssimetrico\\", "BKSimetrico\\", "KMeansAssimetricoProb\\",
                    "KMeansSimetricoProbQuad\\", "NeuralGas\\", "NeuralGasSimetrico\\"]
caminho_avaliacao = ["BKAssimetrico\\", "KMeansAssimetricoProb\\","A_8cen_1\\", "A_8cen_2\\", "A_8cen_3\\", "A_8cen_4\\", "A_8cen_5\\"]
caminho_avaliacao = ["Amostrado_1\\", "Amostrado_2\\","Amotrado_C_1\\", "Amostrado_C_2\\"]
mapa_caminho_avaliacao = {
    "A_2_2_2\\":["BKAssimetrico\\","KMeansAssimetricoProb\\"],
    "A_4_2_1\\":["BKAssimetrico\\","KMeansAssimetricoProb\\"],
    "Pente_8cen\\":["BKAssimetrico\\", "KMeansAssimetricoProb\\","KMeansPente\\", "A_8cen_1\\", "A_8cen_2\\","Amostrado_1\\", "Amostrado_2\\","Amotrado_C_1\\", "Amostrado_C_2\\"],
}


caminho_arvores = ["A_6_2_2\\","A_4_2_3\\","A_2_2_6\\", "Pente_24cen\\", "A_4_2_1\\", "A_2_2_2\\", "Pente_8cen\\"]
mapa_caminho_avaliacao = {
    "A_6_2_2\\":["BKAssimetrico\\","ClusterAssimetrico\\"],
    "A_4_2_3\\":["BKAssimetrico\\","ClusterAssimetrico\\"],
    "A_2_2_6\\":["BKAssimetrico\\","ClusterAssimetrico\\"],
    "Pente_24cen\\":["BKAssimetrico\\","Pente_Amostrado_1\\", "Pente_Amostrado_2\\", "Pente_Amostrado_3\\","Pente_Amostrado_4\\", "Pente_Amostrado_5\\","Pente_modelo_24cen\\"],
    "A_4_2_1\\":["BKAssimetrico\\","ClusterAssimetrico\\"],
    "A_2_2_2\\":["BKAssimetrico\\","ClusterAssimetrico\\"],
    "Pente_8cen\\":["BKAssimetrico\\","Pente_Amostrado_1\\", "Pente_Amostrado_2\\", "Pente_Amostrado_3\\","Pente_Amostrado_4\\", "Pente_Amostrado_5\\","Pente_modelo_8cen\\"],
}



caminho_arvores = ["Deterministico\\",
                    "Vassoura\\",
                    "Outros\\A_2_4_8\\",
                    "Outros\\A_2_10_50\\",
                    "Outros\\A_3_9_45\\",
                    "Outros\\A_5_25_125\\",
                    "Outros\\A_50_50_50\\",
                   ] 
mapa_caminho_avaliacao = {
    "Deterministico\\":[""],
    "Vassoura\\":[""],
    "Outros\\A_2_4_8\\":["BKAssimetrico\\"],
    "Outros\\A_2_10_50\\":["BKAssimetrico\\"],
    "Outros\\A_3_9_45\\":["BKAssimetrico\\"],
    "Outros\\A_5_25_125\\":["BKAssimetrico\\"],
    "Outros\\A_50_50_50\\":["BKAssimetrico\\"],
}
caminho_base = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\"
caminho_caso = "Capitulo_5\\caso_mini_500Cen_cluster_semanais\\"
caminho_caso_arvores = "avaliaArvoresRepresentativo\\"
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