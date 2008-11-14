#!/usr/bin/env python
#encoding: iso-8859-15

#TODO: Hacer test con los tres gráficos de condensa.py. Para ello hay
# que resolver el problema de usar subplot y show en cada figura.

from pylab import *
import colorsys
import operator

def colorlist(steps):
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

def dibujapresionestemperaturas(nombre_grafica, muro, Rs_ext, Rs_int, temperaturas, presiones, presiones_sat, U, HR_int, HR_ext, f_Rsi, f_Rsimin):
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

    espesores_capas = muro.espesores
    rotulos = x_capas(espesores_capas)
    rotulo_se = rotulos[1]
    rotulo_si = rotulos[-2]
    # Dibujar gráfica
    sp1 = subplot('111')
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
    colordict = colores_capas(muro.nombre_capas)
    rotuloanterior = rotulo_se
    for capa, rotulo in zip(muro.nombre_capas, rotulos[2:]):
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
    length = ymax - ymin
    ylim(ymin - length / 10.0, ymax + length / 5.0)
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
    length = ymax - ymin
    ylim(ymin - length / 10.0, ymax + length / 5.0)
    # guardar y mostrar gráfica
    #savefig('presionesplot.png')
    show()

def dibujapresiones(muro, puntos_condensacion, presiones, presiones_sat, g):
    """ Representar presiones frente a espesores de aire equivalentes
    señalando planos de condensación y cantidad condensada.
    """
    capas_S = muro.S
    s_sat = [0.0] + [reduce(operator.add, capas_S[:i]) for i in range(1,len(capas_S)+1)]
    s_min = s_sat[0]
    s_max = s_sat[-1]
    x_c = [x for x, y in puntos_condensacion]
    y_c = [y for x, y in puntos_condensacion]
    # Dibujar gráfica
    sp1 = subplot('111')
    title(u"Presiones de vapor (efectiva y de saturación)")
    xlabel(u"Espesor de aire equivalente [m]")
    ylabel(u"Presión de vapor [Pa]", fontdict=dict(color='b'))
    plot(s_sat, presiones_sat[1:-1], 'k-', label='p_sat') #presiones de saturación
    plot(x_c, y_c, 'b-', label='p_vap') # presiones efectivas
    if len(puntos_condensacion) > 2: #si hay condensaciones dibuja la linea original
        plot(s_sat, presiones[1:-1], 'g--')
    leg = legend(loc='upper right')
    ltext  = leg.get_texts()
    setp(ltext, fontsize='small')
    # 30.0 días * 24.0 horas * 3600.0 segundos = 2592000.0 s/mes
    texto_g = "Cantidades condensadas: " + ", ".join(["%.2f" % (2592000.0 * x,) for x in g])
    texto_g_total = r"$Total: %.2f\,[g/m^{2}mes]$" % (2592000.0 * sum(g))
    figtext(0.15, .85, texto_g, fontsize=9)
    figtext(0.15, .80, texto_g_total)
    # Incrementar extensión de límites de ejes para hacer hueco
    xmin, xmax, ymin, ymax = axis()
    lengthx = s_max
    lengthy = ymax - ymin
    axis([- 0.1 * lengthx, lengthx + 0.1 * lengthx, ymin - 0.05 * lengthy, ymax + 0.2 * lengthy])
    # Lineas de tramos de cerramiento
    axvline(s_min, linewidth=2, color='k', ymin=.05, ymax=.8)
    for rotulo in s_sat[1:-1]:
        axvline(rotulo, color='0.5', ymin=.05, ymax=.8)
    axvline(s_max, linewidth=2, color='k', ymin=.05, ymax=.8)
    # Lineas de tramos de cerramiento con condensaciones
    for rotulo in x_c[1:-1]:
        axvline(rotulo, linewidth=1, color='r', ymin=.05, ymax=.8)
    # Mostrar
    show()

if __name__ == "__main__":
    from capas import *
    import datos_ejemplo
    import condensa

    capas = datos_ejemplo.capas
    muro = Cerramiento(capas)

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

    dibujapresionestemperaturas("Cerramiento tipo", muro, Rs_ext, Rs_int,
            temperaturas, presiones, presiones_sat, U, HR_int, HR_ext, f_Rsi, f_Rsimin)
    g, puntos_condensacion = condensa.calculacantidadcondensacion(muro, presiones, presiones_sat)
    g, puntos_evaporacion = condensa.calculacantidadevaporacion(muro, presiones, presiones_sat, interfases=[2])
    dibujapresiones(muro, puntos_condensacion, presiones, presiones_sat, g)
    dibujapresiones(muro, puntos_evaporacion, presiones, presiones_sat, g)
