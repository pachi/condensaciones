#!/usr/bin/env python
#encoding: utf-8
import operator
import psicrom
import materiales

class Cerramiento(object):
    def __init__(self, nombre, capas, Rse=None, Rsi=None):
        self.nombre = nombre
        self.capas = capas
        self.Rse = Rse
        self.Rsi = Rsi

    @property
    def nombre_capas(self):
        "Nombre de las capas"
        return [nombre for nombre, e in self.capas]

    @property
    def espesores(self):
        "Espesores de las capas [m]"
        return [e for nombre, e in self.capas]

    @property
    def espesores_acumulados(self):
        return [0.0] + [reduce(operator.add, self.espesores[:i]) for i in range(1, len(self.espesores)+1)]

    @property
    def R(self):
        "Resistencia térmica de las capas [m²K/W]"
        def resist_capa(capa, e=None):
            tipo = materiales.tipo(nombre)
            if tipo == 'PROPERTIES':
                return e / materiales.conductividad(nombre)
            elif tipo == 'RESISTANCE':
                return materiales.resistencia(nombre)
            else:
                raise
        return [self.Rse] + [resist_capa(nombre, e) for nombre, e in self.capas] + [self.Rsi]

    @property
    def S(self):
        "Espesor de aire equivalente de las capas [m]"
        return [e * materiales.difusividad(nombre) for nombre, e in self.capas]

    @property
    def S_acumulados(self):
        "Espesor de aire equivalente acumulado en cada capa del cerramiento [m]"
        return [0.0] + [reduce(operator.add, self.S[:i]) for i in range(1,len(self.S)+1)]

    @property
    def S_total(self):
        "Espesor de aire equivalente de todo el cerramiento [m]"
        return sum(self.S)

    @property
    def R_total(self):
        """Resistencia térmica total del cerramiento [m²K/W]
        """
        return sum(self.R)

    @property
    def U(self):
        """Transmitancia térmica del cerramiento [W/m²K]
        """
        return 1.0 / self.R_total

    def temperaturas(self, tempext, tempint):
        """Devuelve lista de temperaturas [ºC]:
        temperatura exterior, temperatura superficial exterior,
        temperaturas intersticiales, temperatura superficial interior
        y temperatura interior.
            tempext - temperatura exterior media en el mes de enero
            tempint - temperatura interior de cálculo (20ºC)
        """
        temperaturas = [tempext]
        for capa_Ri in self.R:
            tempj = temperaturas[-1] + (capa_Ri * (tempint - tempext) / self.R_total)
            temperaturas.append(tempj)
        return temperaturas

    def presiones(self, temp_ext, temp_int, HR_ext, HR_int):
        """Devuelve una lista de presiones de vapor [Pa]
        presión de vapor al exterior, presiones de vapor intermedias y presión de vapor interior.
        """
        pres_ext = psicrom.pvapor(temp_ext, HR_ext)
        pres_int = psicrom.pvapor(temp_int, HR_int)
        # La presión al exterior es constante, en el aire y la superficie exterior de cerramiento
        presiones_vapor = [pres_ext, pres_ext]
        for capa_Si in self.S:
            pres_j = presiones_vapor[-1] + capa_Si * (pres_int - pres_ext) / self.S_total
            presiones_vapor.append(pres_j)
        # La presión interior es constante, en la superficie interior de cerramiento y en el aire
        presiones_vapor.append(pres_int)
        return presiones_vapor

    def presionessat(self, tempext, tempint):
        "Presiones de saturación en cada capa [Pa]"
        temperaturas = self.temperaturas(tempext, tempint)
        return [psicrom.psat(temperatura) for temperatura in temperaturas]

    def cantidadcondensacion(self, temp_ext, temp_int, HR_ext, HR_int):
        """Calcular cantidad de condensación y coordenadas (S, presión de vapor)
        de los planos de condensación.
        Devuelve g [g/m²s], puntos_condensacion
        """
        presiones = self.presiones(temp_ext, temp_int, HR_ext, HR_int)
        presiones_sat = self.presionessat(temp_ext, temp_int)
        # calculamos las posiciones x, y correspondientes a espesor de aire equivalente
        # y presiones de saturación
        Scapas = self.S
        x_jo = [0.0] + [reduce(operator.add, Scapas[:i]) for i in range(1,len(Scapas)+1)]
        y_jo = [presiones[1]] + [p for p in presiones_sat[2:-2]] + [presiones[-1]]

        # Calculamos la envolvente convexa inferior de la linea de presiones de saturación
        # partiendo de presion_exterior y presion_interior como extremos.
        # Los puntos de tangencia son los planos de condensación
        def _giraIzquierda((p, q, r)):
            "¿Forman los vectores pq:qr un giro a la izquierda?"
            _det = ((q[0]*r[1] + p[0]*q[1] + r[0]*p[1]) -
                    (q[0]*p[1] + r[0]*q[1] + p[0]*r[1]))
            return (_det > 0) or False

        puntos = [(x, y) for x, y in zip(x_jo, y_jo)]
        envolvente_inf = [puntos[0], puntos[1]]
        for p in puntos[2:]:
            envolvente_inf.append(p)
            while len(envolvente_inf) > 2 and not _giraIzquierda(envolvente_inf[-3:]):
                del envolvente_inf[-2]
        x_j = [x for x, y in envolvente_inf]
        y_j = [y for x, y in envolvente_inf]
        # condensaciones g/m2.s
        g = [(psicrom.tasatransferenciavapor(y_j[n+1], y_j[n+2], x_j[n+1], x_j[n+2]) -
            psicrom.tasatransferenciavapor(y_j[n], y_j[n+1], x_j[n], x_j[n+1]))
            for n in range(len(y_j) - 2)]
        return g, envolvente_inf

    def cantidadevaporacion(self, temp_ext, temp_int, HR_ext, HR_int, interfases):
        """Calcular cantidad de evaporacion devolver coordenadas (S, presión de vapor)
        Devuelve g [g/m²s], puntos_evaporacion
        """
        presiones = self.presiones(temp_ext, temp_int, HR_ext, HR_int)
        presiones_sat = self.presionessat(temp_ext, temp_int)
        # calculamos las posiciones x, y correspondientes a espesor de aire equivalente
        # y presiones de saturación
        Scapas = self.S
        x_jo = [0.0] + [reduce(operator.add, Scapas[:i]) for i in range(1,len(Scapas)+1)]
        y_jo = [presiones[1]] + [p for p in presiones_sat[2:-2]] + [presiones[-1]]

        puntos_evaporacion = [(x_jo[i], y_jo[i]) for i in interfases]
        envolvente_inf = [(x_jo[0], y_jo[0])] + puntos_evaporacion + [(x_jo[-1], y_jo[-1])]
        x_j = [x for x, y in envolvente_inf]
        y_j = [y for x, y in envolvente_inf]
        # evaporaciones g/m2.s
        g = [(psicrom.tasatransferenciavapor(y_j[n+1], y_j[n+2], x_j[n+1], x_j[n+2]) -
            psicrom.tasatransferenciavapor(y_j[n], y_j[n+1], x_j[n], x_j[n+1]))
            for n in range(len(y_j) - 2)]
        return g, envolvente_inf

