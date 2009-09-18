#!/usr/bin/env python
#encoding: iso-8859-15

import gtk
import pango
import ptcanvas

class CTextView(gtk.ScrolledWindow):
    "Control para mostrar datos de Cerramientos en formato Texto"
    __gtype_name__ = 'CTextView'
    #TODO: Convertir a scrolledwindow cuando glade3 soporte buffer de texto con
    #textags en la textagtable (ahora permite crear tablas pero no añadir tags
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
        self.buffer.set_text("")
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

if __name__ == "__main__":
    w = gtk.Window()
    v = gtk.VBox()
    t = CTextView()
    v.pack_start(t)
    w.add(v)
    w.show_all()
    #t.update(muro)
    w.connect('destroy', gtk.main_quit)
    gtk.main()