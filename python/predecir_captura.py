from __future__ import annotations

from pathlib import Path
import sys

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "modelos" / "modelo_calidad_ppg_v1.joblib"


def main() -> None:
    if not MODEL.exists():
        raise FileNotFoundError("Primero ejecute entrenar_calidad.py.")
    if len(sys.argv) < 2:
        raise ValueError(r"Uso: python predecir_captura.py ruta\a\captura.csv")

    path = Path(sys.argv[1].strip('"'))
    df = pd.read_csv(path)
    x = pd.to_numeric(df["differential_V"], errors="coerce").dropna().to_numpy(dtype=float)
    if x.size < 300:
        raise ValueError("La captura es demasiado corta o no contiene muestras válidas.")

    centered = pd.Series(x - pd.Series(x).median())
    features = {
        "dc_mean": float(x.mean()),
        "ac_std": float(centered.std(ddof=1)),
        "robust_amplitude": float(centered.quantile(0.95) - centered.quantile(0.05)),
        "diff_std": float(pd.Series(x).diff().dropna().std(ddof=1)),
    }

    bundle = joblib.load(MODEL)
    X = pd.DataFrame([features], columns=bundle["features"])
    model = bundle["model"]
    pred = int(model.predict(X)[0])
    proba = model.predict_proba(X)[0]

    print("Características:")
    for name, value in features.items():
        print(f"  {name}: {value:.6f}")
    print("\nClasificación experimental:")
    print("  APTA / estable" if pred == 1 else "  NO APTA / movimiento")
    print(f"  Probabilidad clase no apta: {proba[0]:.3f}")
    print(f"  Probabilidad clase apta: {proba[1]:.3f}")
    print("Nota: la salida solo refleja las condiciones representadas en el dataset.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}")
        raise
