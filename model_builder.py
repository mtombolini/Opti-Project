import gurobipy as gp
from gurobipy import GRB

def build_model(sets, params):
    A, T, F, R = sets["A"], sets["T"], sets["F"], sets["R"]
    da, lla, eta, cW, beta, cD = params["da"], params["lla"], params["eta"], params["cW"], params["beta"], params["cD"]

    model = gp.Model("Riego")

    # Variables: qa_t_f[a][t][f]
    qa = {(a, t, f): model.addVar(lb=0, name=f"qa_{a}_{t}_{f}")
          for a in A for t in T for f in F}
    za = {a: model.addVar(vtype=GRB.BINARY, name=f"za_{a}") for a in A}
    delta = {(a, t): model.addVar(lb=0, name=f"delta_{a}_{t}") for a in A for t in T}
    ua = {(a, t, r): model.addVar(vtype=GRB.BINARY, name=f"ua_{a}_{t}_{r}") for a in A for t in T for r in R}
    ya = {(a, t): model.addVar(vtype=GRB.BINARY, name=f"ya_{a}_{t}") for a in A for t in T}

    # Función objetivo: minimizar costos de agua, penalización por no cultivar y déficit hídrico
    model.setObjective(
        gp.quicksum(cW[f] * qa[a, t, f] for a in A for t in T for f in F) +
        gp.quicksum(beta[a] * (1 - za[a]) for a in A) +
        gp.quicksum(cD * delta[a, t] for a in A for t in T),
        GRB.MINIMIZE
    )

    # Restricción de método único
    for a in A:
        for t in T:
            model.addConstr(gp.quicksum(ua[a, t, r] for r in R) == ya[a, t], name=f"metodo_unico_{a}_{t}")

    # Restricción de balance hídrico
    for a in A:
        for t in T:
            model.addConstr(
                gp.quicksum(qa[a, t, f] * gp.quicksum(eta[a, r] * ua[a, t, r] for r in R) for f in F) + delta[a, t] + lla[a, t] == da[a, t] * za[a],
                name=f"balance_{a}_{t}"
            )

    return model, {"qa": qa, "za": za, "delta": delta, "ya": ya, "ua": ua}
