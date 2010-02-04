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

    def test_tasatransferenciavapor(self):
        """Tasa de transferencia de vapor"""
        g_total = 3600.0 * psicrom.g(1016.00114017,
                                                          1285.32312909,
                                                          0.0, 2.16)
        self.assertAlmostEqual(g_total, 0.08977400, places=8) # g/m2.s

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(PsicromTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
