from setuptools import setup, find_packages

setup(
    name='pygaming',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'pyinstaller', 'pygame'
    ],
    entry_points={
        'console_scripts': [
            'pygaming-install=pygaming/_commands/_installer:install',
            'pygaming-init=pygaming/_commands/_init_cwd:init_pygaming'
        ],
    },
)