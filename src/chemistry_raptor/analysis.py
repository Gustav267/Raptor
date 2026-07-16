from dataclasses import dataclass
from typing import Any

import numpy as np
from lmfit.model import ModelResult
from scipy.optimize import root_scalar

from .model import seven_pl, erst_abl, zwe_abl, erste_ableitung_minus_1


def aep_from_ph7(best_values, ph_wert, x_start):
    res = root_scalar(
        lambda x: seven_pl(x, **best_values) - ph_wert,
        x0=x_start,
        method="newton",
        fprime=lambda x: erst_abl(x, **best_values),
    )
    return res.root if res.converged else None


def finde_x_bei_steigung_eins(bereich, best_values) -> float | None:
    """Nullstellen der Ableitung - 1 suchen im bereich"""

    def function(x):
        return erste_ableitung_minus_1(x, best_values)

    def fprime(x):
        return zwe_abl(x, **best_values)

    # fprime accepts a callable, with the same arguments as function, therefore the error is ok.
    res = root_scalar(
        function, bracket=bereich, fprime=fprime
    )  # sucht Nullstelle in Bereich
    return float(res.root) if res.converged else None


@dataclass
class Tangentenverfahren:
    aequivalenzpunkt: tuple[float, float] | None
    x_steigung_eins: list[float] | None


def aep_from_tangentenverfahren(
    aep_approx: float | int,
    best_values: ModelResult,
    vol_max: Any,
    vol_min: Any,
    vol_min_safe: Any | float,
):
    # Bereiche für die Suche nach Steigung 1
    below_above_aep_segments = [
        [vol_min_safe, aep_approx],
        [aep_approx, vol_max],
    ]  # Vermeidet Probleme bei 0

    # x-Werte mit Steigung 1 finden im Bereich und eindeutige Werte behalten
    x_steigung_eins = [
        finde_x_bei_steigung_eins(bereich, best_values)
        for bereich in below_above_aep_segments
    ]
    if len(x_steigung_eins) <= 0:
        raise ArithmeticError("Keine Werte mit Steigung 1 gefunden!")

    punkt_zu_steigung_eins = [
        np.array([x, seven_pl(x, **best_values)]) for x in x_steigung_eins
    ]
    steigung = 1  # Steigung 1 in Originalskala

    def tangente(x, x_tangentenpunkt, y_tangentenpunkt):
        return steigung * (x - x_tangentenpunkt) + y_tangentenpunkt

    x_tangentenwerte_scaled = np.linspace(vol_min, vol_max, 10)
    x_tangentenwerte_ml = np.linspace(vol_min, vol_max, 10)
    y_tangenten = [
        tangente(x_tangentenwerte_scaled, p[0], p[1]) for p in punkt_zu_steigung_eins
    ]

    # Mittlere Gerade
    x_mittel, y_mittel = (
        np.mean(x_steigung_eins),
        np.mean([p[1] for p in punkt_zu_steigung_eins]),
    )
    y_mittlere_tangente = tangente(x_tangentenwerte_scaled, x_mittel, y_mittel)

    def finde_aequivalenzpunkt(x_startwert):
        res = root_scalar(
            lambda x: seven_pl(x, **best_values) - tangente(x, x_mittel, y_mittel),
            x0=x_startwert,
            method="newton",
        )
        return res.root if res.converged else None

    aequivalenzpunkt_x = finde_aequivalenzpunkt(aep_approx)
    aequivalenzpunkt_y = seven_pl(aequivalenzpunkt_x, **best_values)
    aequivalenzpunkt = np.array([aequivalenzpunkt_x, aequivalenzpunkt_y])
    return (
        aequivalenzpunkt,
        x_steigung_eins,
        x_tangentenwerte_ml,
        y_mittlere_tangente,
        y_tangenten,
    )
