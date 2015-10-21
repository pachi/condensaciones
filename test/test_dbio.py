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
"""Tests del módulo condensaciones.dbutils"""

#TODO: Con configobj ahora habría que probar, por un lado, la conversión de
#TODO: formato .bdc a .ini y, por otro, de formato .ini a materiales.
#TODO: test DB2ini de dbutils 
#TODO: de materiales testea loadmaterialesdb

import os
import unittest
import condensaciones.dbutils as dbutils

this_dir = os.path.dirname(__file__)
DB = os.path.join(this_dir, "./PCatalogo.bdc")

parsedfile = {u'default':
            [{u'GROUP': u'B_VAPOR',
              u'NAME': u'B_Vapor Z3 (d_1mm)',
              u'DENSITY': u'1', u'SPECIFIC-HEAT': u'1',
              u'MATERIAL': u'B_Vapor Z2 (d_1mm)', u'NAME_CALENER': u'',
              u'LIBRARY': u'NO', u'THICKNESS': u'0.001',
              u'VAPOUR-DIFFUSIVITY-FACTOR': u'1350', u'TYPE': u'PROPERTIES',
              u'IMAGE': u'asfalto.bmp', u'CONDUCTIVITY': u'500'},
             {u'GROUP': u'B_VAPOR',
              u'NAME': u'B_Vapor Z3 (d_1mm)',
              u'DENSITY': u'1', u'SPECIFIC-HEAT': u'1',
              u'MATERIAL': u'B_Vapor Z3 (d_1mm)', u'NAME_CALENER': u'',
              u'LIBRARY': u'NO', u'THICKNESS': u'0.001',
              u'VAPOUR-DIFFUSIVITY-FACTOR': u'2030', u'TYPE': u'PROPERTIES',
              u'IMAGE': u'asfalto.bmp', u'CONDUCTIVITY': u'500'},
             {u'GROUP': u'B_VAPOR',
              u'NAME': u'B_Vapor Al (d_0.008mm)',
              u'DENSITY': u'2700', u'SPECIFIC-HEAT': u'880',
              u'MATERIAL': u'B_Vapor Al (d_0.008mm)', u'NAME_CALENER': u'',
              u'LIBRARY': u'NO', u'THICKNESS': u'0.000008',
              u'VAPOUR-DIFFUSIVITY-FACTOR': u'1E+8', u'TYPE': u'PROPERTIES',
              u'IMAGE': u'metales.bmp', u'CONDUCTIVITY': u'230'}
            ]}

class  DBTestCase(unittest.TestCase):
    """Comprobaciones de interpretación de datos"""
    def setUp(self):
        """Module-level setup"""
        self.parsedfile = dbutils.parsefile(DB)
        self.materials, self.names, self.groups = dbutils._db2data(DB)

    def test_parsefile(self):
        """Interpretación de archivo de datos"""
        self.assertEqual(self.parsedfile, parsedfile)

    def test_db2data(self):
        """Conversión de datos a diccionarios"""
        keys = [u'B_Vapor Al (d_0.008mm)', u'B_Vapor Z3 (d_1mm)']
        mk = self.materials.keys()
        mk.sort()
        groupdata = list(self.groups.values()[0])
        groupdata.sort()
        self.assertEqual(mk, keys)
        self.assertEqual(groupdata, keys)

    def test_db2data2(self):
        """Conversión de elementos a objetos"""
        m = self.materials[u'B_Vapor Al (d_0.008mm)']
        self.assertEqual(m.name, u'B_Vapor Al (d_0.008mm)')
        self.assertEqual(m.group, u'B_VAPOR')
        self.assertEqual(m.type, u'PROPERTIES')
        self.assertEqual(m.conductivity, 230.0)
        self.assertEqual(m.thickness, 0.000008)
        self.assertEqual(m.mu, 1.0e8)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(DBTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
