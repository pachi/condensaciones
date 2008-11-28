#!/usr/bin/env python
#encoding: iso-8859-15

#TODO: Hacer test con los tres gráficos de condensa.py. Para ello hay
# que resolver el problema de usar subplot y show en cada figura.

# import matplotlib
# matplotlib.use('GTK')

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

#TODO: crear método espesoracumulado en Cerramiento y usar aquí
def x_capas(espesores_capas, margen_lateral=0.025):
    rotulos = [-margen_lateral, 0.0]
    for espesor in espesores_capas:
        nuevo = rotulos[-1] + espesor
        rotulos.append(nuevo)
    rotulos.append(rotulos[-1] + margen_lateral)
    return rotulos

def plot_prestemp(subplot, presiones, presiones_sat, temperaturas, rotulos_s, colordict):
    #nemotécnicas intermedias
    rotulo_se = rotulos_s[1]
    rotulo_si = rotulos_s[-2]
    P_se = presiones[1]
    P_sat_se = presiones_sat[1]
    T_se = temperaturas[1]
    T_si = temperaturas[-2]

    title(u"Presiones de vapor y temperaturas", fontsize='large')
    xlabel(u"Distancia [m]")
    ylabel(u"Presión de vapor [Pa]", fontdict=dict(color='b'))
    text(0.1, 0.92, 'exterior',
            transform=subplot.transAxes, fontsize=10, fontstyle='italic', horizontalalignment='right')
    text(0.9, 0.92, 'interior',
            transform=subplot.transAxes, fontsize=10, fontstyle='italic', horizontalalignment='left')
    # Lineas de tramos de cerramiento
    axvline(rotulo_se, linewidth=2, color='k', ymin=.05, ymax=.9)
    for rotulo in rotulos_s[2:-2]:
        axvline(rotulo, color='0.5', ymin=.05, ymax=.9)
    axvline(rotulo_si, linewidth=2, color='k', ymin=.05, ymax=.9)
    # Rellenos de materiales
    rotuloanterior = rotulo_se
    for capa, rotulo in zip(muro.nombre_capas, rotulos_s[2:]):
        color = colordict[capa]
        axvspan(rotuloanterior, rotulo, facecolor=color, alpha=0.25, ymin=.05, ymax=.9)
        rotuloanterior = rotulo
    # lineas de datos
    plot(rotulos_s, presiones, 'b-', linewidth=0.5)
    plot(rotulos_s, presiones_sat, 'b-', linewidth=1.5)
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
    plot(rotulos_s, temperaturas, 'r:')
    # Valores de T_si y T_se
    annotate(r'$T_{se}=%.1f^\circ C$' % T_se,
            xy=(rotulo_se - 0.002, T_se),
            horizontalalignment='right')
    annotate(r'$T_{si}=%.1f^\circ C$' % T_si,
            xy=(rotulo_si + 0.002, T_si),
            horizontalalignment='left',
            verticalalignment='top')
    ax2.yaxis.tick_right()
    # extender eje para evitar coincidencia con curvas de presiones
    ymin, ymax = ylim()
    length = ymax - ymin
    ylim(ymin - length / 10.0, ymax + length / 5.0)

