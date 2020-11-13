# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################
from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model
    def _query_get(self, domain=None):
        """
        Modifica della query che genera la Registrazione Contabile a partire dal Resoconto Fiscale:
        vengono filtrati i movimenti contabili relativi a conto d'imposta
        """
        tables, where_clause, where_clause_params = super(AccountMoveLine, self)._query_get(domain=domain)
        tables += ''',account_tax_repartition_line, account_account'''
        where_clause += ''' 
        AND "account_tax_repartition_line".id = tax_repartition_line_id 
        AND "account_tax_repartition_line".account_id = account_account.id 
        AND "account_tax_repartition_line".account_id IS NOT NULL
        AND "account_account".l10n_it_account_usage = 'tax_account'
        '''
        return tables, where_clause, where_clause_params
