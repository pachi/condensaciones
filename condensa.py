#!/usr/bin/env python
#encoding: iso-8859-15
import math
from pylab import *

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
    delta_v = G / (n * V)
    Pext = pvapor(T_e, hrext)
    delta_p = 462.0 * delta_v * (T_i + T_e) / 2.0
    Pi = Pext + delta_p
    Psi = psat(T_si)
    hrint = 100.0 * Pi / Psi
    return hrint

def calculaU(R_total):
    """Transmitancia térmica del cerramiento"""
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

def colorlist(steps):
    import colorsys
    clist =[]
    salto_color = 0.0
    for i in range(steps):
        color = colorsys.hls_to_rgb(salto_color, .5, .7)
        clist.append(color)
        salto_color += 1.0/steps
    return clist

def dibujagrafica(nombre, capas, Rs_ext, Rs_int, temperaturas, presiones, presiones_sat, U, HR_int, HR_ext):
    # Representar Presiones de saturación vs. Presiones de vapor y temperaturas
    # en un diagrama capa/Presion de vapor y capa/Temp
    T_e = temperaturas[0]
    T_i = temperaturas[-1]
    T_se = temperaturas[1]
    T_si = temperaturas[-2]
    P_se = presiones[1]
    P_sat_se = presiones_sat[1]
    Rtotal = R_total(capas, Rs_ext, Rs_int)
    U = calculaU(Rtotal)
    f_Rsi = calculafRsi(U)
    f_Rsimin = calculafRsimin(T_e, HR_int)
    # TODO: Indicar si cumple f_Rsi > f_Rsi,min, T_si > T_si,min, P > P_sat, etc

    margen_lateral = 0.025
    rotulos = [-margen_lateral, 0.0]
    for elemento in [e for nombre, e, mu, K in capas]:
        nuevo = rotulos[-1] + elemento
        rotulos.append(nuevo)
    rotulos.append(rotulos[-1] + margen_lateral)
    rotulo_se = rotulos[1]
    rotulo_si = rotulos[-2]

    sp1 = subplot(111)
    subplots_adjust(bottom=0.15, top=0.87) # ampliar márgenes

    figtext(0.5, 0.98,
            r'$U = %.2f W/m^2K,\,f_{Rsi} = %.2f,\, f_{Rsi,min} = %.2f$' % (U, f_Rsi, f_Rsimin),
            fontsize='large',
            bbox=dict(facecolor='red', alpha=0.25),
            verticalalignment='top',
            horizontalalignment='center')
    figtext(0.5, 0.03,
            r'$T_{int} = %.2f^\circ C, \, HR_{int} = %.1f\%%, \,'
            'T_{ext} = %.2f^\circ C, \, HR_{ext} = %.1f\%%$' % (T_i, HR_int, T_e, HR_ext),
            fontsize='large',
            bbox=dict(facecolor='blue', alpha=0.25),
            horizontalalignment='center')

    title(u"Presiones de vapor (efectiva y de saturación) y temperaturas")
    xlabel(u"Distancia [m]")
    ylabel(u"Presión de vapor [Pa]", fontdict=dict(color='b'))
    text(0.5, 0.97,
            nombre,
            transform=sp1.transAxes,
            verticalalignment='top',
            horizontalalignment='center',
            fontsize=12,
            fontstyle='italic')
    # Lineas de tramos de cerramiento
    print "Número colores:", len(rotulos)
    colors = colorlist(len(rotulos) - 2) # genera gradiente colores
    axvline(rotulo_se, linewidth=2, color='k', ymin=.05, ymax=.9)
    rotuloanterior = rotulo_se
    for rotulo, color in zip(rotulos[2:-2], colors):
        axvspan(rotuloanterior, rotulo, facecolor=color, alpha=0.25, ymin=.05, ymax=.9)
        axvline(rotulo, color='0.5', ymin=.05, ymax=.9)
        rotuloanterior = rotulo
    #TODO: cambiar color de fondo añadiendo un paso más a colors
    axvspan(rotuloanterior, rotulo_si, facecolor='#fff600', alpha=0.25, ymin=.05, ymax=.9)
    axvline(rotulo_si, linewidth=2, color='k', ymin=.05, ymax=.9)

    # lineas de datos
    plot(rotulos, presiones, 'b-', linewidth=0.5)
    plot(rotulos, presiones_sat, 'b-', linewidth=1.5)
    # Rótulos de lineas de presiones
    annotate(r'$P_{n}$',
            xy=(rotulo_se - 0.002, P_se),
            horizontalalignment='right')
    annotate(r'$P_{sat}$',
            xy=(rotulo_se - 0.002, P_sat_se),
            horizontalalignment='right')

    # incrementar extensión de límites de ejes para hacer hueco
    ymin, ymax = ylim()
    ylim(ymin-ymin/10.0, ymax+ymax/10.0)

    # Nuevo eje vertical de temperaturas
    ax2 = twinx()
    ylabel(u"Temperatura [ºC]", fontdict=dict(color='r'))
    # curva de temperaturas
    plot(rotulos, temperaturas, 'r:')
    # Valores de T_si y T_se
    annotate(r'$T_{se}=%.1f^\circ C$' % T_se,
            xy=(rotulos[1] - 0.002, T_se),
            horizontalalignment='right')
    annotate(r'$T_{si}=%.1f^\circ C$' % T_si,
            xy=(rotulos[-2] + 0.002, T_si),
            horizontalalignment='left',
            verticalalignment='top')
    ax2.yaxis.tick_right()
    # extender eje para evitar coincidencia con curvas de presiones
    ymin, ymax = ylim()
    ylim(ymin-ymin/10.0, ymax+ymax/5.0)
    # guardar y mostrar gráfica
    #savefig('presionesplot.png')
    show()

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

    # pasar esto a las funciones, sin usar n y recalcular. Usar siempre capas en llamadas.
    capas_R = R_capas(capas)
    capas_S = S_capas(capas)
    Rs_ext = 0.04
    Rs_int = 0.13
    R_totalx = R_total(capas, Rs_ext, Rs_int) #("Resistencia total (m²K/W)", 1.25)
    U = 1 / R_totalx
    S_total = sum(capas_S) #Espesor de aire equivalente total (m), 2.16

    temperaturas = calculatemperaturas(capas, temp_ext, temp_int, Rs_ext, Rs_int)
    presiones_sat = calculapresionessat(temperaturas)
    presiones = calculapresiones(capas, temp_ext, temp_int, HR_ext, HR_int)

    print u"Capas: \n\t", "\n\t".join([x[0] for x in capas])
    print u"Temperaturas: %s" % ["%.1f" % x for x in temperaturas]
    print u"Presiones de saturación: %s" % ["%.2f" % x for x in presiones_sat]
    print u"Presiones de vapor: %s" % ["%.2f" % x for x in presiones]
    print u"Presión de vapor exterior: %.2f" % presiones[1] # presión de vapor exterior: 1016.00
    print u"Presión de vapor interior: %.2f" % presiones[-1] # presión de vapor interior: 1285.32

    for pres, pres_sat in zip(presiones, presiones_sat):
        if pres < pres_sat:
            continue
        else:
            print "Se supera la presión de saturación"
    # Se puede calcular la humedad relativa interior para casos en los que no se trate
    # de zonas de baja carga interna.
    # Hay que generalizar el cálculo de la presión exterior para la localidad concreta?
    # Calcular exceso de humedad condensado si se da el caso.
    dibujagrafica("Cerramiento tipo", capas, Rs_ext, Rs_int,
            temperaturas, presiones, presiones_sat, U, HR_int, HR_ext)
