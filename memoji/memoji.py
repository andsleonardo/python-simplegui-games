import simplegui as sg
import random
import math

# Load sprites
TILE_DOWN = sg.load_image(
    "//googledrive.com/host/0B1NYWkyBivJsSFlHQklyaVE4Nk0")
CAKE = sg.load_image(
    "//googledrive.com/host/0B1NYWkyBivJsQTdCOVNnZFF5cjA")
HAPPY = sg.load_image(
    "//googledrive.com/host/0B1NYWkyBivJsalM0RV9QX05oYUU")
HIFIVE = sg.load_image(
    "//googledrive.com/host/0B1NYWkyBivJsWUpwcVFCTzJaT1k")
MAGIC8 = sg.load_image(
    "//googledrive.com/host/0B1NYWkyBivJseEM1djRQVy1BV1k")
MONKEY = sg.load_image(
    "//googledrive.com/host/0B1NYWkyBivJsSFpkMm9MX0RSeE0")
PARTY = sg.load_image(
    "//googledrive.com/host/0B1NYWkyBivJseGZwOEJhd0l6TmM")
PIG = sg.load_image(
    "//googledrive.com/host/0B1NYWkyBivJsYlhzWGgxYmJjUWc")
STAR = sg.load_image(
    "//googledrive.com/host/0B1NYWkyBivJsRU5tdkdtZDU5Z2s")

# Tiles traits
DISTINCT_TILES = 8
TILE_WIDTH, TILE_HEIGHT = 100, 150  # 100px x 150px tiles
TILE_DIV = 10  # Space between cards

# Canvas and frame traits
CNV_WIDTH, CNV_HEIGHT = 990, 580  # Canvas dimensions
CTRLA = 160  # Control Area width
VER_PADDING = 100  # Vertical padding
HOR_PADDING = TILE_DIV + TILE_WIDTH / 2  # Horizontal padding
BIGGER_FONT_SIZE = 60
SMALLER_FONT_SIZE = 17

# In-game messages
TITLE = {"text": "MEMOJI", "width": None}
TAGLINE = "Pair emojis by clicking on the cards below"
INFO = "Made with Twitter emojis (twitter.github.io/twemoji)"
CONGRATS = {"text": "Yay! You made it! "
            "Hit 'Shuffle cards' if you want to try again.",
            "width": None}

# Global variables
turns, record = 0, 0


class Tile:
    def __init__(self, img, exp, loc):
        self.img_object = img
        self.exposed = exp
        self.location = loc

    def get_img(self):
        """ Returns the image object of the tile. """
        return self.img_object

    def is_exposed(self):
        """ Return wether the tile's image is exposed. """
        return self.exposed

    def expose_tile(self):
        """ Reveals the tile's image. """
        self.exposed = True

    def hide_tile(self):
        """ Hide the tile's image. """
        self.exposed = False

    def draw_tile(self, canvas):
        """ Draw the tile on the canvas. """
        # Check wether the tile is exposed
        if self.exposed:
            # Tile facing up
            canvas.draw_image(
                self.img_object,
                [TILE_WIDTH / 2, TILE_HEIGHT / 2],
                [TILE_WIDTH, TILE_HEIGHT],
                self.location, [TILE_WIDTH, TILE_HEIGHT])
        else:
            # Tile facing down
            canvas.draw_image(
                TILE_DOWN,
                [TILE_WIDTH / 2, TILE_HEIGHT / 2],
                [TILE_WIDTH, TILE_HEIGHT],
                self.location, [TILE_WIDTH, TILE_HEIGHT])

    def is_selected(self, pos):
        """ Check if the player clicks on a tile.

        Return True only if a tile contains
        the coordinates (pos[0], pos[1]) of the mouse click.
        """
        inside_hor = self.location[0] - TILE_WIDTH / 2 <= \
            pos[0] <= self.location[0] + TILE_WIDTH / 2
        inside_ver = self.location[1] - TILE_HEIGHT / 2 <= \
            pos[1] <= self.location[1] + TILE_WIDTH / 2
        return inside_hor and inside_ver


