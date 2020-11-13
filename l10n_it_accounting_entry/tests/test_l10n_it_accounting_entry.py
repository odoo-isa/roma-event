# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo.addons.account.tests.account_test_savepoint import AccountTestInvoicingCommon
from odoo.tests import tagged
from odoo.exceptions import ValidationError


@tagged('post_install', '-at_install')
class TestL10nItAccountingEntry(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.env.user.company_id = cls.company_data['company']
        # Set account for managed with accounting entry
        cls.company_data['default_account_receivable'].managed_by_accounting_entry = True
        # Set bank account
        cls.company_data['default_account_liquidity'] = cls.env['account.account'].search([
            ('company_id', '=', cls.env.user.company_id.id),
            ('user_type_id', '=', cls.env.ref('account.data_account_type_liquidity').id)
        ], limit=1)
        # Mixed registration
        cls.account_move_mixed = cls.env['account.move'].create({
            'type': 'entry',
            'date': '2020-06-10',
            'line_ids': [
                # Partner A
                (0, 0, {
                    'name': 'line_mixed_debit',
                    'account_id': cls.company_data['default_account_receivable'].id,
                    'partner_id': cls.partner_a.id,
                    'debit': 200
                }),
                (0, 0, {
                    'name': 'line_mixed_credit',
                    'account_id': cls.company_data['default_account_revenue'].id,
                    'partner_id': cls.partner_a.id,
                    'credit': 200
                }),
                # Partner B
                (0, 0, {
                    'name': 'line_mixed_debit',
                    'account_id': cls.company_data['default_account_receivable'].id,
                    'partner_id': cls.partner_b.id,
                    'debit': 300
                }),
                (0, 0, {
                    'name': 'line_mixed_credit',
                    'account_id': cls.company_data['default_account_revenue'].id,
                    'partner_id': cls.partner_b.id,
                    'credit': 300
                })
            ]
        })
        # Move partner a registration
        cls.account_move_a = cls.env['account.move'].create({
            'type': 'entry',
            'date': '2020-06-10',
            'line_ids': [
                # Partner A
                (0, 0, {
                    'name': 'line_mixed_debit_a',
                    'account_id': cls.company_data['default_account_receivable'].id,
                    'partner_id': cls.partner_a.id,
                    'debit': 200
                }),
                (0, 0, {
                    'name': 'line_mixed_credit_a',
                    'account_id': cls.company_data['default_account_revenue'].id,
                    'partner_id': cls.partner_a.id,
                    'credit': 200
                })
            ]
        })
        # Move partner b registration
        cls.account_move_b = cls.env['account.move'].create({
            'type': 'entry',
            'date': '2020-06-10',
            'line_ids': [
                # Partner B
                (0, 0, {
                    'name': 'line_mixed_debit_b',
                    'account_id': cls.company_data['default_account_receivable'].id,
                    'partner_id': cls.partner_b.id,
                    'debit': 200
                }),
                (0, 0, {
                    'name': 'line_mixed_credit_b',
                    'account_id': cls.company_data['default_account_revenue'].id,
                    'partner_id': cls.partner_b.id,
                    'credit': 200
                })
            ]
        })

    def test_number_and_state_of_entries(self):
        #  posted the accounting entry
        self.account_move_mixed.action_post()
        # The accounting entry will be generated by key move, partner, account. In this case we have two partner and so
        # the generated accounting entry should be 2
        self.assertEqual(
            self.account_move_mixed.accounting_entry_count,
            2,
            "Expected two accounting entry because of key move_id, partner_id, account_id "
        )
        # The generated entry should be in open state because it's amount should be different from zero
        entry_a = self.account_move_mixed.accounting_entry_ids.filtered(lambda e: e.partner_id == self.partner_a)
        self.assertTrue(entry_a, "Must be exist an entry for partner_a")
        # The state must be 'open' and the amount must be equal to 200 and the line should be one
        entry_a = entry_a[0]
        self.assertEqual(
            entry_a.amount,
            200,
            "The amount of the entry_a statement should be equal 200"
        )
        self.assertEqual(
            entry_a.state,
            'open',
            "The state of the entry_a statement should be equal to open"
        )
        self.assertEqual(
            len(entry_a),
            1,
            "Should be present only one line for statement_a"
        )
        # Return to draft should remove accounting entries
        self.account_move_mixed.button_draft()
        self.assertFalse(self.account_move_mixed.accounting_entry_ids, "Move shouldn't have linked entries")
        # Generated entry single partner
        self.account_move_a.action_post()
        self.assertEqual(
            self.account_move_a.accounting_entry_count,
            1,
            "Expected only one account entry for this move"
        )

    def test_button_draft(self):
        # Confirm move a
        self.account_move_a.action_post()
        # Retrieve entry that should be exists and should be only one
        entry = self.account_move_a.accounting_entry_ids
        self.assertTrue(entry, "Must be exist an entry for this move")
        self.assertEqual(
            len(entry),
            1,
            "Expected only one account entry"
        )
        # Create a new move and set manually the accounting entry
        manual_move = self.env['account.move'].create({
            'type': 'entry',
            'date': '2020-06-11',
            'line_ids': [
                (0, 0, {
                    'name': 'line_manual_debit',
                    'account_id': self.company_data['default_account_receivable'].id,
                    'partner_id': self.partner_a.id,
                    'debit': 500,
                    'accounting_entry_id': entry.id
                }),
                (0, 0, {
                    'name': 'line_mixed_credit',
                    'account_id': self.company_data['default_account_revenue'].id,
                    'partner_id': self.partner_a.id,
                    'credit': 500
                })
            ]
        })
        manual_move.action_post()
        # The move should have same entry of the account_move_a
        self.assertEqual(
            entry,
            manual_move.accounting_entry_ids,
            "Manual move should have same entry of the account move a"
        )
        self.assertEqual(
            manual_move.accounting_entry_ids.amount,
            700,
            "Expected amount of 700 for this entry"
        )
        manual_move.button_draft()
        self.assertFalse(manual_move.accounting_entry_ids, "Manual move should not have entry")
        self.assertEqual(
            entry.amount,
            200,
            "Expected amount of 200 after draft move"
        )

    def test_check_of_entries(self):
        move_lines_a = self.account_move_a.line_ids.filtered(lambda l: l.name == 'line_mixed_debit_a')[0]
        move_lines_b = self.account_move_b.line_ids.filtered(lambda l: l.name == 'line_mixed_debit_b')[0]
        # Entry with multiple partner
        with self.assertRaises(ValidationError):
            entry = self.env['l10n_it.accounting.entry'].create({
                'name': 'test',
                'accounting_entry_lines': [
                    (6, 0, [move_lines_a.id, move_lines_b.id])
                ]
            })

    def test_join_split(self):
        #  Validate move for partner a
        self.account_move_a.action_post()
        entry_partner_a = self.account_move_a.accounting_entry_ids
        self.assertTrue(entry_partner_a)
        # Create payment for pay move a (exact amount)
        account_move_pay_a = self.env['account.move'].create({
            'type': 'entry',
            'date': '2020-06-20',
            'line_ids': [
                # Partner A
                (0, 0, {
                    'name': 'payment_a_debit',
                    'account_id': self.company_data['default_account_liquidity'].id,
                    'partner_id': self.partner_a.id,
                    'debit': 200
                }),
                (0, 0, {
                    'name': 'payment_a_credit',
                    'account_id': self.company_data['default_account_receivable'].id,
                    'partner_id': self.partner_a.id,
                    'credit': 200
                })
            ]
        })
        account_move_pay_a.action_post()
        # Should have accounting entry with unbalance value for -200
        entry_payment = account_move_pay_a.accounting_entry_ids
        self.assertTrue(entry_payment)
        self.assertEqual(
            account_move_pay_a.accounting_entry_count,
            1,
            "Expected accounting entry for this payment move"
        )
        self.assertEqual(
            entry_payment.amount,
            -200,
            "Expected amount for -200"
        )
        # Try to reconcile move
        move_lines_partner_a = self.account_move_a.line_ids.filtered(
            lambda l: l.account_id == self.company_data['default_account_receivable']
        )
        move_lines_payment_a = account_move_pay_a.line_ids.filtered(
            lambda l: l.account_id == self.company_data['default_account_receivable']
        )
        (move_lines_partner_a + move_lines_payment_a).reconcile()
        # After the reconciliation, entry for move_partner_a should be closed and have to be included move related to
        # the payment. The accounting entry for the move a should not be exist anymore.
        entry_partner_a = self.account_move_a.accounting_entry_ids
        self.assertEqual(
            entry_partner_a.amount,
            0,
            "The amount of this entry should be zero"
        )
        self.assertEqual(
            entry_partner_a.state,
            'close',
            "The state of this accounting entry should be close"
        )
        self.assertEqual(
            len(entry_partner_a.accounting_entry_lines),
            2,
            "Must be present two move lines linked to this accounting entry"
        )
        self.assertFalse(
            entry_payment.exists(),
            "The entry payment should not exist cause after reconciliation it shouldn't have linked move lines."
        )
        # Testing the split function. restore to default (unreconcile perform also split)
        entry_partner_a.accounting_entry_lines.remove_move_reconcile()
        # After unreconcile each move (partner and payment) should has it's accounting entry
        self.assertEqual(
            entry_partner_a.amount,
            200,
            "After unreconcile move for partner should have it's accounting entry"
        )
        self.assertEqual(
            len(entry_partner_a.accounting_entry_lines),
            1,
            "After unreconcile move line for accounting entry of the partner should be only one"
        )
        self.assertEqual(
            entry_partner_a.state,
            "open",
            "After unreconcile accounting entry of the partner should be in state open"
        )
        # Payment move should now newly have the accounting entry
        entry_payment = account_move_pay_a.accounting_entry_ids
        self.assertTrue(entry_payment, "After unreconcile payment move should have newly the accounting entry")
        self.assertEqual(
            entry_payment.amount,
            -200,
            "The amount of the payment's accounting entry should be -200 after the unreconcile"
        )
        self.assertTrue(
            entry_payment.accounting_entry_lines,
            "After unreconcile payment's accounting entry should has one move line."
        )
        self.assertEqual(
            len(entry_payment.accounting_entry_lines),
            1,
            "After unreconcile payment's accounting entry should has one move line."
        )

    def test_split_wizard(self):
        # We have two move for same partner
        move_a_1 = self.account_move_a
        move_a_2 = self.account_move_a.copy()
        move_a_1.action_post()
        move_a_2.action_post()
        # We have two accounting entries
        entry_a_1 = move_a_1.accounting_entry_ids
        self.assertEqual(
            len(entry_a_1),
            1,
            "Expected only one accounting entry for move_a_1"
        )
        entry_a_2 = move_a_1.accounting_entry_ids
        self.assertEqual(
            len(entry_a_1),
            1,
            "Expected only one accounting entry for move_a_2"
        )
        account_move_pay_a_1 = self.env['account.move'].create({
            'type': 'entry',
            'date': '2020-06-20',
            'line_ids': [
                # Partner A
                (0, 0, {
                    'name': 'payment_a1_debit',
                    'account_id': self.company_data['default_account_liquidity'].id,
                    'partner_id': self.partner_a.id,
                    'debit': 200
                }),
                (0, 0, {
                    'name': 'payment_a1_credit',
                    'account_id': self.company_data['default_account_receivable'].id,
                    'partner_id': self.partner_a.id,
                    'credit': 200
                })
            ]
        })
        account_move_pay_a_1.action_post()
        # Reconcile payment with move
        move_lines_partner_a = move_a_1.line_ids.filtered(
            lambda l: l.account_id == self.company_data['default_account_receivable']
        )
        move_lines_payment_a = account_move_pay_a_1.line_ids.filtered(
            lambda l: l.account_id == self.company_data['default_account_receivable']
        )
        (move_lines_partner_a + move_lines_payment_a).reconcile()
        # join also the move_a_2
        contextual_value = {
            'active_model': 'l10n_it.accounting.entry',
            'active_ids': [move_a_1.accounting_entry_ids.id, move_a_2.accounting_entry_ids.id],
            'action': 'merge'
        }
        merge_wizard = self.env['l10n_it.accounting.entry.merge.split'].with_context(contextual_value).create({
            'main_accounting_entry': move_a_1.accounting_entry_ids.id
        })
        merge_wizard.with_context(contextual_value).process_entries()
        # After merge each moves should be have the same value for the accounting entries
        entry_a_1 = move_a_1.accounting_entry_ids
        entry_a_2 = move_a_2.accounting_entry_ids
        entry_payment = account_move_pay_a_1.accounting_entry_ids
        self.assertTrue(
            entry_a_1 == entry_a_2 == entry_payment,
            "The entry of each moves should be the same"
        )
        # Try to split only move 2
        contextual_value = {
            'active_model': 'account.move',
            'active_ids': [move_a_2.id],
            'action': 'split'
        }
        split_wizard = self.env['l10n_it.accounting.entry.merge.split'].with_context(contextual_value).create({
            'accounting_entry_to_split': [(6, 0, move_a_2.accounting_entry_ids.ids)]
        })
        split_wizard.with_context(contextual_value).process_entries()
        # At this point entry_a_1 and entry_payment should be the same but entry_a_2 should be different
        self.assertEqual(
            move_a_1.accounting_entry_ids,
            account_move_pay_a_1.accounting_entry_ids,
            "The entry of the account payment of the move_a_1 and it's payment should be the same"
        )
        self.assertTrue(
            move_a_1.accounting_entry_ids != move_a_2.accounting_entry_ids,
            "The entry of the account move 1 should be different from the move of the account move 2."
        )
        # Merge from account move
        contextual_value = {
            'active_model': 'account.move',
            'active_ids': [move_a_1.id, move_a_2.id],
            'action': 'merge'
        }
        merge_wizard = self.env['l10n_it.accounting.entry.merge.split'].with_context(contextual_value).create({
            'main_accounting_entry': move_a_1.accounting_entry_ids.id
        })
        merge_wizard.with_context(contextual_value).process_entries()
        # At this point the entries should be newly the same for each move
        entry_a_1 = move_a_1.accounting_entry_ids
        entry_a_2 = move_a_2.accounting_entry_ids
        entry_payment = account_move_pay_a_1.accounting_entry_ids
        self.assertTrue(
            entry_a_1 == entry_a_2 == entry_payment,
            "The entry of each moves should be the same"
        )
        # Split the entry
        contextual_value = {
            'active_model': 'l10n_it.accounting.entry',
            'active_ids': [entry_a_1.id],
            'action': 'split'
        }
        split_wizard = self.env['l10n_it.accounting.entry.merge.split'].with_context(contextual_value).create({
            'accounting_entry_to_split': [(6, 0, entry_a_1.ids)]
        })
        split_wizard.with_context(contextual_value).process_entries()
        # Now all entry should be different
        entry_a_1 = move_a_1.accounting_entry_ids
        entry_a_2 = move_a_2.accounting_entry_ids
        entry_payment = account_move_pay_a_1.accounting_entry_ids
        self.assertTrue(
            entry_a_1 != entry_a_2 != entry_payment,
            "The accounting entry should be all different"
        )
        # Try to merge entry from account move line
        contextual_value = {
            'active_model': 'account.move.line',
            'active_ids': [
                move_a_1.line_ids.filtered(lambda m: m.accounting_entry_id).id,
                account_move_pay_a_1.line_ids.filtered(lambda m: m.accounting_entry_id).id
            ],
            'action': 'merge'
        }
        merge_wizard = self.env['l10n_it.accounting.entry.merge.split'].with_context(contextual_value).create({
            'main_accounting_entry': move_a_1.accounting_entry_ids.id
        })
        merge_wizard.with_context(contextual_value).process_entries()
        # The entries of the account move a1 and payment should be the same and should be different respect to the
        # the move a2 entry
        entry_a_1 = move_a_1.accounting_entry_ids
        entry_a_2 = move_a_2.accounting_entry_ids
        entry_payment = account_move_pay_a_1.accounting_entry_ids
        self.assertEqual(
            entry_a_1,
            entry_payment,
            "The entries of the move a1 and the payment should be the same"
        )
        self.assertTrue(
            entry_a_1 != entry_a_2,
            "Move a1 and move a2 should be have different entries"
        )