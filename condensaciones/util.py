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
"""Módulo de utilidades varias"""

import os
import colorsys

def get_resource(*path_list):
    "Localiza un recurso del proyecto en base al directorio base del paquete"
    APPROOT = os.path.dirname(__file__)
    return os.path.abspath(os.path.join(APPROOT, *path_list))

def stringify(alist, prec):
    "Convierte lista de números a representación con precisión fija" 
    _format = '%%.%if' % prec
    return "[" + ", ".join([_format % item for item in alist]) + "]"

def colorlist(steps):
    "Devuelte una lista de colores de n elementos"
    saltos = [x / float(steps) for x in range(steps)]
    return [colorsys.hls_to_rgb(salto, .6, .8) for salto in saltos]

def colores_capas(lista_capas):
    "Crea un diccionario asignando a cada capa un color"
    capas_distintas = set(lista_capas)
    colordict = {}
    for nombre, color in zip(capas_distintas, colorlist(len(capas_distintas))):
        colordict[nombre] = color
    return colordict

def add_margin(lista, margen_lateral=0.025):
    "Añade a una lista númerica elementos final e inicial separados un margen"
    return ([lista[0] - margen_lateral] + lista + [lista[-1] + margen_lateral])
