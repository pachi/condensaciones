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

import operator
import psicrom
import materiales

class Cerramiento(object):
    def __init__(self, nombre, descripcion, capas, Rse=None, Rsi=None):
        #TODO: Añadir tipo para seleccionar Rse y Rsi según sea horizontal,
        #TODO: vertical, etc
        self.nombre = nombre
        self.descripcion = descripcion
        self.capas = capas
        self.Rse = Rse
        self.Rsi = Rsi

    @property
    def nombres(self):
        "Nombre de las capas"
        return [nombre for nombre, e in self.capas]

    @property
    def espesores(self):
        "Espesores de las capas [m]"
        return [e for nombre, e in self.capas]

    @property
    def espesores_acumulados(self):
        """Espesores físicos acumulados [m]
        
        Lista de coordenadas X geométricas de las interfases de cada capa.
        """
        return [0.0] + [reduce(operator.add, self.espesores[:i])
                        for i in range(1, len(self.espesores)+1)]

    @property
    def R(self):
        "Resistencia térmica de las capas [m²K/W]"
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
        "Espesor de aire equivalente de las capas [m]"
        return [e * materiales.difusividad(nombre)
                for nombre, e in self.capas]

    @property
    def S_acumulados(self):
        """Espesor de aire equivalente acumulado [m]
        
        Lista de coordenadas X en espesor de aire equivalente de las
        interfases de capa.
        """
        return [0.0] + [reduce(operator.add, self.S[:i])
                        for i in range(1,len(self.S)+1)]

    @property
    def S_total(self):
        "Espesor de aire equivalente de todo el cerramiento [m]"
        return sum(self.S)

    @property
    def R_total(self):
        """Resistencia térmica total del cerramiento [m²K/W]
        """
        return sum(self.R)

    @property
    def U(self):
        """Transmitancia térmica del cerramiento [W/m²K]
        """
        return 1.0 / self.R_total

    def temperaturas(self, temp_ext, temp_int):
        """Devuelve lista de temperaturas [ºC]:
        temperatura exterior, temperatura superficial exterior,
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
        """Devuelve una lista de presiones de vapor [Pa]
        presión de vapor al exterior, presiones de vapor intermedias y presión
        de vapor interior.
        """
        _p_ext = psicrom.pvapor(temp_ext, HR_ext)
        _p_int = psicrom.pvapor(temp_int, HR_int)
        # La presión exterior es constante, en el aire y sup ext de cerramiento
        p_vapor = [_p_ext, _p_ext]
        for capa_Si in self.S:
            pres_j = p_vapor[-1] + (capa_Si * (_p_int - _p_ext) / self.S_total)
            p_vapor.append(pres_j)
        # La presión interior es constante, en sup int de cerramiento y el aire
        p_vapor.append(_p_int)
        return p_vapor

    def presionessat(self, temp_ext, temp_int):
        "Presiones de saturación en cada capa [Pa]"
        _temperaturas = self.temperaturas(temp_ext, temp_int)
        return [psicrom.psat(t) for t in _temperaturas]

    def condensacion(self, temp_ext, temp_int, HR_ext, HR_int):
        """Calcula cantidad de condensación y coordenadas (S, presión de vapor)
        de los planos de condensación.
        Devuelve g [g/m²s], puntos_condensacion
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
        _g = [(psicrom.tasatransferenciavapor(_yj[n+1], _yj[n+2],
                                             _xj[n+1], _xj[n+2]) -
            psicrom.tasatransferenciavapor(_yj[n], _yj[n+1],
                                           _xj[n], _xj[n+1]))
            for n in range(len(_yj) - 2)]
        return _g, envolv_inf

    def evaporacion(self, temp_ext, temp_int, HR_ext, HR_int, interfases):
        """Calcula cantidad de evaporacion y coordenadas (S, presión de vapor)
        de los planos de evaporación.
        Devuelve g [g/m²s], puntos_evaporacion
        """
        p = self.presiones(temp_ext, temp_int, HR_ext, HR_int)
        p_sat = self.presionessat(temp_ext, temp_int)
        # calculamos las posiciones x, y correspondientes a espesor de aire
        # equivalente y presiones de saturación
        Scapas = self.S
        x_jo = [0.0] + [reduce(operator.add, Scapas[:i]) 
                        for i in range(1,len(Scapas)+1)]
        y_jo = ([p[1]] + [p for p in p_sat[2:-2]] + [p[-1]])

        puntos_evapora = [(x_jo[i], y_jo[i]) for i in interfases]
        envolvente_inf = ([(x_jo[0], y_jo[0])] + puntos_evapora +
                          [(x_jo[-1], y_jo[-1])])
        x_j = [x for x, y in envolvente_inf]
        y_j = [y for x, y in envolvente_inf]
        # evaporaciones g/m2.s
        _g = [(psicrom.tasatransferenciavapor(y_j[n+1], y_j[n+2],
                                             x_j[n+1], x_j[n+2]) -
            psicrom.tasatransferenciavapor(y_j[n], y_j[n+1],
                                           x_j[n], x_j[n+1]))
            for n in range(len(y_j) - 2)]
        return _g, envolvente_inf

