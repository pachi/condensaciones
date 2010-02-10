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
"""Tests del módulo condensaciones.dbutils"""

import unittest
import condensaciones.dbutils as dbutils

datablock = ['"B_Vapor Z3 (d_1mm)" = MATERIAL',
             'TYPE           = PROPERTIES',
             '    THICKNESS      = 0.001',
             '    CONDUCTIVITY   = 500',
             '    DENSITY        = 1',
             '    SPECIFIC-HEAT  = 1',
             '    VAPOUR-DIFFUSIVITY-FACTOR = 2030',
             '    NAME           = "B_Vapor Z3 (d_1mm)"',
             '    NAME_CALENER   = ""',
             '    GROUP          = "B_VAPOR"',
             '    IMAGE          = "asfalto.bmp"',
             '    LIBRARY        = NO',
             ]

parsedblock = {'MATERIAL': 'B_Vapor Z3 (d_1mm)',
               'TYPE': 'PROPERTIES',
               'THICKNESS': '0.001',
               'CONDUCTIVITY': '500',
               'DENSITY': '1',
               'SPECIFIC-HEAT': '1',
               'VAPOUR-DIFFUSIVITY-FACTOR': '2030',
               'NAME': 'B_Vapor Z3 (d_1mm)',
               'NAME_CALENER': '',
               'GROUP': 'B_VAPOR',
               'IMAGE': 'asfalto.bmp',
               'LIBRARY': 'NO',}

DB = "./PCatalogo.bdc"

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
        self.block = datablock
        self.parsedblock = dbutils.parseblock(self.block)
        self.parsedfile = dbutils.parsefile(DB)
        self.materials, self.groups = dbutils.db2data(DB)

    def test_parseblock(self):
        """Interpretación de bloque de datos"""
        self.assertEqual(self.parsedblock, parsedblock)

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
