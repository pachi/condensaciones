#!/usr/bin/env python
#encoding: utf-8
#
#   condensaciones.py
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
"""Informe html de cálculo de condensaciones"""

import datetime
from .util import config

__HTMLTEMPLATE = u"""
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
"http://www.w3.org/TR/html4/loose.dtd">
<html>
    <head>
        <META HTTP-EQUIV="CONTENT-TYPE" CONTENT="text/html; charset=utf-8" />
        <title>Informe</title>
        <link rel="stylesheet" type="text/css" href="style.css" />
    </head>
    <body><div class="container">
        <h1>Informe de resultados</h1>

        <h2>Descripción del cerramiento</h2>
        <h3>%(nombrecerramiento)s</h3>
        <h4>%(descripcioncerramiento)s</h4>
        %(capaslist)s
        <h3>Transmitancia térmica total: U = %(U).3f [W/m²K]</h3>

        <h2>Gráficas de presión, temperatura y presión de saturación</h2>
        <h3>Condiciones de cálculo seleccionadas</h3>
        <p>Ambiente exterior (gráficas): %(ambienteexterior)s</p>
        <p>T: %(tempext).1f ºC, HR: %(HRext).1f %%</p>
        <p>Ambiente interior (gráficas): %(ambienteinterior)s</p>
        <p>T: %(tempint).1f ºC, HR: %(HRint).1f %%</p>
        <br />
        <img src="presionestempplot.png" alt="Gráfica de presiones y temperaturas" title="Gráfica de presiones y temperaturas" />
        <br /><br />
        <img src="condensacionesplot.png" alt="Gráfica de condensaciones por periodos" title="Gráfica de condensaciones por periodos" />

        <h2>Comportamiento higrotérmico y cumplimiento del CTE</h2>
        <h3>Condiciones de cálculo para la comprobación de condensaciones superficiales</h3>
        <p>Exterior - T: %(tempextcs).1f ºC, HR: %(HRextcs).1f %%</p>
        <p>Interior - T: %(tempintcs).1f ºC, HR: %(HRintcs).1f %%</p>
        <h3>Condiciones de cálculo para la comprobación de condensaciones intersticiales</h3>
        <p>Exterior - T [ºC]: %(tempextlistci)s, HR [%%]: %(HRextlistci)s</p>
        <p>Interior - T: %(tempintci).1f ºC, HR: %(HRintci).1f %%</p>
        
        <h3>Factores de resistencia superficial</h3>
        <p>f_Rsi = %(fRsi).2f</p>
        <p>f_Rsimin = %(fRsimin).2f</p>

        <h3>Existencia de condensaciones</h3>
        <p>¿Existen condensaciones superficiales?: %(cs)s</p>
        <p>¿Existen condensaciones intersticiales?: %(ci)s</p>

        <p>%(cimeses)s</p>
        <hr />
        <p>Informe generado por <a href="http://www.rvburke.com/condensaciones.html">Condensa</a> el %(today)s</p>
        <p>'Condensa' es software libre que se distribuye bajo licencia GPLv2 o posterior.</p>
        <p>Copyright (c) 2009-2010 Rafael Villar Burke</p>
        </div>
    </body>
</html>
"""

