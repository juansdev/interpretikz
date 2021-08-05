from copy import deepcopy
import enum, math
from functools import partial
from kivy.uix.widget import Widget
import numpy as np
import re
from kivy.properties import ListProperty
from kivy.graphics import Color, Line, Rectangle, Ellipse, InstructionGroup

from kivy.clock import Clock
from bisect import bisect, insort
from .tools_validador_pytikz.validar_dibujar.validadores import Validadores
from .tools_validador_pytikz.validar_dibujar.graficar.relleno import Relleno
from .tools_validador_pytikz.validar_dibujar.graficar.relleno_lineas_libre import Relleno_lineas_libre
from .tools_validador_pytikz.validar_dibujar.graficar.animador import Animador

class Validador_pytikz():
    def __init__(self,comandos_tikz_validos,area_de_dibujar):
        self.comandos_tikz_validos = comandos_tikz_validos
        self.area_de_dibujar = area_de_dibujar
        self.mensajes_de_error = []
        self.estilo_global_local = {}
        self.comandos_global = {}
        self.index_animacion = 0
        self.Animar = Animador(self.area_de_dibujar)
    def validar_pytikz(self):
        for comando_tikz in self.comandos_tikz_validos:
            if(len(self.mensajes_de_error)>0):
                for error in self.mensajes_de_error:
                    print(error)
                    return []
            # self.comandos_tikz.append([self.comando_tikz,self.parametros_comando,self.posiciones,self.figura,self.funcion_de_figura])
            self.comandos_dibujar = ["draw","filldraw","fill","shade"]
            self.comandos_variables_tikz = ["tikzstyle","definecolor","tikzset","animarPytikz","foreach"]
            #Metricas validas
            self.metrica_validos = ["pt","cm"]
            if comando_tikz[0] in self.comandos_dibujar:
                self.__validar_dibujar(comando_tikz[0],comando_tikz[1],comando_tikz[2],comando_tikz[3],comando_tikz[4],self.area_de_dibujar)
            elif comando_tikz[0] in self.comandos_variables_tikz:
                self.__validar_variables_tikz(comando_tikz[0],comando_tikz[1],comando_tikz[2])
            else:
                print("Todavia el comando no esta habilitado.")

        if(len(self.mensajes_de_error)>0):
            for error in self.mensajes_de_error:
                print(error)
                return []
    def __validar_dibujar(self,comando_tikz,parametros_comando,draw_posicion,figuras,funcion_de_figura,area_de_dibujar,habilitado_animador=False):
        if comando_tikz == "draw" or comando_tikz == "filldraw" or comando_tikz == "fill" or comando_tikz=="shade":
            #Estilos predeterminados
            self.degradients = {}
            self.fill = (1,1,1) if comando_tikz == "draw" or comando_tikz == "shade" else (0,0,0) if comando_tikz == "fill" else (0,0,0)
            self.draw = (0,0,0) if comando_tikz == "draw" or comando_tikz == "shade" else (1,1,1) if comando_tikz == "fill" else (0,0,0)
            self.tipo_de_linea = ""
            self.line_width = 1.0
            #Estilos sujeto a cambio debido a parametros definidos en comando.
            estilos_predeterminados = {
                "fill":self.fill,
                "draw":self.draw,
                "degradients":self.degradients,
                "tipo_de_linea":self.tipo_de_linea,
                "line_width":self.line_width,
                "metrica_validos":self.metrica_validos
            }
            self.validadores = Validadores(estilos_predeterminados)
            indice = 0
            for parametro in parametros_comando:
                tupla_validada = False
                diccionario_validada = False
                #Explorar por []
                if indice == 0:
                    for estilo in parametro:
                        estilo = estilo.strip()
                        if estilo in list(self.estilo_global_local.keys()):
                            # print("DETECTADO ESTILO GLOBAL O LOCAL SIN PARAMETROS")
                            # print(estilo)
                            #[[], {'draw': 'red'}]
                            parametros_estilo_global_local = self.estilo_global_local[estilo]
                            indice_estilo_global_local = 0
                            for parametro_estilo_global_local in parametros_estilo_global_local:
                                #Explorar por []
                                if indice_estilo_global_local == 0:
                                    array_estilos_validados = self.validadores.validar_estilos("tupla",parametro_estilo_global_local)
                                    mensajes_de_error_generados = array_estilos_validados[len(array_estilos_validados)-1]
                                    if not len(mensajes_de_error_generados):
                                        self.degradients = array_estilos_validados[0]
                                        self.fill = array_estilos_validados[1]
                                        self.draw = array_estilos_validados[2]
                                        self.tipo_de_linea = array_estilos_validados[3]
                                        self.line_width = array_estilos_validados[4]
                                    else:
                                        self.mensajes_de_error.extend(mensajes_de_error_generados)
                                #Explorar por {}
                                elif indice_estilo_global_local == 1:
                                    #Recorrer keys de {}
                                    keys_diccionario = list(parametro_estilo_global_local.keys())
                                    # print("keys_diccionario")
                                    # print(keys_diccionario)
                                    array_estilos_validados = self.validadores.validar_estilos("diccionario",keys_diccionario,parametro_estilo_global_local)
                                    mensajes_de_error_generados = array_estilos_validados[len(array_estilos_validados)-1]
                                    if not len(mensajes_de_error_generados):
                                        self.degradients = array_estilos_validados[0]
                                        self.fill = array_estilos_validados[1]
                                        self.draw = array_estilos_validados[2]
                                        self.tipo_de_linea = array_estilos_validados[3]
                                        self.line_width = array_estilos_validados[4]
                                    else:
                                        self.mensajes_de_error.extend(mensajes_de_error_generados)
                                indice_estilo_global_local+=1
                        elif not tupla_validada:
                            array_estilos_validados = self.validadores.validar_estilos("tupla",parametro)
                            mensajes_de_error_generados = array_estilos_validados[len(array_estilos_validados)-1]
                            if not len(mensajes_de_error_generados):
                                self.degradients = array_estilos_validados[0]
                                self.fill = array_estilos_validados[1]
                                self.draw = array_estilos_validados[2]
                                self.tipo_de_linea = array_estilos_validados[3]
                                self.line_width = array_estilos_validados[4]
                            else:
                                self.mensajes_de_error.extend(mensajes_de_error_generados)
                            tupla_validada = True
                #Explorar por {}
                elif indice == 1:
                    #Recorrer keys de {}
                    keys_diccionario = list(parametro.keys())
                    for key in keys_diccionario:
                        key_original = key
                        key = key.strip()
                        # print("key")
                        # print(key)
                        # print("list(self.estilo_global_local.keys())")
                        # print(list(self.estilo_global_local.keys()))
                        if key in list(self.estilo_global_local.keys()):
                            # print("DETECTADO ESTILO GLOBAL O LOCAL CON PARAMETROS")
                            # print("key")
                            # print(key)
                            #\draw[estilo global = {red}{solid}] (0,0) rectangle (2.5, 2.5);
                            #{'estilo global ': ' {red}{solid}'}
                            variable_valores_definido = parametro[key_original].strip()
                            variable_valores_definido = [valor for valor in variable_valores_definido.split("}") if valor]
                            variable_valores_definido_limpio = []
                            for e in variable_valores_definido:
                                if e.find("{")!=-1:
                                    variable_valores_definido_limpio.append(e[e.find("{")+1::])
                                else:
                                    variable_valores_definido_limpio.append(e)
                            variable_valores_definido = variable_valores_definido_limpio
                            variable_valores_indefinidos = self.estilo_global_local[key]
                            key_variable_indefinido = list(variable_valores_indefinidos.keys())[0]
                            parametros_estilo_global_local = variable_valores_indefinidos[key_variable_indefinido]
                            #[[['#2'], {'line width': '1.25pt', 'draw ': ' #1'}], [[], {'estilo global/.default ': '[cyan,dotted]'}]]
                            indice_estilo_global_local = 0
                            indice_estilo_global_local_parametro = 0
                            for parametro_estilo_global_local in parametros_estilo_global_local:
                                indice_estilo_global_local_parametro = 1 if indice_estilo_global_local > 1 else 0
                                indice_estilo_global_local = indice_estilo_global_local if indice_estilo_global_local <2 else 0
                                parametro_estilo_global_local = parametros_estilo_global_local[indice_estilo_global_local_parametro][indice_estilo_global_local]
                                #Solo recorre por [['#2'], {'line width': '1.25pt', 'draw ': ' #1'}]
                                if not indice_estilo_global_local_parametro:
                                    #Explorar por []
                                    if indice_estilo_global_local == 0:
                                        for key in parametro_estilo_global_local:
                                            key = key.strip()
                                            if key.find("#") != -1:
                                                # print("variable_valores_definido")
                                                # print(variable_valores_definido)
                                                indice = int(key[key.find("#")+1::])-1 #EJ #2 -> 
                                                # print("indice a utilizar en variable_valores_definido")
                                                # print(indice)
                                                try:
                                                    estilo = variable_valores_definido[indice] #Red, Solid etc...
                                                except:
                                                    #{'estilo global/.default ': '[cyan,5pt]'}
                                                    parametro_estilo_global_local_1 = parametros_estilo_global_local[1][1]
                                                    str1 = list(parametro_estilo_global_local_1.values())[0]#'[cyan,5pt]'
                                                    str2 = str1.replace(']','').replace('[','')
                                                    valores_predeterminado = str2.replace('"','').split(",")#['cyan', '5pt']
                                                    estilo = valores_predeterminado[indice]
                                                    # print("Estilo predeterminado seleccionado "+estilo)
                                                array_estilos_validados = self.validadores.validar_estilos("tupla",estilo)
                                                mensajes_de_error_generados = array_estilos_validados[len(array_estilos_validados)-1]
                                                if not len(mensajes_de_error_generados):
                                                    self.degradients = array_estilos_validados[0]
                                                    self.fill = array_estilos_validados[1]
                                                    self.draw = array_estilos_validados[2]
                                                    self.tipo_de_linea = array_estilos_validados[3]
                                                    self.line_width = array_estilos_validados[4]
                                                else:
                                                    self.mensajes_de_error.extend(mensajes_de_error_generados)
                                    #Explorar por {}
                                    elif indice_estilo_global_local == 1:
                                        #Recorrer keys de {}
                                        values_diccionario = list(parametro_estilo_global_local.values())
                                        indice_key_seleccionado = 0
                                        for value in values_diccionario:
                                            if value.find("#")!=-1:
                                                # print("variable_valores_definido")
                                                # print(variable_valores_definido)
                                                indice = int(value[value.find("#")+1::])-1 #EJ #2 -> 1
                                                # print("indice a utilizar en variable_valores_definido")
                                                # print(indice)
                                                try:
                                                    estilo = variable_valores_definido[indice] #Red, Solid etc...
                                                except:
                                                    #{'estilo global/.default ': '[cyan,5pt]'}
                                                    parametro_estilo_global_local_1 = parametros_estilo_global_local[1][1]
                                                    str1 = list(parametro_estilo_global_local_1.values())[0]#'[cyan,5pt]'
                                                    str2 = str1.replace(']','').replace('[','')
                                                    valores_predeterminado = str1.replace('"','').split(",")#['cyan', '5pt']
                                                    estilo = valores_predeterminado[indice]
                                                    # print("Estilo predeterminado seleccionado "+estilo)
                                                indice_key = 0
                                                for key in list(parametro_estilo_global_local.keys()):
                                                    if indice_key == indice_key_seleccionado:
                                                        key = key.strip()
                                                        array_estilos_validados = self.validadores.validar_estilos("diccionario",key,estilo)
                                                        mensajes_de_error_generados = array_estilos_validados[len(array_estilos_validados)-1]
                                                        if not len(mensajes_de_error_generados):
                                                            self.degradients = array_estilos_validados[0]
                                                            self.fill = array_estilos_validados[1]
                                                            self.draw = array_estilos_validados[2]
                                                            self.tipo_de_linea = array_estilos_validados[3]
                                                            self.line_width = array_estilos_validados[4]
                                                        else:
                                                            self.mensajes_de_error.extend(mensajes_de_error_generados)
                                                    indice_key+=1
                                            indice_key_seleccionado+=1
                                else:
                                    break
                                indice_estilo_global_local+=1
                        elif not diccionario_validada:
                            #Codigos COLOR
                            keys_color = [estilo_global for estilo_global in self.estilo_global_local.keys()]
                            keys_color_invocados = list(parametro.values())
                            # print("Colores globales existentes")
                            # print(keys_color)
                            # print("Parametros establecidos")
                            # print(keys_color_invocados)
                            if True in np.in1d(keys_color_invocados,keys_color):
                                index_keys_color = []
                                for index,value in enumerate(keys_color):
                                    if value in keys_color_invocados:
                                        index_keys_color.append(index)
                                # print("Index donde el Color fue invocado...")
                                # print(index_keys_color)
                                keys_color_invocados = []
                                codigos_color_invocados = []
                                for index,value in enumerate(self.estilo_global_local.values()):
                                    if index in index_keys_color:
                                        keys_color_invocados.append(keys_color[index])
                                        codigos_color_invocados.append(value)
                                codigos_color = [codigo_color for codigo_color in codigos_color_invocados]
                                #Si existe codigos rgb...
                                codigos_rgb = [{index:list(color[1].values())[0]} for index,color in enumerate(codigos_color) if list(color[1].keys())[0].find("RGB") != -1]
                                # print(codigos_rgb)
                                print("Antes de actualizar")
                                print(parametro)
                                i = 0
                                for key in parametro:
                                    if parametro[key] in keys_color:
                                        #Corresponde a un valor RGB?
                                        for codigo in codigos_rgb:
                                            if list(codigo.keys())[0] == i:
                                                for k in parametro:
                                                    if parametro[k] == keys_color_invocados[i]:
                                                        # print("La key...")
                                                        # print(parametro[k])
                                                        # print("Corresponde a un codigo RGB, en el Index: ",i)
                                                        # print(list(codigo.values())[0])
                                                        parametro[k] = list(codigo.values())[0]
                                        i+=1
                            array_estilos_validados = self.validadores.validar_estilos("diccionario",keys_diccionario,parametro)
                            mensajes_de_error_generados = array_estilos_validados[len(array_estilos_validados)-1]
                            if not len(mensajes_de_error_generados):
                                self.degradients = array_estilos_validados[0]
                                self.fill = array_estilos_validados[1]
                                self.draw = array_estilos_validados[2]
                                self.tipo_de_linea = array_estilos_validados[3]
                                self.line_width = array_estilos_validados[4]
                            else:
                                self.mensajes_de_error.extend(mensajes_de_error_generados)
                            diccionario_validada = True
                indice+=1

            #FIGURA SIN PARAMETROS
            if(len(funcion_de_figura[0]) == 0 and len(list(funcion_de_figura[1].keys())) == 0):
                if not len(self.mensajes_de_error):
                    for figura in figuras:
                        #Dibujar rectangulo
                        #\draw[red, dotted, line width= 3pt] (0,0) rectangle (50, 50);
                        #\draw[line with=5pt, draw = cyan,dashed] (1,1) rectangle (2.5, 2.5);
                        if(figura=="rectangle"):
                            punto_inicial_x_y = self.validadores.validar_metrica(draw_posicion[0][0])
                            punto_final_x_y = self.validadores.validar_metrica(draw_posicion[0][1])
                            ancho = self.validadores.validar_metrica(draw_posicion[1][0])
                            alto = self.validadores.validar_metrica(draw_posicion[1][1])
                            rectangulo_dibujado_lineas = [punto_inicial_x_y, punto_final_x_y, punto_inicial_x_y, punto_final_x_y+alto, punto_inicial_x_y+ancho, punto_final_x_y+alto, punto_inicial_x_y+ancho, punto_final_x_y, punto_inicial_x_y, punto_final_x_y]
                            #Dibujar contenido rectangulo
                            #DEGRADADO RECTANGULO
                            if self.degradients:
                                Relleno(area_de_dibujar,figura,self.degradients,(punto_inicial_x_y,punto_final_x_y),(ancho,alto),animador=habilitado_animador)
                            #RELLENO RECTANGULO
                            else:
                                if not habilitado_animador:
                                    figura = InstructionGroup()
                                    figura.add(Color(self.fill[0], self.fill[1], self.fill[2]))
                                    figura.add(Rectangle(pos=(punto_inicial_x_y,punto_final_x_y),size=(ancho,alto)))
                                    area_de_dibujar.canvas.add(figura)
                                else:
                                    self.Animar.figura_a_png(habilitado_animador["generar_gif"],"rectangle",(ancho,alto),(punto_inicial_x_y,punto_final_x_y),(self.fill[0], self.fill[1], self.fill[2]),self.tipo_de_linea,rectangulo_dibujado_lineas,(self.draw[0], self.draw[1], self.draw[2]),self.line_width)
                            #Dibujar borde rectangulo
                            #Si hay separacion de lineas...
                            if self.tipo_de_linea:
                                if not habilitado_animador:
                                    figura = InstructionGroup()
                                    figura.add(Color(self.draw[0], self.draw[1], self.draw[2]))
                                    figura.add(Line(points=rectangulo_dibujado_lineas, dash_offset=10, dash_length=5))
                                    area_de_dibujar.canvas.add(figura)
                            #Si no hay...
                            else:
                                if not habilitado_animador:
                                    figura = InstructionGroup()
                                    figura.add(Color(self.draw[0], self.draw[1], self.draw[2]))
                                    figura.add(Line(points=rectangulo_dibujado_lineas,width=self.line_width))
                                    area_de_dibujar.canvas.add(figura)
                        #DIBUJAR ARCO
                        #\draw[color=ColorA,line width=0.1cm,rounded corners=2ex] (100,100) arc (0:90:5cm);
                        elif(figura=="arc"):
                            indice = 0
                            for posicion in draw_posicion:
                                #Indice parametros validos del Arc...
                                if len(posicion)==3:
                                    indice = indice
                                    break
                                indice+=1

                            posicion_x = self.validadores.validar_metrica(draw_posicion[0][0])
                            posicion_y = self.validadores.validar_metrica(draw_posicion[0][1])

                            angulo_inicial = float(450) if float(draw_posicion[indice][0]) == 0.0 else float(450-(float(draw_posicion[indice][0])))
                            angulo_final = float(450) if float(draw_posicion[indice][1]) == 0.0 else float(450-(float(draw_posicion[indice][1])))
                            radio = self.validadores.validar_metrica(draw_posicion[indice][2])
                            #Eliminar parametro Arc utilizado
                            # print("draw_posicion original")
                            # print(draw_posicion)
                            self.angulo_final_arc = draw_posicion[indice][1]
                            self.longitud_arc = radio
                            del draw_posicion[indice:indice+1]
                            # print("draw_posicion despues de eliminar el Arc utilizado")
                            # print(draw_posicion)
                            #DIBUJAR CONTENIDO ARC
                            #Si aplica relleno o degradado...
                            if self.fill != (1,1,1) or self.degradients:
                                if self.degradients:
                                    #Aplicar degradado a la figura...
                                    Relleno(area_de_dibujar,figura,self.degradients,(posicion_x,posicion_y),(radio*2,radio*2),angulo_inicial, angulo_final,animador=habilitado_animador)
                                else:
                                    #Aplicar relleno a la figura...
                                    if not habilitado_animador:
                                        figura = InstructionGroup()
                                        figura.add(Color(self.fill[0],self.fill[1],self.fill[2]))
                                        figura.add(Ellipse(pos=(posicion_x,posicion_y),size=(radio*2,radio*2),angle_start=angulo_inicial, angle_end=angulo_final))
                                        area_de_dibujar.canvas.add(figura)
                                    else:
                                        self.Animar.figura_a_png(habilitado_animador["generar_gif"],"arc",(radio*2,radio*2),(posicion_x,posicion_y),(self.fill[0], self.fill[1], self.fill[2]),self.tipo_de_linea,[posicion_x,posicion_y,radio,angulo_inicial,angulo_final],(self.draw[0], self.draw[1], self.draw[2]),self.line_width,angle_start=angulo_inicial, angle_end=angulo_final)
                            posicion_x+=radio
                            posicion_y+=radio
                            self.posicion_x_arc = posicion_x
                            self.posicion_y_arc = posicion_y
                            #DIBUJAR ARC
                            #ARCO CON LINEAS DISCONTINUADAS
                            if self.tipo_de_linea:
                                if not habilitado_animador:
                                    figura = InstructionGroup()
                                    figura.add(Color(self.draw[0], self.draw[1], self.draw[2]))
                                    figura.add(Line(circle=[posicion_x,posicion_y,radio,angulo_inicial,angulo_final], dash_offset=10, dash_length=5))
                                    area_de_dibujar.canvas.add(figura)
                            #Si no hay...
                            #ARCO SIN LINEAS DISCONTINUADAS
                            else:
                                if not habilitado_animador:
                                    figura = InstructionGroup()
                                    figura.add(Color(self.draw[0], self.draw[1], self.draw[2]))
                                    figura.add(Line(circle=[posicion_x,posicion_y,radio,angulo_inicial,angulo_final],width=self.line_width))
                                    area_de_dibujar.canvas.add(figura)
                        #DIBUJAR CIRCULO
                        #\draw[draw=red,fill=yellow] (0,0) circle (1cm);
                        elif(figura=="circle"):
                            posicion_x = self.validadores.validar_metrica(draw_posicion[0][0])
                            posicion_y = self.validadores.validar_metrica(draw_posicion[0][1])
                            radio_es_valido = True
                            try:
                                radio = self.validadores.validar_metrica(draw_posicion[1])
                            except:
                                self.mensajes_de_error.append("Error cerca de "+figura+" se esperaba un valor de Radio o de posicion X y Y validos.")
                                radio_es_valido = False
                            #Line:
                            # circle: (60,60,60,90,180)#CIRCULO CERRADO, 40 DE RADIO
                            if radio_es_valido:
                                #DIBUJAR CONTENIDO CIRCULO
                                ancho = radio*2
                                alto = radio*2
                                if self.degradients:
                                    #APLICAR DEGRADADO AL CIRCULO
                                    Relleno(area_de_dibujar,figura,self.degradients,(posicion_x,posicion_y),(ancho,alto),animador=habilitado_animador)
                                else:
                                    #RELLENO CIRCULO
                                    if not habilitado_animador:
                                        figura = InstructionGroup()
                                        figura.add(Color(self.fill[0], self.fill[1], self.fill[2]))
                                        figura.add(Ellipse(pos=(posicion_x,posicion_y),size=(ancho,alto)))
                                        area_de_dibujar.canvas.add(figura)
                                    else:
                                        self.Animar.figura_a_png(habilitado_animador["generar_gif"],"circle",(ancho,alto),(posicion_x,posicion_y),(self.fill[0], self.fill[1], self.fill[2]),self.tipo_de_linea,[posicion_x,posicion_y,radio],(self.draw[0], self.draw[1], self.draw[2]),self.line_width)
                                #DIBUJAR BORDE CIRCULO
                                posicion_x+=radio
                                posicion_y+=radio
                                if self.tipo_de_linea:
                                    if not habilitado_animador:
                                        figura = InstructionGroup()
                                        figura.add(Color(self.draw[0], self.draw[1], self.draw[2]))
                                        figura.add(Line(circle=[posicion_x,posicion_y,radio], dash_offset=10, dash_length=self.line_width))
                                        area_de_dibujar.canvas.add(figura)
                                #Si no hay...
                                else:
                                    if not habilitado_animador:
                                        figura = InstructionGroup()
                                        figura.add(Color(self.draw[0], self.draw[1], self.draw[2]))
                                        figura.add(Line(circle=[posicion_x,posicion_y,radio], width=self.line_width))
                                        area_de_dibujar.canvas.add(figura)
                        #DIBUJAR LINEAS BEZIER
                        #\draw[left color=yellow, bottom color=orange, right color=red,rounded] (0,100) .. controls (100,200) and (200,300) .. (300,400) .. (200,100) .. (300,200);
                        elif(figura=="controls"):
                            coordenadas = []
                            indice = 0
                            figuras_control = []
                            for figura in figuras:
                                if figura == "controls":
                                    figuras_control.append(figura)
                            indice_controls_inicial = 1
                            indice_controls_final = 1
                            for posicion in draw_posicion:
                                if len(figuras_control)>1:
                                    if indice_controls_final < 4:
                                        #Posiciones Control
                                        coordenadas.append(self.validadores.validar_metrica(posicion[0]))
                                        coordenadas.append(self.validadores.validar_metrica(posicion[1]))
                                    elif indice_controls_final >= 4:
                                        break
                                    if indice>0:
                                        #Maximo-Minimo 3 posiciones
                                        indice_controls_final+=1
                                else:
                                    #Posiciones Control
                                    coordenadas.append(self.validadores.validar_metrica(posicion[0]))
                                    coordenadas.append(self.validadores.validar_metrica(posicion[1]))
                                indice += 1
                            #Eliminar parametro Controls utilizado
                            if len(figuras_control)>1:
                                # print("draw_posicion original")
                                # print(draw_posicion)
                                draw_posicion[0] = (str(coordenadas[len(coordenadas)-2]),str(coordenadas[len(coordenadas)-1]))
                                del draw_posicion[indice_controls_inicial:indice_controls_final]
                                # print("draw_posicion despues de eliminar el Control utilizado")
                                # print(draw_posicion)
                            if len(coordenadas)>=4:
                                #Dibujar en el area de dibujado...
                                #Si hay separacion de lineas...
                                if not habilitado_animador:
                                    if self.tipo_de_linea:
                                        figura = InstructionGroup()
                                        figura.add(Color(self.draw[0], self.draw[1], self.draw[2]))
                                        figura.add(Line(bezier=coordenadas, dash_offset=10, dash_length=5))
                                        area_de_dibujar.canvas.add(figura)
                                    #Si no hay...
                                    else:
                                        figura = InstructionGroup()
                                        figura.add(Color(self.draw[0], self.draw[1], self.draw[2]))
                                        figura.add(Line(bezier=coordenadas, width=self.line_width))
                                        area_de_dibujar.canvas.add(figura)
                            else:
                                print("Error cerca de "+str(coordenadas[len(coordenadas)-1])+" se esperaba posiciones de Origen y de Destino")
                        #Si hay figura (--)...
                        #\draw[line width= 1.5pt, fill = yellow, draw  = black](100,100) -- (200,0) -- (50,300) -- (40,200) -- cycle;
                        elif(figura=="--"):
                            coordenadas = []
                            coordenadas_cycle_arc = []
                            draw_posicion_normal = []
                            
                            def posicion_con_angulo(posicion_angulo_str):
                                posicion_angulo_array = posicion_angulo_str.split(":")
                                #AUMENTA Y HASTA Y45:
                                # ANGULO 45
                                # \draw (0,0) -- (45:1cm); -> X1cm Y45
                                # ANGULO 10
                                # \draw (0,0) -- (10:1cm); -> X1cm Y10
                                # ANGULO 0
                                # \draw (0,0) -- (0:1cm); -> X1cm Y0
                                angulo = posicion_angulo_array[0]
                                try:
                                    float(angulo)
                                except:
                                    self.mensajes_de_error.append("Error cerca de '"+str(angulo)+"' se esperaba un valor FLOAT o INTEGER")
                                    return False
                                angulo = float(angulo)
                                longitud = self.validadores.validar_metrica(posicion_angulo_array[1])
                                if angulo>=0 and angulo<=45:                   
                                    posicion_angulo_array = (longitud,angulo)                 
                                    return posicion_angulo_array
                                elif angulo and angulo>45 and angulo<=90:
                                    x = 45-(angulo-45)
                                    posicion_angulo_array = (x,longitud)
                                    return posicion_angulo_array
                                else:
                                    self.mensajes_de_error.append("Error cerca de '"+str(angulo)+"' el valor debe de ser positivo.")
                                    return False
                            
                            for posicion in draw_posicion:
                                if type(posicion) is list and len(posicion) == 2:
                                    draw_posicion_normal.append(posicion)
                                elif type(posicion) is str:
                                    posicion_array = posicion.split(":")
                                    if len(posicion_array)==2:
                                        draw_posicion_normal.append(posicion)
                                    elif posicion == "cycle":
                                        draw_posicion_normal.append(posicion)
                            
                            indice = 0
                            for posicion in draw_posicion_normal:
                                if len(coordenadas) < 4:
                                    if not indice and type(posicion) is str:
                                        self.mensajes_de_error.append("La primera posicion debe de tener como valor una Coordenada X y una Y.")
                                        break
                                    #La posicion es un angulo
                                    elif type(posicion) is str:
                                        posiciones = posicion_con_angulo(posicion)
                                        try:
                                            posicion_x = posiciones[0]
                                            posicion_y = posiciones[1]
                                        except:
                                            break
                                        coordenadas.append(coordenadas[0]+posicion_x)
                                        coordenadas.append(coordenadas[1]+posicion_y)
                                    else:
                                        if("arc" in figuras):
                                            coordenadas.append(self.posicion_x_arc)
                                            coordenadas.append(self.posicion_y_arc)
                                        else:
                                            coordenadas.append(self.validadores.validar_metrica(posicion[0]))
                                            coordenadas.append(self.validadores.validar_metrica(posicion[1]))
                                elif len(coordenadas) >= 4 and posicion != "cycle":
                                    #HASTA NUEVA COORDENADA X,Y
                                    coordenadas.append(self.validadores.validar_metrica(posicion[0]))
                                    coordenadas.append(self.validadores.validar_metrica(posicion[1]))
                                #Si es Cycle...
                                else:
                                    if "arc" in figuras:
                                        #Cerrar desde la posicion del ultimo angulo dibujado de un Arc.
                                        #Hassta el centro (radio) de la posicion del Arc.
                                        posiciones = posicion_con_angulo(str(self.angulo_final_arc)+":"+str(self.longitud_arc))
                                        # print("self.angulo_final_arc")
                                        # print(self.angulo_final_arc)
                                        # print("self.longitud_arc")
                                        # print(self.longitud_arc)
                                        coordenada_arc_x = posiciones[0]+coordenadas[0]
                                        coordenada_arc_y = posiciones[1]+coordenadas[1]
                                        #DESDE ANTERIOR COORDENADA X,Y
                                        coordenadas_cycle_arc.append(coordenada_arc_x)
                                        coordenadas_cycle_arc.append(coordenada_arc_y)
                                        #HASTA COORDENADA ORIGEN X,Y
                                        coordenadas_cycle_arc.append(self.posicion_x_arc)
                                        coordenadas_cycle_arc.append(self.posicion_y_arc)
                                    elif posicion=="cycle":
                                        #HASTA COORDENADA ORIGEN X,Y
                                        coordenadas.append(self.validadores.validar_metrica(str(coordenadas[0])))
                                        coordenadas.append(self.validadores.validar_metrica(str(coordenadas[1])))
                                indice+=1
                            if not len(self.mensajes_de_error):
                                if len(coordenadas)>=4:
                                    #DIBUJAR LINEAS CON CONTENIDO
                                    #Si aplica relleno o degradado...
                                    if self.fill != (1,1,1) or self.degradients:
                                        if self.fill != (1,1,1):
                                            #Crear Imagen con relleno y aplicarlo en el Source de un Rectangle para luego dibujarlo en el Area_de_dibujar
                                            Relleno_lineas_libre(area_de_dibujar,coordenadas,self.fill,animador=habilitado_animador)
                                        else:
                                            Relleno_lineas_libre(area_de_dibujar,coordenadas,self.degradients,False,True,animador=habilitado_animador)
                                    #DIBUJAR LINEAS
                                    #Si hay separacion de lineas...
                                    if self.tipo_de_linea:
                                        if len(coordenadas_cycle_arc):
                                            if not habilitado_animador:
                                                figura = InstructionGroup()
                                                figura.add(Color(self.draw[0], self.draw[1], self.draw[2]))
                                                figura.add(Line(points=coordenadas_cycle_arc, dash_offset=10, dash_length=5))
                                                area_de_dibujar.canvas.add(figura)
                                        if not habilitado_animador:
                                            figura = InstructionGroup()
                                            figura.add(Color(self.draw[0], self.draw[1], self.draw[2]))
                                            figura.add(Line(points=coordenadas, dash_offset=10, dash_length=5))
                                            area_de_dibujar.canvas.add(figura)
                                    #Si no hay...
                                    else:
                                        if len(coordenadas_cycle_arc):
                                            if not habilitado_animador:
                                                figura = InstructionGroup()
                                                figura.add(Color(self.draw[0], self.draw[1], self.draw[2]))
                                                figura.add(Line(points=coordenadas_cycle_arc, width=self.line_width))
                                                area_de_dibujar.canvas.add(figura)
                                        if not habilitado_animador:
                                            figura = InstructionGroup()
                                            figura.add(Color(self.draw[0], self.draw[1],self.draw[2]))
                                            figura.add(Line(points=coordenadas, width=self.line_width))
                                            area_de_dibujar.canvas.add(figura)
                                else:
                                    self.mensajes_de_error.append("Error cerca de "+str(coordenadas[len(coordenadas)-1])+" se esperaba posiciones de Origen y de Destino")
                        #No tiene figura
                        else:
                            self.mensajes_de_error.append("Error el comando TikZ '"+comando_tikz+"' no tiene una figura valida.")
                    
            #FIGURA CON PARAMETROS
            else:
                if not len(self.mensajes_de_error):
                    for figura in figuras:
                        #DIBUJAR ARCO
                        #\draw[bottom color=cyan!60!black, top color=red, middle color = blue!20!white] (100,100) arc[start angle=0, end angle=90, radius=5cm];
                        if(figura=="arc"):
                            posicion_x = self.validadores.validar_metrica(draw_posicion[0][0])
                            posicion_y = self.validadores.validar_metrica(draw_posicion[0][1])
                            
                            diccionario_funcion_figura = {}
                            for key in list(funcion_de_figura[1].keys()):
                                key_nueva = key.strip()
                                diccionario_funcion_figura[key_nueva] = funcion_de_figura[1][key]
                            start_angle = diccionario_funcion_figura["start angle"] if "start angle" in list(diccionario_funcion_figura.keys()) else "0.0"
                            end_angle = diccionario_funcion_figura["end angle"] if "end angle" in list(diccionario_funcion_figura.keys()) else "360.0"
                            radius = diccionario_funcion_figura["radius"] if "radius" in list(diccionario_funcion_figura.keys()) else "10.0"
                            angulo_inicial = 450.0 if self.validadores.validar_metrica(start_angle) == 0.0 else 450-(self.validadores.validar_metrica(start_angle))
                            angulo_final = 450.0 if self.validadores.validar_metrica(end_angle) == 0.0 else 450-(self.validadores.validar_metrica(end_angle))

                            radio_es_valido = True

                            try:
                                radio = self.validadores.validar_metrica(radius)
                            except:
                                self.mensajes_de_error.append("Error cerca de "+figura+" se esperaba un valor de Radio o de posicion X y Y validos.")
                                radio_es_valido = False

                            if radio_es_valido:
                                #DIBUJAR CONTENIDO ARC
                                #Si aplica relleno o degradado...
                                if self.fill != (1,1,1) or self.degradients:
                                    if self.degradients:
                                        #Aplicar degradado a la figura...
                                        Relleno(area_de_dibujar,figura,self.degradients,(posicion_x,posicion_y),(radio*2,radio*2),angulo_inicial,angulo_final,animador=habilitado_animador)
                                    else:
                                        #Aplicar relleno a la figura...
                                        if not habilitado_animador:
                                            figura = InstructionGroup()
                                            figura.add(Color(self.fill[0],self.fill[1],self.fill[2]))
                                            figura.add(Ellipse(pos=(posicion_x,posicion_y),size=(radio*2,radio*2),angle_start=angulo_inicial, angle_end=angulo_final))
                                            area_de_dibujar.canvas.add(figura)
                                        else:
                                            self.Animar.figura_a_png(habilitado_animador["generar_gif"],"arc",(radio*2,radio*2),(posicion_x,posicion_y),(self.fill[0],self.fill[1],self.fill[2]),self.tipo_de_linea,[posicion_x,posicion_y,radio,angulo_inicial,angulo_final],(self.draw[0], self.draw[1], self.draw[2]),self.line_width,angle_start=angulo_inicial, angle_end=angulo_final)
                                #DIBUJAR ARC
                                posicion_x+=radio
                                posicion_y+=radio
                                #BORDE CON LINEAS DISCONTINUADAS
                                if self.tipo_de_linea:
                                    if not habilitado_animador:
                                        figura = InstructionGroup()
                                        figura.add(Color(self.draw[0], self.draw[1], self.draw[2]))
                                        figura.add(Line(circle=[posicion_x,posicion_y,radio,angulo_inicial,angulo_final], dash_offset=10, dash_length=5))
                                        area_de_dibujar.canvas.add(figura)
                                #Si no hay...
                                else:
                                    if not habilitado_animador:
                                        figura = InstructionGroup()
                                        figura.add(Color(self.draw[0], self.draw[1], self.draw[2]))
                                        figura.add(Line(circle=[posicion_x,posicion_y,radio,angulo_inicial,angulo_final],width=self.line_width))
                                        area_de_dibujar.canvas.add(figura)
                        #No tiene figura
                        else:
                            self.mensajes_de_error.append("Error el comando TikZ '"+comando_tikz+"' no tiene una figura valida.")
    def __validar_variables_tikz(self,comando_tikz,funcion_de_comando,parametros_comando,habilitado_animador=False):
        def animar(nuevo_codigo_tikz_anidado,canvas_no_animar,schedule_animate,*args):
            try:
                codigo_a_dibujar = nuevo_codigo_tikz_anidado[self.index_animacion]
                # print("ANIMAR")
                # print(codigo_a_dibujar)
                animacion_valido = True
            except:
                # print("DETENER ANIMACIÓN")
                Clock.unschedule(schedule_animate)
                animacion_valido = False
            if(animacion_valido):
                if(len(canvas_no_animar) == len(self.area_de_dibujar.canvas.children)):
                    for canvas in canvas_no_animar:#Añadir Figuras no animadas...
                        self.area_de_dibujar.canvas.add(canvas)
                else:
                    #Elimina todos los canvas del widget "area de dibujar"
                    canvas_no_animar_arr = []
                    for canva in canvas_no_animar:
                        canvas_no_animar_arr.append(canva)
                    self.area_de_dibujar.canvas.children = canvas_no_animar_arr
                    #Añade los canvas no animados...
                    for canvas in canvas_no_animar:#Añadir Figuras no animadas...
                        self.area_de_dibujar.canvas.add(canvas)
                #Dibujar la figura elegida de la lista
                if(isinstance(codigo_a_dibujar,tuple)):
                    for codigo in codigo_a_dibujar:
                        self.__validar_dibujar(codigo[0],codigo[1],codigo[2],
                        codigo[3],codigo[4],self.area_de_dibujar)
                else:
                    self.__validar_dibujar(codigo_a_dibujar[0],codigo_a_dibujar[1],codigo_a_dibujar[2],
                    codigo_a_dibujar[3],codigo_a_dibujar[4],self.area_de_dibujar)
                #Continuar con la siguiente figura en la lista
                self.index_animacion+=1
            else:
                self.index_animacion = 0
        def validarSecuenciaNumerica(cantidad_parametros,array_secuencia_numerica):
            # print("Parametros_sin_definir_ordenado")
            # print(parametros_sin_definir_ordenado)
            #Los parametros deben ser secuenciales #1,#2,#3. ETC
            parametros_sin_definir_ordenado = []
            indice = 0
            for e in array_secuencia_numerica:
                _ = bisect(parametros_sin_definir_ordenado, e)
                insort(parametros_sin_definir_ordenado, e)
                indice+=1
            indice = 0
            for _ in parametros_sin_definir_ordenado:
                if indice>0:
                    if parametros_sin_definir_ordenado[indice-1]+1 != parametros_sin_definir_ordenado[indice]:
                        parametros_sin_definir_ordenado = []
                        break
                indice+=1
            if not len(parametros_sin_definir_ordenado):
                return[{"error":"Error cerca de '#' se esperaba una secuencia numerica de parametros, ej: #1,#2,#3"}]
            else:
                try:
                    int(cantidad_parametros)
                except:
                    return[{"error":"Error cerca de la cantidad de parametros '#' se esperaba un numero INTEGER."}]
                if not len(self.mensajes_de_error):
                    cantidad_parametros = int(cantidad_parametros)
                    if len(array_secuencia_numerica) != cantidad_parametros:
                        return[{"error":str(cantidad_parametros)+" es diferente a la cantidad de parametros definidos (#) "+str(len(array_secuencia_numerica))}]
                    else:
                        return True
        if comando_tikz == "tikzset":
            #\tikzset{estilo global/.style = {line width=1.25pt, draw = cyan!75!gray,dashed}}
            nombre_variable_entorno = [nombre for nombre in list(funcion_de_comando[1].keys())[0].split(" ") if nombre]
            key_original = list(funcion_de_comando[1].keys())[0]
            nombre_variable = nombre_variable_entorno[0]
            entorno = nombre_variable_entorno[1]
            if entorno == "global/.style":
                entorno = entorno.split("/")[0]
                #NO TIENE PARAMETROS
                if isinstance(funcion_de_comando[1][key_original], list):
                    self.estilo_global_local[nombre_variable+" "+entorno] = funcion_de_comando[1][key_original]
                #TIENE PARAMETROS -> EVALUAR VALIDES PARAMETROS
                else:
                    cantidad_parametros = list(funcion_de_comando[1][key_original].keys())[0]
                    parametros_estilo_global_local = funcion_de_comando[1][key_original][cantidad_parametros]
                    parametros_sin_definir = []
                    indice_estilo_global_local = 0
                    indice_estilo_global_local_parametro = 0
                    for parametro_estilo_global_local in parametros_estilo_global_local:
                        indice_estilo_global_local_parametro = 1 if indice_estilo_global_local > 1 else 0
                        indice_estilo_global_local = indice_estilo_global_local if indice_estilo_global_local <2 else 0
                        parametro_estilo_global_local = parametros_estilo_global_local[indice_estilo_global_local_parametro][indice_estilo_global_local]
                        #Explorar por []
                        if indice_estilo_global_local == 0:
                            for key in parametro_estilo_global_local:
                                key = key.strip()
                                #Aqui se espera Parametros #2
                                if key.find("#") != -1:
                                    try:
                                        int(key[key.find("#")+1::])
                                        parametros_sin_definir.append(int(key[key.find("#")+1::]))
                                    except:
                                        self.mensajes_de_error.append("Error cerca de "+key+" se esperaba un parametro valido. '#'")
                                        break
                                else:
                                    self.mensajes_de_error.append("Error cerca de "+key+" se esperaba un parametro valido. '#'")
                        #Explorar por {}
                        elif indice_estilo_global_local == 1:
                            #Recorrer keys de {}
                            keys_diccionario = list(parametro_estilo_global_local.values())
                            for key in keys_diccionario:
                                if key.find("#")!=-1:
                                    try:
                                        int(key[key.find("#")+1::])
                                        parametros_sin_definir.append(int(key[key.find("#")+1::]))
                                    except:
                                        self.mensajes_de_error.append("Error cerca de "+key+" se esperaba un parametro valido. '#'")
                                        break
                        indice_estilo_global_local+=1
                    if not len(self.mensajes_de_error): 
                        result_validacion_secuencia = validarSecuenciaNumerica(cantidad_parametros,parametros_sin_definir)
                        if type(result_validacion_secuencia) is dict:
                            self.mensajes_de_error.append(result_validacion_secuencia["error"])
                        else:
                            #Si todas las validaciones son correctas...
                            self.estilo_global_local[nombre_variable+" "+entorno] = funcion_de_comando[1][key_original]
        elif comando_tikz == "definecolor":
            nombre_variable_entorno = [nombre for nombre in list(funcion_de_comando[1].keys())[0].split(" ") if nombre]
            nombre_variable = nombre_variable_entorno[0]
            key_original = list(funcion_de_comando[1].keys())[0]
            self.estilo_global_local[nombre_variable] = funcion_de_comando[1][key_original]
        elif comando_tikz == "animarPytikz":
            print("__________________________________________________________")
            print("CODIGO ANIDADO A EJECUTAR")
            print(funcion_de_comando[1]["ejecutar"])
            print("__________________________________________________________")
            codigo_tikz_anidado = funcion_de_comando[1]["ejecutar"]
            conjunto_de_comandos = []

            #Si es para generar GIF, entonces se va a generar imagenes a partir de cada código dentro del comando animarPytikz que se utilizara para generar GIF, y luego se animara el mismo resultado pero en el aplicativo.
            if("save" in parametros_comando[0]):
                habilitado_animador = {"generar_gif":True}
            #Caso contrario, entonces se animara en la misma aplicación
            else:
                habilitado_animador = {"generar_gif":False}
            for comando_tikz_anidado in codigo_tikz_anidado:
                if(len(self.mensajes_de_error)>0):
                    break
                #Comandos preexistentes...
                if type(comando_tikz_anidado) is list:
                    if comando_tikz_anidado[0] in self.comandos_dibujar:
                        #Validar comandos si es para animar
                        self.__validar_dibujar(comando_tikz_anidado[0],comando_tikz_anidado[1],comando_tikz_anidado[2],comando_tikz_anidado[3],comando_tikz_anidado[4],self.area_de_dibujar,habilitado_animador=habilitado_animador)
                    elif comando_tikz_anidado[0] in self.comandos_variables_tikz:
                        #Validar comandos o retornar lista de comandos a animar 
                        frames_foraech = self.__validar_variables_tikz(comando_tikz_anidado[0],comando_tikz_anidado[1],comando_tikz_anidado[2],habilitado_animador=habilitado_animador)
                        if len(frames_foraech):
                            conjunto_de_comandos.append(frames_foraech)
                #Comandos del usuario...
                elif type(comando_tikz_anidado) is dict:
                    for comando_personalizado in comando_tikz_anidado.values():
                        for comando in comando_personalizado:
                            if comando[0] in self.comandos_dibujar:
                                #Validar comandos si es para animar
                                self.__validar_dibujar(comando[0],comando[1],comando[2],comando[3],comando[4],self.area_de_dibujar,habilitado_animador=habilitado_animador)
                            elif comando[0] in self.comandos_variables_tikz:
                                #Validar comandos o retornar lista de comandos a animar 
                                frames_foraech = self.__validar_variables_tikz(comando[0],comando[1],comando[2],habilitado_animador=habilitado_animador)
                                if len(frames_foraech):
                                    conjunto_de_comandos.append(frames_foraech)
                        #Cada conjunto de comando estara dentro de una TUPLA, cada indice de conjunto_de_comandos, pertenece a los comandos anidados en un comando.
                        conjunto_de_comandos.append([tuple(comando_personalizado)])

            #Generar GIF
            if(habilitado_animador["generar_gif"]):
                self.Animar.generar_animacion()

            #Generar animación en aplicativo...
            index_lista_de_comandos = 0
            for index,comando_tikz_anidado in enumerate(codigo_tikz_anidado):
                if type(comando_tikz_anidado) is list:
                    if comando_tikz_anidado[0] == "foreach":
                        del codigo_tikz_anidado[index]
                        for frames in conjunto_de_comandos[index_lista_de_comandos]:
                            codigo_tikz_anidado.insert(0,frames)
                        index_lista_de_comandos+=1
                elif type(comando_tikz_anidado) is dict:
                    #Eliminar el diccionario del comandos de usuario personalizado
                    del codigo_tikz_anidado[index]
                    #Añadir todos los comandos en conjunto del comando personalizado al array codigo_tikz_anidado
                    for frames_comando_personalizado in conjunto_de_comandos[index_lista_de_comandos]:
                        codigo_tikz_anidado.insert(0,frames_comando_personalizado)
                    index_lista_de_comandos+=1
            class MyWidget(Widget):
                my_list = ListProperty([])

            canvas_no_animar = MyWidget()
            canvas_no_animar.my_list = self.area_de_dibujar.canvas.children
            schedule_animate = partial(animar,codigo_tikz_anidado,canvas_no_animar.my_list)
            schedule_animate(schedule_animate)
            Clock.schedule_interval(schedule_animate,1)
        elif comando_tikz == "foreach":
            #Generar valores según Foreach
            
            #Variables Foreach
            each = parametros_comando[0]
            codigo_tikz_anidado = funcion_de_comando[1]["ejecutar"]
            variables = parametros_comando[1]["variables"]
            metrica_validos = self.metrica_validos

            #Variables del generador_valores mediante Foreach
            index = 0
            index_tipo = 0
            index_interior = 0

            nuevo_codigo_tikz_anidado = []
            index_nuevo_codigo_tikz = 0
            generado_nuevo_codigo_tikz_anidado = False

            def reemplazar_valores(codigo_tikz_anidado,var,valor_original,valor_a_reemplazar,index,index_tipo=None,index_interior=None):
                if re.search(r"\\"+var,valor_original):#Si hay variables...
                    #Cambiar valor correspondiente por el asignado en el Foreach
                    variables_anidado = valor_original[
                        re.search(r"\\"+var,valor_original).start():
                        re.search(r"\\"+var,valor_original).end()
                    ]
                    if(index_tipo!=None):
                        if(index_interior!=None):
                            valor_original_str = codigo_tikz_anidado[index][index_tipo][index_interior]
                        else:
                            valor_original_str = codigo_tikz_anidado[index][index_tipo]
                    #Comprobar si se trata de una ecuación
                    resultado = valor_original_str.replace(variables_anidado,valor_a_reemplazar)
                    variables_anidado_con_metrica = ""
                    for metrica in metrica_validos:
                        if re.search(metrica,resultado):
                            variables_anidado_con_metrica = resultado[
                                re.search(r"\d+",resultado).start():
                                re.search(metrica,resultado).end()
                            ]
                    if variables_anidado_con_metrica: resultado = variables_anidado_con_metrica
                    try:
                        nuevo = str(eval(resultado))
                    except:
                        nuevo = valor_original_str.replace(variables_anidado,valor_a_reemplazar)
                    return nuevo
                else:
                    return valor_original
            def generar_valores(codigo_tikz_anidado,var,valor,index_nuevo_codigo_tikz,index,index_tipo=None,index_interior=None):
                for codigo in codigo_tikz_anidado:
                    if(isinstance(codigo,list)): #[[], {}], [('\\i', '0'), '1cm'], ['circle'], [[], {}]]
                        for object in codigo:#
                            if(isinstance(object,list) or isinstance(object,tuple)):#Recorrer [] o ()
                                for string in object:
                                    #Comprobar si se trata de una ecuación
                                    nuevo_codigo_tikz_anidado[index_nuevo_codigo_tikz][index][index_tipo][index_interior] = reemplazar_valores(codigo_tikz_anidado,var,string,valor,index,index_tipo,index_interior)
                                    index_interior += 1
                                index_interior = 0
                            elif(isinstance(object,str)):
                                nuevo_codigo_tikz_anidado[index_nuevo_codigo_tikz][index][index_tipo] = reemplazar_valores(codigo_tikz_anidado,var,object,valor,index,index_tipo)
                            index_tipo+=1
                        index_tipo = 0
                    index+=1

            #Extraer valor each (Si son 2 variables)
            valor_primario = []
            valor_secundario = []
            for valor in each[0]:
                if len(valor.split("/"))>0:
                    index_valor_primari = 0
                    for valor_split in valor.split("/"):
                        if(index_valor_primari==0 or not index_valor_primari%2):
                            valor_primario.append(valor_split)
                        else:
                            valor_secundario.append(valor_split)
                        index_valor_primari+=1
                else:
                    # self.message_error.append("ERROR: DEBE DE TENER VALORES EACH PARA DOS VARIABLES")
                    valor_primario.append(valor)
            if(len(valor_secundario)>0):
                variables[0] = {"variable":variables[0],"each":valor_primario}
                variables[1] = {"variable":variables[1],"each":valor_secundario}
            #Generar valores Foreach
            for var in variables:
                if(isinstance(var,dict)):
                    valor_each = var["each"]
                    var = var["variable"]
                    for codigo_arr in codigo_tikz_anidado:
                        for valor in valor_each:
                            if not generado_nuevo_codigo_tikz_anidado:
                                    nuevo_codigo_tikz_anidado.append(deepcopy(codigo_arr))
                                    generar_valores(codigo_arr,var,valor,index_nuevo_codigo_tikz,index,index_tipo,index_interior)
                            else:
                                generar_valores(nuevo_codigo_tikz_anidado[index_nuevo_codigo_tikz],var,valor,index_nuevo_codigo_tikz,index,index_tipo,index_interior)
                            index_nuevo_codigo_tikz+=1
                            index=0
                else:
                    for codigo_arr in codigo_tikz_anidado:
                        for valor in each[0]:
                            if not generado_nuevo_codigo_tikz_anidado:
                                nuevo_codigo_tikz_anidado.append(deepcopy(codigo_arr))
                                generar_valores(codigo_arr,var,valor,index_nuevo_codigo_tikz,index,index_tipo,index_interior)
                            else:
                                generar_valores(nuevo_codigo_tikz_anidado[index_nuevo_codigo_tikz],var,valor,index_nuevo_codigo_tikz,index,index_tipo,index_interior)
                            index_nuevo_codigo_tikz+=1
                            index=0
                index_nuevo_codigo_tikz=0
                generado_nuevo_codigo_tikz_anidado=True

            print("_____________________________________________-")
            print("CONTENIDO FOREACH A EJECUTAR")
            print(nuevo_codigo_tikz_anidado)#Y estos son los que se pasarán a dibujar...
            print("_____________________________________________-")

            #Retornar lista de comandos si es para animar, no para generar GIF
            if(not habilitado_animador["generar_gif"]):
                #Dividir valores del foreach según Each, para facilitar la animación
                codigo_tikz_por_frame = []
                total_frames = len(each[0])
                for _ in range(total_frames):
                    codigo_tikz_por_frame.append([])
                index = 0
                for codigo in nuevo_codigo_tikz_anidado:
                    codigo_tikz_por_frame[index].append(codigo)
                    if(index == total_frames-1):
                        index = 0
                    else:
                        index+=1
                nuevo_codigo_tikz_por_frame = []
                for frame in codigo_tikz_por_frame:
                    nuevo_codigo_tikz_por_frame.append(tuple(frame))
                return nuevo_codigo_tikz_por_frame
            #Generar imagenes mediante comandos generados por foreach, para luego convertirlos a GIF
            elif(habilitado_animador["generar_gif"]):
                for comando_tikz_anidado in nuevo_codigo_tikz_anidado:
                    self.__validar_dibujar(comando_tikz_anidado[0],comando_tikz_anidado[1],comando_tikz_anidado[2],comando_tikz_anidado[3],comando_tikz_anidado[4],self.area_de_dibujar,habilitado_animador=habilitado_animador)
            #Dibujar según comandos de Foreach
            else:
                for comando_tikz_anidado in nuevo_codigo_tikz_anidado:
                    self.__validar_dibujar(comando_tikz_anidado[0],comando_tikz_anidado[1],comando_tikz_anidado[2],comando_tikz_anidado[3],comando_tikz_anidado[4],self.area_de_dibujar)