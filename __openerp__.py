{
   'name': 'SalesInq Interface',
    'version': '0.4',
    'category': 'Generic Modules',
    'description': """\
            Adds SalesInq tab for products and partners.
            Adds link to external, restricted, SalesInq web page.
            """,
    'author': 'Emile van Sebille',
    'maintainer': 'Emile van Sebille',
    'website': 'www.openerp.com',
    'depends': [
            "base",
            "fnx",
            "product",
            "wholeherb_integration",
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
}