def plot_presiones(subplot, presiones, presiones_sat, rotulos_s, rotulos_ssat, puntos_condensacion, colordict):
    #nemotécnicas intermedias
    rotulo_se = rotulos_s[1]
    rotulo_si = rotulos_s[-2]
    rotulo_ssate = rotulos_ssat[0]
    rotulo_ssati = rotulos_ssat[-1]
    P_se = presiones[1]
    P_sat_se = presiones_sat[1]

    x_c = [x for x, y in puntos_condensacion]
    y_c = [y for x, y in puntos_condensacion]

    title(u"Presiones de vapor (efectiva y de saturación)", fontsize='large')
    xlabel(u"Espesor de aire equivalente [m]")
    ylabel(u"Presión de vapor [Pa]", fontdict=dict(color='b'))
    text(0.1, 0.92, 'exterior',
            transform=subplot.transAxes, fontsize=10, fontstyle='italic', horizontalalignment='right')
    text(0.9, 0.92, 'interior',
            transform=subplot.transAxes, fontsize=10, fontstyle='italic', horizontalalignment='left')
    plot(rotulos_ssat, presiones_sat[1:-1], 'k-', label='p_sat') #presiones de saturación
    plot(x_c, y_c, 'b-', label='p_vap') # presiones efectivas
    if len(puntos_condensacion) > 2: #si hay condensaciones dibuja la linea original
        plot(rotulos_ssat, presiones[1:-1], 'g--')
    # Incrementar extensión de límites de ejes para hacer hueco
    xmin, xmax, ymin, ymax = axis()
    lengthx = rotulo_ssati
    lengthy = ymax - ymin
    axis([- 0.25 * lengthx, lengthx + 0.30 * lengthx, ymin - 0.20 * lengthy, ymax + 0.2 * lengthy])
    # Lineas de tramos de cerramiento
    axvline(rotulo_ssate, linewidth=2, color='k', ymin=.05, ymax=.9)
    for rotulo in rotulos_ssat[1:-1]:
        axvline(rotulo, color='0.5', ymin=.05, ymax=.9)
    axvline(rotulo_ssati, linewidth=2, color='k', ymin=.05, ymax=.9)
    # Rellenos de materiales
    rotuloanterior = rotulo_se
    for capa, rotulo in zip(muro.nombre_capas, rotulos_ssat[1:]):
        color = colordict[capa]
        axvspan(rotuloanterior, rotulo, facecolor=color, alpha=0.25, ymin=.05, ymax=.9)
        rotuloanterior = rotulo
    # Lineas de tramos de cerramiento con condensaciones
    for rotulo in x_c[1:-1]:
        axvline(rotulo, linewidth=1, color='r', ymin=.05, ymax=.8)
    # Rótulos de lineas de presiones
    annotate(r'$P_{n}$',
            xy=(rotulo_se - 0.002, P_se),
            horizontalalignment='right')
    annotate(r'$P_{sat}$',
            xy=(rotulo_se - 0.002, P_sat_se),
            horizontalalignment='right')
    #TODO: añadir rótulos de valores extremos de presiones

def textocomprueba(muro, f_Rsi, f_Rsimin, ccheck=True, y=0.95):
    _boxcolor = ccheck and 'green' or 'red'
    figtext(0.5, y,
            r'$U = %.2f W/m^2K,\,f_{Rsi} = %.2f,\, f_{Rsi,min} = %.2f$' % (muro.U, f_Rsi, f_Rsimin),
            fontsize='large',
            bbox=dict(facecolor=_boxcolor, alpha=0.25),
            verticalalignment='top',
            horizontalalignment='center')

def textodatos(temp_ext, temp_int, HR_ext, HR_int, y=0.875):
    figtext(0.5, y,
            r'$T_{int} = %.2f^\circ C, \, HR_{int} = %.1f\%%, \,'
            'T_{ext} = %.2f^\circ C, \, HR_{ext} = %.1f\%%$' % (temp_int, HR_int, temp_ext, HR_ext),
            fontsize='large', #bbox=dict(facecolor='blue', alpha=0.25),
            horizontalalignment='center')

def textocondensa(g):
    # 30.0 días * 24.0 horas * 3600.0 segundos = 2592000.0 s/mes
    texto_g = "Cantidades condensadas: " + ", ".join(["%.2f" % (2592000.0 * x,) for x in g])
    texto_g_total = r"$Total: %.2f\,[g/m^{2}mes]$" % (2592000.0 * sum(g))
    figtext(0.11, .05, texto_g, fontsize=9)
    figtext(0.11, .02, texto_g_total)

def dibujapresionestemperaturas(nombre_grafica, muro, temp_ext, temp_int, HR_int, HR_ext, f_Rsi, f_Rsimin):
    """Representa Presiones de saturación vs. Presiones de vapor y temperaturas
    en un diagrama capa/Presion de vapor y capa/Temp
    """
    temperaturas = muro.calculatemperaturas(temp_ext, temp_int)
    presiones = muro.calculapresiones(temp_ext, temp_int, HR_ext, HR_int)
    presiones_sat = muro.calculapresionessat(temp_ext, temp_int)
    rotulos_s = x_capas(muro.espesores)
    colordict = colores_capas(muro.nombre_capas)
    ccheck = (f_Rsi > f_Rsimin) and True or False

    sp1 = subplot('111')
    suptitle(nombre_grafica, fontsize='x-large')
    textocomprueba(muro, f_Rsi, f_Rsimin, ccheck, y=0.93)
    textodatos(temp_ext, temp_int, HR_ext, HR_int, y=0.03)
    subplots_adjust(bottom=0.15, top=0.82) # ampliar márgenes
    plot_prestemp(sp1, presiones, presiones_sat, temperaturas, rotulos_s, colordict)
    #savefig('presionesplot.png')
    #subplot_tool() #Ayuda para ajustar márgenes
    show()

