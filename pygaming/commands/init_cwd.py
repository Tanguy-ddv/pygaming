"""
The function init_cwd is used to create the working environment first.
It should be only used by using the command line defined in the `setup.py` file: pygaming init
The function make some basic folders and files to assure the localization of the files for the building
and to guide the programmer.
"""

import os
import shutil
import json
import locale
import importlib.resources
import uuid

def init_cwd():
    """Create some files and folder in the current working directory."""

    cwd = os.getcwd()
    this_dir = str(importlib.resources.files('pygaming'))

    if not os.path.exists(os.path.join(cwd, 'assets')):

        shutil.copytree(
            os.path.join(this_dir, 'commands/templates/assets'),
            os.path.join(cwd, 'assets')
        )

        # Print the success output ot guide the user
        with open(os.path.join(this_dir, 'commands/init_texts/asset_success.txt'), 'r', encoding='utf-8') as f:
            text = ''.join(f.readlines())
        print("\033[33m" + text + "\033[0m")

        os.makedirs(os.path.join(cwd, 'assets', 'musics'), exist_ok=True)
        os.makedirs(os.path.join(cwd, 'assets', 'fonts'), exist_ok=True)
        os.makedirs(os.path.join(cwd, 'assets', 'sounds'), exist_ok=True)
        os.makedirs(os.path.join(cwd, 'assets', 'images'), exist_ok=True)
        os.makedirs(os.path.join(cwd, 'assets', 'cursors'), exist_ok=True)

    if not os.path.exists(os.path.join(cwd, 'data')):

        language = locale.getlocale()[0]

        shutil.copytree(
            os.path.join(this_dir, 'commands/templates/data'),
            os.path.join(cwd, 'data')
        )

        with open(os.path.join(cwd, 'data/settings.json'), 'r', encoding='utf-8') as f:
            settings = json.load(f)
            settings['current_language'] = language
        with open(os.path.join(cwd, 'data/settings.json'), 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4)

        with open(os.path.join(cwd, 'data/config.json'), 'r', encoding='utf-8') as f:
            config = json.load(f)
            config['default_language'] = language
            config['path'] = cwd
            config['game_id'] = str(uuid.uuid4()).replace('-','')

        with open(os.path.join(cwd, 'data/config.json'), 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)


        with open(os.path.join(this_dir, 'commands/init_texts/data_success.txt'), 'r', encoding='utf-8') as f:
            text = ''.join(f.readlines())
        print("\033[35m" + text + "\033[0m")


    if not os.path.exists(os.path.join(cwd, 'src')):

        shutil.copytree(
            os.path.join(this_dir, 'commands/templates/src'),
            os.path.join(cwd, 'src')
        )

        with open(os.path.join(this_dir, 'commands/init_texts/src_success.txt'), 'r', encoding='utf-8') as f:
            text = ''.join(f.readlines())

        print("\033[32m" + text + "\033[0m")

    with open(os.path.join(this_dir, 'commands/init_texts/init_success.txt'), 'r', encoding='utf-8') as f:
        text = ''.join(f.readlines())

    # Reinitialize the color text and print the end of the init text
    print(text)
