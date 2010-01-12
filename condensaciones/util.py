#!/usr/bin/env python
#encoding: utf-8

import os
import colorsys

def get_resource(*path_list):
    "Localiza un recurso del proyecto en base al directorio base del paquete"
    APPROOT = os.path.dirname(__file__)
    return os.path.abspath(os.path.join(APPROOT, *path_list))

def stringify(alist, prec):
    _format = '%%.%if' % prec
    return "[" + ", ".join([_format % item for item in alist]) + "]"

def colorlist(steps):
    clist = []
    salto_color = 0.0
    for i in range(steps):
        color = colorsys.hls_to_rgb(salto_color, .6, .8)
        clist.append(color)
        salto_color += 1.0 / steps
    return clist

def colores_capas(lista_capas):
    capas_distintas = set(lista_capas)
    colordict = {}
    for nombre, color in zip(capas_distintas, colorlist(len(capas_distintas))):
        colordict[nombre] = color
    return colordict

def add_margin(lista, margen_lateral=0.025):
    "Añade un margen a una lista"
    return ([lista[0] - margen_lateral] + lista + [lista[-1] + margen_lateral])