from kivy.app import App
from kivy.graphics.context_instructions import Color
from kivy.graphics.texture import Texture
from kivy.graphics.vertex_instructions import Rectangle, Ellipse
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.properties import (
    NumericProperty, ReferenceListProperty,
    ObjectProperty
)
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.config import Config
from itertools import starmap
from copy import copy
import random

from copy import copy


def fibonacci(max_iter):
    a, b = 1, 1
    for i in range(0, max_iter):
        yield a
        a, b = b, a + b


fib_numbers = [i for i in fibonacci(20)]


class Box():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.drawn = False
        self.number = str(random.sample(fib_numbers, 1)[0])

    def draw(self, BOX_SIZE):
        Color(0, 0, 1., 1)
        Rectangle(pos=(self.x, self.y), size=(BOX_SIZE, BOX_SIZE))
        Color(0, 0, 0)
        # TODO fix this
        x, y = (self.x - 25, self.y - 20)
        Label(text=self.number, font_size=15, pos=(x, y))
        self.drawn = True

# Evil
def Player(Box):
    def draw(self, BOX_SIZE):
        Color(1, 0, 0, 1)
        Ellipse(pos=(self.x - BOX_SIZE / 2, self.y - BOX_SIZE / 2), size=(BOX_SIZE, BOX_SIZE))


class PongGame(Widget):
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)

    def setup(self):
        H, W = starmap(Config.getint, (("graphics", i) for i in ("height", "width")))
        self.BOX_SIZE = 100
        self.free_boxes = {Box(i, j) for i in range(0, H, self.BOX_SIZE)
                           for j in range(0, W, self.BOX_SIZE)}
        self.boxes = set()

    def random_box(self):
        if not self.free_boxes:
            return
        copy(self.free_boxes)
        new_box = random.sample(self.free_boxes, 1)[0]
        self.free_boxes = self.free_boxes - {new_box}
        self.boxes = self.boxes.union({new_box})


    def draw_boxes(self):
        self.random_box()
        for i in (j for j in self.boxes if not j.drawn):
            i.draw(self.BOX_SIZE)

    def update(self, dt):
        with self.canvas:
            self.draw_boxes()


class PongApp(App):
    def build(self):
        self.game = PongGame()
        self.game.setup()
        Clock.schedule_interval(self.game.update, 1.0 / 1.0)
        return self.game


if __name__ == '__main__':
    PongApp().run()
