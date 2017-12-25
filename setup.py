import os
import sys

from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name = "cdx",
<<<<<<< HEAD
    version = '1.2.2',
=======
    version = '1.1.3',
>>>>>>> 53553d1cfa5f3493de319031251ef99f253cec58
    author = "lijun",
    author_email = 'zhanglijuncn@outlook.com',
    url = "https://github.com/ZhangLijuncn/cdx",
    description = 'change dirpath or open a url by bookmark fast in terminal',
    long_description = readme(),
    license = 'MIT',
    packages=['cdx'],
    include_package_data=True,
    entry_points={
        'console_scripts':[
            'cdx=cdx.cdx:main'
            ]
        },
    zip_safe=False,
)
