#!/usr/bin/env python
#encoding: iso-8859-15

from util import get_resource
import dbutils

CATALOGOPACHI = get_resource('..', 'db/PCatalogo.bdc')
CATALOGOCALENER = get_resource('..', 'db/BDCatalogo.bdc')
CATALOGOURSA = get_resource('..', 'db/Catalogo_URSA.BDC')

materiales = dbutils.db2datos([CATALOGOPACHI, CATALOGOCALENER, CATALOGOURSA])

def tipo(nombre):
    return materiales[nombre]['TYPE']

def conductividad(nombre):
    return float(materiales[nombre]['CONDUCTIVITY'])

def resistencia(nombre):
    return float(materiales[nombre]['RESISTANCE'])

def difusividad(nombre):
    return float(materiales[nombre]['VAPOUR-DIFFUSIVITY-FACTOR'])
