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

def calculahrint(temperaturas, hrext, G, volumen, n):
    """Humedad relativa interior del mes de enero, dado el ritmo
    de producci�n de humedad interior y la tasa de renovaci�n de aire,
    para el c�lculo de condensaciones superf.
    n - tasa renovaci�n de aire [h^-1]
    V - Volumen de aire del local [m^3]
    G - ritmo de producci�n de la humedad interior [kg/h]
        higrometr�a 3 o inferior - 55%
        higrometr�a 4 - 62%
        hogrometr�a 5 - 70%
    """
    T_e = temperaturas[0]
    T_i = temperaturas[-1]
    T_si = temperaturas[-2]
    delta_v = G / (n * V)
    Pext = pvapor(T_e, hrext)
    delta_p = 462.0 * delta_v * (T_i + T_e) / 2.0
    Pi = Pext + delta_p
    Psi = psat(T_si)
    hrint = 100.0 * Pi / Psi
    return hrint

def calculaU(R_total):
    """Transmitancia t�rmica del cerramiento"""
    return 1.0 / R_total

def calculafRsi(U):
    return 1.0 - U * 0.25

def calculafRsimin(tempext, hrint):
    p_i = hrint * 2337 / 100.0
    p_sat = p_i / 0.8
    temp_si_min = 237.3 * math.log (p_sat / 610.5) / (17.269 - math.log (p_sat / 610.5))
    return (temp_si_min - tempext) / (20.0 - tempext)

def calculatemperaturas(capas, tempext, tempint, Rs_ext, Rs_int):
    """Devuelve lista de temperaturas:
    temperatura exterior, temperatura superficial exterior,
    temperaturas intersticiales, temperatura superficial interior
    y temperatura interior.
        tempext - temperatura exterior media en el mes de enero
        tempint - temperatura interior de c�lculo (20�C)
        Rs_ext - Resistencia t�rmica superficial exterior
        Rs_int - Resistencia t�rmica superficial interior
    """
    resistencias_capas = [Rs_ext] + R_capas(capas) + [Rs_int]
    rtotal = R_total(capas, Rs_ext, Rs_int)
    temperaturas = [tempext]
    for capa_Ri in resistencias_capas:
        tempj = temperaturas[-1] + capa_Ri * (tempint - tempext) / rtotal
        temperaturas.append(tempj)
    return temperaturas

def calculapresiones(capas, temp_ext, temp_int, HR_ext, HR_int):
    """Devuelve una lista de presiones de vapor
    presi�n de vapor al exterior, presiones de vapor intermedias y presi�n de vapor interior.
    """
    pres_ext = pvapor(temp_ext, HR_ext)
    pres_int = pvapor(temp_int, HR_int)
    Espesor_aire_capas = S_capas(capas)
    S_total = sum(Espesor_aire_capas)
    # La presi�n al exterior es constante, en el aire y la superficie exterior de cerramiento
    presiones_vapor = [pres_ext, pres_ext]
    for capa_Si in Espesor_aire_capas:
        pres_j = presiones_vapor[-1] + capa_Si * (pres_int - pres_ext) / S_total
        presiones_vapor.append(pres_j)
    # La presi�n interior es constante, en la superficie interior de cerramiento y en el aire
    presiones_vapor.append(pres_int)
    return presiones_vapor

def calculapresionessat(temperaturas):
    return [psat(temperatura) for temperatura in temperaturas]


