#Otras librerias
from typing import List, Union
#GLOBAL
import globales
#KIVY
from kivy.core.window import Window
from kivy.properties import OptionProperty
from kivy.metrics import Metrics
#KIVY GRAPHIC
from kivy.graphics import Rectangle
#FRAMEWORK KIVYMD
from kivymd.uix.boxlayout import MDBoxLayout
#LIBRERIAS PROPIAS
#PYTIKZ
from pytikzgenerate.pytikzgenerate import PytikzGenerate

class MainWid(MDBoxLayout):
    """Widget raiz de la aplicacion, contiene el Widget responsivo correspondiente al tamaño de la aplicacion.
    
    Atributo:
    - media = ('M', options=('XS', 'S', 'M', 'L', 'XL')) (OptionProperty), se utiliza para validar si la escala de la aplicacion, alcanzo un tamaño en especifico."""
    media = OptionProperty('M', options=('XS', 'S', 'M', 'L', 'XL'))

    def __init__(self, movil_wid, tablet_pc_wid, **kwargs):
        super(MainWid, self).__init__(**kwargs)
        # GUI's
        self.movil_wid = movil_wid
        self.tablet_pc_wid = tablet_pc_wid
        # ELEGIR GUI A UTILIZAR SEGUN TAMAÑO DE LA VENTANA
        media = self.media_elegido(Window.size[0])
        self.vista_movil = media in ("XS", "S")
        self.vista_pc = not media in ("XS", "S")
        if self.vista_movil:
            self.add_widget(self.movil_wid)
        else:
            self.add_widget(self.tablet_pc_wid)
        Window.bind(size=self.responsivo)
        # EVENTOS DE SIZE Y POS
        self.bind(pos=self.update)
        self.bind(size=self.update)

    def responsivo(self, instance, size)->None:
        """Cambia de Widget responsivo, cada vez que se adentre en un rango inferior de < 500 px o se sobrepasa de esta. Al cambiar de Widget responsivo, se almacenan los comandos escritos anteriormente, los canvas generados y los comandos guardados al proximo widget responsivo a cambiar."""
        ventana_ancho, _ = size
        # ELEGIR GUI A UTILIZAR SEGUN TAMAÑO DE LA VENTANA
        media_nuevo = self.media_elegido(ventana_ancho)
        vista_movil_nuevo = media_nuevo in ("XS", "S")
        vista_pc_nuevo = not media_nuevo in ("XS", "S")
        cambio_vista = True if vista_movil_nuevo != self.vista_movil or vista_pc_nuevo != self.vista_pc else False
        if cambio_vista:
            if vista_movil_nuevo == True != self.vista_movil:
                self.vista_movil = vista_movil_nuevo
                self.vista_pc = vista_pc_nuevo
                cambio_vista = False
                # Limpia los widget añadidos anteriormente.
                self.clear_widgets()
                self.add_widget(self.movil_wid)
                # Actualiza los datos de los botones de dibujos y la lista de imagenes
                self.movil_wid.ids["acceso_rapido_abajo"].children[0].listar_botones_dibujo()
                # Agrega los comandos del Widget anterior al actual Widget, asi como los canvas generados anteriormente
                self.movil_wid.ids["codigo_tikz"].text = self.tablet_pc_wid.ids["codigo_tikz"].text
                PytikzGenerate(self.movil_wid.ids["codigo_tikz"].text,self.movil_wid.ids["area_de_dibujar"](),globales.user_data_dir)
            else:
                self.vista_movil = vista_movil_nuevo
                self.vista_pc = vista_pc_nuevo
                cambio_vista = False
                # Limpia los widget añadidos anteriormente.
                self.clear_widgets()
                self.add_widget(self.tablet_pc_wid)
                # Actualiza los datos de los botones de dibujos y la lista de imagenes
                self.tablet_pc_wid.ids["acceso_rapido_abajo"].children[0].listar_botones_dibujo()
                # Agrega los comandos del Widget anterior al actual Widget, asi como los canvas generados anteriormente
                self.tablet_pc_wid.ids["codigo_tikz"].text = self.movil_wid.ids["codigo_tikz"].text
                PytikzGenerate(self.tablet_pc_wid.ids["codigo_tikz"].text,self.tablet_pc_wid.ids["area_de_dibujar"](),globales.user_data_dir)
    
    def media_elegido(self,ventana_ancho:float)->str:
        """Retorna el nombre de la media del dispositivo segun el ancho en pixeles de la ventana, se calcula de la siguiente manera:
        'XS' if width < 250 else
        'S' if width < 500 else
        'M' if width < 1000 else
        'L' if width < 1200 else
        'XL'
        """
        ventana_ancho = self.convertir_pixel(ventana_ancho)
        return 'XS' if ventana_ancho < 250 else 'S' if ventana_ancho < 500 else 'M' if ventana_ancho < 1000 else 'L' if ventana_ancho < 1200 else 'XL'

    def update(self, *kwargs)->None:
        """Funcion enlazado a evento de escala de Widget, utiliza la imagen de fondo recientemente seleccionada, y lo ajusta automaticamente al tamaño del dispositivo"."""
        
        # ELEGIR LA IMAGEN MAS RECIENTEMENTE
        imagen_de_fondo_usado_recientemente = globales.conexion_bd.api_restful("imagenes_de_fondo", "SELECCIONAR")
        if(len(imagen_de_fondo_usado_recientemente)):
            imagen_de_fondo_usado_recientemente = imagen_de_fondo_usado_recientemente[0][1]
            # Utilizar imagen de fondo recientemente seleccionada, y ajustarlo automaticamente al tamaño del dispositivo...
            self.canvas.before.clear()
            with self.canvas.before:
                Rectangle(source=imagen_de_fondo_usado_recientemente,
                        size=self.size, pos=self.pos)

    def convertir_pixel(self,pixel:float)->float:
        """Convierte el DPI del Pixel al DPI 96, retorna el Pixel con DPI 96."""
        #DPI Default: 96
        #DPI de la pantalla
        dpi_de_pantalla = Metrics.dpi
        if(dpi_de_pantalla!=96):
            pixel = pixel/96
        return pixel