# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AssignCarrierPicking(models.Model):
    """Define this model FIRST"""
    _name = 'assign.carrier.picking'
    _description = 'Assignment Delivery Order Line'
    _order = 'id'

    assignment_id = fields.Many2one(
        'assign.carrier',
        string='Assignment',
        required=True,
        ondelete='cascade',
        index=True
    )
    picking_id = fields.Many2one(
        'stock.picking',
        string='Delivery Order',
        required=True,
        ondelete='restrict',
        index=True
    )
    partner_id = fields.Many2one(
        'res.partner',
        related='picking_id.partner_id',
        string='Customer',
        store=True,
        readonly=True
    )
    origin = fields.Char(
        related='picking_id.origin',
        string='Source Document',
        store=True,
        readonly=True
    )
    scheduled_date = fields.Datetime(
        related='picking_id.scheduled_date',
        string='Scheduled Date',
        store=True,
        readonly=True
    )
    state = fields.Selection(
        related='picking_id.state',
        string='Status',
        store=True,
        readonly=True
    )
    total_weight = fields.Float(
        related='picking_id.total_weight',
        string='Weight (kg)',
        store=True,
        readonly=True
    )
    total_volume = fields.Float(
        related='picking_id.total_volume',
        string='Volume (m³)',
        store=True,
        readonly=True
    )
    
    _sql_constraints = [
        ('unique_assignment_picking', 
         'UNIQUE(assignment_id, picking_id)', 
         'A delivery order can only be added once per assignment!')
    ]

    @api.model_create_multi
    def create(self, vals_list):
        """Automatically update delivery order when added through form"""
        records = super(AssignCarrierPicking, self).create(vals_list)
        
        for record in records:
            if record.assignment_id and record.picking_id:
                # Check if delivery is already assigned to another vehicle
                if record.picking_id.assignment_id and record.picking_id.assignment_id != record.assignment_id:
                    raise ValidationError(
                        "Delivery Order %s is already assigned to %s!\n\n"
                        "Please unassign it first before adding to this vehicle." % (
                            record.picking_id.name,
                            record.picking_id.assignment_id.name
                        )
                    )
                
                # Update the delivery order with vehicle and assignment info
                record.picking_id.write({
                    'vehicle_id': record.assignment_id.vehicle_id.id,
                    'assignment_id': record.assignment_id.id
                })
                
                # Create product lines for this picking
                for move in record.picking_id.move_ids:
                    if move.product_id:
                        # Check if product line already exists
                        existing_product = self.env['assign.carrier.product'].search([
                            ('assignment_id', '=', record.assignment_id.id),
                            ('picking_id', '=', record.picking_id.id),
                            ('move_id', '=', move.id)
                        ], limit=1)
                        
                        if not existing_product:
                            self.env['assign.carrier.product'].create({
                                'assignment_id': record.assignment_id.id,
                                'picking_id': record.picking_id.id,
                                'move_id': move.id,
                            })
                
                # Trigger validation on parent assignment
                record.assignment_id._check_capacity_utilization()
                
                # Post message to assignment
                record.assignment_id.message_post(
                    body="Delivery Order <b>%s</b> added to assignment<br/>"
                         "Customer: %s<br/>"
                         "Weight: %.2f kg | Volume: %.2f m³" % (
                             record.picking_id.name,
                             record.partner_id.name if record.partner_id else 'N/A',
                             record.total_weight,
                             record.total_volume
                         )
                )
        
        return records

    def write(self, vals):
        """Update delivery order when picking changes"""
        result = super(AssignCarrierPicking, self).write(vals)
        
        for record in self:
            if record.assignment_id and record.picking_id:
                # Update vehicle assignment on delivery order
                record.picking_id.write({
                    'vehicle_id': record.assignment_id.vehicle_id.id,
                    'assignment_id': record.assignment_id.id
                })
                
                # Trigger validation on parent assignment
                record.assignment_id._check_capacity_utilization()
        
        return result

    def unlink(self):
        """Clear vehicle assignment from delivery order when removed"""
        # Store info for messages before deletion
        removal_info = []
        for record in self:
            removal_info.append({
                'assignment': record.assignment_id,
                'picking_name': record.picking_id.name,
                'picking': record.picking_id
            })
        
        result = super(AssignCarrierPicking, self).unlink()
        
        # Clear vehicle and assignment from delivery orders and post messages
        for info in removal_info:
            picking = info['picking']
            assignment = info['assignment']
            
            # Check if this picking is still assigned to another assignment
            still_assigned = self.env['assign.carrier.picking'].search([
                ('picking_id', '=', picking.id)
            ], limit=1)
            
            if not still_assigned:
                picking.write({
                    'vehicle_id': False,
                    'assignment_id': False
                })
            
            # Post message to assignment
            if assignment.exists():
                assignment.message_post(
                    body="Delivery Order <b>%s</b> removed from assignment" % info['picking_name']
                )
        
        return result


