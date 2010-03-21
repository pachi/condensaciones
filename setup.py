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

from distutils.core import setup
import py2exe
from matplotlib import get_py2exe_datafiles

__version__ = "0.1"

data_files = [('', ['README', 'NEWS', 'INSTALL', 'COPYING']),
              ('data', ['data/condensa.ui', 'data/BDCatalogo.bdc',
                        'data/Catalogo_URSA.bdc', 'data/PCatalogo.bdc',
                        'data/splash.png']
              )] + get_py2exe_datafiles()

opts = {'py2exe': {
                   'packages': ['encodings', 'matplotlib', 'pytz'],
                   'includes': ['cairo', 'pango', 'pangocairo',
                                'atk', 'gobject', 'gio'],
                   'excludes': ['_wxagg', '_fltkagg', '_cocoaagg', '_gtkagg',
                                'email', 'logging', 'PyQt4', 'nose', 'wx',
                                'scipy', 'tcl', 'Tkinter', 'compiler'],
                   'dll_excludes': ['iconv.dll', 'libxml2.dll',
                                    'tcl85.dll', 'tk85.dll'],
                   #'skip_archive': True,
                   }
        }

setup(
    name='Acciones-CTE',
    version=__version__,
    author='Rafael Villar Burke',
    author_email='pachi@rvburke.com',
    url='http://www.rvburke.com',
    description='Aplicación para el cálculo de condensaciones según CTE',
    long_description=open('README').read(),
    license="COPYING",
    #scripts=['bin/run.py'],
    windows=[{'script':'bin/condensa',
              'icon_resources':[(1, 'data/logo.ico')]}],
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
