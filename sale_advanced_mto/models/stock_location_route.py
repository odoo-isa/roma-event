# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
from logging import getLogger

_logger = getLogger(__name__)


class StockLocationRoute(models.Model):
    _inherit = ["stock.location.route"]

    is_default_route = fields.Boolean(
        string='Default route',
        help='''this option is available only if the route is generating from happy path configuration. If the route is
        checked as default it will be automatically set in the replenish widget when quantity is specified.''',
        copy=False,
        default=False
    )

    is_sale_mto_routing = fields.Boolean(
        string='MTO Routing',
        help='''System field that indicate if the routing it was generated from an happy path configuration.''',
        compute="_compute_is_sale_mto_routing"
    )

    def _compute_is_sale_mto_routing(self):
        """
        This function compute if the route it was made by this module
        :return:
        """
        for record in self:
            record.is_sale_mto_routing = False
            external_id = record.get_external_id()
            external_id = external_id.get(record.id, None)
            if not external_id:
                continue
            external_id = external_id.split('.')
            if external_id[0] != 'sale_advanced_mto':
                continue
            record.is_sale_mto_routing = True

    @api.constrains('is_default_route')
    def _check_unique_default(self):
        """
        Constraint to check the unique of default route by type (pull or buy)/started location/ending location
        :return: void
        Raises:
        ValidationError: The default route is not unique.
        """
        for record in self.filtered(lambda s: s.is_sale_mto_routing and s.is_default_route):
            '''
            The considering route are only that are referred to sale_advanced_mto module.
            Get the type of the route (buy or pull). To do this we assume that:
             - In the first rule of the route there are the starting warehouse and the type of operation (buy or pull)
             - In the last rule of the route there are the final warehouse.
            '''
            # Retrieve the ordered routing's rules
            rules = record.rule_ids.sorted(key=lambda r: r.sequence)
            if not rules:
                continue
            first_rule = rules[0]
            last_rule = rules[-1]
            # From the first rule retrieve the type of the rule
            # if the rule is buy, the started location is the location_id and not the location_src_id.
            started_location = first_rule.location_src_id
            rule_type = first_rule.action
            if rule_type == 'pull_push':
                rule_type = 'pull'
            if rule_type == 'buy':
                started_location = first_rule.location_id
            # From the last rule retrieve the destination location. If it isn't a internal location take the source
            # location instead
            ending_location = last_rule.location_id
            if ending_location.usage not in ('internal', 'transit'):
                ending_location = last_rule.location_src_id
            # Search for duplicating routing
            duplicated_route = record._search_duplicated_sale_mto_rules(rule_type, started_location, ending_location)
            if duplicated_route:
                raise ValidationError(_(
                    "Another route from %s to %s is already settings as default: %s" % (
                        started_location.display_name,
                        ending_location.display_name,
                        duplicated_route[0].display_name
                    )
                ))

    def _search_duplicated_sale_mto_rules(self, rule_type, started_location, ending_location):
        """
        Search for a duplicated route (that is not self) by rule_type/started location, ending location
        :param rule_type: buy|pull
        :param started_location: the started location of the route
        :param ending_location: the ending location of the route
        :return: Recordset of stock.location.route
        """
        query = '''
            with 
            first_rules as(
                select distinct on (sr.route_id)
                   sr.route_id, slr."name", sr."action",  
                   sr.location_src_id, sr.location_id, slr.is_default_route, sl."usage"
                from stock_rule sr
                join stock_location_route slr on sr.route_id = slr.id
                join stock_location sl on sr.location_id = sl.id
                order by sr.route_id, sr."sequence" , sr.id asc
            ),
            last_rules as(
                select distinct on (sr.route_id)
                       sr.route_id, slr."name", sr."action", sr.location_src_id, sr.location_id, slr.is_default_route, sl."usage" 
                from stock_rule sr
                join stock_location_route slr on sr.route_id = slr.id
                join stock_location sl on sr.location_id = sl.id
                order by sr.route_id, sr."sequence" , sr.id desc
            ),
            route_rule_from_to as(
                select 
                    fr.route_id, 
                    fr."name", 
                    fr."action", 
                    case when fr.action='buy' then fr.location_id 
                    else fr.location_src_id 
                    end as started_location,
                    case when lr.usage in ('internal', 'transit') then lr.location_id 
                    else lr.location_src_id 
                    end as ended_location, 
                    fr.is_default_route
                from first_rules fr
                join last_rules lr on fr.route_id = lr.route_id
            )
            select * 
            from route_rule_from_to
            where 1=1
                  and action in %(actions)s
                  and started_location = %(started_location)s
                  and ended_location = %(ended_location)s
                  and route_id != %(route_id)s 
                  and is_default_route = true
        '''
        if rule_type == 'pull':
            available_action = ('pull', 'pull_push')
        else:
            available_action = (rule_type,)
        self.env.cr.execute(query, {
            'actions': available_action,
            'started_location': started_location.id,
            'ended_location': ending_location.id,
            'route_id': self.id
        })
        rows = self.env.cr.fetchall()
        route = self.env['stock.location.route'].browse([t[0] for t in rows])
        return route
