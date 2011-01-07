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
"""Iconos de la aplicación Condensaciones en GTK+"""

import gtk
import util

class IconFactory(gtk.IconFactory):
    def __init__(self, widget):
        """IconFactory para los iconons personalizados."""
        gtk.IconFactory.__init__(self)
        self.add_default()
        icons = {'condensa-application': 'drop.png',
                 'condensa-cerramientos': 'cerramientos.png',
                 'condensa-clima': 'clima.png',}
        for id, filename in icons.items():
            iconfile = util.get_resource('data/icons', filename)
            iconset = gtk.IconSet(gtk.gdk.pixbuf_new_from_file(iconfile))
            self.add(id, iconset)