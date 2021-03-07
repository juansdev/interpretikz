from kivy.graphics.texture import Texture
from kivy.graphics import Rectangle, Color, Mesh, Line
import numpy as np

class Degradado():
    orientation='vertical'
    def __init__(self,mesh_mode,area_de_dibujar,posiciones_array=[],relleno=(),degradients={}):
        print("Posiciones_Array")
        print(posiciones_array)
        #Se dibuja el Mesh en el Widget Area_de_dibujar.
        error_relleno = False
        if len(relleno) and len(relleno)>3 or len(relleno) and len(relleno)<3:
            error_relleno = True
            self.color_rgb_mesh = [1,1,1]
        else:
            print("ENTRE")
            if len(relleno) == 3:
                self.color_rgb_mesh = relleno    
            else:
                self.color_rgb_mesh = [1,1,1]
        print("self.color_rgb_mesh")
        print(self.color_rgb_mesh)
        with area_de_dibujar.canvas:
            Color(self.color_rgb_mesh[0],self.color_rgb_mesh[1],self.color_rgb_mesh[2])#Fondo blanco el Mesh
            self.mesh = self.Build_mesh(posiciones_array)
        mode_array = ('points', 'line_strip', 'line_loop', 'lines','triangle_strip', 'triangle_fan')
        degradients_array = ("left_color", "right_color", "top_color", "middle_color", "bottom_color", "inner_color", "outer_color", "ball_color")
        if mesh_mode in mode_array:
            error_gradient = False
            print("Degradients")
            print(degradients)
            for key in degradients:
                if not key in degradients_array:
                    error_gradient = True
                    print("DEVELOPER: El degradado no es valido. Coloco: "+key)
                    break
            if not error_gradient and not error_relleno:
                self.degradients = degradients
                #Renderizar Mesh.
                self.Change_mode(mesh_mode)
        else:
            print("DEVELOPER: El modo del Mesh no es valido. Coloco: "+mesh_mode)
    
    def Change_mode(self, mode, *largs):
        self.mesh.mode = mode
        if self.degradients:
            self.color_rgb_mesh = [1,1,1]
            texture_mesh = self.Apply_degradient(**self.degradients)
            self.mesh.texture = texture_mesh

    def Build_mesh(self,posiciones_array):
        vertices = []
        vertices_sin_xy = []
        pos_index = 0
        indice_vertices_matriz = []
        indice_vertices = 0
        #[100, 100, 200, 100, 100, 200]
        porcentaje = 1/(len(posiciones_array)/2)#6 -> 0.166 (10%)
        porcentaje_array = np.arange(0.0,1.0,porcentaje).tolist()
        print("porcentaje_array")
        print(porcentaje_array)
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
        print("MESH: vertices")
        print(vertices)#Vertices -> [100,100,0,0,200,100,0,0,100,200,0,0]
        print("MESH: indice_vertices_matriz")
        print(indice_vertices_matriz)#Indices -> [0,1,2]
        return Mesh(vertices=vertices, indices=indice_vertices_matriz)

    def Apply_degradient(self,left_color=(),right_color=(),top_color=(),middle_color=(),bottom_color=(),inner_color=(),outer_color=(),ball_color=()):
        #left color, right color, top color, middle color, bottom color, inner color, outer color, ball color
        texture = Texture.create(size=(1,4), colorfmt='rgba')
        if top_color and bottom_color:
            color_origen = top_color
            color_destino = bottom_color
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
        else:
            degradient = 0
        print("degradient")
        print(degradient)
        buf = bytes(degradient)
        texture.blit_buffer(buf, colorfmt='rgba', bufferfmt='ubyte')
        return texture