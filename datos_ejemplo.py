#!/usr/bin/env python
#encoding: iso-8859-15

#Resistencia térmica                    e       mu      lambda  R       S
#Nombre                                 [m]     [-]     [W/mK]  [m²K/W] [m]
#1/2 pie LP métrico o catalán 40 mm<    0.11    10      0.69    0.16    1.1
#Mortero_de_áridos_ligeros_[vermiculita 0.01    10      0.41    0.02    0.1
#EPS Poliestireno Expandido             0.03    20      0.037   0.81    0.6
#Tabique de LH sencillo [40 mm < Esp    0.03    10      0.44    0.07    0.3
#Enlucido_de_yeso_1000<d<1300           0.01    6       0.57    0.02    0.06
#Rse                                                            0.04
#Rsi (cerramientos verticales)                                  0.13
#Resistencia total (m²K/W)                                      1.25

#U = 0.804
#fRsi = 0.80
#fRsimin = 0.36
capas = [("1/2 pie LP métrico o catalán 40 mm< G < 60 mm", 0.11),
        ("Mortero de áridos ligeros [vermiculita perlita]", 0.01),
        ("EPS Poliestireno Expandido [ 0.037 W/[mK]]", 0.03),
        ("Tabique de LH sencillo [40 mm < Espesor < 60 mm]", 0.03),
        ("Enlucido de yeso 1000 < d < 1300", 0.01),]

#U = 0.496
#fRsi = 0.88
#fRsimin = 0.36
capas2 = [("Granito [2500 < d < 2700]", 0.03),
        ("Mortero de cemento o cal para albañilería y para revoco/enlucido 1800 < d < 2000", 0.02),
        ("XPS Expandido con dióxido de carbono CO2 [ 0.034 W/[mK]]", 0.05),
        ("Tabicón de LH doble  [60 mm < E < 90 mm]", 0.14),
        ("Enlucido de yeso 1000 < d < 1300", 0.015),]

#U = 0.496
#fRsi = 0.88
#fRsimin = 0.36
capas3 = [("Granito [2500 < d < 2700]", 0.03),
        ("Mortero de cemento o cal para albañilería y para revoco/enlucido 1800 < d < 2000", 0.02),
        ("XPS Expandido con dióxido de carbono CO2 [ 0.034 W/[mK]]", 0.05),
        ("Tabicón de LH doble  [60 mm < E < 90 mm]", 0.14),
        ("Aluminio", 0.000008),
        ("Enlucido de yeso 1000 < d < 1300", 0.015),]

# ver barrera de vapor en Base de datos ... ("Film Al 0.000008m", 0.000008),

capas4 = [
        ("XPS Expandido con dióxido de carbono CO2 [ 0.034 W/[mK]]", 0.05),
        ("Placa de yeso laminado [PYL] 750 < d < 900", 0.015),
        ("MW Lana mineral [0.031 W/[mK]]", 0.080),
        ("MW Lana mineral [0.031 W/[mK]]", 0.040),
        ("Placa de yeso laminado [PYL] 750 < d < 900", 0.0125),
        ("Placa de yeso laminado [PYL] 750 < d < 900", 0.0125),
        ]

capas5 = [
        ("EPS Poliestireno Expandido [ 0.037 W/[mK]]", 0.05),
        ("Placa de yeso laminado [PYL] 750 < d < 900", 0.015),
        ("MW Lana mineral [0.031 W/[mK]]", 0.080),
#         ("Aluminio", 0.0008),
#        ("Cámara de aire sin ventilar horizontal 2 cm", 0.015),
        ("MW Lana mineral [0.031 W/[mK]]", 0.040),
        ("Placa de yeso laminado [PYL] 750 < d < 900", 0.0125),
        ("Placa de yeso laminado [PYL] 750 < d < 900", 0.0125),
        ]
#"EPS Poliestireno Expandido [ 0.037 W/[mK]]"
capas6 = [
        ("EPS Poliestireno Expandido [ 0.037 W/[mK]]", 0.05),
        ("Placa de yeso laminado [PYL] 750 < d < 900", 0.015),
        ("MW Lana mineral [0.031 W/[mK]]", 0.080),
#        ("Cámara de aire sin ventilar horizontal 2 cm", 0.015),
        ("XPS Expandido con dióxido de carbono CO2 [ 0.034 W/[mK]]", 0.05),
        ("Placa de yeso laminado [PYL] 750 < d < 900", 0.0125),
        ("Placa de yeso laminado [PYL] 750 < d < 900", 0.0125),
        ]
#"EPS Poliestireno Expandido [ 0.037 W/[mK]]"
