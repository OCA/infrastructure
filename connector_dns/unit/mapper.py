# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.addons.connector.unit.mapper import (mapping,
                                                  ImportMapper,
                                                  )


class DNSImportMapper(ImportMapper):
    """ It provides a default mapper class to be used for all DNS mappers """

    @mapping
    def dns_backend_id(self, record):
        return {'dns_backend_id': self.backend_record.id}
