import kivy, os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.properties import OptionProperty
from kivy.lang.builder import Builder
from kivy.clock import Clock
from kivy.graphics import RenderContext

from Pytikz.pytikz import Pytikz

fs_multitexture = '''
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

class Area_de_dibujo(RelativeLayout):
    def __init__(self,**kwargs):
        self.id = "Area_de_dibujo"
        self.canvas = RenderContext()
        # configurar shader.fs y enlazarlo a un nuevo codigo que automaticamente lo compilara.
        self.canvas.shader.fs = fs_multitexture
        # llamar al constructor del padre
        # si hay algunos objetos graficos, ellos lo añadiran en nuestro nuevo
        # canvas
        super(Area_de_dibujo, self).__init__(**kwargs)
        # nosotros actualizaremos nuestros variables glsl en un clock
        Clock.schedule_interval(self.update_glsl, 0)
    def update_glsl(self, *largs):
        # Esto es necesario para el Shader Vertex predeterminado.
        self.canvas['projection_mat'] = Window.render_context['projection_mat']
        self.canvas['modelview_mat'] = Window.render_context['modelview_mat']

area_de_dibujar_mobile = Area_de_dibujo()
area_de_dibujar_pc_tablet = Area_de_dibujo()

class MobileWid(ScrollView):
    def __init__(self):
        super(MobileWid,self).__init__()
        self.ids["seccion_dibujar"].add_widget(area_de_dibujar_mobile)

class TabletPcWid(GridLayout):
    def __init__(self):
        super(TabletPcWid,self).__init__()
        self.ids["seccion_dibujar"].add_widget(area_de_dibujar_pc_tablet)

Builder.load_file("responsive/movile.kv")
Builder.load_file("responsive/tablet_pc.kv")
mobilewid = MobileWid()
tabletpcwid = TabletPcWid()
responsive_estado = [""]

class MainWid(BoxLayout):
    media = OptionProperty('M', options=('XS', 'S', 'M', 'L', 'XL'))
    def __init__(self):
        super(MainWid,self).__init__()
        width = Window.size[0]
        self.media = (
            'XS' if width < 250 else
            'S' if width < 500 else
            'M' if width < 1000 else
            'L' if width < 1200 else
            'XL'
        )
        if self.media in ("XS","S"):
            self.add_widget(mobilewid)
            responsive_estado[0] = self.media
        else:
            self.add_widget(tabletpcwid)
            responsive_estado[0] = self.media
        Window.bind(size=self.responsive)

    def responsive(self, win, size):
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
            responsive_estado[0] = self.media
            if self.media in ("XS","S"):
                self.clear_widgets()#Limpia los widget añadidos anteriormente.
                self.add_widget(mobilewid)
            else:
                self.clear_widgets()#Limpia los widget añadidos anteriormente.
                self.add_widget(tabletpcwid)

class MainApp(App):
    title = "InterpreTikZ"

    def compilar(self,codigo_tikz):
        #Si esta en Celular...
        if responsive_estado[0] in ("XS","S"):
            mobilewid.ids["seccion_dibujar"].clear_widgets()
            area_de_dibujar_mobile = Area_de_dibujo()
            mobilewid.ids["seccion_dibujar"].add_widget(area_de_dibujar_mobile)
            Pytikz(codigo_tikz,area_de_dibujar_mobile)
        #Si esta en PC o Tablet...
        else:
            tabletpcwid.ids["seccion_dibujar"].clear_widgets()
            area_de_dibujar_pc_tablet = Area_de_dibujo()
            tabletpcwid.ids["seccion_dibujar"].add_widget(area_de_dibujar_pc_tablet)
            Pytikz(codigo_tikz,area_de_dibujar_pc_tablet)

    def build(self):
        return MainWid()

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