import numpy as np
import cv2, imutils
from kivy.graphics import Rectangle
from kivy.graphics import Color
from kivy.uix.widget import Widget
from kivy.app import App
from PIL import ImageDraw, Image
from random import randint as rint
import copy

class Relleno_lineas_libre():
    def __init__(self,area_dibujar,coordenadas_figura,colores,relleno=True,degradado=False):
        #SI ES LISTA
        #RGB A BGR
        if isinstance(colores, tuple):
            colores = [colores[2],colores[1],colores[0]]
        #Convertir numeros flotantes a INT.
        coordenadas_figura = [int(coordenada) for coordenada in coordenadas_figura]
        #Sacar valores Width y Height Minimos...
        indice = 1
        coordenada_individual_arr = []
        min_width = []
        min_height = []
        for coordenada in coordenadas_figura:
            coordenada_individual_arr.append(coordenada)
            if not indice%2:
                min_width.append(coordenada_individual_arr[0])
                min_height.append(coordenada_individual_arr[1])
                coordenada_individual_arr = []
            indice+=1
        min_width = np.array(min_width).min()
        min_height = np.array(min_height).min()
        #Modificar coordenadas originales, convirtiendolos a coordenadas que dibujen desde las coordenadas 0,0
        indice = 1
        coordenada_np = []
        for coordenada in coordenadas_figura:
            if indice%2:
                coordenada_np.append(coordenada-min_width)
            else:
                coordenada_np.append(coordenada-min_height)
            indice+=1
        #Sacar valores maximos de Height y Width usando las coordenadas nuevas.
        #Coordenadas nuevas transformados a unas coordenadas divididas por matrices [[0,0],[100,100],etc]
        coordenada_individual_arr = []
        height = []
        width = []
        coordenada_np_new = []
        for coordenada in coordenada_np:
            coordenada_individual_arr.append(coordenada)
            if not indice%2:
                width.append(coordenada_individual_arr[0])
                height.append(coordenada_individual_arr[1])
                coordenada_np_new.append(coordenada_individual_arr)
                coordenada_individual_arr = []
            indice+=1
        self.max_width = np.array(width).max()
        self.max_height = np.array(height).max()
        #Crear imagen a partir de coordenadas...
        contours = np.array(coordenada_np_new)
        img = np.zeros( (self.max_height,self.max_width) ) #Ancho y alto dependiendo del ancho y alto que ocupe la figura...
        cv2.fillPoly(img, pts =[contours], color=[255,255,255])#Relleno blanco...
        img = imutils.rotate(img, 180)
        self.img = cv2.flip(img, 1)
        self.ruta = './figura.png'
        cv2.imwrite(self.ruta, self.img)
        #Pasar imagen de color blanco a COLOR definido por el usuario...
        if relleno:
            self.__convertir_a_color(colores,relleno=True)
            self.__convertir_a_png()
        elif degradado:
            self.__convertir_a_color([1,1,1],relleno=True)
            self.__convertir_a_png()
            self.__convertir_a_color(colores,degradado=True)
            self.__convertir_a_png()
        #Dibujar en "Area de dibujar"
        pos_graphic = [float(min_width),float(min_height)]
        size_graphic = [float(self.max_width),float(self.max_height)]
        with area_dibujar.canvas:
            Rectangle(pos=pos_graphic,size=size_graphic,source=self.ruta)
        # print("Relleno")
        # print(relleno)
        # print("Degradado")
        # print(degradado)

    #Convertir pixeles blanco a X color...
    def __convertir_a_color(self,colores,relleno=False,degradado=False):
        self.img = cv2.imread(self.ruta)
        def aplicar_relleno():
            Conv_hsv_Gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
            _, mask = cv2.threshold(Conv_hsv_Gray, 0, 255,cv2.THRESH_BINARY_INV |cv2.THRESH_OTSU)
            indices = np.where(mask==0)#El Mask 0 es ignorar color Negro...
            self.img[indices[0], indices[1], :] = [color*255 for color in colores]#Convierte pixeles sobrantes (En este seria solo blanco) a rojo..
        def aplicar_degradado(left_color=(),right_color=(),top_color=(),middle_color=(),bottom_color=(),inner_color=(),outer_color=(),ball_color=()): 
            def gradient_3d(start_list, stop_list):
                result = self.img
                for i, (start, stop) in enumerate(zip(start_list, stop_list)):
                    for f in range(result.shape[0]):
                        degradado_raw = copy.copy(result)
                        degradado_raw[f,:, i] = np.linspace(start, stop, self.max_width).T
                        for c in range(result[f,:,i].shape[0]):
                            if result[f,c,i]:
                                result[f,c,i] = degradado_raw[f, c, i]
                Image.fromarray(np.uint8(result)).save(self.ruta, quality=95)
            if top_color and bottom_color:
                gradient_3d([color*255 for color in top_color],[color*255 for color in bottom_color])
        if relleno:
            aplicar_relleno()
        else:
            aplicar_degradado(**colores)

    def __convertir_a_png(self):
        img = self.img
        #Eliminar pixeles negros...
        h, w, c = img.shape#Se obtiene la dimencion de la imagen (h,w,c)
        # Añadido canal Alpha -- requerido para BGRA (B, G, R, A)
        image_bgra = np.concatenate([img, np.full((h, w, 1), 255, dtype=np.uint8)], axis=-1)
        # Crear una mask donde pixeles negros ([0, 0, 0]) son True
        white = np.all(img == [0, 0, 0], axis=-1)
        # Cambiar valores de Alpha a 0 para todos los pixeles negros
        image_bgra[white, -1] = 0
        cv2.imwrite(self.ruta, image_bgra)

