#CONFIGURACIONES KIVY - WINDOW
from kivy.core.window import Window
#KIVY
from kivy.metrics import Metrics
from kivy.clock import Clock
from kivy.graphics import RenderContext
#FRAMEWORK KIVYMD
from kivymd.app import MDApp
from kivymd.uix.relativelayout import MDRelativeLayout

#Clase del Widget dedicado a guardar los canvas realizados al dibujar.
class AreaDeDibujo(MDRelativeLayout):
    """Widget del "Area de dibujar" del aplicativo.
    
    Atributo:
    FS_MULTITEXTURA (str), valor constante, recibe las texturas generadas por Kivy y permite manejar varias texturas a la vez."""

    FS_MULTITEXTURA = '''
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

    def __init__(self,**kwargs):
        """1. Configura shader.fs y lo enlaza al atributo "FS_MULTITEXTURA" que automaticamente compilara.
        2. Llamar al constructor del padre de "shader.fs", buscando si hay objetos graficos, si es asi, se añadiran en el canvas de "Area de dibujar".
        3. Se actualizara las variables glsl del canvas en un Clock.
        4. Se vincula el evento de escala del Widget al metodo "update".
        5. Actualizar la propiedad "text" el Widget identificado como "info", con el tamaño del lienzo del dibujo actualizado.

        Propiedad:
        - info_size = None (object), contiene el Widget identificado como "info", en donde se mostrara la informacion actualizada del tamaño del lienzo de dibujo.
        """
        #Paso 1 al 3
        self.canvas = RenderContext()
        self.canvas.shader.fs = self.FS_MULTITEXTURA
        super(AreaDeDibujo, self).__init__(**kwargs)
        Clock.schedule_interval(self.actualizar_glsl, 0)
        #Paso 4 y 5
        self.info_size = None
        self.ancho_alto_actualizado = ()
        self.bind(size=self.update)
    
    def limpiar_canvas(self):
        """Limpia los canvas del widget "Area de dibujo"."""
        self.canvas.clear()

    def actualizar_glsl(self, *largs):
        """Actualiza las variables glsl del canvas."""
        self.canvas['projection_mat'] = Window.render_context['projection_mat']
        self.canvas['modelview_mat'] = Window.render_context['modelview_mat']
    
    def update(self,instance,size_actualizado):
        """Funcion enlazado a evento de escala de Widget, actualiza la informacion del tamaño del lienzo, si hay un cambio."""
        #DPI de la pantalla
        dpi_de_pantalla = Metrics.dpi
        operacion_dpi = 2.54 / dpi_de_pantalla
        #Convertir Pixeles ancho y alto de la pantalla, a CM
        ancho_actualizado = size_actualizado[0]
        alto_actualizado = size_actualizado[1]
        self.ancho_alto_actualizado = (round(operacion_dpi*ancho_actualizado,2),round(operacion_dpi*alto_actualizado,2))
        #Actualizar el Label de informacion de tamaño del lienzo del dibujo...
        if(self.info_size):
            ancho_actualizado,alto_actualizado = self.ancho_alto_actualizado
            self.info_size.text = "Ancho: {} - Alto: {}".format(ancho_actualizado, alto_actualizado)
