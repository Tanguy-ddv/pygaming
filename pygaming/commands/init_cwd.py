"""
The function init_working_directory is used to create the working environment first.
It should be only used by using the command line defined in the `setup.py` file:
pygaming-init -name
The function make some basic folders and files to assure the localisation of the files for the building.
"""

import os
import shutil

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

        shutil.copyfile(
            os.path.join(this_dir, 'pygaming', 'commands/localizations.template'),
            os.path.join(cwd, 'data/sql/localizations.sql')
        )

        print(f" The folder {os.path.join(cwd, 'data')} have been created. Insert in this all the data you need: .sql file to manage the database, and other `content` file if needed, as .json and .zip files, or custom files.")