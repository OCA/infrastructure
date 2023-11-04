.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3



Installation
============

To install this module, you need to install the odoo-connector module.

Configuration
=============

To configure this module, you need to:

#. Install a specific module such as connector_dns_dnspod
#. Create and set up the authentication for the DNS service provider in
   Connectors/DNS/backends

Usage
=====

To use this module, you need to:

#. Create your domains, select the DNS provider and confirm them in
   Connectors/DNS/Domains
#. Once the domains are created, you can create the records accordingly
   in Connectors/DNS/records
#. Every time you create, delete or update a new record, a job will be
   created in Connectors/Queue/Jobs 
#. if a job fails, you can check the error and retry the job if necessary.

You might want to check the official documentation of the
`Odoo Connector <http://odoo-connector.com/index.html>`_ to build your own
DNS provider connector.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/224/8.0

Known issues / Roadmap
======================

* Add validations for record types: ``SPF``, ``NAPTR``
* Add a delete synchronizer
* Add tests for each of the ``dns.record.type`` validation regexes
* Add missing tests for ``export_synchronizer`` & ``import_synchronizer``

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/infrastructure-dns/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------



Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
