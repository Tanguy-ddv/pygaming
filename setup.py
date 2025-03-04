from setuptools import setup, find_packages

setup(
    name='pygaming',
    author="Tanguy Dugas du Villard",
    author_mail="tanguy.dugas01@gmail.com",
    version='0.9.0',
    description="Pygaming is a python library based on pygame used to create game more easily by providing several tools.",
    packages=find_packages(),
    install_requires=[
        'pyinstaller', # to build the game as executable
        'pygame', # I don't think I need to explain whay pygame is a requirement.
        'numpy', # To process the matrix behind the surfaces.
        'gamarts', # for the arts
        'ZOCallable', # for the transitions.
        'pygame-cv' # for the camera effects.
    ],
    entry_points={
        'console_scripts': [
            'pygaming=pygaming.commands.cli:cli'
        ],
    },
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Tanguy-ddv/pygaming/",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Games/Entertainment",
        "Topic :: Software Development :: Libraries :: pygame"
    ],
    python_requires='>=3.6',
    include_package_data=True,
    package_data={
        '': ['commands/templates/*'],
    },
)
