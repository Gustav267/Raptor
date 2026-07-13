import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from scipy.optimize import root_scalar

from . import fitting
from .model import zwe_abl
from .analysis import aep_from_ph7, aep_from_tangentenverfahren
from .plotting import plot_all


def create_plot(
    vol_naoh: pd.Series[float | int], ph_wert: pd.Series[float | int], ax1: Axes
):
    if len(vol_naoh) != len(ph_wert):
        raise ValueError("Number of vol_naoh does not match number of ph_wert")
    if len(vol_naoh) <= 8 or len(ph_wert) <= 8:
        raise ValueError("Not enough data points provided")

    # Berechnung des Startwerts für C: Mittelwert der x-Werte an der größten Steigung
    max_diff_index = np.argmax(np.diff(ph_wert))

    # aep_approx ist C_start skaliert auf die Original-Volumenskala
    aep_approx = np.mean(vol_naoh[max_diff_index : max_diff_index + 2])

    vol_max, vol_min = max(vol_naoh), min(vol_naoh)

    # erst_abl/zwe_abl teilen durch x, daher führt x=0 (z.B. wenn die Titration
    # bei 0 ml NaOH beginnt) zu einem ZeroDivisionError bei der Nullstellensuche.
    # Kleine Sicherheitsmarge oberhalb von 0, falls vol_min <= 0 ist.
    epsilon = (vol_max - vol_min) * 1e-6 if vol_max > vol_min else 1e-6
    vol_min_safe = vol_min if vol_min > 0 else epsilon

    # best_values: beste Parameterwerte für die 7-Parameter-Logistische Funktion
    # aep_approx: Startwert für C
    # r_squared: Bestimmtheitsmaß (R^2)
    best_values, aep_approx, r_squared = fitting.fit(vol_naoh, ph_wert, aep_approx)

    (
        aequivalenzpunkt,
        x_steigung_eins,
        x_tangentenwerte_ml,
        y_mittlere_tangente,
        y_tangenten,
    ) = aep_from_tangentenverfahren(
        aep_approx, best_values, vol_max, vol_min, vol_min_safe
    )

    aep_ph7 = aep_from_ph7(best_values, 7, aep_approx)

    ### Nullstelle Zweiter Ableitung ###
    x_scaled_nullstellen_zweiter_ableitung = root_scalar(
        lambda x: zwe_abl(x, **best_values),
        x0=aep_approx,
        method="newton",
    ).root

    plot_all(
        aequivalenzpunkt,
        ax1,
        best_values,
        ph_wert,
        r_squared,
        vol_max,
        vol_min_safe,
        vol_naoh,
        x_scaled_nullstellen_zweiter_ableitung,
        aep_ph7,
        x_scaled_nullstellen_zweiter_ableitung,
        x_steigung_eins,
        x_tangentenwerte_ml,
        y_mittlere_tangente,
        y_tangenten,
    )

    return aep_ph7, x_scaled_nullstellen_zweiter_ableitung, aequivalenzpunkt[0]
