from odoo import models, api, fields, _, Command

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    ticket_ids = fields.One2many(
        comodel_name='helpdesk.ticket',
        inverse_name='sale_order_id',
        string='Tickets')
    
    def create_ticket(self):
        self.ensure_one()
        tag_ids = self.order_line.product_id.helpdesk_tag_id.ids
        
        self.write({
            'ticket_ids': [Command.create({'name': self.name, 'tag_ids': [Command.set(tag_ids)]})]})
    
    def _action_cancel(self):
        res = super(SaleOrder, self)._action_cancel()
        self.ticket_ids.write({'state': 'cancelado'})