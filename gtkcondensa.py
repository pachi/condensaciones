#!/usr/bin/env python
#encoding: iso-8859-15

#TODO: Hacer test con los tres gr�ficos de condensa.py. Para ello hay
# que resolver el problema de usar subplot y show en cada figura.

import gtk
import os
import capas
from datos_ejemplo import climae, climai, murocapas
import comprobaciones
from condensawidgets import CCabecera, CPie
from ptcanvas import CPTCanvas, CPCanvas

class GtkCondensa(object):
    def __init__(self, muro, climae, climai):
        self.muro = muro
        self.climae = climae
        self.climai = climai

        builder = gtk.Builder()
        builder.add_from_file(os.path.join(os.getcwd(), 'condensa.ui'))
        # Controles ventana principal
        self.w = builder.get_object('window1')
        self.cabecera = builder.get_object('cabecera')
        self.grafico1 = builder.get_object('cptcanvas1')
        self.grafico2 = builder.get_object('cpcanvas1')
        self.textview = builder.get_object('ctextview1')
        self.pie = builder.get_object('pie')
        # Controles de di�logo de selecci�n de muros
        self.dlg = builder.get_object('dialogomuro')
        self.tvmuro = builder.get_object('tvmuro')
        self.lblselected = builder.get_object('lblselected')
        self.lsmuros = builder.get_object('liststoremuros')

        smap = {"on_window_destroy" : gtk.main_quit,
                "on_botonmuro_clicked": self.on_botonmuro_clicked,
                "on_tvmuro_cursor_changed" : self.on_tvmuro_cursor_changed,
                "on_btnacepta_clicked": self.on_btnacepta_clicked,
                "on_btncancela_clicked": self.on_btncancela_clicked}
        builder.connect_signals(smap)
        self.actualiza()
        
    def main(self):
        self.w.show_all()
        gtk.main()
        
    def actualiza(self):
        fRsi = comprobaciones.calculafRsi(self.muro.U)
        fRsimin = comprobaciones.calculafRsimin(self.climae.temp, self.climai.temp, self.climai.HR)
        g, puntos_condensacion = self.muro.cantidadcondensacion(self.climae.temp, self.climai.temp, self.climae.HR, self.climai.HR)
        #g, puntos_evaporacion = self.muro.cantidadevaporacion(temp_ext, temp_int, HR_ext, HR_int, interfases=[2])
        ccheck = comprobaciones.compruebacondensaciones(self.muro, self.climae.temp, self.climai.temp, self.climae.HR, self.climai.HR)
        self.cabecera._settitle(self.muro.nombre)
        self.cabecera._setsubtitle1(self.muro.U, fRsi, fRsimin)
        self.cabecera._setsubtitle2(self.climai.temp, self.climai.HR, self.climae.temp, self.climae.HR)
        self.cabecera.ok = ccheck
        self.grafico1.dibuja(self.muro, self.climae, self.climai)
        self.grafico2.dibuja(self.muro, self.climae, self.climai)
        self.textview.update(self.muro)
        gtotal = 2592000.0 * sum(g)
        self.pie._settitle1(gtotal)
        self.pie._settitle2(g)
        
    # -- Retrollamadas ventana principal --
    def on_botonmuro_clicked(self, widget):
#         datosmuro = [("M1",), ("M2",), ("M3",)]
#        for muro in datosmuro:
#            self.lsmuros.append(muro)
        resultado = self.dlg.run()
#        self.nombremuro = self.lblselected.get_text()
        if resultado == gtk.RESPONSE_ACCEPT:
            print 'Cambiado'
        elif resultado == gtk.RESPONSE_CANCEL:
            print 'Sin cambios'
        self.dlg.hide()

    # -- Retrollamadas di�logo muros --
    def on_tvmuro_cursor_changed(self, tv):
        _murotm, _murotm_iter = self.tvmuro.get_selection().get_selected()
        value = _murotm.get_value(_murotm_iter, 0)
        self.lblselected.set_text(value)

    def on_btnacepta_clicked(self, btn):
        self.dlg.response(gtk.RESPONSE_ACCEPT)
#        print 1

    def on_btncancela_clicked(self, btn):
        self.dlg.response(gtk.RESPONSE_CANCEL)
#        print 2

muro = capas.Cerramiento("Cerramiento tipo", murocapas, 0.04, 0.13)
app = GtkCondensa(muro, climae, climai)
app.main()