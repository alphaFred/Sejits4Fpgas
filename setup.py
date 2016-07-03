from distutils.core import setup

setup(
    name='Sejits4Fpgas',
    version='0.1',
    packages=['sejits4fpgas'],
    package_dir={'sejits4fpgas': 'sejits4fpgas'},
    package_data={
        '':['*.config']
    },
    url='',
    license='',
    author='Philipp Ebensberger',
    author_email='contact@3bricks-software.de',
    description='',
    requires=['numpy', 'scikit-image']
)
