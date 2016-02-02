from collections import defaultdict
from osv import osv, fields
from scription import OrmFile
from urllib2 import HTTPPasswordMgr, HTTPBasicAuthHandler, build_opener
from zlib import crc32
import re

salesinq = 'http://openerp.sunridgefarms.com/SalesInq'
settings = OrmFile('/etc/openerp/fnx.ini', section='openerp')
auth_handler = HTTPBasicAuthHandler()
auth_handler.add_password(realm='Zope', user=settings.user, passwd=settings.pw, uri=salesinq)
webpage = build_opener(auth_handler)
del settings
del auth_handler

def get_user_reps(obj, cr, uid, context=None):
    user = obj.pool.get('res.users').browse(cr, uid, uid)
    allow_external_si = user.has_group('salesinq.user')
    si_rep_text = ''
    if allow_external_si:
        si_webpage = obj.pool.get('salesinq.webpage')
        webpage_rec = si_webpage.browse(cr, uid, [('user_id','=',uid)])
        if not webpage_rec:
            allow_external_si = False
        else:
            [webpage_rec] = webpage_rec
            reps = []
            for rep in webpage_rec.rep_ids:
                reps.append(rep.code)
            si_rep_text = ','.join(reps)
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

    def query_salesinq(self, cr, uid, *args):
        si = webpage.open(salesinq)
        si_page = si.read()
        start = si_page.index('<select id="Rep_op"')
        end = si_page.index('</select>', start)
        section = si_page[start:end]
        reps = []
        for line in section.split('\n'):
            match = re.search('value="([^"]*)"', line)
            if match and match.groups()[0] not in (' All ', ''):
                reps.append(match.groups()[0])
        si_reps = self.pool.get('salesinq.rep')
        existing_reps = [rep.code for rep in si_reps.browse(cr, uid)]
        for rep in reps:
            if rep not in existing_reps:
                si_reps.create(cr, uid, {'code':rep})
        return True

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

