# -*- coding: utf-8 -*-

# imports
import openerp
from openerp import SUPERUSER_ID
from openerp.addons.web import http
import logging
import requests

_logger = logging.getLogger(__name__)

# work horses
class SalesInqProxy(http.Controller):

    _cp_path = '/salesinq'

    def __getattr__(self, name):
        return self.get_web_page

    @http.httprequest
    def get_web_page(self, request, **kwds):
        company, salesinq_command = request.httprequest.path[10:].split('/', 1)
        # clean up kwds (some wierd key that's all digits with no value is coming through)
        kwds = [(k, v) for k, v in kwds.items() if v]
        registry = openerp.modules.registry.RegistryManager.get(company)
        with registry.cursor() as cr:
            base_url = registry.get('res.company').browse(cr, SUPERUSER_ID, 1).salesinq_url
            web_data = requests.get('http://%s/%s' % (base_url, salesinq_command), params=kwds)
            return request.make_response(
                    web_data.text,
                    headers=[
                        ('Content-Type', web_data.headers['Content-Type']),
                        ('Content-Length', len(web_data.text)),
                        ],
                    )

# pyvotRpt?ck_qty=on&optX_op=Item&Item_op=000113&rptColFmt_op=allyrsmos
# javascript:ajaxpage('salesinq/test_sunridgefarms/pyvotRpt?optX_op=Cust&Cust_op=479PO&rptColFmt_op=allyrsmos','salesinqcontent');
