# Fleet Carrier Assignment Module

## Overview

The Fleet Carrier Assignment module is an Odoo extension that automatically assigns delivery vehicles to delivery orders based on weight and volume capacity. It uses a best-fit algorithm to optimize vehicle utilization and tracks all vehicle-order assignments for easy monitoring and reporting.

## Version
- **Module Version**: 19.0.0.1
- **Odoo Version**: 19.0
- **License**: LGPL-3

## Author
Innovax Solutions

---

## Features

### 1. Automatic Vehicle Assignment
- Smart vehicle assignment based on product weight and volume
- Best-fit algorithm to select the smallest suitable vehicle
- Support for single or batch delivery assignment
- Real-time capacity checking and validation

### 2. Vehicle Assignment Tracking
- Complete history of all vehicle-order assignments
- Track which vehicles are assigned to which orders
- Monitor vehicle utilization (weight and volume percentages)
- View assignment status and delivery progress

### 3. Delivery Order Enhancement
- Display total weight and volume on delivery orders
- Vehicle assignment directly from delivery order
- Visual indicators for assigned vehicles
- Filters to view deliveries with/without vehicles

### 4. Batch Processing
- Assign multiple deliveries to one vehicle
- Calculate combined weight/volume for batch assignments
- Optimize vehicle usage across multiple orders

---

## Installation

### Prerequisites
The module depends on the following Odoo modules:
- `stock` - Inventory Management
- `fleet` - Fleet Management
- `sale` - Sales Management
- `delivery` - Delivery Management

### Installation Steps

1. Copy the module to your Odoo addons directory:
   ```bash
   cp -r fleet_carrier_assignment /path/to/odoo/addons/
   ```

2. Update the apps list:
   - Go to Apps menu
   - Click "Update Apps List"
   - Search for "Fleet Carrier Assignment"

3. Install the module:
   - Click "Install" button

4. Or use command line:
   ```bash
   odoo-bin -d your_database -u fleet_carrier_assignment
   ```

---

## Configuration

### Step 1: Configure Vehicle Categories with Capacity

1. Navigate to **Fleet → Configuration → Vehicle Model Category**
2. Create or edit vehicle categories
3. Set the following fields:
   - **Weight Capacity (kg)**: Maximum weight the vehicle can carry
   - **Volume Capacity (m³)**: Maximum volume the vehicle can carry

Example categories:
- Small Van: 500 kg / 5 m³
- Medium Truck: 1500 kg / 15 m³
- Large Truck: 5000 kg / 50 m³

### Step 2: Configure Product Weights and Volumes

1. Navigate to **Inventory → Products → Products**
2. Edit each product
3. Under the "Inventory" tab, set:
   - **Weight (kg)**: Product weight
   - **Volume (m³)**: Product volume

### Step 3: Assign Vehicles to Fleet

1. Navigate to **Fleet → Fleet → Vehicles**
2. Create or edit vehicles
3. Assign each vehicle to a **Vehicle Model** that has a **Category** with capacity defined

---

## Usage

### Assigning a Vehicle to a Single Delivery Order

1. Navigate to **Inventory → Operations → Delivery Orders**
2. Open a delivery order (or create a new one)
3. Ensure the order has products with weight defined
4. Click the **"Assign Carrier"** action button in the list view, or
5. The system will:
   - Calculate total weight and volume
   - Find the smallest suitable vehicle
   - Assign the vehicle to the delivery
   - Create a record in Vehicle Assignments
   - Post a message in the delivery order chatter
   - Post a message in the vehicle chatter

### Batch Assignment (Multiple Deliveries to One Vehicle)

1. Navigate to **Inventory → Operations → Delivery Orders**
2. Select multiple delivery orders (use checkboxes)
3. Click **"Assign Carrier"** from the Actions menu
4. The system will:
   - Calculate **combined** weight and volume of all selected orders
   - Find one vehicle that can carry the entire load
   - Assign the **same vehicle** to all selected deliveries
   - Create assignment records for each delivery
   - Show combined utilization percentage

### Viewing Vehicle Assignments

