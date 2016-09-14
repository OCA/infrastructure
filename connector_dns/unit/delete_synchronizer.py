# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


# from openerp.addons.connector.queue.job import job
from openerp.addons.connector.unit.synchronizer import Deleter
# from ..connector import get_environment


class DNSDeleter(Deleter):
    """ Base deleter for DNS """

    def run(self, dns_id):
        """
        Run the synchronization, delete the record on DNS
        :param dns_id: identifier of the record to delete
        """
        raise NotImplementedError('Cannot delete records from DNS.')


# @job(default_channel='root.dns')
# def export_delete_record(session, model_name, backend_id, dns_id):
#     """ Delete a record on DNS """
#     env = get_environment(session, model_name, backend_id)
#     deleter = env.get_connector_unit(DNSDeleter)
#     return deleter.run(dns_id)
