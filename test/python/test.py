#!/usr/bin/kivy
import kivy
kivy.require('1.7.2')

from random import random
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.graphics import Color
from kivy.graphics import Rectangle
from random import random
from random import choice
from kivy.properties import StringProperty
from kivy.clock import Clock
import time

Builder.load_string("""
<Highest>:
    GridLayout:
        cols: 1
        Button:
            id: btn_0
            text: "Hi"
            on_press: root.new()
""")

#CLOCK - EL SLEEP PARA KIVY
class Highest(Screen):
    def new(self):
        self.index = 0
        self.color = [[0,1,0],[1,0,0],[0,0,1]]
        self.evento = Clock.schedule_interval(self.test, 2)
    def test(self,*args):
        print("ENTRE "+str(self.index))
        self.ids["btn_0"].canvas.clear()
        with self.ids["btn_0"].canvas:
            Color(*self.color[self.index])
            Rectangle(pos=self.ids["btn_0"].pos, size=self.ids["btn_0"].size)
        self.index+=1
        if(self.index==len(self.color)):
            print("CANCELO EVENTO")
            Clock.unschedule(self.evento)

# Create the screen manager
sm = ScreenManager()
sm.add_widget(Highest(name='Highest'))

class TestApp(App):

    def build(self):
        return sm

if __name__ == '__main__':
    TestApp().run()