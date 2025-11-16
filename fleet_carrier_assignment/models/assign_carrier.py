# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AssignCarrier(models.Model):
    _name = 'assign.carrier'
    _description = 'Vehicle Assignment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'assignment_date desc'
    _rec_name = 'name'

    name = fields.Char(
        string='Assignment Reference',
        required=True,
        copy=False,
        readonly=True,
        default='New',
        tracking=True
    )
    vehicle_id = fields.Many2one(
        'fleet.vehicle',
        string='Vehicle',
        required=True,
        ondelete='restrict',
        help='Assigned vehicle',
        tracking=True
    )
    license_plate = fields.Char(
        related='vehicle_id.license_plate',
        string='License Plate',
        store=True,
        help='Vehicle license plate'
    )
    assignment_date = fields.Datetime(
        string='Assignment Date',
        default=fields.Datetime.now,
        required=True,
        help='Date and time when the vehicle was assigned',
        tracking=True
    )
    
    # Delivery Orders (One2many relationship)
    picking_ids = fields.One2many(
        'assign.carrier.picking',
        'assignment_id',
        string='Delivery Orders',
        help='All delivery orders assigned to this vehicle'
    )
    
    delivery_count = fields.Integer(
        string='Number of Deliveries',
        compute='_compute_delivery_count',
        store=True
    )
    
    # Product Lines (One2many relationship)
    product_line_ids = fields.One2many(
        'assign.carrier.product',
        'assignment_id',
        string='Products',
        help='All products from all delivery orders'
    )
    
    # Vehicle capacity info
    vehicle_weight_capacity = fields.Float(
        string='Vehicle Capacity (kg)',
        compute='_compute_vehicle_capacity',
        store=True,
        help='Weight capacity of the assigned vehicle'
    )
    vehicle_volume_capacity = fields.Float(
        string='Vehicle Capacity (m³)',
        compute='_compute_vehicle_capacity',
        store=True,
        help='Volume capacity of the assigned vehicle'
    )
    
    # Combined totals
    total_weight = fields.Float(
        string='Total Weight (kg)',
        compute='_compute_totals',
        store=True,
        help='Combined weight of all deliveries'
    )
    total_volume = fields.Float(
        string='Total Volume (m³)',
        compute='_compute_totals',
        store=True,
        help='Combined volume of all deliveries'
    )
    
    # Utilization
    weight_utilization = fields.Float(
        string='Weight Utilization (%)',
        compute='_compute_utilization',
        store=True,
        help='Percentage of vehicle weight capacity used'
    )
    volume_utilization = fields.Float(
        string='Volume Utilization (%)',
        compute='_compute_utilization',
        store=True,
        help='Percentage of vehicle volume capacity used'
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('assigned', 'Assigned'),
        ('in_transit', 'In Transit'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft', required=True, tracking=True)
    
    notes = fields.Text(string='Notes')

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to generate sequence number"""
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('assign.carrier') or 'New'
        return super(AssignCarrier, self).create(vals_list)

    @api.depends('picking_ids')
    def _compute_delivery_count(self):
        for record in self:
            record.delivery_count = len(record.picking_ids)

    @api.depends('vehicle_id', 'vehicle_id.model_id.category_id.weight_capacity',
                 'vehicle_id.model_id.category_id.volume_capacity')
    def _compute_vehicle_capacity(self):
        for record in self:
            category = record.vehicle_id.model_id.category_id
            if category:
                record.vehicle_weight_capacity = category.weight_capacity or 0.0
                record.vehicle_volume_capacity = category.volume_capacity or 0.0
            else:
                record.vehicle_weight_capacity = 0.0
                record.vehicle_volume_capacity = 0.0

    @api.depends('picking_ids', 'picking_ids.total_weight', 'picking_ids.total_volume')
    def _compute_totals(self):
        for record in self:
            record.total_weight = sum(record.picking_ids.mapped('total_weight'))
            record.total_volume = sum(record.picking_ids.mapped('total_volume'))

    @api.depends('total_weight', 'total_volume', 'vehicle_weight_capacity', 'vehicle_volume_capacity')
    def _compute_utilization(self):
        for record in self:
            if record.vehicle_weight_capacity > 0:
                record.weight_utilization = (record.total_weight / record.vehicle_weight_capacity) * 100
            else:
                record.weight_utilization = 0.0

            if record.vehicle_volume_capacity > 0:
                record.volume_utilization = (record.total_volume / record.vehicle_volume_capacity) * 100
            else:
                record.volume_utilization = 0.0


class AssignCarrierPicking(models.Model):
    _name = 'assign.carrier.picking'
    _description = 'Assignment Delivery Order Line'
    _order = 'id'

    assignment_id = fields.Many2one(
        'assign.carrier',
        string='Assignment',
        required=True,
        ondelete='cascade'
    )
    picking_id = fields.Many2one(
        'stock.picking',
        string='Delivery Order',
        required=True,
        ondelete='restrict'
    )
    partner_id = fields.Many2one(
        'res.partner',
        related='picking_id.partner_id',
        string='Customer',
        store=True
    )
    origin = fields.Char(
        related='picking_id.origin',
        string='Source Document',
        store=True
    )
    scheduled_date = fields.Datetime(
        related='picking_id.scheduled_date',
        string='Scheduled Date',
        store=True
    )
    state = fields.Selection(
        related='picking_id.state',
        string='Status',
        store=True
    )
    total_weight = fields.Float(
        related='picking_id.total_weight',
        string='Weight (kg)',
        store=True
    )
    total_volume = fields.Float(
        related='picking_id.total_volume',
        string='Volume (m³)',
        store=True
    )


class AssignCarrierProduct(models.Model):
    _name = 'assign.carrier.product'
    _description = 'Assignment Product Line'
    _order = 'picking_name, id'

    assignment_id = fields.Many2one(
        'assign.carrier',
        string='Assignment',
        required=True,
        ondelete='cascade'
    )
    picking_id = fields.Many2one(
        'stock.picking',
        string='Delivery Order',
        required=True
    )
    picking_name = fields.Char(
        related='picking_id.name',
        string='DO Reference',
        store=True
    )
    move_id = fields.Many2one(
        'stock.move',
        string='Stock Move',
        required=True
    )
    product_id = fields.Many2one(
        'product.product',
        related='move_id.product_id',
        string='Product',
        store=True
    )
    product_uom_qty = fields.Float(
        related='move_id.product_uom_qty',
        string='Quantity',
        store=True
    )
    product_uom = fields.Many2one(
        'uom.uom',
        related='move_id.product_uom',
        string='Unit',
        store=True
    )
    weight = fields.Float(
        string='Unit Weight (kg)',
        related='product_id.weight',
        store=True
    )
    volume = fields.Float(
        string='Unit Volume (m³)',
        related='product_id.volume',
        store=True
    )
    total_weight = fields.Float(
        string='Total Weight (kg)',
        compute='_compute_totals',
        store=True
    )
    total_volume = fields.Float(
        string='Total Volume (m³)',
        compute='_compute_totals',
        store=True
    )

    @api.depends('product_uom_qty', 'weight', 'volume')
    def _compute_totals(self):
        for line in self:
            line.total_weight = line.product_uom_qty * line.weight
            line.total_volume = line.product_uom_qty * line.volume