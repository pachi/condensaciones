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
    #XXX: comprobar si tempint = tempext
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

def compuebacintersticiales(muro, temp_ext, temp_int, HR_ext, HR_int):
    """Comprueba la condici�n de existencia de condensaciones intersticiales en un
    cerramiento o puente t�rmico.
    Devuelve la comprobaci�n
    """
    presiones = muro.calculapresiones(temp_ext, temp_int, HR_ext, HR_int)
    presiones_sat = muro.calculapresionessat(temp_ext, temp_int)
    condensa = False
    for presion_i, presion_sat_i in zip(presiones, presiones_sat):
        if presion_i >= presion_sat_i:
            condensa = True
    return condensa

if __name__ == "__main__":
    import datos_ejemplo
    import capas
    import grafica

    temp_ext = 10.7 #Temperatura enero
    HR_ext = 79 #Humedad relativa enero
    temp_int = 20
    HR_int = 55 #seg�n clase de higrometr�a: 3:55%, 4:62%, 5:70%

    # Datos constructivos
    muro = capas.Cerramiento(datos_ejemplo.capas, 0.04, 0.13)

    f_Rsi = calculafRsi(muro.U)
    f_Rsimin = calculafRsimin(temp_ext, temp_int, HR_int)

    print u"Capas: \n\t", "\n\t".join(muro.nombre_capas)
    print
    c_sup = compruebacsuperificiales(muro, temp_ext, temp_int, HR_int) and u"S�" or u"No"
    print u"Condensaciones superficiales (%s)" % c_sup
    print u"\tfRsi = %.2f, fRsimin = %.2f" % (f_Rsi, f_Rsimin)
    c_int = compuebacintersticiales(muro, temp_ext, temp_int, HR_ext, HR_int) and u"S�" or u"No"
    print u"Condensaciones intersticiales (%s)" % c_int

#     grafica.dibujapresionestemperaturas("Cerramiento tipo", muro,
#             temp_ext, temp_int, HR_int, HR_ext, f_Rsi, f_Rsimin)

    g, puntos_condensacion = muro.calculacantidadcondensacion(temp_ext, temp_int, HR_ext, HR_int)
    grafica.dibuja("Cerramiento tipo", muro, temp_ext, temp_int, HR_ext, HR_int, f_Rsi, f_Rsimin, puntos_condensacion, g)
