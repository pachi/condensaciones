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
"""Gestión de bases de data de materiales LIDER

Permite leer, interpretar y crear un diccionario de acceso a los materiales y
sus propiedades.
"""

import codecs

DEFAULT_SECTION = u'default'

def parseblock(block):
    """Divide bloques de la base de datos recibidos como listas de datos
    
    La primera línea indica el nombre del elemento (e.g. "Ladrillo hueco
    doble"), seguido de su tipo (e.g. MATERIAL).
    
    Las siguientes líneas indican una propiedad (e.g. TYPE, THICKNESS, NAME,
    ...) y un valor (e.g. MATERIAL, 0.001, "Ladrillo hueco doble").
    
    Los nombres y tipos, así como propiedades y valores están separados por
    símbolos '='. Las cadenas de texto se marcan entre comillas dobles.
    
    Cada bloque se termina con un par de puntos ('..').
    
    Ejemplo de bloque:
    
    "B_Vapor Z3 (d_1mm)" = MATERIAL
    TYPE           = PROPERTIES
    THICKNESS      = 0.001
    CONDUCTIVITY   = 500
    DENSITY        = 1
    SPECIFIC-HEAT  = 1
    VAPOUR-DIFFUSIVITY-FACTOR = 2030
    NAME           = "B_Vapor Z3 (d_1mm)"
    NAME_CALENER   = ""
    GROUP          = "B_VAPOR"
    IMAGE          = "asfalto.bmp"
    LIBRARY        = NO
    ..
    """
    _dict = {}
    _nombre, _propiedad = block[0].split('=')
    _dict[_propiedad.strip(" \"")] = _nombre.strip(" \"")
    for line in block[1:]:
        _prop, _dato = line.split('=')
        _dict[_prop.strip(" \"")] = _dato.strip(" \"")
    return _dict

def parsefile(dbfile):
    """Interpreta secciones de la base de datos
    
    Las bases de data se almacenan con codificación ISO-8859-1 e incluyen los
    siguientes elementos:
    
    Comentarios - Líneas que empiezan por '$'
    Palabras clave - Definen propiedades de la base de data (e.g. TEMPLARY)
    Secciones y subsecciones - El nombre de la sección se coloca entre líneas
                               con símbolos '+++'
    
    Devuelve un diccionario indexado por secciones que contiene un diccionario
    con los materiales de cada sección.
    """
    KEYWORDS = ('TEMPLARY',)
    SECTIONDELIMITER = '+++'
    COMMENT = '$'
    
    lines = codecs.open(dbfile, 'rb', 'iso-8859-1')
    data = {}
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
            data[newsection] = []
            lines.next() #el formato es delimitador // nombre // delimitador
            if section in data:
                data[section].append(materiales[:])
            else:
                data[section] = materiales[:]
            section = newsection
            materiales = []
            continue
        else:
            # Cuando llegamos al final de un bloque forzamos su interpretación
            if line.startswith('..'):
                materiales.append(parseblock(block))
                block = []
            # en caso contrario seguimos añadiendo líneas
            else:
                block.append(line)
    if materiales is not []: #si solamente hay sección default
        data[section] = materiales[:]
    return data

def db2data(dbfiles):
    """Convierte una lista de archivos de bases de datos a diccionario de datos
    
    El diccionario está indexado por el nombre del material e incluye el resto
    de datos extraídos.
    """ 
    _resultado = {}
    if not isinstance(dbfiles, (tuple, list)):
        dbfiles = [dbfiles]
    for _f in dbfiles:
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
