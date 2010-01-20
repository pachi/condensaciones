#!/usr/bin/env python
#encoding: utf-8

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_gtkcairo import FigureCanvasGTKCairo
from util import colores_capas, add_margin

#para mostrar bien las expresiones matemáticas / latex
matplotlib.rc('mathtext', fontset='custom')

class GraphData(object):
    """Almacén de datos para dibujado de gráficas"""
    def __init__(self, muro, climae, climai):
        self.temperaturas = muro.temperaturas(climae.temp, climai.temp)
        self.presiones = muro.presiones(climae.temp, climai.temp,
                                        climae.HR, climai.HR)
        self.presiones_sat = muro.presionessat(climae.temp, climai.temp)
        self.nombres = muro.nombres
        self.rotulos_s = add_margin(muro.espesores_acumulados)
        self.rotulos_ssat = muro.S_acumulados
        self.qc, self.p_condensa = muro.condensacion(climae.temp, climai.temp,
                                                     climae.HR, climai.HR)
#        self.qe, self.p_evapora = muro.cantidadevaporacion(temp_ext, temp_int,
#                                                           HR_ext, HR_int,
#                                                           interfases=[2])
        self.color = colores_capas(self.nombres)

        #nemotécnicas intermedias
        self.rotulo_se = self.rotulos_s[1]
        self.rotulo_si = self.rotulos_s[-2]
        self.rotulo_ssate = self.rotulos_ssat[0]
        self.rotulo_ssati = self.rotulos_ssat[-1]
        self.P_se = self.presiones[1]
        self.P_sat_se = self.presiones_sat[1]
        self.P_si = self.presiones[-2] #en superficie, no el aire
        self.P_sat_si = self.presiones_sat[-2] #en superficie, no el aire
        self.T_se = self.temperaturas[1]
        self.T_si = self.temperaturas[-2]


def _dibujacerramiento(ax, nombrecapas, xcapas, colordict):
    """Dibujado de muro
    
    ax - ejes
    nombrecapas - nombres de capas del cerramiento
    xcapas - lista de coordenadas de interfases de capas
    colordict - diccionario con colores según nombres de capa
    """
    # Etiquetas de exterior e interior
    ax.text(0.1, 0.92, 'exterior', transform=ax.transAxes,
            fontsize=10, fontstyle='italic', horizontalalignment='right')
    ax.text(0.9, 0.92, 'interior', transform=ax.transAxes,
            fontsize=10, fontstyle='italic', horizontalalignment='left')
    # Lineas de tramos de cerramiento
    ax.axvline(xcapas[0], linewidth=2, color='k', ymin=.05, ymax=.9)
    for rotulo in xcapas[1:-1]:
        ax.axvline(rotulo, color='0.5', ymin=.05, ymax=.9)
    ax.axvline(xcapas[-1], linewidth=2, color='k', ymin=.05, ymax=.9)
    # Rellenos de materiales
    ymin, ymax = ax.get_ylim()
    rotuloanterior = xcapas[0]
    for _i, (capa, rotulo) in enumerate(zip(nombrecapas, xcapas[1:])):
        ax.axvspan(rotuloanterior, rotulo,
                   facecolor=colordict[capa], alpha=0.25, ymin=.05, ymax=.9)
        ax.text((rotulo + rotuloanterior) / 2.0, ymax, "%i" % _i,
                fontsize=8, fontstyle='italic', horizontalalignment='center')
        rotuloanterior = rotulo

class CPTCanvas(FigureCanvasGTKCairo):
    """Diagrama de presiones de saturación frente a presiones o temperaturas"""
    __gtype_name__ = 'CPTCanvas'

    def __init__(self):
        self.fig = plt.figure()
        FigureCanvasGTKCairo.__init__(self, self.fig)



    def dibuja(self, d, width=600, height=400):
        """Representa Presiones de saturación vs. Presiones de vapor o
        temperaturas.
        
        El eje horizontal representa distancia desde la cara exterior del
        cerramiento [m].
        
        El eje vertical izquierdo tiene unidades de presión de vapor [Pa]
        El eje vertical derecho tiene unidades de temperatura [ºC]
        
        d - contiene los datos para dibujar las gráficas
        """
        # ================== presiones y temperaturas =====================
        # -- dibujo ---
        ax1 = self.fig.add_subplot(111) # 1 fila, 1 columna, dibujo 1
        ax1.set_title(u"Presiones de vapor y temperaturas", fontsize='large')
        ax1.set_xlabel(u"Distancia [m]")
        ax1.set_ylabel(u"Presión de vapor [Pa]", fontdict=dict(color='b'))
        # Eliminamos márgenes de espesor de rotulos_s de capas límite 
        _dibujacerramiento(ax1, d.nombres, d.rotulos_s[1:-1], d.color)
        # Presiones
        ax1.plot(d.rotulos_s, d.presiones, 'b-', linewidth=0.5)
        # Presiones de saturación
        ax1.plot(d.rotulos_s, d.presiones_sat, 'k-', linewidth=0.5)
        # Rótulos
        ax1.annotate(r'$P_{n}$',
                     xy=(d.rotulo_si + 0.002, d.P_si),
                     horizontalalignment='left', verticalalignment='top',
                     color='b', size='small')
        ax1.annotate(r'$P_{sat}$',
                     xy=(d.rotulo_si + 0.002, d.P_sat_si),
                     horizontalalignment='left', verticalalignment='baseline',
                     color='k', size='small')
        # Eje vertical de temperaturas
        ax2 = ax1.twinx()
        ax2.set_ylabel(u"Temperatura [°C]", fontdict=dict(color='r'))
        # Curva de temperaturas
        ax2.plot(d.rotulos_s, d.temperaturas, 'r', linewidth=1.5)
        #fill_between(rotulos_s[1:-1], temperaturas[1:-1], color=(1,0,0,0.1))
        # Valores de T_si y T_se
        ax2.annotate(r'$T_{se}=%.1f°C$' % d.T_se,
                     xy=(d.rotulo_se - 0.002, d.T_se),
                     horizontalalignment='right')
        ax2.annotate(r'$T_{si}=%.1f°C$' % d.T_si,
                     xy=(d.rotulo_si + 0.002, d.T_si),
                     horizontalalignment='left',
                     verticalalignment='top')
        ax2.yaxis.tick_right()
        # Dejar margen fuera de zona de trazado
        ymin, ymax = ax1.get_ylim()
        length = ymax - ymin
        ax1.set_ylim(ymin - 0.1 * length, ymax + 0.2 * length)
        # Dejar margen fuera de zona de trazado
        ymin, ymax = ax2.get_ylim()
        length = ymax - ymin
        ax2.set_ylim(ymin - 0.1 * length, ymax + 0.2 * length)
        # Tamaño
        self.set_size_request(width, height)

    def save(self, filename='presionestempplot.png'):
        # guardar y mostrar gráfica
        self.savefig(filename)

