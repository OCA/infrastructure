# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import mock

from openerp.addons.connector_dns import consumer

from .common import SetUpDNSBase


mk_file = 'openerp.addons.connector_dns.consumer'


class TestConsumer(SetUpDNSBase):

    def setUp(self):
        super(TestConsumer, self).setUp()
        self.model = 'dns.zone.bind'
        self.binding_id = self._new_record()

    def _new_record(self, bind=True):
        return self.env[self.model].create({
            'name': 'Test DNS',
            'dns_id_external': self.dns_id if bind else None,
        })

    def test_delay_export_context_no_export(self):
        """ It should not export if context prohibits """
        self.session = mock.MagicMock()
        self.session.context = {'connector_no_export': True}
        res = consumer.delay_export(self.session, 0, 0, 0)
        self.assertEqual(None, res)

    def test_delay_export(self):
        """ It should call export_record.delay w/ proper args """
        fields = {'test': 123, 'test2': 456}
        expect = [self.session, self.model, self.binding_id]
        with mock.patch('%s.export_record' % mk_file) as mk:
            consumer.delay_export(*expect, vals=fields)
            mk.delay.assert_called_once_with(*expect, fields=fields.keys())

    def test_delay_export_all_bindings_context_no_export(self):
        """ It should not export if context prohibits """
        self.session = mock.MagicMock()
        self.session.context = {'connector_no_export': True}
        res = consumer.delay_export_all_bindings(self.session, 0, 0, 0)
        self.assertEqual(None, res)

    def test_delay_export_all_bindings(self):
        """ It should call export_record.delay w/ proper args """
        fields = {'test': 123, 'test2': 456}
        send = [self.session, 'dns.zone', self.binding_id.odoo_id.id]
        expect = [self.session, self.model, self.binding_id.id]
        with mock.patch('%s.export_record' % mk_file) as mk:
            consumer.delay_export_all_bindings(*send, vals=fields)
            mk.delay.assert_called_once_with(*expect, fields=fields.keys())
