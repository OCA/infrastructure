# -*- coding: utf-8 -*-
# Copyright 2015 Camptocamp SA
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

"""
Helpers usable in the tests
"""

import importlib
import mock

from contextlib import contextmanager

import openerp.tests.common as common

import openerp.addons.connector.backend as backend
from openerp.addons.connector.session import ConnectorSession

from ..backend import dns
from ..unit.binder import DNSModelBinder

backend_adapter = 'openerp.addons.connector_dns.unit.backend_adapter'


class EndTestException(Exception):
    """ It is used to break code execution for logic isolation """


class DNSHelper(object):
    """ Emulate a ConnectorEnvironment """

    def __init__(self, env, model_name, backend):
        self.cr = env.cr
        self.model = env[model_name]
        self.backend = backend.get_backend()
        self.backend_record = backend
        self.session = ConnectorSession(
            env.cr,
            env.uid,
            env.context,
        )
        self.connector_unit = {}

    def get_connector_unit(self, unit_class):
        try:
            return self.connector_unit[unit_class]
        except KeyError:
            self.connector_unit[unit_class] = mock.MagicMock()
            return self.connector_unit[unit_class]


class SetUpDNSBase(common.TransactionCase):
    """ Base class - Test the imports from a DNS Mock. """

    def setUp(self):
        super(SetUpDNSBase, self).setUp()
        self.backend_model = self.env['dns.backend']
        self.dns_id = 123456789
        self.session = ConnectorSession(
            self.env.cr, self.env.uid, context=self.env.context,
        )
        self.test_backend = backend.Backend(
            parent=dns,
            version='none',
        )
        self.EndTestException = EndTestException
        self.backend = self.backend_model.create({
            'name': 'Test DNS',
            'version': 'none',
            'uri': 'URI',
            'login': 'username',
            'password': 'passwd',
            'is_default': True,
        })

    def get_dns_helper(self, model_name):
        """ It returns a simulated ConnectorEnvironment for model_name

        Args:
            model_name (str): Name of model to simulate environment for

        Returns:
            Simulated ``ConnectorEnvironment`` for testing
        """
        return DNSHelper(
            self.env, model_name, self.backend
        )

    def get_mock_binder(self):
        """ It returns a mock specced as a DNSModelBinder """
        binder = mock.MagicMock(spec=DNSModelBinder)
        binder._external_field = DNSModelBinder._external_field
        binder._backend_field = DNSModelBinder._backend_field
        binder._openerp_field = DNSModelBinder._openerp_field
        binder._sync_date_field = DNSModelBinder._sync_date_field
        binder._fail_date_field = DNSModelBinder._fail_date_field
        binder._external_date_field = DNSModelBinder._external_date_field
        return binder

    @contextmanager
    def mock_adapter(self, unit, binder_for=False):
        """ It returns a mocked backend_adapter on unit for testing

        Args:
            unit (connector.ConnectorUnit): to mock adapter on
            binder_for (bool): Also mock ``binder_for`` method on unit

        Yields:
            mock.Mock()
        """
        with mock.patch.object(unit, '_backend_adapter') as API:
            if binder_for:
                with mock.patch.object(unit, 'binder_for') as bind:
                    bind.return_value = self.get_mock_binder()
                    yield API
            else:
                yield API

    @contextmanager
    def mock_job_delay_to_direct(self, job_path):
        """ Replace the ``.delay()`` of a job with a direct call

        Args:
            job_path (str): The python path of the job, such as
                ``openerp.addons.dns.models.dns_record.export_record``

        Yields:
            Patched job
        """
        job_module, job_name = job_path.rsplit('.', 1)
        module = importlib.import_module(job_module)
        job_func = getattr(module, job_name, None)
        assert job_func, "The function %s must exist in %s" % (job_name,
                                                               job_module)

        def clean_args_for_func(*args, **kwargs):
            # remove the special args reserved to .delay()
            kwargs.pop('priority', None)
            kwargs.pop('eta', None)
            kwargs.pop('model_name', None)
            kwargs.pop('max_retries', None)
            kwargs.pop('description', None)
            job_func(*args, **kwargs)

        with mock.patch(job_path) as patched_job:
            # call the direct export instead of 'delay()'
            patched_job.delay.side_effect = clean_args_for_func
            yield patched_job
