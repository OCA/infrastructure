# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import mock

from openerp.addons.connector_dns.unit import import_synchronizer

from .common import SetUpDNSBase

model = 'openerp.addons.connector_dns.unit.import_synchronizer'


class EndTestException(Exception):
    pass


class TestBatchImporter(SetUpDNSBase):

    def setUp(self):
        super(TestBatchImporter, self).setUp()
        self.Importer = import_synchronizer.BatchImporter
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

    def test_run_search_no_filter(self):
        """ It should create a blank dict on no filter """
        expect = {}
        importer = self._new_importer()
        with self.mock_adapter(importer):
            importer.backend_adapter.search.side_effect = EndTestException
            with self.assertRaises(EndTestException):
                importer.run()
            importer.backend_adapter.search.assert_called_once_with(
                **expect
            )

    def test_run_search(self):
        """ It should search backend adapter w/ filters """
        expect = {'expect': 1234, 'test': 45456}
        importer = self._new_importer()
        with self.mock_adapter(importer):
            with mock.patch.object(importer, '_import_record'):
                importer.backend_adapter.search.side_effect = EndTestException
                with self.assertRaises(EndTestException):
                    importer.run(expect)
            importer.backend_adapter.search.assert_called_once_with(
                **expect
            )

    def test_run_import(self):
        """ It should import record """
        expect = ['expect']
        importer = self._new_importer()
        with self.mock_adapter(importer):
            with mock.patch.object(importer, '_import_record'):
                importer.backend_adapter.search.return_value = expect
                importer._import_record.side_effect = EndTestException
                with self.assertRaises(EndTestException):
                    importer.run()
                importer._import_record.assert_called_once_with(
                    expect[0]
                )

    def test_import_record(self):
        """ It should raise NotImplemented on base class """
        importer = self._new_importer()
        with self.assertRaises(NotImplementedError):
            importer._import_record(True)
