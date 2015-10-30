#!/usr/bin/env python
#encoding: utf-8
#
#   condensaciones.py
#   Programa de cálculo de condensaciones según CTE
#
#   Copyright (C) 2009-2011 Rafael Villar Burke <pachi@rvburke.com>
#
#   This program is free software; you can redistribute it and/or
#   modify it under the terms of the GNU General Public License
#   as published by the Free Software Foundation; either version 2
#   of the License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
#   02110-1301, USA.
"""Módulo de dibujo y controles gráficos de la interfaz de usuario"""

import cStringIO
from gi.repository import GObject, Gtk, GdkPixbuf
import numpy
import matplotlib
matplotlib.use('GTK3Cairo')
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas

from .clima import MESES
from .util import config

class CPTCanvas(FigureCanvas):
    """Diagrama de presiones de saturación frente a presiones o temperaturas"""
    __gtype_name__ = 'CPTCanvas'

    # XXX: usaríamos la señal así
    #self.emit("plot-changed")
    # Conectamos a la señal con:
    # CPTcanvasinstance.connect("plot-changed", self.changedcallback)
    # La retrollamada es:
    #def changedcallback(self, canvas):
    #    self.queue_draw()
    __gsignals__ = {
        # Signal our values changed, and a redraw will be needed
        "plot-changed": (GObject.SIGNAL_RUN_LAST, None, ()),
    }

    def __init__(self, width=600, height=400):
        self.model = None
        figure = Figure()
        FigureCanvas.__init__(self, figure)
        figure.set_facecolor('w') # Fondo blanco en vez de gris

        self.ax1 = figure.add_subplot(111, axisbg='None') # 1 fila, 1 columna, dibujo 1
        self.ax1.yaxis.label.set_color('b')
        self.ax1.tick_params(axis='y', colors='b')
        self.ax1.tick_params(axis='x', labelsize='10')
        self.ax1.spines["right"].set_visible(False)
        self.ax1.spines["top"].set_visible(False)
        self.ax1.spines["bottom"].set_visible(False)
        self.ax1.spines["left"].set_edgecolor('b')

        self.ax2 = self.ax1.twinx()
        self.ax2.yaxis.label.set_color('r')
        self.ax2.tick_params(axis='y', colors='r')
        self.ax2.spines["left"].set_visible(False)
        self.ax2.spines["top"].set_visible(False)
        self.ax2.spines["bottom"].set_visible(False)
        self.ax2.spines["right"].set_edgecolor('r')

        self.props.visible = True
        # Tamaño
        self.set_size_request(width, height)
        self.queue_draw()

    def dibuja(self):
        """Representa Presiones de saturación vs. Presiones de vapor o
        temperaturas.

        El eje horizontal representa distancia desde la cara exterior del
        cerramiento [m].

        El eje vertical izquierdo tiene unidades de presión de vapor [Pa]
        El eje vertical derecho tiene unidades de temperatura [ºC]
        """
        m = self.model
        temperaturas = m.c.temperaturas(m.climae.temp, m.climai.temp)
        presiones = m.c.presiones(m.climae.temp, m.climai.temp,
                                  m.climae.HR, m.climai.HR)
        presiones_sat = m.c.presionessat(m.climae.temp, m.climai.temp)

        # Posición de rótulos de las capas y capas aire
        _xpos = list(numpy.cumsum([0.0] + m.c.espesores))
        x_s = ([_xpos[0] - 0.025] + _xpos + [_xpos[-1] + 0.025])

        #nemotécnicas intermedias para superficies (en 0 y -1 está el aire)
        rotulo_se = x_s[1]
        rotulo_si = x_s[-2]
        P_se = presiones[1]
        P_sat_se = presiones_sat[1]
        P_si = presiones[-2] #en superficie, no el aire
        P_sat_si = presiones_sat[-2] #en superficie, no el aire
        T_se = temperaturas[1]
        T_si = temperaturas[-2]

        ax1 = self.ax1 # presiones
        ax2 = self.ax2 # temperaturas
        ax1.clear()  # Limpia imagen de datos anteriores
        ax2.clear()  # Limpia imagen de datos anteriores

        # ========= Eje vertical de presiones
        ax1.set_title(u"Presión de vapor y temperatura", size='large')
        ax1.set_xlabel(u"Espesor [m]")
        ax1.set_ylabel(u"Presión de vapor [Pa]", fontdict=dict(color='b'))
        ax1.text(0.1, 0.92, u'exterior',
                 transform=ax1.transAxes,
                 size=10, style='italic', ha='right')
        ax1.text(0.9, 0.92, u'interior',
                 transform=ax1.transAxes,
                 size=10, style='italic', ha='left')
        ax1.text(0.5, 0.92, u'Condensaciones v%s - www.rvburke.com' % config.version,
                 transform=ax1.transAxes,
                 color='0.5', size=8, ha='center')

        # Rellenos de materiales
        # x in data coords, y in axes coords
        ax1trans = matplotlib.transforms.blended_transform_factory(
            ax1.transData, ax1.transAxes)
        rotuloanterior = x_s[1]
        for _i, (rotulo, color) in enumerate(zip(x_s[2:-1], m.c.colores)):
            ax1.axvspan(rotuloanterior, rotulo,
                        fc=color, alpha=0.25, ymin=0.05, ymax=0.9)
            ax1.text((rotulo + rotuloanterior) / 2.0, 0.075,
                     "%i" % _i, transform=ax1trans,
                     size=8, style='italic', ha='center')
            rotuloanterior = rotulo

        # Lineas de tramos de cerramiento
        ax1.axvline(x_s[1], lw=2, color='k',
                    ymin=.05, ymax=.9)
        for rotulo in x_s[2:-2]:
            ax1.axvline(rotulo, color='0.5',
                        ymin=.05, ymax=.9)
        ax1.axvline(x_s[-2], lw=2, color='k',
                    ymin=.05, ymax=.9)

        # Presiones, presiones de saturación y rótulos
        ax1.plot(x_s, presiones, 'b-', lw=0.5)
        ax1.plot(x_s, presiones_sat, 'k-', lw=0.5)
        # Rótulos de lineas de presiones interiores
        if P_sat_si > P_si:
            va1, va2 = 'top', 'baseline'
        else:
            va1, va2 = 'baseline', 'top'
        ax1.annotate(u'$P_{n}$ = %iPa' % P_si,
                     xy=(rotulo_si, P_si),
                     xytext=(+5, 0), textcoords='offset points', ha='left',
                     va=va1, color='b', size='small')
        ax1.annotate(u'$P_{sat}$ = %iPa' % P_sat_si,
                     xy=(rotulo_si, P_sat_si),
                     xytext=(+5, 0), textcoords='offset points', ha='left',
                     va=va2, color='k', size='small')
        # Rótulos de lineas de presiones exteriores
        if P_sat_se > P_se:
            va1, va2 = 'top', 'baseline'
        else:
            va1, va2 = 'baseline', 'top'

        ax1.annotate(u'$P_{n}$ = %iPa' % P_se,
                     xy=(rotulo_se, P_se),
                     xytext=(-5, 0), textcoords='offset points', ha='right',
                     va=va1, color='b', size='small')
        ax1.annotate(u'$P_{sat}$ = %iPa' % P_sat_se,
                     xy=(rotulo_se, P_sat_se),
                     xytext=(-5, 0), textcoords='offset points', ha='right',
                     va=va2, color='k', size='small')
        # Relleno de zona de condensación (psat <= presiones)
        nsteps = 200
        xmin = x_s[0]
        xmax = x_s[-1]
        xstep = (xmax - xmin) / float(nsteps)
        newx = [xmin + n * xstep for n in range(nsteps)]
        newpres = numpy.interp(newx, x_s, presiones)
        newpressat = numpy.interp(newx, x_s, presiones_sat)
        ax1.fill_between(newx, newpres, newpressat, where=(newpressat < newpres),
                         facecolor='red')
        # Lineas rojas de interfases con condensaciones en el mes actual
        # añadimos 1 al índice porque x_s tiene margen
        for i, gi in m.glist[m.imes]:
            ax1.axvline(x_s[i+1], lw=1.5, color='r', ymin=.05, ymax=.9)
        # Dejar margen fuera de zona de trazado
        ymin, ymax = ax1.get_ylim()
        length = ymax - ymin
        ax1.set_ylim(ymin - 0.1 * length, ymax + 0.2 * length)
            
        # ======== Eje vertical de temperaturas
        ax2.set_ylabel(u"Temperatura [°C]", fontdict=dict(color='r'))
        # Curva de temperaturas y rótulos
        ax2.plot(x_s, temperaturas, 'r', lw=1.5)
        ax2.annotate(u'$T_{se}$=%.1f°C' % T_se,
                     xy=(rotulo_se, T_se),
                     xytext=(-5, 0), textcoords='offset points', ha='right',
                     size='small')
        ax2.annotate(u'$T_{si}$=%.1f°C' % T_si,
                     xy=(rotulo_si, T_si),
                     xytext=(5, 5), textcoords='offset points', ha='left',
                     size='small')
        ax2.yaxis.tick_right()
        # Dejar margen fuera de zona de trazado
        ymin, ymax = ax2.get_ylim()
        length = ymax - ymin
        ax2.set_ylim(ymin - 0.1 * length, ymax + 0.2 * length)
        # BUGFIX: http://stackoverflow.com/questions/27216812/matplotlib-cant-re-draw-first-axis-after-clearing-second-using-twinx-and-cla
        ax2.patch.set_visible(False)

        # XXX: Ver si va...
        # para conectar luego con CPTcanvasinstance.connect("plot-changed", callback)
        self.emit("plot-changed")

    def pixbuf(self, destwidth=600):
        """Obtén un pixbuf a partir del canvas actual"""
        return get_pixbuf_from_canvas(self, destwidth)

    def save(self, filename='presionestempplot.png', dpi=100):
        """Guardar y mostrar gráfica"""
        self.print_figure(filename,
                          format='png',
                          facecolor='w',
                          dpi=dpi)

