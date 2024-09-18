# Pygaming

Pygaming is a python library used to make video games more easily. Built on [pygame](https://www.pygame.org/news), it provides several components to ease the programmer's life.

You can download pygaming in your python projects with 
```bash
pip install pygaming
```

## Features

### Phases and Transitions

Each game consists of several phases. During each phase, the game will update differently, use inputs in a different way and display different things. These phases are linked together via transitions, which are custom subclasses with a given `apply` method.

### Game and Server

The Game is the class that represent the game itself. It is used to link every aspect of the game together and update them.
The Game could be offline, or online. It this case, a Server is needed aswell.
The Server is the class that is used to communicate with the several instances of the game, by receiving and sending data.

### Network

The library implements easy-to-use clients and servers (both accessible in every game and server phase through `self.network`) to allow the players to communicate with the server in a star-shaped network.

### Inputs and Controls

The Inputs class (accessible in every game phase through `self.inputs`) implements the input management. You can easily find the mouse position and velocity,
as well as define controls that could be modified by the user.

### Sound and Music

The SoundBox class (accessible in every game phase through `self.soundbox`) can be easily used to play sounds and manage the volume of the sounds based on categories.
The Jukebox class (accessible in every game phase through `self.jukebox`) can be easily used to play musics buy defining playlists or by playing a music that will loop.

### Files

The File system is manage throw the _assets_ and the _data_ folders. They are automatically explored when using a DataFile, ImageFile, FontFile (and so on) object. DataFile must be subclassed to get objects particular objects stored in the _data_ folder.

### Database and Language

The Database class (accessible in every game and server phase through `self.database`) is used to manage easily the database, query it and insert new lines while playing. The game can automatically manage the language by the use of texts and speeches `self.texts` and `self.speeches` in every game phase.

### Logger

The logger is used to easily logo data with the json format, used to store game historic, make statistics for game developpement and so on.

### Screen

The Screen is used to manage what is displayed during the game. It is composed of Frames, widgets and other graphical elements specific to each game phase.
The focus on widgets and the behavior of the game when hovering some object is also automatically managed.

## How to use it?

### Initialize the working directory

The first step to create your own game is to initialize your working directory. First, be sure have python properly set. You can install pygaming with
```bash
pip install pygaming
```

Then, use the command 
```bash
pygaming init
```
to initialize your working directory. It will automatically create a src/ folder, that will contain all your work, as well as an assets/ folder that will contain your assets (images, sounds, musics and fonts) and a data/ folder that will contains the game data, settings, database etc.
You will notice some files already existing in these folders. You can modify them, but not rename them.

### Make you own assets

You can make your assets by drawing your own characters, recording your own musics and sounds, using your pictures and downwloading some fonts. Do not forget to make your own icon as well. It must be named 'icon.ico' (you can find online converters for the format) and place in the assets/ folder.

### Make your phases and transitions

Now, it is time yo make your own phases and transitions. The files on you src/ folder are great template to start.
All your phases must be subclass of the GamePhase class (or ServerPhase class for server phases) and have a distinct name. They all need to have at least these for methods:
- `start`. This method is called when the phase is starting, it might include several arguments to initialize the phase.
- `update`. This method is called every loop iteration, and constitute the logic of the phase.
- `next`. This method is called every loop iteration and is used to know if the phase is finished. It must return '' if it is not, the name of the new phase if a new phase is to be started, or pygaming.NO_NEXT if the game is finished and the execution should be stopped.
- `end`. This method is called at the end of the phase, and should be used to release memory by deleting assets and save games.
Then, your phases must be linked by using the Transitions objects, that are subclasses of GameTransition (ServerTransition for transitions between server phases). They must have the `apply` method, which take the phase as an argument and return a dict of the argument for the start method of the new phase.
Transitions can be used to restart a phase.

### Test it

To test your game, you can freely execute your server and your game on the same device and verify that everything is working properly.

### Distribute

Once your game is working, you can build it using the command
```bash
pygaming build game name
```
This command will create an executable file (accordingly to your system) that you can give to your friends. Executing it will create one or two new executables (depending if the game is online or not), which are the game and the server.

Be carefull, some antivirus might detect your game as a virus, get in your antivirus settings to allow it.

## Contributions

Feel free to contribute to this project by adding new features or helping optimizing existing features.

## License

This software is distributed under a GNU GENERAL PUBLIC LICENSE
