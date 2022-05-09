from odoo import models, api, fields, _

class PoductTemplate(models.Model):
    _inherit = 'product.template'
    
    helpdesk_tag_id = fields.Many2one(
        comodel_name='helpdesk.ticket.tag',
        string='Helpdesk Tag')
    

    