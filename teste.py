import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.ar_model import AutoReg
import plotly.express as px
import plotly.graph_objects as go
import os
import numpy as np
import scipy.stats as stats
from scipy.stats import ks_2samp
from scipy.stats import chisquare
from scipy.stats import wasserstein_distance

# Define empirical CDF functions
def ecdf(x_vals, probs):
    """Returns an ECDF function based on given values and their cumulative probabilities."""
    def func(x):
        idx = np.searchsorted(x_vals, x, side="right") - 1
        return 0.0 if idx < 0 else probs[idx]
    return np.vectorize(func)


mapa_AO =   {5:1/5      ,     10:1/6,    20:7/30,    25:1/5,    40:1/5}
mapa_Cen2 = {5:0.366666 ,     20:7/30,     25:1/5,    40:1/5}
mapa_Cen1 = {5:1/5      ,     10:1/6,     25:0.43333,    40:1/5}
mapa_Cen3 = {10:0.36666 ,     20:7/30,     25:1/5,    40:1/5}
mapa_Cen4 = {5:1/5      ,     10:1/6,      20:0.43333,    40:1/5}
mapa_Cen5 = {5:1/5      ,     10:1/6,     20:7/30,    25:0.4}
    #cdf_AO = np.cumsum(list(mapa_AO.values()))
    #cdf_Cen2 = np.cumsum(list(mapa_Cen2.values()))

def printaDistWasserstein(mapa_AO, mapa_Cen2, texto):
    suporte = sorted(set(mapa_AO.keys()).union(set(mapa_Cen2.keys())))
    prob_AO = np.array([mapa_AO.get(x, 0) for x in suporte])
    prob_Cen2 = np.array([mapa_Cen2.get(x, 0) for x in suporte])
    prob_AO /= prob_AO.sum()
    prob_Cen2 /= prob_Cen2.sum()
    dist_wasserstein = wasserstein_distance(suporte, suporte, prob_AO, prob_Cen2)
    print(f"Distância de Wasserstein: {dist_wasserstein}")



printaDistWasserstein(mapa_AO, mapa_Cen1, " Exclui 1")
printaDistWasserstein(mapa_AO, mapa_Cen2, " Exclui 2")
printaDistWasserstein(mapa_AO, mapa_Cen3, " Exclui 3")
printaDistWasserstein(mapa_AO, mapa_Cen4, " Exclui 4")
printaDistWasserstein(mapa_AO, mapa_Cen5, " Exclui 5")


def printaChiQuadrado(mapa_AO, mapa_Cen2, texto):
    chaves_comuns = [k for k in mapa_AO.keys() if k in mapa_Cen2]
    observado = np.array([mapa_AO[k] for k in chaves_comuns])
    esperado = np.array([mapa_Cen2[k] for k in chaves_comuns])
    observado /= observado.sum()
    esperado /= esperado.sum()
    chi2_stat, p_value = chisquare(observado, esperado)
    print(texto + f" Estatística qui-quadrado: {chi2_stat:.4f}")
    print(texto + f" Valor-p: {p_value:.4f}")

printaChiQuadrado(mapa_AO, mapa_Cen1, " Exclui 1")
printaChiQuadrado(mapa_AO, mapa_Cen2, " Exclui 2")
printaChiQuadrado(mapa_AO, mapa_Cen3, " Exclui 3")
printaChiQuadrado(mapa_AO, mapa_Cen4, " Exclui 4")
printaChiQuadrado(mapa_AO, mapa_Cen5, " Exclui 5")

def printaKS_manual(mapa_AO, mapa_Cen2, analise):
    all_values = sorted(set(mapa_AO.keys()).union(set(mapa_Cen2.keys())))
    cdf_AO_manual = []
    cdf_Cen2_manual = []
    for value in all_values:
        cdf_AO_manual.append(sum(mapa_AO[k] for k in mapa_AO if k <= value))
        cdf_Cen2_manual.append(sum(mapa_Cen2[k] for k in mapa_Cen2 if k <= value))
    ks_statistic = np.max(np.abs(np.array(cdf_AO_manual) - np.array(cdf_Cen2_manual)))
    print(analise+" KS Statistic: "+ str(ks_statistic))


