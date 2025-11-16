# Fleet Carrier Assignment - Quick Start Guide

## 5-Minute Setup

### Step 1: Install the Module (2 minutes)

1. **Access Odoo Apps**
   - Go to **Apps** menu
   - Click **Update Apps List**
   - Search for "Fleet Carrier Assignment"
   - Click **Install**

2. **Or use command line**:
   ```bash
   odoo-bin -d your_database -u fleet_carrier_assignment
   ```

### Step 2: Configure Vehicle Capacity (2 minutes)

1. **Go to Fleet → Configuration → Vehicle Model Category**

2. **Edit or create categories**:

   | Category Name | Weight Capacity (kg) | Volume Capacity (m³) |
   |--------------|---------------------|---------------------|
   | Small Van    | 500                 | 5                   |
   | Medium Truck | 1500                | 15                  |
   | Large Truck  | 5000                | 50                  |

3. **Save** each category

### Step 3: Configure Products (1 minute)

1. **Go to Inventory → Products → Products**
2. **Edit a product**
3. **Go to "Inventory" tab**
4. **Set**:
   - Weight: 10 kg (example)
   - Volume: 0.1 m³ (example)
5. **Save**

---

## First Assignment (3 minutes)

### Scenario: Assign Vehicle to Delivery Order

1. **Go to Inventory → Operations → Delivery Orders**

2. **Create or open a delivery order**

3. **Add products** with weight defined

4. **Click "Assign Carrier"** button in the list view

5. **Result**:
   - Vehicle automatically assigned
   - Notification shows which vehicle was selected
   - Assignment record created

### View the Assignment

1. **Go to Inventory → Vehicle Assignments → Vehicle Assignments**
2. **See the new record** with:
   - Vehicle name
   - Delivery order
   - Customer
   - Weight/volume
   - Utilization percentage

---

## Common Scenarios

### Scenario 1: Single Delivery Assignment

**Use Case**: You have one delivery order to assign

**Steps**:
1. Open the delivery order
2. Verify products have weight
3. Click "Assign Carrier"
4. System selects smallest suitable vehicle

**Example**:
- Delivery weight: 100 kg
- Available vehicles:
  - Small Van: 500 kg capacity
  - Large Truck: 5000 kg capacity
- **Selected**: Small Van (best fit)

---

### Scenario 2: Batch Assignment

**Use Case**: Multiple deliveries going same direction

**Steps**:
1. Go to delivery orders list
2. Select multiple deliveries (checkboxes)
3. Click **Actions** → **Assign Carrier**
4. System assigns ONE vehicle to ALL deliveries

**Example**:
- 3 deliveries: 100 kg + 150 kg + 200 kg = 450 kg total
- Selected vehicle: Small Van (500 kg capacity)
- Utilization: 90%

---

### Scenario 3: No Suitable Vehicle

**Problem**: No vehicle large enough

**Steps**:
1. Try to assign carrier
2. Error message appears: "No vehicle can carry these combined deliveries"
3. **Solutions**:
   - Split into smaller deliveries
   - Add larger vehicle to fleet
   - Increase vehicle category capacity

---

### Scenario 4: View All Assignments by Vehicle

**Use Case**: See what each vehicle is delivering

**Steps**:
1. Go to **Inventory → Vehicle Assignments**
2. Click **Group By** → **Vehicle**
3. See all assignments grouped by vehicle
4. Expand each vehicle to see deliveries

---

### Scenario 5: Filter Today's Assignments

**Use Case**: See what's being delivered today

**Steps**:
1. Go to **Inventory → Vehicle Assignments**
2. Click **Today** filter
3. See all assignments made today
4. Optionally group by vehicle or customer

---

## Tips & Tricks

### Tip 1: Always Set Product Weight
If products don't have weight, assignment will fail.
**Solution**: Set default weight for product categories.

### Tip 2: Monitor Utilization
Keep utilization between 70-90% for optimal efficiency.
**Low utilization**: Using vehicle bigger than needed
**High utilization**: Near capacity, good efficiency

### Tip 3: Use Batch Assignment for Route Optimization
Assign multiple deliveries to same vehicle to:
- Reduce trips
- Save fuel
- Improve efficiency

### Tip 4: Check Assignment History
Before assigning, check vehicle assignments to avoid double-booking.

### Tip 5: Use Filters Effectively
- Filter by "Without Vehicle" to find unassigned deliveries
- Filter by "With Vehicle" + Group by Vehicle to see routes

---

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Open delivery orders | Alt + D |
| Select all | Ctrl + A |
| Filter search | Ctrl + K |
| Create new | Alt + C |

---

## Troubleshooting

