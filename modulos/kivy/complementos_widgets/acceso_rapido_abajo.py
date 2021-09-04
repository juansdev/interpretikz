#Otras librerias
from typing import List, Union
from functools import partial
#FRAMEWORK KIVYMD
from kivymd.app import MDApp
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.list import OneLineAvatarListItem, IconLeftWidget
#LIBRERIAS PROPIAS
#BD
from modulos.bd import *
#KIVY - Responsivos Widgets
from modulos.kivy.submodulo.main import MainResponsivo

#CARGAR BD
conexion_bd = ConexionBD()

class AccesoRapidoAbajo (MDGridLayout,MainResponsivo):

    def __init__(self, **kwargs):
        super(AccesoRapidoAbajo, self).__init__(**kwargs)
        self.app = MDApp.get_running_app()
        # MOSTRAR DATOS ACTUALIZADOS EN BOTONES INFERIORES DE DIBUJO
        conjunto_de_datos = conexion_bd.api_restful("dibujos_usuario", "SELECCIONAR")
        self.listar_botones_dibujo(conjunto_de_datos)
        
    def listar_botones_dibujo(self, conjunto_de_datos: List[Union[int, str, str]]) -> None:

        def eliminar_dibujo(id: int, nombre_dibujo: str, instance):
            # Agregar los comportamientos correspondientes
            btn_eliminar_dibujo = MDFlatButton(
                text="Eliminar el dibujo", text_color=[0, 0, 0, 1])
            aviso_informativo = AvisoInformativo(
                titulo="¿Seguro que quieres eliminar el dibujo "+nombre_dibujo+"?",
                mensaje="Si decides eliminar el dibujo "+nombre_dibujo +
                ", se eliminara para siempre de la base de datos, no se podra recuperar.",
                botones_adicionales=[btn_eliminar_dibujo],
                agregar_boton_salir=True
            )

            def eliminar(id, instance):
                conexion_bd.api_restful("dibujos_usuario", "ELIMINAR", [id])
                datos = conexion_bd.api_restful(
                    "dibujos_usuario", "SELECCIONAR")
                self.listar_botones_dibujo(datos)
                AvisoInformativo.cerrar_aviso_informativo(
                    aviso_informativo, aviso_informativo.md_dialog)
            btn_eliminar_dibujo.bind(on_press=partial(eliminar, id))

        # Eliminar los botones anteriores
        self.clear_widgets()

        for fila in conjunto_de_datos:
            id = fila[0]
            nombre_dibujo = fila[1]
            comandos_dibujo = fila[2]
            # Crear contenedor lista
            lista_dibujo = OneLineAvatarListItem(
                text=nombre_dibujo, bg_color=self.app.theme_cls.bg_dark,
                theme_text_color="Secondary"
            )
            # Crear icono para la lista
            icon_eliminar_dibujo = IconLeftWidget(
                icon="delete", theme_text_color="Error"
            )
            # Agregar evento a la lista y su icono
            # Comportamiento agregar comandos al input de escribir codigo tikz
            lista_dibujo.bind(on_press=partial(
                self.generar_codigo, comandos_dibujo))
            # Comportamiento eliminar dibujo segun id de la BD
            icon_eliminar_dibujo.bind(on_press=partial(
                eliminar_dibujo, id, nombre_dibujo))
            # Agregar botones hijos al box padre
            lista_dibujo.add_widget(icon_eliminar_dibujo)
            # Agregar botones actualizados al acceso rapido
            self.add_widget(lista_dibujo)

    # Funcion guardar comandos de un dibujo
    def guardar_dibujo(self, nombre_dibujo: str, comandos_dibujo: str) -> None:
        arr_datos = [nombre_dibujo, comandos_dibujo]
        # INSERTAR DATOS EN LA BD
        operacion_valida = conexion_bd.api_restful(
            "dibujos_usuario", "INSERTAR", arr_datos)
        if operacion_valida:
            # MOSTRAR DATOS ACTUALIZADOS
            conjunto_de_datos = conexion_bd.api_restful(
                "dibujos_usuario", "SELECCIONAR")
            self.listar_botones_dibujo(conjunto_de_datos)
            mensaje = "El dibujo "+nombre_dibujo+" se guardo con exito"
        else:
            mensaje = "Ocurrio un error al guardar el dibujo "+nombre_dibujo

        AvisoInformativo(
            mensaje=mensaje
        )