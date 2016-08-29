# -*- coding: utf-8 -*-

import mock
import openerp
from openerp.addons.connector.backend import Backend
from openerp.addons.connector_dns.unit.binder import DNSModelBinder
from openerp.addons.connector.connector import ConnectorEnvironment
from openerp.addons.connector.session import ConnectorSession
from openerp.tests.common import TransactionCase


@openerp.tests.common.at_install(False)
@openerp.tests.common.post_install(True)
class TestDNSModelBinder(TransactionCase):
    """ Test the DNS Model binder implementation"""
    def setUp(self):
        super(TestDNSModelBinder, self).setUp()

        class TestDNSBinder(DNSModelBinder):
            """
            we use already existing fields for the binding
            """
            _model_name = 'dns.binding'
            _external_field = 'ref'
            _sync_date_field = 'date'
            _backend_field = 'color'
            _openerp_field = 'id'

        self.session = ConnectorSession(self.cr, self.uid)
        self.backend = Backend('dummy', version='1.0')
        backend_record = mock.Mock()
        backend_record.id = 1
        backend_record.get_backend.return_value = self.backend
        self.connector_env = ConnectorEnvironment(
            backend_record, self.session, 'dns.binding')
        self.test_dns_binder = TestDNSBinder(self.connector_env)

    def test_binder(self):
        """ Small scenario with the default binder """
        dns_model = mock.Mock()
        dns_model.id = 0
        dns_model.dns_id = 0
        # bind the main partner to external id = 0
        self.test_dns_binder.bind(0, dns_model.id)
        # find the openerp partner bound to external partner 0
        self.test_dns_binder.to_openerp = mock.Mock()
        self.test_dns_binder.to_openerp.return_value.id = 0
        openerp_id = self.test_dns_binder.to_openerp(0)
        self.assertEqual(openerp_id.id, dns_model.id)
        openerp_id = self.test_dns_binder.to_openerp(0, unwrap=True)
        self.assertEqual(openerp_id.id, dns_model.id)
        self.test_dns_binder.to_backend = mock.Mock()
        self.test_dns_binder.to_backend.return_value = '0'
        external_id = self.test_dns_binder.to_backend(dns_model.id)
        self.assertEqual(external_id, '0')
        external_id = self.test_dns_binder.to_backend(dns_model.id, wrap=True)
        self.assertEqual(external_id, '0')
