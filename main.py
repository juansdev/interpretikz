import pytz
from functools import partial
from copy import deepcopy
from datetime import datetime

#KIVY
import kivy, os
from kivy.core.window import Window
from kivy.properties import ObjectProperty,OptionProperty
from kivy.lang.builder import Builder
from kivy.clock import Clock
from kivy.graphics import RenderContext
from kivy.metrics import sp,dp
#KIVY UIX
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.popup import Popup
#KIVY GRAPHIC
from kivy.graphics import Rectangle
#FRAMEWORK KIVYMD
from kivymd.app import MDApp
from kivymd.uix.imagelist import SmartTileWithLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.filemanager import MDFileManager
from kivymd.toast import toast
from kivymd.uix.list import OneLineAvatarListItem, IconLeftWidget
#LIBRERIAS PROPIAS
from pytikz.pytikz import Pytikz
from conexionbd import ConexionBD

#CARGAR BD
conexion_bd = ConexionBD()

fs_multitextura = '''
$HEADER$

// Nuevo uniform que recibirá textura en el índice 1
uniform sampler2D texture1;

void main(void) {

    // Múltiples colores actuales con ambas texturas (0 y 1).
    // Actualmente, ambos usarán exactamente las mismas coordenadas de textura.
    gl_FragColor = frag_color * \
        texture2D(texture0, tex_coord0) * \
        texture2D(texture1, tex_coord0);
}
'''

class AreaDeDibujo(RelativeLayout):
    def __init__(self,**kwargs):
        self.id = "AreaDeDibujo"
        self.canvas = RenderContext()
        # configurar shader.fs y enlazarlo a un nuevo codigo que automaticamente lo compilara.
        self.canvas.shader.fs = fs_multitextura
        # llamar al constructor del padre
        # si hay algunos objetos graficos, ellos lo añadiran en nuestro nuevo
        # canvas
        super(AreaDeDibujo, self).__init__(**kwargs)
        # nosotros actualizaremos nuestros variables glsl en un clock
        Clock.schedule_interval(self.actualizar_glsl, 0)
    def actualizar_glsl(self, *largs):
        # Esto es necesario para el Shader Vertex predeterminado.
        self.canvas['projection_mat'] = Window.render_context['projection_mat']
        self.canvas['modelview_mat'] = Window.render_context['modelview_mat']

area_de_dibujar_mobil = AreaDeDibujo()
area_de_dibujar_pc_tablet = AreaDeDibujo()

generar_comandos_predeterminados = {
    "tikzset(Sin argumentos)":"\n"+r"\tikzset{nombre_estilo global/.style = {}}",
    "tikzset(Con argumentos)":"\n"+r"\tikzset{nombre_estilo global/.style n args = {} = {}, estilo global/.default = {}}",
    "definecolor":"\n"+r"\definecolor{nombre_color}{tipo_color}{codigo_color}",
    "draw(Rectangulo)":"\n"+r"\draw[] (x1,y1) rectangle (x2, y2);",
    "draw(Circulo)":"\n"+r"\draw[] (x1,y1) circle (radio);",
    "draw(Arco)":"\n"+r"\draw[] (x1,y1) arc (desde_angulo:hasta_angulo:radio);",
    "draw(Bezier)":"\n"+r"\draw (x1,y1) .. controls (x2,y2) and (x3,y3);",
    "draw(Linea)":"\n"+r"\draw[] (x1,y1) -- (x2,y2);",
    "newcommand":"\n"+r"""
\newcommand{nombre_comando}[1][cantidad_parametro]{
    
}""",
    "animarPytikz":r"""
\animarPytikz{

}"""
}

#Funcion utilizada en la clase MobilWid y TabletPcWid
def generar_codigo(comandos,tablet_pc_wid,mobil_wid,instance):
    if tablet_pc_wid:
        tablet_pc_wid.ids["codigo_tikz"].text+=comandos
    if mobil_wid:
        mobil_wid.ids["codigo_tikz"].text+=comandos

class MobilWid(ScrollView):
    def __init__(self):
        super(MobilWid,self).__init__()
        self.ids["seccion_dibujar"].add_widget(area_de_dibujar_mobil)

        #Crear botones para generar comandos predeterminados
        for k,v in generar_comandos_predeterminados.items():
            #Si la longitud del texto del boton supera los 16 caracteres...
            boton_generar_comando_predeterminado = MDRaisedButton(md_bg_color=[1,1,1,1],text="[b][color=000000]"+k+"[/color][/b]",font_name="arial")
            #Añadirle el evento para escribir comandos en el Input correspondiente.
            boton_generar_comando_predeterminado.bind(on_press=partial(generar_codigo,v,None,self))
            #Añadirle estilos
            self.ids["acceso_rapido_sup"].add_widget(boton_generar_comando_predeterminado)

