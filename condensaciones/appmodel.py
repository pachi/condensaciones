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
import materiales
import cerramientos
from util import get_resource

CerramientosDB = get_resource('data', 'CerramientosDB.ini')
cerr, cnombres, cgrupos = cerramientos.loadcerramientosdb(CerramientosDB)

class Model(object):
    def __init__(self, cerramiento, climaext, climaint):
        """Constructor de modelo"""
        self.c = cerramiento
        self.climae = climaext
        self.climai = climaint
        self.materiales = []
        self.cerramientos = []
        self.cerramientosDB = {}
        self.cargadata()
        self.cerramientomodificado = False

    def cargadata(self):
        """Carga datos de materiales y cerramientos"""
        #TODO: generar jerarquía de materiales en dbutils en lugar de crear
        #TODO: lista ordenada aquí.
        self.materiales = self.c.matnombres
        self.materiales.sort()
        self.cerramientos = cnombres
        self.cerramientosDB = cerr

    def set_cerramiento(self, cname):
        """Selecciona cerramiento activo a partir de su nombre"""
        self.c = self.cerramientosDB[cname]

    def set_climae(self, te, HRe):
        """Setter de clima exterior para detectar modificación"""
        self.climae = clima.Clima(te, HRe)

    def set_climai(self, ti, HRi):
        """Setter de clima interior para detectar modificación"""
        self.climai = clima.Clima(ti, HRi)
    
    def set_Rse(self, newRse):
        """Cambia Rse"""
        self.c.Rse = newRse
        self.cerramientomodificado = True
    
    def set_Rsi(self, newRsi):
        """Cambia Rsi"""
        self.c.Rsi = newRsi
        self.cerramientomodificado = True
    
    def set_capa(self, index, name, e):
        """Establece tupla de capa según índice. d es una tupla de datos"""
        #TODO: Con material resistivo pon espesor None, o espesor por defecto.
        #newmaterial = self.materiales[newname]
        #capae = None if newmaterial.type == 'RESISTANCE' else float(capae)
        self.c.capas[index] = (name, e)
        self.cerramientomodificado = True

    def capasdata(self):
        """Devuelve iterador por capa con: i, (nombre, espesor, K, R, mu, S)"""
        # quitamos Rse, Rsi en c.R con c.R[1:-1]
        return enumerate(zip(self.c.nombres, self.c.espesores,
                             self.c.K, self.c.R[1:-1], self.c.mu, self.c.S))

    def calcula(self):
        """Calcula resultados para usarlos en presentación"""
        ti, hri = self.climai.temp, self.climai.HR
        te, hre = self.climae.temp, self.climae.HR
        self.fRsi = comprobaciones.fRsi(self.c.U)
        self.fRsimin = comprobaciones.fRsimin(te, ti, hri)
        self.ccheck = comprobaciones.condensaciones(self.c, te, ti, hre, hri)
        self.cs = comprobaciones.condensas(self.c, te, ti, hri)
        self.ci = comprobaciones.condensai(self.c, te, ti, hre, hri)
        self.g, self.pcond = self.c.condensacion(te, ti, hre, hri)
        #self.g, self.pevap = self.c.evaporacion(te,ti,hre,hri,interfases=[2])
        self.totalg = 0.0 if not self.g else sum(self.g)

    # Acciones sobre capas ---------------------------------------------------
 
    def capaadd(self, index):
        """Añade capa tras posición index"""
        ncapatuple = self.c.capas[index]
        self.c.capas.insert(index + 1, ncapatuple)
        self.cerramientomodificado = True
    
    def caparemove(self, index):
        """Elimina capa en posición index"""
        self.c.capas.pop(index)
        self.cerramientomodificado = True
    
    def capaswap(self, index1, index2):
        """Intercambia la posición de dos capas del cerramiento activo"""
        cp = self.c.capas 
        cp[index1], cp[index2] = cp[index2], cp[index1]
        self.cerramientomodificado = True
    
    # Acciones sobre cerramientos --------------------------------------------
    
    def cerramientoadd(self, index):
        """Añade y devuelve nuevo cerramiento tras posición index"""
        i = 1
        while True:
            newname = u"Cerramiento %i" % i
            if newname not in self.cerramientos:
                break
            i += 1
        newc = cerramientos.Cerramiento(newname, 'Nuevo cerramiento')
        self.cerramientosDB[newc.nombre] = newc
        self.cerramientos.insert(index + 1, newc.nombre)
        return newc
    
    def cerramientoremove(self, index):
        """Elimina cerramiento en posición index"""
        #FIXME: No se elimina el cerramiento al guardar. Ver qué pasa
        oldname = self.cerramientos[index]
        self.cerramientos.pop(index)
        del self.cerramientosDB[oldname]
    
    def cerramientoswap(self, index1, index2):
        """Intercambia la posición de dos cerramientos"""
        ce = self.cerramientos 
        ce[index1], ce[index2] = ce[index2], ce[index1]
    
    def cerramientossave(self):
        cerramientos.savecerramientosdb(self.cerramientosDB,
                                        self.cerramientos,
                                        filename=CerramientosDB)
