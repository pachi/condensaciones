#!/usr/bin/env python
#encoding: utf-8
#
#   condensaciones.py
#   Programa de cálculo de condensaciones según CTE
#
#   Copyright (C) 2009-2010 por Rafael Villar Burke <pachi@rvburke.com>
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
"""Interfaz de usuario de Condensaciones en GTK+"""

import gtk
import pango
import util
import appmodel
from ptcanvas import CPTCanvas, CPCanvas, GraphData
import condensaicons
import webbrowser, datetime

class GtkCondensa(object):
    """Aplicación"""
    def __init__(self, cerramiento, climaext, climaint):
        """Inicialización de datos e interfaz
        
        cerramiento - Cerramiento
        climae - datos higrotérmicos del exterior
        climai - datos higrotérmicos del interior
        """
        self.model = appmodel.Model(cerramiento, climaext, climaint)
        UIFILE = util.get_resource('data', 'condensa.ui')
        self.ui = gtk.Builder()
        self.ui.add_from_file(UIFILE)
        self.graficaprestemp = self.ui.get_object('prestemp_canvas')
        self.graficapresiones = self.ui.get_object('presiones_canvas')
        self.capasls = self.ui.get_object('capas_liststore')
        self.capastv = self.ui.get_object('capas_treeview')
        self.materialesls = self.ui.get_object('materiales_liststore')
        self.ui.connect_signals(self)
        gtk.link_button_set_uri_hook(lambda b, u: webbrowser.open(u))
        self.createtexttags()
        self.createicons()
        self.cargadata()
        
    def createicons(self):
        """Crea iconos de aplicación y de botones de herramientas"""
        self.icons = condensaicons.IconFactory(self)
        self.ui.get_object('cerramselectbtn').set_stock_id('condensa-cerramientos')
        self.ui.get_object('climaselectbtn').set_stock_id('condensa-clima')

    def createtexttags(self):
        """Crea marcas de texto para estilos en textbuffer"""
        tb = self.ui.get_object('informe_txtbuffer')
        tb.create_tag("titulo",
                      weight=pango.WEIGHT_BOLD, scale=pango.SCALE_X_LARGE)
        tb.create_tag("titulo2",
                      style=pango.STYLE_ITALIC, scale=pango.SCALE_LARGE)
        tb.create_tag("subtitulo",
                      weight=pango.WEIGHT_BOLD, scale=pango.SCALE_LARGE,)
        tb.create_tag("capa", weight=pango.WEIGHT_BOLD, foreground="#777777")
        tb.create_tag("datoscapa", style=pango.STYLE_ITALIC, indent=30)
        tb.create_tag("resultados", scale=pango.SCALE_MEDIUM, foreground='blue')
        tb.create_tag("nota", scale=pango.SCALE_SMALL)

    def cargadata(self):
        """Carga datos de materiales y cerramientos"""
        for material in self.model.materiales:
            self.materialesls.append((material,))
        cerramientosls = self.ui.get_object('cerramientos_liststore')
        for nombre in self.model.cerramientos:
            descripcion = self.model.cerramientosDB[nombre].descripcion
            cerramientosls.append((nombre, descripcion))
        n = len(self.model.materiales)
        m = len(self.model.cerramientos)
        txt = "Cargados %i materiales, %i cerramientos" % (n, m)
        self.actualiza(txt)
    
    def title(self):
        modifiedmark = "*" if self.model.cerramientomodificado else ""
        txt = "Condensaciones - %s%s" % (self.model.c.nombre, modifiedmark)
        self.ui.get_object('window').set_title(txt)

    def quit(self, w):
        gtk.main_quit()

    def main(self):
        """Arranca la aplicación"""
        self.ui.get_object('window').show_all()
        gtk.main()

    def actualiza(self, txt=None, updategraphs=False):
        """Actualiza cabecera, gráficas, texto y pie de datos"""
        if txt:
            self.ui.get_object('statusbar').push(0, txt)
        self.title()
        self.model.calcula()
        self.actualizacabecera()
        self.actualizapie()
        self.actualizacapas()
        if updategraphs:
            self.actualizagraficas()
            self.actualizainforme()

    def actualizacabecera(self):
        """Actualiza texto de cabecera"""
        model = self.model
        cnombre = self.ui.get_object('nombre_cerramiento')
        cdescripcion = self.ui.get_object('descripcion_cerramiento')
        csubtitulo1 = self.ui.get_object('csubtitulo1')
        csubtitulo2 = self.ui.get_object('csubtitulo2')
        cnombre.props.label = model.c.nombre
        cdescripcion.props.label = model.c.descripcion
        txt = ('U = %.2f W/m²K, f<sub>Rsi</sub> ='
               ' %.2f, f<sub>Rsi,min</sub> = %.2f')
        csubtitulo1.props.label = txt % (model.c.U, model.fRsi, model.fRsimin)
        txt = ('T<sub>ext</sub> = %.2f°C, HR<sub>ext</sub> = %.1f%%, '
               'T<sub>int</sub> = %.2f°C, HR<sub>int</sub> = %.1f%%')
        csubtitulo2.props.label = txt % (model.climae.temp, model.climae.HR,
                                         model.climai.temp, model.climai.HR)
        COLOR_OK = gtk.gdk.color_parse("#AACCAA")
        COLOR_BAD = gtk.gdk.color_parse("#CCAAAA")
        state_color = COLOR_BAD if model.ccheck else COLOR_OK
        cfondo = self.ui.get_object('cfondo')
        cfondo.modify_bg(gtk.STATE_NORMAL, state_color)

    def actualizapie(self):
        """Actualiza pie de ventana principal"""
        _K = 2592000.0 # segundos por mes
        txt = "Total: %.2f [g/m²mes]" % (_K * self.model.totalg)
        self.ui.get_object('pie1').props.label = txt
        txt = ("Cantidades condensadas: " +
               ", ".join(["%.2f" % (_K * x,) for x in self.model.g]))
        self.ui.get_object('pie2').props.label = txt

    def actualizacapas(self):
        """Actualiza pestaña de capas con descripción, capas, Rse, Rsi"""
        rse = self.ui.get_object('Rsevalue')
        rsi = self.ui.get_object('Rsivalue')
        etotal = self.ui.get_object('espesortotal')
        rse.props.text = "%.2f" % float(self.model.c.Rse)
        rsi.props. text = "%.2f" % float(self.model.c.Rsi)
        etotal.props.label = "%.3f" % self.model.c.e
        self.capasls.clear()
        for i, (nombre, e, K, R, mu, S) in self.model.capasdata():
            d = ("%i" % i, nombre, "%.3f" % e,
                 "-" if not K else "%.4f" % K,
                 "%.4f" % R, "%i" % mu, "%.3f" % S)
            self.capasls.append(d)

    def actualizagraficas(self):
        """Redibuja gráficos con nuevos datos"""
        gdata = GraphData(self.model.c, self.model.climae, self.model.climai)
        self.graficaprestemp.clear()
        self.graficaprestemp.dibuja(gdata)
        self.graficapresiones.clear()
        self.graficapresiones.dibuja(gdata)
    
    def actualizainforme(self):
        """Actualiza texto descripción de cerramiento en ventana principal"""
        tb = self.ui.get_object('informe_txtbuffer')
        tb.props.text = ""
        # Denominación cerramiento
        tb.insert_with_tags_by_name(tb.get_start_iter(),
                                "%s\n" % self.model.c.nombre, 'titulo')
        tb.insert_with_tags_by_name(tb.get_end_iter(),
                                "%s\n\n" % self.model.c.descripcion, 'titulo2')
        # Condiciones ambientales
        txt = "Condiciones de cálculo\n"
        tb.insert_with_tags_by_name(tb.get_end_iter(), txt, 'subtitulo')
        txt = ("Temperatura exterior: %.1f [ºC]\n"
               "Humedad relativa exterior: %.1f [%%]\n"
               "Temperatura interior: %.1f [ºC]\n"
               "Humedad relativa interior: %.1f [%%]\n\n"
               "Resistencia superficial exterior: %.2f [m²K/W]\n"
               "Resistencia superficial exterior: %.2f [m²K/W]\n\n"
               ) % (self.model.climae.temp, self.model.climae.HR,
                    self.model.climai.temp, self.model.climai.HR,
                    self.model.c.Rse, self.model.c.Rsi)
        tb.insert_with_tags_by_name(tb.get_end_iter(), txt, 'datoscapa')
        # Cerramiento
        txt = "Descripción del cerramiento\n"
        tb.insert_with_tags_by_name(tb.get_end_iter(), txt, 'subtitulo')
        for i, (nombre, e, K, R, mu, S) in self.model.capasdata():
            txt = "%i - %s:\n" % (i, nombre)
            tb.insert_with_tags_by_name(tb.get_end_iter(), txt, 'capa')
            txt = ("%.3f [m]\nR=%.3f [m²K/W]\n"
                   "μ=%i\nS=%.3f [m]\n" % (e, R, mu, S))
            tb.insert_with_tags_by_name(tb.get_end_iter(), txt, 'datoscapa')
        txt = "Espesor total del cerramiento: %.3f m\n\n" % self.model.c.e
        tb.insert_with_tags_by_name(tb.get_end_iter(), txt, 'capa')
        # Gráficas
        txt = "Gráficas\n"
        tb.insert_with_tags_by_name(tb.get_end_iter(), txt, 'subtitulo')
        tb.insert_pixbuf(tb.get_end_iter(), self.graficaprestemp.pixbuf(600))
        tb.insert(tb.get_end_iter(), "\n\n")
        tb.insert_pixbuf(tb.get_end_iter(), self.graficapresiones.pixbuf(600))
        tb.insert(tb.get_end_iter(), "\n\n")
        # Resultados
        txt = "Resultados\n"
        tb.insert_with_tags_by_name(tb.get_end_iter(), txt, 'subtitulo')
        txt = ("R_total: %.3f [m²K/W]\nS_total = %.3f [m]\n"
               "Transmitancia térmica total: U = %.3f [W/m²K]\n"
               "f_Rsi = %.2f\nf_Rsimin = %.2f\n"
               ) % (self.model.c.R_total, self.model.c.S_total, self.model.c.U,
                    self.model.fRsi, self.model.fRsimin)
        tb.insert_with_tags_by_name(tb.get_end_iter(), txt, 'resultados')
        # Condensaciones
        cs = "Sí" if self.model.cs else "No"
        ci = "Sí" if self.model.ci else "No"
        txt = ("\n¿Existen condensaciones superficiales?: %s\n"
               "¿Existen condensaciones intersticiales?: %s\n") % (cs, ci)
        tb.insert_with_tags_by_name(tb.get_end_iter(), txt, 'resultados')
        # Nota copyright
        today = datetime.datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
        txt = ("\n\nInforme generado por 'Condensa' "
               "(www.rvburke.com/condensaciones.html) el %s\n\n"
               "'Condensa' es software libre que se distribuye bajo licencia "
               "GPLv2 o posterior.\n"
               "Copyright (c) 2009-2010 Rafael Villar Burke\n") % today
        tb.insert_with_tags_by_name(tb.get_end_iter(), txt, 'nota')
        while gtk.events_pending():
            gtk.main_iteration()

    # Selección de ambientes - diálogo ---------------------------------------

    def ambienteselecciona(self, widget):
        """Abre diálogo de selección de ambientes"""
        adialog = self.ui.get_object('ambiente_dlg')
        localidad = self.ui.get_object('localidadentry')
        te = self.ui.get_object('tempextentry')
        hre = self.ui.get_object('hrextentry')
        ti = self.ui.get_object('tempintentry')
        hri = self.ui.get_object('hrintentry')
        localidad.props.text = 'Localidad'
        te.props.text = "%.2f" % self.model.climae.temp
        hre.props.text ="%.2f" % self.model.climae.HR
        ti.props.text = "%.2f" % self.model.climai.temp
        hri.props.text = "%.2f" % self.model.climai.HR
        resultado = adialog.run()
        # gtk.RESPONSE_ACCEPT vs gtk.RESPONSE_CANCEL
        if resultado == gtk.RESPONSE_ACCEPT:
            self.model.set_climae(float(te.props.text), float(hre.props.text))
            self.model.set_climai(float(ti.props.text), float(hri.props.text))
            txt = "Seleccionadas nuevas condiciones ambientales"
            self.actualiza(txt, updategraphs=True)
        adialog.hide()
    
    # Selección de cerramientos - diálogo ------------------------------------
    
    def cerramientoselecciona(self, widget):
        """Abre diálogo de selección de cerramiento"""
        lblselected = self.ui.get_object('lblselected')
        resultado = self.ui.get_object('cerramiento_dlg').run()
        # gtk.RESPONSE_ACCEPT vs gtk.RESPONSE_CANCEL
        if resultado == gtk.RESPONSE_ACCEPT:
            nombrecerr = lblselected.props.label
            self.model.set_cerramiento(nombrecerr)
            txt = "Seleccionado nuevo cerramiento activo: %s" % nombrecerr
            self.actualiza(txt, updategraphs=True)
        self.ui.get_object('cerramiento_dlg').hide()

    def cerramientoactiva(self, tv):
        """Cambia cerramiento seleccionado en lista de cerramientos"""
        lblselected = self.ui.get_object('lblselected')
        cerrtm, cerrtm_iter = tv.get_selection().get_selected()
        lblselected.props.label = cerrtm[cerrtm_iter][0]
    
    def cerramientoadd(self, widget):
        ctv = self.ui.get_object('cerramientotv')
        cerrtm, cerrtm_iter = ctv.get_selection().get_selected()
        if cerrtm_iter:
            cerri = int(cerrtm.get_path(cerrtm_iter)[0])
            newcerr = self.model.cerramientoadd(cerri)
            cerrtm.insert(cerri + 1, row=(newcerr.nombre, newcerr.descripcion))
            txt = "Añadido cerramiento nuevo: %s" % newcerr.nombre
            self.ui.get_object('statusbar').push(0, txt)
            ctv.set_cursor(cerri + 1)

    def cerramientoremove(self, widget):
        ctv = self.ui.get_object('cerramientotv')
        cerrtm, cerrtm_iter = ctv.get_selection().get_selected()
        if cerrtm_iter:
            cerri = int(cerrtm.get_path(cerrtm_iter)[0])
            self.model.cerramientoremove(cerri)
            cerrtm.remove(cerrtm_iter)
            self.ui.get_object('statusbar').push(0, "Eliminado cerramiento")
            if cerri == 0: cerri = 1
            ctv.set_cursor(cerri - 1)

    def cerramientoup(self, widget):
        ctv = self.ui.get_object('cerramientotv')
        cerrtm, cerrtm_iter = ctv.get_selection().get_selected()
        if cerrtm_iter:
            cerri = int(cerrtm.get_path(cerrtm_iter)[0])
            if cerri == 0:
                return
            self.model.cerramientoswap(cerri - 1, cerri)
            previter = cerrtm.get_iter(cerri - 1)
            cerrtm.swap(cerrtm_iter, previter)

    def cerramientodown(self, widget):
        ctv = self.ui.get_object('cerramientotv')
        cerrtm, cerrtm_iter = ctv.get_selection().get_selected()
        if cerrtm_iter:
            cerri = int(cerrtm.get_path(cerrtm_iter)[0])
            if cerri == len(self.model.cerramientos) - 1:
                return
            self.model.cerramientoswap(cerri + 1, cerri)
            nextiter = cerrtm.get_iter(cerri + 1)
            cerrtm.swap(cerrtm_iter, nextiter)

    # Retrollamadas de modificación de capas ----------------------------------
 
    def capacambiamaterial(self, cr, path, new_iter):
        """Cambio de material de la capa en el combo de la vista de capas
        
        cr - Comboboxcellrenderer con contenido modificado
        path - ruta del combo en el treeview
        new_iter - ruta del nuevo valor en el modelo del combo
        """
        capaindex = int(self.capasls[path][0])
        currentname, currente = self.model.c.capas[capaindex]
        newname = self.materialesls[new_iter][0].decode('utf-8')
        if newname != currentname:
            self.model.set_capa(capaindex, newname, float(currente))
            msg = "Modificado material de capa %i: %s" % (capaindex, newname)
            self.actualiza(msg)

    def capacambiaespesor(self, cr, path, new_text):
        """Cambio de espesor en la vista de capas
        
        cr - cellrenderertext que cambia
        path - ruta del cellrenderer en el treeview
        new_text - nuevo texto en la celda de texto
        """
        capaindex = int(self.capasls[path][0])
        currentname = self.capasls[path][1].decode('utf-8')
        currente = float(self.capasls[path][2])
        try:
            newe = float(new_text)
        except ValueError:
            return
        if newe != currente:
            self.model.set_capa(capaindex, currentname, newe)
            msg = "Modificado espesor de capa %i a %f [m]" % (capaindex, newe)
            self.actualiza(msg)

    def capaadd(self, btn):
        """Añade capa a cerramiento en vista de capas"""
        cerrtm, cerrtm_iter = self.capastv.get_selection().get_selected()
        if cerrtm_iter:
            capai = int(cerrtm[cerrtm_iter][0])
            self.model.capaadd(capai)
            self.actualiza("Añadida capa %i" % (capai + 1))
            self.capastv.set_cursor(capai + 1)

    def caparemove(self, btn):
        """Elimina capa seleccionada de cerramiento en vista de capas"""
        cerrtm, cerrtm_iter = self.capastv.get_selection().get_selected()
        if cerrtm_iter:
            capai = int(cerrtm[cerrtm_iter][0])
            self.model.caparemove(capai)
            if capai == 0: capai = 1
            self.actualiza("Eliminada capa %i" % capai)
            self.capastv.set_cursor(capai - 1)

    def capaup(self, btn):
        """Sube capa seleccionada de cerramiento en vista de capas"""
        cerrtm, cerrtm_iter = self.capastv.get_selection().get_selected()
        if cerrtm_iter:
            capai = int(cerrtm[cerrtm_iter][0])
            if capai > 0:
                self.model.capaup(capai)
                self.actualiza("Desplazada capa %i" % capai)
                self.capastv.set_cursor(capai - 1)

    def capadown(self, btn):
        """Baja capa seleccionada de cerramiento en vista de capas"""
        cerrtm, cerrtm_iter = self.capastv.get_selection().get_selected()
        if cerrtm_iter:
            capai = int(cerrtm[cerrtm_iter][0])
            if capai + 1 < len(self.model.c.capas):
                self.model.capadown(capai)
                self.actualiza("Desplazada capa %i" % capai)
                self.capastv.set_cursor(capai + 1)

    def capacambiarse(self, entry, event=None):
        """Toma valor de Rse al activar entry o cambiar el foco"""
        oldrse = self.model.c.Rse
        try:
            newrse = float(entry.props.text)
        except ValueError:
            entry.props.text = oldrse
            return
        if newrse != oldrse:
            self.model.set_Rse(newrse)
            self.actualiza("Nuevo Rse: %.2f" % newrse)

    def capacambiarsi(self, entry, event=None):
        """Toma valor de Rsi al activar entry o cambiar el foco"""
        oldrsi = self.model.c.Rsi
        try:
            newrsi = float(entry.props.text)
        except ValueError:
            entry.props.text = oldrsi
            return
        if newrsi != oldrsi:
            self.model.set_Rsi(newrsi)
            self.actualiza("Nuevo Rsi: %.2f" % newrsi)

    # Retrollamadas generales -------------------------------------------------

    def cambiahoja(self, notebook, page, pagenum):
        """Cambia hoja activa en la interfaz y actualiza gráficas si procede"""
        CREDITOS, CAPAS, GRAFICAPT, GRAFICAPV, INFORME = 0, 1, 2, 3, 4
        if pagenum == GRAFICAPT or pagenum == GRAFICAPV:
            self.actualizagraficas()
        elif pagenum == INFORME:
            self.actualizagraficas()
            self.actualizainforme()