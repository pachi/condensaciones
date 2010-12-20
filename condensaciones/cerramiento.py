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
"""Cerramiento - Clase para la modelización de un cerramiento tipo."""

import numpy
import psicrom
import material
import configobj
from util import get_resource

mdb = material.MaterialesDB(get_resource('data', 'MaterialesDB.ini'))

class Cerramiento(object):
    """Clase para modelizar un cerramiento tipo, multicapa, con cada capa definida
    por su material y sus propiedades físicas.
    """
    #: BBDD de materiales (tipo: MaterialesDB)
    matDB = mdb
    def __init__(self, nombre, descripcion, capas=None,
                 Rse=None, Rsi=None, tipo=None):
        """Inicialización de cerramiento.

        :param str nombre: Nombre del cerramiento
        :param str descripcion: Descripción somera de la composición del cerramiento
        :param list capas: lista de tuplas con la descripción de las capas que
        forman el cerramiento. Cada tupla define una capa, identificada por su
        nombre y su espesor. La lista se ordena de exterior a interior.
        Si no se define, se usa una capa de espesor 0,3m y material el
        primero de la base de datos.
        :param float Rse: Resistencia superficial exterior [m²K/W]
        Si no se indica valor, se usa 0,04 m²K/W.
        :param float Rsi: Resistencia superficial interior [m²K/W]
        Si no se indica valor, se usa 0,13 m²K/W.
        :param str tipo: Tipo de cerramiento en relación a su disposición (horizontal,
        vertical, cubierta, etc) y que sirve para definir de forma
        implícita sus valores de resistencia superficial.
        """
        #: Nombre del cerramiento (str)
        self.nombre = nombre
        #: Descripción somera de la composición del cerramiento
        self.descripcion = descripcion
        #: lista de tuplas con la descripción de las capas que forman
        #: el cerramiento. Cada tupla define una capa, identificada por
        #: su nombre y su espesor. La lista se ordena de exterior a
        #: interior.
        #: Si no se define, se usa una capa de espesor 0,3m y material
        #: el primero de la base de datos.
        self.capas = capas if capas else [(self.matDB.nombres[0], 0.3)]
        for nombre, e in self.capas:
            if nombre not in self.matDB.nombres:
                raise ValueError('Material desconocido: %s' % nombre)
        #: Resistencia superficial exterior [m²K/W]
        #: Si no se indica valor, se usa 0,04 m²K/W.
        self.Rse = Rse if Rse else 0.04
        #: Resistencia superficial interior [m²K/W]
        #: Si no se indica valor, se usa 0,13 m²K/W.
        self.Rsi = Rsi if Rsi else 0.13
        #: Tipo de cerramiento en relación a su disposición (horizontal,
        #: vertical, cubierta, etc) y que sirve para definir de forma
        #: implícita sus valores de resistencia superficial.
        self.tipo = tipo

    @property
    def nombres(self):
        """Lista de nombres de las capas"""
        return [nombre for nombre, e in self.capas]

    @property
    def espesores(self):
        """Lista de espesores de las capas [m]"""
        return [e for nombre, e in self.capas]

    @property
    def e(self):
        """Espesor total [m]"""
        return sum(self.espesores)

    @property
    def mu(self):
        """Lista de difusividades al vapor de las capas [-]"""
        return [self.matDB[nombre].mu for nombre, e in self.capas]

    @property
    def K(self):
        """Lista de conductividades térmicas de las capas [W/mK]"""
        def Ki(capa):
            tipo = self.matDB[capa].type
            if tipo == 'PROPERTIES':
                return self.matDB[capa].conductivity
            else:
                return None
        return [Ki(nombre) for nombre, e in self.capas]

    @property
    def R(self):
        """Lista de resistencias térmicas de las capas [m²K/W]"""
        def Ri(capa, e=None):
            tipo = self.matDB[capa].type
            if tipo == 'PROPERTIES':
                return e / self.matDB[capa].conductivity
            elif tipo == 'RESISTANCE':
                return self.matDB[capa].resistance
            else:
                raise ValueError('Tipo de elemento desconocido %s' % tipo)
        return [self.Rse] + [Ri(nombre, e)
                             for nombre, e in self.capas] + [self.Rsi]

    @property
    def S(self):
        """Lista de espesores de aire equivalente de las capas [m]"""
        return [e * self.matDB[nombre].mu for nombre, e in self.capas]

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

        :param float temp_ext: temperatura exterior media en el mes de enero
        :param float temp_int: temperatura interior de cálculo (20ºC)
        :returns: lista de temperaturas en el cerramiento
        :rtype: list
        """
        _tlist = [temp_ext]
        _k = (temp_int - temp_ext) / self.R_total
        for capa_Ri in self.R:
            tempj = _tlist[-1] + (capa_Ri * _k)
            _tlist.append(tempj)
        return _tlist

    def presiones(self, temp_ext, temp_int, HR_ext, HR_int):
        """Lista de presiones de vapor en el cerramiento [Pa]

        Devuelve la presión de vapor al exterior, presiones de vapor
        intermedias y presión de vapor interior.

        :param float temp_ext: Temperatura exterior del aire [ºC]
        :param float temp_int: Temperatura interior del aire [ºC]
        :param float HR_ext: Humedad relativa exterior del aire [%]
        :param float HR_int: Humedad relativa interior del aire [%]
        :returns: lista de presiones de vapor en el cerramiento
        :rtype: list
        """
        _p_ext = psicrom.pvapor(temp_ext, HR_ext)
        _p_int = psicrom.pvapor(temp_int, HR_int)
        # La presión exterior es constante, en el aire y sup ext de cerr
        p_vapor = [_p_ext, _p_ext]
        _k = (_p_int - _p_ext) / self.S_total
        for capa_Si in self.S:
            pres_j = p_vapor[-1] + (capa_Si * _k)
            p_vapor.append(pres_j)
        # La presión interior es constante, en sup int de cerr y el aire
        p_vapor.append(_p_int)
        return p_vapor

    def presionessat(self, temp_ext, temp_int):
        """Lista de presiones de saturación en el cerramiento [Pa]
        
        :param float temp_ext: Temperatura exterior del aire [ºC]
        :param float temp_int: Temperatura interior del aire [ºC]
        :returns: lista de presiones de vapor de saturación en el cerramiento
        :rtype: list
        """
        _temperaturas = self.temperaturas(temp_ext, temp_int)
        return [psicrom.psat(t) for t in _temperaturas]

    def envolventec(self, temp_ext, temp_int, HR_ext, HR_int, cond_previa=[]):
        """Puntos de las interfases que definen la envolvente de condensaciones
        
        Puntos (S, psat, g) situados en las interfases que definen la envolvente
        de condensaciones. Sus puntos de tangencia con la curva de presiones de
        saturación definen los planos de condensación.
        
        :param float temp_ext: Temperatura exterior del aire [ºC]
        :param float temp_int: Temperatura interior del aire [ºC]
        :param float HR_ext: Humedad relativa exterior del aire [%]
        :param float HR_int: Humedad relativa interior del aire [%]
        :param list cond_previa: Lista de tuplas con posición del plano con
            condensación previa (0 = superficie exterior) y cantidad de
            condensado en ese plano [g/m²] [(n0, g0), (n1, g1), ..., (ni, gi)].
        
        :returns: Lista de tuplas [(S0, p0, g0), (S1, p1 g1), ..., (Si, pi, gi)]
            de distancia a la superficie exterior [m de aire equivalente],
            presión de saturación [Pa] y cantidad de condensación [g/m²s] para
            cada interfase.
        :rtype: list(tuple)
        """
        
        #TODO: devolver solamente coordenadas y no cantidades de condensación
        # ya que no se usan en el cálculo.
        def _giraizq(p, q, r):
            "¿Forman los vectores pq:qr un giro a la izquierda?"
            _det = ((q[0]*r[1] + p[0]*q[1] + r[0]*p[1]) -
                    (q[0]*p[1] + r[0]*q[1] + p[0]*r[1]))
            return (_det > 0) or False
        
        # Calcula las posiciones x, y, g correspondientes a espesor de aire
        # equivalente, presiones de vapor y cantidades condensadas previas.
        # El punto inicial y final corresponden a las presiones de vapor en las
        # superficies exterior e interior, y los puntos intermedios se
        # inicializan a los valores de las presiónes de saturación, para
        # luego calcular la envolvente convexa inferior que nos dará los planos
        # de condensación en los puntos de tangencia.
        interfases = range(len(self.capas) + 1)
        p = self.presiones(temp_ext, temp_int, HR_ext, HR_int)
        p_sat = self.presionessat(temp_ext, temp_int)
        g = dict(cond_previa)
        
        x0 = numpy.cumsum([0.0] + self.S)
        y0 = ([p[1]] + [_p for _p in p_sat[2:-2]] + [p[-1]])       
        g0 = [g.get(i, 0.0) for i in interfases]
        
        puntos = [(xj, yj, gj) for xj, yj, gj in zip(x0, y0, g0)]
        
        # Un punto intermedio B no pertenece a la envolvente convexa si, siendo
        # el punto anterior A y el posterior C, BC produce un giro a la derecha
        # respecto a AB (AC queda por debajo) y si no tiene ya condensación 
        # previa.
        while 1: 
            cont = False
            envolv_inf = [puntos[0], puntos[1]]
            for punto in puntos[2:]:
                envolv_inf.append(punto)
                if (not _giraizq(*envolv_inf[-3:]) and
                    envolv_inf[-2][2] <= 0.0): # gj > 0 implica condensación previa
                    del envolv_inf[-2]
                    cont = True
            if not cont:
                break
            else:
                puntos = envolv_inf[:]
        xj, yj, gj = zip(*envolv_inf)
        return zip(xj,yj)

    def cantidadc(self, envolv_inf, cond_previa=[]):
        """Cantidades condensadas en las interfases [g/m².mes]
        
        Calcula las cantidades de condensación a partir de la envolvente de
        condensaciones y las condensaciones previas en cada interfase.
        """
        _K = 2592000.0 # segundos por mes
        def _g_punto(plist):
            "Calcula la condensación en el punto intermedio (B), para ABC"
            xpa, ypa = plist[0][0], plist[0][1] # p0: (x, y, g)
            xpb, ypb = plist[1][0], plist[1][1] # p1: (x, y, g)
            xpc, ypc = plist[2][0], plist[2][1] # p2: (x, y, g)
            return (psicrom.g(ypb, ypc, xpb, xpc, _K) -
                    psicrom.g(ypa, ypb, xpa, xpb, _K))
        
        x_index = list(numpy.cumsum([0.0] + self.S))
        
        gold = dict(cond_previa)
        gnew = dict((x_index.index(x[0]), _g_punto(envolv_inf[i:])) 
                    for i, x in enumerate(envolv_inf[1:-1]))
        gtotal = [max(0.0,gold.get(i, 0.0) + gnew.get(i, 0.0)) 
                  for i in range(len(x_index))]
        new_cond = [(i, gj) for i, gj in enumerate(gtotal) if gj > 0.0]
        return new_cond

    def condensacion(self, temp_ext, temp_int, HR_ext, HR_int, cond_previa=[]):
        """Cantidad de condensación por interfases

        :param float temp_ext: Temperatura exterior del aire [ºC]
        :param float temp_int: Temperatura interior del aire [ºC]
        :param float HR_ext: Humedad relativa exterior del aire [%]
        :param float HR_int: Humedad relativa interior del aire [%]
        :param list cond_previa: Lista de tuplas con posición del plano con
            condensación previa (0 = superficie exterior) y cantidad de
            condensado en ese plano [g/m²] [(n0, g0), (n1, g1), ..., (ni, gi)].
        :returns: Lista de tuplas con posición del plano de
            condensación (0 = superficie exterior) y cantidad de condensado en
            ese plano (en [g/m²s]) [(n0, g0), (n1, g1), ..., (ni, gi)]
        :rtype: list(tuple, ...)
        """
        envolv_inf = self.envolventec(temp_ext, temp_int, HR_ext, HR_int, cond_previa)
        new_cond = self.cantidadc(envolv_inf, cond_previa)
        return new_cond

#===============================================================================
# BBDD de Cerramientos en formato ConfigObj
#===============================================================================

CERRAMIENTOSDBHEADER = """#   Biblioteca de Cerramientos para Condensa
#
#   Condensa - Programa de cálculo de condensaciones según CTE
#
#   Copyright (C) 2009-2010, Rafael Villar Burke <pachi@rvburke.com>
#
#   Cada sección se denomina con el nombre del cerramiento e incluye:
#   - descripcion: descripción del cerramiento
#   - tipo: tipo genérico del cerramiento  [opcional]
#   - Rse: resistencia superficial exterior [m²K/W] [opcional]
#   - Rsi: resistencia superficial interior [m²K/W] [opcional]
#   además de una subsección de [[capas]] que contiene por cada entrada:
#   - capa: con nombre y espesor de capa [m] separados por una coma
#   El nombre de capa no puede contener comas.
#
#   La sección config incluye configuración general como
#   - nombre: nombre de la base de datos
#   - materiales: nombre de la base de datos de materiales
#""".splitlines()

