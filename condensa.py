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
    """Presión de saturación - temp en ºC"""
    if temp >0.0:
        return 610.5 * math.exp(17.269 * temp / (237.3 + temp))
    else:
        return 610.5 * math.exp(21.875 * temp / (267.5 + temp))

def pvapor(temp, humedad):
    """Presión de vapor - temp en ºC y humedad en tanto por uno.
        temp - temperatura media exterior para el mes dado
        humedad - humedad relativa media para el mes dado.
    """
    return (humedad / 100.0) * psat(temp)

def temploc(temp, delta_alt):
    """Temperatura de la localidad en función de la temperatura de
    la capital de provincia y la diferencia de altitud entre ellas.
        temp - temperatura media exterior de la capital para el mes dado
        delta_alt - altura de la localidad sobre la de la capital.
    """
    return temp - 1.0 * delta_alt / 100.0

def psatloc(temp, delta_alt):
    """Presión de saturación en una localidad situada a una altitud
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
    de producción de humedad interior y la tasa de renovación de aire,
    para el cálculo de condensaciones superf.
    n - tasa renovación de aire [h^-1]
    V - Volumen de aire del local [m^3]
    G - ritmo de producción de la humedad interior [kg/h]
        higrometría 3 o inferior - 55%
        higrometría 4 - 62%
        hogrometría 5 - 70%
    """
    T_e = temperaturas[0]
    T_i = temperaturas[-1]
    T_si = temperaturas[-2]
    ## XXX: En lugar de delta_p y delta_v se puede usar la higrometría de los locales y T_e según norma
    delta_v = G / (n * V) # Exceso de humedad interior
    delta_p = 462.0 * delta_v * (T_i + T_e) / 2.0 # Exceso de presión de vapor interna
    Pext = pvapor(T_e, hrext)
    # Presión de vapor al interior (la ISO 13788 añade un factor de seguridad 1.10 a delta_p)
    Pi = Pext + delta_p
    # Presión de saturación al interior (la ISO 13788 divide por un factor de seguridad de 0.80)
    Psi = psat(T_si)
    hrint = 100.0 * Pi / Psi
    return hrint

def calculaU(capas, Rs_ext, Rs_int):
    """Transmitancia térmica del cerramiento"""
    return 1.0 / R_total(capas, Rs_ext, Rs_int)

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

def tasatransferenciavapor(pe, pi, S_total):
    """Tasa de transferencia de vapor a través del cerramiento.
    Sirve para calcular condensada o evaporada entre interfases.
        pe - presión de vapor exterior
        pi - presión de vapor interior
        S_total - espesor de aire equivalente total
        delta0 -permeabilidad al vapor de agua del aire en relación a la
            presión parcial de vapor [kg/(m.s.Pa) delta0 = 2.10^-10 kg/(m.s.Pa)
    """
    delta0 = 2.0 * 10.0**(-10.0) #kg/(m.s.Pa)
    return delta0 * (pi - pe) / S_total #kg/(m2.s), ver unidad de tiempo

def calculacantidadcondensacion(presiones, presiones_sat, Scapas):
    #XXX: cómo se calcula según ISO 13788?
    p_e = presiones[1]
    p_i = presiones[-1]
    S_T = sum(Scapas)
    S_acumuladas = []
    S_previa = 0.0
    for Scapa in Scapas:
        S_previa = Scapa + S_previa
        S_acumuladas.append(S_previa)
    indices = [i for i, (p_i, ps_i) in enumerate(zip(presiones, presiones_sat)) if p_i > ps_i]
    p_j = [p_e] + [presiones_sat[i] for i in indices] + [p_i]
    s_j = [0.0] + [S_acumuladas[i-2] for i in indices] + [S_T]
    delta0 = 2.0 * 10.0**(-10.0) * 3600.0 * 24.0 * 30.0 * 1000.0 #g/(m.mes.Pa)
    g = [delta0 * (
        ((p_j[n+2] - p_j[n+1]) / (s_j[n+2] - s_j[n+1])) -
        ((p_j[n+1] - p_j[n]) / (s_j[n+1] - s_j[n]))
        ) for n in range(len(indices))]
    # condensaciones g/m2.mes
    # Representar presiones vs. S
    import pylab
    s_todas = [0.0, 0.0] + S_acumuladas + [sum(capas_S)]
    pylab.plot(s_todas, presiones_sat, 'k-', label='p_sat')
    pylab.plot(s_j, p_j, 'b-', label='p_vap')
    pylab.legend()
    pylab.figtext(0.15, .85, "Cantidades condensadas: %s" % g)
    pylab.figtext(0.15, .80, "Total: %.2f" % sum(g))
    pylab.show()


