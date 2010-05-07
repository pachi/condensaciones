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

import configobj

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

class MaterialesDB(object):
    """Base de datos de Materiales
    
    filename - nombre del archivo desde el que cargar la base de datos
    
    nombre - nombre de la base de datos
    
    nombres - lista de nombres de materiales de la BBDD
    nombresgrupos - lista de nombres de grupos de la BBDD
    materiales - diccionario de materiales de la BBDD por nombre de material
    """
    def __init__(self, filename):
        self.loadmaterialesdb(filename)
    
    def __getitem__(self, key):
        return self.materiales[key]
    
    def __setitem__(self, key, value):
        self.materiales[key] = value
        #FIXME: se puede ordenar de otra forma
        self.nombres.append(key)
    
    def __delitem__(self, key):
        del self.materiales[key]
        self.nombres.remove(key)
    
    def loadmaterialesdb(self, filename='DB.ini'):
        """Lee base de datos de materiales en formato ConfigObj de archivo"""
        def unescape(data):
            """Unescape &amp;, &lt;, and &gt; in a string of data."""
            k = data.replace("&lb;", "[").replace("&rb;", "]")
            return k.replace("&amp;", "&")
        
        config = configobj.ConfigObj(filename, encoding='utf-8',
                                     raise_errors=True)
        self.nombres, self.nombresgrupos = [], []
        self.materiales = {}
        # Lee valores de configuración de la base de datos si existe
        if 'config' in config:
            self.config = config['config'].copy()
            del config['config']
            self.nombre = self.config['nombre'] if 'nombre' in self.config else ''
        else:
            self.config = None
        # Lee datos 
        for section in config:
            material = config[section]
            name = unescape(section)
            db = material['db']
            group = material['group']
            mtype = material['type']
            mu = material.as_float('mu')
            m = Material(name, group, mtype, mu, db)
            # Valores por tipo
            if mtype == 'RESISTANCE':
                m.resistance = material.as_float('resistance')
            elif mtype == 'PROPERTIES':
                m.conductivity = material.as_float('conductivity')
                m.thickness = material.as_float('thickness')
                m.density = material.as_float('density')
                m.specific_heat = material.as_float('specific_heat')
            # Valores opcionales
            if 'thickness_change' in material:
                m.thickness_change = material.as_bool('thickness_change')
            if 'thickness_min' in material:
                m.thickness_min = material.as_float('thickness_min')
            if 'thickness_max' in material:
                m.thickness_max = material.as_float('thickness_max')
            self.nombres.append(name)
            if group not in self.nombresgrupos:
                self.nombresgrupos.append(group)
            self.materiales[name] = m