def dibujapresiones(muro, temp_ext, temp_int, HR_ext, HR_int, puntos_condensacion, g):
    """ Representar presiones frente a espesores de aire equivalentes
    señalando planos de condensación y cantidad condensada.
    """
    presiones = muro.calculapresiones(temp_ext, temp_int, HR_ext, HR_int)
    presiones_sat = muro.calculapresionessat(temp_ext, temp_int)
    rotulos_s = x_capas(muro.espesores)
    rotulos_ssat = [0.0] + [reduce(operator.add, muro.S[:i]) for i in range(1,len(muro.S)+1)]
    colordict = colores_capas(muro.nombre_capas)

    sp1 = subplot('111')
    plot_presiones(sp1, presiones, presiones_sat, rotulos_s, rotulos_ssat, puntos_condensacion, colordict)
    show()

def dibuja(nombre_grafica, muro, temp_ext, temp_int, HR_ext, HR_int, f_Rsi, f_Rsimin, puntos_condensacion, g):
    """Representa Presiones de saturación vs. Presiones de vapor y temperaturas
    en un diagrama capa/Presion de vapor y capa/Temp
    """
    temperaturas = muro.calculatemperaturas(temp_ext, temp_int)
    presiones = muro.calculapresiones(temp_ext, temp_int, HR_ext, HR_int)
    presiones_sat = muro.calculapresionessat(temp_ext, temp_int)
    rotulos_s = x_capas(muro.espesores)
    rotulos_ssat = [0.0] + [reduce(operator.add, muro.S[:i]) for i in range(1,len(muro.S)+1)]
    colordict = colores_capas(muro.nombre_capas)
    # TODO: mejorar definición de existencia de condensaciones en lugar de sum(g)
    ccheck = ((f_Rsi > f_Rsimin) and (sum(g) <= 0.0)) and True or False

    figure(figsize=(9,10))
    suptitle(nombre_grafica, fontsize='x-large')
    subplots_adjust(left=0.11, right=0.93, bottom=0.11, top=0.84, hspace=0.25) # ampliar márgenes
    textocomprueba(muro, f_Rsi, f_Rsimin, ccheck)
    textodatos(temp_ext, temp_int, HR_ext, HR_int)
    textocondensa(g)
    sp1 = subplot('211')
    plot_prestemp(sp1, presiones, presiones_sat, temperaturas, rotulos_s, colordict)
    sp1 = subplot('212')
    plot_presiones(sp1, presiones, presiones_sat, rotulos_s, rotulos_ssat, puntos_condensacion, colordict)
    #subplot_tool() #Ayuda para ajustar márgenes
    show()
    # guardar y mostrar gráfica
    #savefig('presionesplot.png')

if __name__ == "__main__":
    import capas
    import datos_ejemplo
    # Valores climáticos
    temp_ext = 10.7
    HR_ext = 79
    temp_int = 20
    HR_int = 55
    # Valores "calculados"
    f_Rsi = 0.80
    f_Rsimin = 0.36

    muro = capas.Cerramiento(datos_ejemplo.capas, 0.04, 0.13)

#     dibujapresionestemperaturas("Cerramiento tipo", muro, temp_ext, temp_int, HR_int, HR_ext, f_Rsi, f_Rsimin)
    g, puntos_condensacion = muro.calculacantidadcondensacion(temp_ext, temp_int, HR_ext, HR_int)
    #dibujapresiones(muro, temp_ext, temp_int, HR_ext, HR_int, puntos_condensacion, g)
    #g, puntos_evaporacion = muro.calculacantidadevaporacion(temp_ext, temp_int, HR_ext, HR_int, interfases=[2])
    #dibujapresiones(muro, temp_ext, temp_int, HR_ext, HR_int, puntos_evaporacion, g)

    dibuja("Cerramiento tipo", muro, temp_ext, temp_int, HR_ext, HR_int, f_Rsi, f_Rsimin, puntos_condensacion, g)
