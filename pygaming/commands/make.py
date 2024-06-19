import shutil
import os
import subprocess

def make():

    cwd= os.getcwd()
    this_dir = os.path.dirname(__name__)

    default_options = [
        '--onefile',
        '--icon=assets/icon.ico',
    ]

    command = ['pyinstaller'] + default_options + [os.path.join(this_dir, 'pygaming', 'commands/setup.py')]
    subprocess.run(command, capture_output=True, text=True)

    shutil.copyfile(
        os.path.join(cwd, 'dist/setup.exe'),
        os.path.join(cwd, f'setup.exe')
    )
