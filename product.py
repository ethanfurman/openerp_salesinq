from collections import defaultdict
from fnx.oe import dynamic_page_stub
from osv import osv, fields

from . import allow_custom_access

def salesinq(obj, cr, uid, ids, fields, arg, context=None):
    user = obj.pool.get('res.users').browse(cr, uid, uid, context=None)
    # check group permissions for user
    custom_access = allow_custom_access(obj, cr, uid, context)
    fields = fields[:]
    result = defaultdict(dict)
    # get default for user if one exists
    first_link = user.salesinq_product_view or None
    first_link_id = 0
    if first_link:
        first_link_id = int(first_link.split('-', 1)[0])
    for product in obj.read(cr, uid, ids, fields=['xml_id'], context=context):
        si_code = (product['xml_id'] or '').replace("'","%%27")
        valid_si_code = is_valid(si_code)
        result[product['id']]['is_salesinq_able'] = valid_si_code
        if not valid_si_code or not user.company_id.product_link_ids:
            result[product['id']]['salesinq_data'] = '<html><body><br/><h2>No links defined.</h2></body></html>'
            continue
        htmlContentList = ['<div id="centeredmenutop"><ul>']
        initial = link = None
        active_list = []
        link_records = user.company_id.product_link_ids
        if user.has_group('fis_integration.purchase_cost'):
            link_records.extend(user.company_id.product_cost_link_ids)
        # for i, link_record in enumerate(user.company_id.product_link_ids + user.company_id.product_cost_link_ids):
        for i, link_record in enumerate(link_records):
            longname, SalesInqURL = link_record.name, link_record.query
            if not SalesInqURL:
                # skip any blank entries
                continue
            if i and i % 3 == 0:
                htmlContentList.append('<li style="">&bullet;</li>'.join(active_list))
                htmlContentList.append('</ul></div><div id="centeredmenubottom"><ul>')
                active_list = []
            settings = dict(
                    url=SalesInqURL.format(product_code=si_code),
                    db=cr.dbname,
                    uid=uid,
                    )
            if longname == 'Custom':
                if custom_access:
                    active_list.append(
                        ('<li><a href="salesinq/custom?oe_db={db}&oe_uid={uid}"'
                        ' target="_blank">Custom</a></li>').format(**settings)
                        )
                continue
            link = 'salesinq/standard?{url}&oe_db={db}&oe_uid={uid}'.format(**settings)
            if len(user.company_id.product_link_ids) > 1:
                active_list.append('''<li><a href="javascript:ajaxpage('%s','salesinqcontent')">%s</a></li>'''
                    % (link, longname)
                    )
            if initial is None:
                # capture the first possible link, just in case
                initial = link
            if first_link_id and link_record.id == first_link_id:
                # reset initial to user selected link
                initial = link
        htmlContentList.append('<li style="">&bullet;</li>'.join(active_list))
        htmlContentList.append('</ul></div>')
        htmlContentList.append('''
                <div id="salesinqcontent"></div>
                <script type="text/javascript">
                ajaxpage('%s','salesinqcontent');
                </script>''' % (initial, ) )
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
