# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    vehicle_id = fields.Many2one(
        'fleet.vehicle', 
        string='Assigned Vehicle',
        help='Vehicle assigned to this delivery order'
    )
    assignment_id = fields.Many2one(
        'assign.carrier',
        string='Vehicle Assignment',
        help='Related vehicle assignment record'
    )
    total_weight = fields.Float(
        string='Total Weight (kg)', 
        compute='_compute_total_weight', 
        store=True,
        help='Total weight of all products in this delivery'
    )
    total_volume = fields.Float(
        string='Total Volume (m³)', 
        compute='_compute_total_volume', 
        store=True,
        help='Total volume of all products in this delivery'
    )
    
    @api.depends('move_ids.product_uom_qty', 'move_ids.product_id.weight')
    def _compute_total_weight(self):
        """Calculate total weight of all products"""
        for picking in self:
            total = 0.0
            for move in picking.move_ids:
                if move.product_id and move.product_id.weight:
                    total += move.product_uom_qty * move.product_id.weight
            picking.total_weight = total
    
    @api.depends('move_ids.product_uom_qty', 'move_ids.product_id.volume')
    def _compute_total_volume(self):
        """Calculate total volume of all products"""
        for picking in self:
            total = 0.0
            for move in picking.move_ids:
                if move.product_id and move.product_id.volume:
                    total += move.product_uom_qty * move.product_id.volume
            picking.total_volume = total
    
    def action_assign_carrier(self):
        """
        Assign vehicles and create a single assignment record with all deliveries
        """
        if not self:
            return
        
        # Check if any delivery order already has a vehicle assignment
        already_assigned = self.filtered(lambda p: p.assignment_id)
        
        if already_assigned:
            # Show which deliveries are already assigned
            assigned_details = []
            for picking in already_assigned:
                assigned_details.append(
                    "• %s → %s (Assignment: %s)" % (
                        picking.name,
                        picking.vehicle_id.name if picking.vehicle_id else 'Unknown',
                        picking.assignment_id.name
                    )
                )
            
            details_text = '\n'.join(assigned_details)
            
            raise UserError(
                "Some delivery orders are already assigned to a vehicle!\n\n"
                "%s\n\n"
                "Please remove them from the selection or unassign them first." % details_text
            )
        
        # Calculate combined weight and volume
        combined_weight = sum(self.mapped('total_weight'))
        combined_volume = sum(self.mapped('total_volume'))
        
        # Validate
        for picking in self:
            if not picking.move_ids:
                raise UserError("No products to deliver in %s!" % picking.name)
        
        if combined_weight <= 0:
            raise UserError("Total weight is 0.\nPlease ensure products have weight defined.")
        
        # Get available vehicles
        vehicles = self.env['fleet.vehicle'].search([
            ('model_id.category_id.weight_capacity', '>', 0)
        ])
        
        if not vehicles:
            raise UserError(
                "No vehicles with capacity defined!\n"
                "Please configure weight_capacity in Fleet → Configuration → Vehicle Model Category"
            )
        
        _logger.info("=" * 80)
        _logger.info("STARTING VEHICLE ASSIGNMENT")
        _logger.info("Required Load: %.2f kg, %.2f m³" % (combined_weight, combined_volume))
        _logger.info("Number of deliveries: %s" % len(self))
        
        # Find suitable vehicles using best-fit algorithm
        suitable_vehicles = []
        
        for vehicle in vehicles:
            category = vehicle.model_id.category_id
            if not category:
                continue
            
            vehicle_weight_capacity = category.weight_capacity or 0
            vehicle_volume_capacity = category.volume_capacity or 0
            
            if vehicle_weight_capacity >= combined_weight:
                if combined_volume > 0 and vehicle_volume_capacity > 0:
                    if vehicle_volume_capacity >= combined_volume:
                        suitable_vehicles.append(vehicle)
                else:
                    suitable_vehicles.append(vehicle)
        
        if not suitable_vehicles:
            max_weight = max(
                v.model_id.category_id.weight_capacity 
                for v in vehicles 
                if v.model_id.category_id
            )
            delivery_list = ', '.join(self.mapped('name'))
            raise UserError(
                "No vehicle can carry these combined deliveries!\n\n"
                "Deliveries: %s\n"
                "Combined Weight Required: %.2f kg\n"
                "Combined Volume Required: %.2f m³\n"
                "Maximum available capacity: %.2f kg" % 
                (delivery_list, combined_weight, combined_volume, max_weight)
            )
        
        # Sort and pick the smallest suitable vehicle
        suitable_vehicles_sorted = sorted(
            suitable_vehicles,
            key=lambda v: (
                v.model_id.category_id.weight_capacity or 0,
                v.model_id.category_id.volume_capacity or 0
            )
        )
        
        suitable_vehicle = suitable_vehicles_sorted[0]
        category = suitable_vehicle.model_id.category_id
        
        _logger.info("SELECTED VEHICLE: %s" % suitable_vehicle.name)
        _logger.info("Capacity: %.2f kg / %.2f m³" % (category.weight_capacity, category.volume_capacity))
        _logger.info("=" * 80)
        
        # Create a SINGLE assignment record
        assignment = self.env['assign.carrier'].create({
            'vehicle_id': suitable_vehicle.id,
            'assignment_date': fields.Datetime.now(),
            'state': 'assigned',
        })
        
        # Link all delivery orders to this assignment
        for picking in self:
            # Update vehicle_id on picking
            picking.write({
                'vehicle_id': suitable_vehicle.id,
                'assignment_id': assignment.id
            })
            
            # Create picking line in assignment
            self.env['assign.carrier.picking'].create({
                'assignment_id': assignment.id,
                'picking_id': picking.id,
            })
            
            # Create product lines for this picking
            for move in picking.move_ids:
                if move.product_id:
                    self.env['assign.carrier.product'].create({
                        'assignment_id': assignment.id,
                        'picking_id': picking.id,
                        'move_id': move.id,
                    })
        
        # Calculate utilization
        weight_util = (combined_weight / category.weight_capacity * 100) if category.weight_capacity else 0
        volume_util = (combined_volume / category.volume_capacity * 100) if category.volume_capacity else 0
        
        # Post message in assignment record
        assignment.message_post(
            body="<b>Vehicle Assignment Created</b><br/>"
                 "<b>Vehicle:</b> %s [%s]<br/>"
                 "<b>Deliveries:</b> %s<br/>"
                 "<b>Total Weight:</b> %.2f kg<br/>"
                 "<b>Total Volume:</b> %.2f m³<br/>"
                 "<b>Utilization:</b> %.1f%% (Weight), %.1f%% (Volume)" % (
                     suitable_vehicle.name,
                     suitable_vehicle.license_plate or 'N/A',
                     len(self),
                     combined_weight,
                     combined_volume,
                     weight_util,
                     volume_util
                 ),
            subject="Assignment Created"
        )
        
        # Return action to open the assignment form
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vehicle Assignment',
            'res_model': 'assign.carrier',
            'res_id': assignment.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_unassign_carrier(self):
        """
        Remove vehicle assignment from delivery orders
        """
        if not self:
            return
        
        # Check if any delivery has an assignment
        assigned_pickings = self.filtered(lambda p: p.assignment_id)
        
        if not assigned_pickings:
            raise UserError("No delivery orders are assigned to any vehicle!")
        
        # Group by assignment
        assignments = assigned_pickings.mapped('assignment_id')
        
        # Prepare details for logging
        _logger.info("=" * 80)
        _logger.info("UNASSIGNING VEHICLE ASSIGNMENTS")
        for assignment in assignments:
            related_pickings = assigned_pickings.filtered(lambda p: p.assignment_id == assignment)
            _logger.info("Assignment: %s" % assignment.name)
            _logger.info("Vehicle: %s" % assignment.vehicle_id.name)
            _logger.info("Deliveries: %s" % ', '.join(related_pickings.mapped('name')))
        _logger.info("=" * 80)
        
        # Store assignment names for notification
        assignment_names = ', '.join(assignments.mapped('name'))
        
        # Remove vehicle and assignment from pickings
        assigned_pickings.write({
            'vehicle_id': False,
            'assignment_id': False
        })
        
        # Delete assignment records (this will cascade delete related lines)
        assignments.unlink()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Vehicle Assignment Removed',
                'message': '%s delivery order(s) have been unassigned.<br/>Assignments deleted: %s' % (
                    len(assigned_pickings),
                    assignment_names
                ),
                'type': 'success',
                'sticky': False,
            }
        }