class CerramientosDB(object):
    """Base de datos de Cerramientos"""

    def __init__(self, filename='CerramientosDB.ini'):
        """Inicialización de la BBDD de Cerramientos

        :param str filename: nombre del archivo desde el que cargar la base de
                             datos
        """
        #: nombre del archivo desde el que cargar la base de datos
        self.filename = filename
        #: diccionario de configuración (nombre, ...)
        self.config = None
        #: diccionario de cerramientos de la BBDD por nombre
        self.cerramientos = {}
        #: lista de nombres de cerramientos de la BBDD
        self.nombres= []
        #: lista de nombres de tipos de cerramiento de la BBDD
        self.nombrestipos = []
        self.loadcerramientosdb(filename)

    def __getitem__(self, key):
        return self.cerramientos[key]

    def __setitem__(self, key, value):
        self.cerramientos[key] = value
        #FIXME: La ordenación puede ser distinta
        self.nombres.append(key)

    def __delitem__(self, key):
        del self.cerramientos[key]
        self.nombres.remove(key)

    def insert(self, cerramiento, index):
        """Insertar cerramiento antes de la posición index

        :param Cerramiento cerramiento: Cerramiento
        :param int index: posición
        """
        self.cerramientos[cerramiento.nombre] = cerramiento
        self.nombres.insert(index, cerramiento.nombre)

    def rename(self, oldkey, newkey):
        """Cambia nombre de cerramiento

        :param str oldkey: nombre antiguo
        :param str newkey: nombre nuevo
        """
        cerr = self.cerramientos[oldkey]
        cerr.nombre = newkey
        self.cerramientos[newkey] = cerr
        del self.cerramientos[oldkey]
        i = self.nombres.index(oldkey)
        self.nombres[i] = newkey

    def loadcerramientosdb(self, filename=None):
        """Lee base de datos de cerramientos en formato ConfigObj

        :param str filename: nombre del archivo que contiene la BBDD.
        """
        def unescape(data):
            """Unescape &amp;, &lt;, and &gt; in a string of data."""
            d = data.replace("&lb;", "[").replace("&rb;", "]")
            return d.replace("&amp;", "&")

        if not filename:
            if self.filename:
                filename = self.filename
            else:
                raise ValueError, "No se ha especificado un archivo"
        config = configobj.ConfigObj(filename,
                                     encoding='utf-8', raise_errors=True)
        if 'config' in config:
            self.config = config['config'].copy()
            del config['config']
        for section in config:
            cerramiento = config[section]
            nombre = unescape(section)
            descripcion = cerramiento['descripcion']
            capas = cerramiento['capas']
            lcapas = [(name, float(e)) for ncapa, (name, e) in capas.items()]
            c = Cerramiento(nombre, descripcion, lcapas)
            if 'tipo' in cerramiento:
                c.tipo = cerramiento['tipo']
            else:
                c.tipo = 'predeterminado'
            if 'Rse' in cerramiento:
                c.Rse = cerramiento.as_float('Rse')
            if 'Rsi' in cerramiento:
                c.Rsi = cerramiento.as_float('Rsi')
            self.cerramientos[nombre] = c
            self.nombres.append(nombre)
            if c.tipo not in self.nombrestipos:
                self.nombrestipos.append(c.tipo)

    def savecerramientosdb(self, filename=None):
        """Guarda base de datos de cerramientos en formato ConfigObj

        :param str filename: nombre del archivo en el que guardar la BBDD.
        """
        def escape(data):
            """Escape &, [ and ] a string of data."""
            d = data.replace("&", "&amp;")
            return d.replace("[", "&lb;").replace("]", "&rb;")

        if not filename:
            if self.filename:
                filename = self.filename
            else:
                raise ValueError, "No se ha especificado un archivo"
        config = configobj.ConfigObj(encoding='utf-8', raise_errors=True)
        if self.config:
            config['config'] = {}
            for key in self.config:
                config['config'][key] = self.config[key]
        for cerramiento in self.nombres:
            if cerramiento not in self.cerramientos:
                raise ValueError, "Cerramiento desconocido: %s" % cerramiento
            c = self.cerramientos[cerramiento]
            config[escape(cerramiento)] = {}
            config.comments[escape(cerramiento)] = '#'
            sect = config[escape(cerramiento)]
            sect['descripcion'] = c.descripcion
            sect['capas'] = {}
            for i, (name, e) in enumerate(c.capas):
                sect['capas']['capa%i' % (i + 1)] = (name, e)
            sect['tipo'] = c.tipo if hasattr(c, 'tipo') else 'predeterminado'
            if hasattr(c, 'Rse'):
                sect['Rse'] = c.Rse
            if hasattr(c, 'Rsi'):
                sect['Rsi'] = c.Rsi
        config.initial_comment = CERRAMIENTOSDBHEADER
        config.filename = filename
        config.write()
