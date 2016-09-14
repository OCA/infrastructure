# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import mock
from openerp.models import BaseModel

from openerp.addons.connector_dns.unit import binder

from .common import SetUpDNSBase


_file = 'openerp.addons.connector_dns.unit.binder'


class TestBinder(SetUpDNSBase):

    def setUp(self):
        super(TestBinder, self).setUp()
        self.model = 'dns.zone.bind'
        self.dns_id = 1234567
        self.Binder = binder.DNSModelBinder

    def _new_binder(self):
        return self.Binder(self.get_dns_helper(
            self.model
        ))

    def test_bind_super(self):
        """ It should call super w/ proper args """
        expect = mock.MagicMock(), mock.MagicMock()
        with mock.patch.object(binder.Binder, 'bind') as mk:
            _binder = self._new_binder()
            _binder.bind(*expect)
            mk.assert_called_once_with(*expect)

    def test_bind_fail_write_no_export(self):
        """ It should set no export context on failure write """
        expect = mock.MagicMock(), mock.MagicMock(spec=BaseModel)
        with mock.patch.object(binder.Binder, 'bind') as mk:
            _binder = self._new_binder()
            mk.side_effect = AssertionError
            _binder.bind(*expect)
            expect[1].with_context.assert_called_once_with(
                connector_no_export=True,
            )

    @mock.patch('%s.fields' % _file)
    def test_bind_handles_assertion_fail(self, fields):
        """ It should write fail time to bind record """
        expect = mock.MagicMock(), mock.MagicMock(spec=BaseModel)
        with mock.patch.object(binder.Binder, 'bind') as mk:
            _binder = self._new_binder()
            mk.side_effect = AssertionError
            _binder.bind(*expect)
            expect[1].with_context().write.assert_called_once_with({
                _binder._fail_date_field: fields.Datetime.now(),
            })

    def test_bind_fail_write_int(self):
        """ It should browse on model if not instance of BaseModel """
        expect = mock.MagicMock(), mock.MagicMock()
        with mock.patch.object(binder.Binder, 'bind') as mk:
            _binder = self._new_binder()
            mk.side_effect = AssertionError
            with mock.patch.object(_binder.connector_env, 'model') as model:
                _binder.bind(*expect)
                model.browse.assert_called_once_with(expect[1])

    def test_external_date_method(self):
        """ It should return input arg """
        expect = mock.MagicMock()
        res = self._new_binder()._external_date_method(expect)
        self.assertEqual(expect, res)
