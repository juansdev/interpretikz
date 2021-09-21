import kivy, time, os, pathlib
#Otras librerias
from functools import partial
from copy import deepcopy
#KIVY
from kivy.core.window import Window
from kivy.config import Config
from kivy.lang.builder import Builder
from kivy.metrics import dp
from kivy.utils import platform
#KIVY UIX
from kivy.uix.colorpicker import ColorPicker
#FRAMEWORK KIVYMD
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.filemanager import MDFileManager
#LIBRERIAS PROPIAS
#GLOBAL
import globales
#PYTIKZ
from pytikzgenerate.pytikzgenerate import PytikzGenerate
#Librerias propias
#BD
from modulos.bd import ConexionBD
#GENEARAR DIAGNOSTICO
from modulos.logging import GenerarDiagnostico
#ANDROID
if(platform=="android"): 
    from android.storage import primary_external_storage_path
    from android.permissions import request_permissions, Permission

__version__ = "0.2.0"

class InterpretikzApp(MDApp):
    title = "InterpreTikZ"
    #Impedir que el usuario acceda a las configuraciones de Kivy desde la App
    use_kivy_settings=False

    def open_settings(self,*args):
        pass

    def __init__(self,**kwargs):
        super(InterpretikzApp,self).__init__(**kwargs)
        #Configuracion - Globales
        globales.init()
        globales.ruta_raiz = os.path.dirname(os.path.abspath(__file__))
        if(platform == "android"):
            globales.user_data_dir = primary_external_storage_path()#/storage/emulated/0
        #Mostrar rutas globales
        GenerarDiagnostico(self.__class__.__name__,"Ruta raiz del directorio: "+globales.ruta_raiz,"info")
        GenerarDiagnostico(self.__class__.__name__,"Ruta del user_data_dir: "+globales.user_data_dir,"info")
        globales.conexion_bd = ConexionBD()
        #Estilos
        self.icon = os.path.join(globales.ruta_raiz,"media/favicon.png")
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.accent_palette = "Green"
        self.estilos = self.__seleccionar_estilo()
        self.estilo_usado_recientemente = self.estilos[0]
        self.theme_cls.theme_style = deepcopy(self.estilo_usado_recientemente)
        #Instancia de clases Widgets hijas
        self.listar_imagenes_mddialog = None
        self.main_wid = None
        self.responsivos_wid = None
        self.explorador_abierto = False
        self.explorador = None
        Window.bind(on_keyboard=self.eventos)

    #Funciones internas de la clase
    def __seleccionar_estilo(self):
        conjunto_de_datos = globales.conexion_bd.api_restful("estilos","SELECCIONAR")
        estilo_usado_recientemente = conjunto_de_datos[0][1]
        id_light = conjunto_de_datos[0][0]
        id_dark = conjunto_de_datos[1][0]
        return [estilo_usado_recientemente,id_light,id_dark]

    #Funciones utilizados por botones de la GUI
    def alternar_estilos(self,*arg):
        #Seleccionar el estilo a cambiar
        if self.estilo_usado_recientemente == "Dark":
            #Actual
            mensaje_estilo_actual = "Modo oscuro"
            #A cambiar
            estilo_a_cambiar = "Light"
            mensaje_estilo_a_cambiar = "Modo claro"
            mensaje_fondo_recomendado = "Claro"
            id = self.estilos[1]
        else:
            #Actual
            mensaje_estilo_actual = "Modo claro"
            #A cambiar
            estilo_a_cambiar = "Dark"
            mensaje_estilo_a_cambiar = "Modo oscuro"
            mensaje_fondo_recomendado = "Oscuro"
            id = self.estilos[2]
        #Estilos a cambiar
        #Informar al usuario sobre el cambio de estilo en Dialog
        btn_aplicar = MDRaisedButton(text="Cambiar al "+mensaje_estilo_a_cambiar, text_color=[0,0,0,1])
        #Reinicia la aplicacion para aplicar los cambios de estilo
        aviso_informativo = AvisoInformativo(
            titulo="¿Quieres cambiar el estilo de la aplicacion?",
            mensaje="Estilo actual: "+mensaje_estilo_actual+".\nEstilo a cambiar: "+mensaje_estilo_a_cambiar+".\nPara este estilo es recomendable utilizarlo junto a un fondo "+mensaje_fondo_recomendado+".",
            botones_adicionales=[
                btn_aplicar
            ],
            agregar_boton_salir=True
        )
        #Agregar los comportamientos correspondientes
        #Actualizar fecha del uso de estilo en la BD
        def aplicar_cambios(id,estilo_a_cambiar,instance):
            #Actualizar variable local
            self.estilo_usado_recientemente = estilo_a_cambiar
            self.estilo_usado_recientemente = estilo_a_cambiar
            #Actualizar fecha del uso de estilo en la BD
            utc_ahora = time.gmtime()
            utc_formateado = "%s-%s-%s %s:%s:%s"%(utc_ahora.tm_year,utc_ahora.tm_mon,utc_ahora.tm_mday,utc_ahora.tm_hour,utc_ahora.tm_min,utc_ahora.tm_sec)
            arr_datos = [id,estilo_a_cambiar,utc_formateado]
            mensaje_de_error = globales.conexion_bd.api_restful("estilos","ACTUALIZAR",arr_datos)
            #Cerrar dialog actual
            AvisoInformativo.cerrar_aviso_informativo(aviso_informativo,aviso_informativo.md_dialog)
            #Abrir dialog informativo de cambio
            if(mensaje_de_error):
                mensaje = "Ocurrio un error al actualizar la hora en la que se elegio el estilo.\n"+"Error: "+mensaje_de_error
                AvisoInformativo(
                    titulo="Error al actualizar",
                    mensaje=mensaje
                )
            else:
                AvisoInformativo(
                    mensaje="Reinicia la aplicacion para efectuar los cambios"
                )
        btn_aplicar.bind(on_release=partial(aplicar_cambios,id,estilo_a_cambiar))

    def mostrar_informacion(self,*args):
        AvisoInformativo(
            titulo="Informacion de la aplicacion",
            mensaje="La aplicacion InterpreTikz fue desarrollada por el estudiante de Ingenieria de Sistemas Juan Guillermo Serrano Ramirez de la UT - CREAD Honda. Como proyecto de grado en la modalidad de pasantias trabajando junto a la Fundacion Conciencia Activa CONATIC.",
        )
        
    def compilar(self,codigo_tikz):
        movil_wid, tablet_pc_wid = self.responsivos_wid
        #Si esta en Celular...
        if self.main_wid.vista_movil:
            area_de_dibujar_movil = movil_wid.ids["area_de_dibujar"]()
            area_de_dibujar_movil.limpiar_canvas()
            PytikzGenerate(codigo_tikz,area_de_dibujar_movil,globales.user_data_dir)
        #Si esta en PC o Tablet...
        else:
            area_de_dibujar_pc_tablet = tablet_pc_wid.ids["area_de_dibujar"]()
            area_de_dibujar_pc_tablet.limpiar_canvas()
            PytikzGenerate(codigo_tikz,area_de_dibujar_pc_tablet,globales.user_data_dir)

    #Funciones en el listador de imagenes
    def listar_imagenes_popup(self,*arg):
        self.listar_imagenes_mddialog = AvisoInformativo(
            titulo="Lista de imagenes de fondo:",
            tipo="custom",
            contenido_cls=ListarImagenes(),
        )

    def cargar_imagen(self, path):
        nombre_del_archivo = os.path.basename(path)
        _, extension = os.path.splitext(nombre_del_archivo)#Background-image M.jpg
        extension_img = [".jpg",".jpeg",".png"]
        if extension in extension_img:
            #Guardar imagen de fondo
            self.listar_imagenes_mddialog.md_dialog.content_cls.agregar_fondo(path)
            self.cerrar_explorador()
            toast(path)
        else:
            #Informar al usuario del error en Dialog
            AvisoInformativo(
                titulo="Error al subir imagen a la Base de Datos",
                mensaje="La extension "+extension+" no es valida.\nLas siguientes extensiones son validas: .jpg, .jpeg, .png"
            )
            self.cerrar_explorador(extension_invalida=True)
        self.explorador_abierto = False

    #Funciones mostrar explorador
    def mostrar_explorador(self,objetivo,listar_imagenes):
        if objetivo == "cargar_imagen":
            #Cerrar el dialog de listar imagenes
            aviso_informativo = self.listar_imagenes_mddialog
            AvisoInformativo.cerrar_aviso_informativo(aviso_informativo,aviso_informativo.md_dialog)
            #Abrir dialog del explorador
            self.explorador = MDFileManager(
                exit_manager=self.cerrar_explorador,
                select_path=self.cargar_imagen
            )
        #Inicio de la ruta del explorador
        if(platform=="win"):
            self.explorador.show(str(pathlib.Path.home()))
        elif(platform=="android"):
            self.explorador.show(globales.user_data_dir)
        self.explorador_abierto = True

    def cerrar_explorador(self, args=None, extension_invalida=False):
        #Cerrar el dialog del explorador
        self.explorador_abierto = False
        self.explorador.close()
        #Abrir el dialog de listar imagenes
        if(not extension_invalida): self.listar_imagenes_mddialog.md_dialog.open()

    def eventos(self, instance, keyboard, keycode, text, modifiers):
        '''Se llamara cuando los botones son presionados en un dispositivo movil.'''
        if keyboard in (1001, 27):
            if self.explorador_abierto:
                self.explorador.back()
        return True

    #Funciones seleccionar un color
    def on_color(self,tooltip_text,instance,value):
        self.get_selected_color(tooltip_text,value)
    
    #Abrir Dialog del Color Picker
    def open_color_picker(self,tooltip_text):
        #Dialog
        color_picker = ColorPicker(size_hint_y= None, height= dp(400),font_name=os.path.join(globales.ruta_raiz,"media/fonts/OpenSans-SemiBold"))
        btn_salir = MDRaisedButton(text="Salir",font_name=os.path.join(globales.ruta_raiz,"media/fonts/OpenSans-SemiBold"))
        aviso_informativo = AvisoInformativo(
            titulo="Paleta de colores:",
            tipo="custom",
            contenido_cls=color_picker,
            auto_desaparecer=False,
            botones_adicionales=[
                btn_salir
            ]
        )
        #Comportamiento Boton de salir y Widget ColorPicker
        color_picker.bind(color=partial(self.on_color,tooltip_text))
        def cerrar_color_picker_dialog(instance):
            #Wid seccion_dibujar - PC - Movil
            for responsivo_wid in self.responsivos_wid:
                seccion_dibujar = responsivo_wid.ids.seccion_dibujar
                seccion_dibujar.selected_shapes_for_fill = []
            AvisoInformativo.cerrar_aviso_informativo(aviso_informativo,aviso_informativo.md_dialog)
        btn_salir.bind(on_release=cerrar_color_picker_dialog)

    def update_color(self, responsivo_wid, pintar_relleno_fondo,label_text, selected_color):
        #Wid seccion_dibujar - PC - Movil
        seccion_dibujar = responsivo_wid.ids.seccion_dibujar
        default_selected_color = [1.0, 1.0, 1.0, 1]
        #La figura seleccionada o a dibujar saldra con el relleno...
        if pintar_relleno_fondo:
            fill_color_old = seccion_dibujar.fill_color
            if default_selected_color == fill_color_old or selected_color != default_selected_color:
                seccion_dibujar.fill_color = selected_color
                seccion_dibujar.add_colored_shapes_area()
        #La figura seleccionada o a dibujar saldra con el relleno del borde...
        else:
            line_color_old = seccion_dibujar.line_color
            if default_selected_color == line_color_old or selected_color != default_selected_color:
                seccion_dibujar.line_color = selected_color
                seccion_dibujar.change_border(change_color=True)
        #Label informativo con el color establecido
        label_text.text = ",".join([str(round(color*255)) for color in selected_color])
        label_text.text_color = selected_color

    def get_selected_color(self,tooltip_text,selected_color):
        pintar_relleno_fondo = False
        for responsivo_wid in self.responsivos_wid:
            if "Rellenar el fondo" == tooltip_text:
                label_text = responsivo_wid.ids.color_relleno
                pintar_relleno_fondo = True
            else:
                label_text = responsivo_wid.ids.color_borde
            self.update_color(responsivo_wid,pintar_relleno_fondo,label_text,selected_color)

    #Construir aplicacion
    def build(self):
        #CARGAR ARCHIVOS KIVYS
        Builder.load_file(os.path.join(globales.ruta_raiz,"kivy/responsivo/movil.kv"))
        Builder.load_file(os.path.join(globales.ruta_raiz,"kivy/responsivo/tablet_pc.kv"))
        Builder.load_file(os.path.join(globales.ruta_raiz,"kivy/listar_imagenes.kv"))
        #Instanciar Main_wid
        self.responsivos_wid = [Movil(),TabletPc()]
        movil_wid, tablet_pc_wid = self.responsivos_wid
        self.main_wid = MainWid(movil_wid, tablet_pc_wid)
        return self.main_wid

    #Evento ejecutado despues del build
    def on_start(self):
        #Solicitar permisos de acceso al Android
        if(platform == "android"):
            def callback(permisos, resultados):
                GenerarDiagnostico(self.__class__.__name__,'Permisos:','info')
                GenerarDiagnostico(self.__class__.__name__,permisos,'info')
                GenerarDiagnostico(self.__class__.__name__,'Permisos concedidos:','info')
                GenerarDiagnostico(self.__class__.__name__,resultados,'info')
                if all([res for res in resultados]):
                    GenerarDiagnostico(self.__class__.__name__,'Todos los permisos fueron concedidos!','info')
                else:
                    GenerarDiagnostico(self.__class__.__name__,'No todos los permisos fueron concedidos!','info')
            request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE], callback)