if __name__ == "__main__":
    from datos_ejemplo import climae, climai, murocapas
    from util import stringify

    Rs_ext = 0.04
    Rs_int = 0.13
    muro = Cerramiento("Cerramiento tipo", "Descripción 1", murocapas,
                       Rs_ext, Rs_int)

    temperaturas = muro.temperaturas(climae.temp, climai.temp)
    presiones_sat = muro.presionessat(climae.temp, climai.temp)
    presiones = muro.presiones(climae.temp, climai.temp, climae.HR, climai.HR)
    p_ext = presiones[1]
    p_int = presiones[-1]

    g, puntos_condensacion = muro.condensacion(climae.temp, climai.temp,
                                               climae.HR, climai.HR)
    cantidad_condensada = sum(g)
    # indicamos evaporación en la interfase 2, pero en realidad habría que ver
    # en cuáles había antes condensaciones y realizar el cálculo en ellas.
    g, puntos_evaporacion = muro.evaporacion(climae.temp, climai.temp,
                                             climae.HR, climai.HR,
                                             interfases=[2])
    cantidad_evaporada = sum(g)

    print u"Cerramiento:\n\t", muro.nombre
    print u"Nombre capas:\n\t", "\n\t".join(muro.nombres)
    print
    print u"Espesores:\n\t", stringify(muro.espesores, 2)
    print u"Espesores acumulados:\n\t", stringify(muro.espesores_acumulados, 2)
    print u"R Capas:\n\t", stringify(muro.R, 2)
    print u"S Capas:\n\t", stringify(muro.S, 2)
    print u"S acumulados:\n\t", stringify(muro.S_acumulados, 2)
    print u"S total:", muro.S_total # Espesor aire equivalente total (m), 2.16
    print u"Rs_ext: %.3f\nRs_int: %.2f" % (muro.Rse, muro.Rsi)
    print u"R_total: %.3f" % muro.R_total #("Resistencia total (m²K/W)", 1.25)
    print u"U: %.3f" % muro.U # 0.80 W/m^2K = 1/Rtotal
    print
    print u"Temperaturas:\n\t", stringify(temperaturas, 1)
    print u"Presiones de vapor:\n\t", stringify(presiones, 1)
    print u"\tPresión de vapor exterior: %.2f" % p_ext # 1016.00
    print u"\tPresión de vapor interior: %.2f" % p_int # 1285.32
    print u"Presiones de saturación:\n\t", stringify(presiones_sat, 1)
    print
    print u"Condensaciones:"
    print u"\tCantidad condensada: %.2f [g/m2.mes]" % (2592000.0 *
                                                       cantidad_condensada,)
    print u"\tCantidad evaporada: %.2f [g/m2.mes]" % (2592000.0 *
                                                      cantidad_evaporada,)
