from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PLOT_DIR = ROOT / "datos" / "plots"


def main() -> None:
    if len(sys.argv) >= 2:
        path = Path(sys.argv[1].strip('"'))
    else:
        files = sorted((ROOT / "datos" / "raw").glob("*.csv"))
        if not files:
            raise FileNotFoundError("No hay CSV en datos/raw.")
        print("Capturas disponibles:")
        for i, f in enumerate(files, 1):
            print(f"{i}. {f.name}")
        choice = int(input("Seleccione archivo: "))
        path = files[choice - 1]

    df = pd.read_csv(path)
    required = {"t_us", "differential_V"}
    if not required.issubset(df.columns):
        raise ValueError(f"El CSV debe contener las columnas {sorted(required)}")

    df["t_us"] = pd.to_numeric(df["t_us"], errors="coerce")
    df["differential_V"] = pd.to_numeric(df["differential_V"], errors="coerce")
    df = df.dropna(subset=["t_us", "differential_V"]).copy()
    if len(df) < 3:
        raise ValueError("La captura tiene muy pocas muestras.")

    t = (df["t_us"].to_numpy() - df["t_us"].iloc[0]) / 1_000_000.0
    v = df["differential_V"].to_numpy()
    intervals = pd.Series(t).diff().dropna()
    fs = 1.0 / intervals.median() if len(intervals) and intervals.median() > 0 else float("nan")

    PLOT_DIR.mkdir(parents=True, exist_ok=True)
    out = PLOT_DIR / f"{path.stem}_grafico.png"

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(t, v, linewidth=0.8)
    ax.set_title(f"PPG diferencial - {path.name}")
    ax.set_xlabel("Tiempo (s)")
    ax.set_ylabel("A0 - A1 (V)")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out, dpi=160)
    plt.show()

    print(f"Muestras: {len(df)}")
    print(f"Duración: {t[-1] - t[0]:.2f} s")
    print(f"Frecuencia efectiva mediana: {fs:.2f} muestras/s")
    print(f"Media diferencial: {v.mean():.6f} V")
    print(f"Desviación estándar: {v.std(ddof=1):.6f} V")
    print(f"Rango pico a pico: {v.max() - v.min():.6f} V")
    print(f"Gráfico guardado: {out}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}")
        raise
