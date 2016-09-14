# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import mock

from openerp.addons.connector_dns import connector

from .common import SetUpDNSBase


mk_file = 'openerp.addons.connector_dns.connector'


class EndTestException(Exception):
    pass


class TestConnector(SetUpDNSBase):

    def setUp(self):
        super(TestConnector, self).setUp()
        self.model = 'dns.zone.bind'
        self.binding_id = self._new_record()
        self.session = mock.MagicMock()

    def _new_record(self):
        return self.env[self.model].create({
            'name': 'Test DNS',
            'dns_id_external': self.dns_id,
        })

    def test_default_dns_backend_id(self):
        self.assertEqual(self.backend, self.binding_id.dns_backend_id)

    def test_get_environment_gets_backend_record(self):
        """ It should browse for backend_record for id """
        mk = self.session.env['dns.backend'].browse
        mk.side_effect = EndTestException
        with self.assertRaises(EndTestException):
            connector.get_environment(
                self.session, self.model, self.binding_id.dns_backend_id.id,
            )
        mk.assert_called_once_with(self.binding_id.dns_backend_id.id)

    def test_get_environment_creates_environment(self):
        """ It should create environment for binding """
        with mock.patch('%s.Environment' % mk_file) as env:
            env.side_effect = EndTestException
            with self.assertRaises(EndTestException):
                connector.get_environment(
                    self.session,
                    self.model,
                    self.binding_id.dns_backend_id.id,
                )
            env.assert_called_once_with(
                self.session.env['dns.backend'].browse(),
                self.session,
                self.model,
            )

    def test_get_environment_return(self):
        """ It should return new environment """
        with mock.patch('%s.Environment' % mk_file) as env:
            res = connector.get_environment(
                self.session, self.model, self.binding_id.dns_backend_id.id,
            )
            self.assertEqual(env(), res)

    def test_add_checkpoint_call(self):
        """ It should call add_checkpoint w/ proper args """
        with mock.patch('%s.checkpoint' % mk_file) as mk:
            mk.add_checkpoint.side_effect = EndTestException
            with self.assertRaises(EndTestException):
                connector.add_checkpoint(
                    self.session,
                    self.model,
                    self.binding_id.id,
                    self.binding_id.dns_backend_id.id,
                )
            mk.add_checkpoint.assert_called_once_with(
                self.session,
                self.model,
                self.binding_id.id,
                'dns.backend',
                self.binding_id.dns_backend_id.id,
            )

    def test_add_checkpoint_return(self):
        """ It should return new checkpoint """
        with mock.patch('%s.checkpoint' % mk_file) as mk:
            res = connector.add_checkpoint(
                self.session,
                self.model,
                self.binding_id.id,
                self.binding_id.dns_backend_id.id,
            )
            self.assertEqual(mk.add_checkpoint(), res)
