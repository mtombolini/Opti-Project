import gurobipy as gp
from gurobipy import GRB

def build_model(sets, params):
    A, T, F, R, E, P = sets["A"], sets["T"], sets["F"], sets["R"], sets["E"], sets["P"]
    da, sa, s_index = params["da"], params["sa"], params["s_index"]
    Qriego = params["Qriego"]
    lla, eta, cW, beta, cD, Qmax, C, lltanque = (
        params["lla"], params["eta"], params["cW"],
        params["beta"], params["cD"], params["Qmax"], params["C"], params["lltanque"]
    )
    hf, eta_p, rho_g, delta_t, Pmax, cE = (
        params["hf"], params["eta_p"], params["rho_g"],
        params["delta_t"], params["Pmax"], params["cE"]
    )
    x_inv = params["x_inv"]
    phi_inv = params["phi_inv"]
    ex = params["ex"]
    ephi = params["ephi"]

    model = gp.Model("Riego")

    # Variables: qa_t_f[a][t][f]
    qa = {(a, t, f): model.addVar(lb=0, name=f"qa_{a}_{t}_{f}")
          for a in A for t in T for f in F}
    za = {a: model.addVar(vtype=GRB.BINARY, name=f"za_{a}") for a in A}
    delta = {(a, t): model.addVar(lb=0, name=f"delta_{a}_{t}") for a in A for t in T}
    ua = {(a, t, r): model.addVar(vtype=GRB.BINARY, name=f"ua_{a}_{t}_{r}") for a in A for t in T for r in R}
    ya = {(a, t): model.addVar(vtype=GRB.BINARY, name=f"ya_{a}_{t}") for a in A for t in T}

    gt = {t: model.addVar(lb=0, name=f"gt_{t}") for t in T}
    wt = {(f, t): model.addVar(lb=0, name=f"wt_{f}_{t}") for f in F for t in T if f != "tanque"}

    x = model.addVar(vtype=GRB.BINARY, name="x")
    phi = model.addVar(vtype=GRB.BINARY, name="phi")

    # Función objetivo: minimizar costos de agua, penalización por no cultivar, déficit hídrico y energía
    model.setObjective(
        gp.quicksum(cW[f] * qa[a, t, f] for a in A for t in T for f in F) +
        gp.quicksum(beta[a] * (1 - za[a]) for a in A) +
        gp.quicksum(cD * delta[a, t] for a in A for t in T)
        +
        gp.quicksum(
            cE[e, t] * (rho_g * hf[f] / eta_p[f]) * (qa[a, t, f] + (wt[f, t] if (f, t) in wt else 0))
            for (f, e) in P for a in A for t in T if f != "tanque"
        )
        + x_inv * x + phi_inv * phi
        + gp.quicksum(cE["red", t] * (ex * x + ephi * phi) for t in T),
        GRB.MINIMIZE
    )

    # R1 Restricción de método único
    for a in A:
        for t in T:
            model.addConstr(gp.quicksum(ua[a, t, r] for r in R) == ya[a, t], name=f"R1_metodo_unico_{a}_{t}")

    # R2 Restricción de balance hídrico
    for a in A:
        s_name = sa[a]
        s = s_index[s_name]
        for t in T:
            model.addConstr(
                gp.quicksum(qa[a, t, f] * gp.quicksum(eta[a, r] * ua[a, t, r] for r in R) for f in F) + delta[a, t] + lla[a, t] == da[a, t, s] * za[a],
                name=f"R2_balance_hidrico_{a}_{t}"
            )

    # R3 Restricciones de límite de extracción por fuente (excepto tanque)
    for f in F:
        if f != "tanque":
            for t in T:
                model.addConstr(
                    gp.quicksum(qa[a, t, f] for a in A) <= Qmax[f, t],
                    name=f"R3_limite_fuente_{f}_{t}"
                )

    # R4 Restricciones de balance del tanque
    for t in T:
        entrada = gp.quicksum(wt[f, t] for f in F if f != "tanque") + lltanque[t]
        salida = gp.quicksum(qa[a, t, "tanque"] for a in A)
        if t == 0:
            model.addConstr(gt[t] == entrada - salida, name=f"R4_tanque_balance_{t}")
        else:
            model.addConstr(gt[t] == gt[t-1] + entrada - salida, name=f"R4_tanque_balance_{t}")
        model.addConstr(gt[t] <= C, name=f"R4_capacidad_tanque_{t}")

    # R5 Restricción de automatización requiere monitoreo
    model.addConstr(phi <= x, name="R5_automatizacion_requiere_monitoreo")

    # R6 Restricción: Activación de riego solo si se cultiva
    for a in A:
        for t in T:
            model.addConstr(ya[a, t] <= za[a], name=f"R6_riego_solo_si_cultivo_{a}_{t}")

    # R7 Restricción: Cobertura hídrica mínima estacional
    gamma = 0.7  # cobertura mínima
    for a in A:
        s_name = sa[a]
        s = s_index[s_name]
        demanda_total = gp.quicksum(da[a, t, s] for t in T)
        agua_aplicada = gp.quicksum(
            gp.quicksum(eta[a, r] * ua[a, t, r] for r in R) * gp.quicksum(qa[a, t, f] for f in F)
            for t in T
        )
        model.addConstr(agua_aplicada >= gamma * demanda_total * za[a], name=f"R7_cobertura_minima_{a}")

    # R8 Restricción adicional: Caudal máximo de riego
    for a in A:
        for t in T:
            model.addConstr(
                gp.quicksum(qa[a, t, f] for f in F) <= Qriego[a] * ya[a, t] * delta_t,
                name=f"R8_max_riego_{a}_{t}"
            )

    # R9 Restricción: Déficit solo si se cultiva
    M = 1000  # valor suficientemente grande
    for a in A:
        for t in T:
            model.addConstr(delta[a, t] <= M * za[a], name=f"R9_delta_si_cultivo_{a}_{t}")

    # R10 Restricción de potencia disponible por fuente de energía
    for e in E:
        for t in T:
            model.addConstr(
                gp.quicksum(
                    (rho_g * hf[f] / eta_p[f]) * (qa[a, t, f] + (wt[f, t] if (f, t) in wt else 0))
                    for f in F if f != "tanque" for a in A
                ) <= Pmax[e] * delta_t,
                name=f"R10_potencia_max_{e}_{t}"
            )

    return model, {"qa": qa, "za": za, "delta": delta, "ya": ya, "ua": ua, "gt": gt, "wt": wt, "x": x, "phi": phi}