#!/usr/bin/env python
#encoding: iso-8859-15

import math

def calculafRsi(U):
    """Factor de temperatura de la superficie interior de un cerramiento, partición
    interior o puentes térmicos INTEGRADOS en los cerramientos.
    """
    return 1.0 - U * 0.25

def calculafRsimin(hrint, tempext, tempint=20.0):
    """Factor de temperatura de la superficie interior mínnimo aceptable de un puente
    térmico, cerramiento o partición interior.
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
    import capas
    import grafica

    temp_ext = 10.7 #Temperatura enero
    HR_ext = 79 #Humedad relativa enero
    temp_int = 20
    HR_int = 55 #según clase de higrometría: 3:55%, 4:62%, 5:70%

    # Datos constructivos
    muro = capas.Cerramiento(datos_ejemplo.capas, 0.04, 0.13)
    presiones = muro.calculapresiones(temp_ext, temp_int, HR_ext, HR_int)
    presiones_sat = muro.calculapresionessat(temp_ext, temp_int)

    f_Rsi = calculafRsi(muro.U) # 0.80
    f_Rsimin = calculafRsimin(HR_int, temp_ext) # 0.36

    print u"Capas: \n\t", "\n\t".join(muro.nombre_capas)
    print
    c_sup = compruebacsuperificiales(f_Rsi, f_Rsimin) and u"Sí" or "No"
    print u"Condensaciones superficiales (%s)" % c_sup
    print u"\tfRsi = %.2f, fRsimin = %.2f" % (f_Rsi, f_Rsimin)
    c_int = compuebacintersticiales(presiones, presiones_sat) and u"Sí" or "No"
    print u"Condensaciones intersticiales (%s)" % c_int

    grafica.dibujapresionestemperaturas("Cerramiento tipo", muro,
            temp_ext, temp_int, HR_int, HR_ext, f_Rsi, f_Rsimin)