1. Navigate to **Inventory → Vehicle Assignments → Vehicle Assignments**
2. View all vehicle-order assignments
3. Use filters:
   - **Today**: Assignments made today
   - **This Week**: Assignments made this week
   - **Draft/Waiting/Ready/Done**: Filter by delivery status
4. Use grouping:
   - Group by Vehicle
   - Group by Customer
   - Group by Delivery Order
   - Group by Assignment Date
   - Group by Status

### Viewing Assignments on Delivery Orders

1. Navigate to **Inventory → Operations → Delivery Orders**
2. Use filters:
   - **With Vehicle**: Show only deliveries with assigned vehicles
   - **Without Vehicle**: Show only deliveries without vehicles
3. Group by Vehicle to see all deliveries assigned to each vehicle

---

## Models Documentation

### 1. `stock.picking` (Inherited)

Extended fields for delivery orders:

| Field | Type | Description |
|-------|------|-------------|
| `vehicle_id` | Many2one | Reference to assigned vehicle (fleet.vehicle) |
| `total_weight` | Float | Total weight of all products in kg (computed) |
| `total_volume` | Float | Total volume of all products in m³ (computed) |
| `vehicle_delivery_id` | Many2one | Reference to vehicle delivery assignment |

**Methods:**
- `_compute_total_weight()`: Calculates total weight from all move lines
- `_compute_total_volume()`: Calculates total volume from all move lines
- `action_assign_carrier()`: Main method for vehicle assignment logic

### 2. `assign.carrier` (New Model)

Tracks vehicle-order assignment history:

| Field | Type | Description | Stored |
|-------|------|-------------|---------|
| `vehicle_id` | Many2one | Assigned vehicle | Yes |
| `picking_id` | Many2one | Related delivery order | Yes |
| `partner_id` | Many2one | Customer (related from picking) | Yes |
| `assignment_date` | Datetime | Date and time of assignment | Yes |
| `state` | Selection | Delivery status (related from picking) | Yes |
| `total_weight` | Float | Weight of delivery (related) | Yes |
| `total_volume` | Float | Volume of delivery (related) | Yes |
| `vehicle_weight_capacity` | Float | Vehicle weight capacity (computed) | Yes |
| `vehicle_volume_capacity` | Float | Vehicle volume capacity (computed) | Yes |
| `weight_utilization` | Float | Weight utilization % (computed) | Yes |
| `volume_utilization` | Float | Volume utilization % (computed) | Yes |
| `origin` | Char | Source document (related) | Yes |
| `scheduled_date` | Datetime | Scheduled delivery date (related) | Yes |
| `license_plate` | Char | Vehicle license plate (related) | Yes |

**Methods:**
- `_compute_vehicle_capacity()`: Computes vehicle capacity from category
- `_compute_utilization()`: Calculates weight and volume utilization percentages

---

## Views Documentation

### Stock Picking Views

#### Form View Enhancement
File: `views/stock_picking_views.xml`

Added fields after `origin`:
- Vehicle (dropdown with vehicle selection)
- Total Weight (automatically calculated)
- Total Volume (automatically calculated)

#### Tree View Enhancement
Added columns:
- Vehicle (optional, shown by default)
- Total Weight (optional, shown by default)
- Total Volume (optional, shown by default)

#### Search View Enhancement
New filters:
- **With Vehicle**: Filter deliveries with assigned vehicles
- **Without Vehicle**: Filter deliveries without vehicles

New grouping:
- **Group by Vehicle**: Group deliveries by assigned vehicle

#### Server Action
- **Assign Carrier**: Available in list view action menu
- Executes `action_assign_carrier()` method on selected records

### Assign Carrier Views

#### List View
File: `views/assign_carrier_views.xml`

Displays all vehicle assignments with:
- Assignment Date
- Vehicle Name
- License Plate
- Delivery Order
- Customer
- Source Document
- Weight and Volume
- Vehicle Capacities
- Utilization Percentages (with percentage widget)
- Delivery Status (with color decorations)
- Scheduled Date

Color decorations:
- Blue: Draft
- Orange: Waiting/Confirmed/Assigned
- Green: Done
- Red: Cancelled

