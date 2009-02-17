#!/usr/bin/env python
#encoding: iso-8859-15

#TODO: Hacer test con los tres gráficos de condensa.py. Para ello hay
# que resolver el problema de usar subplot y show en cada figura.

import gtk
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_gtkcairo import FigureCanvasGTKCairo as FigureCanvas
from util import colores_capas, add_margin

matplotlib.rc('mathtext', fontset='custom') #para mostrar bien las expresiones matemáticas / latex

def plot_prestemp(figure, ax1, presiones, presiones_sat, temperaturas, rotulos, rotulos_s, colordict):
    #nemotécnicas intermedias
    rotulo_se = rotulos_s[1]
    rotulo_si = rotulos_s[-2]
    P_se = presiones[1]
    P_sat_se = presiones_sat[1]
    P_si = presiones[-2]
    P_sat_si = presiones_sat[-2]
    T_se = temperaturas[1]
    T_si = temperaturas[-2]

    ax1.set_title(u"Presiones de vapor y temperaturas", fontsize='large')
    ax1.set_xlabel(u"Distancia [m]")
    ax1.set_ylabel(u"Presión de vapor [Pa]", fontdict=dict(color='b'))
    ax1.text(0.1, 0.92, 'exterior',
            transform=ax1.transAxes, fontsize=10, fontstyle='italic', horizontalalignment='right')
    ax1.text(0.9, 0.92, 'interior',
            transform=ax1.transAxes, fontsize=10, fontstyle='italic', horizontalalignment='left')
    # lineas de datos
    ax1.plot(rotulos_s, presiones, 'b-', linewidth=0.5)
    ax1.plot(rotulos_s, presiones_sat, 'k-', linewidth=0.5)
    # Lineas de tramos de cerramiento
    ax1.axvline(rotulo_se, linewidth=2, color='k', ymin=.05, ymax=.9)
    for rotulo in rotulos_s[2:-2]:
        ax1.axvline(rotulo, color='0.5', ymin=.05, ymax=.9)
    ax1.axvline(rotulo_si, linewidth=2, color='k', ymin=.05, ymax=.9)
    # Rellenos de materiales
    ymin, ymax = ax1.get_ylim()
    rotuloanterior = rotulo_se
    for _i, (capa, rotulo) in enumerate(zip(rotulos, rotulos_s[2:])):
        color = colordict[capa]
        ax1.axvspan(rotuloanterior, rotulo, facecolor=color, alpha=0.25, ymin=.05, ymax=.9)
        ax1.text((rotulo + rotuloanterior) / 2.0, ymax, "%i" % _i,
                fontsize=8, fontstyle='italic', horizontalalignment='center')
        rotuloanterior = rotulo
    # Rótulos de lineas de presiones
    ax1.annotate(r'$P_{n}$',
            xy=(rotulo_si + 0.002, P_si),
            horizontalalignment='left', verticalalignment='top', color='b', size='small')
    ax1.annotate(r'$P_{sat}$',
            xy=(rotulo_si + 0.002, P_sat_si),
            horizontalalignment='left', verticalalignment='baseline', color='k', size='small')
    # incrementar extensión de límites de ejes para hacer hueco
    ymin, ymax = ax1.get_ylim()
    length = ymax - ymin
    ax1.set_ylim(ymin - length / 10.0, ymax + length / 5.0)

    # Nuevo eje vertical de temperaturas
    ax2 = ax1.twinx()
    ax2.set_ylabel(u"Temperatura [°C]", fontdict=dict(color='r'))
    # curva de temperaturas
    ax2.plot(rotulos_s, temperaturas, 'r', linewidth=1.5)
    #fill_between(rotulos_s[1:-1], temperaturas[1:-1], color=(1,0,0,0.1))
    # Valores de T_si y T_se
    ax2.annotate(r'$T_{se}=%.1f°C$' % T_se,
            xy=(rotulo_se - 0.002, T_se),
            horizontalalignment='right')
    ax2.annotate(r'$T_{si}=%.1f°C$' % T_si,
            xy=(rotulo_si + 0.002, T_si),
            horizontalalignment='left',
            verticalalignment='top')
    ax2.yaxis.tick_right()
    # extender eje para evitar coincidencia con curvas de presiones
    ymin, ymax = ax2.get_ylim()
    length = ymax - ymin
    ax2.set_ylim(ymin - length / 10.0, ymax + length / 5.0)

