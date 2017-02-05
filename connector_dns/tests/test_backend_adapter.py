# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import mock
import inspect

from openerp.addons.connector_dns.unit import backend_adapter

from .common import SetUpDNSBase


_file = 'openerp.addons.connector_dns.unit.backend_adapter'


class TestBackendAdapter(SetUpDNSBase):

    CRUD_METHODS = [
        'search',
        'read',
        'search_read',
        'create',
        'write',
        'delete',
        '_call',
    ]

    def setUp(self):
        super(TestBackendAdapter, self).setUp()
        backend_adapter.dnss = {}
        self.model = self.env['dns.zone.bind']
        self.Unit = backend_adapter.DNSAdapter

    def _new_unit(self):
        return self.Unit(
            self.get_dns_helper(self.model._name),
        )

    @mock.patch('%s.DNSLocation' % _file)
    def test_init_creates_location(self, location):
        """ It should creaete new ``DNSLocation`` on init """
        unit = self._new_unit()
        location.assert_called_once_with(
            unit.backend_record.uri,
            unit.backend_record.login,
            unit.backend_record.password,
        )

    def test_init_sets_location(self):
        """ It should set unit.DNS to the new DNSLocation """
        unit = self._new_unit()
        self.assertIsInstance(
            unit.DNS,
            backend_adapter.DNSLocation,
        )

    def test_not_implemented(self):
        """ It should define CRUD methods and raise NotImplemented """
        unit = self._new_unit()
        for method in self.CRUD_METHODS:
            method = getattr(unit, method)
            arg_spec = inspect.getargspec(method)
            args = arg_spec.args[1:]
            with self.assertRaises(NotImplementedError):
                method(*args)
