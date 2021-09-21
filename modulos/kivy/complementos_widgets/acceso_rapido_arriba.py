#Otras librerias
import os
from functools import partial
#GLOBAL
import globales
#FRAMEWORK KIVYMD
from kivymd.app import MDApp
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.button import MDRaisedButton
#LIBRERIAS PROPIAS
#KIVY - Responsivos Widgets
from modulos.kivy.submodulo.main import MainResponsivo

class AccesoRapidoArriba (MDGridLayout,MainResponsivo):
    """Contenedor de los botones superiores, utilizados para generar comandos predeterminados."""
    def __init__(self, **kwargs):
        super(AccesoRapidoArriba,self).__init__(**kwargs)
        self.app = MDApp.get_running_app()
        #Hijos
        #Crear botones para generar comandos predeterminados
        for nombre_comando,conjunto_de_comandos in self.GENERAR_COMANDOS_PREDETERMINADOS.items():
            #Si la longitud del texto del boton supera los 16 caracteres...
            boton_generar_comando_predeterminado = MDRaisedButton(md_bg_color=self.app.theme_cls.bg_dark,text=nombre_comando,theme_text_color="Secondary",font_name=os.path.join(globales.ruta_raiz,"media/fonts/OpenSans-SemiBold"))
            #Añadirle el evento para escribir comandos en el Input correspondiente.
            boton_generar_comando_predeterminado.bind(on_release=partial(self.generar_codigo,conjunto_de_comandos))
            #Añadir hijos
            self.add_widget(boton_generar_comando_predeterminado)