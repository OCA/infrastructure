# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class BackendOpenshift(models.Model):
    _name = "backend.openshift"
    _description = "Openshift Backend"

    name = fields.Char("Name", required=True,)
    api_url = fields.Char("API URL", required=True,)
    token = fields.Char("Token", required=True,)
    apps_domain = fields.Char("Apps Domain", required=True,)
    create_project = fields.Text("Create Project")
    suspend_project = fields.Text("Suspend Project")
    resume_project = fields.Text("Resume Project")
    close_project = fields.Text("Close Project")
