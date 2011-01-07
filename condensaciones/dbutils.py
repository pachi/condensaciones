#!/usr/bin/env python
#encoding: utf-8
#
#   condensaciones.py
#   Programa de cálculo de condensaciones según CTE
#
#   Copyright (C) 2009-2011 Rafael Villar Burke <pachi@rvburke.com>
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
"""Gestión de bases de datos de materiales

Permite leer, interpretar y crear un diccionario de acceso a los materiales y
sus propiedades.
"""

import os
import codecs
import configobj
from material import Material

#===============================================================================
# Funciones de conversión desde BBDD de Lider / Calener a BBDD de Materiales
#===============================================================================

def parsefile(dbfile):
    """Interpreta secciones de la base de datos
    
    Devuelve:
        - diccionario de secciones con diccionario de materiales por sección.
    
    El diccionario de materiales contiene diccionario de propiedades.
    
    Las bases de datos se almacenan con codificación ISO-8859-1.
    
    Formato general del archivo
    ---------------------------
    
    Comentarios - Líneas que empiezan por '$'
    Palabras clave - Definen propiedades de la base de data (e.g. TEMPLARY)
    Secciones y subsecciones - El nombre de la sección se coloca entre líneas
                               con símbolos '+++'
    Bloques de datos - Contienen la información de materiales
    
    Formato de bloques de datos
    ---------------------------
    
    La primera línea indica el nombre del elemento (e.g. "Ladrillo hueco
    doble"), seguido de su tipo (e.g. MATERIAL, GLASS-TYPE, NAME-FRAME).
    
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
    KEYWORDS = ('TEMPLARY',)
    SECTIONDELIMITER = '+++'
    COMMENT = '$'
    DEFAULT_SECTION = u'default'
    
    def parseblock(block):
        """Convierte bloque de datos a diccionario indexado por propiedades"""
        _dict = {}
        _nombre, _propiedad = block[0].split('=')
        _dict[_propiedad.strip(" \"")] = _nombre.strip(" \"")
        for line in block[1:]:
            _prop, _dato = line.split('=')
            _dict[_prop.strip(" \"")] = _dato.strip(" \"")
        return _dict

    lines = codecs.open(dbfile, 'rb', 'iso-8859-1')
    data = {}
    block = []
    materiales = []
    currentsection = DEFAULT_SECTION

    for line in lines:
        line = line.strip()
        if line.startswith(COMMENT) or line == "":
            continue
        elif line.startswith(KEYWORDS):
            continue
        elif line.startswith(SECTIONDELIMITER):
            nextsection = lines.next().strip()
            lines.next() #el formato es delimitador // nombre // delimitador
            data[currentsection] = materiales[:]
            materiales = []
            currentsection = nextsection
            continue
        else:
            # Cuando llegamos al final de un bloque forzamos su interpretación
            block = []
            while not line.startswith('..'):
                block.append(line)
                line = lines.next().strip()
            materiales.append(parseblock(block))
    if not data.keys(): # solamente hay sección default 
        data[currentsection] = materiales[:]
    return data

def _db2data(dbfiles):
    """Convierte lista de archivos de BBDD LIDER/CALENER en objetos Python
    
    Devuelve:
        - diccionario de nombres de material con instancias de Material
        - lista de nombres de materiales (por orden de aparición en BBDD)
        - diccionario grupos con conjuntos de nombres de material
    """
    DEFAULT_SECTION = u'default'
    
    materiales, nombres, groups = {}, [], {}
    if not isinstance(dbfiles, (tuple, list)):
        dbfiles = [dbfiles]

    for _f in dbfiles:
        rawmaterials = parsefile(_f)
        for rm in rawmaterials[DEFAULT_SECTION]:
            mtype = rm['TYPE'].strip()
            name = rm['NAME'].strip()
            group = rm['GROUP'].strip()
            mu = float(rm['VAPOUR-DIFFUSIVITY-FACTOR'].strip())
            db = os.path.basename(_f) or ''
            m = Material(name, group, mtype, mu, db)
            if mtype == 'PROPERTIES':
                m.conductivity = float(rm['CONDUCTIVITY'].strip())
                m.thickness = float(rm['THICKNESS'].strip())
                m.density = float(rm['DENSITY'].strip())
                m.specific_heat = float(rm['SPECIFIC-HEAT'].strip())
            elif mtype == 'RESISTANCE':
                m.resistance = float(rm['RESISTANCE'].strip())
            # Propiedades opcionales
            if 'THICKNESS_CHANGE' in rm:
                value = rm['THICKNESS_CHANGE'].strip().upper()
                m.thickness_change = False if 'NO' in value else True
            if 'THICKNESS_MIN' in rm:
                m.thickness_min = float(rm['THICKNESS_MIN'].strip())
            if 'THICKNESS_MAX' in rm:
                m.thickness_max = float(rm['THICKNESS_MAX'].strip())
            groups.setdefault(group, set()).add(name)
            nombres.append(name)
            materiales[name] = m
    return materiales, nombres, groups

def DB2ini(dbfiles, filename='DB.ini'):
    """Guarda bases de datos de formato LIDER/CALENER en formato ConfigObj
    
    Devuelve:
        - número de materiales
        - número de grupos
    """
    def escape(data):
        """Escape &, [ and ] a string of data."""
        data = data.replace("&", "&amp;")
        return data.replace("[", "&lb;").replace("]", "&rb;")
    
    materiales, names, groups = _db2data(dbfiles)
    config = configobj.ConfigObj(filename, encoding='utf-8')

    for name in names:
        mat = materiales[name]
        # Problema con corchetes en nombre de sección mat.name
        section = escape(mat.name)
        config[section] = {}
        config.comments[section].insert(0, '#') #linea en blanco
        config[section]['name'] = mat.name
        config[section]['db'] = mat.db
        config[section]['group'] = mat.group
        config[section]['type'] = mat.type
        config[section]['mu'] = mat.mu
        if hasattr(mat, 'thickness_change'):
            config[section]['thickness_change'] = str(mat.thickness_change)
        if mat.type == 'PROPERTIES':
            config[section]['thickness'] = str(mat.thickness)
            config[section]['conductivity'] = str(mat.conductivity)
            config[section]['density'] = str(mat.density)
            config[section]['specific_heat'] = str(mat.specific_heat)
            if hasattr(mat, 'thickness_min'):
                config[section]['thickness_min'] = str(mat.thickness_min)
            if hasattr(mat, 'thickness_max'):
                config[section]['thickness_max'] = str(mat.thickness_max)
        elif mat.type == 'RESISTANCE':
            config[section]['resistance'] = str(mat.resistance)
    config.write()
    return len(names), len(groups)