if __name__ == "__main__":
    #Version de Kivy utilizado
    kivy.require("2.0.0")
    #Aplicacion con tamaño autoescalable
    Config.set('graphics', 'resizable', True)
    #Cancela las herramientas de desarrollador Kivy".
    Config.set("input","mouse","mouse,multitouch_on_demand")
    #El keyboard movil aparecera bajo el input.
    Window.keyboard_anim_args = {'d': .2, 't': 'in_out_expo'}
    Window.softinput_mode = "below_target"
    #Widgets
    #KIVY - Principal Widget
    from modulos.kivy.main import MainWid
    #KIVY - Responsivos Widgets
    from modulos.kivy.responsivos_widgets.movil import Movil
    from modulos.kivy.responsivos_widgets.tablet_pc import TabletPc
    #KIVY - Complementos Widgets
    from modulos.kivy.complementos_widgets.listar_imagenes import ListarImagenes
    #Necesarios para el codigo Kivy.
    from modulos.kivy.complementos_widgets.main_scrollview import MainScrollView
    from modulos.kivy.complementos_widgets.painter import PainterWidget
    from modulos.kivy.complementos_widgets.boton_con_info import BotonConInfo
    from modulos.kivy.complementos_widgets.acceso_rapido_arriba import AccesoRapidoArriba
    from modulos.kivy.complementos_widgets.acceso_rapido_abajo import AccesoRapidoAbajo
    #KIVY - Otros Widgets
    from modulos.kivy.otros_widgets.aviso_informativo import AvisoInformativo
    #Lanzar aplicacion Kivy
    InterpretikzApp().run()