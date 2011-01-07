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

import gtk
import numpy
import matplotlib
matplotlib.use('GTKCairo')
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtkcairo import FigureCanvasGTKCairo
from util import colores_capas, add_margin
from clima import MESES

class GraphData(object):
    """Almacén de datos para dibujado de gráficas"""
    def __init__(self, model):
        """Inicializa el almacén de datos
        
        cerr - objeto Cerramiento
        climae - objeto Clima para datos del exterior
        cliai - objeto Clima para datos del interior
        """
        cerr = model.c
        climae = model.climae
        climai = model.climai
        self.temperaturas = cerr.temperaturas(climae.temp, climai.temp)
        self.presiones = cerr.presiones(climae.temp, climai.temp,
                                        climae.HR, climai.HR)
        self.presiones_sat = cerr.presionessat(climae.temp, climai.temp)
        self.nombres = cerr.nombres
        self.rotulos_s = add_margin(list(numpy.cumsum([0.0] + cerr.espesores)))
        #nemotécnicas intermedias
        self.rotulo_se = self.rotulos_s[1]
        self.rotulo_si = self.rotulos_s[-2]
        self.P_se = self.presiones[1]
        self.P_sat_se = self.presiones_sat[1]
        self.P_si = self.presiones[-2] #en superficie, no el aire
        self.P_sat_si = self.presiones_sat[-2] #en superficie, no el aire
        self.T_se = self.temperaturas[1]
        self.T_si = self.temperaturas[-2]

def _dibujacerramiento(ax, nombrecapas, xcapas):
    """Dibujado de cerramiento
    
    ax - ejes
    nombrecapas - nombres de capas del cerramiento
    xcapas - lista de coordenadas de interfases de capas
    """
    colordict = colores_capas(nombrecapas)
    # Etiquetas de exterior e interior
    ax.text(0.1, 0.92, 'exterior', transform=ax.transAxes,
            size=10, style='italic', ha='right')
    ax.text(0.9, 0.92, 'interior', transform=ax.transAxes,
            size=10, style='italic', ha='left')
    ax.text(.5,.92,'www.rvburke.com', transform=ax.transAxes,
            color='0.5', size=8, ha='center')
    # Lineas de tramos de cerramiento
    ax.axvline(xcapas[0], lw=2, color='k', ymin=.05, ymax=.9)
    for rotulo in xcapas[1:-1]:
        ax.axvline(rotulo, color='0.5', ymin=.05, ymax=.9)
    ax.axvline(xcapas[-1], lw=2, color='k', ymin=.05, ymax=.9)
    # Rellenos de materiales
    rotuloanterior = xcapas[0]
    for _i, (capa, rotulo) in enumerate(zip(nombrecapas, xcapas[1:])):
        ax.axvspan(rotuloanterior, rotulo,
                   fc=colordict[capa], alpha=0.25, ymin=.05, ymax=.9)
        ax.text((rotulo + rotuloanterior) / 2.0, 0.0, "%i" % _i,
                size=8, style='italic', ha='center')
        rotuloanterior = rotulo

