# -*- coding: utf-8 -*-

# imports
import openerp
from openerp import SUPERUSER_ID
from openerp.addons.web import http
import io
import logging
import lxml.html as lh
import lxml.html.builder as E
import re
import requests
import zlib

_logger = logging.getLogger(__name__)

# work horses
class SalesInqProxy(http.Controller):

    _cp_path = '/salesinq'

    @http.httprequest
    def standard(self, request, **kwds):
        db = kwds.pop('oe_db')
        uid = int(kwds.pop('oe_uid'))
        # clean up kwds (some wierd key that's all digits with no value is coming through)
        pyvot_kwds = dict([(k, v) for k, v in kwds.items() if v])
        registry = openerp.modules.registry.RegistryManager.get(db)
        with registry.cursor() as cr:
            base_url = registry.get('res.users').browse(cr, SUPERUSER_ID, uid).company_id.salesinq_url
        web_data = requests.get('http://%s/pyvotRpt' % base_url, params=pyvot_kwds)
        page = re.sub(r'<(a|/a).*?>', '', web_data.text, flags=re.I)
        return request.make_response(
                page,
                headers=[
                    ('Content-Type', web_data.headers['Content-Type']),
                    ('Content-Length', len(page)),
                    ],
                )

    @http.httprequest
    def pyvotRpt(self, request, **kwds):
        db = kwds.pop('oe_db')
        uid = int(kwds.pop('oe_uid'))
        # clean up kwds (some wierd key that's all digits with no value is coming through)
        pyvot_kwds = dict([(k, v) for k, v in kwds.items() if v])
        registry = openerp.modules.registry.RegistryManager.get(db)
        with registry.cursor() as cr:
            base_url = registry.get('res.users').browse(cr, SUPERUSER_ID, uid).company_id.salesinq_url
        web_data = requests.get('http://%s/pyvotRpt' % base_url, params=pyvot_kwds)
        page = re.sub(r'<(a|/a).*?>', '', web_data.text, flags=re.I)
        return request.make_response(
                page,
                headers=[
                    ('Content-Type', web_data.headers['Content-Type']),
                    ('Content-Length', len(page)),
                    ],
                )

    @http.httprequest
    def custom(self, request, **kwds):
        db = kwds.pop('oe_db')
        uid = int(kwds.pop('oe_uid'))
        # clean up kwds (some wierd key that's all digits with no value is coming through)
        pyvot_kwds = dict([(k, v) for k, v in kwds.items() if v])
        registry = openerp.modules.registry.RegistryManager.get(db)
        with registry.cursor() as cr:
            allowed_reps = self.get_user_reps(registry, cr, uid)
            allowed_rep_text = '[' + ','.join(allowed_reps) + ']'
            pyvot_kwds['rep_op'] = allowed_rep_text
            user = registry.get('res.users').browse(cr, SUPERUSER_ID, uid)
            base_url = user.company_id.salesinq_url
            base_url = registry.get('res.users').browse(cr, SUPERUSER_ID, uid).company_id.salesinq_url
        url = 'http://%s/salesinq' % base_url
        web_data = requests.get(url, params=pyvot_kwds)
        doc = lh.parse(io.StringIO(web_data.text))
        [main_form] = doc.xpath('//form[@id="pyvotOps"]')
        main_form.append(E.INPUT(name='oe_db', value=db, type='hidden'))
        main_form.append(E.INPUT(name='oe_uid', value=str(uid), type='hidden'))
        page = lh.tostring(doc)
        return request.make_response(
                page,
                headers=[
                    ('Content-Type', web_data.headers['Content-Type']),
                    ('Content-Length', len(page)),
                    ],
                )

    def get_keywords(self, kwds):
        db = kwds.pop('oe_db')
        uid = int(kwds.pop('oe_uid'))
        # clean up kwds (some wierd key that's all digits with no value is coming through)
        kwds = dict([(k, v) for k, v in kwds.items() if v])
        registry = openerp.modules.registry.RegistryManager.get(db)
        with registry.cursor() as cr:
            base_url = registry.get('res.users').browse(cr, SUPERUSER_ID, uid).company_id.salesinq_url
        return base_url, kwds

    def get_user_reps(self, registry, cr, uid):
        si_webpage = registry.get('salesinq.webpage')
        webpage_rec = si_webpage.browse(cr, SUPERUSER_ID, [('user_id','=',uid)])[0]
        reps = []
        for rep in webpage_rec.rep_ids:
            reps.append(rep.code)
        si_rep_text = ','.join(reps)
        crc = '%08X' % (zlib.crc32(str(si_rep_text)) & 0xffffffff,)
        xlate = dict(zip("0123456789ABCDEF","ABCDEFGHIJKLMNOP"))
        crc = ''.join([xlate[c] for c in crc[-3:]])
        reps.append(crc)
        return reps


# pyvotRpt?ck_qty=on&optX_op=Item&Item_op=000113&rptColFmt_op=allyrsmos
# javascript:ajaxpage('salesinq/test_sunridgefarms/pyvotRpt?optX_op=Cust&Cust_op=479PO&rptColFmt_op=allyrsmos','salesinqcontent');
