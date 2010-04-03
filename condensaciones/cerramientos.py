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
"""Módulo de definición de cerramientos y propiedades"""

from cerramiento import Cerramiento
import configobj

def loadcerramientosdb(filename='CerramientosDB.ini'):
    """Lee base de datos de cerramientos en formato ConfigObj
    
    Deveuelve:
        - diccionario de nombres de cerramiento con instancias de Cerramiento
        - lista de nombres de cerramientos
        - diccionario de grupos con conjuntos de nombres de material
    """
    def unescape(data):
        """Unescape &amp;, &lt;, and &gt; in a string of data."""
        data = data.replace("&lb;", "[").replace("&rb;", "]")
        return data.replace("&amp;", "&")
    config = configobj.ConfigObj(filename, encoding='utf-8', raise_errors=True)
    cerramientos, cnames, cgroups = {}, [], {}
    # Lee valores de configuración de la base de datos
    dbconf = config['config']
    del config['config']
    # Lee datos 
    for section in config:
        cerramiento = config[section]
        nombre = unescape(section)
        descripcion = cerramiento['descripcion']
        capas = cerramiento['capas']
        lcapas = [(name, float(e)) for ncapa, (name, e) in capas.items()]
        c = Cerramiento(nombre, descripcion, lcapas)
        # Valores opcionales
        if 'tipo' in cerramiento:
            c.tipo = cerramiento['tipo']
        else:
            c.tipo = 'predeterminado'
        if 'Rse' in cerramiento:
            c.Rse = cerramiento.as_float('Rse')
        if 'Rsi' in cerramiento:
            c.Rsi = cerramiento.as_float('Rsi')
        cerramientos[nombre] = c
        cnames.append(nombre)
        cgroups.setdefault(c.tipo, set()).add(nombre)
    return cerramientos, cnames, cgroups
