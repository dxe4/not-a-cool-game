from kivy.app import App
from kivy.core.window import Window
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Rectangle
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.config import Config
from itertools import starmap
import random
from copy import copy

def fibonacci(max_iter):
    a, b = 1, 1
    for i in range(0, max_iter):
        yield a
        a, b = b, a + b


moves = {
    "left": (-1, 0),
    "right": (1, 0),
    "up": (0, 1),
    "down": (0, -1)
}
BOX_SIZE = 100
fib_numbers = [i for i in fibonacci(20)]


class InvalidMove(Exception):
    pass


class DrawableMixIn(object):
    def __init__(self, x, y, label, color):
        self.old_pos = None
        self.pos = (x, y)
        self.label = label
        self.color = color
        self.drawn = False

    def _move(self, pos_diff, free_boxes_pos):
        x_diff, y_diff = pos_diff
        new_pos = self.x + x_diff * BOX_SIZE, self.y + y_diff * BOX_SIZE

        if new_pos not in free_boxes_pos:
            raise InvalidMove

        self.old_pos = copy(self.pos)
        self.pos = new_pos
        self.draw()

    def draw(self):
        # Avoid garbage collection to draw them...
        self._rec_color = Color(*self.color)
        self._rec = Rectangle(pos=self.pos, size=(BOX_SIZE, BOX_SIZE))
        self._label_color = Color(0, 0, 0)
        self._label = Label(text=self.label, font_size=15, pos=self.pos)
        self.drawn = True
        self._clean_old_pos()

    def _clean_old_pos(self):
        if not self.old_pos:
            return
        Color(0, 0, 0, 1)
        Rectangle(pos=self.old_pos, size=(BOX_SIZE, BOX_SIZE))
        self.old_pos = None

    @property
    def x(self):
        return self.pos[0]

    @property
    def y(self):
        return self.pos[1]


class Box(DrawableMixIn):
    def __eq__(self, other):
        if not isinstance(other, Box):
            return False
        return other.pos == self.pos and other.label == self.label

    def __hash__(self):
        return hash((self.pos, self.label))


class Player(DrawableMixIn):
    def __init__(self, x, y, label, color):
        super(Player, self).__init__(x, y, label, color)


    def move(self, occupied_boxes, free_boxes_pos, pos_diff):
        x_diff, y_diff = pos_diff
        new_pos = self.x + x_diff * BOX_SIZE, self.y + y_diff * BOX_SIZE

        try:
            self._move(pos_diff, free_boxes_pos)
        except InvalidMove:
            pass
        try:
            box_to_move = next((i for i in occupied_boxes if new_pos == i.pos))
            box_to_move._move(pos_diff, free_boxes_pos)
            self._move(pos_diff, [new_pos])
        except (StopIteration, InvalidMove):
            raise InvalidMove("Cant move to {}".format(new_pos))


class NotACoolGame(Widget):
    def setup_keyboard(self):
        self._keyboard = Window.request_keyboard(
            self._keyboard_closed, self, 'text')
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        try:
            pos_diff = moves[keycode[1]]
        except KeyError:
            # key pressed if not key in (up,down,left,right)
            return
        try:
            with self.canvas:
                self.player.move(self.boxes, self.free_boxes_pos, pos_diff)
        except InvalidMove as e:
            pass

    def make_player(self, all_boxes):
        rand_int = random.randint(0, len(all_boxes))
        rand_box = self.all_boxes[rand_int]
        return Player(rand_box.x, rand_box.y, "player", (1, 0, 0))

    def setup(self):
        self.count = 0
        H, W = starmap(Config.getint, (("graphics", i) for i in ("height", "width")))

        self.all_boxes = [Box(i, j, str(random.sample(fib_numbers, 1)[0]), (0, 0, 1))
                          for i in range(0, H, BOX_SIZE)
                          for j in range(0, W, BOX_SIZE)]
        self.boxes = set()

        self.player = self.make_player(self.all_boxes)
        self.setup_keyboard()

    @property
    def free_boxes_pos(self):
        return [i.pos for i in self.free_boxes]

    @property
    def free_boxes(self):
        occupied = [i.pos for i in self.boxes]
        occupied.append(self.player.pos)
        return [i for i in self.all_boxes if i.pos not in occupied]

    def random_box(self):
        if not self.free_boxes:
            return
        new_box = copy(random.sample(self.free_boxes, 1)[0])
        self.boxes.add(new_box)

    def update(self, dt):
        self.count +=1
        with self.canvas:
            self.random_box()
            self.player.draw()
            for i in (j for j in self.boxes):
                i.draw()

class PongApp(App):
    def build(self):
        self.game = NotACoolGame()
        self.game.setup()
        Clock.schedule_interval(self.game.update, 1.0 / 1.0)
        return self.game


if __name__ == '__main__':
    PongApp().run()
