# pygaming
This project aims to be an exhaustive and easy-to-use set of module to create video games. Based on pygame for the screen, sounds and inputs, it also provides widgets, frames, database management, file management, logging, basic LAN, key mapping, menus, lobbies, ...

## Features

- Input manager: The input manager is based on pygame but provide the option of key mapping to allow the player to have a complete choice on the key use.
- Sound manager: The sound manager is based on pygame but provide easier classes to manager efficiently the sounds and the musics of the game.
- Screen manager: The screen manager is based on pygame but provide several additional features to improve the game:
  - Frames
  - Widgets: Buttons, Entries, Labels, Overlays, Comboboxes.
  - Videos
  - Actors
  - Menus
  - Focus manager
- Database manager: The database manager is based on sqlite3 and provide easy-to-use methods to query the database
- Player and Server: abstract base classes for the player and the server.
- LAN connexion: The direct use of the Server and Client classes to make several player interact together.
- Phase manager.
- Logger.
