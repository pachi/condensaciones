#!/usr/bin/env python
#encoding: iso-8859-15

#Resistencia térmica                    e       mu      K       R       S
#Nombre                                 [m]     [-]     [W/mK]  [m²K/W] [m]
#1/2 pie LP métrico o catalán 40 mm<    0.11    10      0.69    0.16    1.1
#Mortero_de_áridos_ligeros_[vermiculita 0.01    10      0.41    0.02    0.1
#EPS Poliestireno Expandido             0.03    20      0.037   0.81    0.6
#Tabique de LH sencillo [40 mm < Esp    0.03    10      0.44    0.07    0.3
#Enlucido_de_yeso_1000<d<1300           0.01    6       0.57    0.02    0.06
#Rse                                                            0.04
#Rsi (cerramientos verticales)                                  0.13
#Resistencia total (m²K/W)                                      1.25
#U = 0.80
#fRsi = 0.80
#fRsimin = 0.36

capas = [("1/2 pie LP métrico o catalán 40 mm<", 0.11, 10.0, 0.69),
        ("Mortero_de_áridos_ligeros_[vermiculita", 0.01, 10.0, 0.41),
        ("EPS Poliestireno Expandido", 0.03, 20.0, 0.037),
        ("Tabique de LH sencillo [40 mm < Esp", 0.03, 10.0, 0.44),
        ("Enlucido_de_yeso_1000<d<1300", 0.01, 6.0, 0.57),]

#U = 0.49
#fRsi = 0.88
#fRsimin = 0.36
capas2 = [("Piedra compacta", 0.03, 82, 3.5),
        ("Mortero de cemento", 0.02, 18, 1.3),
        ("XPS tipo II", 0.05, 93, 0.034),
        ("Ladrillo hueco", 0.14, 5.5, 0.432),
        ("Enlucido de yeso", 0.015, 11, 0.3),]

#U = 0.49
#fRsi = 0.88
#fRsimin = 0.36
capas3 = [("Piedra compacta", 0.03, 82, 3.5),
        ("Mortero de cemento", 0.02, 18, 1.3),
        ("XPS tipo II", 0.05, 93, 0.034),
        ("Ladrillo hueco", 0.14, 5.5, 0.432),
        ("Film Al 0.000008m", 0.000008, 100000, 160),
        ("Enlucido de yeso", 0.015, 11, 0.3),]
