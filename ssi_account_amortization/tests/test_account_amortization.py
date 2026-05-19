# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo import fields
from odoo.tests import Form, tagged


@tagged("post_install", "-at_install")
class TestAccountAmortization(YamlTransactionCase):
    def test_account_amortization(self):
        self.run_yaml_scenario("test_data_account_amortization.yaml")

    def _setup_amortization_data(self):
        """Create prerequisite accounting data for onchange tests."""
        user_type_assets = self.env.ref("account.data_account_type_current_assets")
        user_type_expenses = self.env.ref("account.data_account_type_expenses")
        journal = self.env["account.journal"].create(
            {
                "name": "Test Amortization Journal OC",
                "code": "TOCJ",
                "type": "general",
            }
        )
        debit_account = self.env["account.account"].create(
            {
                "name": "Test Prepaid Expense OC",
                "code": "XTOCAMR01",
                "user_type_id": user_type_assets.id,
                "reconcile": True,
            }
        )
        contra_account = self.env["account.account"].create(
            {
                "name": "Test Expense OC",
                "code": "XTOCAMR02",
                "user_type_id": user_type_expenses.id,
            }
        )
        amortization_type = self.env["account.amortization_type"].create(
            {
                "name": "Test Type For Onchange",
                "code": "TOCTYPE01",
                "direction": "dr",
                "journal_id": journal.id,
                "account_id": debit_account.id,
                "contra_account_id": contra_account.id,
            }
        )
        return journal, debit_account, contra_account, amortization_type

    def test_onchange_type_id_sets_account_fields(self):
        """When type_id is set, account_id, contra_account_id and journal_id
        are auto-populated from the amortization type."""
        (
            journal,
            debit_account,
            contra_account,
            amortization_type,
        ) = self._setup_amortization_data()
        form = Form(self.env["account.amortization"])
        form.source = "manual"
        form.date = fields.Date.today()
        form.date_start = fields.Date.today()
        form.period_number = 1
        form.amount = 1000.0
        form.type_id = amortization_type

        self.assertEqual(form.account_id._origin, debit_account)
        self.assertEqual(form.contra_account_id._origin, contra_account)
        self.assertEqual(form.journal_id._origin, journal)

    def test_onchange_type_id_clears_account_fields(self):
        """When type_id is cleared, account_id, contra_account_id and
        journal_id are also cleared."""
        __, __, __, amortization_type = self._setup_amortization_data()
        form = Form(self.env["account.amortization"])
        form.source = "manual"
        form.date = fields.Date.today()
        form.date_start = fields.Date.today()
        form.period_number = 1
        form.amount = 1000.0
        form.type_id = amortization_type
        # Clear the type
        form.type_id = self.env["account.amortization_type"]

        self.assertFalse(form.account_id._origin)
        self.assertFalse(form.contra_account_id._origin)
        self.assertFalse(form.journal_id._origin)

    def test_onchange_source_clears_move_line_id(self):
        """Changing source clears move_line_id."""
        __, __, __, amortization_type = self._setup_amortization_data()
        form = Form(self.env["account.amortization"])
        form.source = "manual"
        form.date = fields.Date.today()
        form.date_start = fields.Date.today()
        form.type_id = amortization_type
        form.period_number = 1
        form.amount = 1000.0
        # Change source — onchange_move_line_id should fire
        form.source = "move"
        form.source = "manual"

        self.assertFalse(form.move_line_id._origin)
