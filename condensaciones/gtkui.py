#!/usr/bin/env python
#encoding: utf-8
#
#   condensaciones.py
#   Programa de cálculo de condensaciones según CTE
#
#   Copyright (C) 2007-2010 por Rafael Villar Burke <pachi@rvburke.com>
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
"""Interfaz de usuario en GTK+"""

import gtk
import pango
import util
import comprobaciones
from ptcanvas import CPTCanvas, CPCanvas, GraphData

COLOR_OK = gtk.gdk.color_parse("#AACCAA")
COLOR_BAD = gtk.gdk.color_parse("#CCAAAA")

class GtkCondensa(object):
    """Aplicación"""
    def __init__(self, cerramiento=None, climae=None, climai=None):
        """Inicialización de datos e interfaz
        
        cerramiento - Cerramiento
        climae - datos higrotérmicos del exterior
        climai - datos higrotérmicos del interior
        """
        self.cerramiento = cerramiento
        self.climae = climae
        self.climai = climai
        # Cerramientos disponibles
        self.cerramientos = {}
        # --- UI ---
        UIFILE = util.get_resource('..', 'data', 'condensa.ui')
        builder = gtk.Builder()
        builder.add_from_file(UIFILE)
        # Controles ventana principal
        self.w = builder.get_object('window1')
        # - cabecera -
        self.cfondo = builder.get_object('cfondo')
        self.nombre = builder.get_object('nombre_cerramiento')
        self.descripcion = builder.get_object('descripcion_cerramiento')        
        self.csubtitulo1 = builder.get_object('csubtitulo1')
        self.csubtitulo2 = builder.get_object('csubtitulo2')
        # - gráficas -
        self.grafico1 = builder.get_object('cptcanvas1')
        self.grafico2 = builder.get_object('cpcanvas1')
        # - texto -
        self.textview = builder.get_object('cerramientotextview')
        self.cerramientotxtb = builder.get_object('cerramientotxtb')
        self.cerramientotxtb.create_tag("titulo",
                                        weight=pango.WEIGHT_BOLD,
                                        scale=pango.SCALE_X_LARGE)
        self.cerramientotxtb.create_tag("titulo2",
                                        style=pango.STYLE_ITALIC,
                                        scale=pango.SCALE_LARGE)
        self.cerramientotxtb.create_tag("subtitulo",
                                        #underline=pango.UNDERLINE_SINGLE,
                                        weight=pango.WEIGHT_BOLD,
                                        scale=pango.SCALE_LARGE,)
        self.cerramientotxtb.create_tag("capa",
                                        weight=pango.WEIGHT_BOLD,
                                        foreground="#777777")
        self.cerramientotxtb.create_tag("datoscapa",
                                        style=pango.STYLE_ITALIC,
                                        indent=30)
        self.cerramientotxtb.create_tag("resultados",
                                        foreground='blue')
        # - pie -
        self.pie1 = builder.get_object('pie1')
        self.pie2 = builder.get_object('pie2')
        # - pestaña de capas -
        self.rse = builder.get_object('Rsevalue')
        self.rsi = builder.get_object('Rsivalue')
        self.capasls = builder.get_object('capas_liststore')
        # Controles de diálogo de selección de cerramientos
        self.dlg = builder.get_object('cerramientodlg')
        self.cerramientotv = builder.get_object('cerramientotv')
        self.lblselected = builder.get_object('lblselected')
        self.cerramientols = builder.get_object('cerramientos_liststore')

        smap = {"on_window_destroy": gtk.main_quit,
                "on_cerramientobtn_clicked": self.on_cerramientobtn_clicked,
                "on_cerramientotv_cursor_changed": self.on_cerramientotv_cursor_changed,
                }
        builder.connect_signals(smap)
        
        self.cargacerramientos()
        self.actualiza()
        
    def main(self):
        """Arranca la aplicación"""
        self.w.show_all()
        gtk.main()

    def cargacerramientos(self):
        """Carga datos de cerramientos"""
        #TODO: cargar datos de biblioteca
        from datos_ejemplo import cerramientos
        for _c in cerramientos:
            self.cerramientos[_c.nombre] = _c
            self.cerramientols.append((_c.nombre, _c.descripcion))

    def actualiza(self):
        """Actualiza cabecera, gráficas, texto y pie de datos"""
        self.calcula()
        self.actualizacabecera()
        self.actualizapie()
        self.actualizacapas()
        self.actualizagraficas()
        self.actualizainforme()

    def calcula(self):
        c = self.cerramiento
        ti, hri = self.climai.temp, self.climai.HR
        te, hre = self.climae.temp, self.climae.HR
        self.fRsi = comprobaciones.fRsi(c.U)
        self.fRsimin = comprobaciones.fRsimin(te, ti, hri)
        self.ccheck = comprobaciones.condensaciones(c, te, ti, hre, hri)
        self.cs = comprobaciones.condensas(c, te, ti, hri)
        self.ci = comprobaciones.condensai(c, te, ti, hre, hri)
        self.g, pcond = c.condensacion(te, ti, hre, hri)
        #g, pevap = c.evaporacion(te, ti, hre, hri, interfases=[2])
        if not self.g:
            self.totalg = 0.0
        else:
            self.totalg = sum(self.g)

    def actualizacabecera(self):
        """Actualiza texto de cabecera"""
        self.nombre.set_text(self.cerramiento.nombre)
        self.descripcion.set_text(self.cerramiento.descripcion)
        _text = (u'U = %.2f W/m²K, f<sub>Rsi</sub> ='
                 u' %.2f, f<sub>Rsi,min</sub> = %.2f')
        self.csubtitulo1.set_markup(_text % (self.cerramiento.U,
                                             self.fRsi, self.fRsimin))
        _text = (u'T<sub>int</sub> = %.2f°C, HR<sub>int</sub> = %.1f%%, '
                 u'T<sub>ext</sub> = %.2f°C, HR<sub>ext</sub> = %.1f%%')
        self.csubtitulo2.set_markup(_text % (self.climai.temp, self.climai.HR,
                                             self.climae.temp, self.climae.HR))
        self.cfondo.modify_bg(gtk.STATE_NORMAL,
                              self.ccheck and COLOR_BAD or COLOR_OK)

    def actualizapie(self):
        """Actualiza pie de ventana principal"""
        SEGUNDOSPORMES = 2592000.0
        _text = u"Total: %.2f [g/m²mes]" % (SEGUNDOSPORMES * self.totalg)
        self.pie1.set_markup(_text)
        _text = (u"Cantidades condensadas: " +
                 u", ".join(["%.2f" % (SEGUNDOSPORMES * x,) for x in self.g]))
        self.pie2.set_markup(_text)

    def actualizacapas(self):
        """Actualiza pestaña de capas con descripción, capas, Rse, Rsi"""
        cerr = self.cerramiento
        self.rse.set_text("%.2f" % float(cerr.Rse))
        self.rsi.set_text("%.2f" % float(cerr.Rsi))
        self.capasls.clear()
        for i, (nombre, e, R) in enumerate(zip(cerr.nombres, cerr.espesores, cerr.R)):
            self.capasls.append((i, nombre, "%.3f" % e, "%.4f" % R))

    def actualizagraficas(self):
        """Redibuja gráficos con nuevos datos"""
        gdata = GraphData(self.cerramiento, self.climae, self.climai)
        self.grafico1.dibuja(gdata)
        self.grafico2.dibuja(gdata)
    
    def actualizainforme(self):
        """Actualiza texto descripción de cerramiento en ventana principal"""
        _m = self.cerramiento
        _tb = self.cerramientotxtb
        _tb.set_text("")
        _tb.insert_with_tags_by_name(_tb.get_start_iter(),
                                      u"%s\n" % _m.nombre, 'titulo')
        _tb.insert_with_tags_by_name(_tb.get_end_iter(),
                                      u"%s\n\n" % _m.descripcion, 'titulo2')
        # Capas
        _tb.insert_with_tags_by_name(_tb.get_end_iter(),
                                      u"Descripción\n", 'subtitulo')
        for i, (nombre, e, R, S) in enumerate(zip(_m.nombres, _m.espesores,
                                                  _m.R, _m.S)):
            _tb.insert_with_tags_by_name(_tb.get_end_iter(),
                                         u"%i - %s:\n" % (i, nombre), 'capa')
            _txt = u"%.3f [m]\nR=%.3f [m²K/W]\nS=%.3f [m]\n" % (e, R, S)
            _tb.insert_with_tags_by_name(_tb.get_end_iter(), _txt, 'datoscapa')
        # Resultados
        _tb.insert_with_tags_by_name(_tb.get_end_iter(),
                                      u"\nResultados\n", 'subtitulo')
        _txt = (u"R_total: %.3f [m²K/W]\n"
                u"S_total = %.3f [m]\n"
                u"U = %.3f [W/m²K]\n"
                u"f_Rsi = %.2f\n"
                u"f_Rsimin = %.2f\n") % (_m.R_total, _m.S_total, _m.U,
                                       self.fRsi, self.fRsimin)
        _tb.insert_with_tags_by_name(_tb.get_end_iter(), _txt, 'resultados')
        # Condensaciones
        cs = self.cs and "Sí" or "No"
        ci = self.ci and "Sí" or "No"
        _tb.insert_with_tags_by_name(_tb.get_end_iter(),
                                     (u"\nCondensaciones superficiales: %s\n"
                                      u"Condensaciones intersticiales: %s\n"
                                     ) % (cs, ci),
                                     'resultados')
        while gtk.events_pending():
            gtk.main_iteration()

    def on_cerramientobtn_clicked(self, widget):
        """Abrir diálogo de selección de cerramiento"""
        resultado = self.dlg.run()
        # gtk.RESPONSE_ACCEPT vs gtk.RESPONSE_CANCEL
        if resultado == gtk.RESPONSE_ACCEPT:
            nombrecerr = self.lblselected.get_text()
            self.cerramiento = self.cerramientos[nombrecerr]
            self.grafico1.clear()
            self.grafico2.clear()
            self.actualiza()
        self.dlg.hide()

    def on_cerramientotv_cursor_changed(self, tv):
        """Cambio de cerramiento seleccionado en lista de cerramientos"""
        _cerrtm, _cerrtm_iter = tv.get_selection().get_selected()
        _value = _cerrtm.get_value(_cerrtm_iter, 0)
        self.lblselected.set_text(_value)

if __name__ == "__main__":
    from cerramiento import Cerramiento
    from datos_ejemplo import climae, climai, cerramientocapas
    cerr = Cerramiento("Cerramiento tipo", "Tipo",
                       cerramientocapas, Rse=0.04, Rsi=0.13)
    app = GtkCondensa(cerr, climae, climai)
    app.main()