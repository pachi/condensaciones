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

import os
import gtk
import pango
import util
import capas
import comprobaciones
from ptcanvas import CPTCanvas, CPCanvas, GraphData

COLOR_OK = gtk.gdk.color_parse("#AACCAA")
COLOR_BAD = gtk.gdk.color_parse("#CCAAAA")

class GtkCondensa(object):
    def __init__(self, muro, climae, climai):
        self.muro = muro
        self.climae = climae
        self.climai = climai

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
        self.textview = builder.get_object('murotextview')
        self.murotextbuffer = builder.get_object('murotextbuffer')
        self.murotextbuffer.create_tag("titulo",
                                       weight=pango.WEIGHT_BOLD,
                                       scale=pango.SCALE_X_LARGE)
        self.murotextbuffer.create_tag("capa",
                                       weight=pango.WEIGHT_BOLD)
        self.murotextbuffer.create_tag("datoscapa",
                                       style=pango.STYLE_ITALIC,
                                       indent=30)
        self.murotextbuffer.create_tag("resultados",
                                       foreground='blue',
                                       scale=pango.SCALE_LARGE)
        # - pie -
        self.pie1 = builder.get_object('pie1')
        self.pie2 = builder.get_object('pie2')
        # Controles de diálogo de selección de muros
        self.dlg = builder.get_object('dialogomuro')
        self.tvmuro = builder.get_object('tvmuro')
        self.lblselected = builder.get_object('lblselected')
        self.lsmuros = builder.get_object('liststoremuros')

        smap = {"on_window_destroy" : gtk.main_quit,
                "on_botonmuro_clicked": self.on_botonmuro_clicked,
                "on_tvmuro_cursor_changed" : self.on_tvmuro_cursor_changed,}
        builder.connect_signals(smap)
        
        self.cargamuros()
        self.actualiza()
        
    def main(self):
        self.w.show_all()
        gtk.main()

    def cargamuros(self):
        #TODO: cargar datos de biblioteca
        from datos_ejemplo import muros
        listamuros = []
        for muro in muros:
            row = [str(muro.nombre), str(muro)]
            listamuros.append(row)
            #print row
        #datosmuro = [('M1',), ('M2',), ('M3',), ('M4',)]
        datosmuro = listamuros
        for muro in datosmuro:
            pass
            #print muro
            # XXX: No se puede cargar el muro porque la segunda columna debería
            # XXX: ser un PyGobject, y no un Gobject nada más... (glade no
            # XXX: permite seleccionar ese tipo)
            #self.lsmuros.append(muro)

    def actualiza(self):
        self.actualizacabecera()
        self.actualizagraficas()
        self.actualizatexto()
        self.actualizapie()

    def actualizacabecera(self):
        ti = self.climai.temp
        hri = self.climai.HR
        te = self.climae.temp
        hre = self.climae.HR
        fRsi = comprobaciones.fRsi(self.muro.U)
        fRsimin = comprobaciones.fRsimin(te, ti, hri)
        ccheck = comprobaciones.condensaciones(self.muro, te, ti, hre, hri)
        _text = u'<span size="x-large">%s</span>' % self.muro.nombre
        self.ctitulo.set_markup(_text)
        _text = (u'U = %.2f W/m²K, f<sub>Rsi</sub> ='
                 u' %.2f, f<sub>Rsi,min</sub> = %.2f')
        self.csubtitulo1.set_markup(_text % (self.muro.U, fRsi, fRsimin))
        _text = (u'T<sub>int</sub> = %.2f°C, HR<sub>int</sub> = %.1f%%, '
                 u'T<sub>ext</sub> = %.2f°C, HR<sub>ext</sub> = %.1f%%')
        self.csubtitulo2.set_markup(_text % (ti, hri, te, hre))
        self.cfondo.modify_bg(gtk.STATE_NORMAL,
                              ccheck and COLOR_BAD or COLOR_OK)

    def actualizagraficas(self):
        gdata = GraphData(self.muro, self.climae, self.climai)
        self.grafico1.dibuja(gdata)
        self.grafico2.dibuja(gdata)
    
    def actualizatexto(self):
        "Mostrar texto"
        m = self.muro
        _tb = self.murotextbuffer
        _tb.set_text("")
        text = "%s\n\n" % m.nombre
        _tb.insert_with_tags_by_name(_tb.get_start_iter(), text, 'titulo')
        _murotxt = (u"\nR_total: %.3f [m²K/W]\n"
                    u"S_total = %.3f [m]\nU = %.3f [W/m²K]")
        for nombre, e, R, S in zip(m.nombres, m.espesores, m.R, m.S):
            text = u"%s:\n" % nombre
            _tb.insert_with_tags_by_name(_tb.get_end_iter(), text, 'capa')
            text = u"%.3f [m]\nR=%.3f [m²K/W]\nS=%.3f [m]\n" % (e, R, S)
            _tb.insert_with_tags_by_name(_tb.get_end_iter(), text, 'datoscapa')
        text = _murotxt % (m.R_total, m.S_total, m.U)
        _tb.insert_with_tags_by_name(_tb.get_end_iter(), text, 'resultados')
        while gtk.events_pending():
            gtk.main_iteration()

    def actualizapie(self):
        g, pcond = self.muro.condensacion(self.climae.temp, self.climai.temp,
                                          self.climae.HR, self.climai.HR)
#        g, pevap = self.muro.evaporacion(temp_ext, temp_int,
#                                         HR_ext, HR_int, interfases=[2])
        if not g:
            g = 0.0
        _text = u"Total: %.2f [g/m²mes]" % (2592000.0 * sum(g))
        self.pie1.set_markup(_text)
        _text = (u"Cantidades condensadas: " +
                 u", ".join(["%.2f" % (2592000.0 * x,) for x in g]))
        self.pie2.set_markup(_text)

    # -- Retrollamadas ventana principal --
    def on_botonmuro_clicked(self, widget):
        resultado = self.dlg.run()
        # gtk.RESPONSE_ACCEPT == -3, gtk.RESPONSE_CANCEL == -6
        if resultado == gtk.RESPONSE_ACCEPT:
            nombremuro = self.lblselected.get_text()
            #TODO: Cambiar datos de muro
            #self.muro = buscamurodesdenombre(nombremuro)
            self.muro.nombre = nombremuro
            self.actualiza()
        self.dlg.hide()

    # -- Retrollamadas diálogo muros --
    def on_tvmuro_cursor_changed(self, tv):
        _murotm, _murotm_iter = self.tvmuro.get_selection().get_selected()
        value = _murotm.get_value(_murotm_iter, 0)
        self.lblselected.set_text(value)

if __name__ == "__main__":
    from datos_ejemplo import climae, climai, murocapas
    muro = capas.Cerramiento("Cerramiento tipo", murocapas, 0.04, 0.13)
    app = GtkCondensa(muro, climae, climai)
    app.main()