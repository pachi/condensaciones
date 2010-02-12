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
"""Módulo de definición de materiales y propiedades"""

from util import get_resource
from dbutils import db2data

CATALOGOPACHI = get_resource('data/PCatalogo.bdc')
CATALOGOCALENER = get_resource('data/BDCatalogo.bdc')
CATALOGOURSA = get_resource('data/Catalogo_URSA.bdc')

materiales, grupos = db2data([CATALOGOPACHI, CATALOGOCALENER, CATALOGOURSA])

#===============================================================================
# Funciones auxiliares
#===============================================================================
def tipo(nombre):
    """Tipo de elemento en relación a su comportamiento térmico
    
    Puede ser de los tipos:
    - PROPERTIES, definido por su conductividad térmica 'CONDUCTIVITY'
    - RESISTANCE, definido por su resistencia térmica 'RESISTANCE'
    """
    return materiales[nombre].type

def conductividad(nombre):
    """Conductividad térmica del material [W/m.K]"""
    return float(materiales[nombre].conductivity)

def resistencia(nombre):
    """Resistencia térmica del material [m²/K.W]"""
    return float(materiales[nombre].resistance)

def difusividad(nombre):
    """Difusividad al vapor de agua del material"""
    return float(materiales[nombre].mu)

if __name__ == "__main__":
    print materiales