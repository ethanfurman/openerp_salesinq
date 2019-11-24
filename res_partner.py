from collections import defaultdict
from fnx.oe import dynamic_page_stub
from openerp.tools import self_ids
from osv import osv, fields
from salesinq import allow_custom_access


def salesinq(obj, cr, uid, ids, fields, arg, context=None):
    user = obj.pool.get('res.users').browse(cr, uid, uid, context=None)
    # check group permissions for user
    custom_access = allow_custom_access(obj, cr, uid, context)
    fields = fields[:]
    # get default for user if one exists
    first_link = user.salesinq_partner_view or None
    first_link_id = 0
    if first_link:
        first_link_id = int(first_link.split('-', 1)[0])
    # partner_id is the key, value is partner.parent_id or None
    chain = {}
    partners = dict([(r.id, r) for r in obj.browse(cr, uid, ids, context=context)])
    for partner_id, partner in partners.items():
        chain[partner_id] = None
        if partner.parent_id:
            chain[partner_id] = partner.parent_id
    result = defaultdict(dict)
    for partner_id, parent_id in chain.items():
        partner = partners[partner_id]
        si_code = (partner.xml_id or '').replace("'","%27")
        valid_si_code = is_valid(si_code)
        result[partner.id]['is_salesinq_able'] = valid_si_code
        if parent_id is not None and not valid_si_code:
            partner = partners[partner_id]
            si_code = (partner.xml_id or '').replace("'","%27")
            valid_si_code = partner.is_salesinq_able
        if not valid_si_code or not user.company_id.partner_link_ids:
            result[partner_id]['salesinq_data'] = '<html><body><br/><h2>No links defined.</h2></body></html>'
            continue
        htmlContentList = ['<div id="centeredmenutop"><ul>']
        initial = link = None
        midpoint = len(user.company_id.partner_link_ids)//2
        if midpoint < 3:
            midpoint = 0
        active_list = []
        for i, link_record in enumerate(user.company_id.partner_link_ids):
            longname, SalesInqURL = link_record.name, link_record.query
            if midpoint and midpoint == i:
                htmlContentList.append('<li style="">&bullet;</li>'.join(active_list))
                htmlContentList.append('</ul></div><div id="centeredmenubottom"><ul>')
                active_list = []
            if partner.customer:
                settings = dict(
                        cust_or_item='Cust',
                        cust_or_supplier='Cust',
                        )
            else: # .supplier:
                settings = dict(
                        cust_or_item='Item',
                        cust_or_supplier='Supplier',
                        )
            settings['partner_code'] = si_code
            settings['db'] = cr.dbname
            settings['uid'] = uid
            if longname == 'Custom':
                if custom_access:
                    active_list.append(
                        ('<li><a href="salesinq/custom?oe_db={db}&oe_uid={uid}"'
                        ' target="_blank">Custom</a></li>').format(**settings)
                        )
            else:
                link = ('salesinq/standard?' + SalesInqURL + '&oe_db={db}&oe_uid={uid}').format(**settings)
                if len(user.company_id.partner_link_ids) > 1:
                    active_list.append('''<li><a href="javascript:ajaxpage('%s','salesinqcontent');">%s&nbsp;</a></li>'''
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
        result[partner_id]['salesinq_data'] = dynamic_page_stub % "".join(htmlContentList)
    return result

def is_valid(id):
    """
    uses simple hueristics to guess if id is a valid salesinq code
    """
    return bool(id)

class res_partner(osv.Model):
    "Inherits partner and makes the external_id visible and modifiable"
    _name = 'res.partner'
    _inherit = 'res.partner'

    _columns = {
        'is_salesinq_able': fields.function(
            salesinq,
            multi='salesinq',
            string='SalesInq-able',
            type='boolean',
            method=False,
            store={
                'res.partner': (self_ids, ['xml_id'], 10),
                },
            ),
        'salesinq_data': fields.function(
            salesinq,
            multi='salesinq',
            string='Years and Months',
            type='html',
            method=False,
            ),
        }
res_partner()
