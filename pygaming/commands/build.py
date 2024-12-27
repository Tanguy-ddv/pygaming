"""The build function create the game-install.exe file that is to be distributed."""
import os
import json
import shutil
import platform
import importlib.resources
import PyInstaller.__main__
from ..error import PygamingException

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
    # Create the sep for the add-data of pyinstaller
    if platform.system() == 'Windows':
        sep = ';'
    else:
        sep = ':'

    cwd = os.getcwd()
    config_path = os.path.join(cwd, 'data', 'config.json')

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
        config['name'] = name
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f)

    print("The config file has been modified successfully")

    cwd= os.getcwd()

    game_options = [
        '--onefile',
        f"--icon={os.path.join(cwd, 'assets', 'icon.ico')}",
        f"--add-data={os.path.join(cwd, 'data')}{sep}data",
        f"--add-data={os.path.join(cwd, 'assets')}{sep}assets",
    ]

    installer_options = [
        '--onefile',
        #'--noconsole',
        f"--icon={os.path.join(cwd, 'assets', 'icon.ico')}",
        f"--add-data={os.path.join(cwd, 'data')}{sep}data",
        f"--add-data={os.path.join(cwd, 'assets')}{sep}assets",
        f"--add-data={os.path.join(cwd, 'src')}{sep}src",
    ]
    # Build the game file
    if os.path.exists(os.path.join(cwd, "src", "game.py")):
        command = [os.path.join(cwd, "src", "game.py")] + game_options + ['--windowed']
        PyInstaller.__main__.run(command)
        installer_options.append(f"--add-data={os.path.join(cwd, 'dist', 'game.exe')}{sep}game")
        print("The game has been built successfully")
    else:
        raise PygamingException("You need a game.py file as main file of the game")

    # Build the server file
    if os.path.exists(os.path.join(cwd, "src", "server.py")):
        command = [os.path.join(cwd, "src", "server.py")] + game_options
        PyInstaller.__main__.run(command)
        installer_options.append(f"--add-data={os.path.join(cwd, 'dist', 'server.exe')}{sep}server")
        print("The server has been built successfully")

    # Create the installer
    command = [os.path.join(importlib.resources.files('pygaming'), 'commands/install.py')] + installer_options
    PyInstaller.__main__.run(command)

    # Copy paste it on the root.
    try:
        shutil.copyfile(
            os.path.join(cwd, 'dist/install.exe'),
            os.path.join(cwd, f'install-{name}.exe')
        )
    except FileNotFoundError:
        print("The file has been deleted by your antivirus, find it back and tell your antivirus it is ok")

    # Remove the .spec files
    if os.path.isfile(os.path.join(cwd, "game.spec")):
        os.remove(os.path.join(cwd, "game.spec"))
    if os.path.isfile(os.path.join(cwd, "server.spec")):
        os.remove(os.path.join(cwd, "server.spec"))
    if os.path.isfile(os.path.join(cwd, "install.spec")):
        os.remove(os.path.join(cwd, "install.spec"))
