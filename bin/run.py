#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
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

# Para permitir ejecución sin instalar
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.abspath('.'), '..')))

import condensaciones
from condensaciones.capas import Cerramiento
from condensaciones.gtkui import GtkCondensa
from condensaciones.datos_ejemplo import climae, climai, murocapas

muro = Cerramiento("Cerramiento tipo", "Descripción", murocapas, 0.04, 0.13)
app = GtkCondensa(muro, climae, climai)
app.main()