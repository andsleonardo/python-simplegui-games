""" A Python 2 Blackjack implementation for a single player.
In this version of the game, which contains betting mechanics
to keep track of the player's score, the dealer wins ties.
Made by @andsnleo. """

import simplegui as sg
import random
import math

# Dimensions and spacing for drawing
CNV_WIDTH, CNV_HEIGHT = 650, 425  # Canvas
CTRLA = 120  # Control Area width
PADDING = 10
OFFSET = PADDING * 3.5

# Alignments for drawing
TOP_ALIGN = LEFT_ALIGN = OFFSET
BOTTOM_ALIGN = CNV_HEIGHT - OFFSET
RIGHT_ALIGN = CNV_WIDTH - OFFSET
CENTER_ALIGN = (CNV_WIDTH / 2, CNV_HEIGHT / 2)

# Text attributes
FONT_SIZE_SMALLER = 11
FONT_SIZE_SMALL = 14
FONT_SIZE_NORMAL = 20
FONT_SIZE_BIG = 30
FONT_COLOR = "#FAFAFA"
FONT_FAMILY = "sans-serif"
TEXT_DIV = 5

# Load 230x51 Blackjack title (Source: @andsnleo)
BLACKJACK_TITLE = sg.load_image(
    "https://github.com/andsnleo/python-simplegui-games/blob/master/blackjack/assets/blackjack-title.png?raw=true")
TITLE_SIZE = (230, 51)
TITLE_CENTER = (TITLE_SIZE[0] / 2, TITLE_SIZE[1] / 2)

# Load 936x384 deck sprite (Source: jfitz.com)
CARD_SIZE = (72, 96)
CARD_CENTER = (36, 48)
card_images = sg.load_image(
    "http://storage.googleapis.com/codeskulptor-assets/cards_jfitz.png")

# Load 71x96 card back sprite (Source: jfitz.com)
CARD_BACK_SIZE = (71, 96)
CARD_BACK_CENTER = (36, 48)
card_back = sg.load_image(
    "https://github.com/andsnleo/python-simplegui-games/blob/master/blackjack/assets/blackjack-card-back.png?raw=true")

# Define globals for cards
SUITS = ('C', 'S', 'H', 'D')
RANKS = ('A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K')
VALUES = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
          '8': 8, '9': 9, 'T': 10, 'J': 10, 'Q': 10, 'K': 10}


# Classes
class Card:
    def __init__(self, suit, rank):
        if (suit in SUITS) and (rank in RANKS):
            self.suit = suit
            self.rank = rank
        else:
            self.suit = None
            self.rank = None
            print "Invalid card: ", suit, rank

    def __str__(self):
        """ String representation of Card. """
        return self.suit + self.rank

    def get_suit(self):
        """ Return the suit of Card. """
        return self.suit

    def get_rank(self):
        """ Return the rank of Card. """
        return self.rank

    def draw(self, canvas, pos):
        """ Draw Card in the canvas. """
        # Get card location in the 52-card sprite
        card_loc = (CARD_CENTER[0] + CARD_SIZE[0] * RANKS.index(self.rank),
                    CARD_CENTER[1] + CARD_SIZE[1] * SUITS.index(self.suit))
        canvas.draw_image(
            card_images, card_loc, CARD_SIZE,
            pos, CARD_SIZE)


class Hand:
    def __init__(self, tag, side):
        self.hand = []
        self.tag = tag
        self.side = side

    def __str__(self):
        """ Return a string representation of a hand. """
        if len(self.hand) < 1:
            return "No cards in hand."
        else:
            output = "%s's hand contains" % (self.tag.capitalize())
            for card in self.hand:
                output += " %s" % (card)
            return output + "."

    def add_card(self, card):
        """ Add a card to Hand. """
        self.hand.append(card)

    def get_value(self):
        """ Compute the value of a hand. """
        value, aces = 0, 0
        for card in self.hand:
            value += VALUES[card.get_rank()]
            # Keep track of the aces in Hand
            if card.get_rank() == "A":
                aces += 1
        if aces >= 1 and value + 10 <= 21:
            value += 10
        return value

    def get_length(self):
        """ Return the length of Hand. """
        return len(self.hand)

    def draw(self, canvas, pos):
        """ Draw Hand in the canvas. """
        # Draw every card in Hand
        for card in self.hand:
            card.draw(canvas, pos)
            # Hide the dealer's first card until the round ends
            if (self.tag.upper() == "DEALER" and
                    self.hand.index(card) == 0 and in_play):
                canvas.draw_image(
                    card_back,
                    CARD_BACK_CENTER, CARD_BACK_SIZE,
                    pos, CARD_SIZE)
            # Update the cards' coordinates to stack them appropriately
            pos[0] -= 15 * self.side