class CCCanvas(FigureCanvas):
    """Diagrama de condensaciones

    Dibuja un histograma con las condensaciones de cada periodo.
    Cuando existan 12 periodos en el modelo, considera que se trata de meses.

    Es necesario conectar el modelo al control, asignando el modelo del que se
    leen los datos en la propiedad model.
    """
    __gtype_name__ = 'CCCanvas'

    def __init__(self, model=None, width=600, height=200):
        self.model = model
        figure = Figure()
        FigureCanvas.__init__(self, figure)
        figure.set_facecolor('w') # Fondo blanco en vez de gris
        self.ax1 = figure.add_subplot(111, axisbg='None') # 1 fila, 1 columna, dibujo 1
        figure.subplots_adjust(bottom=0.22) # Incrementar margen inferior
        self.props.visible = True
        #self.dibuja()
        # Tamaño
        self.set_size_request(width, height)
        self.queue_draw()
        #XXX: ver cómo cambiar dibuja a do_draw(self, cr) y quitamos las llamadas explícitas
        
    def do_draw(self, cr):
        self.dibuja()

    def dibuja(self):
        """Representa histograma de condensaciones totales en cada mes

        El eje horizontal representa los periodos [meses] y el eje vertical la
        condensación existente [g/m²mes]
        """
        # -- dibujo ---
        ax1 = self.ax1
        ax1.clear() # Limpia imagen de datos anteriores
        ax1.set_title(u"Condensaciones", size='large')
        ax1.set_xlabel(u"Periodo")
        ax1.set_ylabel(u"Cantidad condensada [g/m²mes]", fontdict=dict(color='b'))
        # presiones efectivas
        N = len(self.model.climaslist)
        x_c = numpy.arange(N)
        y_c = self.model.gmeses
        x_names = [mes[:3] for mes in MESES] if N == 12 else [str(i+1) for i in range(N)]
        ax1.bar(x_c, y_c, width=1.0, align='center', fc='b', ec='k')
        ax1.set_xticks(x_c)
        ax1.set_xticklabels(x_names, size='small', rotation=20)
        #self.queue_draw()

    def pixbuf(self, destwidth=600):
        """Obtén un pixbuf a partir del canvas actual"""
        return get_pixbuf_from_canvas(self, destwidth)

    def save(self, filename='condensacionesplot.png', dpi=100):
        """Guardar y mostrar gráfica"""
        self.print_figure(filename,
                          format='png',
                          facecolor='w',
                          dpi=dpi)

