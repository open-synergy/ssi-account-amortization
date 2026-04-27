# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class Amortization(models.Model):
    _name = "account.amortization"
    _inherit = [
        "account.amortization",
        "mixin.single_operating_unit",
    ]
