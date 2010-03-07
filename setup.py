#!/usr/bin/env python

from glob import glob 
from distutils.core import setup

setup(name = "kobas",
      version = "1.2.0",
      description = "KEGG Orthology Based Annotation System",
      author = "Xizeng Mao, Jianmin Wu, Cao Cai, Chen Xie, and Liping Wei",
      author_email = "kobas@mail.cbi.pku.edu.cn",
      url = "http://kobas.cbi.pku.edu.cn",
      package_dir = {"kobas":"kobas"},
      packages = ['kobas',
                  'kobas.kgml',
                  'kobas.pathway',
                  'kobas.tests',],
      scripts = glob('scripts/*'),
      data_files = [('/etc', ['data/kobasrc']), ])
