#!/usr/bin/env python
#encoding: iso-8859-15
import math

def nombre_capas(capas):
    return [nombre for nombre, e, mu, K in capas]

def R_capas(capas):
    return [e / K for nombre, e, mu, K in capas]

def S_capas(capas):
    return [e * mu for nombre, e, mu, K in capas]

def R_total(capas, Rs_ext, Rs_int):
    return Rs_ext + sum(R_capas(capas)) + Rs_int

def calculaU(capas, Rs_ext, Rs_int):
    """Transmitancia térmica del cerramiento"""
    return 1.0 / R_total(capas, Rs_ext, Rs_int)

if __name__ == "__main__":
    def stringify(list, prec):
        format = '%%.%if' % prec
        return "[" + ", ".join([format % item for item in list]) + "]"
    #Resistencia térmica                    e       mu      K       R       S
    #Nombre                                 [m]     [-]     [W/mK]  [m²K/W] [m]
    #1/2 pie LP métrico o catalán 40 mm<    0.11    10      0.69    0.16    1.1
    #Mortero_de_áridos_ligeros_[vermiculita 0.01    10      0.41    0.02    0.1
    #EPS Poliestireno Expandido             0.03    20      0.037   0.81    0.6
    #Tabique de LH sencillo [40 mm < Esp    0.03    10      0.44    0.07    0.3
    #Enlucido_de_yeso_1000<d<1300           0.01    6       0.57    0.02    0.06
    #Rse                                                            0.04
    #Rsi (cerramientos verticales)                                  0.13
    #Resistencia total (m²K/W)                                      1.25
    capas = [("1/2 pie LP métrico o catalán 40 mm<", 0.11, 10.0, 0.69),
            ("Mortero_de_áridos_ligeros_[vermiculita", 0.01, 10.0, 0.41),
            ("EPS Poliestireno Expandido", 0.03, 20.0, 0.037),
            ("Tabique de LH sencillo [40 mm < Esp", 0.03, 10.0, 0.44),
            ("Enlucido_de_yeso_1000<d<1300", 0.01, 6.0, 0.57),]

    Rs_ext = 0.04
    Rs_int = 0.13
    capas_R = R_capas(capas)
    capas_S = S_capas(capas)
    Rtotal = R_total(capas, Rs_ext, Rs_int) #("Resistencia total (m²K/W)", 1.25)
    U = calculaU(capas, Rs_ext, Rs_int) # U = 0.80 W/m²K
    print u"Nombre capas:\n\t", "\n\t".join(nombre_capas(capas))
    print u"R Capas:\n\t", stringify(capas_R, 2)
    print u"S Capas:\n\t", stringify(capas_S, 2)
    print u"Rs_ext: %.2f\nRs_int: %.2f" % (Rs_ext, Rs_int)
    print u"R_total: %.2f\nU: %.2f" % (Rtotal, U)