class AssignCarrierProduct(models.Model):
    """Define this model SECOND"""
    _name = 'assign.carrier.product'
    _description = 'Assignment Product Line'
    _order = 'picking_name, id'

    assignment_id = fields.Many2one(
        'assign.carrier',
        string='Assignment',
        required=True,
        ondelete='cascade',
        index=True
    )
    picking_id = fields.Many2one(
        'stock.picking',
        string='Delivery Order',
        required=True,
        index=True
    )
    picking_name = fields.Char(
        related='picking_id.name',
        string='DO Reference',
        store=True,
        readonly=True
    )
    move_id = fields.Many2one(
        'stock.move',
        string='Stock Move',
        required=True,
        index=True
    )
    product_id = fields.Many2one(
        'product.product',
        related='move_id.product_id',
        string='Product',
        store=True,
        readonly=True
    )
    product_uom_qty = fields.Float(
        related='move_id.product_uom_qty',
        string='Quantity',
        store=True,
        readonly=True
    )
    product_uom = fields.Many2one(
        'uom.uom',
        related='move_id.product_uom',
        string='Unit',
        store=True,
        readonly=True
    )
    weight = fields.Float(
        string='Unit Weight (kg)',
        related='product_id.weight',
        store=True,
        readonly=True
    )
    volume = fields.Float(
        string='Unit Volume (m³)',
        related='product_id.volume',
        store=True,
        readonly=True
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


class AssignCarrier(models.Model):
    """Define this model LAST"""
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
        index=True,
        default=lambda self: 'New',
        tracking=True
    )
    vehicle_id = fields.Many2one(
        'fleet.vehicle',
        string='Vehicle',
        required=True,
        ondelete='restrict',
        help='Assigned vehicle',
        tracking=True,
        index=True
    )
    license_plate = fields.Char(
        related='vehicle_id.license_plate',
        string='License Plate',
        store=True,
        readonly=True,
        help='Vehicle license plate'
    )
    
    # Vehicle availability field for easy tracking
    vehicle_availability = fields.Selection(
        related='vehicle_id.vehicle_availability',
        string='Vehicle Status',
        store=False,
        readonly=True
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
            # Only generate sequence if name is not provided or is 'New'
            if not vals.get('name') or vals.get('name') in ('New', '/'):
                vals['name'] = self.env['ir.sequence'].next_by_code('assign.carrier')
                # If sequence doesn't return a value, use a fallback
                if not vals['name']:
                    vals['name'] = 'VA/00001'
        
        return super(AssignCarrier, self).create(vals_list)

    def write(self, vals):
        """Override write to check capacity and update delivery orders when vehicle changes"""
        # Store old vehicle_id before update
        old_vehicle_ids = {record.id: record.vehicle_id.id for record in self}
        
        result = super(AssignCarrier, self).write(vals)
        
        # If vehicle changed, update all related delivery orders
        if 'vehicle_id' in vals:
            for record in self:
                if old_vehicle_ids.get(record.id) != record.vehicle_id.id:
                    # Update all delivery orders with new vehicle
                    for picking_line in record.picking_ids:
                        picking_line.picking_id.write({
                            'vehicle_id': record.vehicle_id.id
                        })
                    
                    # Post message about vehicle change
                    record.message_post(
                        body="Vehicle changed to: <b>%s</b> [%s]" % (
                            record.vehicle_id.name,
                            record.license_plate or 'N/A'
                        )
                    )
        
        # Check capacity after write if relevant fields changed
        if any(key in vals for key in ['picking_ids', 'vehicle_id']):
            self._check_capacity_utilization()
        
        return result

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

    @api.constrains('picking_ids', 'vehicle_id')
    def _check_capacity_utilization(self):
        """Check if weight and volume utilization doesn't exceed 100%"""
        for record in self:
            # Force recompute to get latest values
            record._compute_totals()
            record._compute_utilization()
            
            if record.weight_utilization > 100:
                raise ValidationError(
                    "⚠️ Weight Capacity Exceeded!\n\n"
                    "📊 Current Utilization: %.2f%%\n"
                    "⚖️  Total Weight: %.2f kg\n"
                    "🚛 Vehicle Capacity: %.2f kg\n"
                    "❌ Exceeds by: %.2f kg\n\n"
                    "Please remove some delivery orders or assign a larger vehicle." % (
                        record.weight_utilization,
                        record.total_weight,
                        record.vehicle_weight_capacity,
                        record.total_weight - record.vehicle_weight_capacity
                    )
                )
            
            if record.volume_utilization > 100:
                raise ValidationError(
                    "⚠️ Volume Capacity Exceeded!\n\n"
                    "📊 Current Utilization: %.2f%%\n"
                    "📦 Total Volume: %.2f m³\n"
                    "🚛 Vehicle Capacity: %.2f m³\n"
                    "❌ Exceeds by: %.2f m³\n\n"
                    "Please remove some delivery orders or assign a larger vehicle." % (
                        record.volume_utilization,
                        record.total_volume,
                        record.vehicle_volume_capacity,
                        record.total_volume - record.vehicle_volume_capacity
                    )
                )
    
    def _update_vehicle_availability(self, availability_state):
        """
        Helper method to update vehicle availability
        Only updates if the fleet_vehicle_revenue module is installed
        """
        self.ensure_one()
        if self.vehicle_id and hasattr(self.vehicle_id, 'vehicle_availability'):
            self.vehicle_id.write({'vehicle_availability': availability_state})
            self.message_post(
                body="Vehicle availability changed to: <b>%s</b>" % dict(
                    self.vehicle_id._fields['vehicle_availability'].selection
                ).get(availability_state, availability_state)
            )
                
    def action_set_assigned(self):
        """Set state to assigned and update vehicle availability to reserved"""
        for record in self:
            record.state = 'assigned'
            # Set vehicle to reserved when assignment is confirmed
            record._update_vehicle_availability('reserved')

    def action_set_draft(self):
        """Set state to draft and update vehicle availability to available"""
        for record in self:
            record.state = 'draft'
            # Set vehicle back to available when returning to draft
            record._update_vehicle_availability('available')

    def action_set_in_transit(self):
        """
        Set state to in_transit and update vehicle availability to in_use
        This is the DISPATCH button action
        """
        for record in self:
            record.state = 'in_transit'
            # Set vehicle to in_use when dispatched (in transit)
            record._update_vehicle_availability('in_use')
            
            # Post message to chatter
            record.message_post(
                body="<b>Vehicle Dispatched</b><br/>"
                     "Vehicle: %s [%s]<br/>"
                     "Deliveries: %s<br/>"
                     "Dispatched at: %s" % (
                         record.vehicle_id.name,
                         record.license_plate or 'N/A',
                         record.delivery_count,
                         fields.Datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                     ),
                subject="Vehicle Dispatched"
            )

    def action_set_done(self):
        """Set state to done and update vehicle availability to available"""
        for record in self:
            record.state = 'done'
            # Set vehicle back to available when done
            record._update_vehicle_availability('available')
            
            # Post completion message
            record.message_post(
                body="<b>Delivery Completed</b><br/>"
                     "Vehicle: %s<br/>"
                     "Total Deliveries: %s<br/>"
                     "Completed at: %s" % (
                         record.vehicle_id.name,
                         record.delivery_count,
                         fields.Datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                     ),
                subject="Delivery Completed"
            )
    
    def action_set_cancel(self):
        """Set state to cancel and update vehicle availability to available"""
        for record in self:
            record.state = 'cancel'
            # Set vehicle back to available when cancelled
            record._update_vehicle_availability('available')
            
            # Post cancellation message
            record.message_post(
                body="<b>Assignment Cancelled</b><br/>"
                     "Vehicle: %s<br/>"
                     "Reason: User cancelled the assignment" % record.vehicle_id.name,
                subject="Assignment Cancelled"
            )