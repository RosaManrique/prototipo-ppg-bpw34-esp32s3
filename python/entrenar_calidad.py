from __future__ import annotations

from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    ConfusionMatrixDisplay,
    confusion_matrix,
)
from sklearn.model_selection import GroupShuffleSplit
from sklearn.tree import DecisionTreeClassifier, plot_tree

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "datos" / "raw"
MODEL_DIR = ROOT / "modelos"
FEATURE_DIR = ROOT / "datos" / "processed"
FEATURES = ["dc_mean", "ac_std", "robust_amplitude", "diff_std"]


def features_from_capture(path: Path) -> dict | None:
    df = pd.read_csv(path)
    required = {"participant_id", "condition", "label", "differential_V"}
    if not required.issubset(df.columns):
        print(f"Se omite {path.name}: faltan columnas {sorted(required - set(df.columns))}")
        return None

    x = pd.to_numeric(df["differential_V"], errors="coerce").dropna().to_numpy(dtype=float)
    if x.size < 300:
        print(f"Se omite {path.name}: solo contiene {x.size} muestras válidas.")
        return None

    # Características sencillas por sesión completa. La etiqueta procede
    # de la condición experimental registrada durante la captura.
    centered = x - np.median(x)
    return {
        "file": path.name,
        "participant_id": str(df["participant_id"].iloc[0]),
        "condition": str(df["condition"].iloc[0]),
        "label": int(df["label"].iloc[0]),
        "dc_mean": float(np.mean(x)),
        "ac_std": float(np.std(centered, ddof=1)),
        "robust_amplitude": float(np.percentile(centered, 95) - np.percentile(centered, 5)),
        "diff_std": float(np.std(np.diff(x), ddof=1)),
        "n_samples": int(x.size),
    }


def main() -> None:
    files = sorted(RAW_DIR.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No hay archivos en {RAW_DIR}. Primero capture sesiones.")

    records = []
    for path in files:
        try:
            record = features_from_capture(path)
            if record is not None and record["label"] in (0, 1):
                records.append(record)
        except Exception as exc:
            print(f"Se omite {path.name}: {exc}")

    if not records:
        raise RuntimeError("No hay capturas válidas etiquetadas como estable (1) o movimiento (0).")

    table = pd.DataFrame(records)
    if table["label"].nunique() != 2:
        raise ValueError("Se requieren registros de ambas clases: estable (1) y movimiento (0).")
    if table["participant_id"].nunique() < 3:
        raise ValueError("Se necesitan al menos 3 participantes para separar evaluación por participante.")

    # Comprobar que cada participante aporta ambas clases para evitar una
    # partición de prueba que contenga una sola clase.
    classes_per_participant = table.groupby("participant_id")["label"].nunique()
    if (classes_per_participant < 2).any():
        print("ADVERTENCIA: algunos participantes no tienen ambas clases.")

    FEATURE_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    feature_csv = FEATURE_DIR / "dataset_caracteristicas.csv"
    table.to_csv(feature_csv, index=False)

    X = table[FEATURES]
    y = table["label"].astype(int)
    groups = table["participant_id"]
    splitter = GroupShuffleSplit(n_splits=30, test_size=0.25, random_state=42)

    split = None
    for train_idx, test_idx in splitter.split(X, y, groups=groups):
        if y.iloc[train_idx].nunique() == 2 and y.iloc[test_idx].nunique() == 2:
            split = (train_idx, test_idx)
            break
    if split is None:
        raise RuntimeError(
            "No se encontró una división por participante con ambas clases en entrenamiento y prueba. "
            "Reúnan más capturas estables y perturbadas de varios participantes."
        )

    train_idx, test_idx = split
    model = DecisionTreeClassifier(
        max_depth=3,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42,
    )
    model.fit(X.iloc[train_idx], y.iloc[train_idx])
    pred = model.predict(X.iloc[test_idx])

    acc = accuracy_score(y.iloc[test_idx], pred)
    report = classification_report(
        y.iloc[test_idx], pred,
        labels=[0, 1],
        target_names=["No apta / movimiento", "Apta / estable"],
        zero_division=0,
    )
    cm = confusion_matrix(y.iloc[test_idx], pred, labels=[0, 1])

    model_path = MODEL_DIR / "modelo_calidad_ppg_v1.joblib"
    joblib.dump({"model": model, "features": FEATURES}, model_path)

    fig, ax = plt.subplots(figsize=(6, 5))
    ConfusionMatrixDisplay(cm, display_labels=["No apta", "Apta"]).plot(
        ax=ax, cmap="Blues", colorbar=False
    )
    ax.set_title("Matriz de confusión - PPG discreta V1")
    fig.tight_layout()
    fig.savefig(MODEL_DIR / "matriz_confusion_v1.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(12, 7))
    plot_tree(
        model,
        feature_names=FEATURES,
        class_names=["No apta", "Apta"],
        filled=True,
        rounded=True,
        ax=ax,
    )
    ax.set_title("Árbol de decisión - calidad de adquisición PPG V1")
    fig.tight_layout()
    fig.savefig(MODEL_DIR / "arbol_decision_v1.png", dpi=160)
    plt.close(fig)

    metrics_path = MODEL_DIR / "metricas_v1.txt"
    with metrics_path.open("w", encoding="utf-8") as f:
        f.write(f"Capturas usadas: {len(table)}\n")
        f.write(f"Participantes: {table['participant_id'].nunique()}\n")
        f.write(f"Entrenamiento: {len(train_idx)} capturas\n")
        f.write(f"Prueba: {len(test_idx)} capturas\n")
        f.write(f"Accuracy: {acc:.4f}\n\n")
        f.write(report)
        f.write("\n\nImportancia de características:\n")
        for name, importance in zip(FEATURES, model.feature_importances_):
            f.write(f"{name}: {importance:.4f}\n")

    print(f"Dataset procesado: {feature_csv}")
    print(f"Accuracy (prueba por participante): {acc:.3f}")
    print(report)
    print(f"Modelo guardado: {model_path}")
    print(f"Matriz: {MODEL_DIR / 'matriz_confusion_v1.png'}")
    print(f"Árbol: {MODEL_DIR / 'arbol_decision_v1.png'}")
    print(f"Métricas: {metrics_path}")
    print("Interpretar los resultados como preliminares; no son validación clínica.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}")
        raise