def get_pixbuf_from_canvas(widget, destwidth=None):
    """Devuelve un pixbuf a partir de un canvas de Matplotlib

    destwidth - ancho del pixbuf de destino
    """

    if destwidth:
        figwidthpx = widget.figure.get_figwidth() * widget.figure.dpi
        scalefactor = float(destwidth) / figwidthpx
        dpi = widget.figure.dpi * scalefactor
    else:
        dpi = widget.figure.dpi

    fd = cStringIO.StringIO()
    widget.figure.savefig(fd, format="png", facecolor='w', dpi=dpi)
    contents = fd.getvalue()
    fd.close()

    loader = GdkPixbuf.PixbufLoader.new_with_type("png")
    loader.write(contents)
    pixbuf = loader.get_pixbuf()
    loader.close()

    return pixbuf

class CRuler(Gtk.DrawingArea):
    """Barra de condensaciones en interfases

    El control dibuja una casilla por cada elemento en condensalist
    (model.gmeses) y la colorea en verde si el elemento es cero o en rojo si es
    mayor que cero. Además, se resalta el periodo actualmente seleccionado, que
    se toma de imes (model.imes)

    Los valores de condensación se representan con un decimal.
    """
    __gtype_name__ = 'CRuler'

    def __init__(self):
        self.model = None
        super(CRuler, self).__init__()
        self.set_size_request(-1, 25)
        self.queue_draw()

    def do_draw(self, cr):
        allocation = self.get_allocation()    
        wh = allocation.height
        ww = allocation.width
        cr.set_line_width(1)
        cr.select_font_face("sans-serif")
        cr.set_font_size(wh / 2.5)
        margin = wh / 6.4
        x, y, twidth, theight, dx, dy = cr.text_extents("ENE")

        # Rótulos laterales de leyenda
        x, y, t1width, t1height, dx, dy = cr.text_extents("Periodo")
        x, y, t2width, t2height, dx, dy = cr.text_extents("g/m².mes")
        titmaxw = max(t1width, t2width) + 2.0 * margin

        cr.move_to(margin, theight + margin)
        cr.set_source_rgb(0.5, 0.5, 0.5)
        cr.show_text(u"Periodo")

        cr.move_to(margin, wh - margin)
        cr.set_source_rgb(0.0, 0.0, 0.0)
        cr.show_text(u"g/m².mes")

        cr.translate(titmaxw, 0)

        # Casillas de Periodos
        ln = len(self.model.gmeses)
        ew = (1.0 * ww - titmaxw) / ln
        ismeses = ln == 12
        gmax = max(self.model.gmeses)
        k = (1.0 * wh / gmax) if gmax else 0.0

        for i, condensa in enumerate(self.model.gmeses):
            # Rectángulos de fondo
            cr.rectangle(i * ew, 0, ew, wh)
            if condensa > 0:
                cr.set_source_rgb(0.8, 0.666667, 0.666667) #CCAAAA COLOR_BAD
            else:
                cr.set_source_rgb(0.666667, 0.8, 0.666667) #AACCAA COLOR_OK
            cr.fill()
            # Rectángulos de cantidad condensada (histograma)
            cr.rectangle(i * ew, wh, ew, -k * condensa)
            cr.set_source_rgb(0.4, 0.8, 0.9)
            cr.fill()
            # Nombres meses
            cr.move_to((i + 0.5) * ew - twidth / 2.0, theight + margin)
            cr.set_source_rgb(0.5, 0.5, 0.5)
            if ismeses:
                cr.show_text(MESES[i][:3].upper())
            else:
                cr.show_text("%s" % i)
            # Cantidad condensada
            txt = "%.1f" % condensa
            x, y, width, height, dx, dy = cr.text_extents(txt)
            cr.move_to((i + 0.5) * ew - width / 2.0, wh - margin)
            cr.set_source_rgb(0.0, 0.0, 0.0)
            cr.show_text(txt)

        # Líneas laterales
        for i in range(1, ln):
            cr.move_to(round(i * ew) + 0.5, 0)
            cr.line_to(round(i * ew) + 0.5, wh)
            cr.set_source_rgb(0, 0, 0)
            cr.stroke()

        # Resalta mes actual
        cr.set_line_width(2)
        if self.model.imes is not None and ln > 1:
            cr.rectangle(round(self.model.imes*ew)+1.5, 0.5, ew-2.0, wh-0.5)
            cr.set_source_rgb(1.0, 0.2, 0.2)
            cr.stroke()
