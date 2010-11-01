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
"""Módulo para la definición, almacenamiento y recuperación de materiales."""

import configobj

class Material(object):
    """Material tipo definido por su nombre, tipo y propiedades

    Los materiales pueden ser del tipo `RESISTANCE`, `PROPERTIES` o
    `SHADING-COEF`, aunque Condensaciones únicamente soporta por ahora los
    dos primeros tipos.

    Todos los materiales disponen de las siguientes propiedades: name, group,
    type, mu, db, thickness_change (opcional).

    Propiedades exclusivas de los materiales del tipo `PROPERTIES`: thickness,
    conductivity, density, specific_heat, thickness_min (opcional),
    thickness_max (opcional).

    Propiedades exclusivas de los materiales del tipo `RESISTANCE`: resistance.
    """
    def __init__(self, name, group, mtype, mu, db=''):
        """Inicialización de datos generales

        :param str name: nombre del material
        :param str group: nombre del grupo genérico al que pertenece el material
        :param str mtype: tipo según definición [RESISTANCE|PROPERTIES|SHADING-COEF]
        :param float mu: resistencia a la difusión del vapor de agua [adimensional]
        :param str db: base de datos de procedencia del material
        """
        #: nombre del material (str)
        self.name = name
        #: nombre del grupo genérico al que pertenece el material (str)
        self.group = group
        #: tipo según definición [`RESISTANCE`|`PROPERTIES`|`SHADING-COEF`] (str)
        self.type = mtype
        #: resistencia a la difusión del vapor de agua [adimensional] (float)
        self.mu = float(mu)
        #: nombre de la base de datos de procedencia del material (str)
        self.db = db
        #: admite espesor pesonalizado [`True`|`False`] (bool) (opcional)
        self.thickness_change = True
        #self.name_calener = ''
        #self.image = 'asfalto.bmp'
        #self.library = False
        if mtype == 'PROPERTIES':
            #: espesor del elemento [m] (float)
            self.thickness = None
            #: conductividad térmica [W/m.K] (float)
            self.conductivity = None
            #: densidad del material [kg/m³] (float)
            self.density = None
            #: calor específico [J/kg.K] (float)
            self.specific_heat = None
            #: espesor mínimo admisible [m] (float) (opcional)
            self.thickness_min = None
            #: espesor máximo admisible [m] (float) (opcional)
            self.thickness_max = None
        elif mtype == 'RESISTANCE':
            #: resistencia térmica del elemento [m²/K.W]
            self.resistance = None

class MaterialesDB(object):
    """Base de datos de Materiales"""

    def __init__(self, filename='DB.ini'):
        """Inicialización de la BBDD de Cerramientos

        :param str filename: nombre del archivo desde el que cargar la base de datos
        """
        #: nombre del archivo desde el que cargar la base de datos (str)
        self.filename = filename
        #: diccionario de configuración (nombre, ...) (dict)
        self.config = None
        #: lista de nombres de materiales de la BBDD (list)
        self.nombres = []
        #: lista de nombres de grupos de la BBDD (list)
        self.nombresgrupos = []
        #: diccionario de materiales de la BBDD por nombre de material (dict)
        self.materiales = {}
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

    def loadmaterialesdb(self, filename=None):
        """Lee base de datos de materiales en formato ConfigObj de archivo

        :param str filename: nombre del archivo desde el que cargar la base de datos
        """
        def unescape(data):
            """Unescape &amp;, &lt;, and &gt; in a string of data."""
            k = data.replace("&lb;", "[").replace("&rb;", "]")
            return k.replace("&amp;", "&")

        if not filename:
            if self.filename:
                filename = self.filename
            else:
                raise ValueError, "No se ha especificado un archivo"
        config = configobj.ConfigObj(filename, encoding='utf-8',
                                     raise_errors=True)
        # Lee valores de configuración de la base de datos si existe
        if 'config' in config:
            self.config = config['config'].copy()
            del config['config']
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
