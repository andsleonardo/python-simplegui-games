""" Gamified stopwatch that counts up to 10 minutes in Python 2.
Try to stop the count on whole seconds to score points. """

import simplegui as sg

# Constants
CTRLA_WIDTH = 85
CANVAS_WIDTH = 300
CANVAS_HEIGHT = 200
CANVAS_FONT_FAMILY = 'serif'
STOPWATCH_FONT_SIZE = 60
SCORE_FONT_FAMILY = 'sans-serif'
SCORE_FONT_SIZE = 16

# Global variables
tenths, total, correct = 0, 0, 0

# Create frame
frame = sg.create_frame('Stopwatch', CANVAS_WIDTH, CANVAS_HEIGHT, CTRLA_WIDTH)

# Helper functions
def format_time(tenths):
    """ Format count with a:bc.d style. """
    a, b, c, d = 0, 0, 0, tenths
    if tenths > 9:
        c = tenths / 10
        d = str(d)[-1]
    if c > 9:
        b = c / 10
        c = str(c)[-1]
    if b > 5:
        a = str(b / 6)
        b = str(b % 6)
    return "%s:%s%s.%s" % (a, b, c, d)

def get_score(total, correct):
    """ Return score made by sucessful/total stops. """
    return "%i / %i" % (correct, total)

def pt2px(points):
    """ Convert points to pixels. """
    return (points * 72) / 96

def abs_center():
    """ Return coordinates to absolutely center align the stopwatch. """

    # Pixels occupied by the counter on the canvas
    stopwatch_text_width = frame.get_canvas_textwidth(
        format_time(tenths), STOPWATCH_FONT_SIZE, CANVAS_FONT_FAMILY)

    hor_pos = (CANVAS_WIDTH - stopwatch_text_width) / 2
    vert_pos = (CANVAS_HEIGHT / 2) + (pt2px(STOPWATCH_FONT_SIZE) / 2)
    return [hor_pos, vert_pos]

def top_right_align():
    """ Return coordinates to align the score on the top right. """
    hor_pos = (CANVAS_WIDTH * 0.75)
    vert_pos = (CANVAS_HEIGHT * 0.2)
    return [hor_pos, vert_pos]

# Event handlers
def draw(canvas):
    """ Insert elements to the canvas. """
    canvas.draw_text(format_time(tenths), abs_center(),
                     STOPWATCH_FONT_SIZE, '#fafafa', CANVAS_FONT_FAMILY)
    canvas.draw_text(get_score(total, correct), top_right_align(),
                     SCORE_FONT_SIZE, '#aaa', SCORE_FONT_FAMILY)

def start():
    """ Initiate count. """
    timer.start()

def stop():
    """ If running, stop count and update score. """
    global score, total, correct
    if timer.is_running() == True:
        timer.stop()
        total += 1
        if tenths % 10 == 0:
            correct += 1

def reset():
    """ Stop and restart stopwatch. """
    global tenths, total, correct
    if timer.is_running() == True:
        timer.stop()
    tenths, total, correct = 0, 0, 0

def count():
    """ Set stopwatch count. """
    global tenths
    tenths += 1

# Create timer
timer = sg.create_timer(100, count)

# Register event handlers
frame.set_canvas_background('#333')
frame.set_draw_handler(draw)
frame.add_button('Start', start, CTRLA_WIDTH)
frame.add_label('')
frame.add_button('Stop', stop, CTRLA_WIDTH)
frame.add_label('')
frame.add_button('Reset', reset, CTRLA_WIDTH)

# Start frame
frame.start()
