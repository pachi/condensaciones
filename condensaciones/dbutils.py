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
"""Funciones para leer bases de datos de materiales tipo LIDER y crear un
diccionario con sus datos.
"""

import codecs

KEYWORDS = ('TEMPLARY',)
SECTIONDELIMITER = '+++'
COMMENT = '$'
DEFAULT_SECTION = u'default'

def parseblock(block):
    _dict = {}
    _nombre, _propiedad = block[0].split('=')
    _dict[_propiedad.strip(" \"")] = _nombre.strip(" \"")
    for line in block[1:]:
        _prop, _dato = line.split('=')
        _dict[_prop.strip(" \"")] = _dato.strip(" \"")
    return _dict

def parsefile(file):
    #TODO: ampliar a listas de archivos para combinar bases de datos (eg. LIDER
    #+ URSA)
    lines = codecs.open(file, 'rb', 'iso-8859-1') #Las BBDD están en iso-8859-1
    datos = {}
    block = []
    materiales = []
    section = DEFAULT_SECTION

    for line in lines:
        line = line.strip()
        if line.startswith(COMMENT) or line == "":
            continue
        elif line.startswith(KEYWORDS):
            continue
        elif line.startswith(SECTIONDELIMITER):
            newsection = lines.next().strip()
            datos[newsection] = []
            lines.next() #el formato es delimitador // nombre // delimitador
            if section in datos:
                datos[section].append(materiales[:])
            else:
                datos[section] = materiales[:]
            section = newsection
            materiales = []
            continue
        else:
            if line.startswith('..'):
                materiales.append(parseblock(block))
                block = []
            else:
                block.append(line)
    if materiales is not []: #si solamente hay sección default
        datos[section] = materiales[:]
    return datos

def db2data(files):
    _resultado = {}
    if not isinstance(files, (tuple, list)):
        files = [files]
    for _f in files:
        #print "Procesando %s" % _f
        _data = parsefile(_f)
        for _material in _data[DEFAULT_SECTION]:
            _nombre = _material['MATERIAL']
            _resultado[_nombre] = _material.copy()
    return _resultado

if __name__ == "__main__":
    import sys
    import util

    if len(sys.argv) < 2:
        argfile = None
    else:
        argfile = sys.argv[1:]
    files = argfile or util.get_resource('../data/BDCatalogo.bdc')
    db = db2data(files)
    print u"%i materiales generados" % len(db)

    if not isinstance(files, (tuple, list)):
        files = [files]
    for f in files:
        datos = parsefile(f)
        print u"Archivo: %s" % f
        print u"Secciones:", datos.keys().sort()
        print (u"%i secciones y %i materiales en la sección "
               u"'default'") % (len(datos), len(datos['default']))
        for index, material in enumerate(datos['default']):
            print material['MATERIAL']
        for dato in db2data(f).keys():
            print dato
        print db2data(f)
