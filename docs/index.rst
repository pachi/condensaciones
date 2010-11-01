.. Entrada a la documentación de Condensaciones

Condensaciones
==============

**Condensaciones** es una aplicación para el cálculo de los *parámetros higrotérmicos* de cerramientos y la comprobación de la existencia de *condensaciones superficiales o intersticiales*.

Los cerramientos se definen por el material y espesor de cada capa, permitiendo importar mediante una aplicación auxiliar las propiedades de materiales de bases de datos como la de LIDER_ / CALENER_.

La aplicación usa la formulación del `Código Técnico de la Edificación (CTE)`_ (**DB-HS**) para el cálculo de los parámetros de los cerramientos y la existencia de condensaciones y, complementariamente, los métodos definidos en la norma **ISO EN 13788:2002**.

Funcionalidad de la aplicación
------------------------------

La aplicación se encuentra todavía en fase de desarrollo y por ello gran parte de su funcionalidad no es accesible directamente (aunque sí desde las librerías base).

En estos momentos la aplicación permite:

* definir las condiciones climáticas exteriores e interiores introduciéndolas directamente o seleccionándolas a partir de una **base de datos de localidades**, con datos climáticos mensuales.
* crear una **biblioteca de cerramientos**, pudiendo modificando el material, espesor, orden y número de sus capas.
* mostrar la **distribución de temperaturas** en el interior del cerramiento.
* mostrar la **distribución de presiones** y presiones de saturación en el interior del cerramiento.
* calcular el **coeficiente de transmisión térmica**, **factor de resistencia superficial** y **resistencias térmicas** intermedias del cerramiento.
* **comprobar la existencia de condensaciones** superficiales e intersticiales.
* calcular la **cantidad de agua condensada** (o evaporada) en cada capa.
* producir un **informe** completo del cálculo y sus comprobaciones.

Licencia
--------

Condensaciones es `software libre`_ multiplataforma (GNU/Linx, Windows, MacOSX...) y se publica bajo licencia GPL_ en su versión 2 o posterior.

La aplicación ha sido escrita por `Rafael Villar Burke`_ usando el lenguaje Python_ y las bibliotecas PyGTK_ y Matplotlib_ para la interfaz gráfica y la generación de diagramas.

En la `página de desarrollo del proyecto`_ están disponibles el `código fuente e instaladores`_ para facilitar su uso.

.. note::

    Condensaciones se distribuye con la esperanza de que resulte útil, pero SIN NINGUNA GARANTÍA, ni garantía MERCANTIL implícita, ni la CONVENIENCIA PARA UN PROPÓSITO PARTICULAR.

Esta documentación corresponde a la versión |release| (|today|).

Documentación
=============

.. toctree::
   :maxdepth: 2

   instalacion
   manual_usuario
   api_reference

..  Índices y tablas
    ================

    * :ref:`genindex`
    * :ref:`search`

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
