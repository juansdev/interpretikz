import glob, uuid
import threading
import moviepy.editor as mpy
import weakref

from kivy.clock import Clock
from PIL import Image
from win32api import GetSystemMetrics
from proglog import ProgressBarLogger
from math import floor
from functools import partial

from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout
from kivy.graphics import Color,Rectangle,Ellipse,Line
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup

from kivy.metrics import dp

#PROGRESS BAR - CÓDIGO KIVY
Builder.load_string('''

<LoadingPopup>:
    title: "Información del progreso de generación"
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
''')

class LoadingPopup(Popup):
    def __init__(self, obj, **kwargs):
        super(LoadingPopup, self).__init__(**kwargs)

#PROGRESS BAR - API DEL MOVIEPY
class MyBarLogger(ProgressBarLogger):
    # `window` is the class where all the gui widgets are held
    def __init__(self,clase_animador):
        super().__init__(init_state=None, bars=None, ignored_bars=None,
                 logged_bars='all', min_time_interval=0, ignore_bars_under=0)
        self.clase_animador = clase_animador
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
            self.clase_animador.do_update(percent_complete, index=index, total=total,generar_gif=True)
        except KeyError as e:
            print("ERROR")
            print(e)

class Animador():
    def __init__(self,area_de_dibujar):
        self.area_de_dibujar = area_de_dibujar

        # CONFIGURACIÓN DEL WID A DESCARGAR COMO IMG
        w = GetSystemMetrics(0)
        h = GetSystemMetrics(1)
        self.wid_gif = RelativeLayout(size=(w,h))
        with self.wid_gif.canvas:
            Color(1,1,1,0)
            Rectangle(pos=self.wid_gif.pos,size=self.wid_gif.size)
    
    def figura_a_png(self,generar_gif,name_figure,size,pos,color_relleno,tipo_de_linea,coords_borde,color_borde,line_width,angle_start=0,angle_end=0): 
        #APLICAR RELLENO
        with self.wid_gif.canvas:
            Color(*color_relleno)
        if name_figure == "rectangle":
            with self.wid_gif.canvas:
                figura = Rectangle(pos=pos,size=size)
        elif name_figure == "arc":
            with self.wid_gif.canvas:
                figura = Ellipse(pos=pos,size=size,angle_start=angle_start,angle_end=angle_end)
        elif name_figure == "circle":
            with self.wid_gif.canvas:
                figura = Ellipse(pos=pos,size=size)
        #APLICAR BORDE
        if tipo_de_linea:
            with self.wid_gif.canvas:
                Color(*color_borde)
            if name_figure == "rectangle":
                with self.wid_gif.canvas:
                    #BORDE RECTANGULO CON LINEAS DISCONTINUADAS
                    Line(points=coords_borde, dash_offset=10, dash_length=5)
            elif name_figure == "arc":
                with self.wid_gif.canvas:
                    Line(circle=coords_borde, dash_offset=10, dash_length=5)
        else:
            if name_figure == "rectangle":
                with self.wid_gif.canvas:
                    #BORDE RECTANGULO
                    Line(points=coords_borde,width=line_width)
            elif name_figure == "arc":
                with self.wid_gif.canvas:
                    Line(circle=coords_borde,width=line_width)
        if generar_gif:
            #1. CONFIGURACIÓN - PROGRESS BAR
            # self.old_value = 0#IMPORTANTE - ANTERIOR VALOR DEJADO POR EL ANTERIOR IMPULSO DE CARGA ILUSTRADO  [PROGRESS BAR]

            #2. DESPLIEGUE DEL POP UP.
            # self.popup = LoadingPopup(self.area_de_dibujar)
            # self.popup.open()

            # self.do_update(0,"Creando imagen en formato PNG a partir de la figura")
            id_figura = str(figura.uid)
            nombre_img = 'figura_estandar_'+id_figura+".png"
            ruta = './Pytikz/source/animacion_temp/'+nombre_img
            self.wid_gif.export_to_png(ruta)
            # self.do_update(20,"Imagen creado\nImagen: "+nombre_img)

            # self.do_update(40,"Recortando imagen eliminando el exceso\nImagen: "+nombre_img)
            image_png = Image.open(ruta)
            image_png.getbbox()
            image_png = image_png.crop(image_png.getbbox())
            # self.do_update(60,"Exceso de la imagen eliminado\nImagen: "+nombre_img)

            # self.do_update(80,"Convirtiendo imagen a JPG\nImagen: "+nombre_img)
            image_png.load() # required for png.split()
            background = Image.new("RGB", image_png.size, (255, 255, 255))
            background.paste(image_png, mask=image_png.split()[3]) # 3 is the alpha channel
            nombre_img = 'figura_estandar_'+id_figura+".jpg"
            ruta = './Pytikz/source/animacion/'+nombre_img
            background.save(ruta, 'JPEG', quality=80)
            # self.do_update(100,"Conversión a JPG exitoso\nImagen final: "+nombre_img)
        
    def generar_animacion(self):
        #1. CONFIGURACIÓN - PROGRESS BAR
        self.old_value = 0#IMPORTANTE - ANTERIOR VALOR DEJADO POR EL ANTERIOR IMPULSO DE CARGA ILUSTRADO  [PROGRESS BAR]

        #2. DESPLIEGUE DEL POP UP, CONEXIÓN AL API Logger del MoviePy Y CREAR UN GIF ANIMADO...
        self.popup = LoadingPopup(self.area_de_dibujar)
        self.popup.open()
        #Genera GIF a partir de una lista de secuencia de imagenes
        threading.Thread(target=self.__make_gif).start()#En este caso la función por la cual el Progress Bar llenara hasta ser terminado es el "self.onMul"

    def __make_gif(self):
        #CONEXIÓN AL API Logger del MoviePy
        my_bar_logger = MyBarLogger(self)
        #GENERAR GIF
        id = str(uuid.uuid4())
        #Ordenar los archivos de forma ascendente
        input_png_list = glob.glob("./Pytikz/source/animacion/*.jpg")
        input_png_list.sort()
        clips = [mpy.ImageClip(i).set_duration(.1)
                    for i in input_png_list]
        concat_clip = mpy.concatenate_videoclips(clips, method="compose")
        concat_clip.write_gif('./animacion_creado_id-'+id+'.gif', fps=2, logger=my_bar_logger)

    def do_update(self, percent_complete, info="",index=0, total=0, generar_gif=False,*args):
        progress = floor(percent_complete)
        if progress != self.old_value and progress % 5 == 0:
            self.popup.ids.progress.value = progress#IMPORTANTE - [PROGRESS BAR]
            self.popup.ids.percent_complete.text = "PORCENTAJE COMPLETO: "+str(progress)
            if generar_gif:
                self.popup.ids.info.text = f"{index} de {total} frames del GIF completados... ({floor(percent_complete)}%)"
            else:
                self.popup.ids.info.text = info
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