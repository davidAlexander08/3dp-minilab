import json
import subprocess







##########################################################################

caminho_arvores = [ "Deterministico\\", "Vassoura\\"]#"Pente_GVZP\\",  "A_4x2x1\\","A_2x2x2\\", "A_8x1x1\\", "A_2x3x4\\", ] # 
#caminho_arvores = [ "A_2x2x2\\","A_4x2x1\\","A_2x3x4\\",] # "A_2x3x4\\",
#caminho_arvores = [ "Rodada_Final\\A_125_125_125\\"] 
mapa_caminho_avaliacao = {
    "Pente_GVZP\\":[""],
    "Deterministico\\":[""],
    "Vassoura\\":[""],
    #"A_2x2x2\\":["KMeansSimetricoProbQuadPente\\"],
    #"A_2x3x4\\":["KMeansSimetricoProbQuadPente\\"],
    "A_2x3x4\\":["BKAssimetrico\\", "KMeansAssimetricoProbPente\\", "KMeansSimetricoProbQuadPente\\"],
    "A_4x2x1\\":["BKAssimetrico\\", "KMeansAssimetricoProbPente\\"],
    #"A_4x2x1\\":["KMeansSimetricoProbQuadPente\\"],
    }
caminho_base = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\"
caminho_caso = "Carmen\\exercicio_27cen_36D\\"
caminho_caso_arvores = "128_Aberturas_Equiprovavel\\"
caminho_caso_arvores = "27_Aberturas_Equiprovavel\\"
##########################################
caminho_arvores = ["revisaoDebora\\A_100x1x1_42_20\\", "revisaoDebora\\A_100x1x1_55_20\\", "revisaoDebora\\A_100x1x1_55_137\\", 
                    "revisaoDebora\\A_100x1x1_84_137\\", "revisaoDebora\\A_100x1x1_254_20\\" ] 
caminho_arvores = [ "revisaoDebora\\Detrm\\"] 
mapa_caminho_avaliacao = {
    "Pente_GVZP\\":[""],
    "revisaoDebora\\A_100x1x1_42_20\\":["KMeansPente\\"],
    "revisaoDebora\\A_100x1x1_55_20\\":["KMeansPente\\"],
    "revisaoDebora\\A_100x1x1_55_137\\":["KMeansPente\\"],
    "revisaoDebora\\A_100x1x1_84_137\\":["KMeansPente\\"],
    "revisaoDebora\\A_100x1x1_254_20\\":["KMeansPente\\"],
    "revisaoDebora\\Detrm\\":["KMeansPente\\"],
    }
caminho_base = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\"
caminho_caso = "Capitulo_5\\caso_mini_500Cen_cluster_semanais\\"
caminho_caso_arvores = "avaliaArvoresRepresentativo\\"



##########################################################################

caminho_arvores = ["Pente_GVZP\\",  "Academicos\\A_4x4x2\\","Academicos\\A_2x2x8\\", "Academicos\\A_8x2x2\\", "Academicos\\A_4x6x3\\", "Academicos\\A_32x1x1\\"] #  
#caminho_arvores = [ "A_2x2x2\\","A_4x2x1\\","A_2x3x4\\",] # "A_2x3x4\\",
#caminho_arvores = [ "Rodada_Final\\A_125_125_125\\"] 
mapa_caminho_avaliacao = {
    "Pente_GVZP\\":[""],
    "Academicos\\A_32x1x1\\":["BKAssimetrico\\", "KMeansPente\\"],
    "Academicos\\A_4x4x2\\":["BKAssimetrico\\", "KMeansAssimetricoProbPente\\", "NeuralGas\\"],
    #"A_2x2x2\\":["KMeansSimetricoProbQuadPente\\"],
    #"A_2x3x4\\":["KMeansSimetricoProbQuadPente\\"],
    "Academicos\\A_2x2x8\\":["BKAssimetrico\\", "KMeansAssimetricoProbPente\\", "NeuralGas\\"],
    "Academicos\\A_8x2x2\\":["BKAssimetrico\\", "KMeansAssimetricoProbPente\\", "NeuralGas\\"],
    "Academicos\\A_4x6x3\\":["KMeansAssimetricoProbPente\\"],
    #"A_4x2x1\\":["KMeansSimetricoProbQuadPente\\"],
    } 
caminho_base = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\"
caminho_caso = "Academico\\exercicio_1D\\"
caminho_caso_arvores = "128_Aberturas_Equiprovavel_FimMundo\\"
#caminho_caso_arvores = "27_Aberturas_Equiprovavel_2\\"



