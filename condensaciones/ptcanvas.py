#!/usr/bin/env python
#encoding: utf-8

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_gtkcairo import FigureCanvasGTKCairo as FigureCanvas
from util import colores_capas, add_margin

#para mostrar bien las expresiones matemáticas / latex
matplotlib.rc('mathtext', fontset='custom')

class GraphData(object):
    """Clase de almacén de datos para dibujar las gráficas"""
    def __init__(self, muro, climae, climai):
        self.temperaturas = muro.temperaturas(climae.temp, climai.temp)
        self.presiones = muro.presiones(climae.temp, climai.temp,
                                        climae.HR, climai.HR)
        self.presiones_sat = muro.presionessat(climae.temp, climai.temp)
        self.rotulos = muro.nombres
        self.rotulos_s = add_margin(muro.espesores_acumulados)
        self.rotulos_ssat = muro.S_acumulados
        self.qc, self.p_condensa = muro.condensacion(climae.temp, climai.temp, climae.HR, climai.HR)
        #self.qe, self.p_evapora = muro.cantidadevaporacion(temp_ext, temp_int, HR_ext, HR_int, interfases=[2])
        self.colordict = colores_capas(self.rotulos)

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

class CPTCanvas(FigureCanvas):
    __gtype_name__ = 'CPTCanvas'

    def __init__(self):
        self.fig = plt.figure()
        FigureCanvas.__init__(self, self.fig)

    def dibuja(self, d, w=600, h=400):
        """Representa Presiones de saturación vs. Presiones de vapor y temperaturas
        en un diagrama capa/Presion de vapor y capa/Temp
        
        d - contiene los datos para dibujar las gráficas
        """
        # ================== presiones y temperaturas =====================
        # -- dibujo ---
        ax1 = self.fig.add_subplot(111) # 1 fila, 1 columna, dibujo 1
        ax1.set_title(u"Presiones de vapor y temperaturas", fontsize='large')
        ax1.set_xlabel(u"Distancia [m]")
        ax1.set_ylabel(u"Presión de vapor [Pa]", fontdict=dict(color='b'))
        ax1.text(0.1, 0.92, 'exterior',
                transform=ax1.transAxes,
                fontsize=10, fontstyle='italic', horizontalalignment='right')
        ax1.text(0.9, 0.92, 'interior',
                transform=ax1.transAxes,
                fontsize=10, fontstyle='italic', horizontalalignment='left')
        # lineas de datos
        ax1.plot(d.rotulos_s, d.presiones, 'b-', linewidth=0.5)
        ax1.plot(d.rotulos_s, d.presiones_sat, 'k-', linewidth=0.5)
        # Lineas de tramos de cerramiento
        ax1.axvline(d.rotulo_se, linewidth=2, color='k', ymin=.05, ymax=.9)
        for rotulo in d.rotulos_s[2:-2]:
            ax1.axvline(rotulo, color='0.5', ymin=.05, ymax=.9)
        ax1.axvline(d.rotulo_si, linewidth=2, color='k', ymin=.05, ymax=.9)
        # Rellenos de materiales
        ymin, ymax = ax1.get_ylim()
        rotuloanterior = d.rotulo_se
        for _i, (capa, rotulo) in enumerate(zip(d.rotulos, d.rotulos_s[2:])):
            color = d.colordict[capa]
            ax1.axvspan(rotuloanterior, rotulo,
                        facecolor=color, alpha=0.25, ymin=.05, ymax=.9)
            ax1.text((rotulo + rotuloanterior) / 2.0, ymax, "%i" % _i,
                    fontsize=8, fontstyle='italic',
                    horizontalalignment='center')
            rotuloanterior = rotulo
        # Rótulos de lineas de presiones
        ax1.annotate(r'$P_{n}$',
                xy=(d.rotulo_si + 0.002, d.P_si),
                horizontalalignment='left', verticalalignment='top',
                color='b', size='small')
        ax1.annotate(r'$P_{sat}$',
                xy=(d.rotulo_si + 0.002, d.P_sat_si),
                horizontalalignment='left', verticalalignment='baseline',
                color='k', size='small')
        # incrementar extensión de límites de ejes para hacer hueco
        ymin, ymax = ax1.get_ylim()
        length = ymax - ymin
        ax1.set_ylim(ymin - length / 10.0, ymax + length / 5.0)
        # Nuevo eje vertical de temperaturas
        ax2 = ax1.twinx()
        ax2.set_ylabel(u"Temperatura [°C]", fontdict=dict(color='r'))
        # curva de temperaturas
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
        # extender eje para evitar coincidencia con curvas de presiones
        ymin, ymax = ax2.get_ylim()
        length = ymax - ymin
        ax2.set_ylim(ymin - length / 10.0, ymax + length / 5.0)
        # -- dibujo ---
        self.set_size_request(w, h)

    def save(self, filename='presionestempplot.png'):
        # guardar y mostrar gráfica
        self.savefig(filename)

