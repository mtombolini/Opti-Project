import gurobipy as gp
from gurobipy import GRB

def build_model(sets, params):
    A, T, F = sets["A"], sets["T"], sets["F"]
    da, lla, eta, cW, beta, cD = params["da"], params["lla"], params["eta"], params["cW"], params["beta"], params["cD"]

    model = gp.Model("Riego")

    # Variables: qa_t_f[a][t][f]
    qa = {(a, t, f): model.addVar(lb=0, name=f"qa_{a}_{t}_{f}")
          for a in A for t in T for f in F}
    za = {a: model.addVar(vtype=GRB.BINARY, name=f"za_{a}") for a in A}
    delta = {(a, t): model.addVar(lb=0, name=f"delta_{a}_{t}") for a in A for t in T}

    # Función objetivo: minimizar costos de agua, penalización por no cultivar y déficit hídrico
    model.setObjective(
        gp.quicksum(cW[f] * qa[a, t, f] for a in A for t in T for f in F) +
        gp.quicksum(beta[a] * (1 - za[a]) for a in A) +
        gp.quicksum(cD * delta[a, t] for a in A for t in T),
        GRB.MINIMIZE
    )

    # Restricción de balance hídrico
    for a in A:
        for t in T:
            model.addConstr(
                sum(eta * qa[a, t, f] for f in F) + delta[a, t] + lla[a, t] == da[a, t] * za[a],
                name=f"balance_{a}_{t}"
            )

    return model, {"qa": qa, "za": za, "delta": delta}
