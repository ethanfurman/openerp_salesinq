{
   'name': 'SalesInq Interface',
    'version': '0.3',
    'category': 'Generic Modules',
    'description': """\
            Adds SalesInq tab for products and partners.
            """,
    'author': 'Emile van Sebille',
    'maintainer': 'Emile van Sebille',
    'website': 'www.openerp.com',
    'depends': [
            "base",
            "fis_integration",
            "product",
            ],
    'update_xml': [
            'res_partner_view.xml',
            'product_view.xml',
        ],
    'test': [],
    'installable': True,
    'active': False,
}
