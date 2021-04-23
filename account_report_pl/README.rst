===========
P&L Report
===========

.. !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! This file is intended to be in every module    !!
   !! to explain why and how it works.               !!
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


.. User https://shields.io for badge creation.
.. |badge1| image:: https://img.shields.io/badge/maturity-Stable-brightgreen
    :target: https://odoo-community.org/page/development-status
    :alt: Stable
.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |badge3| image:: https://img.shields.io/badge/gitlab-calyxservicios--group%2Fodoo%2Fodoo--calyx-lightgray.png?logo=gitlab
    :target: https://gitlab.com/calyxservicios-group/odoo/odoo-calyx
    :alt: calyxservicios-group/odoo/odoo-calyx

|badge1| |badge2| |badge3|

.. !!! Description must be max 2-3 paragraphs, and is required.

This module extends the functionality of Purchase and add field in purchase order for the foreign fields. Besides, add an if
statement in the validation of the document number in purchase invoice

**Table of contents**

.. contents::
   :local:

.. !!! Instalation: must only be present if there are very specific installation instructions, such as installing non-python dependencies.The audience is systems administrators. ] To install this module, you need to: !!!

Install
=======

Search in Applications for Foreign Purchase Order.

.. !!! Configuration: This file is optional, it should explain how to configure the module before using it; it is aimed at advanced users. To configure this module, you need to:

Configure
=========

* Settings -> Purchase
* Write a default text for Special Indications (Exclusive for Foreign Orders)

Usage
=====

* Select OCE in Order Type in Purchase Order.
* Go to "Forgein purchase" page.
* Complete the fields.

Bug Tracker
===========

* Help Contact: `<soporte_odoo@calyxservicios.com.ar>`_


Authors
~~~~~~~

* Calyx Servicios S.A.

Contributors
~~~~~~~~~~~~

* `Calyx Servicios S.A. <http://www.calyxservicios.com.ar/>`_
  
  * Jhone Mendez
  * Federico Gregori
  * Cristian Paradiso

Maintainers
~~~~~~~~~~~

This module is maintained by the Calyx Servicios S.A.

.. image:: https://ss-static-01.esmsv.com/id/13290/galeriaimagenes/obtenerimagen/?width=120&height=40&id=sitio_logo&ultimaModificacion=2020-05-25+21%3A45%3A05
   :alt: Odoo Calyx Servicios S.A.
   :target: http://www.calyxservicios.com.ar/

CALYX SERVICIOS S.A. It is part of the PGK Consultores economic group, member of an important global network, a world organization positioned among the 20 largest consultant-studios in the world.
The PGK Consultores group is one of the 20 largest consultant-studios in Argentina with nearly 200 professionals.

This module is part of the `Custom-Etilfarma <https://github.com/calyxservicios-group/odoo/custom-etilfarma>`_ project on Github.
