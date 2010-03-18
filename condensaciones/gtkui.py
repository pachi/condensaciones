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
import comprobaciones
from ptcanvas import CPTCanvas, CPCanvas, GraphData, get_pixbuf_from_canvas
import webbrowser, datetime

class GtkCondensa(object):
    """Aplicación"""
    def __init__(self, cerramiento, climaext, climaint):
        """Inicialización de datos e interfaz
        
        cerramiento - Cerramiento
        climae - datos higrotérmicos del exterior
        climai - datos higrotérmicos del interior
        """
        self.cerramiento = cerramiento # Cerramiento actual
        self.climae = climaext
        self.climai = climaint
        self.cerramientomodificado = False
        self.graphsredrawpending = True
        self.cerramientosDB = {}
        UIFILE = util.get_resource('data', 'condensa.ui')
        self.builder = gtk.Builder()
        self.builder.add_from_file(UIFILE)
        self.statusbar = self.builder.get_object('statusbar')
        self.graficaprestemp = self.builder.get_object('prestemp_canvas')
        self.graficapresiones = self.builder.get_object('presiones_canvas')
        self.informetxtbuffer = self.builder.get_object('informe_txtbuffer')
        self.createtexttags()
        self.capasls = self.builder.get_object('capas_liststore')
        self.capastv = self.builder.get_object('capas_treeview')
        self.materialesls = self.builder.get_object('materiales_liststore')
        self.cerramientols = self.builder.get_object('cerramientos_liststore')
        self.adlg = self.builder.get_object('ambiente_dlg')
        self.dlg = self.builder.get_object('cerramiento_dlg')
        smap = {"on_window_destroy": gtk.main_quit,
                "on_abtn_clicked": self.ambienteselecciona,
                "on_cbtn_clicked": self.cerramientoselecciona,
                "on_ctv_cursor_changed": self.cerramientoactiva,
                "on_ctnombre_changed": self.capacambiamaterial,
                "on_ctespesor_changed": self.capacambiaespesor,
                "on_capaaddbtn_clicked": self.capaadd,
                "on_caparemovebtn_clicked": self.caparemove,
                "on_capaupbtn_clicked": self.capaup,
                "on_capadownbtn_clicked": self.capadown,
                "on_rsevalue_activate": self.capacambiarse,
                "on_rsevalue_focusout": self.capacambiarse,
                "on_rsivalue_activate": self.capacambiarsi,
                "on_rsivalue_focusout": self.capacambiarsi,
                "on_notebook_switch_page": self.cambiahoja,
                }
        self.builder.connect_signals(smap)
        gtk.link_button_set_uri_hook(lambda b, u: webbrowser.open(u))
        self.cargacerramientos()
        self.actualiza()

    def createtexttags(self):
        """Crea marcas de texto para estilos en textbuffer"""
        tb = self.informetxtbuffer
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

    def main(self):
        """Arranca la aplicación"""
        self.builder.get_object('window1').show_all()
        self.statusbar.push(0, "Aplicación inicializada")
        gtk.main()

    def cargacerramientos(self):
        """Carga datos de materiales y cerramientos"""
        from datos_ejemplo import cerramientos, materiales
        mats = materiales.keys()
        mats.sort()
        for material in mats:
            self.materialesls.append((material,))
        for c in cerramientos:
            self.cerramientosDB[c.nombre] = c
            self.cerramientols.append((c.nombre, c.descripcion))
        n = len(materiales)
        m = len(cerramientos)
        txt = "Cargados %i materiales, %i cerramientos" % (n, m)
        self.statusbar.push(0, txt)

    def actualiza(self):
        """Actualiza cabecera, gráficas, texto y pie de datos"""
        self.calcula()
        self.actualizacabecera()
        self.actualizapie()
        self.actualizacapas()

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
        cnombre = self.builder.get_object('nombre_cerramiento')
        cnombre.set_text(self.cerramiento.nombre)
        cdescripcion = self.builder.get_object('descripcion_cerramiento')
        cdescripcion.set_text(self.cerramiento.descripcion)
        txt = ('U = %.2f W/m²K, f<sub>Rsi</sub> ='
               ' %.2f, f<sub>Rsi,min</sub> = %.2f')
        csubtitulo1 = self.builder.get_object('csubtitulo1')
        csubtitulo1.set_markup(txt % (self.cerramiento.U,
                                      self.fRsi, self.fRsimin))
        txt = ('T<sub>ext</sub> = %.2f°C, HR<sub>ext</sub> = %.1f%%, '
               'T<sub>int</sub> = %.2f°C, HR<sub>int</sub> = %.1f%%')
        csubtitulo2 = self.builder.get_object('csubtitulo2')
        csubtitulo2.set_markup(txt % (self.climae.temp, self.climae.HR,
                                      self.climai.temp, self.climai.HR))
        COLOR_OK = gtk.gdk.color_parse("#AACCAA")
        COLOR_BAD = gtk.gdk.color_parse("#CCAAAA")
        state_color = self.ccheck and COLOR_BAD or COLOR_OK
        cfondo = self.builder.get_object('cfondo')
        cfondo.modify_bg(gtk.STATE_NORMAL, state_color)

    def actualizapie(self):
        """Actualiza pie de ventana principal"""
        SEGUNDOSPORMES = 2592000.0
        txt = "Total: %.2f [g/m²mes]" % (SEGUNDOSPORMES * self.totalg)
        pie1 = self.builder.get_object('pie1')
        pie1.set_markup(txt)
        txt = ("Cantidades condensadas: " +
               ", ".join(["%.2f" % (SEGUNDOSPORMES * x,) for x in self.g]))
        pie2 = self.builder.get_object('pie2')
        pie2.set_markup(txt)

    def actualizacapas(self):
        """Actualiza pestaña de capas con descripción, capas, Rse, Rsi"""
        rse = self.builder.get_object('Rsevalue')
        rsi = self.builder.get_object('Rsivalue')
        c = self.cerramiento
        rse.set_text("%.2f" % float(c.Rse))
        rsi.set_text("%.2f" % float(c.Rsi))
        self.capasls.clear()
        for i, (nombre, e, K, R) in enumerate(zip(c.nombres,
                                               c.espesores,
                                               c.K,
                                               c.R[1:-1] #quitamos Rse, Rsi
                                               )):
            # En materiales "resistivos" no está definido K
            Ktext = "-" if not K else "%.4f" % K
            d = ("%i" % i, nombre, "%.3f" % e, Ktext, "%.4f" % R)
            self.capasls.append(d)

    def actualizagraficas(self):
        """Redibuja gráficos con nuevos datos"""
        gdata = GraphData(self.cerramiento, self.climae, self.climai)
        self.graficaprestemp.clear()
        self.graficaprestemp.dibuja(gdata)
        self.graficapresiones.clear()
        self.graficapresiones.dibuja(gdata)
    
    def actualizainforme(self):
        """Actualiza texto descripción de cerramiento en ventana principal"""
        m = self.cerramiento
        tb = self.informetxtbuffer
        tb.set_text("")
        # Denominación cerramiento
        tb.insert_with_tags_by_name(tb.get_start_iter(),
                                    "%s\n" % m.nombre, 'titulo')
        tb.insert_with_tags_by_name(tb.get_end_iter(),
                                    "%s\n\n" % m.descripcion, 'titulo2')
        # Condiciones ambientales
        txt = "Condiciones de cálculo\n"
        tb.insert_with_tags_by_name(tb.get_end_iter(), txt, 'subtitulo')
        txt = ("Temperatura exterior: %.1f [ºC]\n"
               "Humedad relativa exterior: %.1f [%%]\n"
               "Temperatura interior: %.1f [ºC]\n"
               "Humedad relativa interior: %.1f [%%]\n\n"
               "Resistencia superficial exterior: %.2f [m²K/W]\n"
               "Resistencia superficial exterior: %.2f [m²K/W]\n\n"
               ) % (self.climae.temp, self.climae.HR,
                    self.climai.temp, self.climai.HR,
                    self.cerramiento.Rse, self.cerramiento.Rsi)
        tb.insert_with_tags_by_name(tb.get_end_iter(), txt, 'datoscapa')
        # Cerramiento
        txt = "Descripción del cerramiento\n"
        tb.insert_with_tags_by_name(tb.get_end_iter(), txt, 'subtitulo')
        for i, (nombre, e, R, S) in enumerate(zip(m.nombres, m.espesores,
                                                  m.R, m.S)):
            txt = "%i - %s:\n" % (i, nombre)
            tb.insert_with_tags_by_name(tb.get_end_iter(), txt, 'capa')
            txt = "%.3f [m]\nR=%.3f [m²K/W]\nS=%.3f [m]\n\n" % (e, R, S)
            tb.insert_with_tags_by_name(tb.get_end_iter(), txt, 'datoscapa')
        # Gráficas
        txt = "Gráficas\n"
        tb.insert_with_tags_by_name(tb.get_end_iter(), txt, 'subtitulo')
        pb1 = get_pixbuf_from_canvas(self.graficaprestemp, 600)
        tb.insert_pixbuf(tb.get_end_iter(), pb1)
        tb.insert(tb.get_end_iter(), "\n\n")
        pb2 = get_pixbuf_from_canvas(self.graficapresiones, 600)
        tb.insert_pixbuf(tb.get_end_iter(), pb2)
        tb.insert(tb.get_end_iter(), "\n\n")
        # Resultados
        txt = "Resultados\n"
        tb.insert_with_tags_by_name(tb.get_end_iter(), txt, 'subtitulo')
        txt = ("R_total: %.3f [m²K/W]\nS_total = %.3f [m]\n"
               "U = %.3f [W/m²K]\nf_Rsi = %.2f\nf_Rsimin = %.2f\n"
               ) % (m.R_total, m.S_total, m.U, self.fRsi, self.fRsimin)
        tb.insert_with_tags_by_name(tb.get_end_iter(), txt, 'resultados')
        # Condensaciones
        cs = self.cs and "Sí" or "No"
        ci = self.ci and "Sí" or "No"
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
        localidad = self.builder.get_object('localidadentry')
        te = self.builder.get_object('tempextentry')
        hre = self.builder.get_object('hrextentry')
        ti = self.builder.get_object('tempintentry')
        hri = self.builder.get_object('hrintentry')
        
        localidad.set_text('Localidad')
        te.set_text("%.2f" % self.climae.temp)
        hre.set_text("%.2f" % self.climae.HR)
        ti.set_text("%.2f" % self.climai.temp)
        hri.set_text("%.2f" % self.climai.HR)
        resultado = self.adlg.run()
        # gtk.RESPONSE_ACCEPT vs gtk.RESPONSE_CANCEL
        if resultado == gtk.RESPONSE_ACCEPT:
            self.climae.temp = float(te.get_text())
            self.climae.HR = float(hre.get_text())
            self.climai.temp = float(ti.get_text())
            self.climai.HR = float(hri.get_text())
            self.actualiza()
            #XXX: Se podría retrasar si fuese necesario por rendimiento
            #XXX: Además no se redibujan bien si se está mostrando una pestaña
            #XXX: gráfica.
            self.actualizagraficas()
            self.actualizainforme()
            txt = "Seleccionadas nuevas condiciones ambientales"
            self.statusbar.push(0, txt)
        self.adlg.hide()
    
    # Selección de cerramientos - diálogo ------------------------------------
    
    def cerramientoselecciona(self, widget):
        """Abre diálogo de selección de cerramiento"""
        lblselected = self.builder.get_object('lblselected')
        resultado = self.dlg.run()
        # gtk.RESPONSE_ACCEPT vs gtk.RESPONSE_CANCEL
        if resultado == gtk.RESPONSE_ACCEPT:
            nombrecerr = lblselected.get_text()
            self.cerramiento = self.cerramientosDB[nombrecerr]
            self.actualiza()
            #XXX: Se podría retrasar si fuese necesario por rendimiento
            #XXX: Además no se redibujan bien si se está mostrando una pestaña
            #XXX: gráfica.
            self.actualizagraficas()
            self.actualizainforme()
            txt = "Seleccionado nuevo cerramiento activo: %s"
            self.statusbar.push(0, txt % nombrecerr)
        self.dlg.hide()

    def cerramientoactiva(self, tv):
        """Cambia cerramiento seleccionado en lista de cerramientos"""
        cerrtm, cerrtm_iter = tv.get_selection().get_selected()
        value = cerrtm[cerrtm_iter][0]
        lblselected = self.builder.get_object('lblselected')
        lblselected.set_text(value)

    # Retrollamadas de modificación de capas ----------------------------------
 
    def capacambiamaterial(self, cr, path, new_iter):
        """Cambio de material de la capa en el combo de la vista de capas
        
        cr - Comboboxcellrenderer con contenido modificado
        path - ruta del combo en el treeview
        new_iter - ruta del nuevo valor en el modelo del combo
        """
        capaindex = int(self.capasls[path][0])
        capaname, capae = self.cerramiento.capas[capaindex]
        newname = self.materialesls[new_iter][0].decode('utf-8')
        #TODO: Detecta si es material resistivo y pon espesor a None. Si no,
        #TODO: poner espesor por defecto.