class TabletPcWid(MDGridLayout):
    def __init__(self):
        super(TabletPcWid,self).__init__()
        self.ids["seccion_dibujar"].add_widget(area_de_dibujar_pc_tablet)
        self.app = MDApp.get_running_app()
        
        #Crear botones para generar comandos predeterminados
        for k,v in generar_comandos_predeterminados.items():
            boton_generar_comando_predeterminado = MDRaisedButton(md_bg_color=self.app.theme_cls.bg_dark,text=k,theme_text_color="Secondary",font_name="media/fonts/OpenSans-SemiBold")
            #Añadirle el evento para escribir comandos en el Input correspondiente.
            boton_generar_comando_predeterminado.bind(on_press=partial(generar_codigo,v,self,None))
            #Añadirle estilos
            self.ids["acceso_rapido_sup"].add_widget(boton_generar_comando_predeterminado)

#Clase de los demas Widgets cargadados...

class ListarImagenesWid(MDBoxLayout):
    def __init__(self,main_wid):
        super(ListarImagenesWid,self).__init__()
        self.listar_fondos()
        self.main_wid = main_wid

    def listar_fondos(self):
        #Limpiar fondos anteriores
        self.ids["lista_imagenes"].clear_widgets()
        #Cargar imagenes desde la BD
        conjunto_de_datos = conexion_bd.api_restful("SELECCIONAR","imagenes_de_fondo")
        for fila in conjunto_de_datos:
            id = fila[0]
            ruta = fila[1]
            nombre_de_archivo_con_extension = os.path.basename(ruta)
            filename,_ = os.path.splitext(nombre_de_archivo_con_extension)
            text_wid = "[size=26]"+filename+"[/size]\n[size=14]"+nombre_de_archivo_con_extension+"[/size]"
            smartTitleWithLabel = SmartTileWithLabel(source=ruta,text=text_wid, box_color=[0,0,0,0],on_press=partial(self.fondo_seleccionado,id))
            #Agregar botones actualizados al acceso rapido
            self.ids["lista_imagenes"].add_widget(smartTitleWithLabel)

    def agregar_fondo(self,ruta_imagen):
        arr_datos = [ruta_imagen]
        #INSERTAR DATOS EN LA BD
        operacion_valida = conexion_bd.api_restful("INSERTAR","imagenes_de_fondo",arr_datos)
        if operacion_valida:
            #MOSTRAR DATOS ACTUALIZADOS
            self.listar_fondos()

    def seleccionar_fondo(self,id,ruta,instance):
        #Actualizar fecha de uso de la imagen en la BD
        utc_ahora = datetime.utcnow().replace(tzinfo=pytz.utc)
        utc_formateado = datetime.strftime(utc_ahora,"%Y-%m-%d %H:%M:%S")
        arr_datos = [id,ruta,utc_formateado]
        conexion_bd.api_restful("ACTUALIZAR","imagenes_de_fondo",arr_datos)
        #Reemplazar imagen anterior por esta...
        self.main_wid.canvas.before.clear()
        with self.main_wid.canvas.before:
            Rectangle(source=ruta,size=self.main_wid.size,pos=self.main_wid.pos)
        self.cerrar_dialog()
        self.main_wid.imagen_de_fondo_usado_recientemente = ruta 

    def eliminar_fondo(self,id,instance):
        #ELIMINAR IMAGEN DE LA BD
        operacion_valida = conexion_bd.api_restful("ELIMINAR","imagenes_de_fondo",[id])
        if operacion_valida:
            #MOSTRAR DATOS ACTUALIZADOS
            self.listar_fondos()
        self.cerrar_dialog()

    def cerrar_dialog(self,*args):
        self.dialog.dismiss()

    def fondo_seleccionado(self,id,instance):
        ruta = instance.source
        btn_eliminar_imagen = MDFlatButton(text="Eliminar imagen", text_color=[0,0,0,1])
        btn_seleccionar_imagen = MDRaisedButton(text="Utilizar imagen", text_color=[0,0,0,1])
        #Agregar los comportamientos correspondientes
        btn_seleccionar_imagen.bind(on_press=partial(self.seleccionar_fondo,id,ruta))
        btn_eliminar_imagen.bind(on_press=partial(self.eliminar_fondo,id))
        self.dialog = MDDialog(
            title="¿Que quieres hacer con esta imagen?",
            text="Si decides eliminar la imagen, se eliminara para siempre de la base de datos, no se podra recuperar.",
            radius=[20, 7, 20, 7],
            buttons=[
                btn_eliminar_imagen,
                btn_seleccionar_imagen
            ],
        )
        self.dialog.open()

