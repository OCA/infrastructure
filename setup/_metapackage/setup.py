import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo8-addons-oca-infrastructure-dns",
    description="Meta package for oca-infrastructure-dns Odoo addons",
    version=version,
    install_requires=[
        'odoo8-addon-connector_dns',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
