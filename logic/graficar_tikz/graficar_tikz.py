from kivy.graphics import Color, Line, Rectangle, Ellipse
from kivy.metrics import pt, cm
import re

class Graficar_tikz():
    def __init__(self,area_de_dibujar):
        self.area_de_dibujar = area_de_dibujar
        self.mensajes_de_error = []

    def graficar(self,comandos_tikz_validos):
        for comando_tikz in comandos_tikz_validos:
            if(len(self.mensajes_de_error)>0):
                for error in self.mensajes_de_error:
                    print(error)
                    return []
            #VALIDACION DRAW "FIGURA"
            if(self.draw_figura(validar_comandos=comando_tikz)):
                #comando_tikz[1] = [['red', ' dotted'], {' line width': ' 3pt'}]
                self.draw_figura(comando_tikz[1],comando_tikz[2],comando_tikz[3],self.area_de_dibujar,comando_tikz)
        if(len(self.mensajes_de_error)>0):
            for error in self.mensajes_de_error:
                print(error)
                return []

    def draw_figura(self,draw_parametros=None,draw_posicion=None,figura=None,area_de_dibujar=None,validar_parametro=None,validar_comandos=None):
        if(validar_comandos):
            if validar_comandos[0] == "draw" or validar_comandos[0] == "filldraw": return True
            else: return False
        #FIGURA SIN PARAMETROS
        elif(len(validar_parametro[len(validar_parametro)-1][0]) == 0 and len(list(validar_parametro[len(validar_parametro)-1][1].keys())) == 0 or len(validar_parametro) == 4):
            #DISPONIBLES EN TIK
                #DOTTED = loosely dashed, densely dashed, loosely dotted, and densely dotted
                #COLORES: NO SE TODOS LOS DISPONIBLES
            #\draw[red, dotted, line width= 3pt] (0,0) rectangle (2.5, 2.5);
            
            tipo_de_linea_validos = ["loosely dashed", "dashed", "densely dashed", "loosely dotted", "dotted", "densely dotted"]
            colores_validos = ["red","blue","green","cyan","black","yellow"]

            #draw_parametros = [['red', ' dotted'], {' line width': ' 3pt'}]
            #fill = yellow, draw  = black
            
            #AGREGAR DRAW PARAMETROS DEL COMANDO A VARIABLES
            tipo_de_linea = ""
            line_width = 1.0
            fill = (1,1,1) if validar_parametro[0] == "draw" else (0,0,0)
            draw = (0,0,0)

            indice = 0
            for parametro in draw_parametros:
                #Explorar por []
                if indice == 0:
                    for estilo in parametro:
                        estilo = estilo.strip()
                        if estilo in colores_validos:
                            draw = self.color(estilo)
                        elif estilo in tipo_de_linea_validos:
                            tipo_de_linea = estilo
                #Explorar por {}
                elif indice == 1:
                    #Recorrer keys de {}
                    keys_diccionario = list(parametro.keys())
                    for key in keys_diccionario:
                        # print("key")
                        # print(key)
                        if key.find("line width")!=-1:
                            #Validar si es correcta la unidad de medida utilizada...
                            line_width = self.validar_metrica(parametro[key])
                        elif key.find("fill")!=-1:
                            #Validar si es correcto el color utilizado...
                            relleno = parametro[key].strip()
                            if relleno in colores_validos:
                                fill = self.color(relleno)
                        elif key.find("draw")!=-1:
                            #Validar si es correcto el color utilizado...
                            borde_color = parametro[key].strip()
                            if borde_color in colores_validos:
                                draw = self.color(borde_color)
                indice+=1
            
            if not len(self.mensajes_de_error):
                #Dibujar rectangulo
                #\draw[red, dotted, line width= 3pt] (0,0) rectangle (2.5, 2.5);
                #\draw[line with=1.25pt, draw = cyan!75!gray,dashed] (1,1) rectangle (2.5, 2.5);
                if(figura=="rectangle"):
                    punto_inicial_x_y = draw_posicion[0][0]
                    punto_final_x_y = draw_posicion[0][1]
                    ancho = draw_posicion[1][0]
                    alto = draw_posicion[1][1]
                    #line_width = {"pt":"2"}
                    if line_width != 1.0:
                        line_width = line_width[list(line_width.keys())[0]]
                    print("line_width")
                    print(line_width)
                    #Dibujar en el area de dibujado...
                    #Si hay separacion de lineas...
                    if tipo_de_linea:
                        with area_de_dibujar.canvas:
                            #BORDE RECTANGULO CON LINEAS DISCONTINUADAS
                            area_de_dibujar.color = Color(draw[0], draw[1], draw[2])
                            Line(points=[punto_inicial_x_y, punto_final_x_y, punto_inicial_x_y, punto_final_x_y+alto, punto_inicial_x_y, punto_final_x_y+alto, punto_inicial_x_y+ancho, punto_final_x_y+alto, punto_inicial_x_y+ancho, punto_final_x_y+alto, punto_inicial_x_y+ancho, punto_final_x_y,punto_inicial_x_y+ancho, punto_final_x_y, punto_inicial_x_y, punto_final_x_y], dash_offset=10, dash_length=5)
                            #RELLENO RECTANGULO
                            area_de_dibujar.color = Color(fill[0], fill[1], fill[2])
                            Rectangle(pos=draw_posicion[0],size=draw_posicion[1])
                    #Si no hay...
                    else:
                        with area_de_dibujar.canvas:
                            #BORDE RECTANGULO
                            area_de_dibujar.color = Color(draw[0], draw[1], draw[2])
                            Line(points=[punto_inicial_x_y, punto_final_x_y, punto_inicial_x_y, punto_final_x_y+alto, punto_inicial_x_y, punto_final_x_y+alto, punto_inicial_x_y+ancho, punto_final_x_y+alto, punto_inicial_x_y+ancho, punto_final_x_y+alto, punto_inicial_x_y+ancho, punto_final_x_y,punto_inicial_x_y+ancho, punto_final_x_y, punto_inicial_x_y, punto_final_x_y],width=line_width)
                            #RELLENO RECTANGULO
                            area_de_dibujar.color = Color(fill[0], fill[1], fill[2])
                            Rectangle(pos=draw_posicion[0],size=draw_posicion[1])
                #DIBUJAR ARCO
                #\draw[color=ColorA,line width=0.1cm,rounded corners=2ex] (100,100) arc (0:90:5cm);
                elif(figura=="arc"):
                    posicion_x = draw_posicion[0][0]
                    posicion_y = draw_posicion[0][1]
                    angulo_inicial = float(450) if float(draw_posicion[1][0]) == 0.0 else float(450-(float(draw_posicion[1][0])))
                    angulo_final = float(450) if float(draw_posicion[1][1]) == 0.0 else float(450-(float(draw_posicion[1][1])))
                    radio = self.validar_metrica(draw_posicion[1][2])
                    if line_width != 1.0:
                        line_width = line_width[list(line_width.keys())[0]]
                    if radio != 1.0:
                        radio = radio[list(radio.keys())[0]]
                    print("line_width")
                    print(line_width)
                    #Line:
                    # circle: (60,60,60,90,180)#CIRCULO CERRADO, 40 DE RADIO
                    if tipo_de_linea:
                        with area_de_dibujar.canvas:
                            #ARCO CON LINEAS DISCONTINUADAS
                            area_de_dibujar.color = Color(draw[0], draw[1], draw[2])
                            #(center_x, center_y, radius, angle_start, angle_end, segments):
                            Line(circle=[posicion_x,posicion_y,radio,angulo_inicial,angulo_final], dash_offset=10, dash_length=5)
                    #Si no hay...
                    else:
                        with area_de_dibujar.canvas:
                            #ARCO
                            area_de_dibujar.color = Color(draw[0], draw[1], draw[2])
                            Line(circle=[posicion_x,posicion_y,radio,angulo_inicial,angulo_final],width=line_width)
                #DIBUJAR CIRCULO
                #\draw[draw=red,fill=yellow] (0,0) circle (1cm);
                elif(figura=="circle"):
                    posicion_x = draw_posicion[0][0]
                    posicion_y = draw_posicion[0][1]
                    radio = self.validar_metrica(draw_posicion[1])
                    if line_width != 1.0:
                        line_width = line_width[list(line_width.keys())[0]]
                    if radio != 1.0:
                        radio = radio[list(radio.keys())[0]]
                    print("line_width")
                    print(line_width)
                    #Line:
                    # circle: (60,60,60,90,180)#CIRCULO CERRADO, 40 DE RADIO
                    if tipo_de_linea:
                        with area_de_dibujar.canvas:
                            #RELLENO CIRCULO
                            area_de_dibujar.color = Color(fill[0], fill[1], fill[2])
                            ancho = radio*2
                            alto = radio*2
                            Ellipse(pos=(posicion_x,posicion_y),size=(ancho,alto))
                            #BORDE CIRCULO CON LINEAS DISCONTINUADAS
                            posicion_x+=radio
                            posicion_y+=radio
                            area_de_dibujar.color = Color(draw[0], draw[1], draw[2])
                            Line(circle=[posicion_x,posicion_y,radio], dash_offset=10, dash_length=line_width)
                    #Si no hay...
                    else:
                        with area_de_dibujar.canvas:
                            #RELLENO CIRCULO
                            area_de_dibujar.color = Color(fill[0], fill[1], fill[2])
                            ancho = radio*2
                            alto = radio*2
                            Ellipse(pos=(posicion_x,posicion_y),size=(ancho,alto))
                            # #BORDE CIRCULO
                            posicion_x+=radio
                            posicion_y+=radio
                            area_de_dibujar.color = Color(draw[0], draw[1], draw[2])
                            Line(circle=[posicion_x,posicion_y,radio])
                #\draw[left color=yellow, bottom color=orange, right color=red,rounded] (0,100) .. controls (100,200) and (200,300) .. (300,400) .. (200,100) .. (300,200);
                elif(figura=="controls"):
                    print("line_width")
                    print(line_width)
                    coordenadas = []
                    indice = 0
                    #[(5.0, 0.0), (8.0, 0.0), (5.0, 3.0), 'cycle']
                    for posicion in draw_posicion:
                        coordenadas.append(posicion[0])
                        coordenadas.append(posicion[1])
                    if len(coordenadas)>=4:
                        #ancho_de_linea = {"pt":"2"}
                        if line_width != 1.0:
                            line_width = line_width[list(line_width.keys())[0]]
                        #Dibujar en el area de dibujado...
                        #Si hay separacion de lineas...
                        if tipo_de_linea:
                            with area_de_dibujar.canvas:
                                area_de_dibujar.color = Color(draw[0], draw[1], draw[2])
                                Line(bezier=coordenadas, dash_offset=10, dash_length=5)
                        #Si no hay...
                        else:
                            with area_de_dibujar.canvas:
                                area_de_dibujar.color = Color(draw[0], draw[1], draw[2])
                                Line(bezier=coordenadas, width=line_width)
                    else:
                        print("Error cerca de "+str(coordenadas[len(coordenadas)-1])+" se esperaba posiciones de Origen y de Destino")

                #Si no hay figura...
                #\draw[line width= 1.5pt, fill = yellow, draw  = black](100,100) -- (200,0) -- (50,300) -- (40,200) -- cycle;
                else:
                    coordenadas = []
                    indice = 0
                    #[(5.0, 0.0), (8.0, 0.0), (5.0, 3.0), 'cycle']
                    for posicion in draw_posicion:
                        if len(coordenadas) < 4:
                            coordenadas.append(posicion[0])
                            coordenadas.append(posicion[1])
                        elif len(coordenadas) >= 4 and posicion != "cycle":
                            #indice = 3 ACTUAL
                            #indice = 2 -> 10.0
                            #indice = 3 -> 80.0
                            coordenada_anterior_x = coordenadas[len(coordenadas)-2]
                            coordenada_anterior_y = coordenadas[len(coordenadas)-1]
                            #DESDE ANTERIOR COORDENADA X,Y
                            coordenadas.append(coordenada_anterior_x)
                            coordenadas.append(coordenada_anterior_y)
                            #HASTA NUEVA COORDENADA X,Y
                            coordenadas.append(posicion[0])
                            coordenadas.append(posicion[1])
                        #Si es Cycle...
                        else:
                            coordenada_anterior_x = coordenadas[len(coordenadas)-2]
                            coordenada_anterior_y = coordenadas[len(coordenadas)-1]
                            #DESDE ANTERIOR COORDENADA X,Y
                            coordenadas.append(coordenada_anterior_x)
                            coordenadas.append(coordenada_anterior_y)
                            #HASTA COORDENADA ORIGEN X,Y
                            coordenadas.append(coordenadas[0])
                            coordenadas.append(coordenadas[1])
                    if len(coordenadas)>=4:
                        #ancho_de_linea = {"pt":"2"}
                        if line_width != 1.0:
                            line_width = line_width[list(line_width.keys())[0]]
                        #Dibujar en el area de dibujado...
                        #Si hay separacion de lineas...
                        if tipo_de_linea:
                            with area_de_dibujar.canvas:
                                area_de_dibujar.color = Color(draw[0], draw[1], draw[2])
                                Line(points=coordenadas, dash_offset=10, dash_length=5)
                        #Si no hay...
                        else:
                            with area_de_dibujar.canvas:
                                area_de_dibujar.color = Color(draw[0], draw[1], draw[2])
                                Line(points=coordenadas, width=line_width)
                    else:
                        print("Error cerca de "+str(coordenadas[len(coordenadas)-1])+" se esperaba posiciones de Origen y de Destino")
        else:
        #FIGURA CON PARAMETROS
            print("ENTRE")


    def draw_linea(self):
        pass
        # punto_inicial_x_y = draw_posicion[0][0]
        # punto_final_x_y = draw_posicion[0][1]
        # ancho = draw_posicion[1][0]
        # alto = draw_posicion[1][1]
        # #ancho_de_linea = {"pt":"2"}
        # line_width = pt(ancho_de_linea["pt"]) if ancho_de_linea["pt"] else 1.0
        # if tipo_de_linea:
        #     with area_de_dibujar.canvas:
        #         area_de_dibujar.color = Color(1 if color_definido == "red" else 0, 1 if color_definido == "green" else 0, 1 if color_definido == "blue" else 0)
        #         Line(points=[punto_inicial_x_y, punto_final_x_y, punto_inicial_x_y, punto_final_x_y+alto, punto_inicial_x_y, punto_final_x_y+alto, punto_inicial_x_y+ancho, punto_final_x_y+alto, punto_inicial_x_y+ancho, punto_final_x_y+alto, punto_inicial_x_y+ancho, punto_final_x_y,punto_inicial_x_y+ancho, punto_final_x_y, punto_inicial_x_y, punto_final_x_y], dash_offset=10, dash_length=5)
        # #Si no hay...
        # else:
        #     with area_de_dibujar.canvas:
        #         area_de_dibujar.color = Color(1 if color_definido == "red" else 0, 1 if color_definido == "green" else 0, 1 if color_definido == "blue" else 0)
        #         Line(points=[punto_inicial_x_y, punto_final_x_y, punto_inicial_x_y, punto_final_x_y+alto, punto_inicial_x_y, punto_final_x_y+alto, punto_inicial_x_y+ancho, punto_final_x_y+alto, punto_inicial_x_y+ancho, punto_final_x_y+alto, punto_inicial_x_y+ancho, punto_final_x_y,punto_inicial_x_y+ancho, punto_final_x_y, punto_inicial_x_y, punto_final_x_y], width=line_width)
    
    def validar_metrica(self,metrica_a_validar):
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
                            return {"".join(metrica):pt(valor_metrica)}
                        elif unidad_metrica == "cm":
                            return {"".join(metrica):cm(valor_metrica)}
                    else:
                        return 1.0
        else:
            self.mensajes_de_error.append("Error cerca de "+metrica_a_validar)
        return 1.0

    def color(self,color):
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