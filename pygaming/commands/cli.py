"""
The command line entry point for the pygaming commands.
"""

from .init_cwd import init_cwd
from .install import install
from .uninstall import uninstall

INIT_CWD = 'init'
INSTALL = 'install'
UNINSTALL = 'uninstall'

import sys

def cli():
    
    args = sys.argv
    if len(args) < 2:
        print(f'You need a command: {INIT_CWD}, {INSTALL} OR {UNINSTALL}')
        sys.exit(1)
    cmd = args[1]
    if cmd not in [INIT_CWD, UNINSTALL, INSTALL]:
        print(f"invalid command, you need one of {INIT_CWD}, {INSTALL} OR {UNINSTALL} but got {cmd}")
    
    if cmd == INIT_CWD:
        init_cwd()
    if cmd == INSTALL:
        install()
    if cmd == UNINSTALL:
        uninstall()