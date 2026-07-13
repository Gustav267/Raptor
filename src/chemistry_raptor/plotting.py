from typing import Any

import matplotlib
import numpy as np
from lmfit.model import ModelResult
from matplotlib.axes import Axes
from numpy import ndarray, dtype, float64
from pandas import Series

from .model import seven_pl, zwe_abl, erst_abl

COLOR = "#203864"


def plot_all(
    aequivalenzpunkt,
    ax1: Axes,
    best_values: ModelResult,
    ph_wert: Series[float | int],
    r_squared: float | int,
    vol_max,
    vol_min_safe,
    vol_naoh: Series[float | int],
    vol_nullstellen_zweiter_ableitung: float,
    x_ph7: float | None,
    x_scaled_nullstellen_zweiter_ableitung: float,
    x_steigung_eins: ndarray[tuple[Any, ...], dtype[Any]],
    x_tangentenwerte_ml: ndarray[tuple[int], dtype[float64]],
    y_mittlere_tangente: Any,
    y_tangenten: list[Any],
):
    # Fit-Kurve berechnen für grafische Darstellung
    x_linespace_scaled = np.linspace(vol_min_safe, vol_max, num=200)
    ph_zu_linespace = seven_pl(x_linespace_scaled, **best_values)
    ph_fit_deriv = erst_abl(x_linespace_scaled, **best_values)
    ph_fit_deriv2 = zwe_abl(x_linespace_scaled, **best_values)

    ax2 = ax1.twinx()
    ax2.zorder = 0
    ax1.zorder = 1
    ax1.patch.set_visible(False)
    font = {"size": 11}
    matplotlib.rc("font", **font)

    # Set up plot layout & colours
    ax1.set_ylim(0, 15.0)
    ax1.set_xlabel("Volumen NaOH in ml", color=COLOR)
    ax1.set_ylabel("pH-Wert", color=COLOR)
    ax2.set_ylabel("Ableitungen", color=COLOR)
    ax1.tick_params(axis="both", colors=COLOR)
    ax2.tick_params(axis="both", colors=COLOR)

    plot_titrationskurve(ax1, ph_wert, ph_zu_linespace, vol_naoh, x_linespace_scaled)
    plot_ableitungen(ax2, ph_fit_deriv, ph_fit_deriv2, x_linespace_scaled)
    plot_wendestelle(
        ax1,
        best_values,
        vol_nullstellen_zweiter_ableitung,
        x_scaled_nullstellen_zweiter_ableitung,
    )
    plot_ph7(ax1, x_ph7)
    plot_tangenten(
        aequivalenzpunkt,
        ax1,
        x_steigung_eins,
        x_tangentenwerte_ml,
        y_mittlere_tangente,
        y_tangenten,
    )
    add_r_squared(ax1, r_squared)

    # Legend formatting
    l1 = ax1.legend(loc="upper left")
    l2 = ax2.legend(loc="upper right")
    for text in l1.get_texts():
        text.set_color(COLOR)
    for text in l2.get_texts():
        text.set_color(COLOR)
    for spine in ax1.spines.values():
        spine.set_color(COLOR)
    for spine in ax2.spines.values():
        spine.set_color(COLOR)


def add_r_squared(ax1: Axes, r_squared: float | int):
    ax1.text(
        0.95,
        0.05,
        f"R² = {r_squared:.4f}",
        transform=ax1.transAxes,
        fontsize=10,
        verticalalignment="top",
        horizontalalignment="right",
        color=COLOR,
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.5),
    )


def plot_wendestelle(
    ax1: Axes,
    best_values: ModelResult,
    vol_nullstellen_zweiter_ableitung: float,
    x_scaled_nullstellen_zweiter_ableitung: float,
):
    ax1.scatter(
        vol_nullstellen_zweiter_ableitung,
        seven_pl(x_scaled_nullstellen_zweiter_ableitung, **best_values),
        color="green",
        label=f"Wendestelle bei {vol_nullstellen_zweiter_ableitung:.1f} ml",
        marker="_",
        zorder=9,
        s=20,
    )


def plot_tangenten(
    aequivalenzpunkt,
    ax1: Axes,
    x_steigung_eins: ndarray[tuple[Any, ...], dtype[Any]],
    x_tangentenwerte_ml: ndarray[tuple[int], dtype[float64]],
    y_mittlere_tangente,
    y_tangenten: list[Any],
):
    if len(x_steigung_eins) > 1:
        ax1.scatter(
            aequivalenzpunkt[0],
            aequivalenzpunkt[1],
            color="red",
            label=f"Äquivalenzpunkt bei {aequivalenzpunkt[0]:.1f} ml",
            marker="_",
            zorder=8,
            s=20,
        )
        ax1.plot(
            x_tangentenwerte_ml,
            y_mittlere_tangente,
            color="red",
            linestyle=":",
            linewidth=1,
            zorder=5,
            label="Mittlere Tangente",
        )  # Mittlere Tangente
        ax1.plot(
            x_tangentenwerte_ml,
            y_tangenten[0],
            color=COLOR,
            linestyle=":",
            linewidth=1,
            zorder=3,
            label="Tangenten bei f'(x)=1",
        )  # 1.Tangente bei 45°
        ax1.plot(
            x_tangentenwerte_ml,
            y_tangenten[1],
            color=COLOR,
            linestyle=":",
            linewidth=1,
            zorder=2,
        )  # 2.Tangente bei -45°
    else:
        print("keine tangenten gefunden")


def plot_titrationskurve(
    ax1: Axes,
    ph_wert: Series[float | int],
    ph_zu_linespace,
    vol_naoh: Series[float | int],
    x_linespace_ml: ndarray[tuple[int], dtype[float64]],
):
    ax1.scatter(
        vol_naoh, ph_wert, color="blue", label="Messpunkte", marker="x", zorder=6, s=20
    )
    ax1.plot(
        x_linespace_ml,
        ph_zu_linespace,
        color="orange",
        label="Titrationskurve",
        linewidth=1,
        zorder=4,
    )


def plot_ph7(ax1: Axes, x_ph7: float | None):
    ax1.scatter(
        x_ph7,
        7,
        color="purple",
        label=f"f(x)=7 bei {x_ph7:.1f} ml",
        marker="_",
        zorder=7,
        s=20,
    )


def plot_ableitungen(ax2: Axes, ph_fit_deriv, ph_fit_deriv2, x_linespace_ml):
    ax2.plot(
        x_linespace_ml,
        ph_fit_deriv,
        color="green",
        label="1. Ableitung",
        linewidth=1,
        linestyle="dashed",
        zorder=1,
    )
    ax2.plot(
        x_linespace_ml,
        ph_fit_deriv2,
        color="gray",
        label="2. Ableitung",
        linewidth=1,
        linestyle=":",
        zorder=1,
    )
