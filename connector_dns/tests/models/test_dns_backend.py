# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import mock
from datetime import timedelta, datetime

from ..common import SetUpDNSBase

from openerp import fields, models
from openerp.exceptions import ValidationError


model = 'openerp.addons.connector_dns.models.dns_backend'


class TestDNSBackend(SetUpDNSBase):

    def setUp(self):
        super(TestDNSBackend, self).setUp()
        self.Model = self.env['dns.backend']

    def test_check_default_for_company(self):
        """ It should not allow two defaults for the same company """
        with self.assertRaises(ValidationError):
            self.backend.copy()

    def test_select_version(self):
        """ It should return proper versions """
        self.assertIsInstance(
            self.Model._select_version(),
            list,
        )

    @mock.patch('%s.ConnectorSession' % model)
    def test_import_all_gets_session(self, session):
        """ It should get session for import """
        session.side_effect = self.EndTestException
        with self.assertRaises(self.EndTestException):
            self.backend._import_all(None)

    @mock.patch('%s.ConnectorSession' % model)
    def test_import_all_checks_stucture(self, session):
        """ It should check internal structure on all backends """
        with mock.patch.object(self.backend, 'check_dns_structure') as chk:
            chk.side_effect = self.EndTestException
            with self.assertRaises(self.EndTestException):
                self.backend._import_all('model')

    @mock.patch('%s.import_batch' % model)
    @mock.patch('%s.ConnectorSession' % model)
    def test_import_all_calls_import(self, session, batch):
        """ It should call delayed batch import for model """
        expect = 'model'
        self.backend._import_all(expect)
        batch.delay.assert_called_once_with(
            session(), expect, self.backend.id,
        )

    @mock.patch('%s.ConnectorSession' % model)
    def test_import_from_date_checks_stucture(self, session):
        """ It should check internal structure on all backends """
        with mock.patch.object(self.backend, 'check_dns_structure') as chk:
            chk.side_effect = self.EndTestException
            with self.assertRaises(self.EndTestException):
                self.backend._import_from_date(None, None, None)

    @mock.patch('%s.datetime' % model)
    @mock.patch('%s.import_batch' % model)
    @mock.patch('%s.ConnectorSession' % model)
    def test_import_from_date_calls_import(self, session, batch, dt_mk):
        """ It should call delayed batch import for model """
        expect = 'model', 'import_zones_from_date', 'chg'
        dt_mk.now.return_value = datetime.now()
        expect_date = dt_mk.now() - timedelta(days=5)
        self.backend.import_zones_from_date = expect_date
        expect_date = self.backend.import_zones_from_date
        self.backend._import_from_date(*expect)
        batch.delay.assert_called_once_with(
            session(), expect[0], self.backend.id,
            filters={
                expect[2]: {
                    '>=': fields.Datetime.from_string(
                        expect_date,
                    ),
                    '<=': dt_mk.now(),
                },
            }
        )

    @mock.patch('%s.datetime' % model)
    @mock.patch('%s.import_batch' % model)
    @mock.patch('%s.ConnectorSession' % model)
    def test_import_from_date_writes_new_date(self, session, batch, dt_mk):
        """ It should call delayed batch import for model """
        dt_mk.now.return_value = datetime.now()
        expect_date = dt_mk.now() - timedelta(days=5)
        self.backend.import_zones_from_date = expect_date
        self.backend._import_from_date(
            'model', 'import_zones_from_date', 'chg'
        )
        expect = dt_mk.now()
        self.assertEqual(
            fields.Datetime.to_string(expect),
            self.backend.import_zones_from_date,
        )

    def test_import_dns_zones(self):
        """ It should import proper model on date field """
        with mock.patch.object(self.backend, '_import_from_date') as mk:
            self.backend.import_dns_zones()
            mk.assert_called_once_with(
                'dns.zone.bind',
                'import_zones_from_date',
            )

    def test_import_dns_records(self):
        """ It should import proper model on date field """
        with mock.patch.object(self.backend, '_import_from_date') as mk:
            self.backend.import_dns_records()
            mk.assert_called_once_with(
                'dns.record.bind',
                'import_records_from_date',
            )

    def test_name_get(self):
        """ It should conjoin name and login """
        self.assertEqual(
            '%s (%s)' % (self.backend.name, self.backend.login),
            self.backend.display_name,
        )

    def test_resync_all_get_session(self):
        """ It should obtain current session """
        with mock.patch.object(self.backend, '_get_session') as get:
            get.side_effect = self.EndTestException
            with self.assertRaises(self.EndTestException):
                self.backend.resync_all(None, None)

    def test_resync_all_search(self):
        """ It should search for domain on binding model """
        expect = [1, 2]
        with mock.patch.object(self.backend, '_get_session'):
            with mock.patch.object(self.backend, 'env') as env:
                search = env[self.Model._name].search
                search.side_effect = self.EndTestException
                with self.assertRaises(self.EndTestException):
                    self.backend.resync_all(self.Model._name, expect)
                    search.assert_called_once_with(
                        ('dns_backend_id', 'in', expect),
                    )

    def test_resync_all_search_recordset(self):
        """ It should support recordset inputs for convenience """
        expect = mock.MagicMock(spec=models.BaseModel)
        with mock.patch.object(self.backend, '_get_session'):
            with mock.patch.object(self.backend, 'env') as env:
                search = env[self.Model._name].search
                search.side_effect = self.EndTestException
                with self.assertRaises(self.EndTestException):
                    self.backend.resync_all(self.Model._name, expect)
                    search.assert_called_once_with(
                        ('dns_backend_id', 'in', expect.ids),
                    )

    @mock.patch('%s.import_record' % model)
    def test_resync_all_import_record(self, import_record):
        """ It should call delayed import for all bindings """
        record, binding = mock.MagicMock(), mock.MagicMock()
        record.dns_bind_ids = [binding]
        with mock.patch.object(self.backend, '_get_session') as get:
            with mock.patch.object(self.backend, 'env') as env:
                search = env[self.Model._name].search
                search.return_value = [record]
                self.backend.resync_all(self.Model._name)
                import_record.delay.assert_called_once_with(
                    get(),
                    self.Model._name,
                    binding.backend_id.id,
                    binding.dns_id_external,
                    force=True,
                )
