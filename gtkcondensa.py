#!/usr/bin/env python
#encoding: iso-8859-15

#TODO: Hacer test con los tres gráficos de condensa.py. Para ello hay
# que resolver el problema de usar subplot y show en cada figura.

import gtk
import os
import capas
from datos_ejemplo import climae, climai, murocapas
import comprobaciones
from condensawidgets import CCabecera, CPie
from ptcanvas import CPTCanvas, CPCanvas

class Gtkcondensa(object):
    def __init__(self, muro, climae, climai):
        self.muro = muro
        self.climae = climae
        self.climai = climai
        builder = gtk.Builder()
        builder.add_from_file(os.path.join(os.getcwd(), 'condensa.ui'))
        self.w = builder.get_object('window1')
        self.cabecera = builder.get_object('cabecera')
        self.grafico1 = builder.get_object('cptcanvas1')
        self.grafico2 = builder.get_object('cpcanvas1')
        self.textview = builder.get_object('ctextview1')
        self.pie = builder.get_object('pie')
        self.dialog = builder.get_object('dialogomuro')
        smap = {"on_window_destroy" : gtk.main_quit,
                "on_botonmuro_clicked": self.on_botonmuro_clicked}
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
        
    def on_botonmuro_clicked(self, widget):
        self.dialog.run()

muro = capas.Cerramiento("Cerramiento tipo", murocapas, 0.04, 0.13)
app = Gtkcondensa(muro, climae, climai)
app.main()