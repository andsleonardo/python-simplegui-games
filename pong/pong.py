""" A Python 2 implementation of Pong. """

import simplegui as sg
import random

# CONSTANTS
WIDTH = 650
HEIGHT = 400
FONT_FAMILY = 'sans-serif'
BALL_RADIUS = 15
PAD_WIDTH = 20
PAD_HEIGHT = 80
HALF_PAD_WIDTH = PAD_WIDTH / 2
HALF_PAD_HEIGHT = PAD_HEIGHT / 2
PAD_VEL = 200 / 60
ACCEL = 1.15
VEL_LIMIT = 25
FONT_SIZE = HEIGHT / 7
SMALLER_FONT = FONT_SIZE / 3.4
LEFT = False
RIGHT = True
HEADER = "Pong"
RULES1 = "Use the keys W and S to move the left paddle"
RULES2 = "and the UP and DOWN arrows to move the right paddle"


# HELPER FUNCTIONS
def spawn_ball(direction):
    """ Reset ball's coordinates and velocity.

    Place ball in the center of the canvas and determine
    if it moves right (ball_vel[1] > 0) or left (ball_vel[1] < 0].
    """

    global ball_pos, ball_vel
    ball_pos = [WIDTH / 2, HEIGHT / 2]
    # Assign random velocity values to the ball
    ball_vel = [random.randrange(150, 200) / 60.0,
                -random.randrange(120, 160) / 60.0]
    if direction == LEFT:
        ball_vel[0] = -ball_vel[0]


# EVENT HANDLERS
def new_game():
    """ Start new game of Pong.

    Center paddles in the canvas, zero their velocities,
    reset scores and start 3-second countdown before ball spawn.
    """

    global paddle1_pos, paddle2_pos, paddle1_vel, paddle2_vel
    global countdown, score1, score2

    timer.start()

    paddle1_pos = HEIGHT / 2 - HALF_PAD_HEIGHT
    paddle2_pos = HEIGHT / 2 - HALF_PAD_HEIGHT
    paddle1_vel, paddle2_vel = 0, 0

    countdown = 5
    score1, score2 = 0, 0

    # Randomly chooses which direction the ball will move to
    direction = random.choice([LEFT, RIGHT])
    spawn_ball(direction)


