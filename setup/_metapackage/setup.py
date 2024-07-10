import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-infrastructure",
    description="Meta package for oca-infrastructure Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-base_dns_infrastructure>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
