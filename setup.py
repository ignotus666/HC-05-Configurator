#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name='hc05-configurator',
    version='1.0.0',
    description='GUI tool to configure HC-05 Bluetooth modules via AT commands',
    author='Daryl Hanlon',
    author_email='darylo1@hotmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        'PyQt5',
        'pyserial',
    ],
    entry_points={
        'gui_scripts': [
            'hc05-configurator = main:main',
        ],
    },
    include_package_data=True,
)