def draw(canvas):
    """ Create and update elements in the canvas. """
    global paddle1_pos, paddle2_pos, paddle1_vel, paddle2_vel
    global ball_pos, ball_vel
    global countdown, score1, score2

    # Draw left gutter
    canvas.draw_line(
        [PAD_WIDTH, 0], [PAD_WIDTH, HEIGHT], 1,
        'rgba(255, 255, 255, .3)')
    # Draw right gutter
    canvas.draw_line(
        [WIDTH - PAD_WIDTH, 0], [WIDTH - PAD_WIDTH, HEIGHT], 1,
        'rgba(255, 255, 255, .3)')
    # Draw left paddle
    canvas.draw_line(
        [HALF_PAD_WIDTH, paddle1_pos],
        [HALF_PAD_WIDTH, paddle1_pos + PAD_HEIGHT],
        PAD_WIDTH, 'rgba(255, 255, 255, 1)')
    # Draw right paddle
    canvas.draw_line(
        [WIDTH - HALF_PAD_WIDTH, paddle2_pos],
        [WIDTH - HALF_PAD_WIDTH, paddle2_pos + PAD_HEIGHT],
        PAD_WIDTH, 'rgba(255, 255, 255, 1)')

    # When the countdown stop running
    if countdown <= 0:
        timer.stop()

        # Draw mid line and gutters
        canvas.draw_line(
            [WIDTH / 2, 0], [WIDTH / 2, HEIGHT], 1,
            'rgba(255, 255, 255, .3)')

        # Draw ball
        canvas.draw_circle(
            ball_pos, BALL_RADIUS, 1, '#fafafa', '#fafafa')

        # Get the left score width
        score1_width = frame.get_canvas_textwidth(
            str(score1), FONT_SIZE, FONT_FAMILY)
        # Draw left score
        canvas.draw_text(
            str(score1), [WIDTH / 2 - 30 - score1_width, 70],
            FONT_SIZE, 'rgba(255, 255, 255, 0.5)', FONT_FAMILY)
        # Draw right score
        canvas.draw_text(
            str(score2), [WIDTH / 2 + 30, 70],
            FONT_SIZE, 'rgba(255, 255, 255, 0.5)', FONT_FAMILY)

        # Update ball coordinates based on velocity vector
        ball_pos[0] += ball_vel[0]  # x
        ball_pos[1] += ball_vel[1]  # y

        # Check if the ball hits the top or the bottom of the canvas
        if ball_pos[1] <= BALL_RADIUS or ball_pos[1] + BALL_RADIUS >= HEIGHT:
            # Bounce ball back to the table
            ball_vel[1] = -ball_vel[1]

        # Check if the ball touches the left gutter
        if ball_pos[0] - BALL_RADIUS <= PAD_WIDTH:
            # Determine whether the left paddle's behind the gutter
            if int(ball_pos[1]) in range(
                    int(paddle1_pos) - 5, int(paddle1_pos) + PAD_HEIGHT + 5):
                ball_vel[0] = -ball_vel[0]
                # Accelerate only when ball_vel is under VEL_LIMIT
                if fabs(ball_vel[0]) < VEL_LIMIT:
                    ball_vel[0] = ball_vel[0] * ACCEL
            else:
                score2 += 1
                spawn_ball(RIGHT)
        # Check if the ball touches the right gutter
        elif ball_pos[0] + BALL_RADIUS >= WIDTH - PAD_WIDTH:
            # Determine whether the right paddle's behind the gutter
            if int(ball_pos[1]) in range(
                    int(paddle2_pos) - 5, int(paddle2_pos) + PAD_HEIGHT + 5):
                ball_vel[0] = -ball_vel[0]
                # Accelerate only when ball_vel is under VEL_LIMIT
                if fabs(ball_vel[0]) < VEL_LIMIT:
                    ball_vel[0] = ball_vel[0] * ACCEL
            else:
                score1 += 1
                spawn_ball(LEFT)

        # Update paddle position only if it's kept in the canvas
        if not (paddle1_pos + paddle1_vel < 0 or
                paddle1_pos + paddle1_vel > HEIGHT - PAD_HEIGHT):
            paddle1_pos += paddle1_vel
        if not (paddle2_pos + paddle2_vel < 0 or
                paddle2_pos + paddle2_vel > HEIGHT - PAD_HEIGHT):
            paddle2_pos += paddle2_vel

    # When the countdown's still running
    else:
        # Draw and center the title of the game
        header_width = frame.get_canvas_textwidth(
            HEADER, FONT_SIZE, FONT_FAMILY)
        canvas.draw_text(
            HEADER,
            [WIDTH / 2 - header_width / 2, HEIGHT / 2 - FONT_SIZE * 0.8],
            FONT_SIZE, 'rgba(255, 255, 255, 1)', FONT_FAMILY)

        # Draw and center the game's instructions
        rules_width = frame.get_canvas_textwidth(
            RULES1, SMALLER_FONT, FONT_FAMILY)
        canvas.draw_text(
            RULES1,
            [WIDTH / 2 - rules_width / 2, HEIGHT / 2 - SMALLER_FONT / 2],
            SMALLER_FONT, 'rgba(255, 255, 255, .95)', FONT_FAMILY)
        rules_width = frame.get_canvas_textwidth(
            RULES2, SMALLER_FONT, FONT_FAMILY)
        canvas.draw_text(
            RULES2,
            [WIDTH / 2 - rules_width / 2, HEIGHT / 2 + SMALLER_FONT],
            SMALLER_FONT, 'rgba(255, 255, 255, .95)', FONT_FAMILY)

        # Draw countdown in the center of the canvas
        countdown_width = frame.get_canvas_textwidth(
            str(countdown), FONT_SIZE, FONT_FAMILY)
        canvas.draw_text(
            str(countdown),
            [WIDTH / 2 - countdown_width / 2, HEIGHT / 2 + FONT_SIZE * 1.8],
            FONT_SIZE, 'rgba(255, 255, 255, 0.5)', FONT_FAMILY)


def tick():
    """ Update global countdown every second. """
    global countdown
    countdown -= 1


def keydown(key):
    global paddle1_vel, paddle2_vel
    # Left paddle
    if key == sg.KEY_MAP["w"]:
        paddle1_vel = -PAD_VEL
    elif key == sg.KEY_MAP["s"]:
        paddle1_vel = PAD_VEL
    # Right paddle
    if key == sg.KEY_MAP["up"]:
        paddle2_vel = -PAD_VEL
    elif key == sg.KEY_MAP["down"]:
        paddle2_vel = PAD_VEL


def keyup(key):
    global paddle1_vel, paddle2_vel
    # Left paddle
    if key == sg.KEY_MAP["w"]:
        paddle1_vel = 0
    elif key == sg.KEY_MAP["s"]:
        paddle1_vel = 0
    # Right paddle
    if key == sg.KEY_MAP["up"]:
        paddle2_vel = 0
    elif key == sg.KEY_MAP["down"]:
        paddle2_vel = 0

# Create frame
frame = sg.create_frame("Pong", WIDTH, HEIGHT, 100)
timer = sg.create_timer(1000, tick)
frame.set_canvas_background('#304196')
frame.add_button("Restart", new_game, 100)
frame.set_draw_handler(draw)
frame.set_keydown_handler(keydown)
frame.set_keyup_handler(keyup)

# Start frame
new_game()
frame.start()
timer.start()
