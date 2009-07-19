#!/usr/bin/env python
#encoding: iso-8859-15

import os
import gtk
import pango
import ptcanvas

class CCabecera(gtk.EventBox):
    __gtype_name__ = 'CCabecera'
    COLOR_TRUE = gtk.gdk.color_parse("#AACCAA")
    COLOR_FALSE = gtk.gdk.color_parse("#CCAAAA")
    def __init__(self):
        self.ok = True
        self._vbox = gtk.VBox()
        self._titulo = gtk.Label()
        self._subtitulo1 = gtk.Label()
        self._subtitulo2 = gtk.Label()
        self._settitle()
        self._setsubtitle1()
        self._setsubtitle2()
        gtk.EventBox.__init__(self)
        self._vbox.pack_start(self._titulo)
        self._vbox.pack_start(self._subtitulo1)
        self._vbox.pack_start(self._subtitulo2)
        self._vbox.show_all()
        self.add(self._vbox)
    def do_expose_event(self, event):
        retval = gtk.EventBox.do_expose_event(self, event)
        self.modify_bg(gtk.STATE_NORMAL, self.ok and self.COLOR_TRUE or self.COLOR_FALSE)
        return retval
    def _settitle(self, title="Cerramiento tipo"):
        self._title = title
        _text = u'<span size="x-large">%s</span>' % (self._title,)
        self._titulo.set_markup(_text)
    def _setsubtitle1(self, U=1.0, fRsi=0.80, fRsimin=0.90):
        self._U = U
        self._f_Rsi = fRsi
        self._f_Rsimin = fRsimin
        _text = u'U = %.2f W/m²K, f<sub>Rsi</sub> = %.2f, f<sub>Rsi,min</sub> = %.2f' % (self._U, self._f_Rsi, self._f_Rsimin)
        self._subtitulo1.set_markup(_text)
    def _setsubtitle2(self, tempi=20.0, HRi=60.0, tempe=10.0, HRe=30.0):
        self._tempi = tempi
        self._HRi = HRi
        self._tempe = tempe
        self._HRe = HRe
        _text = u'T<sub>int</sub> = %.2f°C, HR<sub>int</sub> = %.1f%%, T<sub>ext</sub> = %.2f°C, HR<sub>ext</sub> = %.1f%%' % (self._tempi, self._HRi, self._tempe, self._HRe)
        self._subtitulo2.set_markup(_text)

class CPie(gtk.VBox):
    __gtype_name__ = 'CPie'
    def __init__(self):
        self._subtitulo1 = gtk.Label()
        self._subtitulo2 = gtk.Label()
        self._settitle1()
        self._settitle2()
        gtk.VBox.__init__(self)
        self.pack_start(self._subtitulo1)
        self.pack_start(self._subtitulo2)
        self.show_all()
    def _settitle1(self, gtotal=0.0):
        self.gtotal = gtotal
        #_text = u"Total: %.2f [g/m²mes]" % (2592000.0 * sum(g))
        _text = u"Total: %.2f [g/m²mes]" % self.gtotal
        self._subtitulo1.set_markup(_text)
    def _settitle2(self, gcondensadas=None):
        if gcondensadas is None:
            self.gcondensadas = [0]
        else:
            self.gcondensadas = gcondensadas
        _text = u"Cantidades condensadas: " + u", ".join(["%.2f" % (2592000.0 * x,) for x in self.gcondensadas])
        self._subtitulo2.set_markup(_text)

