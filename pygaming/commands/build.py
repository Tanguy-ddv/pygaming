"""The build function create the game-install.exe file that is to be distributed."""

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