class MainApp(App):
    def build(self):
        widget = Widget()
        dinosaurio_array = [100.0, 50.0, 100.0, 100.0, 50.0, 150.0, 50.0, 300.0, 100.0, 200.0, 150.0, 200.0, 250.0, 350.0, 250.0, 450.0, 350.0, 450.0, 350.0, 385.0, 325.0, 385.0, 325.0, 365.0, 350.0, 365.0, 350.0, 350.0, 300.0, 350.0, 300.0, 300.0, 350.0, 300.0, 350.0, 230.0, 325.0, 230.0, 325.0, 280.0, 300.0, 280.0, 300.0, 200.0, 200.0, 100.0, 200.0, 70.0, 230.0, 70.0, 230.0, 50.0, 170.0, 50.0, 170.0, 100.0, 130.0, 100.0, 130.0, 70.0, 160.0, 70.0, 160.0, 50.0, 100.0, 50.0]
        with widget.canvas:
            Color(1,1,1)
            Rectangle(size=[1000,1000],pos=widget.pos)
        Relleno_lineas_libre(widget,dinosaurio_array,{"top_color":(0,0,1),"bottom_color":(1,0,0)},False,True)
        return widget

if __name__ == "__main__":
    MainApp().run()
# dinosaurio_array = [100.0, 50.0, 100.0, 100.0, 50.0, 150.0, 50.0, 300.0, 100.0, 200.0, 150.0, 200.0, 250.0, 350.0, 250.0, 450.0, 350.0, 450.0, 350.0, 385.0, 325.0, 385.0, 325.0, 365.0, 350.0, 365.0, 350.0, 350.0, 300.0, 350.0, 300.0, 300.0, 350.0, 300.0, 350.0, 230.0, 325.0, 230.0, 325.0, 280.0, 300.0, 280.0, 300.0, 200.0, 200.0, 100.0, 200.0, 70.0, 230.0, 70.0, 230.0, 50.0, 170.0, 50.0, 170.0, 100.0, 130.0, 100.0, 130.0, 70.0, 160.0, 70.0, 160.0, 50.0, 100.0, 50.0]
# Relleno_lineas_libre([0,0],None,dinosaurio_array,(0,255,0))