def calculatemperaturas(capas, tempext, tempint, Rs_ext, Rs_int):
    """Devuelve lista de temperaturas:
    temperatura exterior, temperatura superficial exterior,
    temperaturas intersticiales, temperatura superficial interior
    y temperatura interior.
        tempext - temperatura exterior media en el mes de enero
        tempint - temperatura interior de cálculo (20ºC)
        Rs_ext - Resistencia térmica superficial exterior
        Rs_int - Resistencia térmica superficial interior
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
    presión de vapor al exterior, presiones de vapor intermedias y presión de vapor interior.
    """
    pres_ext = pvapor(temp_ext, HR_ext)
    pres_int = pvapor(temp_int, HR_int)
    Espesor_aire_capas = S_capas(capas)
    S_total = sum(Espesor_aire_capas)
    # La presión al exterior es constante, en el aire y la superficie exterior de cerramiento
    presiones_vapor = [pres_ext, pres_ext]
    for capa_Si in Espesor_aire_capas:
        pres_j = presiones_vapor[-1] + capa_Si * (pres_int - pres_ext) / S_total
        presiones_vapor.append(pres_j)
    # La presión interior es constante, en la superficie interior de cerramiento y en el aire
    presiones_vapor.append(pres_int)
    return presiones_vapor

def calculapresionessat(temperaturas):
    return [psat(temperatura) for temperatura in temperaturas]

def compruebacsuperificiales(fRsi, fRsimin):
    """Comprueba la condición de existencia de condensaciones superficiales en un
    cerramiento o puente térmico.
    Devuelve la comprobación y el valor de fRsi y fRsimin
    """
    # TODO: el CTE incluye tablas según zonas y clase de higrometría para fRsimin
    return fRsi > fRsimin

def compuebacintersticiales(presiones, presiones_sat):
    """Comprueba la condición de existencia de condensaciones intersticiales en un
    cerramiento o puente térmico.
    Devuelve la comprobación
    """
    #TODO: devolver la cantidad condensada (s/ UNE EN ISO 13788:2002)
    condensa = False
    for presion_i, presion_sat_i in zip(presiones, presiones_sat):
        if presion_i >= presion_sat_i:
            condensa = True
    return condensa


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
    #XXX: La humedad interior se podría calcular con calculahrint y datos de generación de
    # vapor de agua (higrometría, ventilación, temperatura superficial interior y temp. ext...
    # Hay que generalizar el cálculo de la presión exterior para la localidad concreta?
    # Calcular exceso de humedad condensado si se da el caso.

    # Datos constructivos
    Rs_ext = 0.04
    Rs_int = 0.13
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

    capas_R = R_capas(capas)
    capas_S = S_capas(capas)
    Rtotal = R_total(capas, Rs_ext, Rs_int) #("Resistencia total (m²K/W)", 1.25)
    U = calculaU(capas, Rs_ext, Rs_int) # 0.80 W/m^2K = 1/Rtotal
    S_total = sum(capas_S) # Espesor de aire equivalente total (m), 2.16
    f_Rsi = calculafRsi(U) # 0.80
    f_Rsimin = calculafRsimin(HR_int, temp_ext) # 0.36
    temperaturas = calculatemperaturas(capas, temp_ext, temp_int, Rs_ext, Rs_int)
    presiones_sat = calculapresionessat(temperaturas)
    presiones = calculapresiones(capas, temp_ext, temp_int, HR_ext, HR_int)
    p_ext = presiones[1]
    p_int = presiones[-1]
    g = tasatransferenciavapor(p_ext, p_int, S_total)

    # Temperaturas: [10.7, 11.0, 12.2, 12.4, 18.4, 18.9, 19.0, 20.0]
    # Presiones de saturación: [1286.08, 1311.79, 1418.84, 1435.87, 2114.68, 2182.84, 2200.69, 2336.95]
    # Presiones de vapor: [1016.00, 1016.00, 1153.16, 1165.62, 1240.44, 1277.84, 1285.32, 1285.32]
    print u"Capas: \n\t", "\n\t".join(nombre_capas(capas))
    print u"Temperaturas: %s" % ["%.1f" % x for x in temperaturas]
    print u"Presiones de saturación: %s" % ["%.2f" % x for x in presiones_sat]
    print u"Presiones de vapor: %s" % ["%.2f" % x for x in presiones]
    print u"Presión de vapor exterior: %.2f" % p_ext # presión de vapor exterior: 1016.00
    print u"Presión de vapor interior: %.2f" % p_int # presión de vapor interior: 1285.32
    c_sup = compruebacsuperificiales(f_Rsi, f_Rsimin)
    print u"Condensaciones superficiales (%s) - fRsi = %.2f, fRsimin = %.2f" % (c_sup, f_Rsi, f_Rsimin)
    print u"Condensaciones intersticiales (%s)" % compuebacintersticiales(presiones, presiones_sat)
    print u"Tasa de transferencia de vapor %.3f x 10^-3[kg/(h.m2)]" % (g * 1000.0 * 3600,)

#     import grafica
#     grafica.dibujagrafica("Cerramiento tipo", capas, Rs_ext, Rs_int,
#             temperaturas, presiones, presiones_sat, U, HR_int, HR_ext, f_Rsi, f_Rsimin)

    # Para calcular cantidades condensadas:
    presiones =     [1016.00, 1016.00, 1453.16, 1465.62, 1240.44, 1277.84, 1285.32, 1285.32]
    presiones_sat = [1286.08, 1311.79, 1418.84, 1435.87, 2114.68, 2182.84, 2200.69, 2336.95]
    calculacantidadcondensacion(presiones, presiones_sat, capas_S)
