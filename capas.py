#!/usr/bin/env python
#encoding: iso-8859-15
import math

def nombre_capas(capas):
    return [nombre for nombre, e, mu, K in capas]

def R_capas(capas):
    return [e / K for nombre, e, mu, K in capas]

def S_capas(capas):
    return [e * mu for nombre, e, mu, K in capas]

def R_total(capas, Rs_ext, Rs_int):
    return Rs_ext + sum(R_capas(capas)) + Rs_int

def calculaU(capas, Rs_ext, Rs_int):
    """Transmitancia térmica del cerramiento"""
    return 1.0 / R_total(capas, Rs_ext, Rs_int)


