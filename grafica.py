#!/usr/bin/env python
#encoding: iso-8859-15
from pylab import *
from condensa import nombre_capas

def colorlist(steps):
    import colorsys
    clist =[]
    salto_color = 0.0
    for i in range(steps):
        color = colorsys.hls_to_rgb(salto_color, .6, .8)
        clist.append(color)
        salto_color += 1.0/steps
    return clist

def colores_capas(lista_capas):
    capas_distintas = set(lista_capas)
    colordict = {}
    for nombre, color in zip(capas_distintas, colorlist(len(capas_distintas))):
        colordict[nombre] = color
    return colordict

def x_capas(espesores_capas, margen_lateral=0.025):
    rotulos = [-margen_lateral, 0.0]
    for espesor in espesores_capas:
        nuevo = rotulos[-1] + espesor
        rotulos.append(nuevo)
    rotulos.append(rotulos[-1] + margen_lateral)
    return rotulos

def dibujagrafica(nombre_grafica, capas, Rs_ext, Rs_int, temperaturas, presiones, presiones_sat, U, HR_int, HR_ext, f_Rsi, f_Rsimin):
    """Representa Presiones de saturación vs. Presiones de vapor y temperaturas
    en un diagrama capa/Presion de vapor y capa/Temp
    """
    T_e = temperaturas[0]
    T_i = temperaturas[-1]
    T_se = temperaturas[1]
    T_si = temperaturas[-2]
    P_se = presiones[1]
    P_sat_se = presiones_sat[1]
    Rtotal = 1 / U
    # TODO: Indicar si cumple f_Rsi > f_Rsi,min, T_si > T_si,min, P > P_sat, etc

    espesores_capas = [e for nombre, e, mu, K in capas]
    rotulos = x_capas(espesores_capas)
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
            nombre_grafica,
            transform=sp1.transAxes,
            verticalalignment='top',
            horizontalalignment='center',
            fontsize=12,
            fontstyle='italic')
    # Lineas de tramos de cerramiento
    axvline(rotulo_se, linewidth=2, color='k', ymin=.05, ymax=.9)
    for rotulo in rotulos[2:-2]:
        axvline(rotulo, color='0.5', ymin=.05, ymax=.9)
    axvline(rotulo_si, linewidth=2, color='k', ymin=.05, ymax=.9)

    # Rellenos de materiales
    colordict = colores_capas(nombre_capas(capas))
    rotuloanterior = rotulo_se
    for capa, rotulo in zip(nombre_capas(capas), rotulos[2:]):
        color = colordict[capa]
        axvspan(rotuloanterior, rotulo, facecolor=color, alpha=0.25, ymin=.05, ymax=.9)
        rotuloanterior = rotulo

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
    import grafica
    # Valores constructivos: nombre, espesor, mu, K
    capas = [("1/2 pie LP métrico o catalán 40 mm<", 0.11, 10.0, 0.69),
            ("Mortero_de_áridos_ligeros_[vermiculita", 0.01, 10.0, 0.41),
            ("EPS Poliestireno Expandido", 0.03, 20.0, 0.037),
            ("Tabique de LH sencillo [40 mm < Esp", 0.03, 10.0, 0.44),
            ("Enlucido_de_yeso_1000<d<1300", 0.01, 6.0, 0.57),]
    # Valores climáticos
    temp_ext = 10.7
    HR_ext = 79
    temp_int = 20
    HR_int = 55
    Rs_ext = 0.04
    Rs_int = 0.13
    # Valores "calculados"
    U = 0.80 # W/m^2K
    f_Rsi = 0.80
    f_Rsimin = 0.36
    temperaturas = [10.7, 11.0, 12.2, 12.4, 18.4, 18.9, 19.0, 20.0]
    presiones = [1016.00, 1016.00, 1153.16, 1165.62, 1240.44, 1277.84, 1285.32, 1285.32]
    presiones_sat = [1286.08, 1311.79, 1418.84, 1435.87, 2114.68, 2182.84, 2200.69, 2336.95]

    grafica.dibujagrafica("Cerramiento tipo", capas, Rs_ext, Rs_int,
            temperaturas, presiones, presiones_sat, U, HR_int, HR_ext, f_Rsi, f_Rsimin)
