# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.addons.connector_dns.unit import mapper

from .common import SetUpDNSBase


class TestDNSImporterMapper(SetUpDNSBase):

    def setUp(self):
        super(TestDNSImporterMapper, self).setUp()
        self.Importer = mapper.DNSImportMapper
        self.model = 'dns.zone.bind'
        self.mock_env = self.get_dns_helper(
            self.model
        )
        self.importer = self.Importer(self.mock_env)

    def test_dns_backend_id(self):
        """ It should map backend_id correctly """
        res = self.importer.dns_backend_id(True)
        expect = {'dns_backend_id': self.importer.backend_record.id}
        self.assertDictEqual(expect, res)