class Deck:
    def __init__(self):
        self.deck = [Card(suit, rank) for suit in SUITS for rank in RANKS]
        self.graveyard = []

    def __str__(self):
        """ Return a string representation of Deck. """
        output = "Deck contains"
        for card in self.deck:
            output += " %s" % (card)
        return output + "."

    def shuffle(self):
        """ Shuffle the cards in Deck. """
        random.shuffle(self.deck)

    def regroup_cards(self):
        """ Take cards from the graveyard and add them back to the deck. """
        for card in self.graveyard:
            self.deck.append(card)

    def deal_card(self):
        """ Return the card on the top of Deck and add it to the graveyard. """
        dealt = self.deck.pop(-1)
        self.graveyard.append(dealt)
        return dealt

    def get_length(self):
        """ Return the length of Deck. """
        return len(self.deck)

    def draw(self, canvas, pos):
        """ Draw Deck in the canvas. """
        for card in self.deck:
            canvas.draw_image(
                card_back, CARD_BACK_CENTER,
                CARD_BACK_SIZE, pos, CARD_BACK_SIZE)


class Player:
    def __init__(self, name, side, cash=200):
        self.name = name
        self.cash = cash
        self.corner = side

    def set_new_hand(self):
        """ Create a new hand for Player and return it. """
        self.hand = Hand(self.name, self.corner)
        return self.hand

    def get_cash(self):
        """ Return the amount of money Player has. """
        return self.cash

    def add_cash(self, num):
        """ Given a value num, add it to Player's cash. """
        self.cash += num

    def spend_cash(self, num):
        """ Given a value num, decrease it from Player's cash. """
        self.cash -= num
        return self.cash > num

    def draw(self, canvas):
        """ Draw Player's info in the canvas. """
        # Hide the dealer's total until the round ends
        if self.name.upper() == "DEALER" and in_play:
            value = "Total: ?"
        elif not start:
            value = "Total: 0"
        else:
            value = "Total: %i" % (self.hand.get_value())

        line = 1
        for text in [value, self.name]:
            if self.corner == 1:  # Right side of the table
                align = RIGHT_ALIGN - frame.get_canvas_textwidth(
                    text.upper(), FONT_SIZE_SMALLER, FONT_FAMILY)
            else:
                align = LEFT_ALIGN  # Left side of the table
            canvas.draw_text(
                text.upper(),
                [align, CENTER_ALIGN[1] - CARD_CENTER[1] - PADDING * line],
                FONT_SIZE_SMALLER, FONT_COLOR, FONT_FAMILY)
            line += 1.5


# Initiliaze some useful globals
start, in_play = False, False
total_bet, dealer_bet = 0, 0
bottom_alert = "Press 'Deal' to start a new game."

# Table traits
INITIAL_BET = entry_bet = 8
RAISES = [10, 15, 20]

# Create Player and Deck objects
player = Player("player", 1)
dealer = Player("dealer", -1, None)
bjack_deck = Deck()


def deal():
    global bjack_deck, player, player_hand, dealer_hand
    global total_bet, dealer_bet, entry_bet
    global start, in_play, enough_money
    global bottom_alert

    bottom_alert = ""  # Resets the bottom_alert field

    # Update the "Raise" buttons according to the player's cash
    for index, button in enumerate(RAISE_BUTTONS):
        if player.get_cash() >= 165:
            button.set_text(
                "Raise $%i" % (RAISES[index] * player.get_cash() / 165))

    if player.get_cash() >= entry_bet:
        start = True
        enough_money = True
        total_bet, dealer_bet = 0, 0

        # Player pays the entry bet and the dealer covers it
        player.spend_cash(entry_bet)
        dealer_bet += entry_bet
        total_bet += entry_bet * 2

        # Make sure the deck never runs out of cards
        if bjack_deck.get_length() < 14:
            bjack_deck.regroup_cards()
        bjack_deck.shuffle()

        # Start new hands for the player and the dealer
        player_hand, dealer_hand = player.set_new_hand(), dealer.set_new_hand()
        # Handle two cards for each player
        while (player_hand.get_length(), dealer_hand.get_length) < (2, 2):
            player_hand.add_card(bjack_deck.deal_card())
            dealer_hand.add_card(bjack_deck.deal_card())

        in_play = True  # Defines a playing round

    elif not enough_money:
        if not in_play:
            bottom_alert = "Oops, you don't have enough money!"
            "Better luck next time."
        else:
            bottom_alert = "Maybe you should try hitting or standing?"


