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

"""Módulo para la definición, almacenamiento y recuperación de ambientes
higrotérmicos.
"""

__all__ = ['Clima', 'escape', 'unescape', 'loadclimadb', 'saveclimasdb']

import configobj

class Clima(object):
    """Definición de un ambiente higrotérmico tipo (temperatura, humedad...)

    :param float temp: temperatura [ºC]
    :param float HR: Humedad relativa [%]

    Los parámetros se convierten a float si se reciben como enteros.
    """
    def __init__(self, temp=20.0, HR=55.0):
        """Inicialización de datos"""
        self.temp = float(temp)
        self.HR = float(HR)

#===============================================================================
# Funciones de E/S de datos de clima
#===============================================================================

def escape(data):
    """Codifica &, [ y ] en una cadena de datos.

    :param str data: cadena de datos original
    :returns: cadena de datos codificada
    :rtype: str

    Esta función codifica algunos caracteres de la cadena de datos original
    para permitir su uso seguro en archivos con formato .ini, en donde los
    caracteres codificados no están permitidos para su uso en secciones.

    La función realiza la transformación inversa a :py:func:`unescape`.

    Ejemplo::

        "<5m" -> "&lt;5m"
    """
    return data.replace("&", "&amp;").replace("[", "&lb;").replace("]", "&rb;")

def unescape(data):
    """Decodifica &amp;, &lt;, y &gt; en una cadena de datos.

    :param str data: cadena de datos codificada
    :returns: cadena de datos original
    :rtype: str

    Esta función decodifica una cadena que ha sido transformada para permitir
    el uso seguro de algunos caracteres en archivos con formato .ini.

    La función realiza la transformación inversa a :py:func:`escape`.

    Ejemplo::

        "&lt;5m" -> "<5m"
    """
    return data.replace("&lb;", "[").replace("&rb;", "]").replace("&amp;", "&")

def loadclimadb(filename='ClimaCTE.ini'):
    """Lee una base de datos de climas

    La base de datos proviene de un archivo en formato ConfigObj

    :param str filename: nombre del archivo de la base de datos
    :returns: - diccionario de nombres de localidades con lista de instancias
                de Clima ordenadas por número de mes (enero = 1, diciembre = 12)
              - lista ordenada de nombres de localidades
              - sección de configuración de la base de datos
    :rtype: tuple
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
    """Guarda una base de datos de climas

    La base de datos se almacena en formato ConfigObj

    :param dict climas: contiene lista de instancias de clima para cada
                        localidad
    :param list cnames: lista ordenada de nombres tal como aparecen en la base
                        de datos
    :param dict config: valores de configuración de la base de datos
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
