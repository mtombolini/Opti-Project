import numpy as np
from config import NA, NT, NF, F, A, T

def load_data():
    # Conjuntos
    R = ["surco", "goteo", "aspersión"]
    S = ["arcilla", "franco", "arenoso"]
    s_index = {s: i for i, s in enumerate(S)}
    sets = {
        "A": A,
        "T": T,
        "F": F,
        "R": R,
        "S": S
    }

    sa = {a: S[a % len(S)] for a in A}  # asignación dummy para pruebas

    # Datos dummy para pruebas
    da = np.zeros((NA, NT, len(S)))
    for a in range(NA):
        for t in range(NT):
            for s in range(len(S)):
                da[a, t, s] = 8 + 3 * s + a % 3  # mayor variabilidad en demanda
    lla = np.random.uniform(0, 5, size=(NA, NT))   # Lluvia efectiva simulada
    eta = {(a, r): 0.5 + 0.2 * i for i, r in enumerate(R) for a in A}  # ej: surco=0.5, goteo=0.7, aspersión=0.9
    cW = {"pozo": 30, "red": 35, "tanque": 5}  # Costos de agua ajustados
    beta = {a: 3000 for a in A}  # Penalización por no cultivar aumentada
    cD = 500  # Penalización por déficit hídrico ajustada

    Qmax = {(f, t): 100 for f in F for t in T if f != "tanque"}  # Límite por fuente excepto tanque
    C = 500  # Capacidad del tanque
    lltanque = {t: 20 + 5 * (t % 2) for t in T}  # Lluvia recolectada por tanque ajustada

    # Parámetros para modelar energía y potencia
    hf = {"pozo": 50, "red": 10, "tanque": 5}  # Altura manométrica por fuente
    eta_p = {f: 0.65 for f in F}  # Eficiencia de bomba por fuente
    rho_g = 9.81  # Peso específico del agua
    delta_t = 1  # Duración del período en horas
    Pmax = {"red": 50, "diesel": 30, "solar": 20}  # Potencia máxima por fuente energética
    E = ["red", "diesel", "solar"]
    P = [(f, e) for f in F for e in E]
    cE = {(e, t): 100 + 10 * (t % 2) if e == "red" else 150 if e == "diesel" else 0 for e in E for t in T}  # Costo energético por fuente y tiempo

    sets["E"] = E
    sets["P"] = P
    params = {}
    params.update({
        "hf": hf,
        "eta_p": eta_p,
        "rho_g": rho_g,
        "delta_t": delta_t,
        "Pmax": Pmax,
        "cE": cE
    })

    params.update({
        "da": da,
        "lla": lla,
        "eta": eta,
        "cW": cW,
        "beta": beta,
        "cD": cD,
        "Qmax": Qmax,
        "C": C,
        "lltanque": lltanque,
        "sa": sa,
        "s_index": s_index
    })

    Qriego = {a: 25 for a in A}  # valor ejemplo de caudal máximo
    params["Qriego"] = Qriego

    x_inv = 300  # Costo de inversión en monitoreo reducido
    phi_inv = 500  # Costo de inversión en automatización reducido
    ex = 10  # Energía consumida por monitoreo por periodo
    ephi = 15  # Energía consumida por automatización por periodo

    params.update({
        "x_inv": x_inv,
        "phi_inv": phi_inv,
        "ex": ex,
        "ephi": ephi
    })

    return sets, params
