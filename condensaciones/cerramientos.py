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
    if 'config' in config:
        dbconf = config['config']
        del config['config']
    else:
        dbconf = None
    for section in config:
        cerramiento = config[section]
        nombre = unescape(section)
        descripcion = cerramiento['descripcion']
        capas = cerramiento['capas']
        lcapas = [(name, float(e)) for ncapa, (name, e) in capas.items()]
        c = Cerramiento(nombre, descripcion, lcapas)
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

CDBHEADING = ['#   Biblioteca de Cerramientos para Condensa', '#', 
'#   Condensa - Programa de cálculo de condensaciones según CTE', '#',
'#   Copyright (C) 2009-2010, Rafael Villar Burke <pachi@rvburke.com>', '#',
'#   Cada sección se denomina con el nombre del cerramiento e incluye:',
'#   - descripcion: descripción del cerramiento',
'#   - tipo: tipo genérico del cerramiento  [opcional]',
'#   - Rse: resistencia superficial exterior [m²K/W] [opcional]',
'#   - Rsi: resistencia superficial interior [m²K/W] [opcional]',
'#   además de una subsección de [[capas]] que contiene por cada entrada:',
'#   - capa: con nombre y espesor de capa [m] separados por una coma',
'#   El nombre de capa no puede contener comas.', '#',
'#   La sección config incluye configuración general como',
'#   - nombre: nombre de la base de datos',
'#   - materiales: nombre de la base de datos de materiales', '#',]

def savecerramientosdb(cerrDB, cerrorder=None, configdata=None,
                       filename='CerramientosDB.ini'):
    """Guarda base de datos de cerramientos en formato ConfigObj
    
    Parámetros:
        cerrDB     - diccionario de nombres de cerramiento con instancias de
                     Cerramiento.
        cernames   - lista opcional de nombres de cerramientos para definir el
                     orden en el que se guardarán los datos.
        config     - Diccionario con valores de configuración.
    """
    def escape(data):
        """Escape &, [ and ] a string of data."""
        data = data.replace("&", "&amp;")
        return data.replace("[", "&lb;").replace("]", "&rb;")
    config = configobj.ConfigObj(filename, encoding='utf-8', raise_errors=True)
    config.initial_comment = CDBHEADING
    # Guarda valores de configuración de la base de datos
    config['config'] = {}
    #XXX: Usar valores adecuados o leer de archivo anterior
    config['config']['nombre'] = "CerramientosDB"
    config['config']['materiales'] = "MaterialesDB"
    if configdata:
        for key in configdata:
            config['config'][key] = configdata[key]
    # Guarda datos de cerramientos
    if not cerrorder:
        cerrorder = cerrDB.keys()
        cerrorder.sort()
    for cerramiento in cerrorder:
        if cerramiento not in cerrDB:
            raise ValueError, "Cerramiento desconocido: %s" % cerramiento
        c = cerrDB[cerramiento]
        config[escape(cerramiento)] = {}
        config.comments[escape(cerramiento)] = '#'
        sect = config[escape(cerramiento)]
        sect['descripcion'] = c.descripcion
        sect['capas'] = {}
        for i, (name, e) in enumerate(c.capas):
            sect['capas']['capa%i' % (i + 1)] = (name, e)
        sect['tipo'] = c.tipo if hasattr(c, 'tipo') else 'predeterminado'
        if hasattr(c, 'Rse'):
            sect['Rse'] = c.Rse
        if hasattr(c, 'Rsi'):
            sect['Rsi'] = c.Rsi
    config.write()
