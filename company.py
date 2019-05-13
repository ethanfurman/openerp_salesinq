from openerp.osv import fields, osv

class res_company(osv.Model):
    _inherit = "res.company"
    _columns = {
        'salesinq_url': fields.char('SalesInq Server', size=128),
        'product_link_ids': fields.one2many('salesinq.config.product_link', 'company_id', 'Product Link'),
        'partner_link_ids': fields.one2many('salesinq.config.partner_link', 'company_id', 'Partner Link'),
        }


def unique(model, cr, uid, ids):
    data = model.read(cr, uid, fields=['name', 'query'])
    name_pool = set()
    query_pool = set()
    for datum in data:
        name, query = datum['name'], datum['query']
        if name in name_pool:
            return False
        name_pool.add(name)
        if query in query_pool:
            return False
        query_pool.add(query)
    return True


class salesinq_product_link(osv.Model):
    _name = 'salesinq.config.product_link'
    _columns = {
        'company_id': fields.many2one('res.company', 'Company'),
        'name': fields.char('Link Text', size=64),
        'query': fields.char('Link Query', size=255),
        }
    _constraints = [(unique, 'name or query already in use', ['name', 'query'])]


class salesinq_partner_link(osv.Model):
    _name = 'salesinq.config.partner_link'
    _columns = {
        'company_id': fields.many2one('res.company', 'Company'),
        'name': fields.char('Link Text', size=64),
        'query': fields.char('Link Query', size=255),
        }
    _constraints = [(unique, 'name or query already in use', ['name', 'query'])]

