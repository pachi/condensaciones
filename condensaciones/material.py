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
"""Definición de clase para representar materiales"""

class Material(object):
    """Material tipo definidos por su nombre, tipo y propiedades
    
    Propiedades generales
    ---------------------
        - name - nombre del material
        - group - nombre del grupo genérico al que pertenece el material
        - type - tipo según definición [RESISTANCE|PROPERTIES|SHADING-COEF]
        - mu - resistencia a la difusión del vapor de agua [adimensional]
        - db - base de datos de procedencia del material
        - Propiedades opcionales
            - thickness_change - posiblidad de varios espesores [True|False]
    
    Propiedades de materiales tipo PROPERTIES
    -----------------------------------------
        - thickness - espesor del elemento [m]
        - conductivity - conductividad térmica [W/m.K]
        - density - densidad del material [kg/m³]
        - specific_heat - calor específico [J/kg.K]
            - thickness_min - espesor mínimo [m]
            - thickness_max - espesor máximo [m]
    
    Propiedades de materiales tipo RESISTANCE
    -----------------------------------------
        - resistance - resistencia térmica del elemento [m²/K.W]
    """
    def __init__(self, name, group, mtype, mu, db=''):
        """Inicialización de datos generales"""
        self.name = name
        self.group = group
        self.type = mtype
        self.mu = mu
        self.db = db
        #self.name_calener = ''
        #self.image = 'asfalto.bmp'
        #self.library = False
