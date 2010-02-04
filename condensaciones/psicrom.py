#!/usr/bin/env python
#encoding: utf-8
#
#   condensaciones.py
#   Programa de cálculo de condensaciones según CTE
#
#   Copyright (C) 2007-2010 por Rafael Villar Burke <pachi@rvburke.com>
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
"""Relaciones y cálculos psicrométricos según CTE DB-HE G.3

Relaciones psicrométricas básicas:

- Presión de saturación
- Presión de vapor
- Humedad relativa interior

Cálculos psicrométricos:
- Temperatura de localidad en función de la temperatura de la capital de
  provincia.
- Presión de saturación de una localidad en función de la diferencia de
  altitud respecto a la capital de provincia.
- Humedad relativa de una localidad en función de la diferencia de altitud
  respecto a la capital de provincia.
- Tasa de transferencia de vapor en un cerramiento.
- Humedad relativa interior del mes de enero, dada la higrometría, humedad
  relativa y temperaturas, según ISO EN 13788:2002.
- Humedad relativa interior del mes de enero, dada la humedad relativa,
  temperaturas y renovación de aire, según CTE.
- Humedad relativa interior del mes de enero dada la higrometría, según CTE.
"""

# TODO: Hay que generalizar el cálculo de la presión exterior para la localidad
# concreta? Sería mejor cambiar psatloc, temploc y hrloc a funciones que tengan
# delta_alt = None y se usen siempre?

import sys
import math

def psat(temp):
    """Presión de saturación del aire húmedo [Pa]
    
    temp - temperatura del aire [ºC]
    """
    if temp > 0.0:
        return 610.5 * math.exp(17.269 * temp / (237.3 + temp))
    else:
        return 610.5 * math.exp(21.875 * temp / (267.5 + temp))

def pvapor(temp, humedad):
    """Presión de vapor del aire húmedo [Pa]
    
    temp - Temperatura del aire [ºC]
    humedad - humedad relativa del aire [%]
    """
    return (humedad / 100.0) * psat(temp)

def temploc(temp, deltah):
    """Temperatura de una localidad no capital de provincia [ºC]
    
    Es función de la temperatura y diferencia de altitud con la capital de
    provincia.
    
    temp - temperatura media exterior de la capital para el mes dado [ºC]
    deltah - altura de la localidad sobre la de la capital [m]
    """
    return temp - 1.0 * deltah / 100.0

def psatloc(temp, deltah):
    """Presión de saturación en una localidad no capital de provincia [Pa]
    
    Es función de la temperatura y diferencia de altitud con la capital de
    provincia.
    
    temp - temperatura media exterior de la capital para el mes dado [ºC]
    deltah - altura de la localidad sobre la de la capital [m]
    """
    return psat(temploc(temp, deltah))

def hrloc(temp, humedad, deltah):
    """Humedad relativa para la localidad no capital de provincia [%]
    
    Es función de la temperatura, humedad y diferencia de nivel con la capital
    de provincia [%].
    
    temp - temperatura media exterior de la capital para el mes dado [ºC]
    humedad - humedad relativa media de la capital para el mes dado [%]
    deltah - altura de la localidad sobre la de la capital [m]
    
    Si la altura fuese negativa se debería tomar como altura la de la capital.
    """
    if deltah < 0.0:
        deltah = 0
    return 100.0 * (pvapor(temp, humedad) / psatloc(temp, deltah))

def g(pe, pi, Se, Si):
    """Tasa de transferencia de vapor a través del cerramiento [g/m2.s]
    
    Resulta útil para calcular condensada o evaporada entre interfases.
    
    pe - presión de vapor exterior [Pa]
    pi - presión de vapor interior [Pa]
    Se - espesor de aire equivalente en pe [m]
    Si - espesor de aire equivalente en pi [m]
    delta0 - permeabilidad al vapor de agua del aire en relación a la presión
             parcial de vapor [g/m.s.Pa (por unidad de tiempo)]
    """
    delta0 = 2.0 * 10.0**(-7.0) #delta0 -> [g/(m.s.Pa)]
    if Si == Se:
        return sys.maxint
    return delta0 * (pi - pe) / (Si - Se) #[g/(m².s)]

