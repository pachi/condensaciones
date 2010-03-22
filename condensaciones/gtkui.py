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

class Model(object):
    def __init__(self, cerramiento, climaext, climaint):
        """Constructor de modelo"""
        self.c = cerramiento
        self.climae = climaext
        self.climai = climaint

    def calcula(self):
        """Calcula resultados para usarlos en presentación"""
        ti, hri = self.climai.temp, self.climai.HR
        te, hre = self.climae.temp, self.climae.HR
        self.fRsi = comprobaciones.fRsi(self.c.U)
        self.fRsimin = comprobaciones.fRsimin(te, ti, hri)
        self.ccheck = comprobaciones.condensaciones(self.c, te, ti, hre, hri)
        self.cs = comprobaciones.condensas(self.c, te, ti, hri)
        self.ci = comprobaciones.condensai(self.c, te, ti, hre, hri)
        self.g, self.pcond = self.c.condensacion(te, ti, hre, hri)
        #self.g, self.pevap = self.c.evaporacion(te,ti,hre,hri,interfases=[2])
        self.totalg = 0.0 if not self.g else sum(self.g)

    def capasdata(self):
        """Devuelve iterador por capa con: i, (nombre, espesor, K, R, mu, S)"""
        # quitamos Rse, Rsi en c.R con c.R[1:-1]
        return enumerate(zip(self.c.nombres, self.c.espesores,
                             self.c.K, self.c.R[1:-1], self.c.mu, self.c.S))

class GtkCondensa(object):
    """Aplicación"""
    def __init__(self, cerramiento, climaext, climaint):
        """Inicialización de datos e interfaz
        
        cerramiento - Cerramiento
        climae - datos higrotérmicos del exterior
        climai - datos higrotérmicos del interior
        """
        self.model = Model(cerramiento, climaext, climaint)
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
        self.builder.connect_signals(self)
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

    def quit(self, w):
        gtk.main_quit()

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
        self.model.calcula()
        self.actualizacabecera()
        self.actualizapie()
        self.actualizacapas()

    def actualizacabecera(self):
        """Actualiza texto de cabecera"""
        model = self.model
        cnombre = self.builder.get_object('nombre_cerramiento')
        cdescripcion = self.builder.get_object('descripcion_cerramiento')
        csubtitulo1 = self.builder.get_object('csubtitulo1')
        csubtitulo2 = self.builder.get_object('csubtitulo2')
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
        cfondo = self.builder.get_object('cfondo')
        cfondo.modify_bg(gtk.STATE_NORMAL, state_color)

    def actualizapie(self):
        """Actualiza pie de ventana principal"""
        pie1 = self.builder.get_object('pie1')
        pie2 = self.builder.get_object('pie2')
        _K = 2592000.0 # segundos por mes
        pie1.props.label = "Total: %.2f [g/m²mes]" % (_K * self.model.totalg)
        txt = ("Cantidades condensadas: " +
               ", ".join(["%.2f" % (_K * x,) for x in self.model.g]))
        pie2.props.label = txt

    def actualizacapas(self):
        """Actualiza pestaña de capas con descripción, capas, Rse, Rsi"""
        rse = self.builder.get_object('Rsevalue')
        rsi = self.builder.get_object('Rsivalue')
        etotal = self.builder.get_object('espesortotal')
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
        tb = self.informetxtbuffer
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
            txt = "%.3f [m]\nR=%.3f [m²K/W]\nμ=%i\nS=%.3f [m]\n" % (e, R,
                                                                    mu, S)
            tb.insert_with_tags_by_name(tb.get_end_iter(), txt, 'datoscapa')
        txt = "Espesor total del cerramiento: %.3f m\n\n" % self.model.c.e
        tb.insert_with_tags_by_name(tb.get_end_iter(), txt, 'capa')
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
        localidad = self.builder.get_object('localidadentry')
        te = self.builder.get_object('tempextentry')
        hre = self.builder.get_object('hrextentry')
        ti = self.builder.get_object('tempintentry')
        hri = self.builder.get_object('hrintentry')
        
        localidad.props.text = 'Localidad'
        te.props.text = "%.2f" % self.model.climae.temp
        hre.props.text ="%.2f" % self.model.climae.HR
        ti.props.text = "%.2f" % self.model.climai.temp
        hri.props.text = "%.2f" % self.model.climai.HR
        resultado = self.adlg.run()
        # gtk.RESPONSE_ACCEPT vs gtk.RESPONSE_CANCEL
        if resultado == gtk.RESPONSE_ACCEPT:
            self.model.climae.temp = float(te.props.text)
            self.model.climae.HR = float(hre.props.text)
            self.model.climai.temp = float(ti.props.text)
            self.model.climai.HR = float(hri.props.text)
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
            nombrecerr = lblselected.props.label
            self.model.c = self.cerramientosDB[nombrecerr]
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
        lblselected = self.builder.get_object('lblselected')
        cerrtm, cerrtm_iter = tv.get_selection().get_selected()
        lblselected.props.label = cerrtm[cerrtm_iter][0]

    # Retrollamadas de modificación de capas ----------------------------------
 
    def capacambiamaterial(self, cr, path, new_iter):
        """Cambio de material de la capa en el combo de la vista de capas
        
        cr - Comboboxcellrenderer con contenido modificado
        path - ruta del combo en el treeview
        new_iter - ruta del nuevo valor en el modelo del combo
        """
        capaindex = int(self.capasls[path][0])
        capaname, capae = self.model.c.capas[capaindex]
        newname = self.materialesls[new_iter][0].decode('utf-8')
        #TODO: Detecta si es material resistivo y pon espesor a None. Si no,
        #TODO: poner espesor por defecto.
