#!/usr/bin/env python
from distutils.core import setup

setup(
  name="sitetools",
  version="1.0.0",
  author="Maciek Ruckgaber",
  author_email="maciekrb@gmail.com",
  description="Python utils for assisting in site migration tasks",
  long_description=open('README.md').read(),
  packages=["sitetools"],
  license="BSD License",
  scripts=[
      "sitetools/siteutil.py"
  ],
  classifiers=[
    'Development Status :: Release Candidate',
    'Environment :: Web Environment',
    'Intended Audience :: Web App Developers, Systems Administrators',
    'License :: BSD License',
    'Operating System :: OS Independent',
    'Topic :: Software Development :: Libraries'
  ]
)
