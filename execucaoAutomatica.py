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
##########################################################################
caminho_arvores = ["A_4x4x2_L\\", "A_8x2x2_L\\", "A_2x2x8_L\\"] #"A_32x1x1_Caminho_1Est\\",]# "Pente_GVZP\\", "1Perc\\", "5Perc\\", "10Perc\\", "50Perc\\", "75Perc\\"]#"A_2x2x8\\"]#"Pente_GVZP\\", "A_4x4x2\\", "A_8x2x2\\",, "A_2x4x4\\"]#, "A_32x1x1_S226\\", "A_32x1x1_S280\\", "A_32x1x1_S394\\", ]#, "A_4x6x3\\"] #]  "A_32x1x1\\"

mapa_caminho_avaliacao = {
    "Pente_GVZP\\":[""],
    "A_2x4x4\\":["BKAssimetrico\\","KMeansAssimetricoProbPente\\",  "KMeansSimetricoProbQuadPente\\"],
    "A_4x4x2\\":["BKAssimetrico\\", "KMeansAssimetricoProbPente\\", "KMeansSimetricoProbQuadPente\\"],
    "A_2x2x8\\":["BKAssimetrico\\"],#, "KMeansAssimetricoProbPente\\", "KMeansSimetricoProbQuadPente\\"
    "A_8x2x2\\":["BKAssimetrico\\", "KMeansAssimetricoProbPente\\", "KMeansSimetricoProbQuadPente\\"],
    "A_4x6x3\\":["KMeansAssimetricoProbPente\\"],
    "A_32x1x1\\":["NeuralGas\\"],
    "A_32x1x1_S42\\":["KMeansPente\\"],
    "A_32x1x1_S84\\":["KMeansPente\\"],
    "A_32x1x1_S226\\":["KMeansPente\\"],
    "A_32x1x1_S280\\":["KMeansPente\\"],
    "A_32x1x1_S394\\":["KMeansPente\\"],
    "A_32x1x1_S17\\":["KMeansPente\\"],
    "A_32x1x1_S25\\":["KMeansPente\\"],
    "1Perc\\":[""],
    "5Perc\\":[""],
    "10Perc\\":[""],
    "25Perc\\":[""],
    "50Perc\\":[""],
    "75Perc\\":[""],
    "A_4x4x2_L\\":["KMeansAssimetricoProbPente\\", "KMeansAssimetricoLinear\\"],
    "A_2x2x8_L\\":[ "KMeansAssimetricoProbPente\\", "KMeansAssimetricoLinear\\"],
    "A_8x2x2_L\\":["KMeansAssimetricoProbPente\\", "KMeansAssimetricoLinear\\"],
    "A_32x1x1_Caminho_1Est\\":["KMeansPente\\","KMeansAssimetricoProbPente\\" ],
    } 
caminho_base = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\" 
caminho_caso = "Academico_Dissertacao\\exercicio_36D\\"
caminho_caso_arvores = ""
#caminho_caso_arvores = "27_Aberturas_Equiprovavel_2\\"



##########################################
caminho_arvores = ["Eol_dem\\Pente_GVZP\\", "Eol_dem\\A_4x4x2\\", "Eol_cen\\Pente_GVZP\\", "Eol_cen\\A_4x4x2\\"] #,
# 
#"64Folhas\\A_8x4x2\\", "64Folhas\\A_4x4x4\\", "64Folhas\\A_2x4x8\\",
 
mapa_caminho_avaliacao = {
    "Eol_dem\\Pente_GVZP\\":[""],
    "Eol_dem\\A_4x4x2\\" :["BKAssimetrico\\", "KMeansAssimetricoProbPente\\", "KMeansSimetricoProbQuadPente\\" ],#
    "Eol_cen\\Pente_GVZP\\":[""],
    "Eol_cen\\A_4x4x2\\" :["BKAssimetrico\\", "KMeansAssimetricoProbPente\\", "KMeansSimetricoProbQuadPente\\" ],#
    "A_2x2x8\\" :["BKAssimetrico\\", "KMeansAssimetricoProbPente\\", "KMeansSimetricoProbQuadPente\\" ],#
    "A_8x2x2\\" :["BKAssimetrico\\", "KMeansAssimetricoProbPente\\", "KMeansSimetricoProbQuadPente\\" ],#
    "A_4x6x3\\" :["KMeansAssimetricoProbPente\\"],#
    "A_32x1x1\\" :["KMeansPente\\"],#
    }
caminho_base = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\"
caminho_caso = "Academico_Dissertacao\\exercicio_36D_EOL\\"
caminho_caso_arvores = ""


##########################################
caminho_arvores = ["Determ_Teste\\"] #,"A_1x1x32\\", 
# 
#"64Folhas\\A_8x4x2\\", "64Folhas\\A_4x4x4\\", "64Folhas\\A_2x4x8\\",
 
