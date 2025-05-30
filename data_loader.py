import numpy as np
from config import NA, NT, NF, F, A, T

def load_data():
    # Conjuntos
    sets = {
        "A": A,
        "T": T,
        "F": F
    }

    # Datos dummy para pruebas
    da = np.full((NA, NT), 10)  # Demanda hídrica constante (10 m3)
    lla = np.zeros((NA, NT))   # Lluvia efectiva (0 en esta fase)
    eta = 0.8                  # Eficiencia fija
    cW = {"pozo": 100, "red": 120}  # Costos de agua
    beta = {a: 500 for a in A}  # Penalización por no cultivar
    cD = 300  # Penalización por déficit hídrico

    params = {
        "da": da,
        "lla": lla,
        "eta": eta,
        "cW": cW,
        "beta": beta,
        "cD": cD
    }

    return sets, params