def capaslist(model):
    """Genera tabla con descripción de nudos"""
    _table = (u'<table><thead>'
              u'<tr><th>i</th><th>Descripción de la capa</th>'
              u'<th class="center">espesor<br />[m]</th>'
              u'<th class="center">K<br />[W/mK]</th>'
              u'<th class="center">R<br />[m²K/W]</th>'
              u'<th class="center">μ<br />[-]</th>'
              u'<th class="center">S<br />[m]</th></tr>'
              u'</thead><tbody>%s %s %s %s %s</tbody></table>')
    _s = (u'<tr><td class="index">%d</td><td class="name">%s</td>'
          u'<td class="center">%.3f</td><td class="center">%.3f</td>'
          u'<td class="center">%.3f</td><td class="center">%i</td>'
          u'<td class="center">%.3f</td>'
          u'</tr>')
    _rows = u"".join(_s % (i, nombre, e, K or 0.0, R, mu, S)
                    for i, (nombre, e, K, R, mu, S, color)
                    in model.capasdata())
    _r1 = (u'<tr><td colspan="7" class="seprow"></td></tr>'
           u'<tr>'
           u'<td></td><td class="right">Totales capas:</td>'
           u'<td class="center bold">%.3f</td>'
           u'<td></td><td class="center bold">%.3f</td>'
           u'<td></td><td class="center bold">%.3f</td></tr>'
           ) % (model.c.e, model.c.R_total, model.c.S_total)
    _r2 = (u'<tr><td></td>'
           u'<td class="right">Resistencia superficial exterior - Rse:</td>'
           u'<td></td><td></td><td class="center bold">%.3f</td></tr>'
           ) % model.c.Rse
    _r3 = (u'<tr><td></td>'
           u'<td class="right">Resistencia superficial interior - Rsi:</td>'
           u'<td></td><td></td><td class="center bold">%.3f</td></tr>'
           ) % model.c.Rsi
    _r4 = (u'<tr><td colspan="7" class="seprow"></td></tr>'
           u'<tr><td></td><td class="right">Totales cerramiento:</td>'
           u'<td></td><td></td><td class="center bold">%.3f</td></tr>'
           ) % model.c.R_total
    return _table % (_rows, _r1, _r2, _r3, _r4)

def createreport(ui, model):
    """Genera el informe de resultados"""
    today = datetime.datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
    tempextlistci = u", ".join(u"%.1f" % clima.temp for clima in model.climaslist)
    HRextlistci = u", ".join(u"%.1f" % clima.HR for clima in model.climaslist)
    cs = u"Sí" if model.cs else u"No"
    ci = u"Sí" if model.ci else u"No"
    if model.ci:
        meses = u", ".join(u"%i" % i for i, value in enumerate(model.glist) if value)
        cimeses = u"\nPeriodos con condensaciones intersticiales: %s\n" % meses
    else:
        cimeses = u''

    s = __HTMLTEMPLATE % {u'nombrecerramiento': model.c.nombre,
                          u'descripcioncerramiento': model.c.descripcion,
                          u'capaslist': capaslist(model),
                          u'U': model.c.U,
                          #Hacer tablas mejor que esto
                          u'tempext': model.climae.temp,
                          u'HRext': model.climae.HR,
                          u'tempint': model.climai.temp,
                          u'HRint': model.climai.HR,
                          #Hacer tablas mejor que esto
                          u'tempextcs': model.climaslist[0].temp,
                          u'HRextcs': model.climaslist[0].HR,
                          u'tempintcs': 20.0,
                          u'HRintcs': model.climai.HR,
                          #Hacer tablas mejor que esto
                          u'tempextlistci': tempextlistci,
                          u'HRextlistci': HRextlistci,
                          u'tempintci': 20.0,
                          u'HRintci': model.climai.HR,
                          #
                          u'ambienteexterior': model.ambienteexterior,
                          u'ambienteinterior': model.ambienteinterior,
                          u'fRsi': model.fRsi,
                          u'fRsimin': model.fRsimin,
                          u'cs': cs,
                          u'ci': ci,
                          u'cimeses': cimeses,
                          #
                          u'today': today
                          }
    filename = config.userresource('report', 'report.html')
    rfile = open(filename, "w")
    rfile.write(s.encode('utf-8'))
    rfile.close()
    # Se dibujan y guardan todos los diagramas
    graficaprestemp = ui.get_object('prestemp_canvas')
    graficacondensaciones = ui.graficacondensaciones
    filename = config.userresource('report','presionestempplot.png')
    graficaprestemp.save(filename)
    filename = config.userresource('report','condensacionesplot.png')
    graficacondensaciones.save(filename)
