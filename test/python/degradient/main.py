from kivy.app import App
from kivy.graphics.texture import Texture
from kivy.graphics import Rectangle
from kivy.uix.boxlayout import BoxLayout
from colorsys import hsv_to_rgb
import six

class MyLayout(BoxLayout):

    def __init__(self,**kwargs):
        super(MyLayout,self).__init__(**kwargs)
        w = 10
        h = 10
        texture = Texture.create(size=(w, h))
        buf = []

        # color_base = [255,0,0]
        # color_final = [240,100,50]
        for i in range(h):
            for j in range(w):
                color_base = hsv_to_rgb(j/float(w),1,i/float(h)) # colorsys takes (0,0,0) to (1,1,1)
                pixel = [int(a*b) for a,b in zip(color_base,[255,255,255])] # since color goes from (0,0,0) to (1,1,1), we multiply by 255
                buf.extend(pixel)

        # buf = b''.join(map(chr, buf))
        buf = b''.join(list(map(lambda x: six.int2byte(x), buf)))
        texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
        with self.canvas:
            Rectangle(texture=texture, pos=self.pos, size=(w, h))

class MyApp(App):

    def build(self):
        return MyLayout()


if __name__ == "__main__":
    MyApp().run()