
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'WoWgic',
    'author': 'Mari Satheesh',
    'url': 'URL to get it at.',
    'download_url': 'Where to download it.',
    'author_email': 'sathishsms@gmail.com',
    'version': '0.1',
    'install_requires': ['Flask>=0.10.1'],
    'packages': ['wowgic_dev'],
    'scripts': [],
    'name': 'wowgic'
}

setup(**config)
