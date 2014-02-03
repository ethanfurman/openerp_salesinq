from collections import defaultdict
from fnx import xid
from osv import osv, fields
from urllib import urlopen


salesinq_links = [
        ('salesinq_yrsmos','All Years & Months',
            "pyvotRpt?optX_op=%s&%s_op=%s&rptColFmt_op=allyrsmos"),
        ('salesinq_yrsmos_shipto','All Years & Months by Ship To',
            "pyvotRpt?%s_op=%s&rptColFmt_op=allyrsmos&optX_op=ShipTo"),
        ('salesinq_yrsmos_item','All Years & Months by Item',
            "pyvotRpt?%s_op=%s&rptColFmt_op=allyrsmos&optX_op=Item"),
        ('salesinq_yrs','All Years',
            "pyvotRpt?optX_op=%s&%s_op=%s&rptColFmt_op=allyears"),
        ('salesinq_yrs_shipto','All Years by ShipTo',
            "pyvotRpt?ck_descs=on&%s_op=%s&rptColFmt_op=allyears&optX_op=ShipTo"),
        ('salesinq_yrs_item','All Years by Item',
            "pyvotRpt?ck_descs=on&%s_op=%s&rptColFmt_op=allyears&optX_op=Item"),
        ('salesinq_yrs_shiptoitem','All Years by ShipTo & Item',
            "pyvotRpt?ck_descs=on&%s_op=%s&rptColFmt_op=allyears&optX_op=ShipTo&optY_op=Item"),
        ]

#########################################################
#            pyvotRpt?optX_op=Item&Supplier_op=000140&rptColFmt_op=rollingyear
###########################################################################################

SalesInqStub = """<HTML>
<HEAD>
<script type="text/javascript">

/***********************************************
* Dynamic Ajax Content- (c) Dynamic Drive DHTML code library (www.dynamicdrive.com)
* This notice MUST stay intact for legal use
* Visit Dynamic Drive at http://www.dynamicdrive.com/ for full source code
***********************************************/

var bustcachevar=1 //bust potential caching of external pages after initial request? (1=yes, 0=no)
var loadedobjects=""
var rootdomain="http://"+window.location.hostname
var bustcacheparameter=""

function ajaxpage(url, containerid){
          var page_request = false
            if (window.XMLHttpRequest) // if Mozilla, Safari etc
                page_request = new XMLHttpRequest()
                  else 
                      if (window.ActiveXObject){ // if IE
                                try {
                                            page_request = new ActiveXObject("Msxml2.XMLHTTP")
                                                  } 
                                      catch (e){
                                                  try{
                                                                page_request = new ActiveXObject("Microsoft.XMLHTTP")
                                                                        }
                                                          catch (e){}
                                                                }
                                          }
                          else
                                return false
                                  page_request.onreadystatechange=function(){
                                          loadpage(page_request, containerid)
                                            }
                                    if (bustcachevar) //if bust caching of external page
                                        bustcacheparameter=(url.indexOf("?")!=-1)? "&"+new Date().getTime() : "?"+new Date().getTime()
                                            page_request.open('GET', url+bustcacheparameter, true)
                                                page_request.send(null) 
                                                }

function loadpage(page_request, containerid){
        //if (page_request.readyState == 4 && (page_request.status==200 || window.location.href.indexOf("http")==-1))
        //alert("alerting..."+page_request+"...alerted")
        document.getElementById(containerid).innerHTML=page_request.responseText
        }

function loadobjs(){
        if (!document.getElementById)
        return
        for (i=0; i<arguments.length; i++){
            var file=arguments[i]
            var fileref=""
            if (loadedobjects.indexOf(file)==-1){ //Check to see if this object has not already been added to page before proceeding
                if (file.indexOf(".js")!=-1){ //If object is a js file
                    fileref=document.createElement('script')
                    fileref.setAttribute("type","text/javascript");
                    fileref.setAttribute("src", file);
                    }
                else if (file.indexOf(".css")!=-1){ //If object is a css file
                    fileref=document.createElement("link")
                    fileref.setAttribute("rel", "stylesheet");
                    fileref.setAttribute("type", "text/css");
                    fileref.setAttribute("href", file);
                    }
                }
            if (fileref!=""){
                document.getElementsByTagName("head").item(0).appendChild(fileref)
                loadedobjects+=file+" " //Remember this object as being already added to page
                }
            }
        }

</script>
</HEAD>
  <BODY>
      %s
    <div id="salesinqcontent">salesinqcontent</div>
  </BODY>
</HTML>

"""


