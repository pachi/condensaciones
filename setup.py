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
import shutil
from glob import glob
from distutils.core import setup
from condensaciones import __version__

# Remove 'build' dir and recreate 'dist' dir
if os.path.isfile('MANIFEST'):
    os.remove('MANIFEST')
shutil.rmtree("build", ignore_errors=True)
shutil.rmtree("dist", ignore_errors=True)
os.mkdir("dist")

DATA_FILES = [('', 'README.txt NEWS.txt INSTALL.txt COPYING.txt'.split()),
              ('data', glob('data/*.ui')),
              ('data', glob('data/*.ini')),
              ('data', ['data/splash.png']),
              ('data/icons', glob('data/icons/*.png')),
              ('report', ['report/style.css'])]

if 'py2exe' in sys.argv:
    import py2exe
    from matplotlib import get_py2exe_datafiles

    # Copy MSVC Runtime
    shutil.copytree("MSVCCRT", "./dist/Microsoft.VC90.CRT")

    # Copy GTK+ runtime files
    def ignore_files(adir, files):
        return set([f for f in files if (not f.endswith('.dll') and
                                         not os.path.isdir(os.path.join(adir,f)))])
    GTKBASE = 'C:/winp/Gtk+/'
    shutil.copytree(GTKBASE + 'etc', './dist/etc')
    shutil.copytree(GTKBASE + 'lib', './dist/lib', ignore=ignore_files)
    shutil.copytree(GTKBASE + 'share/themes/MS-Windows', './dist/share/themes/MS-Windows')
    shutil.copytree(GTKBASE + 'share/locale/es', './dist/share/locale/es')

    # Enable the MS-Windows theme.
    #f = open(os.path.join(self.exe_dir, 'etc', 'gtk-2.0', 'gtkrc'), 'w')
    #print >>f, 'gtk-theme-name = "MS-Windows"'
    #f.close()

    nsifile = open("setup.nsi.in", "rb").read()
    nsifile = nsifile.replace("@VERSION@", __version__)
    open("setup.nsi", "wb").write(nsifile)

    PY2EXE_PACKAGES = ['encodings', 'matplotlib', 'pytz']
    PY2EXE_INCLUDES = 'cairo,pango,pangocairo,atk,gobject,gio'
    PY2EXE_EXCLUDES = ('_wxagg _fltkagg _cocoaagg _gtkagg _tkagg email logging '
                       'PyQt4 nose wx scipy tcl Tkinter compiler json jinja2 '
                       'pygments sphinx').split()
    PY2EXE_DLL_EXCLUDES = ('iconv.dll libxml2.dll tcl85.dll tk85.dll '
                           'pywintypes26.dll POWRPROF.dll DNSAPI.dll '
                           'MSIMG32.DLL libglade-2.0-0.dll').split()

    kwargs = {'windows': [{'script':'bin/condensa',
                           'description':'Condensa - Cálculo de condensaciones',
                           'icon_resources':[(0, 'data/icons/logo.ico')]}],
              'console':[{'script':'bin/importDB',
                          'description':'Conversor de BBDD Lider/CALENER a BBDD Condensa',
                          'icon_resources':[(0, 'data/icons/logo.ico')]}],
              'options':{'py2exe':{'packages': PY2EXE_PACKAGES,
                                   'includes': PY2EXE_INCLUDES,
                                   'excludes': PY2EXE_EXCLUDES,
                                   'dll_excludes': PY2EXE_DLL_EXCLUDES,
                                   'skip_archive': True, # no crear library.zip
                                   #'bundle_files': 3, # no comprimir
                                   'compressed': False,
                                   #'optimize': 2
                                   }},
              'data_files': DATA_FILES + get_py2exe_datafiles()}
else:
    kwargs = {'data_files': DATA_FILES}

setup(name='Acciones-CTE',
      version=__version__,
      author='Rafael Villar Burke',
      author_email='pachi@rvburke.com',
      url='http://www.rvburke.com',
      description='Aplicación para el cálculo de condensaciones según CTE',
      long_description=open('README.txt').read(),
      license="GNU GPL2+",
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
        'Programming Language :: Python'],
      packages=['condensaciones', 'condensaciones.test'],
      scripts=['bin/condensa', 'bin/importDB'],
      **kwargs
)