#        newmaterial = materiales[newname]
#        capae = None if newmaterial.type == 'RESISTANCE' else float(capae)
        try:
            self.model.c.capas[capaindex] = (newname, float(capae))
            self.cerramientomodificado = True
            self.actualiza()
            self.graphsredrawpending = True
            txt = "Modificado material de capa %i" % capaindex
            self.statusbar.push(0, txt)
        except:
            self.model.c.capas[capaindex] = (capaname, float(capae))

    def capacambiaespesor(self, cr, path, new_text):
        """Cambio de espesor en la vista de capas
        
        cr - cellrenderertext que cambia
        path - ruta del cellrenderer en el treeview
        new_text - nuevo texto en la celda de texto
        """
        capaindex = int(self.capasls[path][0])
        capaname, capae = self.model.c.capas[capaindex]
        try:
            newe = float(new_text)
        except ValueError:
            return
        if newe != capae:
            self.model.c.capas[capaindex] = (capaname, newe)
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
            ncapatuple = self.model.c.capas[capai]
            self.model.c.capas.insert(capai + 1, ncapatuple)
            self.actualiza()
            self.graphsredrawpending = True
            self.capastv.set_cursor(capai + 1)
            self.statusbar.push(0, "Añadida capa %i" % (capai + 1))

    def caparemove(self, btn):
        """Elimina capa seleccionada de cerramiento en vista de capas"""
        cerrtm, cerrtm_iter = self.capastv.get_selection().get_selected()
        if cerrtm_iter:
            capai = int(cerrtm[cerrtm_iter][0])
            self.model.c.capas.pop(capai)
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
                cp = self.model.c.capas
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
            if capai + 1 < len(self.model.c.capas):
                cp = self.model.c.capas
                cp[capai + 1], cp[capai] = cp[capai], cp[capai + 1]
                self.actualiza()
                self.graphsredrawpending = True
                self.capastv.set_cursor(capai + 1)
                self.statusbar.push(0, "Desplazada capa %i" % capai)

    def capacambiarse(self, entry, event=None):
        """Toma valor de Rse al activar entry o cambiar el foco"""
        oldrse = self.model.c.Rse
        try:
            newrse = float(entry.props.text)
        except ValueError:
            entry.props.text = oldrse
            return
        if newrse != oldrse:
            self.model.c.Rse = newrse
            self.statusbar.push(0, "Nuevo Rse: %.2f" % newrse)
            self.cerramientomodificado = True
            self.graphsredrawpending = True
            self.actualiza()

    def capacambiarsi(self, entry, event=None):
        """Toma valor de Rsi al activar entry o cambiar el foco"""
        oldrsi = self.model.c.Rsi
        try:
            newrsi = float(entry.props.text)
        except ValueError:
            entry.props.text = oldrsi
            return
        if newrsi != oldrsi:
            self.model.c.Rsi = newrsi
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