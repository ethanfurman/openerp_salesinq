from openerp.osv import fields, osv

class res_company(osv.Model):
    _inherit = "res.company"
    _columns = {
            'salesinq_url': fields.char('SalesInq Server', size=128),
            }
