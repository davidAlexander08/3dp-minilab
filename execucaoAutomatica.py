import json
import subprocess
#from julia.api import Julia
#import os 
#os.environ["JULIA_SYSIMAGE"] = "C:\\your\\path\\PDDAppSysimage.dll"
#jl = Julia(compiled_modules=False)
#from julia import Main


caminho_arvores = [ "Pente_GVZP\\", "Pente_8cen\\", "A_2_2_2\\", "A_4_2_1\\" ] 
#caminho_arvores = [ "Rodada_Final\\A_125_125_125\\"] 
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

caminho_caso = "Carmen\\exercicio_27cen_20D\\"
caminho_caso_arvores = "27_Aberturas_Equiprovavel\\"
##########################################
caminho_arvores = ["GTMIN\\A_25_75_150_Teste\\"] 
#caminho_arvores = [ "Rodada_Final\\A_125_125_125\\"] 
mapa_caminho_avaliacao = {
    "Pente_GVZP\\":[""],
    "GTMIN\\A_25_75_150_Teste\\":["KMeansAssimetricoProbPenteSemente13\\"],
    "GTMIN\\A_25_125_250\\":["KMeansAssimetricoProb\\"],
    "GTMIN\\A_100_100_100\\":["BKAssimetrico\\"],
    "GTMIN\\A_100_100_100\\":["KMeansPente\\"],
    "A_4_2_1\\":["BKAssimetrico\\", "KMeansAssimetricoProb\\"],
    "Rodada_Final\\A_125_125_125\\":["BKAssimetrico\\"],
    }
caminho_base = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\"
caminho_caso = "Capitulo_5\\caso_mini_500Cen_cluster_semanais\\"
caminho_caso_arvores = "avaliaArvoresRepresentativo\\"
##########################################
caminho_arvores = ["Pente_GVZP\\", "Academicos\\A_4x4x2\\",
                   "Academicos\\A_2x2x8\\", "Academicos\\A_4x6x3\\",
                   "Academicos\\A_8x2x2\\", "Academicos\\A_32x1x1\\" ] 
# 

mapa_caminho_avaliacao = {
    "Pente_GVZP\\":[""],
    "Academicos\\A_2x2x8\\":["BKAssimetrico\\", "KMeansAssimetricoProb\\", "KMeansAssimetricoProbRegress\\","KMeansAssimetricoProbPente\\", "KMeansSimetricoProbQuad\\", "KMeansSimetricoProbQuadPente\\","KMeansSimetricoProbQuadRegress\\","NeuralGas\\"],
    "Academicos\\A_4x4x2\\":["BKAssimetrico\\", "KMeansAssimetricoProb\\", "KMeansAssimetricoProbRegress\\","KMeansAssimetricoProbPente\\", "KMeansSimetricoProbQuad\\", "KMeansSimetricoProbQuadPente\\","KMeansSimetricoProbQuadRegress\\","NeuralGas\\"],
    "Academicos\\A_4x6x3\\":["BKAssimetrico\\", "KMeansAssimetricoProb\\", "KMeansAssimetricoProbRegress\\","KMeansAssimetricoProbPente\\", "KMeansSimetricoProbQuad\\", "KMeansSimetricoProbQuadPente\\","KMeansSimetricoProbQuadRegress\\","NeuralGas\\"],
    "Academicos\\A_8x2x2\\":["BKAssimetrico\\", "KMeansAssimetricoProb\\", "KMeansAssimetricoProbRegress\\","KMeansAssimetricoProbPente\\", "KMeansSimetricoProbQuad\\", "KMeansSimetricoProbQuadPente\\","KMeansSimetricoProbQuadRegress\\","NeuralGas\\"],
    "Academicos\\A_32x1x1\\":["BKAssimetrico\\", "KMeansPente\\"],
    "16Folhas\\A_16x1x1\\":["BKAssimetrico\\", "KMeansPente\\"],
    "8Folhas\\A_2x2x2\\":["BKAssimetrico\\", "BKSimetrico\\","KMeansAssimetricoProb\\", "KMeansAssimetricoProbPente\\", "KMeansAssimetricoProbRegress\\","KMeansSimetricoProbQuad\\", "KMeansSimetricoProbQuadPente\\", "KMeansSimetricoProbQuadRegress\\","NeuralGas\\"],
    "8Folhas\\A_4x2x1\\":["BKAssimetrico\\", "BKSimetrico\\","KMeansAssimetricoProb\\", "KMeansAssimetricoProbPente\\", "KMeansAssimetricoProbRegress\\","KMeansSimetricoProbQuad\\", "KMeansSimetricoProbQuadPente\\", "KMeansSimetricoProbQuadRegress\\","NeuralGas\\"],
    "8Folhas\\A_8x1x1\\":["BKAssimetrico\\", "KMeansPente\\"],
    "GTMIN\\A_25_75_150_Teste\\":["KMeansAssimetricoProbPenteSemente13\\"],
    }
