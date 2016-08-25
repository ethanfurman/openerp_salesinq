from collections import defaultdict
from fnx import xid
from fnx.oe import dynamic_page_stub
from osv import osv, fields

from salesinq import get_user_reps
from _links import partner_links, partner_modules


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
    # both partner and partner.parent ids
    all_ids = []
    # partner_id is the key, value is partner.parent_id or None
    chain = {}
    for partner in obj.browse(cr, uid, ids, context=context):
        all_ids.append(partner.id)
        chain[partner.id] = None
        if partner.parent_id:
            all_ids.append(partner.parent_id)
            chain[partner.id] = partner.parent_id
    xml_ids = xid.get_xml_ids(
            obj, cr, uid, all_ids, None,
            arg=partner_modules,
            context=context)
    result = defaultdict(dict)
    dbname = cr.dbname
    for partner_id, parent_id in chain.items():
        result[partner_id]['xml_id'] = xml_ids[partner_id]['xml_id']
        si_codes = xml_ids[partner_id]
        si_code = (si_codes['xml_id'] or '').replace("'","%27")
        valid_si_code = is_valid(si_code)
        partner = obj.browse(cr, uid, [partner_id], context=context)[0]
        if parent_id is not None and not valid_si_code:
            si_codes = xml_ids[parent_id]
            si_code = (si_codes['xml_id'] or '').replace("'","%27")
            valid_si_code = is_valid(si_code)
            partner = obj.browse(cr, uid, [parent_id.id], context=context)[0]
        result[partner_id]['is_salesinq_able'] = valid_si_code
        for fld in fields:
            if not valid_si_code:
                result[partner_id][fld] = ''
                continue
            htmlContentList = [ ]
            for shortname, longname, SalesInqURL in partner_links:
                if shortname == 'salesinq_yrs':
                    htmlContentList.append('<br>')
                if partner.customer:
                    si_fields = 'Cust','Cust'
                else: # .supplier:
                    si_fields = 'Item', 'Supplier'
                subs = SalesInqURL.count('%s')
                if subs == 0:
                    if allow_external_si:
                        htmlContentList.append('''<a href="salesinq/%s/%s?rep_op=%s" target="_blank">&bullet;%s&bullet;&nbsp;</a>'''
                                % (dbname, SalesInqURL, si_rep_text, longname)
                                )
                else:
                    if subs == 3:
                        codes = si_fields + (si_code,)
                    else:
                        codes = si_fields[1:] + (si_code,)
                    htmlContentList.append('''<a href="javascript:ajaxpage('salesinq/%s/%s','salesinqcontent');">&bullet;%s&bullet;&nbsp;</a>'''
                            % (dbname, SalesInqURL % codes, longname)
                            )
            htmlContentList.append('''
                    <div id="salesinqcontent"></div>
                    <script type="text/javascript">
                    ajaxpage('salesinq/%s/%s','salesinqcontent');
                    </script>''' % (dbname, partner_links[0][2] % (si_fields[0], si_fields[1], si_code)) )
            result[partner_id][fld] = dynamic_page_stub % "".join(htmlContentList)
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
