from data_loader import load_data
from model_builder import build_model
from solver import solve_model
from output_handler import show_results

def main():
    sets, params = load_data()
    model, variables = build_model(sets, params)
    solve_model(model)
    show_results(model, variables)

if __name__ == "__main__":
    main()