##########################################################################

caminho_arvores = ["27cen\\10Perc\\Pente_Gerado\\", "27cen\\10Perc\\A_2x2x2\\", "27cen\\10Perc\\A_4x2x1\\", "27cen\\10Perc\\A_8x1x1\\"]
#caminho_arvores = [ "A_2x2x2\\","A_4x2x1\\","A_2x3x4\\",] # "A_2x3x4\\",
#caminho_arvores = [ "Rodada_Final\\A_125_125_125\\"] 
mapa_caminho_avaliacao = {
    "27cen\\10Perc\\Pente_Gerado\\":[""],
    "Pente_GVZP_2cen\\":[""],
    "Pente_GVZP_4cen\\":[""],
    "Pente_GVZP_8cen\\":[""],
    "Pente_GVZP_27cen\\":[""],
    "Arvore_2_2_2\\":[""],
    "Arvore_4_2_2\\":[""],
    "Arvore_8_2_2\\":[""],
    "Arvore_27_2_2\\":[""],
    "ArvorePerc_2\\":["10Perc\\", "3Perc\\", "5Perc\\", "10Perc\\"],
    "ArvorePerc_27\\":["10Perc\\", "3Perc\\", "5Perc\\", "10Perc\\"],
    "27cen\\10Perc\\A_2x2x2\\":["BKAssimetrico\\", "KMeansAssimetricoProbPente\\"],
    "27cen\\10Perc\\A_4x2x1\\":["BKAssimetrico\\", "KMeansAssimetricoProbPente\\"],
    "27cen\\10Perc\\A_8x1x1\\":["BKAssimetrico\\", "KMeansPente\\"],
    } 
caminho_base = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\"
caminho_caso = "Academico\\exercicio_1D_PenteArvore\\"
caminho_caso_arvores = ""
#caminho_caso_arvores = "27_Aberturas_Equiprovavel_2\\"

##########################################################################
caminho_arvores = ["Pente_GVZP\\", "A_4x4x2\\", "A_8x2x2\\", "A_2x2x8\\"]

mapa_caminho_avaliacao = {
    "Pente_GVZP\\":[""],
    "A_4x4x2\\":["BKAssimetrico\\", "KMeansAssimetricoProbPente\\", "KMeansSimetricoProbQuadPente\\","NeuralGas\\"],
    "A_2x2x8\\":["BKAssimetrico\\", "KMeansAssimetricoProbPente\\", "KMeansSimetricoProbQuadPente\\","NeuralGas\\"],
    "A_8x2x2\\":["BKAssimetrico\\", "KMeansAssimetricoProbPente\\", "KMeansSimetricoProbQuadPente\\","NeuralGas\\"],
    "27cen\\10Perc\\A_8x1x1\\":["BKAssimetrico\\", "KMeansPente\\"],
    } 
caminho_base = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\"
caminho_caso = "Academico_Dissertacao\\exercicio_5D\\"
caminho_caso_arvores = ""
#caminho_caso_arvores = "27_Aberturas_Equiprovavel_2\\"




##########################################
caminho_arvores = ["Eol_dem\\Pente_GVZP\\", "Eol_dem\\A_4x4x2\\" , "Eol_cen\\Pente_GVZP\\", "Eol_cen\\A_4x4x2\\" ] #,
# 
#"64Folhas\\A_8x4x2\\", "64Folhas\\A_4x4x4\\", "64Folhas\\A_2x4x8\\",
 
