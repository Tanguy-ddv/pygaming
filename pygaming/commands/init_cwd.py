"""
The function init_working_directory is used to create the working environment first.
It should be only used by using the command line defined in the `setup.py` file:
pygaming-init -name
The function make some basic folders and files to assure the localization of the files for the building
and to guide the programmer.
"""

import os
import shutil
import json
import locale

def init_cwd():
    """
    Create some files and folder in the current working directory.
    """

    cwd= os.getcwd()
    this_dir = os.path.dirname(__name__)

    if not os.path.exists('assets'):

        os.mkdir(os.path.join(cwd, 'assets'))
        os.mkdir(os.path.join(cwd, 'assets/musics'))
        os.mkdir(os.path.join(cwd, 'assets/sounds'))
        os.mkdir(os.path.join(cwd, 'assets/fonts'))
        os.mkdir(os.path.join(cwd, 'assets/images'))

        open(os.path.join(cwd, 'assets/icon.ico'),'w').close()
        open(os.path.join(cwd, 'assets/loop_times.json'),'w').close()

        print(f"The folder {os.path.join(cwd, 'assets')} has been created, remember to modify the icon.ico file with your icon. You can easily convert any .png image into a .ico with online converter.")

    if not os.path.exists('src'):
        os.mkdir(os.path.join(cwd, 'src'))

        shutil.copyfile(
            os.path.join(this_dir, 'pygaming', 'commands/game.template'),
            os.path.join(cwd, 'src/game.py')
        )

        shutil.copyfile(
            os.path.join(this_dir, 'pygaming', 'commands/player.template'),
            os.path.join(cwd, 'src/player.py')
        )

        shutil.copyfile(
            os.path.join(this_dir, 'pygaming', 'commands/server.template'),
            os.path.join(cwd, 'src/server.py')
        )

        print(f"The folder {os.path.join(cwd, 'src')} has been created and already contains three files. Keep either Server and Player OR Game. In this folder, add all your code.")
       
    if not os.path.exists('data'):
        os.mkdir('data')
        os.mkdir('data/sql')

        # create the 'tables.sql' file that will be used to generate the files.
        shutil.copyfile(
            os.path.join(this_dir, 'pygaming', 'commands/tables.template'),
            os.path.join(cwd, 'data/sql/tables.sql')
        )
        # Create an empty ig_queries.sql to store all the insert queries executed during the game.
        open(os.path.join(cwd, 'data/sql/ig_queries.sql'), 'w').close()

        # Create the 'localizations.sql' that is used to store all the texts of the game.
        shutil.copyfile(
            os.path.join(this_dir, 'pygaming', 'commands/localizations.template'),
            os.path.join(cwd, 'data/sql/localizations.sql')
        )
        # Create the keymap.json file used to map the inputs.
        shutil.copyfile(
            os.path.join(this_dir, 'pygaming', 'commands/keymap.template'),
            os.path.join(cwd, 'data/keymap.json')
        )

        with open(os.path.join(cwd, 'data/config.json'), 'r') as f:
            json.dump(
                {
                    'default_langage': locale.getdefaultlocale()[0],
                    'volume' : {
                        'main' : 1,
                        'music' : 1,
                        'sounds' : 1
                    }
                },
                f
            )

        print(f" The folder {os.path.join(cwd, 'data')} have been created. Insert in this all the data you need: .sql file to manage the database, and other `content` file if needed, as .json and .zip files, or custom files.")