def _x_salesinq(obj, cr, uid, ids, field_name, arg, context=None):
    if context is None:
        context = {}
    xml_ids = [v for (k, v) in
            xid.get_xml_ids(
                obj, cr, uid, ids, field_name,
                arg=('supplier_integration','FIS Supplier/Vendor', CONFIG_ERROR),
                context=context).items()
            ]
    result = {}
    for id, xml_id in zip(ids, xml_ids):
        result[id] = urlopen(_salesinq_links[field_name] % xml_id).read()
    return result


def salesinq(obj, cr, uid, ids, fields, arg, context=None):
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
            arg=('F33', 'F65', 'F163'),
            context=context)
    result = defaultdict(dict)
    for partner_id, parent_id in chain.items():
        result[partner_id]['xml_id'] = xml_ids[partner_id]['xml_id']
        si_codes = xml_ids[partner_id]
        si_code = si_codes['xml_id'].replace("'","%27")
        valid_si_code = is_valid(si_code)
        partner = obj.browse(cr, uid, [partner_id], context=context)[0]
        if parent_id is not None and not valid_si_code:
            si_code = xml_ids[parent_id]
            valid_si_code = is_valid(si_code)
            partner = obj.browse(cr, uid, [parent_id], context=context)[0]
        result[partner_id]['is_salesinq_able'] = valid_si_code
        for fld in fields:
            if not valid_si_code:
                result[partner_id][fld] = ''
                continue
            htmlContentList = [ ]
            for shortname, longname, SalesInqURL in salesinq_links:
                if shortname == 'salesinq_yrs':
                    htmlContentList.append('<br>')
                if partner.customer:
                    si_fields = 'Cust','Cust'
                else: # .supplier:
                    si_fields = 'Item', 'Supplier'
                if SalesInqURL.count('%s') == 3:
                    codes = si_fields + (si_code,)
                else:
                    codes = si_fields[1:] + (si_code,)
                htmlContentList.append('''<a href="javascript:ajaxpage('%s','salesinqcontent');">&bullet;%s&bullet;&nbsp;</a>''' % (SalesInqURL % codes, longname))
            htmlContentList.append('''
                    <script type="text/javascript">
                    ajaxpage('%s','salesinqcontent');
                    </script>''' % (salesinq_links[0][2] % (si_fields[0], si_fields[1], si_code)) )
            result[partner_id][fld] = SalesInqStub % "".join(htmlContentList)
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
        'salesinq_yrsmos': fields.function(
            salesinq,
            multi='custom',
            string='Years and Months',
            type='html',
            method=False,
            ),
        'salesinq_yrsmos_shipto': fields.function(
            salesinq,
            multi='custom',
            string='Years and Months by Ship-to',
            type='html',
            method=False,
            ),
        'salesinq_yrsmos_item': fields.function(
            salesinq,
            multi='custom',
            string='Years and Months by Item',
            type='html',
            method=False,
            ),
        'salesinq_yrs': fields.function(
            salesinq,
            multi='custom',
            string='Years',
            type='html',
            method=False,
            ),
        'salesinq_yrs_shipto': fields.function(
            salesinq,
            multi='custom',
            string='Years by Ship-to',
            type='html',
            method=False,
            ),
        'salesinq_yrs_item': fields.function(
            salesinq,
            multi='custom',
            string='Years by Item',
            type='html',
            method=False,
            ),
        'salesinq_yrs_shiptoitem': fields.function(
            salesinq,
            multi='custom',
            string='Years by Ship-to/Item',
            type='html',
            method=False,
            ),
        }
res_partner()
