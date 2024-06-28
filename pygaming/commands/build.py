"""The build function create the game-install.exe file that is to be distributed."""
import os
import json
import subprocess
import shutil

def build(name: str):
    """
    Build the game-install.exe file that need to be distributed, including a .zip of the src, assets and data files.
    Executing this file ask the user to choose a folder to save the game data, unzip them in this folder and
    then call pyinstaller to build the server and the game .exe files.
    This function must be called by using the command line `pygaming build [name-of-the-game]`.

    params:
    ---
    name: str, the name of the game.
    """
    cwd = os.getcwd()
    config_path = os.path.join(cwd, 'data', 'config.json')
    this_dir = os.path.dirname(__name__)

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
        config['name'] = name
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f)
    
        cwd= os.getcwd()
    this_dir = os.path.dirname(__name__)

    options = [
        '--onefile',
        '--windowed'
        '--icon=assets/icon.ico',
        f"--add-data={os.path.join(cwd, 'data')};data",
        f"--add-data={os.path.join(cwd, 'assets')};assets",
        f"--add-data={os.path.join(cwd, 'src')};src",
    ]

    command = ['pyinstaller'] + options + [os.path.join(this_dir, 'pygaming', 'commands/install.py')]
    subprocess.run(command, capture_output=True, text=True)

    shutil.copyfile(
        os.path.join(cwd, 'dist/install.exe'),
        os.path.join(cwd, f'install-{name}.exe')
    )