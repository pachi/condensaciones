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
"""Interfaz de usuario de Condensaciones en GTK+"""

import webbrowser, datetime

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GObject, Pango

from . import appmodel, htmlreport
from .util import config
from .widgets import CPTCanvas, CCCanvas, CondensaIconFactory

class GtkCondensa(object):
    """Aplicación"""
    def __init__(self):
        """Inicialización de datos e interfaz"""
        self.cfg = config
        self.model = appmodel.Model()
        self.ui = Gtk.Builder()
        self.ui.graficacondensaciones = CCCanvas(self.model) # Histograma de condensaciones
        self.ui.add_from_file(config.appresource('condensa.ui'))
        self.capasls = self.ui.get_object('capas_liststore')
        self.capastv = self.ui.get_object('capas_treeview')
        self.ui.connect_signals(self)
        # Elementos de la UI que no se pueden generar en Glade ----------------
        # Conecta modelos a gráficas
        self.ui.get_object('prestemp_canvas').model = self.model
        self.ui.get_object('cruler').model = self.model
        # Marcas de texto para estilos en textbuffer --------------------------
        tb = self.ui.get_object('informe_txtbuffer')
        # Iconos de aplicación y de botones de herramientas -------------------
        self.icons = CondensaIconFactory(self)
        self.ui.get_object('cerramselectbtn').set_stock_id('condensa-cerramientos')
        self.ui.get_object('climaselectbtn').set_stock_id('condensa-clima')
        # Carga datos de materiales, cerramientos y clima
        self.materialesls = self.ui.get_object('materiales_liststore')
        for material in self.model.c.matDB.nombres:
            self.materialesls.append((material,))
        self.cerramientotv = self.ui.get_object('cerramientotv')
        self.cerramientosls = self.ui.get_object('cerramientos_liststore')
        for nombre in self.model.cerramientosDB.nombres:
            descripcion = self.model.cerramientosDB[nombre].descripcion
            self.cerramientosls.append((nombre, descripcion))
        self.localidadesls = self.ui.get_object('localidadesls')
        self.localidadesls.clear()
        for nombrelocalidad in self.model.climas:
            self.localidadesls.append((nombrelocalidad,))
        self.ui.get_object('localidadcb').props.active = 0
        n = len(self.model.c.matDB.nombres)
        m = len(self.model.cerramientosDB.nombres)
        r = len(self.model.climas)
        msg = "Cargados %i materiales, %i cerramientos, %i climas"  % (n, m, r)
        self.actualiza(msg)

    #{ Funciones generales de aplicación

    def quit(self, w, *args):
        """Salir de la aplicación"""
        Gtk.main_quit()

    def main(self):
        """Arranca la aplicación"""
        self.ui.get_object('window').show_all()
        Gtk.main()

    #{ Funciones de actualización de datos en interfaz

    def actualiza(self, txt=None):
        """Actualiza cabecera, gráficas, texto y pie de datos"""
        if txt:
            self.ui.get_object('statusbar').push(0, txt)
        modifiedmark = "*" if self.model.modificado else ""
        txt = "Condensaciones - %s%s" % (self.model.c.nombre, modifiedmark)
        self.ui.get_object('window').set_title(txt)
        self.actualizacabecera()
        self.actualizapie()
        self.actualizacapas()
        GObject.idle_add(self.actualizagraficas)
        if self.ui.get_object('notebook').props.page == 3: #INFORME
            # Debemos asegurarnos de actualizar las gráficas antes del informe
            while Gtk.events_pending():
                Gtk.main_iteration()
            self.actualizainforme()

    def actualizacabecera(self):
        """Actualiza texto de cabecera"""
        m, ui = self.model, self.ui
        ui.get_object('nombre_cerramiento').props.label = m.c.nombre
        ui.get_object('descripcion_cerramiento').props.label = m.c.descripcion
        txt_t1 = (u"<span color='#0000'>U = %.2f W/m²K, f<sub>Rsi</sub> ="
                  u" %.2f, f<sub>Rsi,min</sub> = %.2f</span>"
                  ) % (m.c.U, m.fRsi, m.fRsimin)
        ui.get_object('csubtitulo1').props.label = txt_t1
        txt_t2 = (u"<span color='#0000'>%s: T<sub>ext</sub> = %.2f°C, HR<sub>ext</sub> = %.1f%%, "
                  u"%s: T<sub>int</sub> = %.2f°C, HR<sub>int</sub> = %.1f%%</span>"
                  ) % (m.ambienteexterior, m.climae.temp, m.climae.HR,
                       m.ambienteinterior, m.climai.temp, m.climai.HR)
        ui.get_object('csubtitulo2').props.label = txt_t2

        # Ver estilos para hacer esto
        # https://github.com/GNOME/pitivi/blob/master/pitivi/timeline/elements.py
        ci, cs = m.ci, m.cs
        if ci and cs:
            # El cerramiento condensa en las condiciones ambientales actuales
            state_color = "#CCAAAA" # rojo COLOR_BAD
        elif ci or cs:
            # El cerramiento condensa en las condiciones CTE (enero para
            # cond. superficiales y todos los meses para cond. intersticiales
            state_color = "#FFDD77" # naranja COLOR_SEE
        else:
            state_color = "#AACCAA" # verde COLOR_OK
        ui.get_object('cfondo').modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse(state_color))

    def actualizapie(self):
        """Actualiza pie de ventana principal"""
        m, ui = self.model, self.ui
        txt = (u"Condensación en interfases (%s): " % m.ambienteexterior +
               u", ".join([u"%.2f (%i)" % (x, i) for i, x in m.glist[m.imes]]))
        ui.get_object('pie').props.label = txt

    def actualizacapas(self):
        """Actualiza pestaña de capas con descripción, capas, Rse, Rsi"""
        m, ui = self.model, self.ui
        ui.get_object('Rsevalue').props.text = "%.2f" % float(m.c.Rse)
        ui.get_object('Rsivalue').props. text = "%.2f" % float(m.c.Rsi)
        ui.get_object('espesortotal').props.label = "%.3f" % m.c.e
        self.capasls.clear()
        for i, (nombre, e, K, R, mu, S, color) in m.capasdata():
            r, g, b = color
            colorstr = "rgba(%i,%i,%i,0.25)" % (int(255*r), int(255*g), int(255*b))
            d = ("%i" % i, nombre, "%.3f" % e,
                 "-" if not K else "%.4f" % K,
                 "%.4f" % R, "%i" % mu, "%.3f" % S, colorstr)
            self.capasls.append(d)

    def actualizagraficas(self):
        """Redibuja gráficos con nuevos datos"""
        self.ui.get_object('cruler').queue_draw()
        self.ui.get_object('prestemp_canvas').dibuja()
        self.ui.graficacondensaciones.dibuja()

    #{ Pestaña de informe

    def actualizainforme(self):
        """Actualiza texto descripción de cerramiento en ventana principal"""
        m, ui = self.model, self.ui
        tb = ui.get_object('informe_txtbuffer')
        presionespb = ui.get_object('prestemp_canvas').pixbuf(600)
        condensacionespb = ui.graficacondensaciones.pixbuf(600)
        
        #etiquetas
        titulo = ui.get_object('tag_titulo')
        titulo2 = ui.get_object('tag_titulo2')
        subtitulo = ui.get_object('tag_subtitulo')
        capa = ui.get_object('tag_capa')
        datoscapa = ui.get_object('tag_datoscapa')
        resultados = ui.get_object('tag_resultados')
        nota = ui.get_object('tag_nota')

        def addtxt(txt, tag=None):
            enditer = tb.get_end_iter()
            if tag:
                tb.insert_with_tags(enditer, txt, tag)
            else:
                tb.insert(enditer, txt)

        # Reset
        tb.props.text = ""
        # Denominación cerramiento
        addtxt(u"%s\n" % m.c.nombre, titulo)
        addtxt(u"%s\n\n" % m.c.descripcion, titulo2)
        # Condiciones ambientales
        addtxt(u"Condiciones de cálculo\n", subtitulo)
        addtxt(u"Ambiente exterior (gráficas): %s\n" % m.ambienteexterior, capa)
        addtxt((u"Temperatura exterior: %.1f ºC\n"
                u"Humedad relativa exterior: %.1f %%\n\n")
               % (m.climae.temp, m.climae.HR), datoscapa)
        addtxt(u"Ambiente interior (gráficas): %s\n" % m.ambienteinterior, capa)
        addtxt((u"Temperatura interior: %.1f ºC\n"
                u"Humedad relativa interior: %.1f %%\n\n")
               % (m.climai.temp, m.climai.HR), datoscapa)
        addtxt((u"Resistencia superficial exterior: %.2f m²K/W\n"
                u"Resistencia superficial exterior: %.2f m²K/W\n\n")
               % (m.c.Rse, m.c.Rsi), capa)
        #
        addtxt((u"Condiciones de cálculo para la comprobación de condensaciones"
                u" superficiales\n"), capa)
        addtxt((u"Exterior - T: %.1f ºC, HR: %.1f %%\n"
                u"Interior - T: %.1f ºC, HR: %.1f %%\n\n")
               % (m.climaslist[0].temp, m.climaslist[0].HR, 20.0, m.climai.HR), datoscapa)
        #
        addtxt((u"Condiciones de cálculo para la comprobación de condensaciones"
                u" intersticiales\n"), capa)
        tempextlist = u", ".join(u"%.1f" % clima.temp for clima in m.climaslist)
        hrextlist = u", ".join(u"%.1f" % clima.HR for clima in m.climaslist)
        addtxt((u"Exterior - \n\tT [ºC]: %s\n\tHR [%%]: %s\n"
                u"Interior - T [ºC]: %.1f, HR [%%]: %.1f\n\n")
               % (tempextlist, hrextlist, 20.0, m.climai.HR), datoscapa)
        # Cerramiento
        addtxt(u"Descripción del cerramiento\n", subtitulo)
        for i, (nombre, e, K, R, mu, S, color) in m.capasdata():
            addtxt(u"%i - %s:\n" % (i, nombre), capa)
            addtxt((u"%.3f [m]\nR=%.3f [m²K/W]\n"
                    u"μ=%i\nS=%.3f [m]\n" % (e, R, mu, S)), datoscapa)
        addtxt(u"Espesor total del cerramiento: %.3f m\n\n" % m.c.e, capa)
        # Gráficas
        addtxt(u"Gráficas\n", subtitulo)
        tb.insert_pixbuf(tb.get_end_iter(), presionespb)
        addtxt(u"\n")
        tb.insert_pixbuf(tb.get_end_iter(), condensacionespb)
        addtxt(u"\n")
        # Resultados
        addtxt(u"Resultados\n", subtitulo)
        addtxt((u"R_total: %.3f [m²K/W]\nS_total = %.3f [m]\n"
                u"Transmitancia térmica total: U = %.3f [W/m²K]\n"
                u"f_Rsi = %.2f\nf_Rsimin = %.2f\n\n")
               % (m.c.R_total, m.c.S_total, m.c.U, m.fRsi, m.fRsimin), resultados)
        # Condensaciones
        cs = u"Sí" if m.cs else u"No"
        ci = u"Sí" if m.ci else u"No"
        addtxt((u"\n¿Existen condensaciones superficiales?: %s\n"
                u"¿Existen condensaciones intersticiales?: %s\n") % (cs, ci), resultados)
        if m.ci:
            meses = u", ".join(u"%i" % i for i, value in enumerate(m.glist) if value)
            addtxt((u"\nPeriodos con condensaciones intersticiales: %s\n") % meses, resultados)
        # Nota copyright
        today = datetime.datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
        addtxt((u"\n\nInforme generado por 'Condensa' "
                u"(www.rvburke.com/condensaciones.html) el %s\n\n"
                u"'Condensa' es software libre que se distribuye bajo licencia "
                u"GPLv2 o posterior.\n"
                u"Copyright (c) 2009-2010 Rafael Villar Burke\n") % today, nota)

    def openhtmlreport(self, widget):
        htmlreport.createreport(self.ui, self.model)
        report = 'file://' + config.userresource('report', 'report.html')
        webbrowser.open(report)

    #{ Retrollamadas del diálogo de selección de ambientes

    def ambienteselecciona(self, widget):
        """Abre diálogo de selección de ambientes"""
        m, ui = self.model, self.ui
        adialog = ui.get_object('ambiente_dlg')
        te = ui.get_object('tempextentry')
        hre = ui.get_object('hrextentry')
        ti = ui.get_object('tempintentry')
        hri = ui.get_object('hrintentry')
        te.props.text = "%.2f" % m.climae.temp
        hre.props.text ="%.2f" % m.climae.HR
        ti.props.text = "%.2f" % m.climai.temp
        hri.props.text = "%.2f" % m.climai.HR
        resultado = adialog.run()
        if resultado == Gtk.ResponseType.ACCEPT:
            if not ui.get_object('localidadcb').props.sensitive:
                m.climae = float(te.props.text), float(hre.props.text)
            m.climai = float(ti.props.text), float(hri.props.text)
            msg = "Seleccionadas nuevas condiciones ambientales"
            self.actualiza(msg)
        adialog.hide()

    def _setclimaext(self):
        m, ui = self.model, self.ui
        m.localidad = m.climas[ui.get_object('localidadcb').props.active]
        m.imes = ui.get_object('mescb').props.active
        ui.get_object('mescb').props.active = m.imes # puede haber menos climas
        ui.get_object('tempextentry').props.text = "%.f" % m.climae.temp
        ui.get_object('hrextentry').props.text = "%.f" % m.climae.HR

    def meschanged(self, widget):
        """Cambio en el combo de meses"""
        self._setclimaext()

    def localidadchanged(self, combo):
        """Cambio en el combo de localidades"""
        if combo.props.sensitive and combo.props.active != -1:
            self._setclimaext()

    def climamanualtoggle(self, widget):
        """Cambio en casilla de selección de entrada manual de datos
        climáticos
        """
        m, ui = self.model, self.ui
        active = widget.props.active
        ui.get_object('localidadcb').props.sensitive = not active
        ui.get_object('mescb').props.sensitive = not active
        ui.get_object('tempextentry').props.sensitive = active
        ui.get_object('hrextentry').props.sensitive = active
        if not active:
            self._setclimaext()
        else:
            m.localidad = None
            ui.get_object('tempextentry').props.text = "%.f" % m.climae.temp
            ui.get_object('hrextentry').props.text = "%.f" % m.climae.HR

    #{ Retrollamadas del diálogo de selección de cerramientos

    def cerramientoselecciona(self, widget):
        """Abre diálogo de selección de cerramiento"""
        m, ui = self.model, self.ui
        if not ui.get_object('lblselected').props.label in m.cerramientosDB.nombres:
            self.cerramientotv.set_cursor(0)
        resultado = ui.get_object('cerramiento_dlg').run()
        # Gtk.ResponseType.ACCEPT vs Gtk.ResponseType.CANCEL
        if resultado == Gtk.ResponseType.ACCEPT:
            nombrecerr = ui.get_object('lblselected').props.label
            m.set_cerramiento(nombrecerr)
            msg = "Seleccionado nuevo cerramiento activo: %s" % nombrecerr
            self.actualiza(msg)
        ui.get_object('cerramiento_dlg').hide()

    def cerramientoactiva(self, tv):
        """Cambia cerramiento seleccionado en lista de cerramientos"""
        cerrtm, cerrtm_iter = tv.get_selection().get_selected()
        if cerrtm_iter:
            self.ui.get_object('lblselected').props.label = cerrtm[cerrtm_iter][0]

    def cerramientonombreeditado(self, cr, path, newtext):
        """Edita nombre de cerramiento"""
        oldname = self.cerramientosls[path][0]
        self.cerramientosls[path][0] = newtext
        self.model.cerramientocambianombre(oldname, newtext)

    def cerramientodescripcioneditada(self, cr, path, newtext):
        """Edita descripción de cerramiento"""
        cerrname = self.cerramientosls[path][0]
        self.cerramientosls[path][1] = newtext
        self.model.cerramientocambiadescripcion(cerrname, newtext)

    def cerramientoadd(self, widget):
        """Añade cerramiento de la lista de cerramientos"""
        cerrtm, cerrtm_iter = self.cerramientotv.get_selection().get_selected()
        if cerrtm_iter:
            cerri = int(cerrtm.get_path(cerrtm_iter)[0])
            newcerr = self.model.cerramientoadd(cerri)
            cerrtm.insert(cerri + 1, row=(newcerr.nombre, newcerr.descripcion))
            msg = "Añadido cerramiento nuevo: %s" % newcerr.nombre
            self.ui.get_object('statusbar').push(0, msg)
            self.cerramientotv.set_cursor(cerri + 1)

    def cerramientoremove(self, widget):
        """Elimina cerramiento de la lista de cerramientos
        
        Al menos debe quedar un cerramiento"""
        if len(self.model.cerramientosDB.nombres) == 1:
            self.ui.get_object('statusbar').push(0, "Debe existir al menos un cerramiento")
        else:
            cerrtm, cerrtm_iter = self.cerramientotv.get_selection().get_selected()
            if cerrtm_iter:
                cerri = int(cerrtm.get_path(cerrtm_iter)[0])
                self.model.cerramientoremove(cerri)
                cerrtm.remove(cerrtm_iter)
                self.ui.get_object('statusbar').push(0, "Eliminado cerramiento")
                if cerri == 0: cerri = 1
                self.cerramientotv.set_cursor(cerri - 1)

    def cerramientoup(self, widget):
        """Sube cerramiento en lista de cerramientos"""
        cerrtm, cerrtm_iter = self.cerramientotv.get_selection().get_selected()
        if cerrtm_iter:
            cerri = int(cerrtm.get_path(cerrtm_iter)[0])
            if cerri == 0:
                return
            self.model.cerramientoswap(cerri - 1, cerri)
            previter = cerrtm.get_iter(cerri - 1)
            cerrtm.swap(cerrtm_iter, previter)

    def cerramientodown(self, widget):
        """Baja cerramiento en lista de cerramientos"""
        cerrtm, cerrtm_iter = self.cerramientotv.get_selection().get_selected()
        if cerrtm_iter:
            cerri = int(cerrtm.get_path(cerrtm_iter)[0])
            if cerri == len(self.model.cerramientosDB.nombres) - 1:
                return
            self.model.cerramientoswap(cerri + 1, cerri)
            nextiter = cerrtm.get_iter(cerri + 1)
            cerrtm.swap(cerrtm_iter, nextiter)

    def cerramientoguardar(self, widget):
        """Guarda lista de cerramientos en disco"""
        self.model.cerramientossave()

    #{ Retrollamadas de modificación de capas en pestaña de capas

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
            if capai == 0:
                return
            self.model.capaswap(capai - 1, capai)
            self.actualiza("Desplazada capa %i" % capai)
            self.capastv.set_cursor(capai - 1)

    def capadown(self, btn):
        """Baja capa seleccionada de cerramiento en vista de capas"""
        cerrtm, cerrtm_iter = self.capastv.get_selection().get_selected()
        if cerrtm_iter:
            capai = int(cerrtm[cerrtm_iter][0])
            if capai == len(self.model.c.capas) - 1:
                return
            self.model.capaswap(capai + 1, capai)
            self.actualiza("Desplazada capa %i" % capai)
            self.capastv.set_cursor(capai + 1)

    def capacambiarse(self, entry, event=None):
        """Toma valor de Rse al activar entry o cambiar el foco"""
        try:
            newrse = float(entry.props.text)
            if newrse != self.model.c.Rse:
                self.model.set_Rse(newrse)
                self.actualiza("Nuevo Rse: %.2f" % newrse)
        except ValueError:
            entry.props.text = self.model.c.Rse

    def capacambiarsi(self, entry, event=None):
        """Toma valor de Rsi al activar entry o cambiar el foco"""
        try:
            newrsi = float(entry.props.text)
            if newrsi != self.model.c.Rsi:
                self.model.set_Rsi(newrsi)
                self.actualiza("Nuevo Rsi: %.2f" % newrsi)
        except ValueError:
            entry.props.text = self.model.c.Rsi

    #{ Retrollamadas generales

    def cambiahoja(self, notebook, page, pagenum):
        """Cambia hoja activa en la interfaz y actualiza informe si procede"""
        if pagenum == 3: #INFORME
            self.actualizainforme()
