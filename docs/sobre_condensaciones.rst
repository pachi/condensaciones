.. _sobre_condensaciones:
==============
Condensaciones
==============

.. _descripcion_general:
Descripción general
===================

**Condensaciones** es una aplicación que permite realizar el **cálculo de los parámetros higrotérmicos** de cerramientos y la **comprobación de la existencia de condensaciones** *superficiales* o *intersticiales*.

Los cerramientos se definen por el material y espesor de cada capa, permitiendo importar mediante una aplicación auxiliar las propiedades de materiales de bases de datos como la de LIDER_/CALENER_.

La aplicación usa la formulación del `Código Técnico de la Edificación (CTE)`_ (**DB-HS**) para el cálculo de los parámetros de los cerramientos y la existencia de condensaciones y, complementariamente, los métodos definidos en la norma **ISO EN 13788:2002**.

.. _funcionalidad:
Funcionalidad
=============

La aplicación se encuentra todavía en fase de desarrollo, por lo que algunas funciones no están del todo desarrolladas o solamente están disponibles a través de la interfaz de programación.

La aplicación permite:

* **Definir las condiciones climáticas de cálculo**, exteriores e interiores, bien mediante su introducción directa o a partir de una **base de datos de localidades**, con datos climáticos mensuales.
* **Gestionar una biblioteca de cerramientos**, pudiendo añadir, eliminar o modificar los cerramientos almacenados.
* **Modificar la composición de los cerramientos de la biblioteca**, alterando su material, espesor, orden y número de capas.
* **Importar bases de datos de materiales** en formato LIDER_/CALENER_ para su uso en la definición de las capas de los cerramientos.
* **Representar gráficamente la distribución de temperaturas** en el interior del cerramiento.
* **Representar gráficamente la distribución de presiones** y presiones de saturación en el interior del cerramiento.
* **Calcular el coeficiente de transmisión térmica U** del cerramiento.
* **Calcular el factor de resistencia superficial** del cerramiento.
* **Mostrar la resistencias térmica** de cada una de las capas intermedias del cerramiento.
* **Comprobar la existencia de condensaciones superficiales o intersticiales**.
* **Calcular la cantidad de condensados** (o agua evaporada) en cada capa.
* **Emitir un informe** completo de los distintos cálculos y comprobaciones.

.. _licencia:
Licencia (GPL2+)
================

Condensaciones es `software libre`_ multiplataforma (GNU/Linx, Windows, MacOSX...) y se publica bajo licencia GPL_ en su versión 2 o posterior.

La aplicación ha sido escrita por `Rafael Villar Burke`_ usando el lenguaje Python_ y las bibliotecas PyGTK_ y Matplotlib_ para la interfaz gráfica y la generación de diagramas.

En la `página de desarrollo del proyecto`_ está disponible su `código fuente e instaladores`_, para facilitar su uso.

.. note::

    Condensaciones se distribuye con la esperanza de que resulte útil, pero SIN NINGUNA GARANTÍA, ni garantía MERCANTIL implícita, ni la CONVENIENCIA PARA UN PROPÓSITO PARTICULAR.

.. _software libre: https://secure.wikimedia.org/wikipedia/es/wiki/Software_libre
.. _GPL: https://secure.wikimedia.org/wikipedia/es/wiki/GNU_General_Public_License
.. _Python: http://www.python.org
.. _PyGTK: http://www.pygtk.org
.. _Matplotlib: http://matplotlib.sourceforge.net
.. _Rafael Villar Burke: http://www.rvburke.com
.. _código fuente e instaladores: https://bitbucket.org/pachi/condensaciones/downloads/
.. _página de desarrollo del proyecto: https://bitbucket.org/pachi/condensaciones/
.. _LIDER: http://www.codigotecnico.org/cte/opencms/web/recursos/aplicaciones/contenido/texto_0002.html
.. _CALENER: http://www.mityc.es/energia/desarrollo/EficienciaEnergetica/CertificacionEnergetica/ProgramaCalener/Paginas/DocumentosReconocidos.aspx
.. _Código Técnico de la Edificación (CTE): http://www.codigotecnico.org/
