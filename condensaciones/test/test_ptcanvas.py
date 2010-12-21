#!/usr/bin/env python
#encoding: utf-8
#
#   Programa de cálculo de condensaciones según CTE
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
"""Tests del módulo condensaciones.ptcanvas"""

import unittest
import glib
import gtk
from condensaciones.cerramiento import Cerramiento
from condensaciones.clima import Clima
from condensaciones.ptcanvas import *

climae = Clima(5, 96) #T, HR
climai = Clima(20.0, 55) #T, HR

capas1 = [(u"1/2 pie LP métrico o catalán 40 mm< G < 60 mm", 0.11),
          (u"Mortero de áridos ligeros [vermiculita perlita]", 0.01),
          (u"EPS Poliestireno Expandido [ 0.037 W/[mK]]", 0.03),
          (u"Tabique de LH sencillo [40 mm < Espesor < 60 mm]", 0.03),
          (u"Enlucido de yeso 1000 < d < 1300", 0.01),]

class MockModel(object):
    def __init__(self, c, ce, ci):
        self.c = c
        self.climae = ce
        self.climai = ci

class  PTCanvasTestCase(unittest.TestCase):
    """Comprobaciones de condensación"""
    def setUp(self):
        """Module-level setup"""
        self.c1 = Cerramiento("Cerramiento tipo", "Descripción tipo",
                              capas1, Rse=0.04, Rsi=0.13)
        self.model = MockModel(self.c1, climae, climai)
        
    def test_gdata(self):
        """Muestra gráfica"""
        w = gtk.Window()
        v = gtk.VBox()
        pt = CPTCanvas()
        p = CPCanvas()
        pt.dibuja(self.model)
        p.dibuja(self.model)
        v.pack_start(pt)
        v.pack_start(p)
        w.add(v)
        w.show_all()
        w.connect('destroy', gtk.main_quit)
        glib.timeout_add_seconds(5, gtk.main_quit)
        gtk.main()

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(PTCanvasTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)