def plot_presiones(figure, ax1, presiones, presiones_sat, rotulos, rotulos_s, rotulos_ssat, puntos_condensacion, colordict):
    #nemotécnicas intermedias
    rotulo_se = rotulos_s[1]
    rotulo_si = rotulos_s[-2]
    rotulo_ssate = rotulos_ssat[0]
    rotulo_ssati = rotulos_ssat[-1]
    P_se = presiones[1]
    P_sat_se = presiones_sat[1]
    P_si = presiones[-2] #en superficie, no el aire
    P_sat_si = presiones_sat[-2] #en superficie, no el aire

    x_c = [x for x, y in puntos_condensacion]
    y_c = [y for x, y in puntos_condensacion]

    ax1.set_title(u"Presiones de vapor (efectiva y de saturación)", fontsize='large')
    ax1.set_xlabel(u"Espesor de aire equivalente [m]")
    ax1.set_ylabel(u"Presión de vapor [Pa]", fontdict=dict(color='b'))
    ax1.text(0.1, 0.92, 'exterior',
            transform=ax1.transAxes, fontsize=10, fontstyle='italic', horizontalalignment='right')
    ax1.text(0.9, 0.92, 'interior',
            transform=ax1.transAxes, fontsize=10, fontstyle='italic', horizontalalignment='left')
    ax1.plot(x_c, y_c, 'b-', label='p_vap') # presiones efectivas
    ax1.plot(rotulos_ssat, presiones_sat[1:-1], 'k-', label='p_sat', linewidth=1.5) #presiones de saturación
    if len(puntos_condensacion) > 2: #si hay condensaciones dibuja la linea original
        ax1.plot(rotulos_ssat, presiones[1:-1], 'g--')
    # Incrementar extensión de límites de ejes para hacer hueco
    # además guardamos extremos del gráfico interior, sin márgen
    # para luego hacer rótulos, etc
    xmin, xmax, ymin, ymax = ax1.axis()
    lengthx = rotulo_ssati
    lengthy = ymax - ymin
    ax1.axis([- 0.25 * lengthx, lengthx + 0.30 * lengthx, ymin - 0.20 * lengthy, ymax + 0.2 * lengthy])
    # Lineas de tramos de cerramiento
    ax1.axvline(rotulo_ssate, linewidth=2, color='k', ymin=.05, ymax=.9)
    for rotulo in rotulos_ssat[1:-1]:
        ax1.axvline(rotulo, color='0.5', ymin=.05, ymax=.9)
    ax1.axvline(rotulo_ssati, linewidth=2, color='k', ymin=.05, ymax=.9)
    # Rellenos de materiales
    rotuloanterior = rotulo_se
    for _i, (capa, rotulo) in enumerate(zip(rotulos, rotulos_ssat[1:])):
        color = colordict[capa]
        ax1.axvspan(rotuloanterior, rotulo, facecolor=color, alpha=0.25, ymin=.05, ymax=.9)
        ax1.text((rotulo + rotuloanterior) / 2.0, ymax, "%i" % _i,
                fontsize=8, fontstyle='italic', horizontalalignment='center')
        rotuloanterior = rotulo
    # Lineas de tramos de cerramiento con condensaciones
    for rotulo in x_c[1:-1]:
        ax1.axvline(rotulo, linewidth=1.5, color='r', ymin=.05, ymax=.9)
    # Rótulos de lineas de presiones exteriores
    if P_sat_se > P_se:
        va1, va2 = 'top', 'baseline'
    else:
        va1, va2 = 'baseline', 'top'
    ax1.annotate(r'$P_{n}$ = %iPa' % P_se,
            xy=(rotulo_se - 0.01, P_se),
            horizontalalignment='right', verticalalignment=va1, color='b', size='small')
    ax1.annotate(r'$P_{sat}$ = %iPa' % P_sat_se,
            xy=(rotulo_se - 0.01, P_sat_se),
            horizontalalignment='right', verticalalignment=va2, color='k', size='small')
    # Rótulos de lineas de presiones interiores
    if P_sat_si > P_si:
        va1, va2 = 'top', 'baseline'
    else:
        va1, va2 = 'baseline', 'top'
    ax1.annotate(r'$P_{n}$ = %iPa' % P_si,
            xy=(rotulo_ssati + 0.01, P_si),
            horizontalalignment='left', verticalalignment=va1, color='b', size='small')
    ax1.annotate(r'$P_{sat}$ = %iPa' % P_sat_si,
            xy=(rotulo_ssati + 0.01, P_sat_si),
            horizontalalignment='left', verticalalignment=va2, color='k', size='small')