class CTextView(gtk.ScrolledWindow):
    "Control para mostrar datos de Cerramientos en formato Texto"
    __gtype_name__ = 'CTextView'
    def __init__(self):
        gtk.ScrolledWindow.__init__(self)
        self.tv = gtk.TextView()
        self.tv.set_wrap_mode(gtk.WRAP_WORD)
        self.buffer = self.tv.get_buffer()
        self.add(self.tv)
        self.init_tags()

    def init_tags(self):
        self.buffer.create_tag("titulo", weight=pango.WEIGHT_BOLD, scale=pango.SCALE_X_LARGE)
        tag = self.buffer.create_tag("capa", weight=pango.WEIGHT_BOLD)
        self.buffer.create_tag("datoscapa", style=pango.STYLE_ITALIC, indent=30)
        self.buffer.create_tag("resultados", foreground='blue', scale=pango.SCALE_LARGE)

    def update(self, muro):
        "Mostrar texto"
        text = "%s\n\n" % muro.nombre
        iter = self.buffer.get_start_iter()
        self.buffer.insert_with_tags_by_name(iter, text, 'titulo')
        _murotxt = u"\nR_total: %.3f [m²K/W]\nS_total=%.3f [m]\nU = %.3f [W/m²K]"
        for nombre, e, R, S in zip(muro.nombre_capas, muro.espesores, muro.R, muro.S):
            #el archivo de datos de ejemplo está en formato latin1
            text = u"%s:\n" % nombre.decode('iso-8859-1')
            iter = self.buffer.get_end_iter()
            self.buffer.insert_with_tags_by_name(iter, text, 'capa')
            text = u"%.3f [m]\nR=%.3f [m²K/W]\nS=%.3f [m]\n" % (e, R, S)
            iter = self.buffer.get_end_iter()
            self.buffer.insert_with_tags_by_name(iter, text, 'datoscapa')
        text = _murotxt % (muro.R_total, muro.S_total, muro.U)
        iter = self.buffer.get_end_iter()
        self.buffer.insert_with_tags_by_name(iter, text, 'resultados')
        while gtk.events_pending():
            gtk.main_iteration()

class CDialogoMuro(object):
    """Clase para mostrar el diálogo de selección de muro"""

    def __init__(self):
        builder = gtk.Builder()
        builder.add_from_file(os.path.join(os.getcwd(), 'condensa.ui'))
        self.dlg = builder.get_object('dialogomuro')
        self.tvmuro = builder.get_object('tvmuro')
        self.lblselected = builder.get_object('lblselected')
        self.lsmuros = builder.get_object('liststoremuros')
#        datosmuro = [("M1",), ("M2",), ("M3",)]
#        for muro in datosmuro:
#            self.lsmuros.append(muro)
        smap = {"on_tvmuro_cursor_changed" : self.on_tvmuro_cursor_changed,
                "on_btnacepta_clicked": self.on_btnacepta_clicked,
                "on_btncancela_clicked": self.on_btncancela_clicked}
        builder.connect_signals(smap)
        self.lblselected.set_text("Nada")

    def on_tvmuro_cursor_changed(self, tv):
        _murotm, _murotm_iter = self.tvmuro.get_selection().get_selected()
        value = _murotm.get_value(_murotm_iter, 0)
        print value
        self.lblselected.set_text(value)
        print

    def on_btnacepta_clicked(self, btn):
        self.dlg.response(gtk.RESPONSE_ACCEPT)
        print 1

    def on_btncancela_clicked(self, btn):
        self.dlg.response(gtk.RESPONSE_CANCEL)
        print 2

    def run(self):
        self.result = self.dlg.run()
        self.nombremuro = self.lblselected.get_text()
        self.dlg.destroy()
        return self.nombremuro

if __name__ == "__main__":
    w = gtk.Window()
    v = gtk.VBox()
    c = CCabecera()
    t = CTextView()
    p = CPie()
    v.pack_start(c)
    v.pack_start(t)
    v.pack_start(p)
    w.add(v)
    w.show_all()
    #t.update(muro)
    w.connect('destroy', gtk.main_quit)
    gtk.main()
    
#    def on_clicked(widget, accion):
#        resultado, accion_resultado = AccionDialog(accion).run()
#        if resultado == gtk.RESPONSE_APPLY:
#            print accion_resultado
#            accion = accion_resultado
#        elif resultado == gtk.RESPONSE_CANCEL:
#            print 'Acción intacta'
#        elif resultado == gtk.RESPONSE_DELETE_EVENT:
#            gtk.main_quit()