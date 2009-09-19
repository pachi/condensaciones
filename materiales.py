#!/usr/bin/env python
#encoding: iso-8859-15

import dbutils

materiales = dbutils.db2datos(['db/PCatalogo.bdc', 'db/BDCatalogo.bdc', 'db/Catalogo_URSA.BDC'])

def tipo(nombre):
    return materiales[nombre]['TYPE']

def conductividad(nombre):
    return float(materiales[nombre]['CONDUCTIVITY'])

def resistencia(nombre):
    return float(materiales[nombre]['RESISTANCE'])

def difusividad(nombre):
    return float(materiales[nombre]['VAPOUR-DIFFUSIVITY-FACTOR'])
