def show_results(model, variables):
    qa = variables["qa"]
    za = variables["za"]
    delta = variables["delta"]
    ya = variables["ya"]
    ua = variables["ua"]
    if model.status == 2:  # Óptimo encontrado
        print("\nResultados:")
        for key, var in qa.items():
            if var.X > 1e-6:
                print(f"qa[{key}] = {var.X:.2f}")
        print("\n--- Sectores cultivados ---")
        for a, var in za.items():
            print(f"Sector {a}: {'Sí' if var.X > 0.5 else 'No'}")
        print("\n--- Déficit hídrico por sector y día ---")
        for key, var in delta.items():
            if var.X > 1e-6:
                print(f"delta[{key}] = {var.X:.2f}")
        print("\n--- Métodos de riego utilizados ---")
        for (a, t, r), var in ua.items():
            if var.X > 0.5:
                print(f"Sector {a}, Día {t}: {r}")
        print(f"\nCosto total: {model.ObjVal:.2f}")
        x = variables["x"]
        phi = variables["phi"]
        if model.status == 2:
            print(f"\nSistema de monitoreo activado: {'Sí' if x.X > 0.5 else 'No'}")
            print(f"Sistema de automatización activado: {'Sí' if phi.X > 0.5 else 'No'}")
        else:
            print("\n[!] No se pudo evaluar activación de tecnologías porque no se encontró solución óptima.")
    else:
        print("No se encontró solución óptima.")
