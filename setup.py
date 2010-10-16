#!/usr/bin/env python
# encoding: utf-8
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
#
# Py2EXE: python setup.py py2exe
# Indicar en $PYTHONDIR\Lib\site-packages\matplotlib\mpl-data\matplotlibrc
# como default backend GTKCairo -> "backend: GTKCairo"

import os
import sys
import glob
import shutil
from distutils.core import setup

__version__ = "0.5"

# Remove 'build' dir and recreate 'dist' dir
shutil.rmtree("build", ignore_errors=True)
shutil.rmtree("dist", ignore_errors=True)
os.mkdir("dist")

data_files = [('', 'README.txt NEWS.txt INSTALL.txt COPYING.txt'.split()),
              ('data', ['data/condensa.ui', 'data/MaterialesDB.ini',
                        'data/CerramientosDB.ini',
                        'data/ClimaCTE.ini', 'data/splash.png']
              ),
              ('data/icons', ['data/icons/cerramientos.png',
                              'data/icons/clima.png',
                              'data/icons/drop.png']
              ),
              ('report', ['report/style.css']
               )]
opts = {}

if sys.platform == 'win32':
    import py2exe
    from matplotlib import get_py2exe_datafiles
    shutil.copytree("MSVCCRT", "./dist/Microsoft.VC90.CRT")
    data_files += get_py2exe_datafiles() 
    opts['py2exe']= {'packages': ['encodings', 'matplotlib', 'pytz'],
                     'includes': 'cairo, pango, pangocairo, atk, gobject, gio',
                     'excludes': ['_wxagg', '_fltkagg', '_cocoaagg', '_gtkagg',
                                  'email', 'logging', 'PyQt4', 'nose', 'wx',
                                  'scipy', 'tcl', 'Tkinter', 'compiler'],
                     'dll_excludes': 'iconv.dll,libxml2.dll,tcl85.dll,tk85.dll,'\
                                     'pywintypes26.dll,POWRPROF.dll,DNSAPI.dll,'\
                                     'libpangoft2-1.0-0.dll,MSIMG32.DLL,'\
                                     'freetype6.dll,libglade-2.0-0.dll',
                     'skip_archive': True, # para no crear library.zip
                     'optimize': 1}

setup(
    name='Acciones-CTE',
    version=__version__,
    author='Rafael Villar Burke',
    author_email='pachi@rvburke.com',
    url='http://www.rvburke.com',
    description='Aplicación para el cálculo de condensaciones según CTE',
    long_description=open('README.txt').read(),
    license="GNU GPL2+",
    scripts=['bin/condensa', 'bin/importDB'],
    windows=[{'script':'bin/condensa',
              'description':'Condensa - Cálculo de condensaciones',
              'icon_resources':[(0, 'data/icons/logo.ico')]
              }],
    console=[{'script':'bin/importDB',
              'description':'Conversor de BBDD Lider/CALENER a BBDD Condensa',
              'icon_resources':[(0, 'data/icons/logo.ico')]
              }],
    packages=['condensaciones', 'condensaciones.test'],
    options=opts,
    data_files=data_files,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Natural Language :: Spanish',
        'Topic :: Scientific/Engineering',
        'Programming Language :: Python']
)
