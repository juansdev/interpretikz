#Otras librerias
from functools import partial
import weakref
#KIVY UIX
from kivy.uix.scrollview import ScrollView
#FRAMEWORK KIVYMD
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
#LIBRERIAS PROPIAS
from modulos.kivy.submodulo.main import MainResponsivo
from modulos.kivy.complementos_widgets.area_de_dibujo import AreaDeDibujo

class Movil(ScrollView,MainResponsivo):
    """Widget responsivo, utilizado cuando la aplicacion es reducida en tamaño a menos de 500px."""
    def __init__(self,**kwargs):
        super(Movil,self).__init__(**kwargs)
        self.area_de_dibujar_movil = AreaDeDibujo()
        self.ids["seccion_dibujar"].add_widget(self.area_de_dibujar_movil)
        #Al Widget AreaDeDibujo se le añade el ID "area_de_dibujar"
        self.ids["area_de_dibujar"] = weakref.ref(self.area_de_dibujar_movil)
        self.app = MDApp.get_running_app()

        #Crear botones para generar comandos predeterminados
        for nombre_comando,conjunto_de_comandos in self.GENERAR_COMANDOS_PREDETERMINADOS.items():
            #Si la longitud del texto del boton supera los 16 caracteres...
            boton_generar_comando_predeterminado = MDRaisedButton(md_bg_color=self.app.theme_cls.bg_dark,text=nombre_comando,theme_text_color="Secondary",font_name="media/fonts/OpenSans-SemiBold")
            #Añadirle el evento para escribir comandos en el Input correspondiente.
            boton_generar_comando_predeterminado.bind(on_press=partial(self.generar_codigo,conjunto_de_comandos))
            #Añadirle estilos
            self.ids["acceso_rapido_sup"].add_widget(boton_generar_comando_predeterminado)
        
        #Actualizar el Label de informacion de tamaño del lienzo del dibujo
        self.bind(size=self.update)
    
    def update(self,instance,size_new):
        """Funcion enlazado a evento de escala de Widget, actualiza la propiedad "info_size" de la clase "AreaDeDibujo", con el Widget identificado como "info"."""
        sizes_nuevos_lienzo_dibujo = self.area_de_dibujar_movil.ancho_alto_actualizado
        if(len(sizes_nuevos_lienzo_dibujo)):
            self.area_de_dibujar_movil.info_size = self.ids["info"]