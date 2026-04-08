import pandas as pd
import matplotlib.pyplot as plt
from chemistry_raptor import create_plot
from typing import Annotated
import xlwings as xw


def __to_series(val):
    if isinstance(val, (int, float)):
        val = [val]
    elif isinstance(val, (list, tuple)):
        if val and isinstance(val[0], (list, tuple)):
            val = [row[0] for row in val]
    return pd.to_numeric(pd.Series(val), errors="coerce")


@xw.func
@xw.ret(expand="table")
def RAPTOR(
        vol_naoh: Annotated[list, {"doc": "Volumina der Maßlösung"}],
        ph_werte: Annotated[list, {"doc": "gemessene pH-Werte"}],
        titel: Annotated[str, {"doc": "Titel des Diagrams"}]="Titrationskurve",
        subtitel: Annotated[str, {"subtitel": "Untertitel des Diagrams"}] = "",
        breite: Annotated[float, {"doc": "Breite des Diagrams"}] = 8,
        hoehe: Annotated[float, {"doc": "Höhe des Diagrams"}] = 5
) -> list:
    """Erstellt ein Plot anhand einer Liste an verbrauchter Maßlösung und pH-Werten"""
    caller = xw.Book.caller()
    sheet = caller.sheets.active

    vol_naoh = __to_series(vol_naoh)
    ph_werte = __to_series(ph_werte)

    fig, ax = plt.subplots(figsize=(float(breite), float(hoehe)))
    fig.suptitle(titel, size='xx-large', weight="bold")
    if subtitel is not None:
        ax.set_title(subtitel)
    results = create_plot(vol_naoh, ph_werte, ax)

    name = titel
    if subtitel != "":
        name += f" - {subtitel}"
    name += f" ({breite}x{hoehe})"

    sheet.pictures.add(fig, name=name, update=True)
    plt.close(fig)

    return [
        ["RAPTOR", "Ergebnisse"],
        ["f(x)=7", results[0]],
        ["Wendestelle", results[1]],
        ["Äquivalenzpunkt", results[2]],
    ]