mapa_caminho_avaliacao = {
    "Eol_dem\\Pente_GVZP\\":[""],
    "Eol_dem\\A_4x4x2\\" :["BKAssimetrico\\", "KMeansAssimetricoProbPente\\", "KMeansSimetricoProbQuadPente\\" ],#
    "Eol_dem\\A_4x4x2\\" :["BKAssimetrico\\", "KMeansAssimetricoProbPente\\", "KMeansSimetricoProbQuadPente\\" ],#
    "Eol_cen\\Pente_GVZP\\":[""],
    "Eol_cen\\A_4x4x2\\" :["BKAssimetrico\\", "KMeansAssimetricoProbPente\\", "KMeansSimetricoProbQuadPente\\" ],#
    "A_2x2x8\\" :["BKAssimetrico\\", "KMeansAssimetricoProbPente\\", "KMeansSimetricoProbQuadPente\\" ],#
    "A_8x2x2\\" :["BKAssimetrico\\", "KMeansAssimetricoProbPente\\", "KMeansSimetricoProbQuadPente\\" ],#
    "A_1x1x32\\" :["KMeansAssimetricoProbPente\\"],#
    "A_4x6x3\\" :["KMeansAssimetricoProbPente\\"],#
    "A_32x1x1\\" :["KMeansPente\\"],#
    "Determ_Teste\\" :["BKAssimetrico\\"],#
    }
caminho_base = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\"
caminho_caso = "Capitulo_5\\caso_mini_500Cen_cluster_semanais\\"
caminho_caso_arvores = "Dissertacao\\Final_TOL001\\"


##########################################################################
caminho_arvores = [ "Eol_cen\\A_25x3x2\\", "Eol_dem\\A_25x3x2\\"]# "A_8x2x2_KM\\", "A_2x2x8\\", "A_2x2x8_KM\\"] #"A_32x1x1_Caminho_1Est\\",]# "Pente_GVZP\\", "1Perc\\", "5Perc\\", "10Perc\\", "50Perc\\", "75Perc\\"]#"A_2x2x8\\"]#"Pente_GVZP\\", "A_4x4x2\\", "A_8x2x2\\",, "A_2x4x4\\"]#, "A_32x1x1_S226\\", "A_32x1x1_S280\\", "A_32x1x1_S394\\", ]#, "A_4x6x3\\"] #]  "A_32x1x1\\"
mapa_caminho_avaliacao = {
    "Pente_GVZP\\":[""],
    "Eol_cen\\A_4x4x2\\" :["KMeansAssimetricoProbPente\\" ],#
    "Eol_cen\\A_25x3x2\\":["KMeansAssimetricoProbPente\\"],#, "KMeansAssimetricoProbPente\\", "KMeansSimetricoProbQuadPente\\"],
    "Eol_dem\\A_25x3x2\\":["KMeansAssimetricoProbPente\\"],#, "KMeansAssimetricoProbPente\\", "KMeansSimetricoProbQuadPente\\"],
    "A_8x2x2\\":["KMeansAssimetricoProbPente\\"],#, "KMeansAssimetricoProbPente\\", "KMeansSimetricoProbQuadPente\\"],
    "A_2x2x8\\":["KMeansAssimetricoProbPente\\"],#, "KMeansAssimetricoProbPente\\", "KMeansSimetricoProbQuadPente\\"],
    "A_4x4x2_KM\\":["KMeansAssimetricoProbPente\\"],#, "KMeansAssimetricoProbPente\\", "KMeansSimetricoProbQuadPente\\"],
    "A_2x2x8_KM\\":["KMeansAssimetricoProbPente\\"],#, "KMeansAssimetricoProbPente\\", "KMeansSimetricoProbQuadPente\\"],
    "A_8x2x2_KM\\":["KMeansAssimetricoProbPente\\"],#, "KMeansAssimetricoProbPente\\", "KMeansSimetricoProbQuadPente\\"],
    } 
caminho_base = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\" 
caminho_caso = "Capitulo_5\\cenarios_500Cen_cluster_semanais_EOL\\EOL_4\\"
caminho_caso_arvores = ""
#caminho_caso_arvores = "27_Aberturas_Equiprovavel_2\\"


JSON_PDD = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\PDD\\src\\caminho.json"

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
        with open(JSON_PDD, "r") as file_PDD:
            config_PDD = json.load(file_PDD)
        config_PDD["CAMINHO_CASO"] = caminho_base+caminho_caso
        config_PDD["TOLERANCIA"] = 0.01
        with open(JSON_PDD, "w") as file_PDD:
            json.dump(config_PDD, file_PDD, indent=4)
        print("✅ JSON PDD updated!")

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