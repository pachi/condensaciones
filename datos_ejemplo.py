#!/usr/bin/env python
#encoding: iso-8859-15

#Resistencia t�rmica                    e       mu      K       R       S
#Nombre                                 [m]     [-]     [W/mK]  [m�K/W] [m]
#1/2 pie LP m�trico o catal�n 40 mm<    0.11    10      0.69    0.16    1.1
#Mortero_de_�ridos_ligeros_[vermiculita 0.01    10      0.41    0.02    0.1
#EPS Poliestireno Expandido             0.03    20      0.037   0.81    0.6
#Tabique de LH sencillo [40 mm < Esp    0.03    10      0.44    0.07    0.3
#Enlucido_de_yeso_1000<d<1300           0.01    6       0.57    0.02    0.06
#Rse                                                            0.04
#Rsi (cerramientos verticales)                                  0.13
#Resistencia total (m�K/W)                                      1.25
capas = [("1/2 pie LP m�trico o catal�n 40 mm<", 0.11, 10.0, 0.69),
        ("Mortero_de_�ridos_ligeros_[vermiculita", 0.01, 10.0, 0.41),
        ("EPS Poliestireno Expandido", 0.03, 20.0, 0.037),
        ("Tabique de LH sencillo [40 mm < Esp", 0.03, 10.0, 0.44),
        ("Enlucido_de_yeso_1000<d<1300", 0.01, 6.0, 0.57),]
