#!/usr/bin/env python
# encoding: utf-8
#
#   condensaciones.py
#   Programa de cÃ¡lculo de condensaciones segÃºn CTE
#
#   Copyright (C) 2009-2010 por Rafael Villar Burke <pachi@rvburke.com>
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
"""Overlay application and version information on background image

This script overlays informational text (name, version, author...)
over a background image to be used as splash.
"""
import optparse
import cairo
import pango, pangocairo

APPNAME = 'condensaciones'
APPDESC = u'Aplicación para el cálculo de condensaciones y parámetros higrotérmicos en cerramientos'
COPYTXT = u'© 2009-2010 Rafael Villar Burke [GPL v2+]'
WEBTXT = u'http://www.rvburke.com'

def splashimage(version='1.0', bgfile='background.png', outfile='fondo.png'):
    """Create a splash image using a background image and a version string

    version: version string
    bgfile: background image in png format (400x470px)
    outfile: output file name. Will be written in png format
    """
    surface = cairo.ImageSurface.create_from_png(bgfile)
    cr = cairo.Context(surface)
    width, height = surface.get_width(), surface.get_height()
    cr.set_source_rgb(1, 1, 1)
    pctx = pangocairo.CairoContext(cr)
    layout = pctx.create_layout()
    layout.set_font_description(pango.FontDescription("Helvetica"))
    layout.set_markup(u"<span size='8000'>%s</span><span size='4000'> v.%s\n%s\n%s\n\n</span>"
                      u"<span size='2000' weight='bold'>%s</span>" %(APPNAME, version, COPYTXT, WEBTXT, APPDESC))
    w, h = layout.get_pixel_size()
    sc = min((width - 30.0) / w, (height - 30.0) / h)
    cr.translate(15.5, 0.5 + (height - 15 - sc * h))
    cr.scale(sc, sc)
    pctx.show_layout(layout)
    cr.stroke()
    surface.write_to_png(outfile)
    cr.show_page()
    surface.finish()

if __name__ == "__main__":
    parser = optparse.OptionParser(usage='%prog [options] <version>')
    parser.add_option('-b', action="store", dest="background",
        default="background.png", help="background image file")
    parser.add_option('-o', action="store", dest="outputfile",
        default="fondo.png", help="output file")
    options, remainder = parser.parse_args()
    version = remainder[0] if remainder else '1.0'
    splashimage(version, options.background, options.outputfile)
