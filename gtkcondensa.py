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

muro = capas.Cerramiento("Cerramiento tipo", murocapas, 0.04, 0.13)
fRsi = comprobaciones.calculafRsi(muro.U)
fRsimin = comprobaciones.calculafRsimin(climae.temp, climai.temp, climai.HR)
g, puntos_condensacion = muro.cantidadcondensacion(climae.temp, climai.temp, climae.HR, climai.HR)
#g, puntos_evaporacion = muro.cantidadevaporacion(temp_ext, temp_int, HR_ext, HR_int, interfases=[2])
ccheck = comprobaciones.compruebacondensaciones(muro, climae.temp, climai.temp, climae.HR, climai.HR)

builder = gtk.Builder()
builder.add_from_file(os.path.join(os.getcwd(), 'condensa.ui'))
builder.connect_signals({ "on_window_destroy" : gtk.main_quit })
w = builder.get_object('window1')
cabecera = builder.get_object('cabecera')
grafico1 = builder.get_object('cptcanvas1')
grafico2 = builder.get_object('cpcanvas1')
textview = builder.get_object('ctextview1')
pie = builder.get_object('pie')

cabecera._settitle(muro.nombre)
cabecera._setsubtitle1(muro.U, fRsi, fRsimin)
cabecera._setsubtitle2(climai.temp, climai.HR, climae.temp, climae.HR)
cabecera.ok = ccheck

grafico1.dibuja("Cerramiento tipo", muro, climae, climai)
grafico2.dibuja("Cerramiento tipo", muro, climae, climai)
textview.update(muro)

gtotal = 2592000.0 * sum(g)
pie._settitle1(gtotal)
pie._settitle2(g)

w.show_all()
gtk.main()
