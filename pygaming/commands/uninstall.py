import shutil
import os

def uninstall():

    cwd = os.getcwd()

    if os.path.isdir(os.path.join(cwd, 'build/game')):
        shutil.rmtree(os.path.join(cwd, 'build/game'))

    if os.path.isdir(os.path.join(cwd, 'build/player')):
        shutil.rmtree(os.path.join(cwd, 'build/player'))

    if os.path.isdir(os.path.join(cwd, 'build/server')):
        shutil.rmtree(os.path.join(cwd, 'build/server'))

    if os.path.exists(os.path.join(cwd, 'dist/game.exe')):
        os.remove(os.path.join(cwd, 'dist/game.exe'))
    
    if os.path.exists(os.path.join(cwd, 'dist/player.exe')):
        os.remove(os.path.join(cwd, 'dist/player.exe'))
    
    if os.path.exists(os.path.join(cwd, 'dist/server.exe')):
        os.remove(os.path.join(cwd, 'dist/server.exe'))
