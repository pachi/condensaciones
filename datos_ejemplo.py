#!/usr/bin/env python
#encoding: iso-8859-15

class Clima(object):
    def __init__(self, temp, HR):
        self.temp = float(temp)
        self.HR = float(HR)

climae1 = Clima(10.7, 79) #datos enero Sevilla
climae2 = Clima(5, 96) #datos para provocar condensaciones
climai1 = Clima(20.0, 55) #según clase de higrometría: 3:55%, 4:62%, 5:70%

climae = climae2
climai = climai1

capas1 = [("1/2 pie LP métrico o catalán 40 mm< G < 60 mm", 0.11),
        ("Mortero de áridos ligeros [vermiculita perlita]", 0.01),
        ("EPS Poliestireno Expandido [ 0.037 W/[mK]]", 0.03),
        ("Tabique de LH sencillo [40 mm < Espesor < 60 mm]", 0.03),
        ("Enlucido de yeso 1000 < d < 1300", 0.01),]
valores1 = {"U":0.804, "S_total":2.16, "fRsi":0.80}

capas2 = [("Granito [2500 < d < 2700]", 0.03),
        ("Mortero de cemento o cal para albañilería y para revoco/enlucido 1800 < d < 2000", 0.02),
        ("XPS Expandido con dióxido de carbono CO2 [ 0.034 W/[mK]]", 0.05),
        ("Tabicón de LH doble  [60 mm < E < 90 mm]", 0.14),
        ("Enlucido de yeso 1000 < d < 1300", 0.015),]
valores2 = {"U":0.496, "S_total":316.69, "fRsi":0.88}

capas3 = [("Granito [2500 < d < 2700]", 0.03),
        ("Mortero de cemento o cal para albañilería y para revoco/enlucido 1800 < d < 2000", 0.02),
        ("XPS Expandido con dióxido de carbono CO2 [ 0.034 W/[mK]]", 0.05),
        ("Tabicón de LH doble  [60 mm < E < 90 mm]", 0.14),
        ("B_Vapor Al (d_0.008mm)", 0.000008),
        ("Enlucido de yeso 1000 < d < 1300", 0.015),]
valores3 = {"U":0.496, "S_total":1106.69, "fRsi":0.88}

capas4 = [
        ("XPS Expandido con dióxido de carbono CO2 [ 0.034 W/[mK]]", 0.05),
        ("Placa de yeso laminado [PYL] 750 < d < 900", 0.015),
        ("MW Lana mineral [0.031 W/[mK]]", 0.080),
        ("MW Lana mineral [0.031 W/[mK]]", 0.040),
        ("Placa de yeso laminado [PYL] 750 < d < 900", 0.0125),
        ("Placa de yeso laminado [PYL] 750 < d < 900", 0.0125)]
valores4 = {"U":0.176, "S_total":5.28, "fRsi":0.36}

capas5 = [
        ("EPS Poliestireno Expandido [ 0.037 W/[mK]]", 0.05),
        ("Placa de yeso laminado [PYL] 750 < d < 900", 0.015),
        ("MW Lana mineral [0.031 W/[mK]]", 0.080),
#        ("Cámara de aire sin ventilar horizontal 2 cm", 0.015),
        ("XPS Expandido con dióxido de carbono CO2 [ 0.034 W/[mK]]", 0.05),
        ("Placa de yeso laminado [PYL] 750 < d < 900", 0.0125),
        ("Placa de yeso laminado [PYL] 750 < d < 900", 0.0125)]
valores5 = {"U":0.175, "S_total":6.24, "fRsi":0.36}

capas6 = [
        ("EPS Poliestireno Expandido [ 0.037 W/[mK]]", 0.05),
        ("Placa de yeso laminado [PYL] 750 < d < 900", 0.015),
        ("MW Lana mineral [0.031 W/[mK]]", 0.080),
#        ("Cámara de aire sin ventilar horizontal 2 cm", 0.015),
        ("B_Vapor Al (d_0.008mm)", 0.000008),
        ("MW Lana mineral [0.031 W/[mK]]", 0.040),
        ("Placa de yeso laminado [PYL] 750 < d < 900", 0.0125),
        ("Placa de yeso laminado [PYL] 750 < d < 900", 0.0125)]
valores6 = {"U":0.181, "S_total":801.28, "fRsi":0.36}

murocapas = capas1
