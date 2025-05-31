from data_loader import load_data
from model_builder import build_model
from solver import solve_model
from output_handler import show_results
import matplotlib.pyplot as plt
import numpy as np

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

        # --- Visualizaciones ---
        A = sets["A"]
        T = sets["T"]
        R = sets["R"]
        qa = variables["qa"]
        ua = variables["ua"]
        gt = variables["gt"]

        # Volumen de riego por sector y día
        riego_matrix = np.zeros((len(A), len(T)))
        for (a, t, f), var in qa.items():
            riego_matrix[a][t] += var.X
        plt.imshow(riego_matrix, cmap="YlGnBu", aspect="auto")
        plt.xlabel("Día")
        plt.ylabel("Sector")
        plt.title("Volumen de riego por sector y día")
        plt.colorbar(label="m³")
        plt.show()

        # Método de riego por sector y día
        metodo_matrix = np.full((len(A), len(T)), -1)
        for (a, t, r), var in ua.items():
            if var.X > 0.5:
                metodo_matrix[a][t] = R.index(r)
        plt.imshow(metodo_matrix, cmap="tab10", aspect="auto")
        plt.xlabel("Día")
        plt.ylabel("Sector")
        plt.title("Método de riego utilizado")
        plt.colorbar(ticks=[0, 1, 2], label="Método", format=plt.FuncFormatter(lambda x, _: R[int(x)] if 0 <= int(x) < len(R) else ""))
        plt.show()

        # Evolución del nivel del estanque
        gt_values = [gt[t].X for t in T]
        plt.plot(T, gt_values, marker="o")
        plt.xlabel("Día")
        plt.ylabel("Nivel del estanque (m³)")
        plt.title("Evolución del nivel del estanque")
        plt.grid(True)
        plt.show()
    else:
        print("\n[!] No se pudo evaluar activación de tecnologías porque no se encontró solución óptima.")

if __name__ == "__main__":
    main()
