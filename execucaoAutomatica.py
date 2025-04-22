import json
import subprocess

# Paths
caminho_base = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\"
caminho_caso = "Carmen\\exercicio_27cen_3D\\"
json_path = caminho_base+caminho_caso+"dadosEntrada.json"  # <-- Update if needed
julia_script = "src\\PDD.jl"

caminho_caso_arvores = "3Aberturas_Equiprovavel\\"
caminho_arvores = ["A_2_2_2_Teste\\"]
caminho_avaliacao = ["KMeansAssimetricoLinear\\", "KMeansAssimetricoLinearQuad\\", "KMeansAssimetricoPacote\\",
                    "KMeansAssimetricoProb\\", "KMeansAssimetricoProbQuad\\", "KMeansSimetricoLinear\\",
                    "KMeansSimetricoLinearQuad\\", "KMeansSimetricoPacote\\", "KMeansSimetricoProb\\", 
                    "KMeansSimetricoProbQuad\\"]
for caminho_arvore in caminho_arvores:
    for avaliacao in caminho_avaliacao:
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