'''
Multitexture Example
====================

This example blends two textures: the image mtexture1.png of the letter K
and the image mtexture2.png of an orange circle. You should see an orange
K clipped to a circle. It uses a custom shader, written in glsl
(OpenGL Shading Language), stored in a local string.

Note the image mtexture1.png is a white 'K' on a transparent background, which
makes it hard to see.
'''

from kivy.clock import Clock
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.graphics import RenderContext, Color, Rectangle, BindTexture


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


kv = """
<MultitextureLayout>:

    MultitextureWidget:

"""

Builder.load_string(kv)


class MultitextureWidget(Widget):

    def __init__(self, **kwargs):
        self.canvas = RenderContext()
        # configurar shader.fs y enlazarlo a un nuevo codigo que automaticamente lo compilara.
        self.canvas.shader.fs = fs_multitexture
        with self.canvas:
            Color(1, 1, 1)

            # aqui, nosotros estamos enlazando una textura personalizada en el index 1
            # esto seria usado como texture1 en el shader.
            # Los nombres de los archivos son engañosos: no corresponden al
            # index aqui o en el shader.
            BindTexture(source='mtexture2.png', index=1)

            # crear un rectangulo con textura (estara en el index 0)
            Rectangle(size=(150, 150), source='mtexture1.png', pos=(500, 200))

        # establecer la texture1 para usar la textura en el index 1
        self.canvas['texture1'] = 1

        # llamar al constructor del padre
        # si hay algunos objetos graficos, ellos lo añadiran en nuestro nuevo
        # canvas
        super(MultitextureWidget, self).__init__(**kwargs)

        # nosotros actualizaremos nuestros variables glsl en un clock
        Clock.schedule_interval(self.update_glsl, 0)

    def update_glsl(self, *largs):
        # Esto es necesario para el Shader Vertex predeterminado.
        self.canvas['projection_mat'] = Window.render_context['projection_mat']
        self.canvas['modelview_mat'] = Window.render_context['modelview_mat']


class MultitextureLayout(FloatLayout):

    def __init__(self, **kwargs):
        self.size = kwargs['size']
        super(MultitextureLayout, self).__init__(**kwargs)


class MultitextureApp(App):

    def build(self):
        return MultitextureLayout(size=(600, 600))


if __name__ == '__main__':
    MultitextureApp().run()