# backend/application/chart_helper.py
import os
from datetime import datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from flask import current_app as app


def ensure_chart_dir():
    export_dir = os.path.join(app.static_folder, "exports", "charts")
    os.makedirs(export_dir, exist_ok=True)
    return export_dir


def generate_bar_chart(series: dict, title: str = "", filename_prefix: str = "chart"):
    """series: {label: value}. Returns (absolute_path, relative_static_path)."""
    export_dir = ensure_chart_dir()
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    filename = f"{filename_prefix}_{ts}.png"
    filepath = os.path.join(export_dir, filename)

    labels = list(series.keys())
    values = [float(series[k]) for k in labels]

    plt.figure(figsize=(7, 3.5))
    bars = plt.bar(labels, values, color="#0d6efd")
    plt.title(title)
    plt.xticks(rotation=20, ha="right")
    plt.grid(axis="y", linestyle="--", alpha=0.3)
    for b in bars:
        h = b.get_height()
        plt.text(b.get_x() + b.get_width() / 2, h, f"{int(h)}", ha="center", va="bottom", fontsize=8)
    plt.tight_layout()
    plt.savefig(filepath, dpi=110, bbox_inches="tight")
    plt.close()

    rel_path = f"exports/charts/{filename}"
    return filepath, rel_path