class CPTCanvas(FigureCanvasGTKCairo):
    """Diagrama de presiones de saturación frente a presiones o temperaturas"""
    __gtype_name__ = 'CPTCanvas'

    def __init__(self):
        self.model = None
        self.fig = Figure()
        FigureCanvasGTKCairo.__init__(self, self.fig)
        self.fig.set_facecolor('w') # Fondo blanco en vez de gris
        self.ax1 = self.fig.add_subplot(111) # 1 fila, 1 columna, dibujo 1
        self.ax2 = self.ax1.twinx()

    def dibuja(self, width=600, height=400):
        """Representa Presiones de saturación vs. Presiones de vapor o
        temperaturas.
        
        El eje horizontal representa distancia desde la cara exterior del
        cerramiento [m].
        
        El eje vertical izquierdo tiene unidades de presión de vapor [Pa]
        El eje vertical derecho tiene unidades de temperatura [ºC]
        
        d - GraphData, contiene los datos para dibujar las gráficas
        """
        d = GraphData(self.model)
        # Eje vertical de presiones
        ax1 = self.ax1
        ax1.clear()  # Limpia imagen de datos anteriores
        
        ax1.set_title(u"Presiones de vapor y temperaturas", size='large')
        ax1.set_xlabel(u"Distancia [m]")
        ax1.set_ylabel(u"Presión de vapor [Pa]", fontdict=dict(color='b'))
        # Eliminamos márgenes de espesor de rotulos_s de capas límite 
        _dibujacerramiento(ax1, d.nombres, d.rotulos_s[1:-1])
        # Presiones, presiones de saturación y rótulos
        ax1.plot(d.rotulos_s, d.presiones, 'b-', lw=0.5)
        ax1.plot(d.rotulos_s, d.presiones_sat, 'k-', lw=0.5)
        # Rótulos de lineas de presiones interiores
        if d.P_sat_si > d.P_si:
            va1, va2 = 'top', 'baseline'
        else:
            va1, va2 = 'baseline', 'top'
        ax1.annotate(u'$P_{n}$ = %iPa' % d.P_si,
                     xy=(d.rotulo_si, d.P_si),
                     xytext=(+5,0), textcoords='offset points', ha='left',
                     va=va1, color='b', size='small')
        ax1.annotate(u'$P_{sat}$ = %iPa' % d.P_sat_si,
                     xy=(d.rotulo_si, d.P_sat_si),
                     xytext=(+5,0), textcoords='offset points', ha='left',
                     va=va2, color='k', size='small')
        # Rótulos de lineas de presiones exteriores
        if d.P_sat_se > d.P_se:
            va1, va2 = 'top', 'baseline'
        else:
            va1, va2 = 'baseline', 'top'
        ax1.annotate(u'$P_{n}$ = %iPa' % d.P_se,
                     xy=(d.rotulo_se, d.P_se),
                     xytext=(-5,0), textcoords='offset points', ha='right',
                     va=va1, color='b', size='small')
        ax1.annotate(u'$P_{sat}$ = %iPa' % d.P_sat_se,
                     xy=(d.rotulo_se, d.P_sat_se),
                     xytext=(-5,0), textcoords='offset points', ha='right',
                     va=va2, color='k', size='small')
        # Relleno de zona de condensación (psat <= presiones)
        nsteps = 200
        xmin = d.rotulos_s[0]
        xmax = d.rotulos_s[-1]
        xstep = (xmax - xmin) / float(nsteps)
        newx = [xmin + n * xstep for n in range(nsteps)]
        newpres = numpy.interp(newx, d.rotulos_s, d.presiones)
        newpressat = numpy.interp(newx, d.rotulos_s, d.presiones_sat)
        ax1.fill_between(newx, newpres, newpressat, where=newpressat<newpres,
                         facecolor='red')
        # Lineas rojas de interfases con condensaciones en el mes actual
        # añadimos 1 al índice porque rotulos_s tiene margen
        for i, gi in self.model.glist[self.model.imes]:
            ax1.axvline(d.rotulos_s[i+1], lw=1.5, color='r', ymin=.05, ymax=.9)
        # Eje vertical de temperaturas
        ax2 = self.ax2
        ax2.clear()  # Limpia imagen de datos anteriores
        ax2.set_ylabel(u"Temperatura [°C]", fontdict=dict(color='r'))
        # Curva de temperaturas y rótulos
        ax2.plot(d.rotulos_s, d.temperaturas, 'r', lw=1.5)
        ax2.annotate(u'$T_{se}$=%.1f°C' % d.T_se,
                     xy=(d.rotulo_se, d.T_se),
                     xytext=(-5,0), textcoords='offset points', ha='right',
                     size='small')
        ax2.annotate(u'$T_{si}$=%.1f°C' % d.T_si,
                     xy=(d.rotulo_si, d.T_si),
                     xytext=(5,5), textcoords='offset points', ha='left',
                     size='small')
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
        self.draw()

    def pixbuf(self, destwidth=600):
        """Obtén un pixbuf a partir del canvas actual"""
        return get_pixbuf_from_canvas(self, destwidth)

    def save(self, filename='presionestempplot.png'):
        """Guardar y mostrar gráfica"""
        self.fig.savefig(filename)

