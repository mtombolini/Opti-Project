import numpy as np
from config import NA, NT, NF, F, A, T

def load_data():
    # Conjuntos
    R = ["surco", "goteo", "aspersión"]
    sets = {
        "A": A,
        "T": T,
        "F": F,
        "R": R
    }

    # Datos dummy para pruebas
    da = np.full((NA, NT), 10)  # Demanda hídrica constante (10 m3)
    lla = np.zeros((NA, NT))   # Lluvia efectiva (0 en esta fase)
    eta = {(a, r): 0.5 + 0.2 * i for i, r in enumerate(R) for a in A}  # ej: surco=0.5, goteo=0.7, aspersión=0.9
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