caminho_base = "C:\\Users\\david.alexander\\Documents\\git\\3dp-minilab\\"
caminho_caso = "Capitulo_5\\exercicio_27cen_5D\\"
caminho_caso_arvores = "128_Aberturas_Equiprovavel_Pfundo\\"
##########################################
caminho_arvores = ["revisaoDebora\\Vassoura\\", "revisaoDebora\\A_25x4x2\\",
                   "revisaoDebora\\A_50x2x2\\", "revisaoDebora\\A_60x3x2\\",
                   "revisaoDebora\\A_100x2x1\\"] 
caminho_arvores = ["revisaoDebora\\A_25x3x2\\"] 

mapa_caminho_avaliacao = {
    "revisaoDebora\\Vassoura\\":["BKAssimetrico\\", "KMeansAssimetricoProb\\", "KMeansAssimetricoProbPente\\", "KMeansSimetricoProbQuadPente\\"],
    "revisaoDebora\\A_25x4x2\\":["BKAssimetrico\\", "KMeansAssimetricoProb\\", "KMeansAssimetricoProbPente\\", "KMeansSimetricoProbQuadPente\\"],
    "revisaoDebora\\A_50x2x2\\":["BKAssimetrico\\", "KMeansAssimetricoProb\\", "KMeansAssimetricoProbPente\\", "KMeansSimetricoProbQuadPente\\"],
    "revisaoDebora\\A_60x3x2\\":["BKAssimetrico\\", "KMeansAssimetricoProb\\", "KMeansAssimetricoProbPente\\", "KMeansSimetricoProbQuadPente\\"],
    "revisaoDebora\\A_25x3x2\\":["BKAssimetrico\\", ],
    "revisaoDebora\\A_100x1x1_55_137\\":["KMeansPente\\",],
    "revisaoDebora\\A_100x1x1_84_137\\":["KMeansPente\\",],
    "revisaoDebora\\A_100x1x1_254_20\\":["KMeansPente\\",],
    "revisaoDebora\\A_25x4x2_13_96\\":["KMeansAssimetricoProbPente\\", "KMeansSimetricoProbQuadPente\\"],
    "revisaoDebora\\A_25x4x2_75_33\\":["KMeansAssimetricoProbPente\\", "KMeansSimetricoProbQuadPente\\"],
    "revisaoDebora\\A_25x4x2_254_20\\":["KMeansAssimetricoProbPente\\", "KMeansSimetricoProbQuadPente\\"],
    "revisaoDebora\\A_25x4x2_267_547\\":["KMeansAssimetricoProbPente\\", "KMeansSimetricoProbQuadPente\\"],
    "revisaoDebora\\A_50x2x2_S137_255\\":["KMeansAssimetricoProbPente\\", "KMeansSimetricoProbQuadPente\\"],
    "revisaoDebora\\A_50x2x2_S4220\\":["KMeansAssimetricoProbPente\\", "KMeansSimetricoProbQuadPente\\"],
    "revisaoDebora\\A_50x2x2_S5520\\":["KMeansAssimetricoProbPente\\", "KMeansSimetricoProbQuadPente\\"],
    }
caminho_base = "C:\\Users\\david.alexander\\Documents\\git\\3dp-minilab\\"
caminho_caso = "Capitulo_5\\caso_mini_500Cen_cluster_semanais\\"
caminho_caso_arvores = "avaliaArvoresRepresentativo\\"


json_path = caminho_base+caminho_caso+"dadosEntrada.json"  # <-- Update if needed
julia_script = "PDD\\src\\PDD.jl"
sysimage_path = "PDDApp.dll"  # Update this with your actual sysimage path


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
        #subprocess.run(["julia", julia_script])
        #PDDApp.executaModelo()
        subprocess.run(["julia", f"--sysimage={sysimage_path}", julia_script])
        #subprocess.run(["julia", f"--sysimage={sysimage_path}", "-e",'include("C:/Users/david.alexander/Documents/git/3dp-minilab/src/PDD.jl"); executaModelo()'])

        #subprocess.run([
        #    "julia", 
        #    "--sysimage", sysimage_path,  # Specify the precompiled sysimage
        #    "-e", "using PDD; PDD.executaModelo()"  # Call the function inside the compiled image
        #])