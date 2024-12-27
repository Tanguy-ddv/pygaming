Pygaming is a python library used to big make 2D games. Built on [pygame](https://www.pygame.org/news), it contains several features to help building big games easily.

You can download pygaming in your python projects with

```bash
pip install pygaming
```

# Features

## Template

Pygaming implements a template to be used for every game. This is mainly done because pygaming uses default names for files that the developper will have to modify without renaming it.

## Phases

Each game consists of several phases: menus, lobbies, stages, etc. Each phase has a unique way to be updated at every loop iteration, they will display different elements, play different sounds and musics, and handle the input in different ways. The core architecure of a game based on pygaming is based on the implementation of customized phases. The phases are linked by transitions, and are identified by unique names.

## Games

An highlevel class named "Game" is provided by the library to be the main instance of the project. It is a very simple object that have to be created, and that is an argument for all phases. The .run() method of the game is to be called once all phases are instanciated and will run the main loop of the game.

## Online

The library implements easy-to-use asynchronous clients and servers classes to allow multiple players to play together. Similarly to the game and phases, a server can be instanciated with multiple ServerPhase. The .update() method of these phases are to be used to communicate with the players and run the game logic.

## Settings

Pygaming offers a way to easily manage game settings such as language, controls, fullscreen, volumes, and settings specific to the game itself (difficulties, rules, ...). The settings are automatically saved between two games.
Pgaming also offers config params that are not to be changed by the player, such as default values for language and cursor, screen size, fps, ...

## Mouse, Keyboard and Controls

The players can interact with the game through his keyboard and mouse. The keyboard inputs are mapped into controls, defined through the settings. The mouse inputs are very easy to use as well.

## Language

Pygaming offers a support for multiple languages by using localizations. When a speech is to be told or a text to be displayed, pygaming will automatically fetch the translated sound or text based on its localization, using the current language setting.

## Sound and Music

The sounds and speeches of the game can be easily played via the soundbox. Volumes for these sounds are also managed through categories, whose corresponding volumes are settings allowing the players to chose their prefered balance.
Pygaming also includes a jukebox to play music and make them automatically loop, or to play playlists.

## Files

Pygaming file managing system allows the developper to manage the files that are to be permanently saved (like config or some assets) and files that can have modifications. These files are automatically retrieved using one specific function. Pygaminf also easily allow the developper to use a unique icon for the game.

## Database

An sqlite database is automatically created and is used to store the localizations and sound categories for the game, but can also be used by the developper to store game data.

## Logger

The logger is used to easily logo data with the json format, used to store game history, make statistics for game developpement and so on.
The logger can be used for debugging as well.

## Screen

Pygaming manages automatically the screen to update all the elements.

### Frames

The main elements of the screen are frames. They are related to game phases. They represent a portion of the screen or of the parent frame. A frame can contain multiple widgets

### Widget

Pygaming implements several widgets that can be used to allow interaction between the player and the game. Four widgets have been implemented: labels, sliders, buttons and entries. More are to come.

### Window and masks

Windows are classes that represent the position of the frame in its parent. They can have masks. Masks are matrices with the same shape as the windows. The are used to apply effect on the frame, by apply a function on the pixels, based on the mask value.

### Arts

Arts are improvement of pygame surfaces. They allow the use of animation in the game. As animations can be openned from .gif files, arts can also be non-animated images openned from image files, or created as geometries. Arts can be transformed by using all transformations classes, including drawing, rotation and other shape transformation, as well as image processing algorithm (on which masks can be used).

## Resource management

Pygaming implements a resource management allowing it to load arts at the beginning of a phase (instead of at its instantiation) and unload them at the end. Masks, translations and sounds also benefits from this system. The computation of the current image of the game is also optimized.

## Distribution

Pygaming implements a command to build the game and an installer as executable files, allowing maximum portability.

# How to use it?

## Initialize the working directory

The first step to create your own game is to initialize your working directory. First, be sure to have python properly set. You can install pygaming with

```bash
pip install pygaming
```

Then, use the command

```bash
pygaming init
```

to initialize your working directory. It will automatically create a src/ folder, that will contain all your code, as well as an assets/ folder that will contain your assets (images, sounds, musics and fonts) and a data/ folder that will contains the game data, settings, database etc.
You will notice some files already existing in these folders. You can modify them, but not rename them.

## Make your own assets

You can make your assets by drawing your own characters, recording your own musics and sounds, using your pictures and downwloading some fonts. Do not forget to make your own icon as well. It must be named 'icon.ico' (you can find online converters for the format) and place in the assets/ folder to replace the template one.

## Define your database

In the database file, add your tables and complete the localizations, speeches, sounds and tables files. The sound table is used to define the sounds that will be loaded in each phase, same for the fonts. The localizations and speeches are used to manage languages.

## Make your phases

Now, it is time you make your own phases. The files on your src/ folder are great template to start.
All your phases must be subclass of the GamePhase class (or ServerPhase class for server phases) and have a distinct name. They all need to have at least these four methods:

- start(your_args: ...) -> None. This method is called at the beginning of the phase, and is used to initialize it, based on the arguments of the method.
- end() -> None. This method is called at the end of the phase, and is mostly used to unload assets and perform savings.
- update(loop_duration: int) -> None. This method is called at every iteration of the game's main loop. It is used to update the phase. The whole game logic is store here.
- next() -> str. This method is called at every iteration of the game's main loop. It used to know what is happening. It either return pygaming.STAY if the phase is not over, pygaming.NO_NEXT if the user requested to quit the game, or the name of another frame to be started.
- apply_transition(next_frame: str) -> dict[str, Any]. This method is called only when next() returns the name of another frame. In this case, this name is passed as argument of this method. This method should output a dict, whose keys are the name of the arguments of the .start() function of the next frame, and whose values are the values given for these arguments.

## Create your game

To create the game, you need to instantiate a object of the class pygaming.Game. Then, instantiate one object for each of your frame, using the game you just created as argument. Finally, call the run() method of your game. Do the same for your server, by instantiatiing a pygaming.Server object.

## Test it

To test your game, you can freely execute your server and your game on the same device and verify that everything is working properly. Change the debug flag of the game instance to be in debug mode.

## Distribute

Once your game is working, you can build it using the command

```bash
pygaming build game name
```

This command will create an executable file (accordingly to your system) that you can give to your friends. Executing it will create one or two new executables (depending if the game is online or not), which are the game and the server.

Be carefull, some antivirus might detect your game as a virus, get in your antivirus settings to allow it.

# Contributions

Feel free to contribute to this project by adding new features or helping optimizing existing ones.

# License

This software is distributed under a GNU GENERAL PUBLIC LICENSE
