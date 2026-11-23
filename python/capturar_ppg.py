from __future__ import annotations

import csv
import re
import time
from datetime import datetime
from pathlib import Path

import serial
from serial.tools import list_ports

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "datos" / "raw"
BAUD = 115200


def choose_port() -> str:
    ports = list(list_ports.comports())
    print("\nPuertos disponibles:")
    for p in ports:
        print(f"  {p.device}: {p.description}")
    port = input("Puerto del ESP32-S3 (ej. COM5): ").strip()
    if not port:
        raise ValueError("No se indicó el puerto serial.")
    return port


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    port = choose_port()

    participant = input("Código anónimo (ej. P01): ").strip().upper()
    if not re.fullmatch(r"P\d{2,3}", participant):
        raise ValueError("Use un código como P01, P02; no escriba nombres.")

    condition = input("Condición (estable / movimiento / prueba): ").strip().lower()
    if condition not in {"estable", "movimiento", "prueba"}:
        raise ValueError("Condición no válida.")

    duration_text = input("Duración en segundos [20]: ").strip()
    duration = float(duration_text) if duration_text else 20.0
    if not 5 <= duration <= 120:
        raise ValueError("Use una duración entre 5 y 120 segundos.")

    label = {"estable": 1, "movimiento": 0, "prueba": -1}[condition]
    session = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_id = f"{participant}_{condition}_{session}"
    out_path = RAW_DIR / f"{session_id}.csv"

    print("\nCierre Arduino Serial Monitor/Plotter antes de continuar.")
    print("El ESP32 puede reiniciarse al abrir el puerto.")
    input("Coloque el dedo de forma cómoda. Presione ENTER para iniciar...")

    rows: list[list[object]] = []
    start = None
    with serial.Serial(port, BAUD, timeout=0.25) as ser:
        time.sleep(2.0)
        ser.reset_input_buffer()
        start = time.monotonic()
        while time.monotonic() - start < duration:
            line = ser.readline().decode("utf-8", errors="ignore").strip()
            if not line or line.startswith("#") or line.startswith("sample_idx"):
                continue
            parts = line.split(",")
            if len(parts) != 5:
                continue
            try:
                idx = int(parts[0])
                t_us = int(parts[1])
                adc = int(parts[2])
                voltage = float(parts[3])
                led = int(parts[4])
            except ValueError:
                continue
            rows.append([participant, session_id, condition, label, idx, t_us, adc, voltage, led])

    if not rows:
        raise RuntimeError("No se recibieron muestras. Revise el firmware y el puerto COM.")

    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "participant_id", "session_id", "condition", "label",
            "sample_idx", "t_us", "adc_counts", "differential_V", "led_on"
        ])
        writer.writerows(rows)

    # Estimación de frecuencia real a partir de las marcas de tiempo del ESP32.
    timestamps = [int(row[5]) for row in rows]
    intervals = [(b - a) / 1_000_000 for a, b in zip(timestamps, timestamps[1:]) if b > a]
    if intervals:
        intervals_sorted = sorted(intervals)
        median_dt = intervals_sorted[len(intervals_sorted) // 2]
        actual_rate = 1.0 / median_dt if median_dt > 0 else 0.0
    else:
        actual_rate = 0.0

    print(f"\nArchivo guardado: {out_path}")
    print(f"Muestras recibidas: {len(rows)}")
    print(f"Frecuencia efectiva aproximada: {actual_rate:.1f} muestras/s")
    print("Etiqueta: captura experimental; verificar visualmente antes de usarla para entrenar.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}")
        raise
