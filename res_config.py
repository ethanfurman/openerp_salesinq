from openerp.osv import fields, osv

class salesinq_config_settings(osv.TransientModel):
    _name = 'salesinq.config.settings'
    _inherit = "res.config.settings"
    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'salesinq_url': fields.related(
            'company_id', 'salesinq_url',
            type='char',
            string='SalesInq Server',
            ),
        'product_link_ids': fields.related(
            'company_id', 'product_link_ids',
            type='one2many',
            relation='salesinq.config.product_link',
            fields_id='company_id',
            string='Product Link',
            ),
        'partner_link_ids': fields.related(
            'company_id', 'partner_link_ids',
            type='one2many',
            relation='salesinq.config.partner_link',
            fields_id='company_id',
            string='Partner Link',
            ),
        }

    def create(self, cr, uid, values, context=None):
        id = super(salesinq_config_settings, self).create(cr, uid, values, context)
        # Hack: to avoid some nasty bug, related fields are not written upon record creation.
        # Hence we write on those fields here.
        vals = {}
        for fname, field in self._columns.iteritems():
            if isinstance(field, fields.related) and fname in values:
                vals[fname] = values[fname]
        self.write(cr, uid, [id], vals, context)
        return id

    def _default_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.company_id.id

    _defaults = {
        'company_id': _default_company,
        }

    def onchange_company_id(self, cr, uid, ids, company_id, context=None):
        # update related fields
        values = {}
        if company_id:
            company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
            values = {
                'salesinq_url': company.salesinq_url,
                'product_link_ids': [r.id for r in company.product_link_ids],
                'partner_link_ids': [r.id for r in company.partner_link_ids],
                }
        return {'value': values}


