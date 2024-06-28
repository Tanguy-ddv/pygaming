import os
import json
import sys

def setup():
    """The function executed by the setup.exe file to install the game."""
    name = sys.argv[2]
    abs_path = os.path.abspath('.')
    config_path = abs_path + '/data/config.json'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
        config['path_to_dynamic'] = abs_path
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f)

if __name__ == '__main__':
    setup()