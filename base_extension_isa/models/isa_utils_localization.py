from odoo import models, api


class IsaUtilsLocalization(models.TransientModel):
    _name = 'isa.utils.localization'
    _description = 'ISA Localization Utilities'

    @api.model
    # This method modify the paper format values related to the sale order report.
    def clean_isa_modules_metadata_translations(self):
        isa_modules_ids = self.env['ir.module.module'].search([('author', '=', 'ISA S.r.L.')]).ids
        short_desc_to_delete = self.env['ir.translation'].search([('name', '=', 'ir.module.module,shortdesc'),('res_id', 'in', isa_modules_ids)])
        summary_to_delete = self.env['ir.translation'].search([('name', '=', 'ir.module.module,summary'),('res_id', 'in', isa_modules_ids)])
        description_to_delete = self.env['ir.translation'].search([('name', '=', 'ir.module.module,description'),('res_id', 'in', isa_modules_ids)])
        short_desc_to_delete.unlink()
        summary_to_delete.unlink()
        description_to_delete.unlink()
