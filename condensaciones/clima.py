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
"""Clima - Clase para la modelización de un ambiente tipo."""

import configobj

class Clima(object):
    """Clase para almacenamiento de datos de temperatura, humedad, etc"""
    def __init__(self, temp=20.0, HR=55.0):
        """Inicialización de datos
        
        :type temp: int or float
        :param temp: temperatura [ºC]
        :type HR: int or float
        :param HR: Humedad relativa [%]
        """
        self.temp = float(temp)
        self.HR = float(HR)

#===============================================================================
# Funciones de E/S de datos de clima
#===============================================================================

def unescape(data):
    """Unescape &amp;, &lt;, and &gt; in a string of data."""
    return data.replace("&lb;", "[").replace("&rb;", "]").replace("&amp;", "&")

def escape(data):
    """Escape &, [ and ] a string of data."""
    return data.replace("&", "&amp;").replace("[", "&lb;").replace("]", "&rb;")

def loadclimadb(filename='ClimaCTE.ini'):
    """Lee base de datos de climas en formato ConfigObj

    Devuelve:
        - diccionario de nombres de localidades con lista de instancias de
          Clima ordenadas por número de mes (enero = 1, diciembre = 12)
        - lista ordenada de nombres de localidades
    """
    config = configobj.ConfigObj(filename, encoding='utf-8', raise_errors=True)
    climas, cnames = {}, []
    if 'config' in config:
        dbconf = config['config']
        del config['config']
    else:
        dbconf = None
    for section in config:
        s = config[section]
        nombre = unescape(section)
        tempdata = s['T']
        hrdata = s['HR']
        if isinstance(tempdata, list):
            if len(tempdata) != len(hrdata):
                raise ValueError, "Valores no coincidentes de temperatura y" \
                " HR en %s (%i vs %i)" % (nombre, len(tempdata), len(hrdata))
            elif len(tempdata) == 12:
                climas[nombre] = [Clima(t, hr)
                                  for t, hr in zip(tempdata, hrdata)]
            else:
                raise ValueError, "Número erróneo de valores en %s" % nombre
        else:
            climas[nombre] = [Clima(tempdata, hrdata)]
        cnames.append(nombre)
    return climas, cnames, dbconf

def saveclimasdb(climas, nameorder=None, configdata=None,
                 filename='ClimaCTE.ini'):
    """Guarda base de datos de climas en formato ConfigObj
    
    Parámetros:
        climas     - diccionario de localidades con lista de instancias de
                     clima.
        cnames     - lista opcional de nombres que define el orden en la base
                     de datos.
        config     - Diccionario opcional con valores de configuración.
    """
    config = configobj.ConfigObj(filename, encoding='utf-8', raise_errors=True)
    if not nameorder:
        nameorder = climas.keys()
        nameorder.sort()
    removed = [k for k in config.keys() if not (k in nameorder or
                                                k == u'config')]
    if removed:
        for k in removed:
            del config[k]
    if u'config' not in config:
        config['config'] = {}
    if configdata:
        for key in configdata:
            config['config'][key] = configdata[key]
    for name in nameorder:
        if name not in climas:
            raise ValueError, "Nombre desconocido: %s" % name
        c = climas[name]
        ename = escape(name)
        sect = config[ename] 
        sect = {}
        config.comments[ename] = '#'
        sect['T'] = [_item.T for _item in c]
        sect['HR'] = [_item.HR for _item in c] 
    config.write()