### Problem: "No products to deliver" error
**Cause**: Delivery order has no products
**Solution**: Add products to delivery order

### Problem: "Total weight is 0" error
**Cause**: Products don't have weight defined
**Solution**:
1. Go to product form
2. Set weight in Inventory tab
3. Save product
4. Try assignment again

### Problem: "No vehicles with capacity defined" error
**Cause**: No vehicle categories have capacity set
**Solution**:
1. Go to Fleet → Configuration → Vehicle Model Category
2. Edit categories
3. Set Weight Capacity
4. Save

### Problem: Vehicle assigned but not ideal
**Cause**: Algorithm picks smallest suitable vehicle
**Solution**:
- If you want different vehicle, manually change it
- Or adjust vehicle capacities to guide algorithm

### Problem: Cannot see assignment records
**Cause**: Insufficient access rights
**Solution**:
- Ask admin to grant Stock User/Manager rights
- Check Settings → Users & Companies → Users

---

## Video Tutorials

### Watch These Quick Videos

1. **Installation & Setup** (3 min)
   - Install module
   - Configure vehicle categories
   - Set product weights

2. **Basic Assignment** (2 min)
   - Assign vehicle to one delivery
   - View assignment record

3. **Batch Assignment** (3 min)
   - Select multiple deliveries
   - Assign to one vehicle
   - View utilization

4. **Monitoring & Reports** (4 min)
   - Use filters and groups
   - Track vehicle assignments
   - Analyze utilization

---

## Next Steps

### Learn More
- Read full [README.md](README.md) for detailed documentation
- Read [TECHNICAL_GUIDE.md](TECHNICAL_GUIDE.md) for developer info

### Customize
- Add custom fields to assignments
- Extend vehicle selection algorithm
- Create custom reports

### Get Support
- Check documentation
- Contact: Innovax Solutions
- Report issues in project repository

---

## Cheat Sheet

### Quick Reference Card

```
┌─────────────────────────────────────────────────┐
│ FLEET CARRIER ASSIGNMENT CHEAT SHEET            │
├─────────────────────────────────────────────────┤
│                                                 │
│ SETUP:                                          │
│  ✓ Set vehicle category capacity                │
│  ✓ Set product weights                          │
│  ✓ Add vehicles to fleet                        │
│                                                 │
│ ASSIGN:                                         │
│  • Single: Select delivery → Assign Carrier     │
│  • Batch: Select multiple → Actions → Assign   │
│                                                 │
│ VIEW ASSIGNMENTS:                               │
│  • Inventory → Vehicle Assignments              │
│  • Filter by: Today, This Week, Status          │
│  • Group by: Vehicle, Customer, Date            │
│                                                 │
│ TROUBLESHOOT:                                   │
│  • No weight? → Set product weight              │
│  • No capacity? → Configure category            │
│  • No vehicles? → Add to fleet                  │
│                                                 │
│ OPTIMIZE:                                       │
│  • Target 70-90% utilization                    │
│  • Batch deliveries for same route              │
│  • Use smallest suitable vehicle                │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## Example Workflow

### Real-World Example: E-Commerce Delivery

**Company**: Online Shop
**Daily Orders**: 50-100 deliveries
**Fleet**: 3 small vans, 2 medium trucks

#### Morning Routine (8:00 AM)

1. **Review new orders**
   - Go to Delivery Orders
   - Filter: Ready to Assign

2. **Group by location** (manual)
   - North area: 15 orders
   - South area: 20 orders
   - East area: 10 orders

3. **Assign vehicles**
   - Select North orders → Assign Carrier
     - Result: Medium Truck (85% utilization)
   - Select South orders → Assign Carrier
     - Result: Medium Truck (92% utilization)
   - Select East orders → Assign Carrier
     - Result: Small Van (78% utilization)

4. **Review assignments**
   - Go to Vehicle Assignments
   - Group by Vehicle
   - Print delivery sheets

5. **Dispatch**
   - Drivers collect delivery sheets
   - Load vehicles according to assignments

#### End of Day (6:00 PM)

1. **Review metrics**
   - Total deliveries: 45
   - Vehicles used: 3 (instead of 6)
   - Average utilization: 85%
   - **Savings**: 50% fewer trips

---

## Best Practices Summary

✓ **Always** set product weights before creating deliveries
✓ **Always** configure vehicle capacities before assigning
✓ **Group** deliveries by route/area for batch assignment
✓ **Monitor** utilization to ensure efficiency
✓ **Review** assignment history regularly
✓ **Update** vehicle capacities as fleet changes

---

**Ready to optimize your deliveries? Start assigning!**

For detailed information, see [README.md](README.md)
