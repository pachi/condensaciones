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

def temploc(temp, delta_alt):
    """Temperatura de una localidad no capital de provincia [ºC]
    
    Es función de la temperatura y diferencia de altitud con la capital de
    provincia.
    
    temp - temperatura media exterior de la capital para el mes dado [ºC]
    delta_alt - altura de la localidad sobre la de la capital [m]
    """
    return temp - 1.0 * delta_alt / 100.0

def psatloc(temp, delta_alt):
    """Presión de saturación en una localidad no capital de provincia [Pa]
    
    Es función de la temperatura y diferencia de altitud con la capital de
    provincia.
    
    temp - temperatura media exterior de la capital para el mes dado [ºC]
    delta_alt - altura de la localidad sobre la de la capital [m]
    """
    return psat(temploc(temp, delta_alt))

def hrloc(temp, humedad, delta_alt):
    """Humedad relativa para la localidad no capital de provincia [%]
    
    Es función de la temperatura, humedad y diferencia de nivel con la capital
    de provincia [%].
    
    temp - temperatura media exterior de la capital para el mes dado [ºC]
    humedad - humedad relativa media de la capital para el mes dado [%]
    delta_alt - altura de la localidad sobre la de la capital [m]
    
    Si la altura fuese negativa se debería tomar como altura la de la capital.
    """
    if delta_alt < 0.0: delta_alt = 0
    return 100.0 * (pvapor(temp, humedad) / psatloc(temp, delta_alt))

def tasatransferenciavapor(pe, pi, Se, Si):
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

def calculahrinthigrometriaISO(temp_ext, temp_sint, hrext, higrometria):
    """Humedad relativa interior [%] del mes de enero
    
    Es función del ritmo de producción de humedad interior (higrometría),
    definida según ISO EN 13788:2002
    
    temp_ext - Temperatura exterior [ºC]
    temps_int - Temperatura superficial interior [ºC]
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
        if temp_ext <= 0.0:
            delta_p = 270.0
        elif temp_ext < 20.0:
            delta_p = 270.0 - 13.5 * (20.0 - temp_ext)
        else:
            delta_p = 0.0
    elif higrometria == 2:
        if temp_ext <= 0.0:
            delta_p = 540.0
        elif temp_ext < 20.0:
            delta_p = 540.0 - 27.0 * (20.0 - temp_ext)
        else:
            delta_p = 0.0
    elif higrometria == 3:
        if temp_ext <= 0.0:
            delta_p = 810.0
        elif temp_ext < 20.0:
            delta_p = 810.0 - 40.5 * (20.0 - temp_ext)
        else:
            delta_p = 0.0
    elif higrometria == 4:
        if temp_ext <= 0.0:
            delta_p = 1080.0
        elif temp_ext < 20.0:
            delta_p = 1080.0 - 54.0 * (20.0 - temp_ext)
        else:
            delta_p = 0.0
    else:
        delta_p = 1300.0
    return (100.0 * (pvapor(temp_ext, hrext) + delta_p) / psat(temp_sint))

def calculahrintCTE(temp_ext=None, temp_int=None, temp_sint=None,
                    hrext=None, G=None, V=None, n=None,
                    higrometria=None):
    """Humedad relativa interior [%] del mes de enero
    
    Es función del ritmo de producción de humedad interior y la tasa de
    renovación de aire o, alternativamente, la higrometría, según se define
    en el CTE.
    
    Útil para el cálculo de condensaciones superficiales.

    temp_ext - temperatura exterior [ºC]
    temp_int - temperatura interior [ºC]
    temp_sint - temperatura superficial interior [ºC]
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
    if None in (temp_ext, temp_int, temp_sint, hrext, G, V, n):
        raise ValueError("Faltan parámetros")
    # Exceso de humedad interior:
    delta_v = G / (n * V)
    # Exceso de presión de vapor interna:
    delta_p = 462.0 * delta_v * (temp_int + temp_ext) / 2.0
    return (100.0 * (pvapor(temp_ext, hrext) + delta_p) / psat(temp_sint))

if __name__ == "__main__":
    from datos_ejemplo import climae, climai

    higrometria = 3
    # Datos constructivos
    Rs_ext = 0.04
    Rs_int = 0.13
    # datos calculados
    temp_sint = 19.0330684375
    G = 0.55 #higrometría 3
    volumen = 10 #m3
    n = 1 #[h^-1]

    hrint = calculahrinthigrometriaISO(climae.temp, temp_sint,
                                    climae.HR, higrometria=higrometria) #65.86%
    hrintCTE = calculahrintCTE(climae.temp, climai.temp, temp_sint,
                               climae.HR, G, volumen, n)
    hrintCTE2 = calculahrintCTE(higrometria=3)
    g_total = tasatransferenciavapor(1016.00114017, 1285.32312909,
                                     0.0, 2.16) #0,0898 g/m2.s

    print u"Humedad relativa interior para higrometría 3: %.2f" % hrint #65.86%
    print (u"Humedad relativa interior para V=%.2f, G=%.2f, n=%.2f (CTE): "
           u"%.2f") % (volumen, G, n, hrintCTE) #63.89%
    print (u"Humedad relativa interior para higrometría 3 (CTE): "
           u"%.2f") % hrintCTE2 #55.00%
    print (u"\tTasa de transferencia de vapor "
           u"%.4f x 10^-3[g/(h.m2)]") % (g_total * 3600.0,) #0,0898 g/m2.s