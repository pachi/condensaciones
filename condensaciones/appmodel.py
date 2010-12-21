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
"""Modelo de la aplicación Condensaciones"""

import comprobaciones
import clima
import cerramiento
from util import get_resource, colores_capas

cdb = cerramiento.CerramientosDB(get_resource('data', 'CerramientosDB.ini'))
CLIMASDB = get_resource('data', 'ClimaCTE.ini')
climasDB, climasnombres, climasdbconfig = clima.loadclimadb(CLIMASDB)
climae = climasDB['Climaext'][0] if 'Climaext' in climasDB else clima.Clima(5, 96)
climai = climasDB['Climaint'][0] if 'Climaint' in climasDB else clima.Clima(20, 55)
MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio',
         'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']

class Model(object):
    def __init__(self):
        """Constructor de modelo"""
        self.climaslist = [climae] # climas exteriores
        self._localidad = None # Sin localidad seleccionada
        self._imes = 0 # índice del mes activo en climaslist
        self._climai = climai # clima interior
        # Carga datos de materiales y cerramientos
        self.cerramientosDB = cdb
        # cerramiento actual
        self.c = self.cerramientosDB[self.cerramientosDB.nombres[0]]
        self.climasDB = climasDB
        self.climas = climasnombres
        self.modificado = False # ¿Existen cambios sin guardar?

    @property
    def localidad(self):
        """Localidad actual"""
        return self._localidad or 'Localidad genérica'
    
    @localidad.setter
    def localidad(self, lname):
        """Actualiza localidad y lista de climas exteriores para la misma"""
        if lname in self.climasDB.keys():
            self.climaslist = self.climasDB[lname]
            self._localidad = lname
        elif lname is None:
            self._localidad = None

    @property
    def ambienteinterior(self):
        return 'Predefinido'

    @property
    def ambienteexterior(self):
        mes = MESES[self.imes] if len(self.climaslist) == 12 else str(self.imes)
        return "%s [%s]" % (self.localidad, mes)

    @property
    def imes(self):
        """Mes actualmente activo de climaslist"""
        return self._imes
    
    @imes.setter
    def imes(self, index):
        """Establece el mes activo en climaslist"""
        climaslen = len(self.climaslist)
        if index > climaslen - 1:
            index = climaslen - 1
        self._imes = index

    @property
    def climae(self):
        """Getter de clima exterior"""
        return self.climaslist[self.imes]

    @climae.setter
    def climae(self, value):
        """Setter de clima exterior"""
        clm = value if isinstance(value, clima.Clima) else clima.Clima(*value)
        self.climaslist = [clm]
        self.imes = 0

    @property
    def climai(self):
        """Getter de clima exterior"""
        return self._climai

    @climai.setter
    def climai(self, value):
        """Setter de clima interior
        
        value puede ser del tipo clima.Clima o una tupla (temp, HR)
        """
        clm = value if isinstance(value, clima.Clima) else clima.Clima(*value)
        self._climai = clm

    @property
    def fRsi(self):
        """Factor de temperatura de la superficie interior"""
        return comprobaciones.fRsi(self.c.U)

    @property
    def fRsimin(self):
        """Factor de temperatura de la superficie interior mínimo
        
        El CTE indica que se calcule para el mes de enero (DB-HE1 3.2.3.1)
        y, a falta de datos, un ambiente interior con temperatura 20ºC
        y HR según higrometría. En este caso tenemos datos suficientes.
        
        TODO: comprobar que las resistencias superficiales son las correctas
        """
        te = self.climaslist[0].temp
        return comprobaciones.fRsimin(te, self.climai.temp, self.climai.HR)

    @property
    def glist(self):
        """Calcula lista de condensaciones intersticiales"""
        return comprobaciones.calculaintersticiales(self.c,
                                                    self.climai.temp,
                                                    self.climai.HR,
                                                    self.climaslist)

    @property
    def gmeses(self):
        """Lista de condensaciones acumuladas en cada mes"""
        return comprobaciones.gmeses(self.glist)
        
    @property
    def cs(self):
        """Comprueba la existencia de condensaciones superficiales s/CTE"""
        return self.fRsi < self.fRsimin

    @property
    def ci(self):
        """Comprueba la existencia de condensaciones intersticiales"""
        return sum(self.gmeses)

    def set_cerramiento(self, cname):
        """Selecciona cerramiento activo a partir de su nombre"""
        self.c = self.cerramientosDB[cname]
    
    def set_Rse(self, newRse):
        """Cambia Rse"""
        self.c.Rse = newRse
        self.modificado = True
    
    def set_Rsi(self, newRsi):
        """Cambia Rsi"""
        self.c.Rsi = newRsi
        self.modificado = True
    
    def set_capa(self, index, name, e):
        """Establece tupla de capa según índice. d es una tupla de datos"""
        #TODO: Con material resistivo pon espesor None, o espesor por defecto.
        #newmaterial = self.materiales[newname]
        #capae = None if newmaterial.type == 'RESISTANCE' else float(capae)
        self.c.capas[index] = (name, e)
        self.modificado = True

    def capasdata(self):
        """Devuelve iterador por capa con:
            i, (nombre, espesor, K, R, mu, S, c)
        """           
        cdict = colores_capas(self.c.nombres)
        colores = [cdict[nombre] for nombre in self.c.nombres]
        
        # quitamos Rse, Rsi en c.R con c.R[1:-1]
        return enumerate(zip(self.c.nombres, self.c.espesores,
                             self.c.K, self.c.R[1:-1],
                             self.c.mu, self.c.S, colores))
    
    # Acciones sobre capas ---------------------------------------------------
    
    def capaadd(self, index):
        """Añade capa tras posición index"""
        ncapatuple = self.c.capas[index]
        self.c.capas.insert(index + 1, ncapatuple)
        self.modificado = True
    
    def caparemove(self, index):
        """Elimina capa en posición index"""
        self.c.capas.pop(index)
        self.modificado = True
    
    def capaswap(self, index1, index2):
        """Intercambia la posición de dos capas del cerramiento activo"""
        cp = self.c.capas 
        cp[index1], cp[index2] = cp[index2], cp[index1]
        self.modificado = True
    
    # Acciones sobre cerramientos --------------------------------------------
    
    def cerramientoadd(self, index):
        """Añade y devuelve nuevo cerramiento tras posición index"""
        i = 1
        while True:
            newname = u"Cerramiento %i" % i
            if newname not in self.cerramientosDB.nombres:
                break
            i += 1
        newc = cerramiento.Cerramiento(newname, 'Nuevo cerramiento')
        self.cerramientosDB.insert(newc, index + 1)
        return newc
    
    def cerramientoremove(self, index):
        """Elimina cerramiento en posición index"""
        oldname = self.cerramientosDB.nombres[index]
        del self.cerramientosDB[oldname]
    
    def cerramientoswap(self, index1, index2):
        """Intercambia la posición de dos cerramientos"""
        ce = self.cerramientosDB.nombres
        ce[index1], ce[index2] = ce[index2], ce[index1]

    def cerramientocambianombre(self, oldname, newname):
        """Cambia nombre de cerramiento a nuevonombre"""
        if oldname != newname:
            i = self.cerramientosDB.rename(oldname, newname)

    def cerramientocambiadescripcion(self, cerr, newdesc):
        """Cambia nombre de cerramiento a nuevonombre"""
        self.cerramientosDB[cerr].descripcion = newdesc

    def cerramientossave(self):
        """Guarda base de datos de cerramientos"""
        self.cerramientosDB.savecerramientosdb()
