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
"""Gestión de bases de data de materiales LIDER

Permite leer, interpretar y crear un diccionario de acceso a los materiales y
sus propiedades.
"""

import codecs

#===============================================================================
# Clases base para representar elementos de las BBDD de Lider
#===============================================================================
class Material(object):
    """Material tipo"""
    klass = 'MATERIAL'
    def __init__(self, name, group, mtype, mu):
        """Inicialización de datos generales
        
        name - nombre del material
        group - grupo genérico al que pertenece el material
        mtype - tipo de material [RESISTANCE|PROPERTIES|SHADING-COEF]
        mu - difusividad al vapor de agua
        """
        self.name = name
        self.group = group
        self.type = None
        # Difusividad al vapor de agua del material
        self.mu = mu
        #self.name_calener = ''
        #self.image = 'asfalto.bmp'
        #self.library = False

class PropertiesMaterial(Material):
    """Material de tipo Properties"""
    def __init__(self, name, group, mu, conductivity, thickness=None):
        """Inicialización de datos generales
        
        conductivity - conductividad térmica [W/m.K]
        thickness - espesor del elemento [m]
        """
        Material.__init__(self, name, group, type, mu)
        self.type = 'PROPERTIES'
        self.thickness = thickness #[m]
        self.conductivity = conductivity #[W/m.K]
        #self.density = 1#properties
        #self.specific_heat = 1#properties
        #self.thickness_min =  .04#properties
        #self.thickness_max =  .06#properties

class ResistanceMaterial(Material):
    """Material de tipo Resistance"""
    def __init__(self, name, group, mu, resistance):
        """Inicialización de datos generales
        
        resistance - resistencia térmica [m²/K.W]
        """
        Material.__init__(self, name, group, type, mu)
        self.type = 'RESISTANCE'
        self.resistance = resistance #[m²/K.W]
        #self.thickness_change = False#resistance

#===============================================================================
# Funciones para transformar BBDD de Lider a objetos Python
#===============================================================================

DEFAULT_SECTION = u'default'

def parseblock(block):
    """Divide bloques de la base de datos recibidos como listas de datos
    
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

def db2data(dbfiles):
    """Convierte una lista de archivos de bases de datos a diccionario de datos
    
    El diccionario está indexado por el nombre del material e incluye el resto
    de datos extraídos.
    """ 
    materials = {}
    groups = {}
    if not isinstance(dbfiles, (tuple, list)):
        dbfiles = [dbfiles]
    for _f in dbfiles:
        #print "Procesando %s" % _f
        rawmaterials = parsefile(_f)
        for rm in rawmaterials[DEFAULT_SECTION]:
            mtype = rm['TYPE'].strip()
            name = rm['NAME'].strip()
            group = rm['GROUP'].strip()
            mu = float(rm['VAPOUR-DIFFUSIVITY-FACTOR'].strip())
            if mtype == 'PROPERTIES':
                conductivity = float(rm['CONDUCTIVITY'].strip())
                thickness = float(rm['THICKNESS'].strip())
                mat = PropertiesMaterial(name, group, mu,
                                         conductivity, thickness)
            elif mtype == 'RESISTANCE':
                resistance = float(rm['RESISTANCE'].strip())
                mat = ResistanceMaterial(name, group, mu, resistance)
            groups.setdefault(group, set()).add(name)
            materials[name] = mat
    return materials, groups
