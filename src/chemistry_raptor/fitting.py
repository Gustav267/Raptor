import pandas as pd
from lmfit import Model
from lmfit.model import ModelResult
from logging import debug, info

from .model import seven_pl

"""Anzahl der Iterationen für den Fit (je mehr, desto genauer,maximal 10^10)"""
ITERATIONS = 100000000


def fit(
    vol_naoh: pd.Series[float | int], ph_wert: pd.Series[float | int], aep_approx: float
) -> tuple[ModelResult, float | int, float | int]:
    ph_max, ph_min = max(ph_wert), min(ph_wert)

    param_bounds = {
        "A": (ph_min - 6, ph_min + 6),
        "D": (ph_max - 6, ph_max + 6),
        "C": (aep_approx * 0.6, aep_approx * 1.4),
        "B": (0.1, 140),
        "G": (0.1, 4),
        "F": (-1, 2),
    }

    # lmfit-Modell erstellen und Parametergrenzen setzen
    model = Model(seven_pl)
    params = model.make_params(A=ph_min, D=ph_max, C=aep_approx, B=10, G=1, F=1)
    for param, (lower, upper) in param_bounds.items():
        params[param].set(min=lower, max=upper)

    # Fit durchführen mit skalierten x-Werten
    result = model.fit(
        ph_wert, params, x=vol_naoh, method="leastsq", max_nfev=ITERATIONS
    )
    debug(result.fit_report())
    debug(f"Anzahl der durchgeführten Iterationen: {result.nfev}")

    # Angepassten C Parameter extrahieren: Startwert für die Suche nach AQ punkt
    param_c: float | int = result.params["C"].value
    info(f"Parameter C (Aep_gesch) bei: {param_c:.3f} ml")

    # Extract R² from the fit report and save it as a parameter
    r_squared_from_report: float = result.rsquared if hasattr(result, "rsquared") else 0.0

    return result.best_values, param_c, r_squared_from_report
