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
"""Tests del módulo condensaciones.comprobaciones"""

import unittest
from condensaciones.cerramiento import Cerramiento
from condensaciones.clima import Clima
import condensaciones.comprobaciones as comprobaciones

climae = Clima(5, 96) #T, HR
climai = Clima(20.0, 55) #T, HR
climae1 = Clima(10.7, 79) #datos enero Sevilla
climai1 = Clima(20.0, 75) #T, HR

capas1 = [(u"1/2 pie LP métrico o catalán 40 mm< G < 60 mm", 0.11),
          (u"Mortero de áridos ligeros [vermiculita perlita]", 0.01),
          (u"EPS Poliestireno Expandido [ 0.037 W/[mK]]", 0.03),
          (u"Tabique de LH sencillo [40 mm < Espesor < 60 mm]", 0.03),
          (u"Enlucido de yeso 1000 < d < 1300", 0.01),]

class  ComprobacionesTestCase(unittest.TestCase):
    """Comprobaciones de condensación"""
    def setUp(self):
        """Module-level setup"""
        self.c1 = Cerramiento("Cerramiento tipo", "Descripción",
                              capas1, Rse=0.04, Rsi=0.13)

    def test_fRsi(self):
        """Factor de temperatura superficial"""
        _fRsi = comprobaciones.fRsi(self.c1.U)
        self.assertAlmostEqual(_fRsi, 0.79907855, places=8)

    def test_fRsimin(self):
        """Factor de temperatura superficial mínimo - caso favorable"""
        _fRsimin = comprobaciones.fRsimin(climae.temp, climai.temp, climai.HR)
        self.assertAlmostEqual(_fRsimin, 0.60574531, places=8)

    def test_fRsimin1(self):
        """Factor de temperatura superficial mínimo - caso desfavorable"""
        _fRsimin = comprobaciones.fRsimin(climae.temp,
                                          climai1.temp, climai1.HR)
        self.assertAlmostEqual(_fRsimin, 0.930793648, places=8)

    def test_fRsimin2(self):
        """Factor de temperatura superficial mínimo - caso ISO"""
        _fRsimin = comprobaciones.fRsimin(climae.temp,
                                          climai1.temp, 20)
        self.assertAlmostEqual(_fRsimin, -0.36882331, places=8)
        self.assertRaises(ValueError, comprobaciones.fRsimin, 20, 20)

    def test_condensas(self):
        """Condensación superficial - sin condensación"""
        _cs = comprobaciones.testcondensas(self.c1,
                                           climae.temp,
                                           climai.temp, climai.HR)
        self.assertFalse(_cs)

    def test_condensas1(self):
        """Condensación superficial - con condensación"""
        _cs = comprobaciones.testcondensas(self.c1,
                                           climae.temp,
                                           climai1.temp, climai1.HR)
        self.assertTrue(_cs)

    def test_condensai(self):
        """Condensación intersticial - con condensación"""
        _ci = comprobaciones.testcondensai(self.c1,
                                           climae.temp, climai.temp,
                                           climae.HR, climai.HR)
        self.assertTrue(_ci)

    def test_condensai1(self):
        """Condensación intersticial - sin condensación"""
        _ci = comprobaciones.testcondensai(self.c1,
                                           climae1.temp, climai.temp,
                                           climae1.HR, climai.HR)
        self.assertFalse(_ci)

    def test_condensaciones(self):
        """Condensaciones (superficial o intersticial) - con condensaciones"""
        _c = comprobaciones.testcondensaciones(self.c1,
                                               climae.temp, climai.temp,
                                               climae.HR, climai.HR)
        self.assertTrue(_c)

    def test_condensaciones1(self):
        """Condensaciones (superficial o intersticial) - sin condensaciones"""
        _c = comprobaciones.testcondensaciones(self.c1,
                                               climae1.temp, climai.temp,
                                               climae1.HR, climai.HR)
        self.assertFalse(_c)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(ComprobacionesTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
