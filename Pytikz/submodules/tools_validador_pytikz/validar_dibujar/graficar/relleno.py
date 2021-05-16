from kivy.graphics import Color, BindTexture, Rectangle, Ellipse
from kivy.graphics.texture import Texture

#Relleno para figuras cerradas (Excluyendo la figura de lineas y bezier).
class Relleno():
    def __init__(self,area_dibujar,name_figure,degradado,pos,size,angle_start=0,angle_end=0):
        with area_dibujar.canvas:
            Color(1, 1, 1)   
        if name_figure == "rectangle":
            with area_dibujar.canvas:      
                # crear la figura (estara en el index 0)
                figura = Rectangle(pos=pos,size=size)
        elif name_figure == "arc":
            with area_dibujar.canvas:
                figura = Ellipse(pos=pos,size=size,angle_start=angle_start,angle_end=angle_end)
        elif name_figure == "circle":
            with area_dibujar.canvas:
                figura = Ellipse(pos=pos,size=size)
        id_figura = figura.uid
        url_texture_degradado = self.__aplicar_degradado(id_figura,**degradado)
        with area_dibujar.canvas:
            # aqui, nosotros estamos enlazando una textura personalizada en el index 1
            # esto seria usado como texture1 en el shader.
            # Los nombres de los archivos son engañosos: no corresponden al
            # index aqui o en el shader.
            BindTexture(source=url_texture_degradado, index=1)
        # establecer la texture1 para usar la textura en el index 1
        area_dibujar.canvas['texture1'] = 1

    def __aplicar_degradado(self,id_figura,left_color=(),right_color=(),top_color=(),middle_color=(),bottom_color=(),inner_color=(),outer_color=(),ball_color=()):
        #left color, right color, top color, middle color, bottom color, inner color, outer color, ball color
        if top_color and bottom_color:
            color_origen = bottom_color
            color_destino = top_color
            red_origen = color_origen[0]*255
            green_origen = color_origen[1]*255
            blue_origen = color_origen[2]*255
            red_destino = color_destino[0]*255
            green_destino = color_destino[1]*255
            blue_destino = color_destino[2]*255
            c1 = [red_origen, green_origen, blue_origen, 255]
            c1_trans = [red_origen, green_origen, blue_origen, 128]
            c2_trans = [red_destino, green_destino, blue_destino, 128]
            c2 = [red_destino, green_destino, blue_destino, 255]
            degradient = c1+c1_trans+c2_trans+c2
            degradient = [int(degra) for degra in degradient]
        else:
            degradient = 0
        texture = Texture.create(size=(4,1), colorfmt='rgba')
        texture.blit_buffer(bytes(degradient),colorfmt='rgba', bufferfmt='ubyte')
        url_texture = "./Pytikz/source/relleno/figura_relleno_"+str(id_figura)+".png"
        texture.save(url_texture)
        return url_texture