def hrintISO(text, tsint, hrext, higrometria):
    """Humedad relativa interior [%] del mes de enero
    
    Es función del ritmo de producción de humedad interior (higrometría),
    definida según ISO EN 13788:2002
    
    text - Temperatura exterior [ºC]
    tsint - Temperatura superficial interior [ºC]
    hrext - Humedad relativa exterior [%]
    higrometria - nivel del ritmo de producción de la humedad interior
        Higrometría 1 (zonas de almacenamiento): delta_p = 270 Pa
        Higrometría 2 (oficinas, tiendas): delta_p = 540 Pa
        Higrometría 3 (viviendas residencial): delta_p = 810 Pa
        Higrometría 4 (viv. alta ocupación, rest., cocinas): delta_p = 1080 Pa
        Higrometría 5 (lavanderías, piscinas, restaurantes): delta_p = 1300 Pa
    """
    # delta_p: exceso de presión interna
    if higrometria == 1:
        if text <= 0.0:
            delta_p = 270.0
        elif text < 20.0:
            delta_p = 270.0 - 13.5 * (20.0 - text)
        else:
            delta_p = 0.0
    elif higrometria == 2:
        if text <= 0.0:
            delta_p = 540.0
        elif text < 20.0:
            delta_p = 540.0 - 27.0 * (20.0 - text)
        else:
            delta_p = 0.0
    elif higrometria == 3:
        if text <= 0.0:
            delta_p = 810.0
        elif text < 20.0:
            delta_p = 810.0 - 40.5 * (20.0 - text)
        else:
            delta_p = 0.0
    elif higrometria == 4:
        if text <= 0.0:
            delta_p = 1080.0
        elif text < 20.0:
            delta_p = 1080.0 - 54.0 * (20.0 - text)
        else:
            delta_p = 0.0
    else:
        delta_p = 1300.0
    return (100.0 * (pvapor(text, hrext) + delta_p) / psat(tsint))

def hrintCTE(text=None, tint=None, tsint=None,
                    hrext=None, G=None, V=None, n=None,
                    higrometria=None):
    """Humedad relativa interior [%] del mes de enero
    
    Es función del ritmo de producción de humedad interior y la tasa de
    renovación de aire o, alternativamente, la higrometría, según se define
    en el CTE.
    
    Útil para el cálculo de condensaciones superficiales.

    text - temperatura exterior [ºC]
    tint - temperatura interior [ºC]
    tsint - temperatura superficial interior [ºC]
    hrext - Humedad relativa del aire exterior [%]
    G - ritmo de producción de la humedad interior [kg/h]
    V - Volumen de aire del local [m³]
    n - tasa renovación de aire [h^-1]
    
    higrometria - nivel del ritmo de producción de la humedad interior
        Higrometría 1 (zonas de almacenamiento)
        Higrometría 2 (oficinas, tiendas)
        Higrometría 3 (viviendas residencial): HR = 55%
        Higrometría 4 (viv. alta ocupación, rest., cocinas): HR = 62%
        Higrometría 5 (lavanderías, piscinas, restaurantes): HR = 70%
    """
    if higrometria:
        if higrometria in (3, 4, 5):
            return {3: 55.0, 4:62.0, 5:70.0}[higrometria]
        else:
            raise ValueError("Higrometría fuera de rango: %s" % higrometria)
    if None in (text, tint, tsint, hrext, G, V, n):
        raise ValueError("Faltan parámetros")
    # Exceso de humedad interior:
    deltav = G / (n * V)
    # Exceso de presión de vapor interna:
    # Constante de gas para el vapor de agua Rv = 462 [Pa.m³/K.kg]
    delta_p = 462.0 * deltav * (tint + text) / 2.0
    return (100.0 * (pvapor(text, hrext) + delta_p) / psat(tsint))
