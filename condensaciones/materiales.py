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

from util import get_resource
import dbutils

CATALOGOPACHI = get_resource('../data/PCatalogo.bdc')
CATALOGOCALENER = get_resource('../data/BDCatalogo.bdc')
CATALOGOURSA = get_resource('../data/Catalogo_URSA.bdc')

materiales = dbutils.db2data([CATALOGOPACHI, CATALOGOCALENER, CATALOGOURSA])

def tipo(nombre):
    return materiales[nombre]['TYPE']

def conductividad(nombre):
    return float(materiales[nombre]['CONDUCTIVITY'])

def resistencia(nombre):
    return float(materiales[nombre]['RESISTANCE'])

def difusividad(nombre):
    return float(materiales[nombre]['VAPOUR-DIFFUSIVITY-FACTOR'])

if __name__ == "__main__":
    print materiales