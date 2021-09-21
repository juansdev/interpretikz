#KIVY
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
#FRAMEWORK KIVYMD
from kivymd.app import MDApp


class MainScrollView(ScrollView):
    """ScrollView principal de la aplicacion, contiene los Widgets de herramientas."""

    def __init__(self, **kwargs):
        super(MainScrollView,self).__init__(**kwargs)
        #Estilos
        self.bar_color = [.1686274509803922, .1764705882352941, .1843137254901961, 1]
        self.bar_inactive_color = [.5019607843137255, .5019607843137255, .5019607843137255, 1]
        self.effect_cls = "ScrollEffect"
        self.do_scroll_x = False
        #Evento
        self.bind(on_scroll_stop=self.deshabilitar_widgets_al_scrolear)
    
    def deshabilitar_widgets_al_scrolear(self,instance,mouse_event)->None:
        """Evento que se ejecuta cuando el Scroll se detiente despues de ser deslizado, se habilitan/deshabilitan los botones dependiendo si este es mostrado/ocultado tras un Scrolling."""
        app = MDApp.get_running_app()
        root_wid = app.root
        responsivo_wid = app.root.children[0]
        #Contenedor
        contenedor = self.children[0]
        ancho_contenedor, alto_contenedor = contenedor.size
        alto_contenedor = root_wid.convertir_pixel(alto_contenedor)
        #Posiciones del acceso rapido arriba y abajo
        posiciones = {
            "acceso_rapido_arriba":{
                "widget":responsivo_wid.ids["acceso_rapido_arriba"],
                "posicion_top":alto_contenedor*(90)/100,
                "posicion_bottom":alto_contenedor*(83)/100,
                "listo":False
            },
            "acceso_rapido_abajo":{
                "widget":responsivo_wid.ids["acceso_rapido_abajo"],
                "posicion_top":alto_contenedor*(67)/100,
                "posicion_bottom":alto_contenedor*(58)/100,
                "listo":False
            }
        }
        acceso_rapido_arriba_wid = posiciones["acceso_rapido_arriba"]["widget"]
        acceso_rapido_abajo_wid = posiciones["acceso_rapido_abajo"]["widget"]
        #Posicion en pixeles del Scroll Y
        porcentaje_scroll_y = instance.scroll_y*100
        posicion_scroll_y = alto_contenedor*(porcentaje_scroll_y)/100
        #Acciones que se ejecutan cuando se oculta/muestra el Acceso rapido superior
        if(posiciones["acceso_rapido_arriba"]["posicion_bottom"] > posicion_scroll_y):
            for hijo_btn in acceso_rapido_arriba_wid.children[0].children:
                hijo_btn.disabled = True
        else:
            for hijo_btn in acceso_rapido_arriba_wid.children[0].children:
                hijo_btn.disabled = False

        if(posiciones["acceso_rapido_abajo"]["posicion_top"] < posicion_scroll_y):
            for hijo_btn in acceso_rapido_abajo_wid.children[0].children:
                hijo_btn.disabled = True
        else:
            for hijo_btn in acceso_rapido_abajo_wid.children[0].children:
                hijo_btn.disabled = False