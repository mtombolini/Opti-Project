from gurobipy import Model
import gurobipy as gp

def build_model(sets, params):
    A = sets['A']
    T = sets['T']
    R = sets['R']
    F = sets['F']

    da = params['da']
    eta = params['eta']

    model = Model('OptiModel')

    za = model.addVars(A, vtype=gp.GRB.BINARY, name='za')
    ya = model.addVars(A, T, vtype=gp.GRB.BINARY, name='ya')
    ua = model.addVars(A, T, R, vtype=gp.GRB.CONTINUOUS, name='ua')
    qa = model.addVars(A, T, F, vtype=gp.GRB.CONTINUOUS, name='qa')
    delta = model.addVars(A, T, vtype=gp.GRB.CONTINUOUS, name='delta')

    # ... (otras restricciones y objetivo)

    # Restricción 4: Activación de riego solo si se cultiva
    for a in A:
        for t in T:
            model.addConstr(ya[a, t] <= za[a], name=f"riego_solo_si_cultivo_{a}_{t}")

    # Restricción 5: Cobertura hídrica mínima estacional
    gamma = 0.7  # cobertura mínima
    for a in A:
        demanda_total = gp.quicksum(da[a, t] for t in T)
        agua_aplicada = gp.quicksum(
            gp.quicksum(eta[a, r] * ua[a, t, r] for r in R) * gp.quicksum(qa[a, t, f] for f in F)
            for t in T
        )
        model.addConstr(agua_aplicada >= gamma * demanda_total * za[a], name=f"cobertura_min_{a}")

    # Restricción 9: Déficit solo si se cultiva
    M = 1000  # valor suficientemente grande
    for a in A:
        for t in T:
            model.addConstr(delta[a, t] <= M * za[a], name=f"delta_si_cultivo_{a}_{t}")

    return model, {'za': za, 'ya': ya, 'ua': ua, 'qa': qa, 'delta': delta}
