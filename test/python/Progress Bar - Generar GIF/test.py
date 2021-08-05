import threading
from functools import partial

from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import StringProperty
from kivy.uix.spinner import Spinner
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.popup import Popup



Builder.load_string('''

# SE DEJA
<LoadingPopup>:
    title: "Popup"
    size_hint: None, None
    size: 400, 400
    auto_dismiss: False

    BoxLayout:
        orientation: "vertical"
        Label:
            id: result
            text: ''
            size_hint: (1.0, 0.5)
        ProgressBar:
            id: progress
            size_hint: (1.0, 0.1)
# HASTA AQUÍ
<MainScreen>:
    BoxLayout:
        orientation: 'vertical'

        Spinner:
            id: first
            text: ' First Number'
            values: ['1','2','3','4','5','6','7','8','9']

        Spinner:
            id: second
            text: ' Second Number'
            values: ['1','2','3','4','5','6','7','8','9']

        Button:
            id: res
            on_press: root.doit_in_thread(first.text,second.text)
            text: 'Multiply'


''')

class LoadingPopup(Popup):#SE DEJA
    def __init__(self, obj, **kwargs):
        super(LoadingPopup, self).__init__(**kwargs)

class MainScreen(FloatLayout):
    changet = StringProperty()

    def doit_in_thread(self, fir, sec):#SE DEJA
        self.popup = LoadingPopup(self)
        self.popup.open()
        threading.Thread(target=partial(self.onMul, fir, sec)).start()#En este caso la función por la cual el Progress Bar llenara hasta ser terminado es el "self.onMul"

    def do_update(self, value, text, *args):#SE DEJA
        self.popup.ids.progress.value = value#IMPORTANTE - [PROGRESS BAR]
        self.popup.ids.result.text = "RESULTADO: "+text#RESULTADO OPERACIONES [SOLO INFORMATIVO]

    def onMul(self, fir, sec):
        #OPERACIONES
        a = (int(fir)*int(sec))
        print(a)
        b = 0
        old_value = 0#IMPORTANTE - ANTERIOR VALOR DEJADO POR EL ANTERIOR IMPULSO DE CARGA ILUSTRADO  [PROGRESS BAR]
        endRange = 1000000#IMPORTANTE - FINAL DE PROGRESS BAR  [PROGRESS BAR]
        #CIERRO OPERACIONES
        for i in range(endRange):
            progress = int(((i+1)*100)/endRange)#IMPORTNATE - PROGRESO ACTUAL DE LA BARRA [PROGRESS BAR]
            if progress != old_value and progress % 5 == 0:
                text = str(b*(int(fir)*int(sec)))#RESULTADO OPERACIONES [SOLO INFORMATIVO]
                Clock.schedule_once(partial(self.do_update, progress, text))
                old_value = progress
            b+=1
        self.popup.dismiss()

class TestApp(App):
    def build(self):
        return MainScreen()

if __name__ == "__main__":
    TestApp().run()