from data_loader import load_data
from model_builder import build_model
from solver import solve_model
from output_handler import show_results

def main():
    sets, params = load_data()
    s_index = {s: i for i, s in enumerate(sets["S"])}
    params.update({"s_index": s_index})
    model, variables = build_model(sets, params)
    solve_model(model)
    # Diagnóstico IIS si el modelo es inviable
    if model.status == 3:  # Infeasible
        print("\n[!] El modelo es inviable. Ejecutando diagnóstico IIS...")
        model.computeIIS()
        model.write("infeasible.ilp")
        for c in model.getConstrs():
            if c.IISConstr:
                print(f"Restricción inviable: {c.ConstrName}")
    show_results(model, variables)
    x = variables["x"]
    phi = variables["phi"]
    if model.status == 2:
        print(f"\nSistema de monitoreo activado: {'Sí' if x.X > 0.5 else 'No'}")
        print(f"Sistema de automatización activado: {'Sí' if phi.X > 0.5 else 'No'}")
    else:
        print("\n[!] No se pudo evaluar activación de tecnologías porque no se encontró solución óptima.")

if __name__ == "__main__":
    main()