#### Form View
Organized sections:
1. **Assignment Information**: Vehicle, license plate, date, status
2. **Delivery Information**: Order reference, customer, origin, scheduled date
3. **Load Details**: Total weight and volume
4. **Vehicle Capacity**: Weight and volume capacity
5. **Utilization**: Percentage usage of weight and volume

#### Search View
Filters:
- **Today**: Assignments created today
- **This Week**: Assignments created this week
- **Draft/Waiting/Ready/Done**: Filter by delivery status

Group By options:
- Vehicle
- Customer
- Delivery Order
- Assignment Date
- Status

---

## Algorithm Details

### Best-Fit Vehicle Assignment Algorithm

The module uses a best-fit algorithm to optimize vehicle selection:

1. **Calculate Load**: Sum total weight and volume of all selected deliveries
2. **Find Suitable Vehicles**:
   - Check all vehicles with defined capacity
   - Filter vehicles where capacity >= required load
   - Consider both weight AND volume constraints
3. **Sort by Capacity**: Sort suitable vehicles from smallest to largest
4. **Select Best Fit**: Pick the smallest vehicle that can carry the load
5. **Assign Vehicle**: Set the same vehicle to all selected deliveries
6. **Create Records**: Generate assignment records for tracking
7. **Notify Users**: Post messages in delivery and vehicle chatters

### Capacity Validation

Weight validation:
```
vehicle_weight_capacity >= sum(delivery.total_weight)
```

Volume validation (if applicable):
```
vehicle_volume_capacity >= sum(delivery.total_volume)
```

### Utilization Calculation

Weight utilization:
```
(total_weight / vehicle_weight_capacity) * 100
```

Volume utilization:
```
(total_volume / vehicle_volume_capacity) * 100
```

---

## Security & Access Rights

File: `security/ir.model.access.csv`

### Stock Users (group_stock_user)
- **Fleet Vehicle**: Read-only access
- **Assign Carrier**: Read-only access

### Stock Managers (group_stock_manager)
- **Assign Carrier**: Full access (create, read, write, delete)

---

## Menu Structure

```
Inventory
├── Operations
│   └── Delivery Orders (enhanced with vehicle assignment)
└── Vehicle Assignments
    └── Vehicle Assignments (new menu)
```

---

## Technical Details

### File Structure

```
fleet_carrier_assignment/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── stock_picking.py        # Delivery order extension
│   └── assign_carrier.py       # Assignment tracking model
├── views/
│   ├── stock_picking_views.xml # Delivery order view enhancements
│   └── assign_carrier_views.xml # Assignment views and menu
├── security/
│   └── ir.model.access.csv     # Access rights configuration
└── README.md                    # This file
```

### Dependencies

```python
'depends': [
    'stock',      # Inventory Management
    'fleet',      # Fleet Management
    'sale',       # Sales Management
    'delivery',   # Delivery Management
]
```

### Data Loading Order

1. `security/ir.model.access.csv` - Access rights (loaded first)
2. `views/stock_picking_views.xml` - Delivery order views
3. `views/assign_carrier_views.xml` - Assignment views and menu

---

## Logging

The module uses Python logging for debugging and monitoring:

```python
import logging
_logger = logging.getLogger(__name__)
```

Log levels:
- **INFO**: Vehicle assignment process, vehicle selection, capacity checks
- **ERROR**: No suitable vehicles found, capacity issues

View logs in Odoo:
```bash
tail -f /var/log/odoo/odoo-server.log
```

---

## Error Handling

### Common Errors and Solutions

#### "No products to deliver"
**Cause**: Delivery order has no move lines
**Solution**: Add products to the delivery order

#### "Total weight is 0"
**Cause**: Products don't have weight defined
**Solution**: Set weight on products (Inventory → Products → Inventory tab)

#### "No vehicles with capacity defined"
**Cause**: No vehicle categories have weight_capacity set
**Solution**: Configure capacity in Fleet → Configuration → Vehicle Model Category

#### "No vehicle can carry these combined deliveries"
**Cause**: Combined weight/volume exceeds all available vehicle capacities
**Solutions**:
- Add larger vehicles to fleet
- Split deliveries into smaller batches
- Increase capacity of existing vehicle categories

---

## Best Practices