class CPCanvas(FigureCanvas):
    __gtype_name__ = 'CPCanvas'

    def __init__(self):
        self.fig = plt.figure()
        FigureCanvas.__init__(self, self.fig)

    def dibuja(self, d, w=600, h=400):
        """Representa Presiones de saturación vs. Presiones de vapor en un
        diagrama capa/Presion de vapor y capa/Temp
        
        d - contiene los datos para dibujar las gráficas
        """
        # ============================ presiones ==========================
        x_c = [x for x, y in d.p_condensa]
        y_c = [y for x, y in d.p_condensa]
        # -- dibujo ---
        ax1 = self.fig.add_subplot(111) # 1 fila, 1 columna, dibujo 1
        ax1.set_title(u"Presiones de vapor (efectiva y de saturación)",
                      fontsize='large')
        ax1.set_xlabel(u"Espesor de aire equivalente [m]")
        ax1.set_ylabel(u"Presión de vapor [Pa]", fontdict=dict(color='b'))
        ax1.text(0.1, 0.92, 'exterior',
                transform=ax1.transAxes,
                fontsize=10, fontstyle='italic', horizontalalignment='right')
        ax1.text(0.9, 0.92, 'interior',
                transform=ax1.transAxes,
                fontsize=10, fontstyle='italic', horizontalalignment='left')
        ax1.plot(x_c, y_c, 'b-', label='p_vap') # presiones efectivas
        ax1.plot(d.rotulos_ssat, d.presiones_sat[1:-1],
                 'k-', label='p_sat', linewidth=1.5) #presiones de saturación
        #si hay condensaciones dibuja la linea original
        if len(d.p_condensa) > 2:
            ax1.plot(d.rotulos_ssat, d.presiones[1:-1], 'g--')
        # Incrementar extensión de límites de ejes para hacer hueco
        # además guardamos extremos del gráfico interior, sin márgen
        # para luego hacer rótulos, etc
        xmin, xmax, ymin, ymax = ax1.axis()
        lengthx = d.rotulo_ssati
        lengthy = ymax - ymin
        ax1.axis([- 0.25 * lengthx,
                  lengthx + 0.30 * lengthx,
                  ymin - 0.20 * lengthy,
                  ymax + 0.2 * lengthy])
        # Lineas de tramos de cerramiento
        ax1.axvline(d.rotulo_ssate, linewidth=2, color='k', ymin=.05, ymax=.9)
        for rotulo in d.rotulos_ssat[1:-1]:
            ax1.axvline(rotulo, color='0.5', ymin=.05, ymax=.9)
        ax1.axvline(d.rotulo_ssati, linewidth=2, color='k', ymin=.05, ymax=.9)
        # Rellenos de materiales
        rotuloanterior = d.rotulo_se
        for _i, (capa, rotulo) in enumerate(zip(d.rotulos, d.rotulos_ssat[1:])):
            color = d.colordict[capa]
            ax1.axvspan(rotuloanterior, rotulo,
                        facecolor=color, alpha=0.25, ymin=.05, ymax=.9)
            ax1.text((rotulo + rotuloanterior) / 2.0, ymax, "%i" % _i,
                    fontsize=8, fontstyle='italic',
                    horizontalalignment='center')
            rotuloanterior = rotulo
        # Lineas de tramos de cerramiento con condensaciones
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
        # -- dibujo ---
        self.set_size_request(w, h)

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

    w = gtk.Window()
    v = gtk.VBox()
    pt = CPTCanvas()
    p = CPCanvas()
    pt.dibuja(muro, climae, climai)
    p.dibuja(muro, climae, climai)
    v.pack_start(pt)
    v.pack_start(p)
    w.add(v)
    w.show_all()
    w.connect('destroy', gtk.main_quit)
    gtk.main()