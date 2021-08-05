from proglog import ProgressBarLogger
from math import floor
import weakref


import glob, uuid
import moviepy.editor as mpy

#LIBRERIAS NECESARIAS PARA EL POPUP - PROGRESS BAR
import threading
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar

from kivy.metrics import dp

#PROGRESS BAR - API DEL MOVIEPY
class MyBarLogger(ProgressBarLogger):
    # `window` is the class where all the gui widgets are held
    def __init__(self,popup_progress_bar):
        super().__init__(init_state=None, bars=None, ignored_bars=None,
                 logged_bars='all', min_time_interval=0, ignore_bars_under=0)
        self.popup_progress_bar = popup_progress_bar
    def callback(self, **changes):
        # Every time the logger is updated, this function is called with
        # the `changes` dictionnary of the form `parameter: new value`.
        # the `try` is to avoid KeyErrors before moviepy generates a `'t'` dict 
        try:
            index = self.state['bars']['t']['index']
            total = self.state['bars']['t']['total']
            percent_complete = index / total * 100
            if percent_complete < 0:
                percent_complete = 0
            if percent_complete > 100:
                percent_complete = 100
            self.popup_progress_bar.do_update(percent_complete, index, total)
        except KeyError as e:
            print("ERROR")
            print(e)

#PROGRESS BAR - CÓDIGO KIVY
Builder.load_string('''

# SE DEJA
<LoadingPopup>:
    title: "Popup"
    size_hint: None, None
    size: 400, dp(400)
    auto_dismiss: False

    BoxLayout:
        orientation: "vertical"
        Label:
            id: percent_complete
            text: ''
            size_hint: (1.0, 0.3)
        Label:
            id: info
            text: ''
            size_hint: (1.0, 0.2)
        ProgressBar:
            id: progress
            size_hint: (1.0, 0.1)
# HASTA AQUÍ
<MainScreen>:
    BoxLayout:
        orientation: 'vertical'
    Button:
        on_press: root.doit_in_thread()
        text: 'Generar GIF'
''')

class LoadingPopup(Popup):
    def __init__(self, obj, **kwargs):
        super(LoadingPopup, self).__init__(**kwargs)

class MainScreen(FloatLayout):

    def __init__(self,**kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.old_value = 0#IMPORTANTE - ANTERIOR VALOR DEJADO POR EL ANTERIOR IMPULSO DE CARGA ILUSTRADO  [PROGRESS BAR]
        self.endRange = 100#IMPORTANTE - FINAL DE PROGRESS BAR  [PROGRESS BAR]

    def doit_in_thread(self):#SE DEJA
        self.popup = LoadingPopup(self)
        self.popup.open()
        threading.Thread(target=self.__make_gif).start()#En este caso la función por la cual el Progress Bar llenara hasta ser terminado es el "self.onMul"
    
    def __make_gif(self):
        my_bar_logger = MyBarLogger(self)
        # CREAR UN GIF ANIMADO...
        id = str(uuid.uuid4())
        #Recorta entorno transparente que sobra fuera de los bordes
        input_png_list = glob.glob("./source/*.jpg")
        input_png_list.sort()
        #Genera GIF a partir de una lista de secuencia de imagenes
        clips = [mpy.ImageClip(i).set_duration(.1)
                    for i in input_png_list]
        concat_clip = mpy.concatenate_videoclips(clips, method="compose")
        concat_clip.write_gif("./test.gif", fps=60,logger=my_bar_logger)

        #NOTA: SOLO CAMBIAN LAS RUTAS...

    def do_update(self, percent_complete, index, total,*args):
        progress = floor(percent_complete)
        if progress != self.old_value and progress % 5 == 0:
            self.popup.ids.progress.value = progress#IMPORTANTE - [PROGRESS BAR]
            self.popup.ids.percent_complete.text = "PORCENTAJE COMPLETO: "+str(progress)
            self.popup.ids.info.text = f"{index} de {total} frames del GIF completados... ({floor(percent_complete)}%)"
            if(progress == 100):
                self.popup.dismiss()
                content_popup = BoxLayout(orientation='vertical')
                content_popup.add_widget(Label(text='El GIF fue creado satisfactoriamente',size_hint=(1,.8)))
                close_btn = Button(text="Vale",size_hint=(1,.2))
                content_popup.add_widget(close_btn)
                popup = Popup(title='!ÉXITO!',
                content=content_popup,
                size_hint=(None, None), size=(400, dp(400)), auto_dismiss=False)
                close_btn.bind(on_press=popup.dismiss)
                popup.open()

class TestApp(App):
    def build(self):
        return MainScreen()

if __name__ == "__main__":
    TestApp().run()