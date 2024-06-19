"""
This file contains the function to build the game, i.e to make it a .exe file.
Once called, the function build one 'name'-server.py and one 'name'.py (where name is the name of the game).
This function shouldn't be called in a different way than by the command line
defined in the `setup.py` file. (i.e with pygaming-install).
"""
import subprocess
import os
import shutil

def install():
    """Install the game as a .exe"""

    default_options = [
        '--onefile',
        '--icon=assets/icon.ico',
        '--add-data=data;data',
        '--add-data=assets;assets',
    ]

    cwd = os.getcwd()

    if os.path.exists(os.path.join(cwd, "src/game.py")):
        command = ['pyinstaller'] + default_options + ['--windowed'] + [os.path.join(cwd, "src/game.py")]
        subprocess.run(command, capture_output=True, text=True)
    
        shutil.copyfile(
            os.path.join(cwd, 'dist/game.exe'),
            os.path.join(cwd, f'game.exe')
        )

    if os.path.exists(os.path.join(cwd, "src/player.py")):
        command = ['pyinstaller'] + default_options + [os.path.join(cwd, "src/player.py")]
        subprocess.run(command, capture_output=True, text=True)
    
        shutil.copyfile(
            os.path.join(cwd, 'dist/player.exe'),
            os.path.join(cwd, f'player.exe')
        )

    if os.path.exists(os.path.join(cwd, "src/server.py")):
        command = ['pyinstaller'] + default_options + [os.path.join(cwd, "src/server.py")]
        subprocess.run(command, capture_output=True, text=True)
    
        shutil.copyfile(
            os.path.join(cwd, 'dist/server.exe'),
            os.path.join(cwd, f'server.exe')
        )

    print("""Successfull installation of the game. You can now play it without python and distribute it easily,
          simply by using copy-pasting the files. You may also rename the files with the name of your game.""")