import pygaming as pgg
import numpy as np

LOBBY = "lobby"
PLAYGROUND = "playground"


class SettingsFrame(pgg.Frame):

    def __init__(self, master: pgg.GamePhase):

        bg = pgg.art.ColoredRectangle(pgg.Color("#fff"), 400, 600, border_radius=10,
                transformation=pgg.art.transformation.DrawRectangle(
                    pgg.Color('black'),
                    (200, 300), 400, 600, 8, 0, 10
            )
        )

        super().__init__(master, bg.to_window(master.config.dimension[0]//2, master.config.dimension[1]//2, pgg.anchors.CENTER), bg)

        self.validate_button = pgg.widget.TextButton(
            self,
            self.width//2, 5*self.height//6,
            pgg.art.ColoredRectangle(pgg.Color('#444'), 3*self.width//4, self.master.typewriter.get_linesize("default_bold") + 8),
            "default_bold",
            pgg.Color("white"),
            'LOC_VALIDATE_SETTINGS',
            on_unclick_command=self.update_settings,
            anchor=pgg.anchors.CENTER
        )
        self.fullscreen = master.settings.fullscreen
        self.fullscreen_button = pgg.widget.TextButton(
            self,
            self.width//2, 1*self.height//6,
            pgg.art.ColoredRectangle(pgg.Color('#444'), 8*self.width//9, self.master.typewriter.get_linesize("default_bold") + 8),
            "default_bold",
            pgg.Color("white"),
            'LOC_FULLSCREEN_ON' if self.fullscreen else 'LOC_FULLSCREEN_OFF',
            on_unclick_command=self.toggle_fullscreen,
            anchor=pgg.anchors.CENTER
        )

        self.language = master.settings.language
        self.language_button = pgg.widget.TextButton(
            self,
            self.width//2, 2*self.height//6,
            pgg.art.ColoredRectangle(pgg.Color('#444'), 8*self.width//9, self.master.typewriter.get_linesize("default_bold") + 8),
            "default_bold",
            pgg.Color("white"),
            'LOC_LANGUAGE_EN' if self.language == 'en_US' else 'LOC_LANGUAGE_FR',
            on_unclick_command=self.toggle_language,
            anchor=pgg.anchors.CENTER

        )
        self.controls = master.settings.controls['playground']['K_RIGHT'] == 'right' # True if normal, False is inverted
        self.controls_button = pgg.widget.TextButton(
            self,
            self.width//2, 3*self.height//6,
            pgg.art.ColoredRectangle(pgg.Color('#444'), 8*self.width//9, self.master.typewriter.get_linesize("default_bold") + 8),
            "default_bold",
            pgg.Color("white"),
            'LOC_CONTROLS_NORMAL' if self.controls else 'LOC_CONTROLS_INVERTED',
            on_unclick_command=self.toggle_controls,
            anchor=pgg.anchors.CENTER

        )

    def init_values(self):
        self.fullscreen = self.master.settings.fullscreen
        self.language = self.master.settings.language
        self.controls = self.master.settings.controls['K_RIGHT'] == 'right' # True if normal, False is inverted
        self.fullscreen_button.set_localization_or_text('LOC_FULLSCREEN_ON' if self.fullscreen else 'LOC_FULLSCREEN_OFF')
        self.controls_button.set_localization_or_text('LOC_CONTROLS_NORMAL' if self.controls else 'LOC_CONTROLS_INVERTED')
        self.language_button.set_localization_or_text('LOC_LANGUAGE_EN' if self.language == 'en_US' else 'LOC_LANGUAGE_FR')

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.fullscreen_button.set_localization_or_text('LOC_FULLSCREEN_OFF' if self.fullscreen else 'LOC_FULLSCREEN_ON')

    def toggle_language(self):
        self.language = {'en_US' : 'fr_FR', 'fr_FR' : 'en_US'}[self.language]
        self.language_button.set_localization_or_text('LOC_LANGUAGE_EN' if self.language == 'en_US' else 'LOC_LANGUAGE_FR')

    def toggle_controls(self):
        self.controls = not self.controls
        self.controls_button.set_localization_or_text('LOC_CONTROLS_NORMAL' if self.controls else 'LOC_CONTROLS_INVERTED')

    def update_settings(self):
        self.master.settings.set_fullscreen(self.fullscreen)
        self.master.settings.set_language(self.language)
        if self.controls:
            self.master.settings.set_controls({"K_LEFT": "left", "K_RIGHT": "right", "K_ESCAPE": "pause"}, PLAYGROUND)
        else:
            self.master.settings.set_controls({"K_RIGHT": "left", "K_LEFT": "right", "K_ESCAPE": "pause"}, PLAYGROUND)

        self.game.update_settings()
        self.master.notify_change_all() # Update all the elements of the game so the new settings are taken into account.

        self.master.pause()

class LobbyGamePhase(pgg.GamePhase):
    """The first phase of the game is offline and consists on chosing a color."""

    def __init__(self, game: pgg.Game):
        super().__init__(LOBBY, game)
        WINDOW_WIDTH, WINDOW_HEIGHT = game.config.dimension

        self.is_ready = False # is changed to True when the validation button is clicked.

        # Create the phase's frame.

        background_color = pgg.Color("#999") # The color of the background of our main frame
        initial_color = [
            pgg.Color(255, 0, 0), pgg.Color(0, 0, 255), pgg.Color(0, 255, 0), pgg.Color(255, 255, 0),
            pgg.Color(255, 0, 255), pgg.Color(0, 255, 255), pgg.Color(255, 255, 255), pgg.Color(0, 0, 0)
        ][np.random.randint(0, 8)] # This phase is about selecting a color, we set the initial value as a random
        # among : blue, red, green, magenta, yellow, cyan, black and white.
        self.current_color = initial_color

        # We will display the current color in this rectangle.
        self.selected_color_displayer_area = ((WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 130), 200, 100)
        
        # We create the background: it is a coloredractangle, of the same size than the game window.
        # We draw the initial color on it
        self.background = pgg.art.ColoredRectangle(
            background_color,
            WINDOW_WIDTH,
            WINDOW_HEIGHT,
            transformation=pgg.art.transformation.DrawRectangle(
                initial_color,
                *self.selected_color_displayer_area
            )
        )

        # We want to add a mask on the frame. This mask is a binary mask based on the alpha value
        # of a colored rectangle with rounded angles.
        window_mask = pgg.mask.FromArtAlpha(
            pgg.art.ColoredRectangle((0, 0, 0), WINDOW_WIDTH, WINDOW_HEIGHT, 0, 50)
        )
        # The window has the same size than the frame, and starts in (0, 0).
        # The window has a mask, which effect is DARKEN: 10%
        window = pgg.Window(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, mask = window_mask, mask_effects={pgg.mask.DARKEN : 10})

        # We create the frame, with the window defined above and the background as its art.
        self.frame = pgg.Frame(
            self,
            window,
            self.background
        )

        # We create the label and the entry to select a name
        LABEL_SIZE = (300, self.typewriter.get_linesize("default_bold") + 4)
        LABEL_POSITION = (50, 50)
        
        self.name_label = pgg.widget.Label(
            self.frame,
            pgg.art.ColoredRectangle((0, 0, 0, 0), *LABEL_SIZE),
            "default_bold",
            (0, 0, 0, 255),
            'LOC_SELECT_NAME',
            *LABEL_POSITION,
            justify=pgg.anchors.CENTER_RIGHT
        )

        self.name_entry = pgg.widget.Entry(
            self.frame,
            LABEL_POSITION[0] + LABEL_SIZE[0] + 10,
            LABEL_POSITION[1],
            pgg.art.ColoredRectangle((255, 255, 255, 255), *LABEL_SIZE),
            "default_bold",
            (0, 0, 0, 255),
            None,
            None,
            justify=pgg.anchors.CENTER_LEFT,
            max_length=25,
            forbid_characters=" ',?"
        )

        # Create the color sliders

        self.slider_label = pgg.widget.Label(
            self.frame,
            pgg.art.ColoredRectangle((0, 0, 0, 0), *LABEL_SIZE),
            "default_bold",
            (0, 0, 0, 255),
            'LOC_SELECT_COLOR',
            x = WINDOW_WIDTH//2,
            y=WINDOW_HEIGHT//2 - LABEL_SIZE[1] - 10,
            justify=pgg.anchors.CENTER,
            anchor=pgg.anchors.TOP_CENTER
        )

        # We define the basic colors and we darken them by 10%.
        # The light color will be used for the background of the sliders when it is not focused.
        # the dark color for the background of theslider when it is focused
        red = pgg.Color('red')
        dark_red = red.darken(10)
        green = pgg.Color('green')
        dark_green = green.darken(10)
        blue = pgg.Color('blue')
        dark_blue = blue.darken(10)
        white = pgg.Color("white")
        grey = white.darken(10)

        # We define some constant for the position of the sliders.
        SLIDER_WIDTH = 180
        SLIDER_HEIGHT = 50
        SLIDER_PAD = 30

        # For each color, we create the rounded rectangle that will be the background of the sliders.
        red_slider_bg = pgg.art.ColoredRectangle(red, SLIDER_WIDTH, SLIDER_HEIGHT, border_radius=SLIDER_HEIGHT//2)
        red_slider_fbg = pgg.art.ColoredRectangle(dark_red, SLIDER_WIDTH, SLIDER_HEIGHT, border_radius=SLIDER_HEIGHT//2)

        green_slider_bg = pgg.art.ColoredRectangle(green, SLIDER_WIDTH, SLIDER_HEIGHT, border_radius=SLIDER_HEIGHT//2)
        green_slider_fbg = pgg.art.ColoredRectangle(dark_green, SLIDER_WIDTH, SLIDER_HEIGHT, border_radius=SLIDER_HEIGHT//2)

        blue_slider_bg = pgg.art.ColoredRectangle(blue, SLIDER_WIDTH, SLIDER_HEIGHT, border_radius=SLIDER_HEIGHT//2)
        blue_slider_fbg = pgg.art.ColoredRectangle(dark_blue, SLIDER_WIDTH, SLIDER_HEIGHT, border_radius=SLIDER_HEIGHT//2)

        # We also create the cursors of the sliders
        slider_cursor = pgg.art.ColoredCircle(white, SLIDER_HEIGHT//2, 7)
        slider_cursor_focused = pgg.art.ColoredCircle(grey, SLIDER_HEIGHT//2, 9)

        # We create the slider.
        self.red_slider = pgg.widget.Slider(
            master=self.frame, # The frame in which this slider is placed.
            x=WINDOW_WIDTH//2 - SLIDER_WIDTH//2 - SLIDER_WIDTH - SLIDER_PAD,
            y=WINDOW_HEIGHT//2, # x,y: the coordinate of the top left of the slider in the frame.
            values=range(0, 256), # The accepted values for the red parameter: an integer from 0 to 255
            normal_background=red_slider_bg, # The background when the slider is not focused
            normal_cursor=slider_cursor.copy(), # The cursor when the slider is not focused
            initial_value=initial_color.r, # the initial value
            focused_background=red_slider_fbg,
            focused_cursor=slider_cursor_focused.copy()
        )
        # Here, we use .copy() to individualize each cursor, as the same art object is also used in the other widgets.
        # Now, if we want to modify the cursor, we can, it will not affect the copy.
        # In this specific case, we don't modify the cursor more and we only have one image, so copying is not mandatory.

        self.green_slider = pgg.widget.Slider(
            self.frame,
            WINDOW_WIDTH//2,
            WINDOW_HEIGHT//2,
            range(0, 256),
            green_slider_bg,
            slider_cursor.copy(),
            initial_color.g,
            green_slider_fbg,
            slider_cursor_focused.copy(),
            anchor=pgg.anchors.TOP_CENTER
        )

        self.blue_slider = pgg.widget.Slider(
            self.frame,
            WINDOW_WIDTH//2 + SLIDER_WIDTH//2 + SLIDER_PAD,
            WINDOW_HEIGHT//2,
            range(0, 256),
            blue_slider_bg,
            slider_cursor.copy(),
            initial_color.b,
            blue_slider_fbg,
            slider_cursor_focused.copy()
        )

        # Create the validation button

        button_bg = pgg.art.ColoredEllipse(white, 100, 50) # The button to validate is an Ellipse, this is its background
        button_focus_bg = button_bg.copy(pgg.art.transformation.DrawEllipse(grey.lighten(5), 100, 50, (100, 50), 3)) # We duplicate the background to add a grey unfilled ellipsis on top for when it is focused

        self.button = pgg.widget.TextButton( # We create the validation button
            self.frame, # Its master is once again the frame
            WINDOW_WIDTH//2,
            WINDOW_HEIGHT//2 + 100,
            button_bg, # Its background is the ellipse
            "default_big", # The font used to display the text in this button
            (0, 0, 0, 255), # The color of the font: black
            'LOC_LETS_PLAY', # The localization to display.
            None, # When the button is clicked, it will display the same background as when it is not.
            button_focus_bg, # When the button is focused but not clicked, its background is different
            anchor=pgg.anchors.TOP_CENTER, # We use an anchor to not specify the top left via x,y but to specify the top center.
            active_area=pgg.mask.FromArtAlpha(button_bg), # We don't want to be able to click in the rectangle outside of the ellipse so we specify the active area.
            # This is the standard behavior if active_area=None is passed instead.
            on_click_command=self.set_ready # The command to be executed when the button is clicked
        )

        self.settings_frame = SettingsFrame(self)
        self.settings_frame.hide()

        self.settings_button = pgg.widget.TextButton(
            self.frame,
            WINDOW_WIDTH, 0,
            pgg.art.ColoredRectangle(grey.darken(10), 200, self.typewriter.get_linesize("default") + 4),
            "default",
            white, 'LOC_SETTINGS',
            anchor=pgg.anchors.TOP_RIGHT,
            on_click_command=self.show_settings
        )

    def show_settings(self):
        self.settings_frame.show()
        self.button.disable()

    def pause(self):
        self.settings_frame.hide()
        self.button.enable()

    def set_ready(self):
        self.is_ready = True # When the button is clicked, this flag is set to True

    def next(self):
        if self.is_ready: # Which mean we are ready to go to the game
            return PLAYGROUND
        else: # If we are not ready, we just stay here.
            return pgg.STAY
    
    def apply_transition(self, next_phase):
        # The input for the next phase are red, green and blue and name. The values for these arguments are generated here.
        return {'red' : self.current_color.r, 'green' : self.current_color.g, 'blue' : self.current_color.b, 'name': self.name_entry.get()}
    
    def end(self):
        if self.is_ready:
            self.logger.write({"Color chosen" : {'red' : self.current_color.r, 'green' : self.current_color.g, 'blue' : self.current_color.b}})
        # At the end of the phase, if we leave becasue we are ready to join the playground and not because we asked to quit the game, we log what color
        # we chose. These log can be used later to compute some stats for example. 

    def start(self):
        self.is_ready = False
        self.settings_frame.hide()

    def update(self, loop_duration: int):
        if self.current_color.r != self.red_slider.get() or self.current_color.g != self.green_slider.get() or self.current_color.b != self.blue_slider.get():
            # If the player used the sliders to change the color he want to play with.
            self.current_color = pgg.Color(self.red_slider.get(), self.green_slider.get(), self.blue_slider.get()) # We have a new color
            self.background.transform(pgg.art.transformation.DrawRectangle( # We draw on the are a square of this color.
                self.current_color,
                *self.selected_color_displayer_area
            ), self.settings)
            self.logger.write({"Color changed" : {'red' : self.current_color.r, 'green' : self.current_color.g, 'blue' : self.current_color.b}}, True)
            # Only in debugging mode, we log the color that we just selected.

class Pawn(pgg.Actor):

    def __init__(self, color: pgg.Color, frame: pgg.Frame):

        PAWN_SIZE = 40, 40

        main_surface = pgg.art.ColoredRectangle(
            color, *PAWN_SIZE, border_bottom_left_radius=PAWN_SIZE[1]//2, border_bottom_right_radius=PAWN_SIZE[1]//2,
        )
        super().__init__(frame, main_surface, 0, 0, anchor=pgg.anchors.TOP_CENTER, layer=1)
    
    def update(self, loop_duration):
        pass # For this specific case, we don't need to update anything as we use always the same art

    def make_surface(self):
        return  self.main_surface.get(self.game.settings, None)

    def start(self):
        pass

    def end(self):
        pass

class Player:

    def __init__(self, color: pgg.Color, pawn: Pawn, frame: pgg.Frame, initial_score: int, name: str, rank: int):
        self.color = color
        self.pawn = pawn
        self._height = frame.game.typewriter.get_linesize("default") + 10
        self.name = name
        self.name_label = pgg.widget.Label(
            frame,
            pgg.art.ColoredRectangle((0, 0, 0, 0), 100, self._height),
            "default",
            color,
            name,
            0,
            rank*self._height,
            justify=pgg.anchors.CENTER_LEFT
        )

        self.score_label = pgg.widget.Label(
            frame,
            pgg.art.ColoredRectangle((0, 0, 0, 0), frame.game.typewriter.size("default", "1000")[0] + 10, self._height),
            "default",
            self.color,
            str(initial_score),
            100,
            rank*self._height,
            justify=pgg.anchors.CENTER_LEFT
        )
        self.score = initial_score

    def update_score(self, new_score: int):
        self.score = new_score
        self.score_label.set_localization_or_text(str(self.score))

    def update_rank(self, new_rank: str):
        self.name_label.move(None, self._height*new_rank, None)
        self.score_label.move(None, self._height*new_rank, None)


class PlaygroundGamePhase(pgg.GamePhase):

    def __init__(self, game):
        super().__init__(PLAYGROUND, game)

        # Initialize the game data
        self.players: dict[str, Player] = {}
        self.asked_to_leave = False

        # Create the background where the game is displayed

        background_color = pgg.Color('white')
        grid_color = pgg.Color('grey')
        grid_frequency = 7
        grid_thickness = 1

        WINDOW_WIDTH, WINDOW_HEIGHT = self.config.dimension

        DrawGridTransformation = pgg.art.transformation.Pipeline(*[
            pgg.art.transformation.DrawLine(grid_color, (0, i*WINDOW_HEIGHT//grid_frequency), (WINDOW_WIDTH, i*WINDOW_HEIGHT//grid_frequency), grid_thickness)
            for i in range(1, grid_frequency)
        ], *[
            pgg.art.transformation.DrawLine(grid_color, (i*WINDOW_WIDTH//grid_frequency, 0), (i*WINDOW_WIDTH//grid_frequency, WINDOW_HEIGHT), grid_thickness)
            for i in range(1, grid_frequency)
        ])


        background = pgg.art.ColoredRectangle(
            background_color,
            WINDOW_WIDTH,
            WINDOW_HEIGHT,
            transformation=DrawGridTransformation
        )

        self.frame = pgg.Frame(
            self,
            background.to_window(0, 0),
            background
        )

        # Create the pause frame

        pause_bg = pgg.art.ColoredRectangle(pgg.Color("#fff"), 200, 400, border_radius=10,
                transformation=pgg.art.transformation.DrawRectangle(
                    pgg.Color('black'),
                    (100, 200), 200, 400, 8, 0, 10
            )
        )

        self.pause_frame = pgg.Frame(
            self.frame,
            pause_bg.to_window(WINDOW_WIDTH//2, WINDOW_HEIGHT//2, pgg.anchors.CENTER),
            pause_bg,
            layer=2 # set to 2 to be displayed on top of the pawns, whose layers are 1.
        )

        BUTTONS_DIMENSION = (180, 50)

        resume_button = pgg.widget.TextButton(
            self.pause_frame,
            self.pause_frame.width//2, self.pause_frame.height//4,
            pgg.art.ColoredRectangle(pgg.Color('red').darken(30), *BUTTONS_DIMENSION),
            "default_bold",
            pgg.Color('white'),
            'LOC_RESUME',
            on_click_command=self.resume,
            anchor=pgg.anchors.CENTER
        )

        return_button = pgg.widget.TextButton(
            self.pause_frame,
            self.pause_frame.width//2, self.pause_frame.height//2,
            pgg.art.ColoredRectangle(pgg.Color('blue').darken(30), *BUTTONS_DIMENSION),
            "default_bold",
            pgg.Color('white'),
            'LOC_RETURN',
            on_click_command=self.ask_to_leave,
            anchor=pgg.anchors.CENTER
        )

        settings_button = pgg.widget.TextButton(
            self.pause_frame,
            self.pause_frame.width//2, 3*self.pause_frame.height//4,
            pgg.art.ColoredRectangle(pgg.Color('green').darken(30), *BUTTONS_DIMENSION),
            "default_bold",
            pgg.Color('white'),
            'LOC_SETTINGS',
            on_click_command=self.show_settings,
            anchor=pgg.anchors.CENTER
        )

        self.settings_frame = SettingsFrame(self)

    def ask_to_leave(self):
        self.asked_to_leave = True
        self.game.client.send("action", "disconnection")

    def next(self):
        return "lobby" if self.asked_to_leave else pgg.STAY
    
    def end(self):
        self.players = {}
        self.frame.children.clear() # remove all children (labels and pawns) of players.

    def start(self, red, blue, green, name):
        self.game.connect()
        self.players = {}
        self.game.client.send('new_player', {'red' : red, 'blue' : blue, 'green' : green, 'name': name})

        # (Re)init the game.
        self.players.clear()
        self.asked_to_leave = False
        self.pause_frame.hide()
        self.settings_frame.hide()

    def apply_transition(self, next_phase):
        return {} # We can only transition to the lobby which require no arguments.

    def get_rank(self, player: Player):
        return sum([1 for pl in self.players.values() if pl.score > player.score])

    def update(self, loop_duration):
         # Update the position and score of all the pawns based on the last data

        if self.game.client.last_receptions:
            last_data = self.game.client.last_receptions[-1]
            self.game.client.clean_last()

            if last_data[pgg.HEADER] == 'game_update':
                payload = last_data[pgg.PAYLOAD]
                names_to_delete = []
                for player in self.players.values(): # For all existing player
                    if player.name in payload: # If this player is still playing
                        player.update_score(payload[player.name]['score']) # update its score
                    else:
                        names_to_delete.append(player.name)
                for name in names_to_delete:
                    del self.players[name]

                for player_name in payload: # add the new player to the players dict.
                    if player_name not in self.players:
                        color = pgg.Color(payload[player_name]['red'], payload[player_name]['green'], payload[player_name]['blue'])
                        pawn = Pawn(color, self.frame)
                        self.players[player_name] = Player(color, pawn, self.frame, payload[player_name]['score'], player_name, len(self.players) + 1)

                for player in self.players.values(): # update the score and the position of the players
                    rank = self.get_rank(player)
                    player.update_rank(rank)
                    player.pawn.move(payload[player.name]['x'], payload[player.name]['y'])
                    self.notify_change()

        if not self.pause_frame.visible and not self.settings_frame.visible: # Otherwise it means that we are in pause.

            # send the data to the server
            if self.keyboard.actions_pressed.get('left'):

                self.game.client.send("action", "left")
            if self.keyboard.actions_pressed.get('right'):
                self.game.client.send("action", "right")

        # Interact with the pause
        if self.keyboard.actions_down.get('pause') and not self.settings_frame.visible:
            if self.pause_frame.visible:
                self.resume()
            else:
                self.pause()

    def resume(self):
        self.pause_frame.hide()

    def pause(self):
        self.pause_frame.show()
        self.settings_frame.hide()

    def show_settings(self):
        self.settings_frame.show()
        self.pause_frame.hide()

g = pgg.Game(LOBBY, debug=False) # Instantiate the game
LobbyGamePhase(g) # Instantiate each phases
PlaygroundGamePhase(g)
g.run() # Run the game