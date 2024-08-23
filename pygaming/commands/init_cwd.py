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

def init_cwd():
    """Create some files and folder in the current working directory."""

    cwd = os.getcwd()
    this_dir = os.path.dirname(__name__)

    # Create the asset folder with:
    # - the 'musics', 'sounds', 'fonts', 'images' subfolders
    # - One icon.ico file (by default the pygaming icon)
    # - Two empty .json files: 
    #   - categories.json that map a sound file to its category (used to manage the different game volumes)
    #   - loop_times.json that map a music file to its loop instant (in sec).
    # Remark: These two file might stay empty if no musics (or no looping musics) and no sound or no sound categories.
    if not os.path.exists(os.path.join(cwd, 'assets')):
            
        with open(os.path.join(this_dir, 'pygaming', 'commands/init_texts/assert_success.txt'), 'r') as f:
            TEXT = ''.join(f.readlines())

        os.mkdir(os.path.join(cwd, 'assets'))
        os.mkdir(os.path.join(cwd, 'assets/musics'))
        os.mkdir(os.path.join(cwd, 'assets/sounds'))
        os.mkdir(os.path.join(cwd, 'assets/fonts'))
        os.mkdir(os.path.join(cwd, 'assets/images'))
        os.mkdir(os.path.join(cwd, 'assets/videos'))

        # Copy/paste the icon.ico default file
        shutil.copyfile(
            os.path.join(this_dir, 'pygaming', 'commands/templates/icon.ico'),
            os.path.join(cwd, 'assets/icon.ico')
        )

        # Create an empty loop_times.json
        with open(os.path.join(cwd, 'assets/musics/loop_times.json'),'w') as f:
            json.dump({}, f)
        
        # Create an empty categories.json
        with open(os.path.join(cwd, 'assets/sounds/categories.json'),'w') as f:
            json.dump({}, f)

        # Print the success output ot guide the user
        print("\033[33m" + TEXT + "\033[0m")

    # Create the data folder with:
    # - The sql subfolder containing all the sql files, including:
    #   - The tables.sql, which is the first file to be executed and which contains the table definitions
    #   - The localizations.sql, which contains all the texts of the game in several languages
    #   - The ig_queries.sql, which will be udpate during the game by adding successive queries.
    # - The settings.json files which contains a dict of settings that mught be modified during the game.
    #   The settings are: 
    #   - the control "THEKEY" :  "action"
    #   - the volume
    #   - the current language
    #   - the full screen (0/1)

    if not os.path.exists(os.path.join(cwd, 'data')):

        with open(os.path.join(this_dir, 'pygaming', 'commands/init_texts/data_success.txt'), 'r') as f:
            TEXT = ''.join(f.readlines())
        
        os.mkdir('data')
        os.mkdir('data/sql')
        os.mkdir('data/saves')
        os.mkdir('data/logs')

        # create the 'tables.sql' file that will be used to generate the files.
        shutil.copyfile(
            os.path.join(this_dir, 'pygaming', 'commands/templates/tables.sql'),
            os.path.join(cwd, 'data/sql/tables.sql')
        )
        # Create an empty ig_queries.sql to store all the insert queries executed during the game.
        open(os.path.join(cwd, 'data/sql/ig_queries.sql'), 'w').close()

        # Create the 'localizations.sql' that is used to store all the texts of the game.
        shutil.copyfile(
            os.path.join(this_dir, 'pygaming', 'commands/templates/localizations.sql'),
            os.path.join(cwd, 'data/sql/localizations.sql')
        )
        # Create the config.json that contains constants data that will be put into the executable
        shutil.copyfile(
            os.path.join(this_dir, 'pygaming', 'commands/templates/config.json'),
            os.path.join(cwd, 'data/config.json')
        )
        # Set the default language to the user language
        with open(os.path.join(this_dir, 'pygaming', 'commands/templates/config.json'), 'r') as f:
            config = json.load(f)
            config['default_language'] = locale.getdefaultlocale()[0]
        with open(os.path.join(this_dir, 'pygaming', 'commands/templates/config.json'), 'w') as f:
            json.dump(config, f)
        # Create the settings.json file that store the settings
        shutil.copyfile(
            os.path.join(this_dir, 'pygaming', 'commands/templates/settings.json'),
            os.path.join(cwd, 'data/settings.json')
        )
        # Set the current language to the user language
        with open(os.path.join(this_dir, 'pygaming', 'commands/templates/settings.json'), 'r') as f:
            settings = json.load(f)
            settings['current_language'] = locale.getdefaultlocale()[0]
        with open(os.path.join(this_dir, 'pygaming', 'commands/templates/settings.json'), 'w') as f:
            json.dump(settings, f)
        
        print("\033[35m" + TEXT + "\033[0m")

    # Create the src folder with:
    # - The game.py file which is a template to use. Any offline could follow this template.
    # - The server.py file which is a template to use. Any online game must have one server.
    #   The server must be launched once and every player connects to it via the player.py file
    #   The server is used to do all the calculations of the game, then send the data to the players.
    # - The player.py file which is a tempalte to use. Any online game must have one player.py / playing player.
    #   The player class display things, based on the server receptions, and send data to the server

    if not os.path.exists(os.path.join(cwd, 'src')):

        with open(os.path.join(this_dir, 'pygaming', 'commands/init_texts/src_success.txt'), 'r') as f:
            TEXT = ''.join(f.readlines())

        os.mkdir(os.path.join(cwd, 'src'))

        shutil.copyfile(
            os.path.join(this_dir, 'pygaming', 'commands/templates/game.py'),
            os.path.join(cwd, 'src/game.py')
        )

        shutil.copyfile(
            os.path.join(this_dir, 'pygaming', 'commands/templates/server.py'),
            os.path.join(cwd, 'src/server.py')
        )

        print("\033[32m" + TEXT + "\033[0m")

    with open(os.path.join(this_dir, 'pygaming', 'commands/init_texts/init_success.txt'), 'r') as f:
        TEXT = ''.join(f.readlines())

    # Reinitialize the color text and print the end of the init text
    print(TEXT)
