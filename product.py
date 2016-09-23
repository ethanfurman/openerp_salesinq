from collections import defaultdict
from fnx.oe import dynamic_page_stub
from osv import osv, fields

from salesinq import allow_custom_access
from _links import product_links

def salesinq(obj, cr, uid, ids, fields, arg, context=None):
    # check group permissions for user
    custom_access = allow_custom_access(obj, cr, uid, context)
    fields = fields[:]
    result = defaultdict(dict)
    for product in obj.read(cr, uid, ids, fields=['xml_id'], context=context):
        si_code = (product['xml_id'] or '').replace("'","%%27")
        valid_si_code = is_valid(si_code)
        result[product['id']]['is_salesinq_able'] = valid_si_code
        if not valid_si_code:
            result[product['id']]['salesinq_data'] = ''
            continue
        htmlContentList = []
        if len(product_links) > 1:
            for shortname, longname, SalesInqURL in product_links:
                if SalesInqURL.count('%s') == 0:
                    if custom_access:
                        htmlContentList.append('''<a href="salesinq/%s?oe_db=%s&oe_uid=%s" target="_blank">&bullet;%s&bullet;&nbsp;</a>'''
                                % (SalesInqURL, cr.dbname, uid, longname)
                                )
                    continue
                if shortname == 'salesinq_allyears_rep':
                    htmlContentList.append('<br>')
                htmlContentList.append('''<a href="javascript:ajaxpage('salesinq/%s&oe_db=%s&oe_uid=%s','salesinqcontent');">&bullet;%s&bullet;&nbsp;</a>'''
                        % (SalesInqURL % si_code, cr.dbname, uid, longname)
                        )
        htmlContentList.append('''
                <div id="salesinqcontent"></div>
                <script type="text/javascript">
                ajaxpage('salesinq/%s&oe_db=%s&oe_uid=%s','salesinqcontent');
                </script>''' % (product_links[0][2] % si_code, cr.dbname, uid) )
        result[product['id']]['salesinq_data'] = dynamic_page_stub % "".join(htmlContentList)
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
