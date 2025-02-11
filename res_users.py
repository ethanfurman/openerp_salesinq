from openerp import SUPERUSER_ID
from openerp.osv import osv, fields
from VSS.utils import translator

class res_users(osv.Model):
    _name = 'res.users'
    _inherit = 'res.users'

    def _salesinq_get_product_view_links(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid, context=context)
        settings = self.pool.get('salesinq.config.product_link')
        ids = settings.search(cr, SUPERUSER_ID, [('company_id','=',user.company_id.id)], context=context)
        res = settings.read(cr, SUPERUSER_ID, ids, ['id', 'name', ], context=context)
        return [
                ('%02d-%s' % (r['id'], compress(r['name'])), r['name'])
                for r in res
                ]

    def _salesinq_get_product_cost_view_links(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid, context=context)
        if not user.has_group('fis_integration.purchase_cost'):
            return []
        settings = self.pool.get('salesinq.config.product_cost_link')
        ids = settings.search(cr, SUPERUSER_ID, [('company_id','=',user.company_id.id)], context=context)
        res = settings.read(cr, SUPERUSER_ID, ids, ['id', 'name', ], context=context)
        return [
                ('%02d-%s' % (r['id'], compress(r['name'])), r['name'])
                for r in res
                ]

    def _salesinq_get_partner_view_links(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid, context=context)
        settings = self.pool.get('salesinq.config.partner_link')
        ids = settings.search(cr, SUPERUSER_ID, [('company_id','=',user.company_id.id)], context=context)
        res = settings.read(cr, SUPERUSER_ID, ids, ['id', 'name', ], context=context)
        return [
                ('%02d-%s' % (r['id'], compress(r['name'])), r['name'])
                for r in res
                ]

    def _has_salesinq(self, cr, uid, ids, field, arg, context=None):
        res = {}
        imd = self.pool.get('ir.model.data')
        salesinq_group = set([
                r['res_id']
                for r in imd.read(
                    cr,
                    SUPERUSER_ID,
                    [('module','=','salesinq'),('model','=','res.groups')],
                    fields=['id', 'res_id'],
                    )])
        for r in self.read(cr, SUPERUSER_ID, ids, fields=['id', 'name', 'groups_id'], context=context):
            res[r['id']] = bool(set(r['groups_id']) & salesinq_group)
        return res

    #XXX: doesn't reset if user's company is changed

    _columns = {
            'salesinq_product_view': fields.selection(
                string='Default Product View',
                selection=_salesinq_get_product_view_links,
                ),
            'salesinq_product_cost_view': fields.selection(
                string='Default Product Cost View',
                selection=_salesinq_get_product_cost_view_links,
                ),
            'salesinq_partner_view': fields.selection(
                string='Default Partner View',
                selection=_salesinq_get_partner_view_links,
                ),
            'salesinq_privileges': fields.function(
                _has_salesinq,
                string='Salesinq',
                type='boolean',
                ),
            }

alphanum = translator(
        to=' ',
        keep='01234567890 abcdefghijklmnopqrstuvwxyz',
        )
def compress(text):
    return '_'.join(alphanum(text.lower()).split())
