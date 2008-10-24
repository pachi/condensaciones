#/usr/bin/env python
#encoding: iso-8859-15
import math

def psat(temp):
    """Presión de saturación - temp en ºC"""
    if temp >0.0:
        return 610.5 * math.exp(17.269 * temp / (237.3 + temp))
    else:
        return 610.5 * math.exp(21.875 * temp / (267.5 + temp))

def pvapor(temp, humedad):
    """Presión de vapor - temp en ºC y humedad en tanto por uno.
    temp - temperatura media exterior para el mes dado
    humedad - humedad relativa media para el mes dado"""
    return (humedad / 100.0) * psat(temp)

def temploc(temp, delta_alt):
    """Temperatura de la localidad en función de la temperatura de
    la capital de provincia y la diferencia de altitud entre ellas.
    temp - temperatura media exterior de la capital para el mes dado
    delta_alt - altura de la localidad sobre la de la capital."""
    return temp - 1.0 * delta_alt / 100.0

def psatloc(temp, delta_alt):
    """Presión de saturación en una localidad situada a una altitud
    distinta a la capital de provincia.
    temp - temperatura media exterior de la capital para el mes dado
    delta_alt - altura de la localidad sobre la de la capital."""
    return psat(temploc(temp, delta_alt))

def hrelloc(temp, humedad, delta_alt):
    """Humedad relativa para la localidad situada a una diferencia
    de altitud dada sobre la capital de provincia.
    temp - temperatura media exterior de la capital para el mes dado
    humedad - humedad relativa media de la capital para el mes dado
    delta_alt - altura de la localidad sobre la de la capital."""
    return pvapor(temp, humedad) / (psatloc(temp, delta_alt) * temploc(temp, delta_alt))

def humrelint(tempext, tempint, Pe, Psat, G, volumen, n):
    """Humedad relativa interior del mes de enero, dado el ritmo
    de producción de humedad interior y la tasa de renovación de aire,
    para el cálculo de condensaciones superf."""
    #TODO
    delta_v = G / (n * V)
    delta_p = 462.0 * delta_v * (tempint + tempext) / 2.0
    Pi = Pe + delta_p
    Pe = 1.0 #??
    Psat = 1.0 #??
    return

def tempsup(tempext, tempint, Rtotal, Rk, tempj):
    """Temperatura en interfase de la capa n (con la capa n-1)
    temp(n) = temp(n-1) + R(n)/Rtotal * (tempint - tempext)
    tempext - temperatura exterior media en el mes de enero
    tempint - temperatura interior de cálculo (20ºC)
    Rtotal - Resistencia térmica total del elemento constructivo (m2K/W)
    Rk - Resistencia térmica superficial de la capa n
    tempj - Temperatura de la capa n-1 (text para n=1)"""
    return tempj + Rk * (tempint - tempext) / Rtotal

def calculatempsup(Resistencias_capas, tempext, tempint, R_total):
    """Devuelve lista de temperaturas:
        temperatura exterior, temperatura superficial exterior,
        temperaturas intersticiales, temperatura superficial interior
        y temperatura interior"""
    temps = [tempext]
    for capa_Ri in Resistencias_capas:
        tempj = tempsup(tempext, tempint, R_total, capa_Ri, temps[-1])
        temps.append(tempj)
    return temps

def pressup(pext, pint, Stotal, Sk, Pj):
    """Presión de vapor en capa n (a partir de la capa n-1)
    P(n) = P(n-1) + Sd(n-1) / SUM Sd(n) * (Pint - Pext)
    pext - presión de vapor del aire exterior [Pa]
    pint - presión de vapor del aire interior [Pa]
    Stotal - Espesor de aire equivalente de todas las capas.
    Sk - Espesor de aire equivalente de la capa n
    Pj - Presión de vapor en la capa n-1"""
    return Pj + Sk * (pint - pext) / Stotal

def calculapresvap(Espesor_aire_capas, pext, pint, S_total):
    """Devuelve una lista de presiones de vapor intermedias:
    P(n) = P(n-1) + Sd(n-1) / SUM Sd(n) * (Pint - Pext)"""
    pres = [pext]
    for capa_Si in Espesor_aire_capas:
        presj = pressup(pext, pint, S_total, capa_Si, pres[-1])
        pres.append(presj)
    return pres

if __name__ == "__main__":
    #Datos climáticos Sevilla
    T_e_med = [10.7, 11.9, 14.0, 16.0, 19.6, 23.4, 26.8, 26.8, 24.4, 19.5, 14.3, 11.1]
    HR_med = [79, 75, 68, 65, 59, 56, 51, 52, 58, 67, 76, 79]
    delta_altura = 0 #diferencia de altura con la capital de provincia (en m)

    #Datos Sevilla enero: Te=10.7ºC, HR=79%
    temp_ext = 10.7 #Temperatura enero
    HR_ext = 79 #Humedad relativa enero
    temp_int = 20
    HR_int = 55 #según clase de higrometría: 3:55%, 4:62%, 5:70%

    # Datos constructivos
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

    capas_propiedades = [(str(n), e / K, e * mu) for n, (nombre, e, mu, K) in enumerate(capas)] # (n, Ri, Si)
    capas_R = [prop[1] for prop in capas_propiedades]
    capas_S = [prop[2] for prop in capas_propiedades]

    Rs_ext = 0.04
    Rs_int = 0.13
    R_total = Rs_ext + sum(capas_R) + Rs_int #("Resistencia total (m²K/W)", 1.25)
    S_total = sum(capas_S) #Espesor de aire equivalente total (m), 2.16

    temperaturas = calculatempsup([Rs_ext] + capas_R + [Rs_int], temp_ext, temp_int, R_total)
    presiones_sat = [psat(temperatura) for temperatura in temperaturas]
    pres_ext = pvapor(temp_ext, HR_ext) # presión de vapor exterior: 1016.00
    pres_int = pvapor(temp_int, HR_int) # presión de vapor interior: 1285.32
    presiones = [pres_ext] + calculapresvap(capas_S, pres_ext, pres_int, S_total) + [pres_int]

    print "Capas: ", capas
    print "Propiedades de capas: ", capas_propiedades
    print "Temperaturas: ", temperaturas
    print "Presiones de saturación: ", presiones_sat
    print "Presiones de vapor: ", presiones

    for pres, pres_sat in zip(presiones, presiones_sat):
        if pres < pres_sat:
            continue
        else:
            print "Se supera la presión de saturación"
    # Representar Presiones de saturación vs. Presiones de vapor y temperaturas
    # en un diagrama capa/Presion de vapor y capa/Temp

    # Se puede calcular la humedad relativa interior para casos en los que no se trate
    # de zonas de baja carga interna.
    # Hay que generalizar el cálculo de la presión exterior para la localidad concreta?
    # Calcular exceso de humedad condensado si se da el caso.
