import os
import sys
import re

from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))
NAME = 'cxx2rs'

with open(os.path.join(here, 'README.rst')) as readme:
    README = readme.read()

with open(os.path.join(here, 'CHANGES.rst')) as changes:
    CHANGES = changes.read()

with open(os.path.join(here, NAME, '__init__.py')) as version:
    VERSION = re.compile(r".*__version__ = '(.*?)'",
                         re.S).match(version.read()).group(1)



requires = [
    'setuptools',
    'clang'
    ]

setup(name=NAME,
      version=VERSION,
      description='A rust-binding generator for C/C++ files',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Intended Audience :: Developers",
        ],
      author='manuels',
      url='https://github.com/manuels/cxx2rs',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      entry_points="""\
      [console_scripts]
      {name} = {name}.__main__:main
      """.format(name=NAME),
      )

