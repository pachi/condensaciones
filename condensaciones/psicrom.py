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
"""Relaciones psicrométricas"""

# TODO: Hay que generalizar el cálculo de la presión exterior para la localidad
# concreta? Sería mejor cambiar psatloc, temploc y hrloc a funciones que tengan
# delta_alt = None y se usen siempre?

import sys
import math

def psat(temp):
    """Presión de saturación - temp en ºC"""
    if temp > 0.0:
        return 610.5 * math.exp(17.269 * temp / (237.3 + temp))
    else:
        return 610.5 * math.exp(21.875 * temp / (267.5 + temp))

def pvapor(temp, humedad):
    """Presión de vapor - temp en ºC y humedad en tanto por uno.
        temp - temperatura media exterior para el mes dado
        humedad - humedad relativa media para el mes dado.
    """
    return (humedad / 100.0) * psat(temp)

def temploc(temp, delta_alt):
    """Temperatura de la localidad en función de la temperatura de
    la capital de provincia y la diferencia de altitud entre ellas.
        temp - temperatura media exterior de la capital para el mes dado
        delta_alt - altura de la localidad sobre la de la capital.
    """
    return temp - 1.0 * delta_alt / 100.0

def psatloc(temp, delta_alt):
    """Presión de saturación en una localidad situada a una altitud
    distinta a la capital de provincia.
        temp - temperatura media exterior de la capital para el mes dado
        delta_alt - altura de la localidad sobre la de la capital.
    """
    return psat(temploc(temp, delta_alt))

def hrloc(temp, humedad, delta_alt):
    """Humedad relativa para la localidad situada a una diferencia
    de altitud dada sobre la capital de provincia.
        temp - temperatura media exterior de la capital para el mes dado
        humedad - humedad relativa media de la capital para el mes dado
        delta_alt - altura de la localidad sobre la de la capital.
    """
    return pvapor(temp, humedad) / ((psatloc(temp, delta_alt) * 
                                     temploc(temp, delta_alt)))

def tasatransferenciavapor(pe, pi, Se, Si):
    """Tasa de transferencia de vapor a través del cerramiento g/m2.s
    Sirve para calcular condensada o evaporada entre interfases.
        pe - presión de vapor exterior
        pi - presión de vapor interior
        Se - espesor de aire equivalente en pe
        Si - espesor de aire equivalente en pi
        delta0 -permeabilidad al vapor de agua del aire en relación a la
            presión parcial de vapor (en g/m.s.Pa)x(tiempo)
    """
    delta0 = 2.0 * 10.0**(-7.0) #delta0 -> [g/(m.s.Pa)]
    if Si == Se:
        return sys.maxint
    return delta0 * (pi - pe) / (Si - Se) #g/(m2.s)

def calculahrinthigrometria(temp_ext, temp_sint, hrext, higrometria):
    """Humedad relativa interior del mes de enero, dado el ritmo
    de producción de humedad interior según ISO EN 13788:2002
    higrometría - ritmo de producción de la humedad interior
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

def calculahrintCTE(temp_ext, temp_int, temp_sint, hrext, G, volumen, n):
    """Humedad relativa interior del mes de enero, dado el ritmo
    de producción de humedad interior y la tasa de renovación de aire,
    para el cálculo de condensaciones superf.
    temp_ext - temperatura exterior
    temp_int - temperatura interior
    temp_sint - temperatura superficial interior
    n - tasa renovación de aire [h^-1]
    V - Volumen de aire del local [m^3]
    G - ritmo de producción de la humedad interior [kg/h]
        higrometría 3 o inferior - 55%
        higrometría 4 - 62%
        hogrometría 5 - 70%
    """
    # Exceso de humedad interior:
    delta_v = G / (n * volumen)
    # Exceso de presión de vapor interna:
    delta_p = 462.0 * delta_v * (temp_int + temp_ext) / 2.0
    return (100.0 * (pvapor(temp_ext, hrext) + delta_p) / psat(temp_sint))

def calculahrinthigrometriaCTE(higrometria):
    """Humedad relativa interior del mes de enero, según CTE
    """
    if higrometria == 5:
        return 70.0
    elif higrometria == 4:
        return 62.0
    elif higrometria <= 3:
        return 55.0
    else:
        raise "Higrometría no definida"

if __name__ == "__main__":
    import cerramiento
    from datos_ejemplo import climae, climai, murocapas

    higrometria = 3

    # Datos constructivos
    Rs_ext = 0.04
    Rs_int = 0.13
    muro = cerramiento.Cerramiento("Cerramiento tipo", murocapas,
                                   Rs_ext, Rs_int)
    # datos calculados
    temp_sint = 19.0330684375
    G = 0.55 #higrometría 3
    volumen = 10 #m3
    n = 1 #[h^-1]

    hrint = calculahrinthigrometria(climae.temp, temp_sint,
                                    climae.HR, higrometria=higrometria) #65.86%
    hrintCTE = calculahrintCTE(climae.temp, climai.temp, temp_sint,
                               climae.HR, G, volumen, n)
    hrinthigroCTE = calculahrinthigrometriaCTE(3)
    g_total = tasatransferenciavapor(1016.00114017, 1285.32312909,
                                     0.0, 2.16) #0,0898 g/m2.s

    print u"Humedad relativa interior para higrometría 3: %.2f" % hrint #65.86%
    print (u"Humedad relativa interior para V=%.2f, G=%.2f, n=%.2f (CTE): "
           u"%.2f") % (volumen, G, n, hrintCTE) #63.89%
    print (u"Humedad relativa interior para higrometría 3 (CTE): "
           u"%.2f") % hrinthigroCTE #55.00%
    print (u"\tTasa de transferencia de vapor "
           u"%.4f x 10^-3[g/(h.m2)]") % (g_total * 3600.0,) #0,0898 g/m2.s
