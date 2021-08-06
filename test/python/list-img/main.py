from kivymd.app import MDApp
from kivy.lang import Builder

KV = '''
Popup:
    ScrollView:

        MDGridLayout:
            cols: 3
            row_default_height: (self.width - self.cols*self.spacing[0]) / self.cols
            row_force_default: True
            adaptive_height: True
            padding: dp(4), dp(4)
            spacing: dp(4)

            SmartTileWithStar:
                box_color: 0,0,0,0
                source: "images/3949076.jpg"

            SmartTileWithStar:
                box_color: 0,0,0,0
                source: "images/5558009.jpg"

            SmartTileWithStar:
                box_color: 0,0,0,0
                source: "images/Lunar_Eclipse_Wallpaper_L.jpg"
'''


class MyApp(MDApp):
    def build(self):
        return Builder.load_string(KV)


MyApp().run()