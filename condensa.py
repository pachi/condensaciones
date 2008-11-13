#!/usr/bin/env python
#encoding: iso-8859-15
import math
from capas import *
import operator

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
    delta_v = G / (n * V) # Exceso de humedad interior
    delta_p = 462.0 * delta_v * (T_i + T_e) / 2.0 # Exceso de presión de vapor interna
    return 100.0 * (pvapor(T_e, hrext) + delta_p) / psat(T_si)

def calculahrinthigrometria(temperaturas, hrext, higrometria):
    """Humedad relativa interior del mes de enero, dado el ritmo
    de producción de humedad interior según ISO EN 13788:2002
    higrometría - ritmo de producción de la humedad interior
        Higrometría 1 (zonas de almacenamiento): delta_p = 270 Pa
        Higrometría 2 (oficinas, tiendas): delta_p = 540 Pa
        Higrometría 3 (viviendas residencial): delta_p = 810 Pa
        Higrometría 4 (viviendas alta ocupación, restaurantes, cocinas): delta_p = 1080 Pa
        Higrometría 5 (lavanderías, piscinas, restaurantes): delta_p = 1300 Pa
    """
    T_e = temperaturas[0]
    T_i = temperaturas[-1]
    T_si = temperaturas[-2]
    # delta_p: exceso de presión interna
    if higrometria == 1:
        if T_e <=0.0:
            delta_p = 270.0
        elif T_e < 20.0:
            delta_p = 270.0 - 13.5 * (20.0 - T_e)
        else:
            delta_p = 0.0
    elif higrometria == 2:
        if T_e <=0.0:
            delta_p = 540.0
        elif T_e < 20.0:
            delta_p = 540.0 - 27.0 * (20.0 - T_e)
        else:
            delta_p = 0.0
    elif higrometria == 3:
        if T_e <=0.0:
            delta_p = 810.0
        elif T_e < 20.0:
            delta_p = 810.0 - 40.5 * (20.0 - T_e)
        else:
            delta_p = 0.0
    elif higrometria == 4:
        if T_e <=0.0:
            delta_p = 1080.0
        elif T_e < 20.0:
            delta_p = 1080.0 - 54.0 * (20.0 - T_e)
        else:
            delta_p = 0.0
    else:
        delta_p = 1300.0
    return 100.0 * (pvapor(T_e, hrext) + delta_p) / psat(T_si)

def calculahrinthigrometriaCTE(higrometria):
    """Humedad relativa interior del mes de enero, según CTE
    """
    if higrometria == 5:
        return 70.0
    elif higrometria == 4:
        return 62.0
    elif higrometria <= 3:
        return 55.0
    else:
        raise "Higrometría no definida"

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

def tasatransferenciavapor(pe, pi, Se, Si):
    """Tasa de transferencia de vapor a través del cerramiento g/m2.s
    Sirve para calcular condensada o evaporada entre interfases.
        pe - presión de vapor exterior
        pi - presión de vapor interior
        Se - espesor de aire equivalente en pe
        Si - espesor de aire equivalente en pi
        delta0 -permeabilidad al vapor de agua del aire en relación a la
            presión parcial de vapor (en g/m.s.Pa)x(tiempo)
    """
    delta0 = 2.0 * 10.0**(-7.0) #delta0 -> [g/(m.s.Pa)]
    return delta0 * (pi - pe) / (Si - Se) #g/(m2.s)