if __name__ == "__main__":
    #Datos clim�ticos Sevilla
    T_e_med = [10.7, 11.9, 14.0, 16.0, 19.6, 23.4, 26.8, 26.8, 24.4, 19.5, 14.3, 11.1]
    HR_med = [79, 75, 68, 65, 59, 56, 51, 52, 58, 67, 76, 79]
    delta_altura = 0 #diferencia de altura con la capital de provincia (en m)

    #Datos Sevilla enero: Te=10.7�C, HR=79%
    temp_ext = 10.7 #Temperatura enero
    HR_ext = 79 #Humedad relativa enero
    temp_int = 20
    HR_int = 55 #seg�n clase de higrometr�a: 3:55%, 4:62%, 5:70%
    #XXX: La humedad interior se podr�a calcular con calculahrint y datos de generaci�n de
    # vapor de agua (higrometr�a, ventilaci�n, temperatura superficial interior y temp. ext...

    # Datos constructivos
    #Resistencia t�rmica                    e       mu      K       R       S
    #Nombre                                 [m]     [-]     [W/mK]  [m�K/W] [m]
    #1/2 pie LP m�trico o catal�n 40 mm<    0.11    10      0.69    0.16    1.1
    #Mortero_de_�ridos_ligeros_[vermiculita 0.01    10      0.41    0.02    0.1
    #EPS Poliestireno Expandido             0.03    20      0.037   0.81    0.6
    #Tabique de LH sencillo [40 mm < Esp    0.03    10      0.44    0.07    0.3
    #Enlucido_de_yeso_1000<d<1300           0.01    6       0.57    0.02    0.06
    #Rse                                                            0.04
    #Rsi (cerramientos verticales)                                  0.13
    #Resistencia total (m�K/W)                                      1.25
    capas = [("1/2 pie LP m�trico o catal�n 40 mm<", 0.11, 10.0, 0.69),
            ("Mortero_de_�ridos_ligeros_[vermiculita", 0.01, 10.0, 0.41),
            ("EPS Poliestireno Expandido", 0.03, 20.0, 0.037),
            ("Tabique de LH sencillo [40 mm < Esp", 0.03, 10.0, 0.44),
            ("Enlucido_de_yeso_1000<d<1300", 0.01, 6.0, 0.57),]

    # pasar esto a las funciones, sin usar n y recalcular. Usar siempre capas en llamadas.
    capas_R = R_capas(capas)
    capas_S = S_capas(capas)
    Rs_ext = 0.04
    Rs_int = 0.13
    Rtotal = R_total(capas, Rs_ext, Rs_int) #("Resistencia total (m�K/W)", 1.25)
    U = calculaU(Rtotal) # 0.80 W/m^2K
    S_total = sum(capas_S) # Espesor de aire equivalente total (m), 2.16
    f_Rsi = calculafRsi(U) # 0.80
    f_Rsimin = calculafRsimin(temp_ext, HR_int) # 0.36

    temperaturas = calculatemperaturas(capas, temp_ext, temp_int, Rs_ext, Rs_int)
    presiones_sat = calculapresionessat(temperaturas)
    presiones = calculapresiones(capas, temp_ext, temp_int, HR_ext, HR_int)

    print u"Capas: \n\t", "\n\t".join(nombre_capas(capas))
    print u"Temperaturas: %s" % ["%.1f" % x for x in temperaturas]
    print u"Presiones de saturaci�n: %s" % ["%.2f" % x for x in presiones_sat]
    print u"Presiones de vapor: %s" % ["%.2f" % x for x in presiones]
    print u"Presi�n de vapor exterior: %.2f" % presiones[1] # presi�n de vapor exterior: 1016.00
    print u"Presi�n de vapor interior: %.2f" % presiones[-1] # presi�n de vapor interior: 1285.32

    for pres, pres_sat in zip(presiones, presiones_sat):
        if pres < pres_sat:
            continue
        else:
            print "Se supera la presi�n de saturaci�n"
    # Se puede calcular la humedad relativa interior para casos en los que no se trate
    # de zonas de baja carga interna.
    # Hay que generalizar el c�lculo de la presi�n exterior para la localidad concreta?
    # Calcular exceso de humedad condensado si se da el caso.
    import grafica

    grafica.dibujagrafica("Cerramiento tipo", capas, Rs_ext, Rs_int,
            temperaturas, presiones, presiones_sat, U, HR_int, HR_ext, f_Rsi, f_Rsimin)
