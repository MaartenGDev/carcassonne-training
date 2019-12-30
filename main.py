import random
from time import sleep
from tkinter import *
from PIL import ImageTk, Image
import cv2

cards = {
    'G_G_G_G': 4,
    'G_G_R_G': 2,
    'C_C_C_C_S': 1,
    'C_C_G_C': 3,
    'C_C_G_C_S': 1,

    'C_C_R_C': 1,
    'C_C_R_C_S': 2,
    'C_G_G_C': 3,
    'C_G_G_C_S': 2,
    'C_R_R_C': 3,

    'C_R_R_C_S': 2,
    'G_C_G_C': 1,
    'G_C_G_C_S': 2,
    'C_G_G_C_1': 2,
    'C_G_C_G': 3,

    'C_G_G_G': 5,
    'C_G_R_R': 3,
    'C_R_R_G': 3,
    'C_R_R_R': 3,
    'C_R_G_R': 4,

    'R_G_R_G': 8,
    'G_G_R_R': 9,
    'G_R_R_R': 4,
    'R_R_R_R': 1,
}

start_card_combination = 'C_R_G_R'


class Card:
    x: int
    y: int
    identifier: int
    top_side = None
    right_side = None
    bottom_side = None
    left_side = None
    combination: str

    def __init__(self, identifier: int, combination: str, x: int, y: int):
        self.x = x
        self.y = y
        self.identifier = identifier
        self.combination = combination

    @staticmethod
    def can_mount_at_side(card, other_combination: str, side: str):
        if card is None:
            return True

        other_side = Card.reverse_side(side)

        if getattr(card, side) is not None:
            return False

        return Card.get_letter_for_side(card.combination, side) == Card.get_letter_for_side(other_combination,
                                                                                            other_side)

    @staticmethod
    def get_letter_for_side(combination: str, side: str):
        sides = combination.split("_")

        if side == 'top_side':
            return sides[0]
        if side == 'right_side':
            return sides[1]
        if side == 'bottom_side':
            return sides[2]
        if side == 'left_side':
            return sides[3]

    def possible_mount_sides(self, other_combination: str, used_cards):
        sides = self.combination.split("_")
        provided_sides = other_combination.split("_")

        card_top_left = self.find_card_on_coordinates(used_cards, self.x - 1, self.y + 1)
        card_top_top = self.find_card_on_coordinates(used_cards, self.x, self.y + 2)
        card_top_right = self.find_card_on_coordinates(used_cards, self.x + 1, self.y + 1)

        card_left_left = self.find_card_on_coordinates(used_cards, self.x - 2, self.y)
        card_bottom_left = self.find_card_on_coordinates(used_cards, self.x - 1, self.y - 1)

        card_right_top = self.find_card_on_coordinates(used_cards, self.x + 1, self.y + 1)
        card_right_right = self.find_card_on_coordinates(used_cards, self.x + 2, self.y)
        card_right_bottom = self.find_card_on_coordinates(used_cards, self.x + 1, self.y - 1)

        card_bottom_bottom = self.find_card_on_coordinates(used_cards, self.x, self.y - 2)

        possible_sides = []

        # + = card to place
        # - = current card
        # * = other spots with matching sides

        #   *
        # * + *
        #   -
        if sides[0] == provided_sides[2] and self.top_side is None:
            if Card.can_mount_at_side(card_top_left, other_combination, 'right_side') and Card.can_mount_at_side(
                    card_top_top, other_combination, 'bottom_side') and Card.can_mount_at_side(card_top_right,
                                                                                               other_combination,
                                                                                               'left_side'):
                possible_sides.append('top_side')

        #   *
        # - + *
        #   *
        if sides[1] == provided_sides[3] and self.right_side is None:
            if Card.can_mount_at_side(card_right_top, other_combination, 'bottom_side') and Card.can_mount_at_side(
                    card_right_right, other_combination, 'left_side') and Card.can_mount_at_side(card_right_bottom,
                                                                                                 other_combination,
                                                                                                 'top_side'):
                possible_sides.append('right_side')

        #   -
        # * + *
        #   *
        if sides[2] == provided_sides[0] and self.bottom_side is None:
            if Card.can_mount_at_side(card_right_bottom, other_combination, 'left_side') and Card.can_mount_at_side(
                    card_bottom_bottom, other_combination, 'top_side') and Card.can_mount_at_side(card_bottom_left,
                                                                                                  other_combination,
                                                                                                  'right_side'):
                possible_sides.append('bottom_side')

        #   *
        # * + -
        #   *
        if sides[3] == provided_sides[1] and self.left_side is None:
            if Card.can_mount_at_side(card_top_left, other_combination, 'bottom_side') and Card.can_mount_at_side(
                    card_left_left, other_combination, 'right_side') and Card.can_mount_at_side(card_bottom_left,
                                                                                                other_combination,
                                                                                                'top_side'):
                possible_sides.append('left_side')

        return possible_sides

    def find_card_on_coordinates(self, used_cards, x, y):
        return next((card for card in used_cards if card.x == x and card.y == y), None)

    @staticmethod
    def reverse_side(side: str):
        if side is 'top_side':
            return 'bottom_side'
        if side is 'bottom_side':
            return 'top_side'
        if side is 'left_side':
            return 'right_side'
        if side is 'right_side':
            return 'left_side'

    @staticmethod
    def get_offset(side: str):
        if side is 'top_side':
            return 0, 1
        if side is 'bottom_side':
            return 0, -1
        if side is 'left_side':
            return -1, 0
        if side is 'right_side':
            return 1, 0


