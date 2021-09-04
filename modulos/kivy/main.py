#KIVY
from kivy.core.window import Window
from kivy.properties import OptionProperty
#KIVY GRAPHIC
from kivy.graphics import Rectangle
#FRAMEWORK KIVYMD
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
#LIBRERIAS PROPIAS
#BD
from modulos.bd import *

#CARGAR BD
conexion_bd = ConexionBD()

class MainWid(MDBoxLayout):
    """Widget raiz de la aplicacion, contiene el Widget responsivo correspondiente al tamaño de la aplicacion.
    
    Atributo:
    - media = ('M', options=('XS', 'S', 'M', 'L', 'XL')) (OptionProperty), se utiliza para validar si la escala de la aplicacion, alcanzo un tamaño en especifico."""
    media = OptionProperty('M', options=('XS', 'S', 'M', 'L', 'XL'))

    def __init__(self, movil_wid, tablet_pc_wid, **kwargs):
        super(MainWid, self).__init__(**kwargs)
        # MainApp
        self.app = MDApp.get_running_app()
        # ELEGIR LA IMAGEN MAS RECIENTEMENTE
        self.imagen_de_fondo_usado_recientemente = conexion_bd.api_restful(
            "imagenes_de_fondo", "SELECCIONAR")[0][1]
        # GUI's
        self.movil_wid = movil_wid
        self.tablet_pc_wid = tablet_pc_wid
        # ELEGIR GUI A UTILIZAR SEGUN TAMAÑO DE LA VENTANA
        width = Window.size[0]
        self.media = (
            'XS' if width < 250 else
            'S' if width < 500 else
            'M' if width < 1000 else
            'L' if width < 1200 else
            'XL'
        )
        self.responsivo_estado = [""]
        if self.media in ("XS", "S"):
            self.add_widget(self.movil_wid)
            self.responsivo_estado[0] = self.media
        else:
            self.add_widget(self.tablet_pc_wid)
            self.responsivo_estado[0] = self.media
        Window.bind(size=self.responsivo)
        # EVENTOS DE SIZE Y POS
        self.bind(pos=self.update)
        self.bind(size=self.update)
        self.update()

    def responsivo(self, win, size):
        """Cambia de Widget responsivo, cada vez que se alcanza una escala de < 500 px. O se sobrepasa de esta."""
        width, _ = size
        media_nuevo = (
            'XS' if width < 250 else
            'S' if width < 500 else
            'M' if width < 1000 else
            'L' if width < 1200 else
            'XL'
        )
        if self.media != media_nuevo:
            self.media = media_nuevo
            self.responsivo_estado[0] = self.media
            if self.media in ("XS", "S"):
                # Limpia los widget añadidos anteriormente.
                self.clear_widgets()
                self.add_widget(self.movil_wid)
            else:
                # Limpia los widget añadidos anteriormente.
                self.clear_widgets()
                self.add_widget(self.tablet_pc_wid)

    def update(self, *kwargs):
        """Funcion enlazado a evento de escala de Widget, utiliza la imagen de fondo recientemente seleccionada, y lo ajusta automaticamente al tamaño del dispositivo"."""
        # Utilizar imagen de fondo recientemente seleccionada, y ajustarlo automaticamente al tamaño del dispositivo...
        self.canvas.before.clear()
        with self.canvas.before:
            Rectangle(source=self.imagen_de_fondo_usado_recientemente,
                      size=self.size, pos=self.pos)