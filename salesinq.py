from collections import defaultdict
# from fnx import xid, dynamic_page_stub, static_page_stub
from osv import osv, fields
from urllib import urlopen

# from _links import product_links, product_modules


class salesinq_webpage(osv.Model):
    'stores the web page from the SalesInq engine'
    _name = 'salesinq.webpage'
    _rec_name = 'id'
    # _mirrors = {'user_id': ['name']

    def query_salesinq(cr, uid, *args):
        pass

    def _convert_page(self, cr, uid, ids, field_name, arg, context=None):
        pass

    _columns = {
        'user_id': fields.many2one('res.users', 'User Name'),
        # 'web_page': fields.text('Web Page', required=True),
        'rep_ids': fields.many2many('salesinq.rep', string='Allowed Reps'),
        }


class salesinq_rep(osv.Model):
    'stores the currently available reps'
    _name = 'salesinq.rep'
    _rec_name = 'code'

    _columns = {
        'code': fields.char('Rep code', size=10, required=True),
        }