#Funcion utilizada en la clase MainWid y MainApp
def eliminar_dibujo(id,app,mobil_wid,tablet_pc_wid,instance):
    btn_eliminar_dibujo = MDFlatButton(text="Eliminar dibujo", text_color=[0,0,0,1])
    btn_cancelar = MDRaisedButton(text="Cancelar", text_color=[0,0,0,1])
    dialog = MDDialog(
        title="¿Seguro que quieres eliminar este dibujo?",
        text="Si decides eliminar el dibujo, se eliminara para siempre de la base de datos, no se podra recuperar.",
        radius=[20, 7, 20, 7],
        buttons=[
            btn_eliminar_dibujo,
            btn_cancelar
        ]
    )
    #Agregar los comportamientos correspondientes
    def cancelar(dialog,*args):
        dialog.dismiss()
    def eliminar(id,dialog,instance):
        conexion_bd.api_restful("ELIMINAR","dibujos_usuario",[id])
        datos = conexion_bd.api_restful("SELECCIONAR","dibujos_usuario")
        listar_botones_dibujo(datos,app,mobil_wid,tablet_pc_wid)
        cancelar(dialog)
    btn_cancelar.bind(on_press=partial(cancelar,dialog))
    btn_eliminar_dibujo.bind(on_press=partial(eliminar,id,dialog))
    dialog.open()

def listar_botones_dibujo(conjunto_de_datos,app,mobil_wid,tablet_pc_wid):
    #Eliminar los botones anteriores
    tablet_pc_wid.ids["acceso_rapido_bot"].clear_widgets()
    mobil_wid.ids["acceso_rapido_bot"].clear_widgets()
    #Agregar los botones nuevos a cada padre
    wids_a_agregar = [tablet_pc_wid,mobil_wid]
    for fila in conjunto_de_datos:
        id = fila[0]
        nombre_dibujo = fila[1]
        comandos_dibujo = fila[2]
        for gui_wid in wids_a_agregar:
            #Crear contenedor lista
            lista_dibujo = OneLineAvatarListItem(
                text=nombre_dibujo, bg_color=app.theme_cls.bg_dark,
                theme_text_color="Secondary"
            )
            #Crear icono para la lista
            icon_eliminar_dibujo = IconLeftWidget(
                icon="delete", theme_text_color="Error"
            )
            #Agregar evento a la lista y su icono
            #Comportamiento agregar comandos al input de escribir codigo tikz
            lista_dibujo.bind(on_press=partial(generar_codigo,comandos_dibujo,tablet_pc_wid,mobil_wid))
            #Comportamiento eliminar dibujo segun id de la BD
            icon_eliminar_dibujo.bind(on_press=partial(eliminar_dibujo,id,app,mobil_wid,tablet_pc_wid))
            #Agregar botones hijos al box padre
            lista_dibujo.add_widget(icon_eliminar_dibujo)
            #Agregar botones actualizados al acceso rapido
            gui_wid.ids["acceso_rapido_bot"].add_widget(lista_dibujo)

responsivo_estado = [""]

class MainWid(MDBoxLayout):
    media = OptionProperty('M', options=('XS', 'S', 'M', 'L', 'XL'))
    def __init__(self,mobil_wid,tablet_pc_wid):
        super(MainWid,self).__init__()
        #MainApp
        self.app = MDApp.get_running_app()
        #ELEGIR LA IMAGEN MAS RECIENTEMENTE
        self.imagen_de_fondo_usado_recientemente = conexion_bd.api_restful("SELECCIONAR","imagenes_de_fondo")[0][1]
        #GUI's
        self.mobil_wid = mobil_wid
        self.tablet_pc_wid = tablet_pc_wid
        #ELEGIR GUI A UTILIZAR SEGUN TAMAÑO DE LA VENTANA
        width = Window.size[0]
        self.media = (
            'XS' if width < 250 else
            'S' if width < 500 else
            'M' if width < 1000 else
            'L' if width < 1200 else
            'XL'
        )
        if self.media in ("XS","S"):
            self.add_widget(self.mobil_wid)
            responsivo_estado[0] = self.media
        else:
            self.add_widget(self.tablet_pc_wid)
            responsivo_estado[0] = self.media
        Window.bind(size=self.responsivo)
        #MOSTRAR DATOS ACTUALIZADOS EN BOTONES INFERIORES DE DIBUJO
        conjunto_de_datos = conexion_bd.api_restful("SELECCIONAR","dibujos_usuario")
        listar_botones_dibujo(conjunto_de_datos,self.app,self.mobil_wid,self.tablet_pc_wid)
        #EVENTOS DE SIZE Y POS
        self.bind(pos=self.update)
        self.bind(size=self.update)
        self.update()

    def responsivo(self, win, size):
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
            responsivo_estado[0] = self.media
            if self.media in ("XS","S"):
                self.clear_widgets()#Limpia los widget añadidos anteriormente.
                self.add_widget(self.mobil_wid)
            else:
                self.clear_widgets()#Limpia los widget añadidos anteriormente.
                self.add_widget(self.tablet_pc_wid)

    def update(self,*kwargs):
        #Utilizar imagen de fondo recientemente seleccionada...
        self.canvas.before.clear()
        with self.canvas.before:
            Rectangle(source=self.imagen_de_fondo_usado_recientemente,size=self.size,pos=self.pos)
        #Utilizar estilo recientemente seleccionada

