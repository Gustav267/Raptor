# Definition der 7-Parameter-Logistischen Funktion (PL7)
def seven_pl(
    x,
    A: float | int,
    D: float | int,
    C: float | int,
    B: float | int,
    G: float | int,
    F: float | int,
):
    return D + (A - D) / (1 + ((x / C) ** B) ** G) + (F * x)


# Erste ableitung der 7-Parameter-Logistischen Funktion  (skaliert)
def erst_abl(
    x,
    A: float | int,
    D: float | int,
    C: float | int,
    B: float | int,
    G: float | int,
    F: float | int,
):
    return (
        -B * G * (A - D) * ((x / C) ** B) ** G / (x * (((x / C) ** B) ** G + 1) ** 2)
        + F
    )


def erste_ableitung_minus_1(x, best_values):
    """Hilfsfunktion f(x) = erst_abl(x) - 1"""
    return (erst_abl(x, **best_values)) - 1


# Zweite Ableitung der 7-Parameter-Logistischen Funktion
def zwe_abl(
    x,
    A: float | int,
    D: float | int,
    C: float | int,
    B: float | int,
    G: float | int,
    F: float | int,
):
    return (
        B
        * G
        * (A - D)
        * (B * G * ((x / C) ** B) ** G - B * G + ((x / C) ** B) ** G + 1)
        * ((x / C) ** B) ** G
        / (x**2 * (((x / C) ** B) ** G + 1) ** 3)
    )
