#!/usr/bin/env python
# encoding: utf-8
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
#
# setup para crear los ejecutables de windows
# el ejecutable y sus dependencias se incluyen en el directorio
# 'dist' que genera el programa
# Para 'compilar' el código ejecutar este script usando:
# python setup.py py2exe
# Recordar cambiar el archivo
# C:\winp\Python26\Lib\site-packages\matplotlib\mpl-data\matplotlibrc
# al reinstalar matplotlib para que indique como default backend GTKCairo:
# backend      : GTKCairo

from distutils.core import setup
import py2exe
import matplotlib

docfiles = ['README', 'NEWS', 'INSTALL', 'COPYING']
datafilelist = ['data/condensa.ui',
                'data/BDCatalogo.bdc',
                'data/Catalogo_URSA.bdc',
                'data/PCatalogo.bdc']
includes = ['cairo', 'pango', 'pangocairo', 'atk', 'gobject']
excludes = ['_wxagg', '_fltkagg', '_cocoaagg', '_gtkagg',
            'email', 'logging', 'PyQt4', 'nose', 'wx', 'scipy',
            'tcl', 'Tkinter', 'compiler']
dllexcludes = [
            'iconv.dll','intl.dll','libatk-1.0-0.dll',
            'libgdk_pixbuf-2.0-0.dll','libgdk-win32-2.0-0.dll',
            'libglib-2.0-0.dll','libgmodule-2.0-0.dll',
            'libgobject-2.0-0.dll','libgthread-2.0-0.dll',
            'libgtk-win32-2.0-0.dll','libpango-1.0-0.dll',
            'libpangowin32-1.0-0.dll', 'libcairo-2.dll',
            'libfontconfig-1.dll', 'libpangoft2-1.0-0.dll',
            'libxml2.dll', 'zlib1.dll', 'libglade-2.0-0.dll',
            'libpangocairo-1.0-0.dll', 'tck85.dll', 'tk85.dll']

opts = {'py2exe': {
                   'packages': ['encodings', 'matplotlib', 'pytz'],
                   'includes': includes,
                   'excludes': excludes,
                   'dll_excludes': dllexcludes,
                   'skip_archive': True,
                   }
        }

data_files = [('', docfiles),
              ('data', datafilelist)] + matplotlib.get_py2exe_datafiles()

long_description = open('README').read()

setup(
    name = 'Acciones-CTE',
    author = 'Rafael Villar Burke',
    author_email='pachi@rvburke.com',
    url='http://www.rvburke.com',
    description = 'Aplicación para el cálculo de condensaciones según CTE',
    long_description = long_description,
    version = '0.01',
    windows = [
        {'script': 'bin/run.py',
        #'icon_resources': [(1, 'notepad.exe')]
        }
    ],
    packages=['condensaciones'],
    options=opts,
    data_files=data_files
)