printaKS_manual(mapa_AO, mapa_Cen1, "Exclui Cen 1")
printaKS_manual(mapa_AO, mapa_Cen2, "Exclui Cen 2")
printaKS_manual(mapa_AO, mapa_Cen3, "Exclui Cen 3")
printaKS_manual(mapa_AO, mapa_Cen4, "Exclui Cen 4")
printaKS_manual(mapa_AO, mapa_Cen5, "Exclui Cen 5")


# Given data points
vector1 = [5, 10, 20, 25, 40] 
prob1 = [1/5, 1/6, 7/30, 1/5, 1/5]

vector2 = [5, 20, 25, 40]   
prob2 = [0.3666, 7/30, 1/5, 1/5]


vector3 = [5, 10, 25, 40]   
prob3 = [1/5, 1/6, 0.4333, 1/5]

vector4 = [10, 20, 25, 40]  
prob4 = [0.3666, 7/30, 1/5, 1/5]

vector5 = [5, 10, 20, 40]  
prob5 = [1/5, 1/6, 0.4333, 1/5]

vector6 = [5, 10, 20, 25]  
prob6 = [1/5, 1/6, 7/30, 0.4]


cdf1 = np.cumsum(prob1)
cdf2 = np.cumsum(prob2)
# Step 2: Align the data points
all_values = sorted(set(vector1 + vector2))
cdf1_extended = np.interp(all_values, vector1, cdf1, left=0, right=1)
cdf2_extended = np.interp(all_values, vector2, cdf2, left=0, right=1)
print(cdf1_extended)
# Step 3: Calculate the maximum difference
ks_statistic = np.max(np.abs(cdf1_extended - cdf2_extended))

print(f"KS Statistic Teste: {ks_statistic}")


def printaKS(prob1, prob2, vector1, vector2):
    prob1 /= np.sum(prob1)
    prob2 /= np.sum(prob2)
    ecdf1 = ecdf(vector1, np.cumsum(prob1))
    ecdf2 = ecdf(vector2, np.cumsum(prob2))
    x_common = np.union1d(vector1, vector2)
    ks_statistic = np.max(np.abs(ecdf1(x_common) - ecdf2(x_common)))
    D, p_value = ks_2samp(vector1, vector2)
    print(f"KS Statistic: {ks_statistic}")
    print(f"P-value (from SciPy KS test): {p_value}")


printaKS(prob1, prob2, vector1, vector2)
printaKS(prob1, prob3, vector1, vector3)
printaKS(prob1, prob4, vector1, vector4)
printaKS(prob1, prob5, vector1, vector5)
printaKS(prob1, prob6, vector1, vector6)

exit(1)


# Create figure
fig = go.Figure()

fig.add_trace(go.Scatter(x=vector1, y=cum_prob1, mode="lines+markers", name="Vector 1 (Normal)", line_shape='hv'))
fig.add_trace(go.Scatter(x=vector2, y=cum_prob2, mode="lines+markers", name="Vector 2 (Uniform)", line_shape='hv'))

# Update layout
fig.update_layout(
    title="Cumulative Distribution Function (CDF)",
    xaxis_title="Value",
    yaxis_title="Cumulative Probability",
    template="plotly_white"
)

# Folder to save the image
output_folder = "teste"
os.makedirs(output_folder, exist_ok=True)
output_path = os.path.join(output_folder, "cumulative_distribution.png")

# Save the figure as PNG
fig.write_image(output_path, format="png", scale=2)

exit(1)
# Sua série temporal
serie = [215, 240, 141, 216, 92, 200, 378, 256, 219, 213]

# Ajuste do modelo PAR-P (Aqui, usando o modelo AutoReg para AR)
# Neste caso, consideramos que P=2 (ou seja, um modelo AR(2) para exemplificar)
model = AutoReg(serie, lags=2)
result = model.fit()

# O AIC é automaticamente calculado durante o ajuste
print("AIC:", result.aic)
