from kivy.app import App
from kivy.uix.button import Button
from kivy.properties import StringProperty


class IconButton(Button):
    icon = StringProperty("reload.png")

# you can alos just put this in your KV file
from kivy.lang import Builder
Builder.load_string("""
<IconButton>:
    text: "RECOMPILAR"
    background_color: [.2274509803921569,.8470588235294118,.1019607843137255,1]
    canvas:
        Rectangle:
            source:self.icon
            pos: [self.center[0]-85,self.center[1]-13]
            size: 30,30
""")


class TestApp(App):
    def build(self):
        return IconButton()


if __name__ in ("__main__", "android"):
    TestApp().run()