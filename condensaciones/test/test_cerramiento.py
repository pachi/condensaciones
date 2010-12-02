#!/usr/bin/env python
#encoding: utf-8
#
#   condensaciones.py
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
"""Tests del módulo condensaciones.cerramiento"""

import unittest
from condensaciones.cerramiento import Cerramiento
from condensaciones.clima import Clima
#from condensaciones.util import stringify

climae = Clima(5, 96) #T, HR
climai = Clima(20.0, 55) #T, HR
climae1 = Clima(10.7, 79) #datos enero Sevilla
climai1 = Clima(20.0, 75) #T, HR

capas1 = [(u"1/2 pie LP métrico o catalán 40 mm< G < 60 mm", 0.11),
          (u"Mortero de áridos ligeros [vermiculita perlita]", 0.01),
          (u"EPS Poliestireno Expandido [ 0.037 W/[mK]]", 0.03),
          (u"Tabique de LH sencillo [40 mm < Espesor < 60 mm]", 0.03),
          (u"Enlucido de yeso 1000 < d < 1300", 0.01),]

class  CerramientoTestCase(unittest.TestCase):
    """Comprobaciones de condensación"""
    def setUp(self):
        """Module-level setup"""
        self.c1 = Cerramiento("Cerramiento tipo", "Descripción",
                              capas1, Rse=0.04, Rsi=0.13)
    def test_nombre(self):
        """Nombre del cerramiento"""
        self.assertEqual(self.c1.nombre, 'Cerramiento tipo')
    
    def test_nombrecapas(self):
        """Nombres de las capas del cerramiento"""
        nombres = self.c1.nombres
        result = [u'1/2 pie LP m\xe9trico o catal\xe1n 40 mm< G < 60 mm',
                  u'Mortero de \xe1ridos ligeros [vermiculita perlita]',
                  u'EPS Poliestireno Expandido [ 0.037 W/[mK]]',
                  u'Tabique de LH sencillo [40 mm < Espesor < 60 mm]',
                  u'Enlucido de yeso 1000 < d < 1300']
        self.assertEqual(nombres, result)
    
    def test_espesores(self):
        """Espesor geométrico de cada capa del cerramiento [m]"""
        e = self.c1.espesores
        result = [0.11, 0.01, 0.03, 0.03, 0.01]
        self.assertEqual(e, result)
    
    def test_R(self):
        """Resistencia térmica de las capas del cerramiento [m²K/W]"""
        R = self.c1.R
        result = [0.040, 0.16491754, 0.02439024, 0.80,
                  0.06741573, 0.01754386, 0.13]
        for a, b in zip(R, result):
            self.assertAlmostEqual(a, b, places=8)

    def test_R_total(self):
        """Resistencia térmica total del cerramiento [m²K/W]"""
        Rt = self.c1.R_total
        self.assertAlmostEqual(Rt, 1.24426738, places=8)

    def test_S(self):
        """Espesor de aire equivalente de cada capa [m]"""
        S = self.c1.S
        result = [1.10, 0.10, 0.6, 0.3, 0.06]
        self.assertEqual(S, result)

    def test_S_total(self):
        """Espesor de aire equivalente total [m]"""
        St = self.c1.S_total
        self.assertEqual(St, 2.16)

    def test_Rs(self):
        """Resistencias superficiales del cerramiento"""
        rse = self.c1.Rse
        rsi = self.c1.Rsi
        self.assertEqual(rse, 0.04)
        self.assertEqual(rsi, 0.13)
        
    def test_U(self):
        """Transmitancia térmica total del cerramiento [W/m²K]"""
        U = self.c1.U
        self.assertAlmostEqual(U, 0.80368578, places=8)

    def test_temperaturas(self):
        """Temperaturas en capas de cerramiento"""
        temperaturas = self.c1.temperaturas(climae.temp, climai.temp)
        result = [5.0, 5.48221147, 7.47033972, 7.76437110, 17.40860050,
                  18.22131646, 18.43281272, 20.0]
        for a, b in zip(temperaturas, result):
            self.assertAlmostEqual(a, b, places=8)

    def test_presiones(self):
        """Presiones de vapor en capas de cerramiento"""
        presiones = self.c1.presiones(climae.temp, climai.temp,
                                      climae.HR, climai.HR)
        result = [836.98994423079864, 836.98994423079864, 1065.3077698541961,
                  1086.0639358199594, 1210.6009316145398, 1272.86942951183,
                  1285.3231290912881, 1285.3231290912881]
        for a, b in zip(presiones, result):
            self.assertAlmostEqual(a, b, places=8)
        p_aire_ext = presiones[0]
        p_aire_int = presiones[-1]
        p_superficie_ext = presiones[1]
        p_superficie_int = presiones[-2]
        self.assertAlmostEqual(p_aire_ext, 836.99, places=2)
        self.assertAlmostEqual(p_aire_int, 1285.32, places=2)
        self.assertAlmostEqual(p_superficie_ext, 836.99, places=2)
        self.assertAlmostEqual(p_superficie_int, 1285.32, places=2)

    def test_presionessat(self):
        """Presiones de saturación en capas de cerramiento"""
        presiones_sat = self.c1.presionessat(climae.temp, climai.temp)
        result = [871.86452524041533, 901.6494125680565, 1034.1390998299653,
                  1055.1221100710804, 1987.3647452639884, 2091.7093045723445,
                  2119.6372278156796, 2336.9511438023419]
        psext = presiones_sat[0]
        psint = presiones_sat[-1]
        self.assertEqual(presiones_sat, result)
        self.assertAlmostEqual(psext, 871.86452524041533, places=8)
        self.assertAlmostEqual(psint, 2336.9511438023419, places=8)

    def test_condensa(self):
        """Condensación intersticial en cerramiento [g/m2.mes]"""
        g, puntos_condensacion = self.c1.condensacion(climae.temp, climai.temp,
                                                      climae.HR, climai.HR)
        cantidad_condensada = sum(g) * 2592000.0 #[g/m2.mes]
        result_cc = 31.397530032177634
        self.assertEqual(cantidad_condensada, result_cc)

    def test_evapora(self):
        """Evaporación intersticial en cerramiento"""
        # indicamos evaporación en la interfase 2, pero habría que ver en
        # cuáles había antes condensaciones y realizar el cálculo en ellas.
        g, puntos_evaporacion = self.c1.evaporacion(climae.temp, climai.temp,
                                                 climae.HR, climai.HR,
                                                 interfases=[2])
        cantidad_evaporada = sum(g) * 2592000.0 #[g/m2.mes]
        result_ce = 30.075454627910425
        #result_ce = 0.0 #FIXME: Solucionar. Implementar bien cálculo
        self.assertEqual(cantidad_evaporada, result_ce)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(CerramientoTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)

