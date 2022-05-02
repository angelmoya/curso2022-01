from odoo import fields, models, api, _, Command
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from datetime import datetime
class HelpdeskTicket(models.Model):
    _name = "helpdesk.ticket"
    _description = "Helpdesk Ticket"
    _order = "sequence"

    @api.model
    def _get_default_user(self):
        return self.env.user
    
    name = fields.Char(required=True, copy=False)
    description = fields.Text(translate=True)
    date = fields.Date(help="Date when the ticket was created")
    date_start = fields.Datetime()
    time = fields.Float(
        string='Time')
    limit_date = fields.Datetime(help="Date and time when the ticket will be closed")
    assigned= fields.Boolean(
        help="Ticket assigned to someone",
        compute='_compute_assigned',
        search='_search_assigned',
        inverse='_set_assigned')
    actions_todo = fields.Html()
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Assigned to',
        # default=lambda self: self.env.user,
        default=_get_default_user,
        )
    user_email = fields.Char(
        string='User Email',
        related='user_id.partner_id.email')
    ticket_company = fields.Boolean(
        string='Ticket Company')
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner')
    partner_email = fields.Char(
        string='Partner Email',
        related='partner_id.email')
    sequence = fields.Integer()
    action_ids = fields.One2many(
        comodel_name='helpdesk.ticket.action',
        inverse_name='ticket_id',
        string='Actions Done')
    tag_name = fields.Char(
        string='Tag Name')
    tag_ids = fields.Many2many(
        comodel_name='helpdesk.ticket.tag',
        relation='helpdesk_ticket_tag_rel',
        column1='ticket_id',
        column2='tag_id',
        string='Tags')
    color = fields.Integer('Color Index', default=0)
    state = fields.Selection(
        [('nuevo', 'Nuevo'),
         ('asignado', 'Asignado'),
         ('en_proceso', 'En proceso'),
         ('pendiente', 'Pendiente'),
         ('resuelto', 'Resuelto'),
         ('cancelado', 'Cancelado')],
        string='State',
        default='nuevo')

    def to_asignado(self):
        self.ensure_one()
        self.state = 'asignado'
    
    def to_en_proceso(self):
        self.write({'state': 'en_proceso'})
    
    def to_pendiente(self):
        for record in self:
            record.state = 'pendiente'
    
    def review_actions(self):
        self.ensure_one()
        self.action_ids.review()

        # actions = self.env['helpdesk.ticket.action'].search([('ticket_id', '=', self.id)])
        # actions.review()
    
    @api.model
    def get_amount_tickets(self):
        # Give amount of ticket for active user
        return self.search_count([('user_id', '=', self.env.user.id)])
    
    @api.depends('user_id')
    def _compute_assigned(self):
        for record in self:
            record.assigned = record.user_id
    
    def _search_assigned(self, operator, value):
        if operator not in ['=', '!='] or not isinstance(value, bool):
            raise UserError(_('Operation not supported'))

        if (operator == '=' and value) or (operator == '!=' and not value):
            new_operator = '!='
        else:
            new_operator = '='

        return [('user_id', new_operator, False)]
    
    def _set_assigned(self):
        for record in self:
            if not record.assigned:
                record.user_id = False
            elif not record.user_id:
                record.user_id = self.env.user

    def create_and_link_tag(self):
        self.ensure_one()
        # creo el ticket y lo asigno
        # tag = self.env['helpdesk.ticket.tag'].create({'name': self.tag_name})
        # self.write({'tag_ids': [(4, tag.id, 0)]})
        # self.write({'tag_ids': [Command.link(tag.id)]})

        # creo el ticket desde la escritura del tag_ids
        # self.write({
        #     'tag_ids': [(0, 0, {'name': self.tag_name})],
        #     'tag_name': False})
        self.write({
            'tag_ids': [Command.create({'name': self.tag_name})],
            'tag_name': False})

        # # crear el tag asociado al ticket
        # self.env['helpdesk.ticket.tag'].create({
        #     'name': self.tag_name,
        #     'ticket_ids': [(6,0,self.ids)]})
        
        # self.env['helpdesk.ticket.tag'].create({
        #     'name': self.tag_name,
        #     'ticket_ids': [Command.set(self.ids)]})
        # self.write({
        #     'tag_name': False})
        
    @api.constrains('time')
    def _check_time(self):
        # for ticket in self:
        #     if ticket.time < 0:
        if self.filtered(lambda t: t.time < 0):
            raise ValidationError(_("The time must be a greather than 0."))
        
    @api.onchange('date_start')
    def _onchange_date_start(self):
        if self.date_start:
            self.limit_date = self.date_start + datetime.timedelta(days=1)
        else:
            self.limit_date = False