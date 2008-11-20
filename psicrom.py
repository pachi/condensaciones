#!/usr/bin/env python
#encoding: iso-8859-15

"""Relaciones psicrom�tricas"""
# TODO: Hay que generalizar el c�lculo de la presi�n exterior para la localidad concreta?

import math
from capas import *
import operator

def psat(temp):
    """Presi�n de saturaci�n - temp en �C"""
    if temp >0.0:
        return 610.5 * math.exp(17.269 * temp / (237.3 + temp))
    else:
        return 610.5 * math.exp(21.875 * temp / (267.5 + temp))

def pvapor(temp, humedad):
    """Presi�n de vapor - temp en �C y humedad en tanto por uno.
        temp - temperatura media exterior para el mes dado
        humedad - humedad relativa media para el mes dado.
    """
    return (humedad / 100.0) * psat(temp)

def temploc(temp, delta_alt):
    """Temperatura de la localidad en funci�n de la temperatura de
    la capital de provincia y la diferencia de altitud entre ellas.
        temp - temperatura media exterior de la capital para el mes dado
        delta_alt - altura de la localidad sobre la de la capital.
    """
    return temp - 1.0 * delta_alt / 100.0

def psatloc(temp, delta_alt):
    """Presi�n de saturaci�n en una localidad situada a una altitud
    distinta a la capital de provincia.
        temp - temperatura media exterior de la capital para el mes dado
        delta_alt - altura de la localidad sobre la de la capital.
    """
    return psat(temploc(temp, delta_alt))

def hrloc(temp, humedad, delta_alt):
    """Humedad relativa para la localidad situada a una diferencia
    de altitud dada sobre la capital de provincia.
        temp - temperatura media exterior de la capital para el mes dado
        humedad - humedad relativa media de la capital para el mes dado
        delta_alt - altura de la localidad sobre la de la capital.
    """
    return pvapor(temp, humedad) / (psatloc(temp, delta_alt) * temploc(temp, delta_alt))

def tasatransferenciavapor(pe, pi, Se, Si):
    """Tasa de transferencia de vapor a trav�s del cerramiento g/m2.s
    Sirve para calcular condensada o evaporada entre interfases.
        pe - presi�n de vapor exterior
        pi - presi�n de vapor interior
        Se - espesor de aire equivalente en pe
        Si - espesor de aire equivalente en pi
        delta0 -permeabilidad al vapor de agua del aire en relaci�n a la
            presi�n parcial de vapor (en g/m.s.Pa)x(tiempo)
    """
    delta0 = 2.0 * 10.0**(-7.0) #delta0 -> [g/(m.s.Pa)]
    return delta0 * (pi - pe) / (Si - Se) #g/(m2.s)

def calculahrinthigrometria(temp_ext, temp_sint, hrext, higrometria):
    """Humedad relativa interior del mes de enero, dado el ritmo
    de producci�n de humedad interior seg�n ISO EN 13788:2002
    higrometr�a - ritmo de producci�n de la humedad interior
        Higrometr�a 1 (zonas de almacenamiento): delta_p = 270 Pa
        Higrometr�a 2 (oficinas, tiendas): delta_p = 540 Pa
        Higrometr�a 3 (viviendas residencial): delta_p = 810 Pa
        Higrometr�a 4 (viviendas alta ocupaci�n, restaurantes, cocinas): delta_p = 1080 Pa
        Higrometr�a 5 (lavander�as, piscinas, restaurantes): delta_p = 1300 Pa
    """
    # delta_p: exceso de presi�n interna
    if higrometria == 1:
        if temp_ext <=0.0:
            delta_p = 270.0
        elif temp_ext < 20.0:
            delta_p = 270.0 - 13.5 * (20.0 - temp_ext)
        else:
            delta_p = 0.0
    elif higrometria == 2:
        if temp_ext <=0.0:
            delta_p = 540.0
        elif temp_ext < 20.0:
            delta_p = 540.0 - 27.0 * (20.0 - temp_ext)
        else:
            delta_p = 0.0
    elif higrometria == 3:
        if temp_ext <=0.0:
            delta_p = 810.0
        elif temp_ext < 20.0:
            delta_p = 810.0 - 40.5 * (20.0 - temp_ext)
        else:
            delta_p = 0.0
    elif higrometria == 4:
        if temp_ext <=0.0:
            delta_p = 1080.0
        elif temp_ext < 20.0:
            delta_p = 1080.0 - 54.0 * (20.0 - temp_ext)
        else:
            delta_p = 0.0
    else:
        delta_p = 1300.0
    return 100.0 * (psicrom.pvapor(temp_ext, hrext) + delta_p) / psicrom.psat(temp_sint)

