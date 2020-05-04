from setuptools import setup


setup(name='joinmarketbase',
      version='0.6.2',
      description='Joinmarket client library for Bitcoin coinjoins',
      url='http://github.com/Joinmarket-Org/joinmarket-clientserver/jmbase',
      author='',
      author_email='',
      license='GPL',
      packages=['jmbase'],
      install_requires=['twisted==19.7.0', 'service-identity',
                        'chromalog==1.0.5'],
      python_requires='>=3.6',
      zip_safe=False)
