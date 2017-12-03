""" Python 2 implementation of RiceRocks, an updated version of
Atari's Asteroids game, by @andsnleo. Art assets: Kim Lathrop
(free re-use in non-commercial projects w/ credit).
Sound assets: sounddogs.com (no redistribution).
"""

import simplegui as sg
import math
import random

# Constants for UI
WIDTH, HEIGHT = 800, 600
CTRLA = 160  # Control area width
PADDING = 10
OFFSET = PADDING * 6
FONT_SIZE_SMALL = 11
FONT_SIZE_BIG = 60
FONT_FAMILY = "sans-serif"
FONT_COLOR = "rgba(255, 255, 255, 1)"

# Useful global
started = False

# Game mechanics constants
ANG_VEL = .03
ACCELERATION = .035
FRICTION = .0085


class ImageInfo:
    def __init__(self, center, size, radius=0, lifespan=None, animated=False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated


# DEBRIS IMAGES : debris1_brown.png, debris2_brown.png, debris3_brown.png,
# debris4_brown.png, debris1_blue.png, debris2_blue.png, debris3_blue.png,
# debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = sg.load_image(
    "http://commondatastorage.googleapis.com/"
    "codeskulptor-assets/lathrop/debris4_blue.png")

# NEBULA IMAGES: nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = sg.load_image(
    "http://commondatastorage.googleapis.com/"
    "codeskulptor-assets/lathrop/nebula_brown.png")

# SPLASH IMAGE
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = sg.load_image(
    "http://commondatastorage.googleapis.com/"
    "codeskulptor-assets/lathrop/splash.png")

# SHIP IMAGE
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = sg.load_image(
    "http://commondatastorage.googleapis.com/"
    "codeskulptor-assets/lathrop/double_ship.png")

# MISSILE IMAGES: shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5, 5], [10, 10], 2, 50)
missile_image = sg.load_image(
    "http://commondatastorage.googleapis.com/"
    "codeskulptor-assets/lathrop/shot2.png")

# ASTEROID IMAGES: asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = sg.load_image(
    "http://commondatastorage.googleapis.com/"
    "codeskulptor-assets/lathrop/asteroid_blend.png")

# ANIMATED EXPLOSIONS: explosion_orange.png, explosion_blue.png,
# explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = sg.load_image(
    "http://commondatastorage.googleapis.com/"
    "codeskulptor-assets/lathrop/explosion_alpha.png")

# Sound assets
soundtrack = sg.load_sound(
    "http://commondatastorage.googleapis.com/"
    "codeskulptor-assets/sounddogs/soundtrack.mp3")
soundtrack.set_volume(.75)
missile_sound = sg.load_sound(
    "http://commondatastorage.googleapis.com/"
    "codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.3)
ship_thrust_sound = sg.load_sound(
    "http://commondatastorage.googleapis.com/"
    "codeskulptor-assets/sounddogs/thrust.mp3")
ship_thrust_sound.set_volume(.5)
explosion_sound = sg.load_sound(
    "http://commondatastorage.googleapis.com/"
    "codeskulptor-assets/sounddogs/explosion.mp3")


# Helper functions
def deg_to_rad(ang):
    """ Convert degrees to radians. """
    return ang * (math.pi / 180)


def angle_to_vector(ang):
    """ Given an angle, get its x and y vectors. """
    return [math.cos(ang), math.sin(ang)]


def dist(p, q):
    """ Compute the distance between two points. """
    return math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)


def process_sprite_group(group, canvas):
    for sprite in group:
        if sprite.update():
            group.discard(sprite)
        sprite.draw(canvas)
        sprite.update()


def group_collide(group, other_group):
    global sprites
    collision_count = 0

    for sprite in group:
        for other_sprite in other_group:
            if sprite.collide(other_sprite):
                collision_count += 1
                explosion = Sprite(
                    sprite.get_position(), [0, 0], 0, 0,
                    explosion_image, explosion_info, explosion_sound)
                sprites["explosions"].add(explosion)
                group.discard(sprite)
                if type(sprite) is type(other_sprite):
                    other_group.discard(other_sprite)

    return True if collision_count > 0 else False


