#!/usr/bin/env python
#encoding: iso-8859-15

import math
import psicrom
from capas import *

def calculafRsi(U):
    """Factor de temperatura de la superficie interior
    """
    return 1.0 - U * 0.25

def calculafRsimin(hrint, tempext, tempint=20.0):
    """Factor de temperatura útil sobre el paramento interior.
    """
    def calculatemp_simin(hrint):
        p_i = hrint * 2337 / 100.0
        p_sat = p_i / 0.8 # la humedad relativa no debería pasar de 0.80
        if p_sat >= 610.5: # condición CTE (son las expresiones inversas de p_sat como f(temp)
            temp_si_min = 237.3 * math.log (p_sat / 610.5) / (17.269 - math.log (p_sat / 610.5))
        else: # condición ISO 13788
            temp_si_min = 265.5 * math.log (p_sat / 610.5) / (21.875 - math.log (p_sat / 610.5))
        return temp_si_min
    temp_si_min = calculatemp_simin(hrint)
    return (temp_si_min - tempext) / (tempint - tempext)

def compruebacsuperificiales(fRsi, fRsimin):
    """Comprueba la condición de existencia de condensaciones superficiales en un
    cerramiento o puente térmico.
    Devuelve la comprobación y el valor de fRsi y fRsimin
    """
    # TODO: el CTE incluye tablas según zonas y clase de higrometría para fRsimin
    return fRsi < fRsimin

def compuebacintersticiales(presiones, presiones_sat):
    """Comprueba la condición de existencia de condensaciones intersticiales en un
    cerramiento o puente térmico.
    Devuelve la comprobación
    """
    condensa = False
    for presion_i, presion_sat_i in zip(presiones, presiones_sat):
        if presion_i >= presion_sat_i:
            condensa = True
    return condensa

if __name__ == "__main__":
    import datos_ejemplo
    import grafica
    from util import stringify
    import psicrom

    #Datos Sevilla enero: Te=10.7ºC, HR=79%
    temp_ext = 10.7 #Temperatura enero
    HR_ext = 79 #Humedad relativa enero
    temp_int = 20
    HR_int = 55 #según clase de higrometría: 3:55%, 4:62%, 5:70%
    higrometria = 3

    # Datos constructivos
    Rs_ext = 0.04
    Rs_int = 0.13
    capas = datos_ejemplo.capas
    muro = Cerramiento(capas, Rs_ext, Rs_int)

    f_Rsi = calculafRsi(muro.U) # 0.80
    f_Rsimin = calculafRsimin(HR_int, temp_ext) # 0.36
    g, puntos_condensacion = muro.calculacantidadcondensacion(temp_ext, temp_int, HR_ext, HR_int)
    cantidad_condensada = sum(g)
    # indicamos evaporación en la interfase 2, pero en realidad habría que ver en cúales había antes
    # condensaciones y realizar el cálculo en ellas.
    g, puntos_evaporacion = muro.calculacantidadevaporacion(temp_ext, temp_int, HR_ext, HR_int, interfases=[2])
    cantidad_evaporada = sum(g)

    # Temperaturas: [10.7, 11.0, 12.2, 12.4, 18.4, 18.9, 19.0, 20.0]
    # Presiones de saturación: [1286.08, 1311.79, 1418.84, 1435.87, 2114.68, 2182.84, 2200.69, 2336.95]
    # Presiones de vapor: [1016.00, 1016.00, 1153.16, 1165.62, 1240.44, 1277.84, 1285.32, 1285.32]
    print u"Capas: \n\t", "\n\t".join(muro.nombre_capas)
    c_sup = compruebacsuperificiales(f_Rsi, f_Rsimin) and u"Sí" or "No"
    print u"Condensaciones superficiales (%s)" % c_sup
    print u"\tfRsi = %.2f, fRsimin = %.2f" % (f_Rsi, f_Rsimin)
    c_int = compuebacintersticiales(presiones, presiones_sat) and u"Sí" or "No"
    print u"Condensaciones intersticiales (%s)" % c_int
    print u"\tCantidad condensada: %.2f [g/m2.mes]" % (2592000.0 * cantidad_condensada,)
    print u"\tCantidad evaporada: %.2f [g/m2.mes]" % (2592000.0 * cantidad_evaporada,)

    grafica.dibujapresionestemperaturas("Cerramiento tipo", muro,
            temp_ext, temp_int, HR_int, HR_ext, f_Rsi, f_Rsimin)
#     grafica.dibujapresiones(muro, temp_ext, temp_int, HR_ext, HR_int, puntos_condensacion, g)
#     grafica.dibujapresiones(muro, temp_ext, temp_int, HR_ext, HR_int, puntos_evaporacion, g)
