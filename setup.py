
from setuptools  import setup

setup(
      name='Using_NetSurfP',
      packages=['Using_NetSurfP'],
      version='0.1',
      description='Tools to help with NetSurfP',
      license = 'MIT',
      author='Sarah Wooller',
      author_email='s.k.wooller@sussex.ac.uk',
      url='https://github.com/SarahWooller/Using_NetSurfP',
      download_url=('https://github.com/SarahWooller/Using_NetSurfP/archive/0.1.tar.gz'),
      keywords=['ENST', 'NetSurfP', 'bioinformatics', 'Uniprot', 'fastas'],
      classifiers=[],
      install_requires=[
          'pandas'
      ],
      setup_requires=[],
      tests_require=[],
      zip_safe = False
      )

