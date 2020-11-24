from math import exp


def PETPT(MSALB, SRAD, TMAX, TMIN, XHLAI):
    TD = 0.60 * TMAX + 0.40 * TMIN

    if XHLAI <= 0.0:
        ALBEDO = MSALB
    else:
        ALBEDO = 0.23 - (0.23 - MSALB) * exp(-0.75 * XHLAI)

    SLANG = SRAD * 23.923
    EEQ = SLANG * (2.04e-4 - 1.83e-4 * ALBEDO) * (TD + 29.0)
    EO = EEQ * 1.1

    if TMAX > 35.0:
        EO = EEQ * ((TMAX - 35.0) * 0.05 + 1.1)
    elif TMAX < 5.0:
        EO = EEQ * 0.01 * exp(0.18 * (TMAX + 20.0))

    EO = max(EO, 0.0001)
    return EO
