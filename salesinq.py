from collections import defaultdict
# from fnx import xid, dynamic_page_stub, static_page_stub
from osv import osv, fields
from urllib import urlopen
from zlib import crc32

# from _links import product_links, product_modules

def get_user_reps(obj, cr, uid, context=None):
    user = obj.pool.get('res.users').browse(cr, uid, uid)
    allow_external_si = user.has_group('salesinq.user')
    si_rep_text = ''
    print user.name, 'is', ('not allowed', 'allowed')[allow_external_si]
    if allow_external_si:
        si_webpage = obj.pool.get('salesinq.webpage')
        webpage_rec = si_webpage.browse(cr, uid, [('user_id','=',uid)])
        if not webpage_rec:
            allow_external_si = False
            print 'no webpage record, cancelling'
        else:
            [webpage_rec] = webpage_rec
            reps = []
            for rep in webpage_rec.rep_ids:
                reps.append(rep.code)
            si_rep_text = str(reps)
            crc = '%08X' % (crc32(str(si_rep_text)) & 0xffffffff,)
            xlate = dict(zip("0123456789ABCDEF","ABCDEFGHIJKLMNOP"))
            crc = ''.join([xlate[c] for c in crc[-3:]])
            reps.append(crc)
            si_rep_text = '[' + ','.join(reps) + ']'
    return allow_external_si, si_rep_text

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

