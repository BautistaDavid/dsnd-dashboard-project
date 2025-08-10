import pickle
from pathlib import Path

# Ruta raíz del proyecto
project_root = Path(__file__).resolve().parent.parent

# Ruta al modelo del equipo
model_path = project_root / "assets" / "model.pkl"

def load_model():
    with model_path.open('rb') as file:
        model = pickle.load(file)
    return model