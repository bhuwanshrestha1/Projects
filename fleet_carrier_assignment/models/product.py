from odoo import fields,api,models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_storable=fields.Boolean( default=True)