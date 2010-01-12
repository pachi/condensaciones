#!/usr/bin/env python
#encoding: utf-8

import os
import gtk
import util
import capas
import comprobaciones
from condensawidgets import CTextView
from ptcanvas import CPTCanvas, CPCanvas

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
        self.textview = builder.get_object('ctextview1')
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
            # XXX: No se puede cargar el muro porque la segunda columna debería ser
            # un PyGobject, y no un Gobject nada más... (glade no permite seleccionar ese tipo)
            #self.lsmuros.append(muro)

    def actualiza(self):
        self.actualizacabecera()
        self.actualizagraficas()
        self.actualizatexto()
        self.actualizapie()

    def actualizacabecera(self):
        fRsi = comprobaciones.calculafRsi(self.muro.U)
        fRsimin = comprobaciones.calculafRsimin(self.climae.temp, self.climai.temp, self.climai.HR)
        ccheck = comprobaciones.compruebacondensaciones(self.muro, self.climae.temp, self.climai.temp, self.climae.HR, self.climai.HR)
        _text = u'<span size="x-large">%s</span>' % self.muro.nombre
        self.ctitulo.set_markup(_text)
        _text = u'U = %.2f W/m²K, f<sub>Rsi</sub> = %.2f, f<sub>Rsi,min</sub> = %.2f' % (self.muro.U, fRsi, fRsimin)
        self.csubtitulo1.set_markup(_text)
        _text = u'T<sub>int</sub> = %.2f°C, HR<sub>int</sub> = %.1f%%, T<sub>ext</sub> = %.2f°C, HR<sub>ext</sub> = %.1f%%' % (self.climai.temp, self.climai.HR, self.climae.temp, self.climae.HR)
        self.csubtitulo2.set_markup(_text)
        self.cfondo.modify_bg(gtk.STATE_NORMAL, ccheck and COLOR_OK or COLOR_BAD)

    def actualizagraficas(self):
        self.grafico1.dibuja(self.muro, self.climae, self.climai)
        self.grafico2.dibuja(self.muro, self.climae, self.climai)
    
    def actualizatexto(self):
        self.textview.update(self.muro)

    def actualizapie(self):
        g, puntos_condensacion = self.muro.cantidadcondensacion(self.climae.temp, self.climai.temp, self.climae.HR, self.climai.HR)
        #g, puntos_evaporacion = self.muro.cantidadevaporacion(temp_ext, temp_int, HR_ext, HR_int, interfases=[2])
        if not g:
            g = 0.0
        gtotal = 2592000.0 * sum(g)
        _text = u"Total: %.2f [g/m²mes]" % gtotal
        self.pie1.set_markup(_text)
        _text = u"Cantidades condensadas: " + u", ".join(["%.2f" % (2592000.0 * x,) for x in g])
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