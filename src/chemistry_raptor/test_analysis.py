import json
import os
import unittest
from dataclasses import dataclass

import numpy as np
import pandas as pd
from lmfit.model import ModelResult

from chemistry_raptor import fitting, aep_from_tangentenverfahren, aep_from_ph7

TESTDATA_FILENAME = os.path.join(os.path.dirname(__file__), 'test_data.json')

@dataclass(frozen=True)
class AnalysisData:
    vol_naoh: pd.Series[float]
    ph_wert: pd.Series[float]
    max_diff_index: int
    aep_approx: float
    vol_max: float
    vol_min: float
    epsilon: float
    vol_min_safe: float
    best_values: ModelResult


class CalculationTests(unittest.TestCase):
    def setUp(self):
        with open(TESTDATA_FILENAME, 'r') as f:
            self.data: list[AnalysisData] = []
            
            for datapoint in json.load(f):
                vol_naoh: float = datapoint['naoh']
                ph_wert: float = datapoint['ph']
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
                self.data.append(AnalysisData(
                    vol_naoh=vol_naoh,
                    ph_wert=ph_wert,
                    max_diff_index=max_diff_index,
                    aep_approx=aep_approx,
                    vol_max=vol_max,
                    vol_min=vol_min,
                    epsilon=epsilon,
                    vol_min_safe=vol_min_safe,
                    best_values=best_values
                ))

    def test_tangentenverfahren(self):
        self.assertGreater(len(self.data), 0)
        for dp in self.data:
            self.assertIsNotNone(aep_from_tangentenverfahren(
                dp.aep_approx, dp.best_values, dp.vol_max, dp.vol_min, dp.vol_min_safe
            ))

    def test_ph7(self):
        self.assertGreater(len(self.data), 0)
        for dp in self.data:
            self.assertIsNotNone(aep_from_ph7(dp.best_values, 7, dp.aep_approx))

if __name__ == '__main__':
    unittest.main()
