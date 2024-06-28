from setuptools import setup, find_packages

setup(
    name='pygaming',
    version='0.1',
    packages=find_packages(include=['pygaming', 'pygaming.*']),
    install_requires=[
        'pyinstaller',
        'pygame'
    ],
    entry_points={
        'console_scripts': [
            'pygaming=pygaming.commands.cli:cli'
        ],
    },
)

