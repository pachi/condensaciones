#!/usr/bin/env python
#encoding: iso-8859-15

import gtk

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

if __name__ == "__main__":
    w = gtk.Window()
    c = CCabecera()
    w.add(c)
    w.show_all()
    w.connect('destroy', gtk.main_quit)
    gtk.main()
