import os
import json
import sys
import shutil
import subprocess

import tkinter as tk
from tkinter import filedialog

def ask_directory():
    """Ask for a directory."""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    folder_path = filedialog.askdirectory(initialdir=os.path.join(os.path.expanduser("~"), "Documents"))
    return folder_path

def install():
    """
    The function executed by the install-game.exe file to install the game.
    It already have the data, assets and src in the temporary folder sys._MEIPASS
    """
    # Ask for a place to place the game
    path_to_parent_folder = ask_directory()
    cwd = os.getcwd()
    # get the data
    base_path = sys._MEIPASS
    # save the config file with the folder where the data are saved.
    # This is useful then, bc you can move the .exe files without causing any issue.
    config_path = os.path.join(base_path, 'data', 'config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
        # Get the name of the game stored here by the build function
        name = config['name']
        path_to_install = path_to_parent_folder + '/' + name
        config['path'] = path_to_install
        
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f)
    # Create the folder where the data, assets and src will e store

    os.mkdir(path_to_install)
    shutil.copytree(
        os.path.join(base_path, 'data'),
        path_to_install + '/data'
    )
    shutil.copytree(
        os.path.join(base_path, 'assets'),
        path_to_install + '/assets'
    )
    shutil.copytree(
        os.path.join(base_path, 'src'),
        path_to_install + '/src'
    )

    default_options = [
        '--onefile',
        '--icon=assets/icon.ico',
        '--add-data=data;data',
        '--add-data=assets;assets',
    ]
    if os.path.exists(os.path.join(base_path, "src/game.py")):
        command = ['pyinstaller'] + default_options + ['--windowed'] + [os.path.join(base_path, "src/game.py")]
        subprocess.run(command, capture_output=True, text=True)
    
        shutil.copyfile(
            os.path.join(cwd, 'dist/game.exe'),
            os.path.join(path_to_install, f'{name}.exe')
        )

    if os.path.exists(os.path.join(base_path, "src/player.py")):
        command = ['pyinstaller'] + default_options + ['--windowed'] + [os.path.join(base_path, "src/player.py")]
        subprocess.run(command, capture_output=True, text=True)
    
        shutil.copyfile(
            os.path.join(cwd, 'dist/player.exe'),
            os.path.join(path_to_install, f'{name}.exe')
        )

    if os.path.exists(os.path.join(base_path, "src/server.py")):
        command = ['pyinstaller'] + default_options + [os.path.join(base_path, "src/server.py")]
        subprocess.run(command, capture_output=True, text=True)
    
        shutil.copyfile(
            os.path.join(cwd, 'dist/server.exe'),
            os.path.join(path_to_install, f'{name}-server.exe')
        )

if __name__ == '__main__':
    install()