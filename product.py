from collections import defaultdict
from fnx import xid, dynamic_page_stub, static_page_stub
from osv import osv, fields
from urllib import urlopen

salesinq_links = [
    ('salesinq_allyrsmos','Years&nbsp;&&nbsp;Months',
        "pyvotRpt?ck_qty=on&optX_op=Item&Item_op=%s&rptColFmt_op=allyrsmos"),
    ('salesinq_allyrsmos_rep','Years&nbsp;&&nbsp;Months&nbsp;by&nbsp;Rep',
        "pyvotRpt?ck_qty=on&Item_op=%s&rptColFmt_op=allyrsmos&optX_op=Rep"),
    ('salesinq_allyrsmos_shipto','Years&nbsp;&&nbsp;Months&nbsp;by&nbsp;ShipTo',
        "pyvotRpt?ck_qty=on&Item_op=%s&rptColFmt_op=allyrsmos&optX_op=ShipTo"),
    ('salesinq_allyears_rep','Years&nbsp;by&nbsp;Rep',
        "pyvotRpt?ck_descs=on&ck_qty=on&Item_op=%s&rptColFmt_op=allyears&optX_op=Rep"),
    ('salesinq_allyrs_shipto','Years&nbsp;by&nbsp;ShipTo',
        "pyvotRpt?ck_descs=on&ck_qty=on&Item_op=%s&rptColFmt_op=allyears&optX_op=ShipTo"),
    ('salesinq_allyrs_repcust','Years&nbsp;by&nbsp;Rep/Customer',
        "pyvotRpt?ck_descs=on&ck_qty=on&Item_op=%s&rptColFmt_op=allyears&optX_op=Rep&optY_op=Cust"),
    ('salesinq_allyrs_statecity','Years&nbsp;by&nbsp;State/City',
        "pyvotRpt?ck_descs=on&ck_qty=on&Item_op=%s&rptColFmt_op=allyears&optX_op=State&optY_op=City"),
    ('salesinq_allyrs_citycust','Years&nbsp;by&nbsp;City/Customer',
        "pyvotRpt?ck_descs=on&ck_qty=on&Item_op=%s&rptColFmt_op=allyears&optX_op=City&optY_op=Cust"),
    ]


def salesinq(obj, cr, uid, ids, fields, arg, context=None):
    fields = fields[:]
    # remove known fields
    if 'xml_id' in fields:
        fields.remove('xml_id')
    if 'is_salesinq_able' in fields:
        fields.remove('is_salesinq_able')
    if 'module' in fields:
        fields.remove('module')
    xml_ids = xid.get_xml_ids(
            obj, cr, uid, ids, None,
            arg=('F135', ),
            context=context)
    result = defaultdict(dict)
    for product_id in ids:
        result[product_id]['xml_id'] = xml_ids[product_id]['xml_id']
        si_codes = xml_ids[product_id]
        si_code = si_codes['xml_id'].replace("'","%%27")
        valid_si_code = is_valid(si_code)
        result[product_id]['is_salesinq_able'] = valid_si_code
        for fld in fields:
            if not valid_si_code:
                result[product_id][fld] = ''
                continue
            #result[product_id][fld] = 'fake html'   # TODO remove for live install!!
            #continue                                # this line too!
            htmlContentList = [ ]
            for shortname, longname, SalesInqURL in salesinq_links:
                if shortname == 'salesinq_allyears_rep':
                    htmlContentList.append('<br>')
                htmlContentList.append('''<a href="javascript:ajaxpage('%s','salesinqcontent');">&bullet;%s&bullet;&nbsp;</a>''' % (SalesInqURL % si_code, longname))
            #for ii in htmlContentList: print ii
            htmlContentList.append('''
                    <div id="salesinqcontent"></div>
                    <script type="text/javascript">
                    ajaxpage('%s','salesinqcontent');
                    </script>''' % (salesinq_links[0][2] % si_code) )
            result[product_id][fld] = dynamic_page_stub % "".join(htmlContentList)
    return result

def is_valid(id):
    """
    uses simple hueristics to guess if id is a valid salesinq code
    """
    return bool(id)


class product_product(osv.Model):
    'Adds Available column and makes external_id visible and searchable'
    _name = 'product.product'
    _inherit = 'product.product'

    _columns = {
        'is_salesinq_able': fields.function(
            salesinq,
            multi='salesinq',
            string='SalesInq-able',
            type='boolean',
            method=False,
            ),
        #'salesinq_allyrs_shipto': fields.function(
        #    _salesinq,
        #    string='SalesInq All Years by Ship To',
        #    type='html',
        #    method=False,
        #    ),
        #'salesinq_allyrs_statecity': fields.function(
        #    _salesinq,
        #    string='SalesInq All Years by State/City',
        #    type='html',
        #    method=False,
        #    ),
        #'salesinq_allyrs_citycust': fields.function(
        #    _salesinq,
        #    string='SalesInq All Years by City/Customer',
        #    type='html',
        #    method=False,
        #    ),
        #'salesinq_allyrs_repcust': fields.function(
        #    _salesinq,
        #    string='SalesInq All Years by Rep/Customer',
        #    type='html',
        #    method=False,
        #    ),
        'salesinq_allyrsmos': fields.function(
            salesinq,
            multi='salesinq',
            string='SalesInq All Years & Months',
            type='html',
            method=False,
            ),
        #'salesinq_allyrsmos_shipto': fields.function(
        #    _salesinq,
        #    string='SalesInq All Years & Months by Ship To',
        #    type='html',
        #    method=False,
        #    ),
        }
product_product()
