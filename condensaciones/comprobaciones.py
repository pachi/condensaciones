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
        raise ValueError('La temperatura exterior e interior es igual')
    return (tempsimin(hrint) - tempext) / (tempint - tempext)

def testcondensas(cerr, temp_ext, temp_int, HR_int):
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
    # con HR=55%, 62%, 70%. Además, impone condiciones exteriores
    # correspondientes al mes de enero y temperatura interior igual a 20ºC.
    return fRsi(cerr.U) < fRsimin(temp_ext, temp_int, HR_int)

def calculaintersticiales(cerr, ti, hri, climasext):
    """Devuelve lista de condensaciones intersticiales para cada interfase
    
    Se calcula usando como clima exterior cada uno de los elementos en
    self.climaslist y condiciones interiores ti, hri.
    
    Para cada clima exterior devuelve, una lista de tuplas formado por el
    índice de la interfase y la cantidad condensada para cada interfase
    con condensación intersticial.
    
    [[(1, 2.5), (3, 3.0), ..., (i, gi)], ..., mesj]
    """
    # Localizar primer mes sin condensaciones previas
    prevcondensa = True
    for startindex, climaj in enumerate(climasext):
        cond = cerr.condensacion(climaj.temp, ti, climaj.HR, hri)
        if not cond:
            prevcondensa = False
        elif not prevcondensa:
            break
    # Si agotamos la lista sin condensaciones volvemos al principio
    if startindex == (len(climasext) - 1) and not cond:
        startindex = 0
    # Calculamos condensaciones en orden
    glist = []
    cond = []
    for i in range(startindex, len(climasext)) + range(0, startindex):
        climaj = climasext[i]
        cond = cerr.condensacion(climaj.temp, ti, climaj.HR, hri, cond)
        glist.append(cond)
    # Reordenar lista y guardar
    return glist[-startindex:] + glist[:-startindex]

def gperiodo(glist, i=0):
    """Cantidad de condensación total de un periodo i en [g/m²mes]
    
    :param list glist: Lista de condensaciones por interfase en tuplas de
        índice y cantidad, tal como devuelve la función calculaintersticiales
    :param int i: Índice del periodo deseado
    :returns: Cantidad acumulada condensada durante el periodo
    :rtype: float
    """
    if i < len(glist):
        g = glist[i]
        totalg = 0.0 if not g else sum(zip(*g)[1])
    else:
        totalg = 0.0
    return totalg

def gmeses(glist):
    """Lista de condensaciones acumuladas en todas las interfases por periodos
    
    :param list glist: Lista de condensaciones por interfases y periodos
    :returns: Lista de condensaciones acumuladas
    :rtype: list
    """
    return [gperiodo(glist, i) for i in range(len(glist))]

def testcondensai(cerr, temp_ext, temp_int, HR_ext, HR_int):
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
    #TODO: Mover aquí appmodel.calculaintersticiales como función a la que se
    #TODO: le entrega una lista de climas exteriores y un cerramiento y
    #TODO: calcula la existencia de condensaciones intersticiales
    g = cerr.condensacion(temp_ext, temp_int, HR_ext, HR_int)
    gq = zip(*g)[1] if g else []
    condensa = (sum(gq) > 0.0)
    return condensa

def testcondensaciones(cerr, temp_ext, temp_int, HR_ext, HR_int):
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
    ci = testcondensai(cerr, temp_ext, temp_int, HR_ext, HR_int)
    cs = testcondensas(cerr, temp_ext, temp_int, HR_int)

    return ci or cs