def new_game():
    """ Start a new game of Memoji. """
    global my_tiles, flipped, turns

    # Get text width of TITLE and CONGRATS messages
    TITLE["width"] = frame.get_canvas_textwidth(
        TITLE["text"], BIGGER_FONT_SIZE, "sans-serif")
    CONGRATS["width"] = frame.get_canvas_textwidth(
        CONGRATS["text"], SMALLER_FONT_SIZE, "sans-serif")

    emojis = [CAKE, HAPPY, HIFIVE, MAGIC8, MONKEY, PARTY, PIG, STAR] * 2
    random.shuffle(emojis)

    flipped = 0  # Keep track of the game's state
    turns = 0
    tries.set_text("Turns: %i" % turns)
    rec.set_text("Your record: %i" % record)

    my_tiles = []
    for i, emj in enumerate(emojis, 1):
        # 1st tile's position
        loc = [TILE_DIV + TILE_WIDTH, TILE_DIV + TILE_HEIGHT]
        if i % DISTINCT_TILES != 0:
            column = i % DISTINCT_TILES
        else:
            column = DISTINCT_TILES
        row = math.ceil(i / float(DISTINCT_TILES))
        loc[0] *= column
        loc[1] = loc[1] * row + (VER_PADDING / 1.5)
        my_tiles.append(Tile(emj, False, loc))


def draw(canvas):
    global my_tiles, record, turns

    # Draw game's TITLE, INFO and TAGLINE
    canvas.draw_text(
        TITLE["text"],
        [HOR_PADDING, VER_PADDING],
        BIGGER_FONT_SIZE, "#fafafa", "monospace")
    canvas.draw_text(
        INFO,
        [HOR_PADDING + TITLE["width"], VER_PADDING - SMALLER_FONT_SIZE * 1.25],
        SMALLER_FONT_SIZE, "#rgba(255, 255, 255, .5)", "sans-serif")
    canvas.draw_text(
        TAGLINE,
        [HOR_PADDING + TITLE["width"], VER_PADDING],
        SMALLER_FONT_SIZE, "#rgba(255, 255, 255, .5)", "sans-serif")

    for tile in my_tiles:
        tile.draw_tile(canvas)

    exposed = [tile.is_exposed() for tile in my_tiles]

    # Check whether the player paired all tiles
    if False not in exposed:
        # Draw CONGRATS message
        canvas.draw_text(
            CONGRATS["text"],
            [CNV_WIDTH / 2 - CONGRATS["width"] / 2,
                CNV_HEIGHT - VER_PADDING / 2],
            SMALLER_FONT_SIZE, "#rgba(255, 255, 255, .5)", "sans-serif")
        # Update the player's guesses record
        if record == 0 or turns < record:
            record = turns


def click(pos):
    global my_tiles, flipped, turns, turn1_tile, turn2_tile
    for tile in my_tiles:
        if tile.is_selected(pos):
            if not tile.is_exposed():
                if flipped == 0:
                    flipped = 1
                    # Store first tile for further comparison
                    turn1_tile = tile
                elif flipped == 1:
                    flipped = 2
                    turns += 1
                    tries.set_text("Turns: %i" % turns)
                    # Store second tile tile for further comparison
                    turn2_tile = tile
                else:
                    if turn1_tile.get_img() != turn2_tile.get_img():
                        # Hide both emojis previously revealed
                        turn1_tile.hide_tile()
                        turn2_tile.hide_tile()
                    # Store emoji for further comparison
                    flipped = 1
                    turn1_tile = tile
                # Reveal emoji
                tile.expose_tile()


# Create frame
frame = sg.create_frame("Memoji", CNV_WIDTH, CNV_HEIGHT, CTRLA)

# Register event handlers
frame.set_canvas_background("#38754f")
frame.add_label("Compete w/ friends by "
                "keeping track of your turns below.", CTRLA)
frame.add_label("")
tries = frame.add_label("Turns: %i" % turns, CTRLA)
rec = frame.add_label("Your record: %i" % record, CTRLA)
frame.add_label("")
frame.add_label("")
frame.add_button("Shuffle cards", new_game, CTRLA)
frame.set_draw_handler(draw)
frame.set_mouseclick_handler(click)

# Initialization
frame.start()
new_game()
