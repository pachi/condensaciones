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
"""Módulo de comprobaciones higrométricas según CTE DB-HE Apéndice G
e ISO 13788:2002"""

import math

def fRsi(U):
    """Factor de temperatura de la superficie interior

    Es aplicable a un cerramiento, partición interior o puentes térmicos
    INTEGRADOS en los cerramientos.

    Se aplica la formulación del CTE DB-HE G.2.1.1

    :param float U: Transmitancia térmica del elemento [W/m²K]
    :returns: factor de temperatura de la superficie interior
    :rtype: float

    .. note::

        Para el cálculo del factor de temperatura de los encuentros de cerramientos
        se deben aplicar los métodos de las normas UNE EN ISO 10 211-1:1995 y
        UNE EN ISO 10 211-2:2002, no implementados en esta función.
    """
    return 1.0 - U * 0.25

def fRsimin(tempext, tempint=20.0, hrint=55.0):
    """Factor de temperatura de la superficie interior mínimo

    Es aplicable a un puente térmico, cerramiento o partición interior.

    Se aplica la formulación del CTE DB-HE G.2.1.2 pero se añaden los límites
    más precisos de la ISO 13788 en cuanto al rango de validez de la presión
    de saturación.

    :param float tempext: Temperatura exterior de la localidad en el mes de enero [ºC]
    :param float tempint: Temperatura del ambiente interior (a falta de otros
                          datos se puede tomar 20ºC) [ºC]
    :param float hrint: Humedad relativa interior [%]
    :returns: factor de temperatura de la superficie interior mínimo
    :rtype: float
    """
    def tempsimin(hrint):
        """Temperatura superficial mínima"""
        # la humedad relativa no debería pasar de 0.80 y psat = pi / HR
        psat = (hrint * 2337.0 / 100.0) / 0.8
        _k = math.log (psat / 610.5)
        if psat >= 610.5: # condición CTE
            temp_si_min = 237.3 * _k / (17.269 - _k)
        else: # condición ISO 13788
            temp_si_min = 265.5 * _k / (21.875 - _k)
        return temp_si_min
    if tempint == tempext:
        raise ValueError('La temperatura exterior e interior son iguales')
    return (tempsimin(hrint) - tempext) / (tempint - tempext)

def condensas(cerr, temp_ext, temp_int, HR_int):
    """Comprueba la condición de existencia de condensaciones superficiales

    Válido para un cerramiento, puente térmico (integrado) o partición
    interior.

    :param Cerramiento cerr: Cerramiento para comprobar
    :param float temp_ext: Temperatura exterior de la localidad en el mes de enero [ºC]
    :param float temp_int: Temperatura del ambiente interior (a falta de otros
                           datos se puede tomar 20ºC) [ºC]
    :param float HR_int: Humedad relativa interior [%]
    :returns: `True` si existen condensaciones superficiales.
    :rtype: float
    """
    # el CTE incluye tablas según zonas y clase de higrometría para fRsimin
    # que están calculadas para la capital más desfavorable de cada zona y
    # con HR=55%, 62%, 70%.
    return fRsi(cerr.U) < fRsimin(temp_ext, temp_int, HR_int)

def condensai(cerr, temp_ext, temp_int, HR_ext, HR_int):
    """Comprueba la condición de existencia de condensaciones intersticiales

    Válido para un cerramiento, puente térmico (integrado) o partición
    interior.

    :param Cerramiento cerr: Cerramiento para comprobar
    :param float temp_ext: Temperatura exterior de la localidad en el mes de enero [ºC]
    :param float temp_int: Temperatura del ambiente interior (a falta de otros
                           datos se puede tomar 20ºC) [ºC]
    :param float HR_ext: Humedad relativa exterior [%]
    :param float HR_int: Humedad relativa interior [%]
    :returns: `True` si existen condensaciones intersticiales.
    :rtype: float
    """
    #TODO: Revisar condensaciones añadiendo condensaciones existentes
    g = cerr.condensacion(temp_ext, temp_int, HR_ext, HR_int)
    gq = zip(*g)[1] if g else []
    condensa = (sum(gq) > 0.0)
    return condensa

def condensaciones(cerr, temp_ext, temp_int, HR_ext, HR_int):
    """Existencia de condensaciones en un cerramiento

    :param Cerramiento cerr: Cerramiento para comprobar
    :param float temp_ext: Temperatura exterior de la localidad en el mes de enero [ºC]
    :param float temp_int: Temperatura del ambiente interior (a falta de otros
                           datos se puede tomar 20ºC) [ºC]
    :param float HR_ext: Humedad relativa exterior [%]
    :param float HR_int: Humedad relativa interior [%]
    :returns: `True` si existen condensaciones superficiales o intersticiales.
    :rtype: float
    """
    ci = condensai(cerr, temp_ext, temp_int, HR_ext, HR_int)
    cs = condensas(cerr, temp_ext, temp_int, HR_int)

    return ci or cs
