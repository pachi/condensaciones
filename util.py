#!/usr/bin/env python
#encoding: iso-8859-15

import colorsys

def stringify(list, prec):
    format = '%%.%if' % prec
    return "[" + ", ".join([format % item for item in list]) + "]"

def colorlist(steps):
    clist =[]
    salto_color = 0.0
    for i in range(steps):
        color = colorsys.hls_to_rgb(salto_color, .6, .8)
        clist.append(color)
        salto_color += 1.0/steps
    return clist

def colores_capas(lista_capas):
    capas_distintas = set(lista_capas)
    colordict = {}
    for nombre, color in zip(capas_distintas, colorlist(len(capas_distintas))):
        colordict[nombre] = color
    return colordict
