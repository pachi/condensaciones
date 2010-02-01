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
        self.ctitulo = builder.get_object('ctitulo')
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
        self.cerramientotxtb.create_tag("capa",
                                        weight=pango.WEIGHT_BOLD)
        self.cerramientotxtb.create_tag("datoscapa",
                                        style=pango.STYLE_ITALIC,
                                        indent=30)
        self.cerramientotxtb.create_tag("resultados",
                                        foreground='blue',
                                        scale=pango.SCALE_LARGE)
        # - pie -
        self.pie1 = builder.get_object('pie1')
        self.pie2 = builder.get_object('pie2')
        # Controles de diálogo de selección de cerramientos
        self.dlg = builder.get_object('cerramientodlg')
        self.cerramientotv = builder.get_object('cerramientotv')
        self.lblselected = builder.get_object('lblselected')
        self.cerramientols = builder.get_object('cerramientoliststore')

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
        self.actualizacabecera()
        self.actualizagraficas()
        self.actualizatexto()
        self.actualizapie()

    def actualizacabecera(self):
        """Actualiza texto de cabecera"""
        cerr = self.cerramiento
        ti = self.climai.temp
        hri = self.climai.HR
        te = self.climae.temp
        hre = self.climae.HR
        fRsi = comprobaciones.fRsi(cerr.U)
        fRsimin = comprobaciones.fRsimin(te, ti, hri)
        ccheck = comprobaciones.condensaciones(cerr, te, ti, hre, hri)
        _text = u'<span size="x-large">%s</span>' % cerr.nombre
        self.ctitulo.set_markup(_text)
        _text = (u'U = %.2f W/m²K, f<sub>Rsi</sub> ='
                 u' %.2f, f<sub>Rsi,min</sub> = %.2f')
        self.csubtitulo1.set_markup(_text % (cerr.U, fRsi, fRsimin))
        _text = (u'T<sub>int</sub> = %.2f°C, HR<sub>int</sub> = %.1f%%, '
                 u'T<sub>ext</sub> = %.2f°C, HR<sub>ext</sub> = %.1f%%')
        self.csubtitulo2.set_markup(_text % (ti, hri, te, hre))
        self.cfondo.modify_bg(gtk.STATE_NORMAL,
                              ccheck and COLOR_BAD or COLOR_OK)

    def actualizagraficas(self):
        """Redibuja gráficos con nuevos datos"""
        gdata = GraphData(self.cerramiento, self.climae, self.climai)
        self.grafico1.dibuja(gdata)
        self.grafico2.dibuja(gdata)
    
    def actualizatexto(self):
        """Actualiza texto descripción de cerramiento en ventana principal"""
        _m = self.cerramiento
        _tb = self.cerramientotxtb
        _tb.set_text("")
        _txt = "%s\n\n" % _m.nombre
        _tb.insert_with_tags_by_name(_tb.get_start_iter(), _txt, 'titulo')
        _cerrtxt = (u"\nR_total: %.3f [m²K/W]\n"
                    u"S_total = %.3f [m]\nU = %.3f [W/m²K]")
        for nombre, e, R, S in zip(_m.nombres, _m.espesores, _m.R, _m.S):
            _txt = u"%s:\n" % nombre
            _tb.insert_with_tags_by_name(_tb.get_end_iter(), _txt, 'capa')
            _txt = u"%.3f [m]\nR=%.3f [m²K/W]\nS=%.3f [m]\n" % (e, R, S)
            _tb.insert_with_tags_by_name(_tb.get_end_iter(), _txt, 'datoscapa')
        _txt = _cerrtxt % (_m.R_total, _m.S_total, _m.U)
        _tb.insert_with_tags_by_name(_tb.get_end_iter(), _txt, 'resultados')
        while gtk.events_pending():
            gtk.main_iteration()

    def actualizapie(self):
        """Actualiza pie de ventana principal"""
        _cerr = self.cerramiento
        g, pcond = _cerr.condensacion(self.climae.temp, self.climai.temp,
                                      self.climae.HR, self.climai.HR)
#        g, pevap = _cerr.evaporacion(temp_ext, temp_int,
#                                     HR_ext, HR_int, interfases=[2])
        if not g:
            _sg = 0.0
        else:
            _sg = sum(g)
        _text = u"Total: %.2f [g/m²mes]" % (2592000.0 * _sg)
        self.pie1.set_markup(_text)
        _text = (u"Cantidades condensadas: " +
                 u", ".join(["%.2f" % (2592000.0 * x,) for x in g]))
        self.pie2.set_markup(_text)

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
    import cerramiento
    from datos_ejemplo import climae, climai, cerramientocapas
    cerr = cerramiento.Cerramiento("Cerramiento tipo", "Tipo",
                                   cerramientocapas, Rse=0.04, Rsi=0.13)
    app = GtkCondensa(cerr, climae, climai)
    app.main()