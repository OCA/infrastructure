# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import mock

from openerp.addons.connector_dns.unit import import_synchronizer

from .common import SetUpDNSBase

model = 'openerp.addons.connector_dns.unit.import_synchronizer'


class TestDelayedBatchImporter(SetUpDNSBase):

    def setUp(self):
        super(TestDelayedBatchImporter, self).setUp()
        self.Importer = import_synchronizer.DelayedBatchImporter
        self.model = 'dns.zone.bind'
        self.mock_env = self.get_dns_helper(
            self.model
        )

    def _new_importer(self, dns_id=None, dns_record=None):
        importer = self.Importer(self.mock_env)
        if dns_id is not None:
            importer.dns_id = dns_id
        if dns_record is not None:
            importer.dns_record = dns_record
        return importer

    def test_import_record(self):
        """ It should call import_record w/ proper args """
        importer = self._new_importer()
        expect = 'expect'
        kwargs = {'test1': 1234, 'test2': 5678}
        with mock.patch('%s.import_record' % model) as mk:
            with mock.patch('%s.int_or_str' % model) as int_or_str:
                importer._import_record(expect, **kwargs)
                mk.delay.assert_called_once_with(
                    importer.session,
                    importer.model._name,
                    importer.backend_record.id,
                    int_or_str(expect),
                    **kwargs
                )
