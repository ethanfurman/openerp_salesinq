from collections import defaultdict
from fnx import xid
from osv import osv, fields
from urllib import urlopen

CONFIG_ERROR = "Cannot sync products until  Settings --> Configuration --> FIS Integration --> %s  has been specified." 

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

LabelLinks = (
    "Plone/LabelDirectory/%s/%sB.bmp",
    "Plone/LabelDirectory/%s/%sNI.bmp",
    "Plone/LabelDirectory/%s/%sMK.bmp"
    )
    

LabelLinkStub = """<HTML>
<HEAD>
</HEAD>
  <BODY>
      %s
  </BODY>
</HTML>
"""


def _LabelLinks(obj, cr, uid, ids, field_name, arg, context=None):
    if context is None:
        context = {}
    xml_ids = [v for (k, v) in 
            xid.get_xml_ids(
                obj, cr, uid, ids, field_name, 
                arg=('F135', ),
                context=context).items()
            ]
    print
    print ids
    print xml_ids
    print
    result = defaultdict(dict)
    htmlContentList = [ ]
    for id, d in zip(ids, xml_ids):  # there should only be one...
        print id, d
        xml_id = d['xml_id']
        print xml_id
        htmlContentList.append('''<img src="%s" width=55%% align="left"/>''' % (LabelLinks[0] % (xml_id, xml_id)))
        htmlContentList.append('''<img src="%s" width=35%% align="right"/><br>''' % (LabelLinks[1] % (xml_id, xml_id)))
        htmlContentList.append('''<br><img src="%s" width=100%% /><br>''' % (LabelLinks[2] % (xml_id, xml_id)))
        result[id] = LabelLinkStub % "".join(htmlContentList)
        print result
        #for ii in htmlContentList: print ii
    #htmlContentList.append('''
    #        <script type="text/javascript">
    #        ajaxpage('%s','labellinkcontent');
    #        </script>''' % (LabelLinks[0] % (xml_id,xml_id)))
    #result[id]['label_server_stub'] = LabelLinkStub % "".join(htmlContentList)
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
                    <script type="text/javascript">
                    ajaxpage('%s','salesinqcontent');
                    </script>''' % (salesinq_links[0][2] % si_code) )
            result[product_id][fld] = SalesInqStub % "".join(htmlContentList)
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
        'label_server_stub': fields.function(
            _LabelLinks,
            string='Current Labels',
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
