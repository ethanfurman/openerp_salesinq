__all__ = ['product', 'res_partner', 'salesinq', 'company', 'res_config', 'controllers']

import product
import res_partner
import salesinq
import company
import res_config
import controllers

from antipathy import Path
here = Path(__file__).dirname
if here.exists('../wholeherb_integration'):
    integration = 'wholeherb_integration'
elif here.exists('../fis_integration'):
    integration = 'fis_integration'
else:
    integration = ''

__openerp__ = """{
   'name': 'SalesInq Interface',
    'version': '0.4',
    'category': 'Generic Modules',
    'description': \"\""\
            Adds SalesInq tab for products and partners.
            Adds link to external, restricted, SalesInq web page.
            \"\"\",
    'author': 'Emile van Sebille',
    'maintainer': 'Emile van Sebille',
    'website': 'www.openerp.com',
    'depends': [
            "base",
            "fnx",
            "product",
            "%s",
            ],
    'css': [
            "static/src/css/salesinq.css",
            ],
    'update_xml': [
            'res_config_view.xaml',
            'res_partner_view.xaml',
            'product_view.xaml',
            'security/salesinq_security.xaml',
            'security/ir.model.access.csv',
            'salesinq_view.xaml',
            ],
    'test': [],
    'installable': True,
    'active': False,
}""" % integration

with open(Path(__file__).dirname/'__openerp__.py', 'w') as f:
    f.write(__openerp__)
