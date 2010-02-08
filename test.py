#!/usr/bin/python
""" Unit test gilet for all the test script, borrown from rpy"""

import os, sys
import random
import unittest

def run(module):
    print 'Testing:', module[4:]
    try:
        unittest.main('kobas.tests.%s' % module)
    except SystemExit:
        pass

if __name__ == '__main__':
    sys.path.insert(0, 'src')
    
    import kobas.tests

    modules = os.listdir(os.path.dirname(kobas.tests.__file__))

    if '--random' in sys.argv:
        random.shuffle(modules)
        sys.argv.remove('--random')
    
    for module in modules:
        if module.startswith('Test') and not module.endswith('.pyc'):
            name = module[:-3]
            run(name)