#        newmaterial = materiales[newname]
#        capae = None if newmaterial.type == 'RESISTANCE' else float(capae)
        try:
            self.cerramiento.capas[capaindex] = (newname, float(capae))
            self.cerramientomodificado = True
            self.actualiza()
            self.graphsredrawpending = True
            txt = "Modificado material de capa %i" % capaindex
            self.statusbar.push(0, txt)
        except:
            self.cerramiento.capas[capaindex] = (capaname, float(capae))

    def capacambiaespesor(self, cr, path, new_text):
        """Cambio de espesor en la vista de capas
        
        cr - cellrenderertext que cambia
        path - ruta del cellrenderer en el treeview
        new_text - nuevo texto en la celda de texto
        """
        capaindex = int(self.capasls[path][0])
        capaname, capae = self.cerramiento.capas[capaindex]
        try:
            newe = float(new_text)
        except ValueError:
            return
        if newe != capae:
            self.cerramiento.capas[capaindex] = (capaname, newe)
            self.cerramientomodificado = True
            self.actualiza()
            self.graphsredrawpending = True
            txt = "Modificado espesor de capa %i a %f [m]"
            self.statusbar.push(0, txt % (capaindex, newe))

    def capaadd(self, btn):
        """Añade capa a cerramiento en vista de capas"""
        cerrtm, cerrtm_iter = self.capastv.get_selection().get_selected()
        if cerrtm_iter:
            capai = int(cerrtm[cerrtm_iter][0])
            #duplicamos propiedades de capa actual
            ncapatuple = self.cerramiento.capas[capai]
            self.cerramiento.capas.insert(capai + 1, ncapatuple)
            self.actualiza()
            self.graphsredrawpending = True
            self.capastv.set_cursor(capai + 1)
            self.statusbar.push(0, "Añadida capa %i" % (capai + 1))

    def caparemove(self, btn):
        """Elimina capa seleccionada de cerramiento en vista de capas"""
        cerrtm, cerrtm_iter = self.capastv.get_selection().get_selected()
        if cerrtm_iter:
            capai = int(cerrtm[cerrtm_iter][0])
            self.cerramiento.capas.pop(capai)
            self.actualiza()
            self.graphsredrawpending = True
            if capai == 0: capai = 1
            self.capastv.set_cursor(capai - 1)
            self.statusbar.push(0, "Eliminada capa %i" % capai)

    def capaup(self, btn):
        """Sube capa seleccionada de cerramiento en vista de capas"""
        cerrtm, cerrtm_iter = self.capastv.get_selection().get_selected()
        if cerrtm_iter:
            capai = int(cerrtm[cerrtm_iter][0])
            if capai > 0:
                cp = self.cerramiento.capas
                cp[capai - 1], cp[capai] = cp[capai], cp[capai - 1]
                self.actualiza()
                self.graphsredrawpending = True
                self.capastv.set_cursor(capai - 1)
                self.statusbar.push(0, "Desplazada capa %i" % capai)

    def capadown(self, btn):
        """Baja capa seleccionada de cerramiento en vista de capas"""
        cerrtm, cerrtm_iter = self.capastv.get_selection().get_selected()
        if cerrtm_iter:
            capai = int(cerrtm[cerrtm_iter][0])
            if capai + 1 < len(self.cerramiento.capas):
                cp = self.cerramiento.capas
                cp[capai + 1], cp[capai] = cp[capai], cp[capai + 1]
                self.actualiza()
                self.graphsredrawpending = True
                self.capastv.set_cursor(capai + 1)
                self.statusbar.push(0, "Desplazada capa %i" % capai)

    def capacambiarse(self, entry, event=None):
        """Toma valor de Rse al activar entry o cambiar el foco"""
        oldrse = self.cerramiento.Rse
        try:
            newrse = float(entry.props.text)
        except ValueError:
            entry.props.text = oldrse
            return
        if newrse != oldrse:
            self.cerramiento.Rse = newrse
            self.statusbar.push(0, "Nuevo Rse: %.2f" % newrse)
            self.cerramientomodificado = True
            self.graphsredrawpending = True
            self.actualiza()

    def capacambiarsi(self, entry, event=None):
        """Toma valor de Rsi al activar entry o cambiar el foco"""
        oldrsi = self.cerramiento.Rsi
        try:
            newrsi = float(entry.props.text)
        except ValueError:
            entry.props.text = oldrsi
            return
        if newrsi != oldrsi:
            self.cerramiento.Rsi = newrsi
            self.statusbar.push(0, "Nuevo Rsi: %.2f" % newrsi)
            self.cerramientomodificado = True
            self.graphsredrawpending = True
            self.actualiza()

    # Retrollamadas generales -------------------------------------------------

    def cambiahoja(self, notebook, page, pagenum):
        """Cambia hoja activa en la interfaz y actualiza gráficas si procede"""
        CREDITOS, CAPAS, GRAFICAPT, GRAFICAPV, INFORME = 0, 1, 2, 3, 4
        if pagenum == GRAFICAPT or pagenum == GRAFICAPV:
            if self.graphsredrawpending:
                self.actualizagraficas()
                self.graphsredrawpending = False
        elif pagenum == INFORME:
            if self.graphsredrawpending:
                self.actualizagraficas()
                self.graphsredrawpending = False
            self.actualizainforme()