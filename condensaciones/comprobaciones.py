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

import math

def fRsi(U):
    """Factor de temperatura de la superficie interior de un cerramiento,
    partición interior o puentes térmicos INTEGRADOS en los cerramientos.
    """
    return 1.0 - U * 0.25

def fRsimin(tempext, tempint, hrint):
    """Factor de temperatura de la superficie interior mínnimo aceptable de un
    puente térmico, cerramiento o partición interior.
    """
    def tempsimin(hrint):
        """Temperatura superficial mínima"""
        # la humedad relativa no debería pasar de 0.80 y psat = pi / HR
        psat = (hrint * 2337.0 / 100.0) / 0.8
        # condición CTE (son las expresiones inversas de psat como f(temp)
        _k = math.log (psat / 610.5)
        if psat >= 610.5:
            temp_si_min = 237.3 * _k / (17.269 - _k)
        else: # condición ISO 13788
            temp_si_min = 265.5 * _k / (21.875 - _k)
        return temp_si_min
    #XXX: comprobar si tempint = tempext?
    return (tempsimin(hrint) - tempext) / (tempint - tempext)

def condensas(cerr, temp_ext, temp_int, HR_int):
    """Comprueba la condición de existencia de condensaciones superficiales en
    un cerramiento o puente térmico.
    
    Devuelve True si existen condensaciones superficiales.
    """
    # el CTE incluye tablas según zonas y clase de higrometría para fRsimin
    # que están calculadas para la capital más desfavorable de cada zona y
    # con HR=55%, 62%, 70%.
    return fRsi(cerr.U) < fRsimin(temp_ext, temp_int, HR_int)

def condensai(cerr, temp_ext, temp_int, HR_ext, HR_int):
    """Comprueba la condición de existencia de condensaciones intersticiales en
    un cerramiento o puente térmico.
    
    Devuelve True si existen condensaciones intersticiales.
    """
    #TODO: Revisar condensaciones viendo si la cantidad condensada es
    # susceptible de evaporación o no
    g, pcondensa = cerr.condensacion(temp_ext, temp_int, HR_ext, HR_int)
    #g, pevapora = cerr.evaporacion(temp_ext, temp_int, HR_ext, HR_int,
    #                                      interfases=[2])
    condensa = (sum(g) > 0.0)
    return condensa

def condensaciones(cerr, temp_ext, temp_int, HR_ext, HR_int):
    """Existencia de condensaciones en un cerramiento.
    
    Devuelve True si existen condensaciones superficiales o intersticiales"""
    ci = condensai(cerr, temp_ext, temp_int, HR_ext, HR_int)
    cs = condensas(cerr, temp_ext, temp_int, HR_int)

    return ci or cs

if __name__ == "__main__":
    import cerramiento
    from datos_ejemplo import climae, climai, cerramientocapas

    cerr = cerramiento.Cerramiento("Cerramiento tipo", "Descripción",
                                   cerramientocapas, Rse=0.04, Rsi=0.13)
    f_Rsi = fRsi(cerr.U)
    f_Rsimin = fRsimin(climae.temp, climai.temp, climai.HR)
    c_sup = condensas(cerr, climae.temp, climai.temp, climai.HR)
    c_int = condensai(cerr, climae.temp, climai.temp,
                                     climae.HR, climai.HR)
    c_soi = condensaciones(cerr, climae.temp, climai.temp,
                           climae.HR, climai.HR)

    print u"Nombre: %s" % (cerr.nombre,)
    print u"Capas: \n\t", "\n\t".join(cerr.nombres)
    print u"\nCondensaciones superficiales (%s)" % (c_sup and u"Sí" or u"No")
    print u"\tfRsi = %.2f, fRsimin = %.2f" % (f_Rsi, f_Rsimin)
    print u"Condensaciones intersticiales (%s)" % (c_int and u"Sí" or u"No")
    print u"Condensaciones (%s)" % (c_soi and u"Sí" or u"No")
