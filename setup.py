from setuptools import setup, find_packages

setup(
    name='pygaming',
    author="Tanguy Dugas du Villard",
    author_mail="tanguy.dugas01@gmail.com",
    version='0.1.0',
    description="Pygaming is a python library based on pygame used to create game more easily by providing several tools.",
    packages=find_packages(),
    install_requires=[
        'pyinstaller',
        'pygame',
        'numpy',
        'pillow'
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
    ],
    python_requires='>=3.6',
    include_package_data=True,
    package_data={
        '': ['commands/templates/*'],
    },
)