class Game:
    session_count = 0
    tile_size = 92
    canvas = None
    base_card = None
    used_cards = []
    card_usage = cards.copy()
    preview = None
    images = []
    card_id = 0
    window_width = 21 * tile_size
    has_options_left = True
    iteration = 1

    tries_per_cards_left = {}
    max_tries = 30

    def __init__(self, master):
        self.master = master
        self.canvas = Canvas(master, width=self.window_width, height=self.window_width / 2, bd=0, highlightthickness=0)
        self.canvas.grid(row=1, column=1)

        self.stats_canvas = Canvas(self.canvas, width=self.window_width, height=10)
        self.stats_canvas.grid(row=2, column=1)
        self.images_canvas = Canvas(self.canvas, width=self.window_width, height=self.window_width / 2 - 10)
        self.images_canvas.grid(row=3, column=1)

        self.master.after(2, self.improve)

    def play_card(self):
        prev_cards_left = self.cards_left()

        if self.base_card is None:
            self.card_id += 1
            self.base_card = Card(self.card_id, start_card_combination, 0, 0)

            self.used_cards.append(self.base_card)
            self.card_usage[start_card_combination] -= 1
        else:
            possible_cards = list(filter(lambda key: self.card_usage[key] > 0, self.card_usage))

            if len(possible_cards) == 0:
                return

            chosen_card_combination = random.choice(possible_cards)
            self.card_id += 1

            for card in self.used_cards:
                mount_sides = card.possible_mount_sides(chosen_card_combination, self.used_cards)
                if len(mount_sides) > 0:
                    chosen_mount_side = random.choice(mount_sides)
                    offset_x, offset_y = Card.get_offset(chosen_mount_side)
                    chosen_card = Card(self.card_id, chosen_card_combination, card.x + offset_x, card.y + offset_y)

                    self.used_cards.append(chosen_card)

                    setattr(card, chosen_mount_side, chosen_card)
                    setattr(chosen_card, Card.reverse_side(chosen_mount_side), card)

                    self.card_usage[chosen_card_combination] -= 1
                    break

        if prev_cards_left != self.cards_left():
            self.images = []
            for child in self.images_canvas.winfo_children():
                child.destroy()

            self.iteration += 1

            top_card = self.get_top_card(self.base_card)
            left_card = self.get_most_left_card(self.used_cards)
            self.draw_board(top_card, self.iteration, left_card.x, top_card.y, [], [])
        else:
            if prev_cards_left not in self.tries_per_cards_left.keys():
                self.tries_per_cards_left[prev_cards_left] = 0

            self.tries_per_cards_left[prev_cards_left] += 1

            if self.tries_per_cards_left[prev_cards_left] > self.max_tries:
                self.has_options_left = False

    def cards_left(self):
        return len(list(filter(lambda key: self.card_usage[key] > 0, self.card_usage)))

    def play(self, on_finished = None):
        self.play_card()

        if len(list(filter(lambda key: self.card_usage[key] > 0, self.card_usage))) == 0:
            self.has_options_left = False

        if self.has_options_left:
            self.canvas.after(1, lambda: self.play(on_finished))

        if not self.has_options_left and on_finished is not None:
            print("Finished!")
            on_finished()

    def get_most_left_card(self, used_cards):
        most_left_card = None
        for card in used_cards:
            if most_left_card is None or card.x < most_left_card.x:
                most_left_card = card

        return most_left_card

    def get_top_card(self, card: Card):
        if card is None or card.top_side is None:
            return card

        return self.get_top_card(card.top_side)

    def draw_board(self, card: Card, iteration: int, lowest_x: int, highest_y: int, shown_ids, used_coords):
        if card is None or card.identifier in shown_ids:
            return

        if len(shown_ids) == 0:
            w = Label(self.stats_canvas, text="Session: %i" % self.session_count)
            w.grid(row=1, column=1)

        img = cv2.putText(cv2.imread('./tiles/' + card.combination + '.png'), "", (0, 20), cv2.FONT_HERSHEY_COMPLEX,
                          0.4, (0, 0, 0))

        b, g, r = cv2.split(img)
        img = cv2.merge((r, g, b))

        image = ImageTk.PhotoImage(Image.fromarray(img))
        self.images.append(image)

        x = abs(lowest_x) + card.x if card.x >= 0 else abs(lowest_x) - abs(card.x)
        y = abs(highest_y) + abs(card.y) if card.y <= 0 else abs(highest_y) - abs(card.y)

        x = x * self.tile_size
        y = y * self.tile_size

        self.images_canvas.create_image((x, y), image=image, anchor='nw')

        if (str(card.x) + '-' + str(card.y)) in used_coords:
            print("Double coord!")

        shown_ids.append(card.identifier)
        used_coords.append(str(card.x) + '-' + str(card.y))

        if card.right_side is not None:
            self.draw_board(card.right_side, iteration, lowest_x, highest_y, shown_ids, used_coords)

        if card.left_side is not None:
            self.draw_board(card.left_side, iteration, lowest_x, highest_y, shown_ids, used_coords)

        if card.bottom_side is not None:
            self.draw_board(card.bottom_side, iteration, lowest_x, highest_y, shown_ids, used_coords)

    def improve(self):
        print("Starting iteration!")
        sleep(0.5)
        self.session_count += 1

        self.base_card = None
        self.has_options_left = True
        self.used_cards = []
        self.tries_per_cards_left = {}
        self.iteration = 0
        self.card_id = 0
        self.card_usage = cards.copy()

        self.images = []
        self.play(lambda: self.improve())


root = Tk()
app = Game(root)
root.mainloop()
