"""The command line entry point for the pygaming commands."""
import sys
from .init_cwd import init_cwd
from .build import build

INIT_CWD = 'init'
BUILD = 'build'

def cli():
    """Execute a command called by the command line 'pygaming ...'"""  
    args = sys.argv
    if len(args) < 2:
        print(f'You need a command: {INIT_CWD} or {BUILD}')
        sys.exit(1)
    cmd = args[1]
    if cmd not in [INIT_CWD, BUILD]:
        print(f"invalid command, you need one of {INIT_CWD} or {BUILD} but got {cmd}")

    if cmd == INIT_CWD:
        init_cwd()
    if cmd == BUILD:
        if len(args) == 2:
            print("Please specify the name of your game as argument of 'pygaming build'")
        else:
            build(" ".join(word.capitalize() for word in args[2:]))