def calculacantidadcondensacion(capas, presiones, presiones_sat):
    """Calcular cantidad de condensación y coordenadas (S, presión de vapor)
    de los planos de condensación.
    Devuelve g, puntos_condensacion
    """
    # calculamos las posiciones x, y correspondientes a espesor de aire equivalente
    # y presiones de saturación
    Scapas = S_capas(capas)
    x_jo = [0.0] + [reduce(operator.add, Scapas[:i]) for i in range(1,len(Scapas)+1)]
    y_jo = [presiones[1]] + [p for p in presiones_sat[2:-2]] + [presiones[-1]]

    # Calculamos la envolvente convexa inferior de la linea de presiones de saturación
    # partiendo de presion_exterior y presion_interior como extremos.
    # Los puntos de tangencia son los planos de condensación
    def _giraIzquierda((p, q, r)):
        "¿Forman los vectores pq:qr un giro a la izquierda?"
        _det = ((q[0]*r[1] + p[0]*q[1] + r[0]*p[1]) -
                (q[0]*p[1] + r[0]*q[1] + p[0]*r[1]))
        return (_det > 0) or False

    puntos = [(x, y) for x, y in zip(x_jo, y_jo)]
    envolvente_inf = [puntos[0], puntos[1]]
    for p in puntos[2:]:
        envolvente_inf.append(p)
        while len(envolvente_inf) > 2 and not _giraIzquierda(envolvente_inf[-3:]):
            del envolvente_inf[-2]
    x_j = [x for x, y in envolvente_inf]
    y_j = [y for x, y in envolvente_inf]
    # condensaciones g/m2.s
    g = [(tasatransferenciavapor(y_j[n+1], y_j[n+2], x_j[n+1], x_j[n+2]) -
        tasatransferenciavapor(y_j[n], y_j[n+1], x_j[n], x_j[n+1]))
        for n in range(len(y_j) - 2)]
    return g, envolvente_inf

def calculacantidadevaporacion(capas, presiones, presiones_sat, interfases):
    """Calcular cantidad de evaporacion devolver coordenadas (S, presión de vapor)
    Devuelve g, puntos_evaporacion
    """
    # calculamos las posiciones x, y correspondientes a espesor de aire equivalente
    # y presiones de saturación
    Scapas = S_capas(capas)
    x_jo = [0.0] + [reduce(operator.add, Scapas[:i]) for i in range(1,len(Scapas)+1)]
    y_jo = [presiones[1]] + [p for p in presiones_sat[2:-2]] + [presiones[-1]]

    puntos_evaporacion = [(x_jo[i], y_jo[i]) for i in interfases]
    envolvente_inf = [(x_jo[0], y_jo[0])] + puntos_evaporacion + [(x_jo[-1], y_jo[-1])]
    x_j = [x for x, y in envolvente_inf]
    y_j = [y for x, y in envolvente_inf]
    # evaporaciones g/m2.s
    g = [(tasatransferenciavapor(y_j[n+1], y_j[n+2], x_j[n+1], x_j[n+2]) -
        tasatransferenciavapor(y_j[n], y_j[n+1], x_j[n], x_j[n+1]))
        for n in range(len(y_j) - 2)]
    return g, envolvente_inf

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
    espesor_aire_capas = S_capas(capas)
    S_total = sum(espesor_aire_capas)
    # La presión al exterior es constante, en el aire y la superficie exterior de cerramiento
    presiones_vapor = [pres_ext, pres_ext]
    for capa_Si in espesor_aire_capas:
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
    condensa = False
    for presion_i, presion_sat_i in zip(presiones, presiones_sat):
        if presion_i >= presion_sat_i:
            condensa = True
    return condensa

