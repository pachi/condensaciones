#!/usr/bin/env python
#encoding: utf-8
#
#   condensaciones.py
#   Programa de cálculo de condensaciones según CTE
#
#   Copyright (C) 2007-2010 por Rafael Villar Burke <pachi@rvburke.com>
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
"""Tests del módulo condensaciones.comprobaciones"""

import unittest
from condensaciones.cerramiento import Cerramiento
from condensaciones.clima import Clima
import condensaciones.comprobaciones as comprobaciones

#climae1 = Clima(10.7, 79) #datos enero Sevilla
climae = Clima(5, 96) #T, HR
climai = Clima(20.0, 55) #T, HR

capas1 = [(u"1/2 pie LP métrico o catalán 40 mm< G < 60 mm", 0.11),
          (u"Mortero de áridos ligeros [vermiculita perlita]", 0.01),
          (u"EPS Poliestireno Expandido [ 0.037 W/[mK]]", 0.03),
          (u"Tabique de LH sencillo [40 mm < Espesor < 60 mm]", 0.03),
          (u"Enlucido de yeso 1000 < d < 1300", 0.01),]

class  ComprobacionesTestCase(unittest.TestCase):
    def setUp(self):
        """Module-level setup"""
        self.c1 = Cerramiento("Cerramiento tipo", "Descripción",
                              capas1, Rse=0.04, Rsi=0.13)

    def test_fRsi(self):
        """Factor de temperatura superficial"""
        _fRsi = comprobaciones.fRsi(self.c1.U)
        self.assertAlmostEqual(_fRsi, 0.79907855, places=8)

    def test_fRsimin(self):
        """Factor de temperatura superficial mínimo"""
        _fRsimin = comprobaciones.fRsimin(climae.temp, climai.temp, climai.HR)
        self.assertAlmostEqual(_fRsimin, 0.60574531, places=8)

    def test_condensas(self):
        """Condensación superficial"""
        _cs = comprobaciones.condensas(self.c1,
                                       climae.temp,
                                       climai.temp, climai.HR)
        self.assertFalse(_cs)

    def test_condensai(self):
        """Condensación intersticial"""
        _ci = comprobaciones.condensai(self.c1,
                                       climae.temp, climai.temp,
                                       climae.HR, climai.HR)
        self.assertTrue(_ci)

    def test_condensaciones(self):
        """Condensaciones (superficial o intersticial)"""
        _c = comprobaciones.condensaciones(self.c1,
                                           climae.temp, climai.temp,
                                           climae.HR, climai.HR)
        self.assertTrue(_c)
 
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(ComprobacionesTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
