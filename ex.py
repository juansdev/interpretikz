from kivy.app import App
from kivy.lang import Builder

main_widget_kv = '''
WaterFill:

<WaterFill@Widget>:
    width: self.height
    size_hint: None, 1
    canvas:
        Color: 
            rgb: (0,1,0)
        Ellipse:
            pos: root.pos
            size: root.size
'''

class TestApp(App):
    def build(self):
        return Builder.load_string(main_widget_kv)

if __name__ == '__main__':
    TestApp().run()