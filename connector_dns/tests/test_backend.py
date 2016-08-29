# -*- coding: utf-8 -*-
# Copyright 2015 Elico Corp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import openerp.tests.common as common
from openerp.addons.connector.backend import Backend
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector_dns.unit.binder import DNSModelBinder


class TestDNSBackend(common.TransactionCase):
    """
    Test DNS Backend
    """

    def setUp(self):
        super(TestDNSBackend, self).setUp()
        self.service = "dns"

    def test_new_backend(self):
        """ Create a backend"""
        backend = Backend(self.service)
        self.assertEqual(backend.service, self.service)

    def test_parent(self):
        """ Bind the backend to a parent backend"""
        backend = Backend(self.service)
        child_backend = Backend(parent=backend)
        self.assertEqual(child_backend.service, backend.service)

    def test_no_service(self):
        """ Should raise an error because no service or parent is defined"""
        with self.assertRaises(ValueError):
            Backend()


class test_backend_register(common.TransactionCase):
    """ Test registration of classes on the Backend"""

    def setUp(self):
        super(test_backend_register, self).setUp()
        self.service = 'dns'
        self.parent = Backend(self.service)
        self.backend = Backend(parent=self.parent)
        self.session = ConnectorSession(self.cr, self.uid)

    def test_register_class(self):
        class BenderBinder(DNSModelBinder):
            _model_name = 'res.users'

        self.backend.register_class(BenderBinder)
        ref = self.backend.get_class(DNSModelBinder,
                                     self.session,
                                     'res.users')
        self.assertEqual(ref, BenderBinder)

    def test_register_class_parent(self):
        """ It should get the parent's class when no class is defined"""

        @self.parent
        class FryBinder(DNSModelBinder):
            _model_name = 'res.users'

        ref = self.backend.get_class(DNSModelBinder,
                                     self.session,
                                     'res.users')
        self.assertEqual(ref, FryBinder)