def hit():
    global bjack_deck, player_hand, dealer_hand
    global start, in_play, bottom_alert

    if in_play:
        player_hand.add_card(bjack_deck.deal_card())
        # Player busts
        if player_hand.get_value() > 21:
            bottom_alert = (
                "You bust with %i and lose $%i. "
                "But, hey, don't give up!"
                % (player_hand.get_value(), dealer_bet))
            in_play = False
    elif not in_play and start:
        bottom_alert = (
            "Hey, you can't hit right now. "
            "'Deal' if you want to gamble more.")


def stand():
    global bjack_deck, player_hand
    global start, in_play, bottom_alert

    if in_play:
        # Add remaining cards to the dealer's hand
        while dealer_hand.get_value() <= 17:
            dealer_hand.add_card(bjack_deck.deal_card())
        in_play = False

        # Dealer busts
        if dealer_hand.get_value() > 21:
            player.add_cash(total_bet)
            bottom_alert = (
                "The dealer busts with %i and you take $%i. New deal?"
                % (dealer_hand.get_value(), dealer_bet))
        # Compare the values of both hands
        elif dealer_hand.get_value() <= 21:
            if player_hand.get_value() > dealer_hand.get_value():
                player.add_cash(total_bet)
                bottom_alert = (
                    "Yay! You earn $%i with %i points! "
                    "Another turn?"
                    % (dealer_bet, player_hand.get_value()))
            elif player_hand.get_value() < dealer_hand.get_value():
                bottom_alert = (
                    "The dealer wins with %i. Bye bye, $%i. "
                    "Another deal?"
                    % (dealer_hand.get_value(), dealer_bet))
            else:
                bottom_alert = (
                    "It's a tie! The dealer wins this round, "
                    "and you lose %i."
                    % (dealer_bet))
    elif not in_play and start:
        bottom_alert = (
            "This turn's already ended. "
            "Press 'Deal' if you want another one.")


def draw(canvas):
    global bjack_deck, total_bet, entry_bet
    global start, in_play, enough_money, bottom_alert

    # Raise the next round's entry bet according to the player's cash
    if player.get_cash() > 0 and player.get_cash() % 200 == 0:
        entry_bet = INITIAL_BET * player.get_cash() / 200

    if start:
        # Check if the player has enough money to play a round
        if player.get_cash() < entry_bet:
            enough_money = False

        # Hands's coordinates in the canvas
        dealer_cards_pos = [LEFT_ALIGN + CARD_CENTER[0], CNV_HEIGHT / 2]
        player_cards_pos = [RIGHT_ALIGN - CARD_CENTER[0],
                            CNV_HEIGHT / 2]
        # Draw the cards in the hands
        dealer_hand.draw(canvas, dealer_cards_pos)
        player_hand.draw(canvas, player_cards_pos)

        if in_play:
            canvas.draw_text(
                "Hit or stand?",
                [OFFSET + TITLE_SIZE[0] + PADDING * 3, OFFSET + TITLE_SIZE[1]],
                FONT_SIZE_NORMAL, "rgba(255, 255, 255, 0.5)", FONT_FAMILY)
    elif not start or not in_play:
        total_bet = 0

    # Draw the game's custom title
    canvas.draw_image(
        BLACKJACK_TITLE, TITLE_CENTER, TITLE_SIZE,
        [OFFSET + TITLE_CENTER[0], OFFSET + TITLE_CENTER[1]],
        TITLE_SIZE)

    # Center the deck in the canvas and draw its cards facing down
    deck_pos = [CNV_WIDTH / 2, CNV_HEIGHT / 2]
    bjack_deck.draw(canvas, deck_pos)

    # Draw the players' name and total points
    player.draw(canvas)
    dealer.draw(canvas)

    # Display the amount of cash bet in the round
    canvas.draw_text(
        "Winner takes:",
        [LEFT_ALIGN, CENTER_ALIGN[1] +
            CARD_CENTER[1] + PADDING * 7 - FONT_SIZE_BIG - TEXT_DIV],
        FONT_SIZE_SMALL, FONT_COLOR, FONT_FAMILY)
    canvas.draw_text(
        "$%i" % (total_bet),
        [LEFT_ALIGN, CENTER_ALIGN[1] + CARD_CENTER[1] + PADDING * 7],
        FONT_SIZE_BIG, FONT_COLOR, FONT_FAMILY)
    # Display the game's entry bet
    canvas.draw_text(
        "Next entry bet:",
        [CENTER_ALIGN[0] - frame.get_canvas_textwidth(
            "Next entry bet:", FONT_SIZE_SMALL, FONT_FAMILY) / 2,
         CENTER_ALIGN[1] + CARD_CENTER[1] +
         PADDING * 7 - FONT_SIZE_BIG - TEXT_DIV],
        FONT_SIZE_SMALL, FONT_COLOR, FONT_FAMILY)
    canvas.draw_text(
        "$%i" % (entry_bet),
        [CENTER_ALIGN[0] - frame.get_canvas_textwidth(
            "$%i" % (entry_bet), FONT_SIZE_BIG, FONT_FAMILY) / 2,
         CENTER_ALIGN[1] + CARD_CENTER[1] + PADDING * 7],
        FONT_SIZE_BIG, FONT_COLOR, FONT_FAMILY)
    # Display the player's total cash
    canvas.draw_text(
        "Your cash:",
        [RIGHT_ALIGN - frame.get_canvas_textwidth(
            "Your cash:", FONT_SIZE_SMALL, FONT_FAMILY),
         CENTER_ALIGN[1] + CARD_CENTER[1] +
         PADDING * 7 - FONT_SIZE_BIG - TEXT_DIV],
        FONT_SIZE_SMALL, FONT_COLOR, FONT_FAMILY)
    canvas.draw_text(
        "$%i" % (player.get_cash()),
        [RIGHT_ALIGN - frame.get_canvas_textwidth(
            "$%i" % (player.get_cash()), FONT_SIZE_BIG, FONT_FAMILY),
         CENTER_ALIGN[1] + CARD_CENTER[1] + PADDING * 7],
        FONT_SIZE_BIG, FONT_COLOR, FONT_FAMILY)

    # Display the bottom_alert field in the the canvas
    canvas.draw_text(
        bottom_alert,
        [CENTER_ALIGN[0] - frame.get_canvas_textwidth(
            bottom_alert, FONT_SIZE_NORMAL, FONT_FAMILY) / 2,
         BOTTOM_ALIGN],
        FONT_SIZE_NORMAL, "rgba(255, 255, 255, 0.5)", FONT_FAMILY)