if __name__ == "__main__":
    from datos_ejemplo import climae, climai, murocapas
    from util import stringify

    Rs_ext = 0.04
    Rs_int = 0.13
    muro = Cerramiento("Cerramiento tipo", murocapas, Rs_ext, Rs_int)

    temperaturas = muro.temperaturas(climae.temp, climai.temp)
    presiones_sat = muro.presionessat(climae.temp, climai.temp)
    presiones = muro.presiones(climae.temp, climai.temp, climae.HR, climai.HR)
    p_ext = presiones[1]
    p_int = presiones[-1]

    g, puntos_condensacion = muro.cantidadcondensacion(climae.temp, climai.temp, climae.HR, climai.HR)
    cantidad_condensada = sum(g)
    # indicamos evaporación en la interfase 2, pero en realidad habría que ver en cúales había antes
    # condensaciones y realizar el cálculo en ellas.
    g, puntos_evaporacion = muro.cantidadevaporacion(climae.temp, climai.temp, climae.HR, climai.HR, interfases=[2])
    cantidad_evaporada = sum(g)

    print u"Cerramiento:\n\t", muro.nombre
    print u"Nombre capas:\n\t", "\n\t".join(muro.nombre_capas)
    print
    print u"Espesores:\n\t", stringify(muro.espesores, 2)
    print u"Espesores acumulados:\n\t", stringify(muro.espesores_acumulados, 2)
    print u"R Capas:\n\t", stringify(muro.R, 2)
    print u"S Capas:\n\t", stringify(muro.S, 2)
    print u"S acumulados:\n\t", stringify(muro.S_acumulados, 2)
    print u"S total:", muro.S_total # Espesor de aire equivalente total (m), 2.16
    print u"Rs_ext: %.3f\nRs_int: %.2f" % (muro.Rse, muro.Rsi)
    print u"R_total: %.3f" % muro.R_total #("Resistencia total (m²K/W)", 1.25)
    print u"U: %.3f" % muro.U # 0.80 W/m^2K = 1/Rtotal
    print
    print u"Temperaturas:\n\t", stringify(temperaturas, 1)
    print u"Presiones de vapor:\n\t", stringify(presiones, 1)
    print u"\tPresión de vapor exterior: %.2f" % p_ext # presión de vapor exterior: 1016.00
    print u"\tPresión de vapor interior: %.2f" % p_int # presión de vapor interior: 1285.32
    print u"Presiones de saturación:\n\t", stringify(presiones_sat, 1)
    print
    print u"Condensaciones:"
    print u"\tCantidad condensada: %.2f [g/m2.mes]" % (2592000.0 * cantidad_condensada,)
    print u"\tCantidad evaporada: %.2f [g/m2.mes]" % (2592000.0 * cantidad_evaporada,)
