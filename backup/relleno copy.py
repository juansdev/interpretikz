from kivy.graphics.texture import Texture
from kivy.graphics import Rectangle, Color, Mesh, Line
import numpy as np

class Relleno():
    
    def __validaciones(self,relleno=(),degradado=()):
        #VALIDACIONES
        error_relleno = False
        error_gradient = False
        def validar_relleno():
            if len(relleno) and len(relleno)>3 or len(relleno) and len(relleno)<3:
                print("DEVELOPER: El relleno no es valido.")
                return True
            else:
                #Si se aplica relleno...
                if len(relleno) == 3:
                    print("APLICO RELLENO")
                    self.color_rgb_mesh = relleno
                #Si no se aplica relleno...
                else:
                    self.color_rgb_mesh = [1,1,1]
                return False
        def validar_degradado():
            degradado_array = ("left_color", "right_color", "top_color", "middle_color", "bottom_color", "inner_color", "outer_color", "ball_color")
            for key in degradado:
                if not key in degradado_array:
                    print("DEVELOPER: El degradado no es valido. Coloco: "+key)
                    return True
            return False
        error_relleno = validar_relleno()
        error_gradient = validar_degradado()
        return not error_gradient and not error_relleno

    def figura_abierta(self,mesh_mode="line_loop",area_de_dibujar=None,posiciones_array=[],relleno=(),degradado={}):
        if(self.__validaciones(relleno,degradado)):
            self.degradado = degradado
            # print("Posiciones_Array")
            # print(posiciones_array)
            # print("self.color_rgb_mesh")
            # print(self.color_rgb_mesh)
            #Se dibuja el Mesh en el Widget Area_de_dibujar.
            with area_de_dibujar.canvas:
                Color(self.color_rgb_mesh[0],self.color_rgb_mesh[1],self.color_rgb_mesh[2])#Fondo blanco el Mesh si se aplica degradado.
                self.mesh = self.__construir_mesh(posiciones_array)
            mode_array = ('points', 'line_strip', 'line_loop', 'lines','triangles','triangle_strip', 'triangle_fan')
            if mesh_mode in mode_array:
                #Renderizar Mesh.
                self.__cambiar_mode(mesh_mode)
            else:
                print("DEVELOPER: El modo del Mesh no es valido. Coloco: "+mesh_mode)

    def __construir_mesh(self,posiciones_array):
        vertices = []
        vertices_sin_xy = []
        pos_index = 0
        indice_vertices_matriz = []
        indice_vertices = 0
        #[100, 100, 200, 100, 100, 200]
        porcentaje = 1/(len(posiciones_array)/2)#6 -> 0.166 (10%)
        porcentaje_array = np.arange(0.0,1.0,porcentaje).tolist()
        # print("porcentaje_array")
        # print(porcentaje_array)
        index_textura = 0
        #Coordenada X
        for point in posiciones_array:
            coordenadas_textura = [porcentaje_array[index_textura],porcentaje_array[index_textura]]
            #2 -> PUSHEA
            #4 -> PUSHEA
            #6 -> PUSHEA
            if not pos_index % 2 and pos_index:#2,4,6
                vertices_sin_xy.extend(coordenadas_textura)#vertices_sin_xy -> [100,100,0,0] pos_index = 2
                vertices_sin_xy.extend([point])#vertices_sin_xy -> [100,100,0,0,100] pos_index = 2
                vertices.extend(vertices_sin_xy)#vertices -> [100,100,0,0,100] pos_index = 2
                vertices_sin_xy = []#vertices_sin_xy -> [] pos_index = 2
                indice_vertices_matriz.append(indice_vertices)
                indice_vertices+=1
                index_textura+=1
            else:
                vertices_sin_xy.append(point)#[100,100] pos_index = 0,1,3,5
                if len(posiciones_array)-1 == pos_index:
                    vertices_sin_xy.extend(coordenadas_textura)
                    vertices.extend(vertices_sin_xy)
                    vertices_sin_xy = []
                    indice_vertices_matriz.append(indice_vertices)
                    indice_vertices+=1
                    index_textura+=1
            pos_index+=1
        print("MESH: indice_vertices_matriz")
        print(indice_vertices_matriz)#Indices -> [0,1,2]
        print("MESH: vertices")
        print(vertices)#Vertices -> [100,100,0,0,200,100,0,0,100,200,0,0]
        return Mesh(vertices=vertices, indices=indice_vertices_matriz)

    def __cambiar_mode(self, mode, *largs):
        self.mesh.mode = mode
        if self.degradado:
            print("APLICO DEGRADADO")
            self.color_rgb_mesh = [1,1,1]
            texture_mesh = self.aplicar_degradado(**self.degradado)
            self.mesh.texture = texture_mesh

    def aplicar_degradado(self,left_color=(),right_color=(),top_color=(),middle_color=(),bottom_color=(),inner_color=(),outer_color=(),ball_color=()):
        #left color, right color, top color, middle color, bottom color, inner color, outer color, ball color
        texture = Texture.create(size=(4,1), colorfmt='rgba')
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
        # print("degradient")
        # print(degradient)
        buf = bytes(degradient)
        texture.blit_buffer(buf, colorfmt='rgba', bufferfmt='ubyte')
        return texture