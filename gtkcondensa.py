#!/usr/bin/env python
#encoding: iso-8859-15

#TODO: Hacer test con los tres gráficos de condensa.py. Para ello hay
# que resolver el problema de usar subplot y show en cada figura.

import gtk
import os
import capas
from datos_ejemplo import climae, climai, murocapas
import comprobaciones
from grafica import PTCanvas

muro = capas.Cerramiento(murocapas, 0.04, 0.13)
f_Rsi = comprobaciones.calculafRsi(muro.U)
f_Rsimin = comprobaciones.calculafRsimin(climae.temp, climai.temp, climai.HR)
g, puntos_condensacion = muro.cantidadcondensacion(climae.temp, climai.temp, climae.HR, climai.HR)
#g, puntos_evaporacion = muro.cantidadevaporacion(temp_ext, temp_int, HR_ext, HR_int, interfases=[2])
ccheck = (comprobaciones.compruebacondensaciones(muro, climae.temp, climai.temp, climae.HR, climai.HR)
          and "#AACCAA" or "#CCAAAA")
basecolor = gtk.gdk.color_parse(ccheck)

builder = gtk.Builder()
builder.add_from_file(os.path.join(os.getcwd(), 'condensa.ui'))
builder.connect_signals({ "on_window_destroy" : gtk.main_quit })
w = builder.get_object('window1')
eb = builder.get_object('eventbox1')
title = builder.get_object('titulo')
subtitulo1 = builder.get_object('subtitulo1')
subtitulo2 = builder.get_object('subtitulo2')
pie1 = builder.get_object('pie1')
pie2 = builder.get_object('pie2')

eb.modify_bg(gtk.STATE_NORMAL, basecolor)
title.set_markup('<span size="x-large">Cerramiento tipo</span>')
subtitulo1.set_markup(u'U = %.2f W/m²K, f<sub>Rsi</sub> = %.2f, f<sub>Rsi,min</sub> = %.2f' % (muro.U, f_Rsi, f_Rsimin))
subtitulo2.set_markup(u'T<sub>int</sub> = %.2f°C, HR<sub>int</sub> = %.1f%%, T<sub>ext</sub> = %.2f°C, HR<sub>ext</sub> = %.1f%%' % (climai.temp, climai.HR, climae.temp, climae.HR))

canvas = PTCanvas()
canvas.dibuja("Cerramiento tipo", muro, climae, climai)
cnv = builder.get_object('comodin')
cnvparent = cnv.get_parent()
cnv.destroy()
cnvparent.add(canvas)
cnvparent.reorder_child(canvas, 1)

pie1.set_markup(u"Total: %.2f [g/m²mes]" % (2592000.0 * sum(g)))
pie2.set_markup(u"Cantidades condensadas: " + u", ".join(["%.2f" % (2592000.0 * x,) for x in g]))
w.show_all()
gtk.main()
