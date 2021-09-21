from kivymd.app import MDApp

class MainResponsivo():
    """Clase padre para los Widgets responsivos como "movil" y "tablet_pc", y para el Widget de complemento "AccesoRapidoAbajo".
    
    Atributo:
    - GENERAR_COMANDOS_PREDETERMINADOS (Dict[str,str]), constante que tiene el nombre de los botones de los comandos (Mostrado en la parte superior de la aplicacion), y el contenido de los comandos respectivos.
    
    Metodo:
    - generar_codigo (Callback), metodo que agrega los comandos de los botones de comandos (Mostrado en la parte superior de la aplicacion).."""

    GENERAR_COMANDOS_PREDETERMINADOS = {
        "Regla":r"\draw[style=help lines] (0,0) grid (ancho_lienzo_de_dibujo,alto_lienzo_de_dibujo);",
        "draw(Linea)":"\n"+r"\draw (x1,y1) -- (x2,y2);",
        "draw(Rectangulo)":"\n"+r"\draw (x1,y1) rectangle (x2, y2);",
        "draw(Circulo)":"\n"+r"\draw (x1,y1) circle (radio);",
        "draw(Arco)":"\n"+r"\draw (x1,y1) arc (desde_angulo:hasta_angulo:radio);",
        "draw(Bezier)":"\n"+r"\draw (x1,y1) .. controls (x2,y2) and (x3,y3) .. (x4,y4);",
        "tikzset(Sin argumentos)":"\n"+r"\tikzset{nombre_estilo global/.style = {}}",
        "tikzset(Con argumentos)":"\n"+r"\tikzset{nombre_estilo global/.style n args = {} = {}, estilo global/.default = {}}",
        "definecolor":"\n"+r"\definecolor{nombre_color}{tipo_color}{codigo_color}",
        "newcommand":"\n"+r"""
    \newcommand{nombre_comando}[1][cantidad_parametro]{
        
    }""",
        "animarPytikz":r"""
    \animarPytikz{

    }""",
        "guardarPytikz":r"""\guardarPytikz{

    }
        """
    }

    def generar_codigo(self,conjunto_de_comandos,*args) ->None:
        """Agrega el conjunto_de_comandos en el Input de escribir codigo."""
        app = MDApp.get_running_app()
        responsivo_wid = app.root.children[0]
        """Agrega el contenido del comando del boton de comando utilizado en el Input Codigo."""
        responsivo_wid.ids["codigo_tikz"].text+=conjunto_de_comandos