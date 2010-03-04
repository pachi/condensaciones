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
import webbrowser

COLOR_OK = gtk.gdk.color_parse("#AACCAA")
COLOR_BAD = gtk.gdk.color_parse("#CCAAAA")

class GtkCondensa(object):
    """Aplicación"""
    def __init__(self, cerramiento=None, climaext=None, climaint=None):
        """Inicialización de datos e interfaz
        
        cerramiento - Cerramiento
        climae - datos higrotérmicos del exterior
        climai - datos higrotérmicos del interior
        """
        self.cerramiento = cerramiento # Cerramiento actual
        self.modificado = False # Cerramiento modificado vs estado inicial
        self.climae = climaext #FIXME: or Clima() para evitar valor None?
        self.climai = climaint #FIXME: or Clima() para evitar valor None?
        # Cerramientos disponibles
        self.cerramientos = {}
        # --- UI ---
        UIFILE = util.get_resource('data', 'condensa.ui')
        builder = gtk.Builder()
        builder.add_from_file(UIFILE)
        self.builder = builder
        # Controles ventana principal
        self.w = builder.get_object('window1')
        self.statusbar = builder.get_object('statusbar')
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
        # - pestaña de capas -
        self.rse = builder.get_object('Rsevalue')
        self.rsi = builder.get_object('Rsivalue')
        self.capasls = builder.get_object('capas_liststore')
        # Controles de diálogo de selección de cerramientos
        self.dlg = builder.get_object('cerramientodlg')
        self.cerramientotv = builder.get_object('cerramientotv')
        self.cerramientols = builder.get_object('cerramientos_liststore')
        # Materiales
        self.materialesls = builder.get_object('materiales_liststore')

        smap = {"on_window_destroy": gtk.main_quit,
                "on_cbtn_clicked": self.on_cerramientobtn_clicked,
                "on_ctv_cursor_changed": self.on_cerramientotv_cursor_changed,
                "on_ctnombre_changed": self.on_ctnombre_changed,
                "on_ctespesor_changed": self.on_ctespesor_changed,
                }
        builder.connect_signals(smap)
        
        gtk.link_button_set_uri_hook(self.open_url)
        self.cargacerramientos()
        self.actualiza()
        
    def main(self):
        """Arranca la aplicación"""
        self.w.show_all()
        gtk.main()

    def cargacerramientos(self):
        """Carga datos de materiales y cerramientos"""
        from datos_ejemplo import cerramientos, materiales
        mats = materiales.keys()
        mats.sort()
        for material in mats:
            self.materialesls.append((material,))
        for c in cerramientos:
            self.cerramientos[c.nombre] = c
            self.cerramientols.append((c.nombre, c.descripcion))
        n = len(materiales)
        m = len(cerramientos)
        txt = u"Cargados %i materiales, %i cerramientos" % (n, m)
        self.statusbar.push(0, txt)

    def actualiza(self):
        """Actualiza cabecera, gráficas, texto y pie de datos"""
        self.calcula()
        self.actualizacabecera()
        self.actualizapie()
        self.actualizacapas()
        self.actualizagraficas()
        self.actualizainforme()

    def calcula(self):
        """Calcula resultados para usarlos en presentación"""
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
        cfondo = self.builder.get_object('cfondo')
        cnombre = self.builder.get_object('nombre_cerramiento')
        cdescripcion = self.builder.get_object('descripcion_cerramiento')
        csubtitulo1 = self.builder.get_object('csubtitulo1')
        csubtitulo2 = self.builder.get_object('csubtitulo2')
        
        cnombre.set_text(self.cerramiento.nombre)
        cdescripcion.set_text(self.cerramiento.descripcion)
        txt = (u'U = %.2f W/m²K, f<sub>Rsi</sub> ='
                 u' %.2f, f<sub>Rsi,min</sub> = %.2f')
        csubtitulo1.set_markup(txt % (self.cerramiento.U,
                                      self.fRsi, self.fRsimin))
        txt = (u'T<sub>ext</sub> = %.2f°C, HR<sub>ext</sub> = %.1f%%, '
               u'T<sub>int</sub> = %.2f°C, HR<sub>int</sub> = %.1f%%')
        csubtitulo2.set_markup(txt % (self.climae.temp, self.climae.HR,
                                      self.climai.temp, self.climai.HR))
        cfondo.modify_bg(gtk.STATE_NORMAL,
                         self.ccheck and COLOR_BAD or COLOR_OK)

    def actualizapie(self):
        """Actualiza pie de ventana principal"""
        SEGUNDOSPORMES = 2592000.0
        txt = u"Total: %.2f [g/m²mes]" % (SEGUNDOSPORMES * self.totalg)
        pie1 = self.builder.get_object('pie1')
        pie1.set_markup(txt)
        txt = (u"Cantidades condensadas: " +
                 u", ".join(["%.2f" % (SEGUNDOSPORMES * x,) for x in self.g]))
        pie2 = self.builder.get_object('pie2')
        pie2.set_markup(txt)

    def actualizacapas(self):
        """Actualiza pestaña de capas con descripción, capas, Rse, Rsi"""
        c = self.cerramiento
        self.rse.set_text("%.2f" % float(c.Rse))
        self.rsi.set_text("%.2f" % float(c.Rsi))
        self.capasls.clear()
        for i, (nombre, e, K, R) in enumerate(zip(c.nombres,
                                               c.espesores,
                                               c.K,
                                               c.R[1:-1] #quitamos Rse, Rsi
                                               )):
            self.capasls.append((i, nombre, "%.3f" % e, "%.4f" % K, "%.4f" % R))

    def actualizagraficas(self):
        """Redibuja gráficos con nuevos datos"""
        gdata = GraphData(self.cerramiento, self.climae, self.climai)
        self.grafico1.clear()
        self.grafico1.dibuja(gdata)
        self.grafico2.clear()
        self.grafico2.dibuja(gdata)
    
    def actualizainforme(self):
        """Actualiza texto descripción de cerramiento en ventana principal"""
        m = self.cerramiento
        tb = self.cerramientotxtb
        tb.set_text("")
        tb.insert_with_tags_by_name(tb.get_start_iter(),
                                      u"%s\n" % m.nombre, 'titulo')
        tb.insert_with_tags_by_name(tb.get_end_iter(),
                                      u"%s\n\n" % m.descripcion, 'titulo2')
        # Capas
        tb.insert_with_tags_by_name(tb.get_end_iter(),
                                      u"Descripción\n", 'subtitulo')
        for i, (nombre, e, R, S) in enumerate(zip(m.nombres, m.espesores,
                                                  m.R, m.S)):
            tb.insert_with_tags_by_name(tb.get_end_iter(),
                                         u"%i - %s:\n" % (i, nombre), 'capa')
            txt = u"%.3f [m]\nR=%.3f [m²K/W]\nS=%.3f [m]\n" % (e, R, S)
            tb.insert_with_tags_by_name(tb.get_end_iter(), txt, 'datoscapa')
        # Resultados
        tb.insert_with_tags_by_name(tb.get_end_iter(),
                                      u"\nResultados\n", 'subtitulo')
        self.grafico1.save('g1.png')
        pb1 = gtk.gdk.pixbuf_new_from_file_at_size('g1.png', 600, 400)
        tb.insert_pixbuf(tb.get_end_iter(), pb1)
        self.grafico2.save('g2.png')
        tb.insert(tb.get_end_iter(), u"\n\n")
        pb2 = gtk.gdk.pixbuf_new_from_file_at_size('g2.png', 600, 400)
        tb.insert_pixbuf(tb.get_end_iter(), pb2)
        tb.insert(tb.get_end_iter(), u"\n\n")
        txt = (u"R_total: %.3f [m²K/W]\n"
                u"S_total = %.3f [m]\n"
                u"U = %.3f [W/m²K]\n"
                u"f_Rsi = %.2f\n"
                u"f_Rsimin = %.2f\n") % (m.R_total, m.S_total, m.U,
                                       self.fRsi, self.fRsimin)
        tb.insert_with_tags_by_name(tb.get_end_iter(), txt, 'resultados')
        # Condensaciones
        cs = self.cs and "Sí" or "No"
        ci = self.ci and "Sí" or "No"
        tb.insert_with_tags_by_name(tb.get_end_iter(),
                                     (u"\nCondensaciones superficiales: %s\n"
                                      u"Condensaciones intersticiales: %s\n"
                                     ) % (cs, ci),
                                     'resultados')
        while gtk.events_pending():
            gtk.main_iteration()

    def open_url(self, button, url):
        """Abre dirección web en navegador predeterminado"""
        webbrowser.open(url)
        
    def on_cerramientobtn_clicked(self, widget):
        """Abrir diálogo de selección de cerramiento"""
        lblselected = self.builder.get_object('lblselected')
        resultado = self.dlg.run()
        # gtk.RESPONSE_ACCEPT vs gtk.RESPONSE_CANCEL
        if resultado == gtk.RESPONSE_ACCEPT:
            nombrecerr = lblselected.get_text()
            self.cerramiento = self.cerramientos[nombrecerr]
            self.actualiza()
        self.dlg.hide()

    def on_cerramientotv_cursor_changed(self, tv):
        """Cambio de cerramiento seleccionado en lista de cerramientos"""
        cerrtm, cerrtm_iter = tv.get_selection().get_selected()
        value = cerrtm.get_value(cerrtm_iter, 0)
        lblselected = self.builder.get_object('lblselected')
        lblselected.set_text(value)

    def on_ctnombre_changed(self, cr, path, new_iter):
        """Cambio de capa en el combo
        
        cr - Comboboxcellrenderer con contenido modificado
        path - ruta del combo en el treeview
        new_iter - ruta del nuevo valor en el modelo del combo
        """
        capaindex = int(self.capasls[path][0])
        oldtext, ecapa = self.cerramiento.capas[capaindex]
        newtext = self.materialesls[new_iter][0].decode('utf-8')
        self.cerramiento.capas[capaindex] = (newtext, float(ecapa))
        self.modificado = True
        try:
            self.actualiza()
        except:
            self.cerramiento.capas[capaindex] = (oldtext, float(ecapa))

    def on_ctespesor_changed(self, cr, path, new_text):
        """Cambio de capa en la entrada de espesor
        
        cr - cellrenderertext que cambia
        path - ruta del cellrenderer en el treeview
        new_text - nuevo texto en la celda de texto
        """
        capaindex = int(self.capasls[path][0])
        ncapa = self.cerramiento.capas[capaindex][0]
        try:
            newe = float(new_text)
            self.cerramiento.capas[capaindex] = (ncapa, newe)
            self.modificado = True
            self.actualiza()
        except ValueError:
            pass

if __name__ == "__main__":
    from cerramiento import Cerramiento
    from datos_ejemplo import climae, climai, cerramientocapas
    _c = Cerramiento("Cerramiento tipo", "Tipo",
                       cerramientocapas, Rse=0.04, Rsi=0.13)
    app = GtkCondensa(_c, climae, climai)
    app.main()