class MainApp(MDApp):
    title = "InterpreTikZ"

    def __init__(self):
        super(MainApp,self).__init__()
        #Estilos
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.accent_palette = "Green"
        self.estilos = self.seleccionar_estilo()
        self.estilo_usado_recientemente = self.estilos[0]
        self.theme_cls.theme_style = deepcopy(self.estilo_usado_recientemente)
        #Instancia de clases Widgets hijas
        self.listar_imagenes_wid = None
        self.main_wid = None
        self.mobil_wid = None
        self.tablet_pc_wid = None
        self.explorador_abierto = False
        self.explorador = None
        Window.bind(on_keyboard=self.eventos)

    def seleccionar_estilo(self):
        datos = conexion_bd.api_restful("SELECCIONAR","estilos")
        estilo_usado_recientemente = datos[0][1]
        id_light = datos[0][0]
        id_dark = datos[1][0]
        return [estilo_usado_recientemente,id_light,id_dark]

    #Funciones utilizados por botones de la GUI
    def invertir_estilo(self,*arg):
        #Actualizar fecha del uso de estilo en la BD
        utc_ahora = datetime.utcnow().replace(tzinfo=pytz.utc)
        utc_formateado = datetime.strftime(utc_ahora,"%Y-%m-%d %H:%M:%S")
        if self.estilo_usado_recientemente == "Dark":
            self.estilo_usado_recientemente = "Light"
            mensaje_estilo_seleccionado = "Modo claro"
            mensaje_fondo = "Claro"
            id = self.estilos[1]
        else:
            self.estilo_usado_recientemente = "Dark"
            mensaje_estilo_seleccionado = "Modo oscuro"
            mensaje_fondo = "Oscuro"
            id = self.estilos[2]
        arr_datos = [id,self.estilo_usado_recientemente,utc_formateado]
        conexion_bd.api_restful("ACTUALIZAR","estilos",arr_datos)
        #Informar al usuario sobre el cambio de estilo en Dialog
        btn_salir = MDRaisedButton(text="Salir", text_color=[0,0,0,1])
        dialog = MDDialog(
            title="Reinicia la aplicacion para aplicar los cambios de estilo",
            text="El estilo seleccionado fue: "+mensaje_estilo_seleccionado+".\nEs recomendado utilizarlo cuando el fondo es "+mensaje_fondo+".",
            radius=[20, 7, 20, 7],
            buttons=[
                btn_salir
            ]
        )
        #Agregar los comportamientos correspondientes
        btn_salir.bind(on_press=partial(self.cerrar_dialog,dialog))
        dialog.open()

    def mostrar_informacion(self,*args):
        btn_salir = MDRaisedButton(text="Salir", text_color=[0,0,0,1])
        dialog = MDDialog(
            title="Informacion de la aplicacion",
            text="La aplicacion InterpreTikz fue desarrollada por el estudiante de Ingenieria de Sistemas Juan Guillermo Serrano Ramirez de la UT - CREAD Honda. Como proyecto de grado en la modalidad de pasantias trabajando junto la Fundacion Conciencia Activa CONATIC.",
            radius=[20, 7, 20, 7],
            buttons=[
                btn_salir
            ]
        )
        btn_salir.bind(on_press=partial(self.cerrar_dialog,dialog))
        dialog.open()

    def compilar(self,codigo_tikz):
        #Si esta en Celular...
        if responsivo_estado[0] in ("XS","S"):
            self.mobil_wid.ids["seccion_dibujar"].clear_widgets()
            area_de_dibujar_mobil = AreaDeDibujo()
            self.mobil_wid.ids["seccion_dibujar"].add_widget(area_de_dibujar_mobil)
            Pytikz(codigo_tikz,area_de_dibujar_mobil)
        #Si esta en PC o Tablet...
        else:
            self.tablet_pc_wid.ids["seccion_dibujar"].clear_widgets()
            area_de_dibujar_pc_tablet = AreaDeDibujo()
            self.tablet_pc_wid.ids["seccion_dibujar"].add_widget(area_de_dibujar_pc_tablet)
            Pytikz(codigo_tikz,area_de_dibujar_pc_tablet)

    #Funcion listar imagenes
    def listar_imagenes_popup(self,*arg):

        self.listar_imagenes_wid = ListarImagenesWid(self.main_wid)
        btn_salir = MDRaisedButton(text="Salir",font_name="media/fonts/OpenSans-SemiBold")
        listar_imagenes_popup_wid = MDDialog(
            title="Lista de imagenes de fondo:",
            type="custom",
            radius=[20, 7, 20, 7],
            content_cls=self.listar_imagenes_wid,
            buttons=[
                btn_salir
            ]
        )
        btn_salir.bind(on_press=partial(self.cerrar_dialog,listar_imagenes_popup_wid))
        listar_imagenes_popup_wid.open()

    #Funciones mostrar cargar
    def mostrar_explorador(self,objetivo):
        if objetivo == "cargar_imagen":
            self.explorador = MDFileManager(
                exit_manager=self.cerrar_explorador,
                select_path=self.cargar_imagen
            )
        #Inicio de la ruta del explorador
        self.explorador.show('C:\\')
        self.explorador_abierto = True

    def cargar_imagen(self, path):
        filename = os.path.basename(path)
        _, extension = os.path.splitext(filename)#Background-image M.jpg
        extension_img = [".jpg",".jpeg",".png"]
        if extension in extension_img:
            #Guardar imagen de fondo
            self.listar_imagenes_wid.agregar_fondo(path)
        else:
            #Informar al usuario del error en Dialog
            btn_cancelar = MDRaisedButton(text="Cancelar", text_color=[0,0,0,1])
            dialog = MDDialog(
                title="Error al subir imagen a la Base de Datos",
                text="La extension "+extension+" no es valida.",
                radius=[20, 7, 20, 7],
                buttons=[
                    btn_cancelar
                ]
            )
            #Agregar los comportamientos correspondientes
            btn_cancelar.bind(on_press=partial(self.cerrar_dialog,dialog))
            dialog.open()
        
        self.explorador_abierto = False
        self.cerrar_explorador()
        toast(path)

    def cerrar_explorador(self, *args):
        self.explorador_abierto = False
        self.explorador.close()

    def cerrar_dialog(self,dialog,*args):
        dialog.dismiss()

    #Funcion guardar comandos de un dibujo
    def guardar_dibujo(self,nombre_dibujo,comandos_dibujo):
        arr_datos = [nombre_dibujo,comandos_dibujo]
        #INSERTAR DATOS EN LA BD
        operacion_valida = conexion_bd.api_restful("INSERTAR","dibujos_usuario",arr_datos)
        if operacion_valida:
            #MOSTRAR DATOS ACTUALIZADOS
            conjunto_de_datos = conexion_bd.api_restful("SELECCIONAR","dibujos_usuario")
            listar_botones_dibujo(conjunto_de_datos,self,self.mobil_wid,self.tablet_pc_wid)

    def eventos(self, instance, keyboard, keycode, text, modifiers):
        '''Se llamara cuando los botones son presionados en un dispositivo movil.'''
        if keyboard in (1001, 27):
            if self.explorador_abierto:
                self.explorador.back()
        return True

    def build(self):
        #CARGAR ARCHIVOS KIVYS
        Builder.load_file("kivy/responsivo/movil_wid.kv")
        Builder.load_file("kivy/responsivo/tablet_pc_wid.kv")
        Builder.load_file("kivy/listar_imagenes_popup.kv")
        #Instanciar Main_wid
        self.mobil_wid = MobilWid()
        self.tablet_pc_wid = TabletPcWid()
        self.main_wid = MainWid(self.mobil_wid,self.tablet_pc_wid)
        return self.main_wid

if __name__ == "__main__":
    MainApp().run()
    #Limpiar contenido de la carpeta source
    folder_parent = "./Pytikz/source/"
    folder_to_delete = ["animacion","relleno","relleno_lineas_libre","animacion_temp"]
    list_dir = []
    for folder in folder_to_delete:
        list_dir.append(folder_parent+folder)
    for dir in list_dir:
        for f in os.listdir(dir):
            os.remove(os.path.join(dir, f))