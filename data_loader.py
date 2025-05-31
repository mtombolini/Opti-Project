import numpy as np
import pandas as pd
from config import NA, NT, NF, F, A, T

def load_data():
    xls = pd.ExcelFile("Data.xlsx")
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

    # Asignación de tipo de suelo a cada sector (dummy: cíclico)
    sa = {a: S[a % len(S)] for a in A}

    # --- Carga de datos reales desde Data.xlsx ---

    # Lluvia recolectada por tanque
    lluvia_df = xls.parse("Promedio lluvia diario")
    lltanque = {t: float(lluvia_df.iloc[t]["recoleccion diaria (m3)"]) for t in T}

    # Costo de oportunidad (beta)
    areas_df = xls.parse("Areas")
    beta = {a: float(areas_df.iloc[a]["costo oportunidad  por año (CLP)"]) / 365 for a in A}

    # Eficiencia de métodos (eta)
    eficiencia_df = xls.parse("eficiencia metodos")
    metodo_map = {"surco": "gravedad", "goteo": "goteo", "aspersión": "aspersión"}
    eta = {(a, r): float(eficiencia_df[eficiencia_df["metodo"] == metodo_map[r]]["promedio"].values[0]) for a in A for r in R}

    # Capacidad del estanque (C)
    estanque_df = xls.parse("Capacidad estanque")
    C = float(estanque_df["capacidad (m^3)"].mean())

    # Altura manométrica (hf) y eficiencia bomba (eta_p)
    altura_df = xls.parse("Altura manometrica")
    bomba_df = xls.parse("Bomba")
    hf = {"pozo": float(altura_df[altura_df["tipo de fuente (f)"].str.contains("pozo", case=False)]["altura maxima (m)"].mean()),
          "red": 10,
          "tanque": 5}
    eta_p = {f: float(bomba_df["promedio"].mean()) for f in F}

    # Costo unitario de agua (cW)
    agua_df = xls.parse("Costo unitario agua")
    cW = {"pozo": float(agua_df[agua_df["fuente"].str.contains("pozo", case=False)]["clp "].mean()),
          "red": float(agua_df[agua_df["fuente"].str.contains("rio|estero", case=False)]["clp "].mean()),
          "tanque": float(agua_df[agua_df["fuente"].str.contains("estanque", case=False)]["clp "].mean())}

    # Penalización por déficit hídrico (cD)
    penal_df = xls.parse("Penalización")
    cD = float(penal_df["Penalizacion (CLP/m^3)"].mean())

    # Costos y energía de sistemas automáticos/monitoreo
    auto_df = xls.parse("automatico")
    # Normalizar valores de la columna 'sistema' para evitar errores por espacios o mayúsculas
    auto_df["sistema"] = auto_df["sistema"].str.strip().str.lower()

    # Validar existencia antes de acceder
    if "monitoreo" in auto_df["sistema"].values and "automatico" in auto_df["sistema"].values:
        x_inv = int(auto_df[auto_df["sistema"] == "monitoreo"]["costo instalacion (CLP)"].values[0])
        phi_inv = int(auto_df[auto_df["sistema"] == "automatico"]["costo instalacion (CLP)"].values[0])
        ex = int(auto_df[auto_df["sistema"] == "monitoreo"]["gasto energetico (kWh)"].values[0])
        ephi = int(auto_df[auto_df["sistema"] == "automatico"]["gasto energetico (kWh)"].values[0])
    else:
        raise ValueError("Faltan valores para 'monitoreo' o 'automatico' en la hoja 'automatico' del Excel.")

    # Demanda hídrica (da)
    suelo_df = xls.parse("Suelos necesidades")
    suelo_df.columns = suelo_df.columns.str.strip().str.lower()
    suelo_df["tipo de suelo"] = suelo_df["tipo de suelo"].str.strip().str.lower()
    suelo_map = {"arcilla": "Arcilloso", "franco": "Franco", "arenoso": "Arenoso"}
    da = np.zeros((NA, NT, len(S)))
    for a in A:
        for t in T:
            for s in range(len(S)):
                suelo_tipo = suelo_map[S[s]]
                valor = suelo_df[suelo_df["tipo de suelo"] == suelo_tipo.lower()]["demanda hidrica 1 hectarea  1 dia (m^3)"].values[0]
                da[a, t, s] = float(valor)

    # Lluvia efectiva (dummy, mantener aleatorio si no hay hoja)
    lla = np.zeros((NA, NT))
    # Si tienes una hoja en el excel, reemplazar aquí la asignación de lla
    # lla_df = xls.parse("???")
    # lla = ... # asignar valores reales aquí

    # Límite de extracción por fuente (excepto tanque)
    Qmax = {(f, t): 150 for f in F for t in T if f != "tanque"}

    # Caudal máximo de riego
    Qriego = {a: 50 for a in A}

    # Parámetros para modelar energía y potencia
    rho_g = 9.81  # Peso específico del agua
    delta_t = 1  # Duración del período en horas
    Pmax = {"red": 50, "diesel": 30, "solar": 20}
    E = ["red", "diesel", "solar"]
    P = [(f, e) for f in F for e in E]
    cE = {(e, t): 100 + 10 * (t % 2) if e == "red" else 150 if e == "diesel" else 0 for e in E for t in T}

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

    params["Qriego"] = Qriego
    params.update({
        "x_inv": x_inv,
        "phi_inv": phi_inv,
        "ex": ex,
        "ephi": ephi
    })

    return sets, params