if __name__ == "__main__":
    import datos_ejemplo

    def stringify(list, prec):
        format = '%%.%if' % prec
        return "[" + ", ".join([format % item for item in list]) + "]"
    #Datos climáticos Sevilla
    T_e_med = [10.7, 11.9, 14.0, 16.0, 19.6, 23.4, 26.8, 26.8, 24.4, 19.5, 14.3, 11.1]
    HR_med = [79, 75, 68, 65, 59, 56, 51, 52, 58, 67, 76, 79]
    delta_altura = 0 #diferencia de altura con la capital de provincia (en m)

    #Datos Sevilla enero: Te=10.7ºC, HR=79%
    temp_ext = 10.7 #Temperatura enero
    HR_ext = 79 #Humedad relativa enero
    temp_int = 20
    HR_int = 55 #según clase de higrometría: 3:55%, 4:62%, 5:70%
    higrometria = 3
    #XXX: La humedad interior se podría calcular con calculahrint y datos de generación de
    # vapor de agua (higrometría, ventilación, temperatura superficial interior y temp. ext...
    # Hay que generalizar el cálculo de la presión exterior para la localidad concreta?
    # Calcular exceso de humedad condensado si se da el caso.

    # Datos constructivos
    capas = datos_ejemplo.capas
    Rs_ext = 0.04
    Rs_int = 0.13

    capas_R = R_capas(capas)
    capas_S = S_capas(capas)
    Rtotal = R_total(capas, Rs_ext, Rs_int) #("Resistencia total (m²K/W)", 1.25)
    U = calculaU(capas, Rs_ext, Rs_int) # 0.80 W/m^2K = 1/Rtotal
    S_total = sum(capas_S) # Espesor de aire equivalente total (m), 2.16
    f_Rsi = calculafRsi(U) # 0.80
    f_Rsimin = calculafRsimin(HR_int, temp_ext) # 0.36
    temperaturas = calculatemperaturas(capas, temp_ext, temp_int, Rs_ext, Rs_int)
    hrint = calculahrinthigrometria(temperaturas, HR_ext, higrometria=higrometria)
    presiones_sat = calculapresionessat(temperaturas)
    #presiones = calculapresiones(capas, temp_ext, temp_int, HR_ext, hrint)
    presiones = calculapresiones(capas, temp_ext, temp_int, HR_ext, HR_int)
    p_ext = presiones[1]
    p_int = presiones[-1]
    g_total = tasatransferenciavapor(p_ext, p_int, 0.0, S_total) #0,0898 g/m2.s
    # Para calcular cantidades condensadas:
    g, puntos_condensacion = calculacantidadcondensacion(capas, presiones, presiones_sat)
    g, puntos_evaporacion = calculacantidadevaporacion(capas, presiones, presiones_sat, interfases=[2])

    # Temperaturas: [10.7, 11.0, 12.2, 12.4, 18.4, 18.9, 19.0, 20.0]
    # Presiones de saturación: [1286.08, 1311.79, 1418.84, 1435.87, 2114.68, 2182.84, 2200.69, 2336.95]
    # Presiones de vapor: [1016.00, 1016.00, 1153.16, 1165.62, 1240.44, 1277.84, 1285.32, 1285.32]
    print u"Capas: \n\t", "\n\t".join(nombre_capas(capas))
    print u"Temperaturas:\n\t", stringify(temperaturas, 1)
    print u"Humedad relativa interior para higrometría 3: %.2f" % hrint #
    print u"Presiones de saturación:\n\t", stringify(presiones_sat, 1)
    print u"Presiones de vapor:\n\t", stringify(presiones, 1)
    print u"\tPresión de vapor exterior: %.2f" % p_ext # presión de vapor exterior: 1016.00
    print u"\tPresión de vapor interior: %.2f" % p_int # presión de vapor interior: 1285.32
    c_sup = compruebacsuperificiales(f_Rsi, f_Rsimin) and u"Sí" or "No"
    print u"Condensaciones superficiales (%s)" % c_sup
    print u"\tfRsi = %.2f, fRsimin = %.2f" % (f_Rsi, f_Rsimin)
    c_int = compuebacintersticiales(presiones, presiones_sat) and u"Sí" or "No"
    print u"Condensaciones intersticiales (%s)" % c_int
    print u"\tTasa de transferencia de vapor %.3f x 10^-3[g/(h.m2)]" % (g_total * 3600.0,)

    import grafica
    grafica.dibujapresionestemperaturas("Cerramiento tipo", capas, Rs_ext, Rs_int,
            temperaturas, presiones, presiones_sat, U, HR_int, HR_ext, f_Rsi, f_Rsimin)
#     grafica.dibujapresiones(capas, puntos_condensacion, presiones, presiones_sat, g)
#     grafica.dibujapresiones(capas, puntos_evaporacion, presiones, presiones_sat, g)
