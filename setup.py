import os
from setuptools import setup

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

extra_files = package_files('sejits4fpgas/hw')
extra_files.append('*.config')


setup(
    name='Sejits4Fpgas',
    version='0.1',
    packages=['sejits4fpgas', 'sejits4fpgas.src'],
    package_dir={'sejits4fpgas': 'sejits4fpgas'},
    package_data={
        'sejits4fpgas':extra_files
    },
    url='',
    license='',
    author='Philipp Ebensberger',
    author_email='contact@3bricks-software.de',
    description='',
    install_requires=["numpy", "scikit-image", "scipy", "pytest"],
)
