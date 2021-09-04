#Otras librerias
import pytz, os
from functools import partial
from datetime import datetime
#KIVY
from kivy.metrics import dp
#KIVY GRAPHIC
from kivy.graphics import Rectangle
#FRAMEWORK KIVYMD
from kivymd.uix.imagelist import SmartTileWithLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
#LIBRERIAS PROPIAS
from modulos.bd import ConexionBD
from modulos.kivy.otros_widgets.aviso_informativo import AvisoInformativo

#CARGAR BD
conexion_bd = ConexionBD()

# Clase contenedor donde se lista las imagenes
class ListarImagenes(MDBoxLayout):
    """Widget de "Listar Imagenes" del aplicativo."""
    def __init__(self, main_wid:object, **kwargs):
        """1. Recoge los fondos de pantalla de la BD y los agrega al Widget identificado como "lista_imagenes".
        
        Propiedad:
        - main_wid = MainWid (object), es el Widget padre de "Listar Imagenes"."""
        super(ListarImagenes, self).__init__(**kwargs)
        self.listar_fondos()
        self.main_wid = main_wid

    def listar_fondos(self) -> None:
        """Recoge los fondos de pantalla de la BD y los agrega al Widget identificado como "lista_imagenes"."""
        # Limpiar fondos anteriores
        self.ids["lista_imagenes"].clear_widgets()
        # Cargar imagenes desde la BD
        conjunto_de_datos = conexion_bd.api_restful(
            "imagenes_de_fondo","SELECCIONAR")
        for fila in conjunto_de_datos:
            id = fila[0]
            ruta = fila[1]
            nombre_de_archivo_con_extension = os.path.basename(ruta)
            nombre_del_archivo, _ = os.path.splitext(
                nombre_de_archivo_con_extension)
            texto = "[size=26]"+nombre_del_archivo+"[/size]\n[size=14]" + \
                nombre_de_archivo_con_extension+"[/size]"
            smart_title_with_label = SmartTileWithLabel(source=ruta, text=texto, box_color=[
                                                        0, 0, 0, 0], on_press=partial(self.fondo_seleccionado, id))
            # Agregar botones actualizados al acceso rapido
            self.ids["lista_imagenes"].add_widget(smart_title_with_label)

    def agregar_fondo(self, ruta_imagen:str) -> None:
        """Agrega la ruta del fondo de pantalla, a la tabla "imagenes_de_fondo" de la BD.
        
        Parametro:
        - ruta_imagen (str), ruta de la imagen."""
        arr_datos = [ruta_imagen]
        # INSERTAR DATOS EN LA BD
        operacion_valida = conexion_bd.api_restful(
            "imagenes_de_fondo","INSERTAR", arr_datos)
        if operacion_valida:
            # MOSTRAR DATOS ACTUALIZADOS
            self.listar_fondos()

    def fondo_seleccionado(self, id:int, instance:object) -> None:
        """Despliega un aviso informativo, y tiene las funciones de "seleccionar_fondo" o de "eliminar_fondo".
        
        Parametros:
        id (int), el ID del fondo de pantalla.
        instance (object), el Widget que desenlazo la ejecucion de la funcion."""
        ruta = instance.source
        btn_eliminar_imagen = MDFlatButton(
            text="Eliminar imagen", text_color=[0, 0, 0, 1])
        btn_seleccionar_imagen = MDRaisedButton(
            text="Utilizar imagen", text_color=[0, 0, 0, 1])
        aviso_informativo = AvisoInformativo(
            titulo="¿Que quieres hacer con esta imagen?",
            mensaje="Si decides eliminar la imagen, se eliminara para siempre de la base de datos, no se podra recuperar.",
            botones_adicionales=[
                btn_eliminar_imagen,
                btn_seleccionar_imagen
            ],
        )
        # Agregar los comportamientos correspondientes
        def seleccionar_fondo(id:int, ruta:str, instance:MDRaisedButton) -> None:
            """Actualiza el fondo de pantalla de la tabla "imagenes_de_fondo" segun la ID, reemplaza los valores por la nueva ruta y el tiempo actualizado, en la BD.
            
            Parametro:
            - id (int), ID de la imagen_de_fondo.
            - ruta (str), ruta de la imagen_de_fondo."""
            # Actualizar fecha de uso de la imagen en la BD
            utc_ahora = datetime.utcnow().replace(tzinfo=pytz.utc)
            utc_formateado = datetime.strftime(utc_ahora, "%Y-%m-%d %H:%M:%S")
            arr_datos = [id, ruta, utc_formateado]
            conexion_bd.api_restful("imagenes_de_fondo","ACTUALIZAR", arr_datos)
            # Reemplazar imagen anterior por esta...
            self.main_wid.canvas.before.clear()
            with self.main_wid.canvas.before:
                Rectangle(source=ruta, size=self.main_wid.size,
                        pos=self.main_wid.pos)
            AvisoInformativo.cerrar_aviso_informativo(aviso_informativo,aviso_informativo.md_dialog)
            self.main_wid.imagen_de_fondo_usado_recientemente = ruta

        def eliminar_fondo(id:int, instance:MDFlatButton) -> None:
            """Elimina el fondo de pantalla segun ID, en la tabla "imagenes_de_fondo".
            
            Parametro:
            - id (int), ID de la imagen_de_fondo."""
            # ELIMINAR IMAGEN DE LA BD
            operacion_valida = conexion_bd.api_restful(
                "imagenes_de_fondo","ELIMINAR", [id])
            if operacion_valida:
                # MOSTRAR DATOS ACTUALIZADOS
                self.listar_fondos()
            AvisoInformativo.cerrar_aviso_informativo(aviso_informativo,aviso_informativo.md_dialog)

        btn_eliminar_imagen.bind(on_press=partial(eliminar_fondo, id))
        btn_seleccionar_imagen.bind(
            on_press=partial(seleccionar_fondo, id, ruta))