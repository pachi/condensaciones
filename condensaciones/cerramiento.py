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
"""Cerramiento - Clase para la modelización de un cerramiento tipo."""

import operator
import psicrom
import materiales

class Cerramiento(object):
    """Clase Cerramiento
    
    Clase para modelizar un cerramiento tipo, multicapa, con cada capa definida
    por su material y sus propiedades físicas.
    """
    def __init__(self, nombre, descripcion, capas,
                 tipo=None, Rse=None, Rsi=None):
        """Inicialización de cerramiento.
        
        nombre - Nombre del cerramiento
        descripción - Descripción somera de la composición del cerramiento
        capas - lista de tuplas con la descripción de las capas que forman
                el cerramiento. Cada tupla define una capa, identificada por
                su nombre y su espesor. La lista se ordena de exterior a
                interior.
        tipo - Tipo de cerramiento en relación a su disposición (horizontal,
                vertical, cubierta, etc) y que sirve para definir de forma
                implícita sus valores de resistencia superficial.
        Rse - Resistencia superficial exterior
        Rsi - Resistencia superficial interior
        """
        #TODO: Tipo selecciona Rse y Rsi según sea horizontal, vertical, etc
        self.nombre = nombre
        self.descripcion = descripcion
        self.capas = capas
        self.Rse = Rse
        self.Rsi = Rsi

    @property
    def nombres(self):
        """Lista de nombres de las capas"""
        return [nombre for nombre, e in self.capas]

    @property
    def espesores(self):
        """Lista de espesores de las capas [m]"""
        return [e for nombre, e in self.capas]

    @property
    def espesores_acumulados(self):
        """Lista de espesores físicos acumulados [m]
        
        Lista de coordenadas X geométricas de las interfases de cada capa.
        """
        return [0.0] + [reduce(operator.add, self.espesores[:i])
                        for i in range(1, len(self.espesores)+1)]

    @property
    def R(self):
        """Lista de resistencias térmicas de las capas [m²K/W]"""
        def _resist_capa(capa, e=None):
            tipo = materiales.tipo(capa)
            if tipo == 'PROPERTIES':
                return e / materiales.conductividad(capa)
            elif tipo == 'RESISTANCE':
                return materiales.resistencia(capa)
            else:
                raise
        return [self.Rse] + [_resist_capa(nombre, e)
                             for nombre, e in self.capas] + [self.Rsi]

    @property
    def S(self):
        """Lista de espesore de aire equivalente de las capas [m]"""
        return [e * materiales.difusividad(nombre)
                for nombre, e in self.capas]

    @property
    def S_acumulados(self):
        """Lista de espesores de aire equivalente acumulados en cada capa [m]
        
        Lista de coordenadas X en espesor de aire equivalente de las
        interfases de capa.
        """
        return [0.0] + [reduce(operator.add, self.S[:i])
                        for i in range(1,len(self.S)+1)]

    @property
    def S_total(self):
        "Espesor de aire equivalente del cerramiento [m]"
        return sum(self.S)

    @property
    def R_total(self):
        """Resistencia térmica total del cerramiento [m²K/W]"""
        return sum(self.R)

    @property
    def U(self):
        """Transmitancia térmica del cerramiento [W/m²K]"""
        return 1.0 / self.R_total

    def temperaturas(self, temp_ext, temp_int):
        """Lista de temperaturas en el cerramiento [ºC]
        
        Devuelve la temperatura exterior, temperatura superficial exterior,
        temperaturas intersticiales, temperatura superficial interior
        y temperatura interior.
        
        temp_ext - temperatura exterior media en el mes de enero
        temp_int - temperatura interior de cálculo (20ºC)
        """
        _tlist = [temp_ext]
        for capa_Ri in self.R:
            tempj = _tlist[-1] + (capa_Ri * (temp_int -
                                             temp_ext) / self.R_total)
            _tlist.append(tempj)
        return _tlist

    def presiones(self, temp_ext, temp_int, HR_ext, HR_int):
        """Lista de presiones de vapor en el cerramiento [Pa]
        
        Devuelve la presión de vapor al exterior, presiones de vapor
        intermedias y presión de vapor interior.
        
        temp_ext - Temperatura exterior del aire [ºC]
        temp_int - Temperatura interior del aire [ºC]
        HR_ext - Humedad relativa exterior del aire [%]
        HR_int - Humedad relativa interior del aire [%]
        """
        _p_ext = psicrom.pvapor(temp_ext, HR_ext)
        _p_int = psicrom.pvapor(temp_int, HR_int)
        # La presión exterior es constante, en el aire y sup ext de cerr
        p_vapor = [_p_ext, _p_ext]
        for capa_Si in self.S:
            pres_j = p_vapor[-1] + (capa_Si * (_p_int - _p_ext) / self.S_total)
            p_vapor.append(pres_j)
        # La presión interior es constante, en sup int de cerr y el aire
        p_vapor.append(_p_int)
        return p_vapor

    def presionessat(self, temp_ext, temp_int):
        """Lista de presiones de saturación en el cerramiento [Pa]
        
        temp_ext - Temperatura exterior del aire [ºC]
        temp_int - Temperatura interior del aire [ºC]
        """
        _temperaturas = self.temperaturas(temp_ext, temp_int)
        return [psicrom.psat(t) for t in _temperaturas]

    def condensacion(self, temp_ext, temp_int, HR_ext, HR_int):
        """Cantidad de condensación y coordenadas de condensación/presión
            
        Devuelve la cantidad de condensación en [g/m²s] y una lista de
        tuplas con las coordenadas de los puntos de condensacion en [m] de
        espesor de aire equivalente y la presión de vapor en ese punto
        (S(i), p_vapor(i)).
        
        temp_ext - Temperatura exterior del aire [ºC]
        temp_int - Temperatura interior del aire [ºC]
        HR_ext - Humedad relativa exterior del aire [%]
        HR_int - Humedad relativa interior del aire [%]
        """
        p = self.presiones(temp_ext, temp_int, HR_ext, HR_int)
        p_sat = self.presionessat(temp_ext, temp_int)
        # calculamos las posiciones x, y correspondientes a espesor de aire
        # equivalente y presiones de saturación
        Scapas = self.S
        _xjo = [0.0] + [reduce(operator.add, Scapas[:i])
                        for i in range(1,len(Scapas)+1)]
        _yjo = ([p[1]] + [_p for _p in p_sat[2:-2]] + [p[-1]])

        # Calculamos la envolvente convexa inferior de la linea de presiones de
        # saturación partiendo de presion_exterior y presion_interior como
        # extremos.
        # Los puntos de tangencia son los planos de condensación
        def _giraizq((p, q, r)):
            "¿Forman los vectores pq:qr un giro a la izquierda?"
            _det = ((q[0]*r[1] + p[0]*q[1] + r[0]*p[1]) -
                    (q[0]*p[1] + r[0]*q[1] + p[0]*r[1]))
            return (_det > 0) or False

        puntos = [(x, y) for x, y in zip(_xjo, _yjo)]
        envolv_inf = [puntos[0], puntos[1]]
        for p in puntos[2:]:
            envolv_inf.append(p)
            while len(envolv_inf) > 2 and not _giraizq(envolv_inf[-3:]):
                del envolv_inf[-2]
        _xj = [x for x, y in envolv_inf]
        _yj = [y for x, y in envolv_inf]
        # condensaciones g/m2.s
        _g = [(psicrom.g(_yj[n+1], _yj[n+2], _xj[n+1], _xj[n+2]) -
               psicrom.g(_yj[n], _yj[n+1], _xj[n], _xj[n+1]))
               for n in range(len(_yj) - 2)]
        return _g, envolv_inf

    def evaporacion(self, temp_ext, temp_int, HR_ext, HR_int, interfases):
        """Cantidad de evaporación y coordenadas de evaporación/presión
        
        Devuelve la cantidad de evaporación en [g/m²s] y una lista de
        tuplas con las coordenadas de los puntos de evaporación en [m] de
        espesor de aire equivalente y la presión de vapor en ese punto
        (S(i), p_vapor(i)).
        
        temp_ext - Temperatura exterior del aire [ºC]
        temp_int - Temperatura interior del aire [ºC]
        HR_ext - Humedad relativa exterior del aire [%]
        HR_int - Humedad relativa interior del aire [%]
        """
        p = self.presiones(temp_ext, temp_int, HR_ext, HR_int)
        p_sat = self.presionessat(temp_ext, temp_int)
        # calculamos las posiciones x, y correspondientes a espesor de aire
        # equivalente y presiones de saturación
        Scapas = self.S
        x_jo = [0.0] + [reduce(operator.add, Scapas[:i]) 
                        for i in range(1,len(Scapas)+1)]
        y_jo = ([p[1]] + [_p for _p in p_sat[2:-2]] + [p[-1]])

        puntos_evapora = [(x_jo[i], y_jo[i]) for i in interfases]
        envolvente_inf = ([(x_jo[0], y_jo[0])] + puntos_evapora +
                          [(x_jo[-1], y_jo[-1])])
        x_j = [x for x, y in envolvente_inf]
        y_j = [y for x, y in envolvente_inf]
        # evaporaciones g/m2.s
        _g = [(psicrom.g(y_j[n+1], y_j[n+2], x_j[n+1], x_j[n+2]) -
               psicrom.g(y_j[n], y_j[n+1], x_j[n], x_j[n+1]))
               for n in range(len(y_j) - 2)]
        return _g, envolvente_inf
