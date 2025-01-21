"""
The install module is the code executed by the installer.
"""
import os
import json
import sys
import shutil

from tkinter import filedialog, Tk
import base64


def ask_directory():
    """Ask for a directory."""
    root = Tk()
    root.withdraw()  # Hide the main window
    folder_path = filedialog.askdirectory(initialdir=os.path.join(os.path.expanduser("~"), "Documents"))
    return folder_path

def install():
    """
    The function executed by the install-game.exe file to install the game.
    It already have the data, assets and src in the temporary folder sys._MEIPASS
    """
    # get the data
    #pylint: disable=protected-access
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
    # Create the folder where the data, assets and src will be store
    modified_path_to_install = path_to_install
    nb_copy = 1
    while os.path.exists(modified_path_to_install):
        modified_path_to_install = path_to_install + f' ({nb_copy})'
        nb_copy += 1

    print("The choosen folder is", modified_path_to_install)

    # save the config file with the folder where the data are saved.
    # This is useful then, bc you can move the .exe files without causing any issue.
    config['path'] = modified_path_to_install

    with open(config_path, 'wb') as f:
        f.write(base64.b64encode(json.dumps(config).encode('utf-8')))

    # Encode the settings and state
    settings_path = os.path.join(base_path, 'data', 'settings.json')

    with open(settings_path, 'r', encoding='utf-8') as f:
        settings = json.load(f)
    with open(settings_path, 'wb') as f:
        f.write(base64.b64encode(json.dumps(settings).encode('utf-8')))

    state_path = os.path.join(base_path, 'data', 'state.json')

    with open(state_path, 'r', encoding='utf-8') as f:
        state = json.load(f)
    with open(state_path, 'wb') as f:
        f.write(base64.b64encode(json.dumps(state).encode('utf-8')))

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
    print('The assets folder has been copied.')

    # Copy the src folder
    shutil.copytree(
        os.path.join(base_path, 'src'),
        modified_path_to_install + '/src'
    )
    print('The src folder has been copied.')

 # Copy the server
    if os.path.exists(os.path.join(base_path, 'server')):
        shutil.copytree(
            os.path.join(base_path, 'server'),
            os.path.join(modified_path_to_install, 'server'),
        )
        shutil.copyfile(
            os.path.join(modified_path_to_install, 'server', 'server_launcher.exe'),
            os.path.join(modified_path_to_install, f'{name}-server.exe'),
        )
        shutil.rmtree(os.path.join(modified_path_to_install, 'server'))
        print('The server has been copied.')

    shutil.copytree(
        os.path.join(base_path, 'game'),
        os.path.join(modified_path_to_install, 'game'),
    )
    shutil.copyfile(
        os.path.join(modified_path_to_install, 'game', 'game_launcher.exe'),
        os.path.join(modified_path_to_install, f'{name}.exe'),
    )
    shutil.rmtree(os.path.join(modified_path_to_install, 'game'))
    print('The game has been copied.')

if __name__ == '__main__':
    install()