mapa_caminho_avaliacao = {
    "Eol_dem\\Pente_GVZP\\":[""],
    "Eol_dem\\A_4x4x2\\" :["BKAssimetrico\\", "KMeansAssimetricoProbPente\\", "KMeansSimetricoProbQuadPente\\" ],#
    "Eol_cen\\Pente_GVZP\\":[""],
    "Eol_cen\\A_4x4x2\\" :["BKAssimetrico\\", "KMeansAssimetricoProbPente\\", "KMeansSimetricoProbQuadPente\\" ],#
    "64Folhas\\A_8x4x2\\":["BKAssimetrico\\", "BKSimetrico\\", "KMeansAssimetricoProb\\", "KMeansSimetricoProbQuad\\", "NeuralGas\\"],
    "64Folhas\\A_4x4x4\\":["BKAssimetrico\\", "BKSimetrico\\", "KMeansAssimetricoProb\\", "KMeansSimetricoProbQuad\\", "NeuralGas\\"],
    "64Folhas\\A_2x4x8\\":["BKAssimetrico\\", "BKSimetrico\\", "KMeansAssimetricoProb\\", "KMeansSimetricoProbQuad\\", "NeuralGas\\"],
    "16Folhas\\A_2x2x4\\":["BKAssimetrico\\", "BKSimetrico\\", "KMeansAssimetricoProb\\", "KMeansAssimetricoProbPente\\", "KMeansAssimetricoProbRegress\\","KMeansSimetricoProbQuad\\", "KMeansSimetricoProbQuadPente\\", "KMeansSimetricoProbQuadRegress\\","NeuralGas\\"],
    "16Folhas\\A_4x2x2\\":["BKAssimetrico\\", "BKSimetrico\\", "KMeansAssimetricoProb\\", "KMeansAssimetricoProbPente\\", "KMeansAssimetricoProbRegress\\","KMeansSimetricoProbQuad\\", "KMeansSimetricoProbQuadPente\\", "KMeansSimetricoProbQuadRegress\\","NeuralGas\\"],
    "16Folhas\\A_16_1_1\\":["BKAssimetrico\\", "KMeansPente\\"],
    "8Folhas\\A_2x2x2\\":["BKAssimetrico\\", "BKSimetrico\\", "KMeansAssimetricoProb\\", "KMeansAssimetricoProbPente\\", "KMeansAssimetricoProbRegress\\","KMeansSimetricoProbQuad\\", "KMeansSimetricoProbQuadPente\\", "KMeansSimetricoProbQuadRegress\\","NeuralGas\\"],
    "8Folhas\\A_4x2x1\\":["BKAssimetrico\\", "BKSimetrico\\", "KMeansAssimetricoProb\\", "KMeansAssimetricoProbPente\\", "KMeansAssimetricoProbRegress\\","KMeansSimetricoProbQuad\\", "KMeansSimetricoProbQuadPente\\", "KMeansSimetricoProbQuadRegress\\","NeuralGas\\"],
    "8Folhas\\A_8x1x1\\":["BKAssimetrico\\", "KMeansPente\\"],
    "8Folhas\\":["A_8x4x2\\", "A_4x4x4\\", "A_2x4x8\\"],
    "Reduzida_Inicio\\":[""],
    "Reduzida_Meio\\":[""],
    "Reduzida_Meio_VarNegativa\\":[""],
    "Reduzida_Meio_VarPositiva\\":[""],
    "Reduzida_MeioMediaNegativaVarCte\\":[""],
    "Reduzida_MeioMediaPositivaVarCte\\":[""],
    "Reduzida_Meio_VarNegativa25\\":[""],
    "Reduzida_Meio_VarPositiva25\\":[""],
    "GTMIN\\A_25_75_150_Teste\\":["KMeansAssimetricoProbPenteSemente13\\"],
    }
caminho_base = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\"
caminho_caso = "Academico_Dissertacao\\exercicio_5D_EOL\\"
caminho_caso_arvores = ""


#########################################
caminho_arvores = ["Determ_Teste\\"] #,"A_1x1x32\\", 
# 
#"64Folhas\\A_8x4x2\\", "64Folhas\\A_4x4x4\\", "64Folhas\\A_2x4x8\\",
 
mapa_caminho_avaliacao = {
    "Determ_Teste\\" :["BKAssimetrico\\", "KMeansAssimetricoProbPente\\"],#
    }
caminho_base = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\"
caminho_caso = "Capitulo_5\\caso_mini_500Cen_cluster_semanais\\"
caminho_caso_arvores = "Dissertacao\\Final_TOL001\\"


JSON_PDD = "C:\\Users\\testa\\Documents\\git\\3dp-minilab\\PDD\\src\\caminho.json"

json_path = caminho_base+caminho_caso+"dadosEntrada.json"  # <-- Update if needed
julia_script = "PDD\\src\\PDD.jl"

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
        config_PDD["TOLERANCIA"] = 0.00001
        with open(JSON_PDD, "w") as file_PDD:
            json.dump(config_PDD, file_PDD, indent=4)
        print("✅ JSON PDD updated!")

            
        with open(json_path, "r") as file:
            config = json.load(file)
            config["CAMINHO_ARVORE_EXTERNA"] = new_arvore_path
            config["CAMINHO_VAZAO_EXTERNA"] = new_cenarios_path
            config["SIMFINAL"] = 0
        with open(json_path, "w") as file:
            json.dump(config, file, indent=4)
        print("✅ JSON updated!")
        # Step 2: Run Julia script
        subprocess.run(["julia", julia_script])