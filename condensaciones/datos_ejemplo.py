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

from cerramiento import Cerramiento

class Clima(object):
    def __init__(self, temp, HR):
        self.temp = float(temp)
        self.HR = float(HR)

climae1 = Clima(10.7, 79) #datos enero Sevilla
climae2 = Clima(5, 96) #datos para provocar condensaciones
climai1 = Clima(20.0, 55) #según clase de higrometría: 3:55%, 4:62%, 5:70%

climae = climae2
climai = climai1

capas1 = [(u"1/2 pie LP métrico o catalán 40 mm< G < 60 mm", 0.11),
        (u"Mortero de áridos ligeros [vermiculita perlita]", 0.01),
        (u"EPS Poliestireno Expandido [ 0.037 W/[mK]]", 0.03),
        (u"Tabique de LH sencillo [40 mm < Espesor < 60 mm]", 0.03),
        (u"Enlucido de yeso 1000 < d < 1300", 0.01),]
valores1 = {"U":0.804, "S_total":2.16, "fRsi":0.80}

capas2 = [(u"Granito [2500 < d < 2700]", 0.03),
        (u"Mortero de cemento o cal para albañilería y para revoco/enlucido 1800 < d < 2000", 0.02),
        (u"XPS Expandido con dióxido de carbono CO2 [ 0.034 W/[mK]]", 0.05),
        (u"Tabicón de LH doble  [60 mm < E < 90 mm]", 0.14),
        (u"Enlucido de yeso 1000 < d < 1300", 0.015),]
valores2 = {"U":0.496, "S_total":316.69, "fRsi":0.88}

capas3 = [(u"Granito [2500 < d < 2700]", 0.03),
        (u"Mortero de cemento o cal para albañilería y para revoco/enlucido 1800 < d < 2000", 0.02),
        (u"XPS Expandido con dióxido de carbono CO2 [ 0.034 W/[mK]]", 0.05),
        (u"Tabicón de LH doble  [60 mm < E < 90 mm]", 0.14),
        (u"B_Vapor Al (d_0.008mm)", 0.000008),
        (u"Enlucido de yeso 1000 < d < 1300", 0.015),]
valores3 = {"U":0.496, "S_total":1106.69, "fRsi":0.88}

capas4 = [
        (u"XPS Expandido con dióxido de carbono CO2 [ 0.034 W/[mK]]", 0.05),
        (u"Placa de yeso laminado [PYL] 750 < d < 900", 0.015),
        (u"MW Lana mineral [0.031 W/[mK]]", 0.080),
        (u"MW Lana mineral [0.031 W/[mK]]", 0.040),
        (u"Placa de yeso laminado [PYL] 750 < d < 900", 0.0125),
        (u"Placa de yeso laminado [PYL] 750 < d < 900", 0.0125)]
valores4 = {"U":0.176, "S_total":5.28, "fRsi":0.36}

capas5 = [
        (u"EPS Poliestireno Expandido [ 0.037 W/[mK]]", 0.05),
        (u"Placa de yeso laminado [PYL] 750 < d < 900", 0.015),
        (u"MW Lana mineral [0.031 W/[mK]]", 0.080),
#        (u"Cámara de aire sin ventilar horizontal 2 cm", 0.015),
        (u"XPS Expandido con dióxido de carbono CO2 [ 0.034 W/[mK]]", 0.05),
        (u"Placa de yeso laminado [PYL] 750 < d < 900", 0.0125),
        (u"Placa de yeso laminado [PYL] 750 < d < 900", 0.0125)]
valores5 = {"U":0.175, "S_total":6.24, "fRsi":0.36}

capas6 = [
        (u"EPS Poliestireno Expandido [ 0.037 W/[mK]]", 0.05),
        (u"Placa de yeso laminado [PYL] 750 < d < 900", 0.015),
        (u"MW Lana mineral [0.031 W/[mK]]", 0.080),
#        (u"Cámara de aire sin ventilar horizontal 2 cm", 0.015),
        (u"B_Vapor Al (d_0.008mm)", 0.000008),
        (u"MW Lana mineral [0.031 W/[mK]]", 0.040),
        (u"Placa de yeso laminado [PYL] 750 < d < 900", 0.0125),
        (u"Placa de yeso laminado [PYL] 750 < d < 900", 0.0125)]
valores6 = {"U":0.181, "S_total":801.28, "fRsi":0.36}

murocapas = capas1

# --------- Lista de capas para empezar con datos -------------
muro1 = Cerramiento(u"Cerramiento 1",
                    u"1/2' LP + EPS 3cm + LH + Yeso",
                    capas1, 0.04, 0.13)
muro2 = Cerramiento(u"Cerramiento 2",
                    u"Granito 3cm + XPS 5cm + LHD + Yeso",
                    capas2, 0.04, 0.13)
muro3 = Cerramiento(u"Cerramiento 3",
                    u"Granito 3cm + XPS 5cm + LHD + BV + Yeso",
                    capas3, 0.04, 0.13)
muro4 = Cerramiento(u"Cerramiento 4",
                    u"XPS 5cm + MW 8cm + MW 4cm + PYL 1.25cm + PYL 1.25cm",
                    capas4, 0.04, 0.13)
muro5 = Cerramiento(u"Cerramiento 5",
                    u"EPS 5cm + PYL 1.5cm + MW 8cm + XPS 5cm + PYL 1.25cm + PYL 1.25cm",
                    capas5, 0.04, 0.13)
muro6 = Cerramiento(u"Cerramiento 6",
                    u"EPS 5cm + PYL 1.5cm + MW 8cm + BV + MW 4cm + PYL 1.25cm + PYL 1.25cm",
                    capas6, 0.04, 0.13)

muros = [muro1, muro2, muro3, muro4, muro5, muro6]