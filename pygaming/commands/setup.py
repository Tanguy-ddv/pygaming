import os
import json
from .install import install
abs_path = os.path.abspath('.')
config_path = abs_path + '/data/config.json'
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)
    config['path_to_dynamic'] = abs_path
with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(config, f)
install()