def raise_bet(value):
    """ Add value to the table's total amount of bets.

    This value is deduced from the player's total cash
    if they have enough money to bet and the round is rolling.
    """

    global total_bet, dealer_bet, in_play, bottom_alert
    if value > player.get_cash() or not in_play:
        bottom_alert = "You cannot bet $%i right now." % (value)
    elif in_play:
        player.spend_cash(value)
        dealer_bet += value
        total_bet += value * 2
        bottom_alert = ""


# More button event handlers
def raise1():
    """ Raise bet.

    This button event handler calls the raise_bet() function
    with the custom value taken from the first "Raise" button text.
    """

    value = int(RAISE_BUTTONS[0].get_text().split(" $")[1])
    raise_bet(value)


def raise2():
    """ Raise bet.

    This button event handler calls the raise_bet() function
    with the custom value taken from the second "Raise" button text.
    """

    value = int(RAISE_BUTTONS[1].get_text().split(" $")[1])
    raise_bet(value)


def raise3():
    """ Raise bet.

    This button event handler calls the raise_bet() function
    with the custom value taken from the third "Raise" button text.
    """

    value = int(RAISE_BUTTONS[2].get_text().split(" $")[1])
    raise_bet(value)


def all_in():
    """ Bet all of the player's money.

    This button event handler calls the raise_bet()
    function with value=player.get_cash().
    """

    raise_bet(player.get_cash())


def magic_cash():
    """ Add $100 to the player's cash. """
    global bottom_alert
    if not in_play:
        player.add_cash(200)
        bottom_alert = ""
    else:
        bottom_alert = "You can only do this between turns."


# Initializate frame with green (#38754f) canvas
frame = sg.create_frame("Blackjack", CNV_WIDTH, CNV_HEIGHT, CTRLA)
frame.set_canvas_background("#38754f")

# Create buttons, labels and canvas callback
frame.set_draw_handler(draw)
frame.add_button("Deal", deal, CTRLA)
frame.add_button("Hit", hit, CTRLA)
frame.add_button("Stand", stand, CTRLA)
frame.add_label("")
frame.add_label("Up your game:")
frame.add_label("")
RAISE_BUTTONS = [
    frame.add_button("Raise $%i" % (RAISES[0]), raise1, CTRLA),
    frame.add_button("Raise $%i" % (RAISES[1]), raise2, CTRLA),
    frame.add_button("Raise $%i" % (RAISES[2]), raise3, CTRLA)]
frame.add_button("All-in", all_in, CTRLA)
frame.add_label("")
frame.add_label("Cheat the game:")
frame.add_label("")
frame.add_button("Get more cash", magic_cash, CTRLA)

# Get things rolling
frame.start()
