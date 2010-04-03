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
"""Módulo de definición de materiales y propiedades"""

from material import Material
import configobj

def loadmaterialesdb(filename='DB.ini'):
    """Lee base de datos de materiales en formato ConfigObj
    
    Deveuelve:
        - diccionario de nombres de material con instancias de Material
        - lista de nombres de materiales
        - diccionario de grupos con conjuntos de nombres de material
    """
    def unescape(data):
        """Unescape &amp;, &lt;, and &gt; in a string of data."""
        data = data.replace("&lb;", "[").replace("&rb;", "]")
        return data.replace("&amp;", "&")
    #TODO:Falta por convertir datos al tipo adecuado
    config = configobj.ConfigObj(filename, encoding='utf-8', raise_errors=True)
    materiales, names, groups = {}, [], {}
    for section in config:
        material = config[section]
        name = unescape(material['name'])
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
        materiales[name] = m
        names.append(name)
        groups.setdefault(group, set()).add(name)
    return materiales, names, groups
