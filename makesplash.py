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

    # Normalize the canvas
    # transform so that (0,0) to (1,1)
    # maps to (15, 15) to (width - 30, height - 30)
    width, height = surface.get_width(), surface.get_height()
    cr.translate(15, 300)
    cr.scale((width - 30) / 1.0, (height - 30) / 1.0)
    cr.set_source_rgb(1, 1, 1)
    cr.set_line_width(0.01)
    cr.select_font_face('Helvetica')
    cr.set_font_size(0.08)
    #px = max(cr.device_to_user_distance(1, 1))
    fascent, fdescent, fheight, fxadvance, fyadvance = cr.font_extents()
    #print cr.font_extents()
    #xbearing, ybearing, twidth, theight, xadvance, yadvance
    _, _, twidth, theight, _, _ = cr.text_extents(APPNAME)
    cr.set_source_rgb(1, 1, 1)
    cr.move_to(0.0, fheight)
    cr.show_text(APPNAME)
    cr.set_font_size(0.05)
    cr.move_to(twidth + 0.03, fheight)
    cr.show_text(version)
    cr.set_font_size(0.04)
    y = 1.7 * fheight
    cr.move_to(0.0, y)
    cr.show_text(COPYTXT)
    fascent, fdescent, fheight, fxadvance, fyadvance = cr.font_extents()
    y = y + 1.0 * fheight
    cr.move_to(0.0, y)
    cr.show_text(WEBTXT)
    cr.move_to(0.0, y + 1.0 * fheight)
    cr.set_font_size(1.0)
    _, _, tw, th, _, _ = cr.text_extents(APPDESC)
    cr.set_font_size(1.0 / tw)
    cr.show_text(APPDESC)
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
