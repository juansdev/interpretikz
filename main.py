import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.core.window import WindowBase
from kivy.properties import OptionProperty
from kivy.lang.builder import Builder
from logic.main import Pytikz
import numpy as np

class Area_de_dibujar(RelativeLayout):
    def __init__(self):
        super(Area_de_dibujar,self).__init__()
        self.id = "area_de_dibujar"

area_de_dibujar_mobile = Area_de_dibujar()
area_de_dibujar_pc_tablet = Area_de_dibujar()

class MobileWid(ScrollView):
    def __init__(self):
        super(MobileWid,self).__init__()
        self.ids["seccion_dibujar"].add_widget(area_de_dibujar_mobile)

class TabletPcWid(GridLayout):
    def __init__(self):
        super(TabletPcWid,self).__init__()
        self.ids["seccion_dibujar"].add_widget(area_de_dibujar_pc_tablet)

Builder.load_file("responsive/movile.kv")
Builder.load_file("responsive/tablet_pc.kv")
mobilewid = MobileWid()
tabletpcwid = TabletPcWid()
responsive_estado = [""]

class MainWid(BoxLayout):
    media = OptionProperty('M', options=('XS', 'S', 'M', 'L', 'XL'))
    # id = "Main"
    def __init__(self):
        super(MainWid,self).__init__()
        width = Window.size[0]
        self.media = (
            'XS' if width < 250 else
            'S' if width < 500 else
            'M' if width < 1000 else
            'L' if width < 1200 else
            'XL'
        )
        if self.media in ("XS","S"):
            self.add_widget(mobilewid)
            responsive_estado[0] = self.media
        else:
            self.add_widget(tabletpcwid)
            responsive_estado[0] = self.media
        Window.bind(size=self.responsive)

    def responsive(self, win, size):
        width, height = size
        media_nuevo = (
            'XS' if width < 250 else
            'S' if width < 500 else
            'M' if width < 1000 else
            'L' if width < 1200 else
            'XL'
        )
        if self.media != media_nuevo:
            self.media = media_nuevo
            responsive_estado[0] = self.media
            if self.media in ("XS","S"):
                self.clear_widgets()#Limpia los widget añadidos anteriormente.
                self.add_widget(mobilewid)
            else:
                self.clear_widgets()#Limpia los widget añadidos anteriormente.
                self.add_widget(tabletpcwid)

class MainApp(App):
    title = "PyTikz"

    def compilar(self,codigo_tikz):
        #Si esta en Celular...
        if responsive_estado[0] in ("XS","S"):
            mobilewid.ids["seccion_dibujar"].clear_widgets()
            area_de_dibujar_mobile = Area_de_dibujar()
            mobilewid.ids["seccion_dibujar"].add_widget(area_de_dibujar_mobile)
            Pytikz(codigo_tikz,area_de_dibujar_mobile)
        #Si esta en PC o Tablet...
        else:
            tabletpcwid.ids["seccion_dibujar"].clear_widgets()
            area_de_dibujar_pc_tablet = Area_de_dibujar()
            tabletpcwid.ids["seccion_dibujar"].add_widget(area_de_dibujar_pc_tablet)
            Pytikz(codigo_tikz,area_de_dibujar_pc_tablet)

    def build(self):
        return MainWid()

if __name__ == "__main__":
    MainApp().run()