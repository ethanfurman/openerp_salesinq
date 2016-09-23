from collections import defaultdict
from fnx.oe import dynamic_page_stub
from osv import osv, fields

from salesinq import allow_custom_access
from _links import partner_links


def salesinq(obj, cr, uid, ids, fields, arg, context=None):
    # check group permissions for user
    custom_access = allow_custom_access(obj, cr, uid, context)
    fields = fields[:]
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
        if parent_id is not None and not valid_si_code:
            partner = partners[partner_id]
            si_code = (partner.xml_id or '').replace("'","%27")
            valid_si_code = is_valid(si_code)
        result[partner_id]['is_salesinq_able'] = valid_si_code
        if not valid_si_code:
            result[partner_id]['salesinq_data'] = ''
            continue
        htmlContentList = []
        for shortname, longname, SalesInqURL in partner_links:
            if shortname == 'salesinq_yrs':
                htmlContentList.append('<br>')
            if partner.customer:
                si_fields = 'Cust','Cust'
            else: # .supplier:
                si_fields = 'Item', 'Supplier'
            subs = SalesInqURL.count('%s')
            if subs == 0:
                if custom_access:
                    htmlContentList.append('''<a href="salesinq/%s?oe_db=%s&oe_uid=%s" target="_blank">&bullet;%s&bullet;&nbsp;</a>'''
                            % (SalesInqURL, cr.dbname, uid, longname)
                            )
            else:
                if subs == 3:
                    codes = si_fields + (si_code,)
                else:
                    codes = si_fields[1:] + (si_code,)
                htmlContentList.append('''<a href="javascript:ajaxpage('salesinq/%s&oe_db=%s&oe_uid=%s','salesinqcontent');">&bullet;%s&bullet;&nbsp;</a>'''
                        % (SalesInqURL % codes, cr.dbname, uid, longname)
                        )
        htmlContentList.append('''
                <div id="salesinqcontent"></div>
                <script type="text/javascript">
                ajaxpage('salesinq/%s&oe_db=%s&oe_uid=%s','salesinqcontent');
                </script>''' % (partner_links[0][2] % (si_fields[0], si_fields[1], si_code), cr.dbname, uid) )
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
            multi='custom',
            string='SalesInq-able',
            type='boolean',
            method=False,
            ),
        'salesinq_data': fields.function(
            salesinq,
            multi='custom',
            string='Years and Months',
            type='html',
            method=False,
            ),
        }
res_partner()
