#!/usr/bin/env python

from setuptools import setup
from io import open

version = open('VERSION', 'r', encoding='utf-8').read().strip()

setup(
  name = 'nosql-rest-preprocessor',
  packages = ['nosql_rest_preprocessor'],
  version = version,
  description = 'A middleware module which solves common problems when building rest-apis with nosql databases.',
  author = 'Felix Bruckmeier',
  author_email = 'felix.m.bruckmeier@gmail.com',
  url = 'https://github.com/felixbr/nosql-rest-preprocessor/',
  download_url = 'https://github.com/felixbr/nosql-rest-preprocessor/tarball/%s' % version,
  keywords = ['nosql', 'rest', 'web', 'middleware'],
  classifiers = [],
  license = 'MIT',
  install_requires = []
)