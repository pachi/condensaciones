#!/usr/bin/env python
#encoding: iso-8859-15

import math

def calculafRsi(U):
    """Factor de temperatura de la superficie interior de un cerramiento, partici�n
    interior o puentes t�rmicos INTEGRADOS en los cerramientos.
    """
    return 1.0 - U * 0.25

def calculafRsimin(tempext, tempint, hrint):
    """Factor de temperatura de la superficie interior m�nnimo aceptable de un puente
    t�rmico, cerramiento o partici�n interior.
    """
    def calculatemp_simin(hrint):
        p_i = hrint * 2337 / 100.0
        p_sat = p_i / 0.8 # la humedad relativa no deber�a pasar de 0.80
        if p_sat >= 610.5: # condici�n CTE (son las expresiones inversas de p_sat como f(temp)
            temp_si_min = 237.3 * math.log (p_sat / 610.5) / (17.269 - math.log (p_sat / 610.5))
        else: # condici�n ISO 13788
            temp_si_min = 265.5 * math.log (p_sat / 610.5) / (21.875 - math.log (p_sat / 610.5))
        return temp_si_min
    temp_si_min = calculatemp_simin(hrint)
    #XXX: comprobar si tempint = tempext?
    return (temp_si_min - tempext) / (tempint - tempext)

def compruebacsuperificiales(muro, temp_ext, temp_int, HR_int):
    """Comprueba la condici�n de existencia de condensaciones superficiales en un
    cerramiento o puente t�rmico.
    Devuelve la comprobaci�n y el valor de fRsi y fRsimin
    """
    # el CTE incluye tablas seg�n zonas y clase de higrometr�a para fRsimin que
    # est�n calculadas para la capital m�s desfavorable de cada zona y con HR=55%, 62%, 70%.
    fRsi = calculafRsi(muro.U)
    fRsimin = calculafRsimin(temp_ext, temp_int, HR_int)
    return fRsi < fRsimin

def compruebacintersticiales(muro, temp_ext, temp_int, HR_ext, HR_int):
    """Comprueba la condici�n de existencia de condensaciones intersticiales en un
    cerramiento o puente t�rmico.
    Devuelve la comprobaci�n
    """
#    presiones = muro.presiones(temp_ext, temp_int, HR_ext, HR_int)
#    presiones_sat = muro.presionessat(temp_ext, temp_int)
#    condensa = False
#    for presion_i, presion_sat_i in zip(presiones, presiones_sat):
#        if presion_i >= presion_sat_i:
#            condensa = True
#
#TODO: Revisar condensaciones viendo si la cantidad condensada es susceptible
# de evaporaci�n
    g, puntos_condensacion = muro.cantidadcondensacion(temp_ext, temp_int, HR_ext, HR_int)
    #g, puntos_evaporacion = muro.cantidadevaporacion(temp_ext, temp_int, HR_ext, HR_int, interfases=[2])
    condensa = (sum(g) > 0.0)
    return condensa

def compruebacondensaciones(muro, temp_ext, temp_int, HR_ext, HR_int):
    ci = compruebacintersticiales(muro, temp_ext, temp_int, HR_ext, HR_int)
    cs = compruebacsuperificiales(muro, temp_ext, temp_int, HR_int)

    return ci and cs

if __name__ == "__main__":
    import capas
    import grafica
    from datos_ejemplo import climae, climai, murocapas

    muro = capas.Cerramiento(murocapas, 0.04, 0.13)
    f_Rsi = calculafRsi(muro.U)
    f_Rsimin = calculafRsimin(climae.temp, climai.temp, climai.HR)
    c_sup = compruebacsuperificiales(muro, climae.temp, climai.temp, climai.HR)
    c_int = compuebacintersticiales(muro, climae.temp, climai.temp, climae.HR, climai.HR)

    print u"Capas: \n\t", "\n\t".join(muro.nombre_capas)
    print u"\nCondensaciones superficiales (%s)" % (c_sup and u"S�" or u"No")
    print u"\tfRsi = %.2f, fRsimin = %.2f" % (f_Rsi, f_Rsimin)
    print u"Condensaciones intersticiales (%s)" % (c_int and u"S�" or u"No")