### 1. Product Configuration
- Always set weight for products used in deliveries
- Set volume for products where volume constraints matter
- Keep product data up to date

### 2. Vehicle Categories
- Define realistic capacity values
- Create categories for different vehicle sizes
- Update capacities when vehicle specs change

### 3. Vehicle Assignment
- Review auto-assigned vehicles before confirming
- Use batch assignment for route optimization
- Monitor utilization percentages to maximize efficiency

### 4. Monitoring
- Regularly check Vehicle Assignments view
- Use filters to track pending/completed deliveries
- Group by vehicle to balance workload

---

## API Integration

### Programmatic Vehicle Assignment

```python
# Assign vehicle to a single delivery
picking = self.env['stock.picking'].browse(picking_id)
picking.action_assign_carrier()

# Batch assignment
pickings = self.env['stock.picking'].browse([id1, id2, id3])
pickings.action_assign_carrier()

# Get assignment history
assignments = self.env['assign.carrier'].search([
    ('vehicle_id', '=', vehicle_id)
])

# Get all assignments for a delivery
assignments = self.env['assign.carrier'].search([
    ('picking_id', '=', picking_id)
])
```

---

## Customization Examples

### Custom Capacity Check

Extend the algorithm to add custom constraints:

```python
class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_assign_carrier(self):
        # Add custom validation here
        # Then call parent method
        return super(StockPicking, self).action_assign_carrier()
```

### Add Custom Fields to Assignment

```python
class AssignCarrier(models.Model):
    _inherit = 'assign.carrier'

    driver_id = fields.Many2one('res.partner', string='Driver')
    estimated_time = fields.Float(string='Estimated Time (hours)')
```

---

## Troubleshooting

### Module Not Appearing in Apps
1. Check file permissions
2. Restart Odoo server
3. Update apps list
4. Check `__manifest__.py` syntax

### Vehicle Not Being Assigned
1. Check product weights are defined
2. Verify vehicle category has capacity
3. Check Odoo logs for error messages
4. Ensure vehicle is linked to a model with category

### Assignment Records Not Created
1. Verify access rights for current user
2. Check if `assign.carrier` model is loaded
3. Review Odoo logs for errors
4. Upgrade module: `odoo-bin -u fleet_carrier_assignment`

---

## Frequently Asked Questions (FAQ)

### Q: Can I manually assign a vehicle?
**A**: Yes, you can manually select a vehicle in the delivery order form view using the "Assigned Vehicle" field.

### Q: Can one vehicle be assigned to multiple deliveries?
**A**: Yes, use batch assignment by selecting multiple deliveries and clicking "Assign Carrier".

### Q: Can I change the assigned vehicle after assignment?
**A**: Yes, you can change the vehicle field on the delivery order. However, this won't update the assignment record.

### Q: How do I remove a vehicle assignment?
**A**: Clear the "Assigned Vehicle" field on the delivery order.

### Q: Can I assign deliveries without weight defined?
**A**: No, products must have weight defined for the assignment algorithm to work.

### Q: What happens if no suitable vehicle is found?
**A**: The system shows an error message indicating the required capacity and maximum available capacity.

---

## Changelog

### Version 19.0.0.1
- Initial release
- Automatic vehicle assignment based on weight and volume
- Best-fit algorithm implementation
- Vehicle assignment tracking model
- Batch assignment support
- Utilization monitoring
- Enhanced delivery order views
- Vehicle assignments menu and views

---

## Support

For issues, questions, or feature requests:
- Create an issue in your project repository
- Contact: Innovax Solutions
- Documentation: This README file

---

## License

LGPL-3 (GNU Lesser General Public License v3.0)

---

## Future Enhancements

Planned features for future versions:
- Route optimization
- Driver assignment
- Real-time vehicle tracking integration
- Delivery time estimation
- Vehicle availability calendar
- Cost calculation based on distance
- Fuel consumption tracking
- Multi-depot support
- Mobile app integration

---

## Contributing

To contribute to this module:
1. Follow Odoo coding guidelines
2. Add appropriate comments and docstrings
3. Update this documentation
4. Test thoroughly before committing
5. Submit pull requests with clear descriptions

---

**End of Documentation**
