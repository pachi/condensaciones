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
"""Tests del módulo condensaciones.psicrom"""

import unittest
import condensaciones.psicrom as psicrom

class  PsicromTestCase(unittest.TestCase):
    """Comprobaciones de condensación"""
    def test_psat(self):
        """Presión de saturación"""
        psat1 = psicrom.psat(-20.0)
        self.assertAlmostEqual(psat1, 104.23015948, places=8)
        psat2 = psicrom.psat(20.0)
        self.assertAlmostEqual(psat2, 2336.95114380, places=8)

    def test_pvapor(self):
        """Presión de vapor"""
        p = psicrom.pvapor(20.0, 55.0)
        self.assertAlmostEqual(p, 1285.32312909, places=8)

    def test_temploc(self):
        """Temperatura en localidad no capital de provincia"""
        t = psicrom.temploc(20.0, 100.0)
        self.assertAlmostEqual(t, 19.0, places=8)

    def test_psatloc(self):
        """Presión de saturación en localidad no capital de provincia"""
        p = psicrom.psatloc(20.0, 100.0)
        self.assertAlmostEqual(p, 2196.15124323, places=8)

    def test_hrloc(self):
        """Humedad relativa en localidad no capital de provincia"""
        hr1 = psicrom.hrloc(20.0, 55.0, -100.0)
        self.assertAlmostEqual(hr1, 55.0, places=8)
        hr2 = psicrom.hrloc(20.0, 55.0, 100.0)
        self.assertAlmostEqual(hr2, 58.52616631, places=8)

    def test_hrintISO(self):
        """Humedad relativa interior - método ISO EN 13788:2002"""
        temp_sint = 19.0330684375
        hrint = psicrom.hrintISO(5, temp_sint, 96, higrometria=3)
        self.assertAlmostEqual(hrint, 47.23481837, places=8)

    def test_hrintCTE1(self):
        """Humedad relativa interior - método CTE datos ambientales"""
        temp_sint = 19.0330684375
        G = 0.55 #higrometría 3
        n = 1 # renovaciones/hora [h^-1]
        volumen = 10 #volumen recinto [m³]
        hrintCTE = psicrom.hrintCTE(5, 20, temp_sint, 96, G, volumen, n)
        self.assertAlmostEqual(hrintCTE, 52.46614215, places=8)

    def test_hrintCTE2(self):
        """Humedad relativa interior - método CTE higrometría"""
        hrintCTE2 = psicrom.hrintCTE(higrometria=3)
        self.assertAlmostEqual(hrintCTE2, 55.00, places=8)

    def test_g(self):
        """Tasa de transferencia de vapor"""
        g_total = 3600.0 * psicrom.g(1016.00114017,
                                                          1285.32312909,
                                                          0.0, 2.16)
        self.assertAlmostEqual(g_total, 0.08977400, places=8) # g/m2.s

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(PsicromTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
