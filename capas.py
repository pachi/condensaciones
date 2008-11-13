#!/usr/bin/env python
#encoding: iso-8859-15
import math

class Cerramiento(object):
    def __init__(self, capas):
        self._capas = capas

    @property
    def nombre_capas(self):
        """Nombre de las capas
        """
        return [nombre for nombre, e, mu, K in self._capas]

    @property
    def R(self):
        """Resistencia térmica de las capas
        """
        return [e / K for nombre, e, mu, K in self._capas]

    @property
    def S(self):
        """Espesor de aire equivalente de las capas
        """
        return [e * mu for nombre, e, mu, K in self._capas]

    def R_total(self, Rs_ext, Rs_int):
        """Resistencia térmica total del cerramiento
        """
        return Rs_ext + sum(self.R) + Rs_int

    def U(self, Rs_ext, Rs_int):
        """Transmitancia térmica del cerramiento
        """
        return 1.0 / self.R_total(Rs_ext, Rs_int)

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
    import datos_ejemplo
    def stringify(list, prec):
        format = '%%.%if' % prec
        return "[" + ", ".join([format % item for item in list]) + "]"

    capas = datos_ejemplo.capas
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

    muro = Cerramiento(capas)
    print u"Nombre capas:\n\t", "\n\t".join(muro.nombre_capas)
    print u"R Capas:\n\t", stringify(muro.R, 2)
    print u"S Capas:\n\t", stringify(muro.S, 2)
    print u"Rs_ext: %.2f\nRs_int: %.2f" % (Rs_ext, Rs_int)
    print u"R_total: %.2f\nU: %.2f" % (muro.R_total(Rs_ext, Rs_int), muro.U(Rs_ext, Rs_int))

