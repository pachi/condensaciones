#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   condensaciones.py
#   Programa de c�lculo de condensaciones seg�n CTE
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
"""Conversión de BBDD de Lider / Calener a BBDD ConfigObj"""

import os, sys
import optparse
if not hasattr(sys, 'frozen'):
    currpath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.append(currpath)
from condensaciones import dbutils

usage = "%prog [opciones] archivo1 [archivo2] ..."
parser = optparse.OptionParser(usage=usage)
parser.add_option('-o', '--outfile',
                  action="store", default="DB.ini", dest="outfile",
                  help="Archivo de salida ('%default' por defecto)")
(options, args) = parser.parse_args()
ofile = options.outfile
files = args
if args:
    nmats, ngroups = dbutils.DB2ini(files, ofile)
    print "Convertidos %i materiales en %i grupos" % (nmats, ngroups)
else:
    print "Importa BBDD de LIDER/CALENER para Condensaciones"
    print "Copyright (C) 2007-2010 Rafael Villar Burke <pachi@rvburke.com>"
    print
    parser.print_help()