# Ship class
class Ship:

    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0], pos[1]]
        self.vel = [vel[0], vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()

    def get_position(self):
        return self.pos

    def get_radius(self):
        return self.radius

    def draw(self, canvas):
        if self.thrust:
            canvas.draw_image(
                self.image,
                [self.image_center[0] + self.image_size[0],
                 self.image_center[1]],
                self.image_size, self.pos, self.image_size, self.angle)
        else:
            canvas.draw_image(
                self.image, self.image_center, self.image_size,
                self.pos, self.image_size, self.angle)

    def update(self):
        # update angle
        self.angle += self.angle_vel

        # update position
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT

        # update velocity
        if self.thrust:
            acc = angle_to_vector(self.angle)
            self.vel[0] += acc[0] * ACCELERATION
            self.vel[1] += acc[1] * ACCELERATION

        # Update Ship's velocity accounting the friction
        self.vel[0] *= (1 - FRICTION)
        self.vel[1] *= (1 - FRICTION)

    def thrusters_on(self):
        self.thrust = True
        ship_thrust_sound.rewind()
        ship_thrust_sound.play()

    def thrusters_off(self):
        self.thrust = False
        ship_thrust_sound.pause()

    def increment_angle_vel(self):
        self.angle_vel += ANG_VEL

    def decrement_angle_vel(self):
        self.angle_vel -= ANG_VEL

    def shoot(self):
        global sprites
        forward = angle_to_vector(self.angle)
        missile_pos = [
            self.pos[0] + self.radius * forward[0],
            self.pos[1] + self.radius * forward[1]]
        missile_vel = [
            self.vel[0] + 6 * forward[0], self.vel[1] + 6 * forward[1]]
        a_missile = Sprite(
            missile_pos, missile_vel, self.angle, 0,
            missile_image, missile_info, missile_sound)
        sprites["missiles"].add(a_missile)


# Sprite class
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound=None):
        self.pos = [pos[0], pos[1]]
        self.vel = [vel[0], vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        if sound:
            sound.rewind()
            sound.play()

    def draw(self, canvas):
        if self.animated:
            self.image_center = [64, 64]
            self.image_center[0] += self.image_size[0] * self.age
        canvas.draw_image(
            self.image, self.image_center, self.image_size,
            self.pos, self.image_size, self.angle)

    def update(self):
        # update angle
        self.angle += self.angle_vel

        # update position
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT

        self.age += 1
        return True if self.age > self.lifespan else False

    def get_position(self):
        return self.pos

    def get_radius(self):
        return self.radius

    def collide(self, other_object):
        collision = self.radius + other_object.get_radius() > \
            dist(self.pos, other_object.get_position())
        return True if collision else False


# Key handlers to control ship
def keydown(inp):
    global sprites, P1_COMMANDS, started
    for key, command in P1_COMMANDS.items():
        if started and inp == sg.KEY_MAP[key] and command[0] is not None:
            command[0]()


def keyup(inp):
    global sprites, P1_COMMANDS, started
    for key, command in P1_COMMANDS.items():
        if started and inp == sg.KEY_MAP[key] and command[1] is not None:
            command[1]()


# Mouseclick handlers that reset UI
# and conditions whether splash image is drawn
def click(pos):
    global started
    center = [WIDTH / 2, HEIGHT / 2]
    size = splash_info.get_size()
    inwidth = (center[0] - size[0] / 2) < pos[0] < (center[0] + size[0] / 2)
    inheight = (center[1] - size[1] / 2) < pos[1] < (center[1] + size[1] / 2)
    if (not started) and inwidth and inheight:
        started = True


def draw(canvas):
    global sprites
    global time, score, lives, started

    # Backgrond animation
    time += 1
    wtime = (time / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()

    canvas.draw_image(
        nebula_image, nebula_info.get_center(), nebula_info.get_size(),
        [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(
        debris_image, center, size,
        (wtime - WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_image(
        debris_image, center, size,
        (wtime + WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))

    # Draw and update sprites
    for collection in sprites.values():
        process_sprite_group(collection, canvas)

    # Draw splash screen if not started
    if not started:
        canvas.draw_image(
            splash_image, splash_info.get_center(),
            splash_info.get_size(), [WIDTH / 2, HEIGHT / 2],
            splash_info.get_size())
    else:
        # Check for collisions
        if group_collide(sprites["rocks"], sprites["ships"]):
            lives -= 1
        elif group_collide(sprites["rocks"], sprites["missiles"]):
            score += 1

        # Reset game when player's out of lives
        if lives == 0:
            ship_thrust_sound.rewind()
            started = False
            new_game()

        # Get important measures for UI text
        lives_text_width = frame.get_canvas_textwidth(
            "LIVES", FONT_SIZE_SMALL, FONT_FAMILY)
        lives_num_width = frame.get_canvas_textwidth(
            "%i" % (lives), FONT_SIZE_BIG, FONT_FAMILY)
        score_text_width = frame.get_canvas_textwidth(
            "SCORE", FONT_SIZE_SMALL, FONT_FAMILY)
        score_num_width = frame.get_canvas_textwidth(
            "%i" % (score), FONT_SIZE_BIG, FONT_FAMILY)

        # Draw lives remaining
        canvas.draw_text(
            "LIVES", [OFFSET * 2, OFFSET],
            FONT_SIZE_SMALL, FONT_COLOR, FONT_FAMILY)
        canvas.draw_text(
            "%i" % (lives),
            [OFFSET * 2 + (lives_text_width - lives_num_width) / 2,
             OFFSET - PADDING / 2 + FONT_SIZE_BIG],
            FONT_SIZE_BIG, FONT_COLOR, FONT_FAMILY)

        # Draw score
        canvas.draw_text(
            "SCORE", [WIDTH - OFFSET * 2 - score_text_width, OFFSET],
            FONT_SIZE_SMALL, FONT_COLOR, FONT_FAMILY)
        canvas.draw_text(
            "%i" % (score),
            [WIDTH - OFFSET * 2 - (score_text_width + score_num_width) / 2,
             PADDING * 11.5], FONT_SIZE_BIG, FONT_COLOR, FONT_FAMILY)


# Timer handler that spawns a rock
def rock_spawner():
    global sprites
    if started and len(sprites["rocks"]) < 12:
        rock_pos = [random.randrange(0, WIDTH), random.randrange(0, HEIGHT)]
        rock_vel = [random.random() * .6 - .3, random.random() * .6 - .3]
        rock_avel = random.random() * .03

        # Recalculate the rock's position if the ship's too close
        for ship in sprites["ships"]:
            while dist(rock_pos, ship.get_position()) < 150:
                rock_pos = [random.randrange(0, WIDTH),
                            random.randrange(0, HEIGHT)]

        # Create new instance of rock Sprite
        a_rock = Sprite(
            rock_pos, rock_vel, 0, rock_avel,
            asteroid_image, asteroid_info)
        sprites["rocks"].add(a_rock)


def new_game():
    global sprites
    global score, lives, time

    # Reset globals
    lives, score, time = 3, 0, 0
    # Play the game's soundtrack
    soundtrack.rewind()
    soundtrack.play()

    # Initialize collection of sprites
    sprites = {
        "ships": [], "rocks": set(), "missiles": set(), "explosions": set()}

    # Initialize ship and two sprites
    my_ship = Ship(
        [WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
    sprites["ships"].append(my_ship)
    set_key_commands()


def set_key_commands():
    global P1_COMMANDS
    P1_COMMANDS = {
        "up": (sprites["ships"][0].thrusters_on,
               sprites["ships"][0].thrusters_off),
        "left": (sprites["ships"][0].decrement_angle_vel,
                 sprites["ships"][0].increment_angle_vel),
        "right": (sprites["ships"][0].increment_angle_vel,
                  sprites["ships"][0].decrement_angle_vel),
        "space": (sprites["ships"][0].shoot, None)}

# Create frame
frame = sg.create_frame("Asteroids", WIDTH, HEIGHT, CTRLA)

# Register handlers
frame.set_keyup_handler(keyup)
frame.set_keydown_handler(keydown)
frame.set_mouseclick_handler(click)
frame.set_draw_handler(draw)

timer = sg.create_timer(1000, rock_spawner)

# Get things rolling
timer.start()
frame.start()
new_game()
