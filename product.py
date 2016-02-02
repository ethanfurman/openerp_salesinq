from collections import defaultdict
from fnx import xid
from fnx.oe import dynamic_page_stub, static_page_stub
from osv import osv, fields
from urllib import urlopen

from salesinq import get_user_reps
from _links import product_links, product_modules

def salesinq(obj, cr, uid, ids, fields, arg, context=None):
    # check group permissions for user
    allow_external_si, si_rep_text = get_user_reps(obj, cr, uid, context)
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
            arg=product_modules,
            context=context)
    result = defaultdict(dict)
    for product_id in ids:
        result[product_id]['xml_id'] = xml_ids[product_id]['xml_id']
        si_codes = xml_ids[product_id]
        si_code = (si_codes['xml_id'] or '').replace("'","%%27")
        valid_si_code = is_valid(si_code)
        result[product_id]['is_salesinq_able'] = valid_si_code
        for fld in fields:
            if not valid_si_code:
                result[product_id][fld] = ''
                continue
            htmlContentList = []
            if len(product_links) > 1:
                for shortname, longname, SalesInqURL in product_links:
                    if SalesInqURL.count('%s') == 0:
                        if allow_external_si:
                            htmlContentList.append('''<a href="%s?rep_op=%s" target="_blank">&bullet;%s&bullet;&nbsp;</a>''' % (SalesInqURL, si_rep_text, longname))
                        continue
                    if shortname == 'salesinq_allyears_rep':
                        htmlContentList.append('<br>')
                    htmlContentList.append('''<a href="javascript:ajaxpage('%s','salesinqcontent');">&bullet;%s&bullet;&nbsp;</a>''' % (SalesInqURL % si_code, longname))
            htmlContentList.append('''
                    <div id="salesinqcontent"></div>
                    <script type="text/javascript">
                    ajaxpage('%s','salesinqcontent');
                    </script>''' % (product_links[0][2] % si_code) )
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
        'salesinq_data': fields.function(
            salesinq,
            multi='salesinq',
            string='SalesInq All Years & Months',
            type='html',
            method=False,
            ),
        }
product_product()