def dibuja(nombre_grafica, muro, climae, climai, f_Rsi, f_Rsimin, puntos_condensacion, g):
    """Representa Presiones de saturación vs. Presiones de vapor y temperaturas
    en un diagrama capa/Presion de vapor y capa/Temp
    """
    temperaturas = muro.calculatemperaturas(climae.temp, climai.temp)
    presiones = muro.calculapresiones(climae.temp, climai.temp, climae.HR, climai.HR)
    presiones_sat = muro.calculapresionessat(climae.temp, climai.temp)
    rotulos = muro.nombre_capas
    rotulos_s = add_margin(muro.espesores_acumulados)
    rotulos_ssat = muro.S_acumulados
    colordict = colores_capas(muro.nombre_capas)
    # TODO: mejorar definición de existencia de condensaciones en lugar de sum(g)
    ccheck = ((f_Rsi > f_Rsimin) and (sum(g) <= 0.0)) and True or False

    fig = plt.figure(figsize=(9,10), dpi=80)
    fig.suptitle(nombre_grafica, fontsize='x-large')
    fig.subplots_adjust(left=0.11, right=0.93, bottom=0.11, top=0.84, hspace=0.25) # ampliar márgenes
    fig.text(0.5, 0.95,
            r'$U = %.2f W/m^2K,\,f_{Rsi} = %.2f,\, f_{Rsi,min} = %.2f$' % (muro.U, f_Rsi, f_Rsimin),
            fontsize='large',
            bbox=dict(facecolor=(ccheck and (0.5,0.7,0.5,0.8) or (0.7,0.5,0.5,0.8))),
            verticalalignment='top',
            horizontalalignment='center')
    fig.text(0.5, 0.875,
            r'$T_{int} = %.2f°C, \, HR_{int} = %.1f\%%, \,'
            'T_{ext} = %.2f°C, \, HR_{ext} = %.1f\%%$' % (climai.temp, climai.HR, climae.temp, climae.HR),
            fontsize='large', #bbox=dict(facecolor='blue', alpha=0.25),
            horizontalalignment='center')
    # 30.0 días * 24.0 horas * 3600.0 segundos = 2592000.0 s/mes
    texto_g = "Cantidades condensadas: " + ", ".join(["%.2f" % (2592000.0 * x,) for x in g])
    texto_g_total = r"$Total: %.2f\,[g/m^{2}mes]$" % (2592000.0 * sum(g))
    fig.text(0.11, .05, texto_g, fontsize=9)
    fig.text(0.11, .02, texto_g_total)
    # ================== presiones y temperaturas =====================
    axis1 = fig.add_subplot('211')
    plot_prestemp(fig, axis1, presiones, presiones_sat, temperaturas, rotulos, rotulos_s, colordict)
    # ============================ presiones ==========================
    axis2 = fig.add_subplot('212')
    plot_presiones(fig, axis2, presiones, presiones_sat, rotulos, rotulos_s, rotulos_ssat, puntos_condensacion, colordict)
    #subplot_tool() #Ayuda para ajustar márgenes
    #show()
    # guardar y mostrar gráfica
    #savefig('presionesplot.png')
    return fig

if __name__ == "__main__":
    import capas
    from datos_ejemplo import climae, climai, murocapas
    import comprobaciones

    muro = capas.Cerramiento(murocapas, 0.04, 0.13)
    f_Rsi = comprobaciones.calculafRsi(muro.U)
    f_Rsimin = comprobaciones.calculafRsimin(climae.temp, climai.temp, climai.HR)
    g, puntos_condensacion = muro.calculacantidadcondensacion(climae.temp, climai.temp, climae.HR, climai.HR)
    #g, puntos_evaporacion = muro.calculacantidadevaporacion(temp_ext, temp_int, HR_ext, HR_int, interfases=[2])

    fig = dibuja("Cerramiento tipo", muro, climae, climai, f_Rsi, f_Rsimin, puntos_condensacion, g)

    w = gtk.Window()
    w.connect('delete-event', gtk.main_quit)
    w.set_default_size(600,800)
    canvas = FigureCanvas(fig)
    canvas.show()
    w.add(canvas)
    w.show_all()
    gtk.main()
