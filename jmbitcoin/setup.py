from setuptools import setup


setup(name='joinmarketbitcoin',
      version='0.6.2',
      description='Joinmarket client library for Bitcoin coinjoins',
      url='http://github.com/Joinmarket-Org/joinmarket-clientserver/jmbitcoin',
      author='',
      author_email='',
      license='GPL',
      packages=['jmbitcoin'],
      install_requires=['coincurve', 'python-bitcointx>=1.0.5', 'pyaes', 'urldecode'],
      zip_safe=False)
