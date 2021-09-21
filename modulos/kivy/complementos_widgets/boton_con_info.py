#Otras librerias
from functools import partial
from typing import Union
#KIVY
from kivy.metrics import dp
#FRAMEWORK KIVYMD
from kivymd.app import MDApp
from kivymd.uix.button import MDIconButton
from kivymd.uix.tooltip import MDTooltip
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.label import MDLabel

# Clases botones, usados en el modo de dibujo
class BotonConInfo(MDIconButton, MDTooltip):
    """Widget de MDIconButton+MDTooltip, utilizado en los botones del "Modo de dibujo", etc."""
    def __init__(self, **kwargs):
        super(BotonConInfo, self).__init__(**kwargs)

    def on_state(self, instance, value):
        """Se cambia el icono del boton presionado con otro, y el texto tambien con otro."""
        if(value == "normal"):
            app = MDApp.get_running_app()
            responsivo_wid = app.root.children[0]
            icon_current = self.icon
            tooltip_text_current = self.tooltip_text

            #Evento del Mostrar el modo dibujo
            if(icon_current=="gesture-tap-button"):
                params = [self,"mode","lock","seccion_dibujar",["botones_modo_dibujar_1","botones_modo_dibujar_2","botones_modo_dibujar_3"],["label_modo_normal_1","label_modo_dibujar_1"]]
                params = [self.__devolver_widget(param,responsivo_wid) for param in params]
                self.ocultar_botones(*params)
            
            icons = {"eye": "eye-off", "eye-off": "eye",
                    "checkbox-multiple-blank-outline": "checkbox-multiple-blank", "checkbox-multiple-blank": "checkbox-multiple-blank-outline","lock":"lock-open","lock-open":"lock"}
            tooltip_texts = {"Ocultar edicion": "Mostrar edicion",
                            "Mostrar edicion": "Ocultar edicion", "Ocultar el modo dibujo": "Mostrar el modo dibujo", "Mostrar el modo dibujo": "Ocultar el modo dibujo","Habilitar dibujo":"Deshabilitar dibujo","Deshabilitar dibujo":"Habilitar dibujo"}
            icon_next = icon_current
            tooltip_text_next = tooltip_text_current
            if icon_current in icons.keys():
                icon_next = icons[icon_current]
            if tooltip_text_current in tooltip_texts.keys():
                tooltip_text_next = tooltip_texts[tooltip_text_current]
            self.icon = icon_next
            self.tooltip_text = tooltip_text_next

    def __devolver_widget(self,id:Union[str,list,object],responsivo_wid:object)->object:
        """Verifica si la ID corresponde a la de un Widget y si es asi entonces retorna ese Widget. Si no entonces retorna la ID."""
        if(isinstance(id,str)):
            return responsivo_wid.ids[id]
        elif(isinstance(id,list)):
            ids = id
            return [responsivo_wid.ids[id] for id in ids]
        else:
            return id
    

    def ocultar_botones(self, instance, mode, lock, seccion_dibujar, conjuntos_de_botones, conjunto_de_labels):
        """Se alterna los botones a mostrar, entre el "Modo de dibujo" al "Modo normal"."""
        # Conjunto de labels del modo de dibujar
        label_modo_normal_1, label_modo_dibujar_1 = conjunto_de_labels
        deshabilitado = label_modo_dibujar_1.disabled
        if not deshabilitado:
            # Ocultar labels modo dibujar
            label_modo_dibujar_1.opacity = 0
            label_modo_dibujar_1.disabled = True
            # Mostrar labels modo normal
            label_modo_normal_1.opacity = 1
        else:
            # Ocultar labels modo dibujar
            label_modo_dibujar_1.opacity = 1
            label_modo_dibujar_1.disabled = False
            # Mostrar labels modo normal
            label_modo_normal_1.opacity = 0

        # Conjunto de botones del modo de dibujar
        for conjunto_de_botones in conjuntos_de_botones:
            for child in conjunto_de_botones.children:
                if instance != child:
                    if isinstance(child, type(self)):
                        # Boton del modo de dibujar
                        deshabilitado = child.disabled
                        if not deshabilitado:
                            child.opacity = 0
                            child.disabled = True
                            # Bloquear interaccion con las funciones de dibujo usando el Touch, ademas de ocultar el modo de edicion
                            if lock.icon != "lock":
                                lock.icon = "lock"
                                lock.tooltip_text = "Habilitar dibujo"
                            if mode.text != "Ninguno":
                                mode.text = "Ninguno"
                            if child.icon == "eye":
                                seccion_dibujar.change_edit_mode(child)
                                child.icon = "eye-off"
                                child.tooltip_text = "Mostrar edicion"
                        else:
                            child.opacity = 1
                            child.disabled = False
                            # Desbloquear interaccion con las funciones de dibujo usando el Touch, ademas de mostrar el modo de edicion
                            if lock.icon != "lock-open":
                                lock.icon = "lock-open"
                                lock.tooltip_text = "Bloquear dibujo"
                            if mode.text != "Forma libre":
                                mode.text = "Forma libre"
                            if child.icon == "eye-off":
                                seccion_dibujar.change_edit_mode(child)
                                child.icon = "eye"
                                child.tooltip_text = "Ocultar edicion"

    def abrir_menu_figuras(self, instance, mode):
        """Despliega un menu con la lista de figuras disponibles en el "Modo de dibujo"."""
        # Valor del Label con el ID "mode"
        self.mode = mode
        # Cabecera de la lista desplegable
        menu_header = MDBoxLayout(
            orientation='vertical', adaptive_size=True, padding=dp(4))
        menu_container = MDBoxLayout(spacing=dp(12), adaptive_size=True)
        header_icon_container = MDIconButton(
            icon="gesture-tap-button", pos_hint={"center_y": .5})
        header_label_container = MDLabel(
            text="Figuras", adaptive_size=True, pos_hint={"center_y": .5})
        menu_container.add_widget(header_icon_container)
        menu_container.add_widget(header_label_container)
        menu_header.add_widget(menu_container)

        # Contenido de la lista desplegable
        list_shapes = ["Circulo", "Elipse", "Poligono",
                       "Forma libre", "Punto", "Ninguno"]
        menu_items = []
        for i in list_shapes:
            menu_items.append({
                "text": i,
                "viewclass": "OneLineListItem",
                "height": dp(56),
                "on_release": lambda x=i: self.cerrar_menu_figuras(x),
            })

        # Dropdown Menu - Header y Contenedor
        self.menu = MDDropdownMenu(
            header_cls=menu_header,
            items=menu_items,
            caller=instance,
            width_mult=4,
        )
        self.menu.open()

    def cerrar_menu_figuras(self, text_item):
        """Al seleccionar una figura, se cierra el menu."""
        self.mode.text = text_item
        self.menu.dismiss()