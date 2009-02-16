#!/usr/bin/env python
#encoding: iso-8859-15
"""Funciones para leer bases de datos de materiales tipo LIDER y crear un
diccionario con sus datos.
"""
KEYWORDS = ('TEMPLARY',)
SECTIONDELIMITER = '+++'
COMMENT = '$'
DEFAULT_SECTION = 'default'

def parseblock(block):
    _dict = {}
    _nombre, _propiedad = block[0].split('=')
    _dict[_propiedad.strip(" \"")] = _nombre.strip(" \"")
    for line in block[1:]:
        _prop, _dato = line.split('=')
        _dict[_prop.strip(" \"")] = _dato.strip(" \"")
    return _dict

def parsefile(file):
    #TODO: ampliar a listas de archivos para combinar bases de datos (eg. LIDER + URSA)
    lines = open(file, 'rb')
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
    if materiales is not []: #si solamente hay secci�n default
        datos[section] = materiales[:]
    return datos

def db2datos(files):
    _resultado = {}
    if not isinstance(files, (tuple, list)):
        files = [files]
    for file in files:
        #print "Procesando %s" % file
        datos = parsefile(file)
        for material in datos[DEFAULT_SECTION]:
            _nombre = material['MATERIAL']
            _resultado[_nombre] = material.copy()
    return _resultado

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        argfile = None
    else:
        argfile = sys.argv[1:]
    files = argfile or "db/PCatalogo.bdc"
    db = db2datos(files)
    print "%i materiales generados" % len(db)

#     for file in files:
#         datos = parsefile(file)
#         print "Archivo: %s" % file
#         print "Secciones:", datos.keys().sort()
#         print "%i secciones y %i materiales en la secci�n 'default'" % (len(datos), len(datos['default']))
#
#     for index, material in enumerate(datos['default']):
#         print material['MATERIAL']
#     for dato in b2datos(file).keys():
#         print dato
#     print b2datos(file)
