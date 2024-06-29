import os
import json
import sys
import shutil

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
    # get the data
    base_path = sys._MEIPASS

    # Get the name
    config_path = os.path.join(base_path, 'data', 'config.json')

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
        # Get the name of the game stored here by the build function
        name: str = config['name']
    
    # Ask for a place to place the game
    path_to_parent_folder = ask_directory()
    if path_to_parent_folder is None:
        return

    path_to_install = path_to_parent_folder + '/' + name
    # Create the folder where the data, assets and src will e store
    modified_path_to_install = path_to_install
    nb_copy = 1
    while os.path.exists(modified_path_to_install):
        modified_path_to_install = path_to_install + f' ({nb_copy})'

    print("The choosen folder is", modified_path_to_install)

    # save the config file with the folder where the data are saved.
    # This is useful then, bc you can move the .exe files without causing any issue.
    config['path'] = modified_path_to_install
        
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f)

    
    # Copy the data folder
    shutil.copytree(
        os.path.join(base_path, 'data'),
        modified_path_to_install + '/data'
    )
    print('The data folder has been copied.')
    # Copy the asset folder
    shutil.copytree(
        os.path.join(base_path, 'assets'),
        modified_path_to_install + '/assets'
    )
    print('The data assets has been copied.')

    # Copy the src folder
    shutil.copytree(
        os.path.join(base_path, 'src'),
        modified_path_to_install + '/src'
    )
    print('The src assets has been copied.')

 # Copy the server
    if os.path.exists(os.path.join(base_path, 'server')):
        shutil.copytree(
            os.path.join(base_path, 'server'),
            os.path.join(modified_path_to_install, 'server'),
        )
        shutil.copyfile(
            os.path.join(modified_path_to_install, 'server', 'server.exe'),
            os.path.join(modified_path_to_install, 'server.exe'),
        )
        shutil.rmtree(os.path.join(modified_path_to_install, 'server'))
        print('The server.exe has been copied.')

 # Copy the game
    if os.path.exists(os.path.join(base_path, 'game')):
        shutil.copytree(
            os.path.join(base_path, 'game'),
            os.path.join(modified_path_to_install, 'game'),
        )
        shutil.copyfile(
            os.path.join(modified_path_to_install, 'game', 'game.exe'),
            os.path.join(modified_path_to_install, 'game.exe'),
        )
        shutil.rmtree(os.path.join(modified_path_to_install, 'game'))
        print('The game.exe has been copied.')

# Copy the player
    if os.path.exists(os.path.join(base_path, 'player')):
        shutil.copytree(
            os.path.join(base_path, 'player'),
            os.path.join(modified_path_to_install, 'player'),
        )
        shutil.copyfile(
            os.path.join(modified_path_to_install, 'player', 'player.exe'),
            os.path.join(modified_path_to_install, 'player.exe'),
        )
        shutil.rmtree(os.path.join(modified_path_to_install, 'player'))
        print('The player.exe has been copied.')

if __name__ == '__main__':
    install()