class CPCanvas(FigureCanvasGTKCairo):
    """Diagrama de presiones"""
    __gtype_name__ = 'CPCanvas'

    def __init__(self):
        self.fig = plt.figure()
        FigureCanvasGTKCairo.__init__(self, self.fig)


    def dibuja(self, d, width=600, height=400):
        """Representa Presiones de saturación vs. Presiones de vapor
        
        El eje horizontal representa es espesor de aire equivalente desde
        la cara exterior del cerramiento [m].
        
        El eje vertical tiene unidades de presión de Vapor [Pa]
        
        d - contiene los datos para dibujar las gráficas
        """
        x_c = [x for x, y in d.p_condensa]
        y_c = [y for x, y in d.p_condensa]
        # -- dibujo ---
        ax1 = self.fig.add_subplot(111) # 1 fila, 1 columna, dibujo 1
        ax1.set_title(u"Presiones de vapor (efectiva y de saturación)",
                      fontsize='large')
        ax1.set_xlabel(u"Espesor de aire equivalente [m]")
        ax1.set_ylabel(u"Presión de vapor [Pa]", fontdict=dict(color='b'))
        _dibujacerramiento(ax1, d.nombres, d.rotulos_ssat, d.color)
        # presiones efectivas
        ax1.plot(x_c, y_c, 'b-', label='p_vap')
        #presiones de saturación
        ax1.plot(d.rotulos_ssat, d.presiones_sat[1:-1],
                 'k-', label='p_sat', linewidth=1.5)
        #si hay condensaciones dibuja la linea original
        if len(d.p_condensa) > 2:
            ax1.plot(d.rotulos_ssat, d.presiones[1:-1], 'g--')
        # Lineas de tramos de cerramiento con condensaciones en rojo
        for rotulo in x_c[1:-1]:
            ax1.axvline(rotulo, linewidth=1.5, color='r', ymin=.05, ymax=.9)
        # Rótulos de lineas de presiones exteriores
        if d.P_sat_se > d.P_se:
            va1, va2 = 'top', 'baseline'
        else:
            va1, va2 = 'baseline', 'top'
        ax1.annotate(r'$P_{n}$ = %iPa' % d.P_se,
                     xy=(d.rotulo_se - 0.01, d.P_se),
                     horizontalalignment='right', verticalalignment=va1,
                     color='b', size='small')
        ax1.annotate(r'$P_{sat}$ = %iPa' % d.P_sat_se,
                     xy=(d.rotulo_se - 0.01, d.P_sat_se),
                     horizontalalignment='right', verticalalignment=va2,
                     color='k', size='small')
        # Rótulos de lineas de presiones interiores
        if d.P_sat_si > d.P_si:
            va1, va2 = 'top', 'baseline'
        else:
            va1, va2 = 'baseline', 'top'
        ax1.annotate(r'$P_{n}$ = %iPa' % d.P_si,
                     xy=(d.rotulo_ssati + 0.01, d.P_si),
                     horizontalalignment='left', verticalalignment=va1,
                     color='b', size='small')
        ax1.annotate(r'$P_{sat}$ = %iPa' % d.P_sat_si,
                     xy=(d.rotulo_ssati + 0.01, d.P_sat_si),
                     horizontalalignment='left', verticalalignment=va2,
                     color='k', size='small')
        # Dejar margen fuera de zona de trazado
        xmin, xmax, ymin, ymax = ax1.axis()
        lengthx = d.rotulo_ssati #xmax = rotulo_ssati ;xmin = rotulo_ssate = 0
        lengthy = ymax - ymin
        ax1.axis([xmin - 0.3 * lengthx, xmax + 0.2 * lengthx,
                  ymin - 0.1 * lengthy, ymax + 0.2 * lengthy])
        # Tamaño
        self.set_size_request(width, height)

    def save(self, filename='presionesplot.png'):
        # guardar y mostrar gráfica
        self.savefig(filename)

if __name__ == "__main__":
    import gtk
    from capas import Cerramiento
    from datos_ejemplo import climae, climai, murocapas

    Rs_ext = 0.04
    Rs_int = 0.13
    muro = Cerramiento("Cerramiento tipo", murocapas, Rs_ext, Rs_int)
    data = GraphData(muro, climae, climai)

    w = gtk.Window()
    v = gtk.VBox()
    pt = CPTCanvas()
    p = CPCanvas()
    pt.dibuja(data)
    p.dibuja(data)
    v.pack_start(pt)
    v.pack_start(p)
    w.add(v)
    w.show_all()
    w.connect('destroy', gtk.main_quit)
    gtk.main()