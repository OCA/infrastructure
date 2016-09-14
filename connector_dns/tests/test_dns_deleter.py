# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.addons.connector_dns.unit import delete_synchronizer

from .common import SetUpDNSBase


model = 'openerp.addons.connector_dns.unit.delete_synchronizer'


class EndTestException(Exception):
    pass


class TestDNSDeleter(SetUpDNSBase):

    def setUp(self):
        super(TestDNSDeleter, self).setUp()
        self.model = 'dns.zone.bind'
        self.dns_id = 'dns_id'
        self.binding_id = 1234
        self.Exporter = delete_synchronizer.DNSDeleter

    def _new_exporter(self, dns_id=None, binding_record=None,
                      binding_id=None,
                      ):
        exporter = self.Exporter(self.get_dns_helper(
            self.model
        ))
        exporter.dns_id = dns_id
        exporter.binding_record = binding_record
        exporter.binding_id = binding_id
        return exporter

    def _new_record(self, sync_date=False):
        return self.env[self.model].create({
            'name': 'Test',
            'sync_date': sync_date,
            'warehouse_id': self.env.ref('stock.warehouse0').id,
        })

    def test_run_not_implemented(self):
        """ It should raise NotImplementedError """
        with self.assertRaises(NotImplementedError):
            self._new_exporter().run(True)
