import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.ar_model import AutoReg

# Sua série temporal
serie = [215, 240, 141, 216, 92, 200, 378, 256, 219, 213]

# Ajuste do modelo PAR-P (Aqui, usando o modelo AutoReg para AR)
# Neste caso, consideramos que P=2 (ou seja, um modelo AR(2) para exemplificar)
model = AutoReg(serie, lags=2)
result = model.fit()

# O AIC é automaticamente calculado durante o ajuste
print("AIC:", result.aic)