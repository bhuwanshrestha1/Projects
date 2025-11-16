# -*- coding: utf-8 -*-
{
    'name': 'Fleet Carrier Assignment',
    'version': '19.0.0.1',
    'sequence': "-1",
    'category': 'Inventory/Delivery',
    'summary': 'Automatically assign vehicles to delivery orders based on weight capacity',
    'description': """
        Fleet Carrier Assignment
        =========================
        * Automatically assign vehicles to delivery orders
        * Based on product weight and vehicle capacity
        * Optimal vehicle selection (best-fit algorithm)
        * Support for weight and volume constraints
    """,
    'author': 'Innovax Solutions',
    'website': '',
    'depends': [
        'stock','fleet','sale','delivery','mail'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_picking_views.xml',
        'views/assign_carrier_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}