class CCCanvas(FigureCanvasGTKCairo):
    """Diagrama de condensaciones
    
    Dibuja un histograma con las condensaciones de cada periodo.
    Cuando existan 12 periodos en el modelo, considera que se trata de meses.
    
    Es necesario conectar el modelo al control, asignando el modelo del que se
    leen los datos en la propiedad model.
    """
    __gtype_name__ = 'CCCanvas'

    def __init__(self):
        self.model = None
        self.fig = Figure()
        FigureCanvasGTKCairo.__init__(self, self.fig)
        self.fig.set_facecolor('w') # Fondo blanco en vez de gris
        self.ax1 = self.fig.add_subplot(111) # 1 fila, 1 columna, dibujo 1
        self.fig.subplots_adjust(bottom=0.22) # Incrementar margen inferior

    def dibuja(self, width=600, height=200):
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
        x_names = [mes[:3] for mes in MESES] if N == 12 else [str(i) for i in range(N)]
        ax1.bar(x_c, y_c, width=1.0, align='center', fc='b', ec='k')
        ax1.set_xticks(x_c)
        ax1.set_xticklabels(x_names, size='small', rotation=20)
        # Tamaño
        self.set_size_request(width, height)
        self.draw()

    def pixbuf(self, destwidth=600):
        """Obtén un pixbuf a partir del canvas actual"""
        return get_pixbuf_from_canvas(self, destwidth)

    def save(self, filename='condensacionesplot.png'):
        """Guardar y mostrar gráfica"""
        self.fig.savefig(filename)


def get_pixbuf_from_canvas(canvas, destwidth=None):
    """Devuelve un pixbuf a partir de un canvas de Matplotlib
    
    destwidth - ancho del pixbuf de destino
    """
    w, h = canvas.get_width_height()
    destwidth = destwidth if destwidth else w
    destheight = h * destwidth / w
    #Antes de mostrarse la gráfica en una de las pestañas no existe el _pixmap
    #pero al generar el informe queremos que se dibuje en uno fuera de pantalla
    oldpixmap = canvas._pixmap if hasattr(canvas, '_pixmap') else None        
    pixmap = gtk.gdk.Pixmap(None, w, h, depth=24)
    canvas._renderer.set_pixmap(pixmap) # mpl backend_gtkcairo
    canvas._render_figure(pixmap, w, h) # mpl backend_gtk
    if oldpixmap:
        canvas._renderer.set_pixmap(oldpixmap)
    cm = pixmap.get_colormap()
    pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, w, h)
    pixbuf.get_from_drawable(pixmap, cm, 0, 0, 0, 0, -1, -1)
    scaledpixbuf = pixbuf.scale_simple(destwidth, destheight,
                                       gtk.gdk.INTERP_HYPER)
    return scaledpixbuf

class CRuler(gtk.DrawingArea):
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
        self.connect("expose-event", self.expose)

    def expose(self, widget, event):
        wh = self.allocation.height
        ww = self.allocation.width
        cr = widget.window.cairo_create()
        cr.set_line_width(1)
        cr.select_font_face("sans-serif")
        # wh = margin + font_size + 1.2 x margin + font_size + margin
        cr.set_font_size(wh / 2.5)
        margin = wh / 6.4
        x, y, twidth, theight, dx, dy = cr.text_extents("ENE")
        
        # Rótulos laterales de leyenda
        x, y, t1width, t1height, dx, dy = cr.text_extents("Periodo")
        x, y, t2width, t2height, dx, dy = cr.text_extents("g/m².mes")
        titmaxw = max(t1width, t2width) + 2.0 * margin
        
        cr.move_to(margin, theight + margin)
        cr.set_source_rgb(0.5, 0.5, 0.5)
        cr.show_text("Periodo")
        
        cr.move_to(margin, wh - margin)
        cr.set_source_rgb(0.0, 0.0, 0.0)
        cr.show_text("g/m².mes")

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
            cr.rectangle(i * ew , wh, ew, -k * condensa)
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
