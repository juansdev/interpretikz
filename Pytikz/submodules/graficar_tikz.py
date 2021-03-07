from kivy.graphics import Color, Line, Rectangle, Ellipse
from kivy.metrics import pt, cm
from bisect import bisect, insort
import re
from .tools_graficar_tikz.degradado import Degradado

class Graficar_tikz():
    def __init__(self,area_de_dibujar):
        self.area_de_dibujar = area_de_dibujar
        self.mensajes_de_error = []

    def Graficar(self,comandos_tikz_validos):
        self.estilo_global_local = {}
        for comando_tikz in comandos_tikz_validos:
            if(len(self.mensajes_de_error)>0):
                for error in self.mensajes_de_error:
                    print(error)
                    return []
            # self.comandos_tikz.append([self.comando_tikz,self.parametros_comando,self.posiciones,self.figura,self.funcion_de_figura])
            comandos_dibujar = ["draw","filldraw","fill","shade"]
            comandos_variables_tikz = ["tikzstyle","definecolor","tikzset"]
            if comando_tikz[0] in comandos_dibujar:
                self.Dibujar(comando_tikz[0],comando_tikz[1],comando_tikz[2],comando_tikz[3],comando_tikz[4],self.area_de_dibujar)
            elif comando_tikz[0] in comandos_variables_tikz:
                self.Variables_tikz(comando_tikz[0],comando_tikz[1])
            else:
                #shade
                print("Todavia el comando no esta habilitado.")

        if(len(self.mensajes_de_error)>0):
            for error in self.mensajes_de_error:
                print(error)
                return []

    def Dibujar(self,comando_tikz,parametros_comando,draw_posicion,figuras,funcion_de_figura,area_de_dibujar):

        if comando_tikz == "draw" or comando_tikz == "filldraw" or comando_tikz == "fill":
            
            self.tipo_de_linea_validos = ["loosely dashed", "dashed", "densely dashed", "loosely dotted", "dotted", "densely dotted"]
            self.colores_validos = ["red","blue","green","cyan","black","yellow"]
            
            #Estilos simples
            self.tipo_de_linea = ""
            self.line_width = 1.0
            self.fill = (1,1,1) if comando_tikz == "draw" else (0,0,0) if comando_tikz == "fill" else (0,0,0)
            self.draw = (0,0,0) if comando_tikz == "draw" else (1,1,1) if comando_tikz == "fill" else (0,0,0)
            #Estilos gradiantes
            #left color, right color, top color, middle color, bottom color, inner color, outer color, ball color
            self.degradients = {}

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
                                    self.Validar_estilos("tupla",parametro_estilo_global_local)
                                #Explorar por {}
                                elif indice_estilo_global_local == 1:
                                    #Recorrer keys de {}
                                    keys_diccionario = list(parametro_estilo_global_local.keys())
                                    print("keys_diccionario")
                                    print(keys_diccionario)
                                    self.Validar_estilos("diccionario",keys_diccionario,parametro_estilo_global_local)
                                indice_estilo_global_local+=1
                        elif not tupla_validada:
                            self.Validar_estilos("tupla",parametro)
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
                            #["red","solid"]
                            variable_valores_indefinidos = self.estilo_global_local[key]
                            # cantidad_parametros = int(list(variable_valores_indefinidos.keys())[0])
                            # if cantidad_parametros != len(variable_valores_definido):
                            #     self.mensajes_de_error.append("Error cerca de "+comando_tikz+" se esperaba una cantidad de parametros igual que el de la variable llamada.")
                            # else:
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
                                                self.Validar_estilos("tupla",estilo)
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
                                                        self.Validar_estilos("diccionario",key,estilo)
                                                    indice_key+=1
                                            indice_key_seleccionado+=1
                                else:
                                    break
                                indice_estilo_global_local+=1
                        elif not diccionario_validada:
                            self.Validar_estilos("diccionario",keys_diccionario,parametro)
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
                            punto_inicial_x_y = self.Validar_metrica(draw_posicion[0][0])
                            punto_final_x_y = self.Validar_metrica(draw_posicion[0][1])
                            ancho = self.Validar_metrica(draw_posicion[1][0])
                            alto = self.Validar_metrica(draw_posicion[1][1])
                            rectangulo_dibujado_lineas = [punto_inicial_x_y, punto_final_x_y, punto_inicial_x_y, punto_final_x_y+alto, punto_inicial_x_y+ancho, punto_final_x_y+alto, punto_inicial_x_y+ancho, punto_final_x_y, punto_inicial_x_y, punto_final_x_y]
                            #Dibujar en el area de dibujado...
                            #Si hay separacion de lineas...
                            if self.tipo_de_linea:
                                with area_de_dibujar.canvas:
                                    #BORDE RECTANGULO CON LINEAS DISCONTINUADAS
                                    area_de_dibujar.color = Color(self.draw[0], self.draw[1], self.draw[2])
                                    Line(points=rectangulo_dibujado_lineas, dash_offset=10, dash_length=5)
                                    #RELLENO RECTANGULO
                                    area_de_dibujar.color = Color(self.fill[0], self.fill[1], self.fill[2])
                                    Rectangle(pos=(punto_inicial_x_y,punto_final_x_y),size=(ancho,alto))
                                if self.degradients:
                                    Degradado("triangle_strip",area_de_dibujar,rectangulo_dibujado_lineas,degradients=self.degradients)
                            #Si no hay...
                            else:
                                with area_de_dibujar.canvas:
                                    #BORDE RECTANGULO
                                    area_de_dibujar.color = Color(self.draw[0], self.draw[1], self.draw[2])
                                    Line(points=rectangulo_dibujado_lineas,width=self.line_width)
                                    #RELLENO RECTANGULO
                                    area_de_dibujar.color = Color(self.fill[0], self.fill[1], self.fill[2])
                                    # area_de_dibujar.color = Color(0, 0, 0)
                                    Rectangle(pos=(punto_inicial_x_y,punto_final_x_y),size=(ancho,alto))
                                if self.degradients:
                                    Degradado("triangle_strip",area_de_dibujar,rectangulo_dibujado_lineas,degradients=self.degradients)
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

                            posicion_x = self.Validar_metrica(draw_posicion[0][0])
                            posicion_y = self.Validar_metrica(draw_posicion[0][1])

                            angulo_inicial = float(450) if float(draw_posicion[indice][0]) == 0.0 else float(450-(float(draw_posicion[indice][0])))
                            angulo_final = float(450) if float(draw_posicion[indice][1]) == 0.0 else float(450-(float(draw_posicion[indice][1])))
                            radio = self.Validar_metrica(draw_posicion[indice][2])
                            #Eliminar parametro Arc utilizado
                            # print("draw_posicion original")
                            # print(draw_posicion)
                            posicion_x+=radio
                            posicion_y+=radio
                            self.posicion_x_arc = posicion_x
                            self.posicion_y_arc = posicion_y
                            self.angulo_final_arc = draw_posicion[indice][1]
                            self.longitud_arc = radio
                            del draw_posicion[indice:indice+1]
                            # print("draw_posicion despues de eliminar el Arc utilizado")
                            # print(draw_posicion)
                            #Line:
                            # circle: (60,60,60,90,180)#CIRCULO CERRADO, 40 DE RADIO
                            if self.tipo_de_linea:
                                with area_de_dibujar.canvas:
                                    #ARCO CON LINEAS DISCONTINUADAS
                                    area_de_dibujar.color = Color(self.draw[0], self.draw[1], self.draw[2])
                                    Line(circle=[posicion_x,posicion_y,radio,angulo_inicial,angulo_final], dash_offset=10, dash_length=5)
                            #Si no hay...
                            else:
                                with area_de_dibujar.canvas:
                                    #ARCO SIN LINEAS DISCONTINUADAS
                                    area_de_dibujar.color = Color(self.draw[0], self.draw[1], self.draw[2])
                                    Line(circle=[posicion_x,posicion_y,radio,angulo_inicial,angulo_final],width=self.line_width)
                        #DIBUJAR CIRCULO
                        #\draw[draw=red,fill=yellow] (0,0) circle (1cm);
                        elif(figura=="circle"):
                            posicion_x = self.Validar_metrica(draw_posicion[0][0])
                            posicion_y = self.Validar_metrica(draw_posicion[0][1])
                            radio_es_valido = True
                            try:
                                radio = self.Validar_metrica(draw_posicion[1])
                            except:
                                self.mensajes_de_error.append("Error cerca de "+figura+" se esperaba un valor de Radio o de posicion X y Y validos.")
                                radio_es_valido = False
                            #Line:
                            # circle: (60,60,60,90,180)#CIRCULO CERRADO, 40 DE RADIO
                            if radio_es_valido:
                                if self.tipo_de_linea:
                                    with area_de_dibujar.canvas:
                                        #RELLENO CIRCULO
                                        area_de_dibujar.color = Color(self.fill[0], self.fill[1], self.fill[2])
                                        ancho = radio*2
                                        alto = radio*2
                                        Ellipse(pos=(posicion_x,posicion_y),size=(ancho,alto))
                                        #BORDE CIRCULO CON LINEAS DISCONTINUADAS
                                        posicion_x+=radio
                                        posicion_y+=radio
                                        area_de_dibujar.color = Color(self.draw[0], self.draw[1], self.draw[2])
                                        Line(circle=[posicion_x,posicion_y,radio], dash_offset=10, dash_length=self.line_width)
                                #Si no hay...
                                else:
                                    with area_de_dibujar.canvas:
                                        #RELLENO CIRCULO
                                        area_de_dibujar.color = Color(self.fill[0], self.fill[1], self.fill[2])
                                        ancho = radio*2
                                        alto = radio*2
                                        Ellipse(pos=(posicion_x,posicion_y),size=(ancho,alto))
                                        # #BORDE CIRCULO
                                        posicion_x+=radio
                                        posicion_y+=radio
                                        area_de_dibujar.color = Color(self.draw[0], self.draw[1], self.draw[2])
                                        Line(circle=[posicion_x,posicion_y,radio])
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
                                        coordenadas.append(self.Validar_metrica(posicion[0]))
                                        coordenadas.append(self.Validar_metrica(posicion[1]))
                                    elif indice_controls_final >= 4:
                                        break
                                    if indice>0:
                                        #Maximo-Minimo 3 posiciones
                                        indice_controls_final+=1
                                else:
                                    #Posiciones Control
                                    coordenadas.append(self.Validar_metrica(posicion[0]))
                                    coordenadas.append(self.Validar_metrica(posicion[1]))
                                indice += 1
                            #Eliminar parametro Controls utilizado
                            if len(figuras_control)>1:
                                print("draw_posicion original")
                                print(draw_posicion)
                                draw_posicion[0] = (str(coordenadas[len(coordenadas)-2]),str(coordenadas[len(coordenadas)-1]))
                                del draw_posicion[indice_controls_inicial:indice_controls_final]
                                print("draw_posicion despues de eliminar el Control utilizado")
                                print(draw_posicion)
                            if len(coordenadas)>=4:
                                print("coordenadas")
                                print(coordenadas)
                                #Dibujar en el area de dibujado...
                                #Si hay separacion de lineas...
                                if self.tipo_de_linea:
                                    with area_de_dibujar.canvas:
                                        area_de_dibujar.color = Color(self.draw[0], self.draw[1], self.draw[2])
                                        Line(bezier=coordenadas, dash_offset=10, dash_length=5)
                                #Si no hay...
                                else:
                                    with area_de_dibujar.canvas:
                                        area_de_dibujar.color = Color(self.draw[0], self.draw[1], self.draw[2])
                                        Line(bezier=coordenadas, width=self.line_width)
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
                                longitud = self.Validar_metrica(posicion_angulo_array[1])
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
                                if type(posicion) is tuple and len(posicion) == 2:
                                    draw_posicion_normal.append(posicion)
                                elif type(posicion) is str:
                                    posicion_array = posicion.split(":")
                                    if len(posicion_array)==2:
                                        draw_posicion_normal.append(posicion)
                                    elif posicion == "cycle":
                                        draw_posicion_normal.append(posicion)
                            indice = 0
                            print("draw_posicion_normal")
                            print(draw_posicion_normal)
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
                                            coordenadas.append(self.Validar_metrica(posicion[0]))
                                            coordenadas.append(self.Validar_metrica(posicion[1]))
                                elif len(coordenadas) >= 4 and posicion != "cycle":
                                    #HASTA NUEVA COORDENADA X,Y
                                    coordenadas.append(self.Validar_metrica(posicion[0]))
                                    coordenadas.append(self.Validar_metrica(posicion[1]))
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
                                    else:
                                        #HASTA COORDENADA ORIGEN X,Y
                                        coordenadas.append(self.Validar_metrica(str(coordenadas[0])))
                                        coordenadas.append(self.Validar_metrica(str(coordenadas[1])))
                                indice+=1
                            if not len(self.mensajes_de_error):
                                print("coordenadas")
                                print(coordenadas)
                                if len(coordenadas)>=4:
                                  #Dibujar en el area de dibujado...
                                    #Si hay separacion de lineas...
                                    if self.tipo_de_linea:
                                        if len(coordenadas_cycle_arc):
                                            with area_de_dibujar.canvas:
                                                area_de_dibujar.color = Color(self.draw[0], self.draw[1], self.draw[2])
                                                Line(points=coordenadas_cycle_arc, dash_offset=10, dash_length=5)    
                                        with area_de_dibujar.canvas:
                                            area_de_dibujar.color = Color(self.draw[0], self.draw[1], self.draw[2])
                                            Line(points=coordenadas, dash_offset=10, dash_length=5)
                                        if self.fill != (1,1,1) or self.degradients:
                                            Degradado("triangle_fan",area_de_dibujar,coordenadas,(self.fill[0],self.fill[1],self.fill[2]),self.degradients)
                                    #Si no hay...
                                    else:
                                        if len(coordenadas_cycle_arc):
                                            with area_de_dibujar.canvas:
                                                area_de_dibujar.color = Color(self.draw[0], self.draw[1], self.draw[2])
                                                Line(points=coordenadas_cycle_arc, width=self.line_width)
                                        with area_de_dibujar.canvas:
                                            area_de_dibujar.color = Color(self.draw[0], self.draw[1],self.draw[2])
                                            Line(points=coordenadas, width=self.line_width)
                                        if self.fill != (1,1,1) or self.degradients:
                                            Degradado("triangle_fan",area_de_dibujar,coordenadas,(self.fill[0],self.fill[1],self.fill[2]),self.degradients)
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
                            posicion_x = self.Validar_metrica(draw_posicion[0][0])
                            posicion_y = self.Validar_metrica(draw_posicion[0][1])
                            
                            diccionario_funcion_figura = {}
                            for key in list(funcion_de_figura[1].keys()):
                                key_nueva = key.strip()
                                diccionario_funcion_figura[key_nueva] = funcion_de_figura[1][key]
                            # print(diccionario_funcion_figura)
                            start_angle = diccionario_funcion_figura["start angle"] if "start angle" in list(diccionario_funcion_figura.keys()) else "0.0"
                            end_angle = diccionario_funcion_figura["end angle"] if "end angle" in list(diccionario_funcion_figura.keys()) else "360.0"
                            radius = diccionario_funcion_figura["radius"] if "radius" in list(diccionario_funcion_figura.keys()) else "10.0"
                            # print("start_angle")
                            # print(start_angle)
                            # print("end_angle")
                            # print(end_angle)
                            # print("radius")
                            # print(radius)
                            angulo_inicial = 450.0 if self.Validar_metrica(start_angle) == 0.0 else 450-(self.Validar_metrica(start_angle))
                            angulo_final = 450.0 if self.Validar_metrica(end_angle) == 0.0 else 450-(self.Validar_metrica(end_angle))

                            radio_es_valido = True

                            try:
                                radio = self.Validar_metrica(radius)
                            except:
                                self.mensajes_de_error.append("Error cerca de "+figura+" se esperaba un valor de Radio o de posicion X y Y validos.")
                                radio_es_valido = False

                            if radio_es_valido:
                                if self.tipo_de_linea:
                                    with area_de_dibujar.canvas:
                                        #ARCO CON LINEAS DISCONTINUADAS
                                        posicion_x+=radio
                                        posicion_y+=radio
                                        area_de_dibujar.color = Color(self.draw[0], self.draw[1], self.draw[2])
                                        #(center_x, center_y, radius, angle_start, angle_end, segments):
                                        Line(circle=[posicion_x,posicion_y,radio,angulo_inicial,angulo_final], dash_offset=10, dash_length=5)
                                #Si no hay...
                                else:
                                    with area_de_dibujar.canvas:
                                        #ARCO SIN LINEAS DISCONTINUADAS
                                        posicion_x+=radio
                                        posicion_y+=radio
                                        area_de_dibujar.color = Color(self.draw[0], self.draw[1], self.draw[2])
                                        Line(circle=[posicion_x,posicion_y,radio,angulo_inicial,angulo_final],width=self.line_width)
                        #No tiene figura
                        else:
                            self.mensajes_de_error.append("Error el comando TikZ '"+comando_tikz+"' no tiene una figura valida.")
        elif comando_tikz=="shade":
            #shade
            print("Todavia el comando no esta habilitado.")

    def Variables_tikz(self,comando_tikz=None,funcion_de_comando=None): 
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
                        #Los parametros deben ser secuenciales #1,#2,#3. ETC
                        parametros_sin_definir_ordenado = []
                        indice = 0
                        for e in parametros_sin_definir:
                            numero = bisect(parametros_sin_definir_ordenado, e)
                            insort(parametros_sin_definir_ordenado, e)
                            indice+=1
                        indice = 0
                        for x in parametros_sin_definir_ordenado:
                            if indice>0:
                                if parametros_sin_definir_ordenado[indice-1]+1 != parametros_sin_definir_ordenado[indice]:
                                    parametros_sin_definir_ordenado = []
                                    break
                            indice+=1
                        # print("Parametros_sin_definir_ordenado")
                        # print(parametros_sin_definir_ordenado)
                        parametros_sin_definir = parametros_sin_definir_ordenado
                        if not len(parametros_sin_definir):
                            self.mensajes_de_error.append("Error cerca de '#' se esperaba una secuencia numerica de parametros, ej: #1,#2,#3")
                        else:
                            try:
                                int(cantidad_parametros)
                            except:
                                self.mensajes_de_error.append("Error cerca de '#' se esperaba un numero INTEGER.")
                            if not len(self.mensajes_de_error):
                                cantidad_parametros = int(cantidad_parametros)
                                if len(parametros_sin_definir) != cantidad_parametros:
                                    self.mensajes_de_error.append(str(cantidad_parametros)+" es diferente a la cantidad de parametros definidos (#) "+str(len(parametros_sin_definir)))
                                else:
                                    #Si todas las validaciones son correctas...
                                    self.estilo_global_local[nombre_variable+" "+entorno] = funcion_de_comando[1][key_original]

    def Validar_metrica(self,metrica_a_validar):
        metrica_validos = ["pt","cm"]
        unidad_metrica = re.compile("[a-z]")
        metrica = []
        distanciamiento_metrica = []
        for unidad in unidad_metrica.finditer(metrica_a_validar):
            # print(unidad.start(), unidad.group())
            distanciamiento_metrica.append(unidad.start())
            metrica.append(unidad.group())
        #VALIDAR METRICA.
        if len(distanciamiento_metrica)>1:
            distanciamiento_original = ""
            for distanciamiento in distanciamiento_metrica:
                if not distanciamiento_original:
                    distanciamiento_original = distanciamiento
                else:
                    if not distanciamiento_original+1==distanciamiento:
                        self.mensajes_de_error.append("Error cerca de "+metrica_a_validar)
            if not len(self.mensajes_de_error):
                try:
                    float(metrica_a_validar[:distanciamiento_metrica[0]])
                except:
                    self.mensajes_de_error.append("Error cerca de "+str(metrica_a_validar[:distanciamiento_metrica[0]])+" se esperaba un valor FLOAT O INTEGER")
                if not self.mensajes_de_error:
                    #Validar unidad de metrica
                    unidad_metrica = "".join(metrica) 
                    if unidad_metrica in metrica_validos:
                        valor_metrica = float(metrica_a_validar[:distanciamiento_metrica[0]])
                        if unidad_metrica == "pt":
                            return pt(valor_metrica)
                        elif unidad_metrica == "cm":
                            return cm(valor_metrica)
                    else:
                        return 10.0
        else:
            try:
                float(metrica_a_validar)
            except:
                self.mensajes_de_error.append("Error cerca de "+metrica_a_validar)
            if not len(self.mensajes_de_error):
                return float(metrica_a_validar)
        return 10.0

    def Color(self,color):
        #["red","blue","green","cyan","black","yellow"]
        #RGB
        if color == "red":
            return (1,0,0)
        elif color == "blue":
            return (0,0,1)
        elif color == "green":
            return (0,1,0)
        elif color == "cyan":
            return (0,1,1)
        elif color == "black":
            return (0,0,0)
        elif color == "yellow":
            return (1,1,0)
        elif color == "white":
            return (1,1,1)
    
    def Validar_estilos(self,tipo_dato,valor,valor_diccionario=None):
        def draw_tupla(valor,tupla=False):
            if tupla:
                valor = valor.strip()
            color_porcentaje = valor.split("!")
            if valor in self.colores_validos:
                self.draw = self.Color(valor)
            elif valor in self.tipo_de_linea_validos:
                self.tipo_de_linea = valor
            elif len(color_porcentaje)==3:#green!70!blue
                self.Color_porcentaje(color_porcentaje)
        def draw_diccionario(valor,valor_diccionario,diccionario=False):
            if diccionario:
                key_original = valor
                valor_diccionario = valor_diccionario[key_original]
            key = valor.strip()
            if key.find("line width")!=-1:
                #Validar si es correcta la unidad de medida utilizada...
                self.line_width = self.Validar_metrica(valor_diccionario)
            elif key.find("fill")!=-1:
                #Validar si es correcto el color utilizado...
                relleno = valor_diccionario.strip()
                color_porcentaje = relleno.split("!")
                if relleno in self.colores_validos:
                    self.fill = self.Color(relleno)
                elif len(color_porcentaje)==3:#green!70!blue
                    self.fill = self.Color_porcentaje(color_porcentaje)
            elif key.find("draw")!=-1:
                #Validar si es correcto el color utilizado...
                borde_color = valor_diccionario.strip()
                color_porcentaje = borde_color.split("!")
                if borde_color in self.colores_validos:
                    self.draw = self.Color(borde_color)
                elif len(color_porcentaje)==3:#green!70!blue
                    self.draw = self.Color_porcentaje(color_porcentaje)
            #left color, right color, top color, middle color, bottom color, inner color, outer color, ball color
            elif key.find("left color")!=-1:
                #Validar si es correcto el color utilizado...
                left_color = valor_diccionario.strip()
                color_porcentaje = left_color.split("!")
                if left_color in self.colores_validos:
                    self.degradients["left_color"] = self.Color(left_color)
                elif len(color_porcentaje)==3:#green!70!blue
                    self.degradients["left_color"] = self.Color_porcentaje(color_porcentaje)
            elif key.find("right color")!=-1:
                #Validar si es correcto el color utilizado...
                right_color = valor_diccionario.strip()
                color_porcentaje = right_color.split("!")
                if right_color in self.colores_validos:
                    self.degradients["right_color"] = self.Color(right_color)
                elif len(color_porcentaje)==3:#green!70!blue
                    self.degradients["right_color"] = self.Color_porcentaje(color_porcentaje)
            elif key.find("top color")!=-1:
                #Validar si es correcto el color utilizado...
                top_color = valor_diccionario.strip()
                color_porcentaje = top_color.split("!")
                if top_color in self.colores_validos:
                    self.degradients["top_color"] = self.Color(top_color)
                elif len(color_porcentaje)==3:#green!70!blue
                    self.degradients["top_color"] = self.Color_porcentaje(color_porcentaje)
            elif key.find("middle color")!=-1:
                #Validar si es correcto el color utilizado...
                middle_color = valor_diccionario.strip()
                color_porcentaje = middle_color.split("!")
                if middle_color in self.colores_validos:
                    self.degradients["middle_color"] = self.Color(middle_color)
                elif len(color_porcentaje)==3:#green!70!blue
                    self.degradients["middle_color"] = self.Color_porcentaje(color_porcentaje)
            elif key.find("bottom color")!=-1:
                #Validar si es correcto el color utilizado...
                bottom_color = valor_diccionario.strip()
                color_porcentaje = bottom_color.split("!")
                if bottom_color in self.colores_validos:
                    self.degradients["bottom_color"] = self.Color(bottom_color)
                elif len(color_porcentaje)==3:#green!70!blue
                    self.degradients["bottom_color"] = self.Color_porcentaje(color_porcentaje)
            elif key.find("inner color")!=-1:
                #Validar si es correcto el color utilizado...
                inner_color = valor_diccionario.strip()
                color_porcentaje = inner_color.split("!")
                if inner_color in self.colores_validos:
                    self.degradients["inner_color"] = self.Color(inner_color)
                elif len(color_porcentaje)==3:#green!70!blue
                    self.degradients["inner_color"] = self.Color_porcentaje(color_porcentaje)
            elif key.find("outer color")!=-1:
                #Validar si es correcto el color utilizado...
                outer_color = valor_diccionario.strip()
                color_porcentaje = outer_color.split("!")
                if outer_color in self.colores_validos:
                    self.degradients["outer_color"] = self.Color(outer_color)
                elif len(color_porcentaje)==3:#green!70!blue
                    self.degradients["outer_color"] = self.Color_porcentaje(color_porcentaje)
            elif key.find("ball color")!=-1:
                #Validar si es correcto el color utilizado...
                ball_color = valor_diccionario.strip()
                color_porcentaje = ball_color.split("!")
                if ball_color in self.colores_validos:
                    self.degradients["ball_color"] = self.Color(ball_color)
                elif len(color_porcentaje)==3:#green!70!blue
                    self.degradients["ball_color"] = self.Color_porcentaje(color_porcentaje)
        if tipo_dato == "tupla":
            #VARIABLE SIN PARAMETROS O NORMAL
            if isinstance(valor,list):
                for estilo in valor:
                    draw_tupla(estilo,tupla=True)
            #VARIABLE CON PARAMETROS
            else:
                draw_tupla(valor)
        elif tipo_dato == "diccionario":
            #VARIABLE SIN PARAMETROS O NORMAL
            if isinstance(valor,list):
                keys_diccionario = valor
                for key in keys_diccionario:
                    draw_diccionario(key,valor_diccionario,True)
            #VARIABLE CON PARAMETROS
            else:
                draw_diccionario(valor,valor_diccionario)

    def Color_porcentaje(self,color_porcentaje):
        porcentaje = color_porcentaje[1]
        try:
            porcentaje = int(porcentaje)
        except:
            self.mensajes_de_error.append("El porcentaje debe de tener un valor INTEGER")
        if porcentaje > 100 or porcentaje < 0:
            self.mensajes_de_error.append("El porcentaje debe de tener un valor entre 0-100")
        elif not len(self.mensajes_de_error):
            color_1 = color_porcentaje[0].lower().strip()
            color_2 = color_porcentaje[2].lower().strip()
            color_1 = self.Color(color_1)
            color_2 = self.Color(color_2)
            if len(color_1) == 3 and len(color_2) == 3:
                color_elegido = []
                indice = 0
                #color RGB
                for color in color_2:
                    if color != color_1[indice]:
                        #0
                        if not color:
                            color_elegido.append((color+(porcentaje/100)))
                        #1
                        elif color:
                            color_elegido.append((color-(porcentaje/100)))
                    else:
                        color_elegido.append(color)
                    indice+=1
                return color_elegido