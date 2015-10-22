#!/usr/bin/env python
#encoding: utf-8
#
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
"""Módulo de utilidades varias"""

import os, sys, shutil

def get_main_dir():
    """Find main dir even for py2exe frozen modules"""
    if hasattr(sys, "frozen"): #py2exe frozen module
        md = os.path.dirname(sys.executable)
    else:
        # normal run
        md = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        # test run XXX: revisar, ya que se ha movido test
        if not os.path.isdir(os.path.join(md, 'data')):
            md = os.path.abspath(os.path.join(md, '..'))
            if not os.path.isdir(os.path.join(md, 'data')):
                raise ValueError('No se encuentra directorio base')
    return md

class AppConfig(object):
    def __init__(self):
        self.maindir = get_main_dir()
        self.userdir = self._userdir()
        self.paths = {
            'mainconf': self.appresource('Condensaciones.ini'),
            'cerramientosdb': self.userresource('CerramientosDB.ini'),
            'climasdb': self.userresource('ClimasDB.ini'),
            'materialesdb': self.userresource('MaterialesDB.ini')
        }

    @property
    def datadir(self):
        return os.path.join(self.maindir, 'data')
            
    def _userdir(self):
        """Localiza o crea el directorio de configuración y bases de datos

        Usa por defecto el directorio condensaciones en el home del usario
        """
        CONFIGFILES = ['Condensaciones.ini', 'CerramientosDB.ini',
                       'MaterialesDB.ini', 'ClimasDB.ini']
        udir = os.path.join(os.path.expanduser('~'), 'condensaciones')
        if not os.path.exists(udir):
            os.makedirs(udir)
        for cfile in CONFIGFILES:
            ucfile = os.path.join(udir, cfile)
            if not os.path.exists(ucfile):
                shutil.copy(self.appresource(cfile), ucfile)
        return udir

    def appresource(self, *path_list):
        """Localiza un recurso del programa"""
        return os.path.join(self.datadir, *path_list)

    def userresource(self, *path_list):
        """Localiza un recurso del usuario"""
        return os.path.join(self.userdir, *path_list)

config = AppConfig()