def calculahrintCTE(temp_ext, temp_int, temp_sint, hrext, G, volumen, n):
    """Humedad relativa interior del mes de enero, dado el ritmo
    de producci�n de humedad interior y la tasa de renovaci�n de aire,
    para el c�lculo de condensaciones superf.
    temp_ext - temperatura exterior
    temp_int - temperatura interior
    temp_sint - temperatura superficial interior
    n - tasa renovaci�n de aire [h^-1]
    V - Volumen de aire del local [m^3]
    G - ritmo de producci�n de la humedad interior [kg/h]
        higrometr�a 3 o inferior - 55%
        higrometr�a 4 - 62%
        hogrometr�a 5 - 70%
    """
    delta_v = G / (n * volumen) # Exceso de humedad interior
    delta_p = 462.0 * delta_v * (temp_int + temp_ext) / 2.0 # Exceso de presi�n de vapor interna
    return 100.0 * (psicrom.pvapor(temp_ext, hrext) + delta_p) / psicrom.psat(temp_sint)

def calculahrinthigrometriaCTE(higrometria):
    """Humedad relativa interior del mes de enero, seg�n CTE
    """
    if higrometria == 5:
        return 70.0
    elif higrometria == 4:
        return 62.0
    elif higrometria <= 3:
        return 55.0
    else:
        raise "Higrometr�a no definida"

if __name__ == "__main__":
    import datos_ejemplo

    #Datos Sevilla enero: Te=10.7�C, HR=79%
    temp_ext = 10.7 #Temperatura enero
    HR_ext = 79 #Humedad relativa enero
    temp_int = 20
    HR_int = 55 #seg�n clase de higrometr�a: 3:55%, 4:62%, 5:70%
    higrometria = 3

    # Datos constructivos
    Rs_ext = 0.04
    Rs_int = 0.13
    muro = Cerramiento(datos_ejemplo.capas, Rs_ext, Rs_int)
    # datos calculados
    temp_sint = 19.0330684375
    G = 0.55 #higrometr�a 3
    volumen = 10 #m3
    n = 1 #[h^-1]

    hrint = calculahrinthigrometria(temp_ext, temp_sint, HR_ext, higrometria=higrometria) #65.86%
    hrintCTE = calculahrintCTE(temp_ext, temp_int, temp_sint, HR_ext, G, volumen, n)
    hrinthigroCTE = calculahrinthigrometriaCTE(3)
    g_total = tasatransferenciavapor(1016.00114017, 1285.32312909, 0.0, 2.16) #0,0898 g/m2.s

    print u"Humedad relativa interior para higrometr�a 3: %.2f" % hrint #65.86%
    print u"Humedad relativa interior para V=%.2f, G=%.2f, n=%.2f (CTE): %.2f" % (volumen, G, n, hrintCTE) #63.89%
    print u"Humedad relativa interior para higrometr�a 3 (CTE): %.2f" % hrinthigroCTE #55.00%
    print u"\tTasa de transferencia de vapor %.4f x 10^-3[g/(h.m2)]" % (g_total * 3600.0,) #0,0898 g/m2.s