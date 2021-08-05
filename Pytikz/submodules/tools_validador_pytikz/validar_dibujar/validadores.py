from kivy.metrics import pt, cm
import re

class Validadores():
    def __init__(self,estilos_predeterminados):
        self.tipo_de_linea_validos = ["loosely dashed", "dashed", "densely dashed", "loosely dotted", "dotted", "densely dotted"]
        self.colores_validos = ["red","blue","green","cyan","black","yellow"]
        #Estilos predeterminados
        self.degradients = estilos_predeterminados["degradients"]
        self.fill = estilos_predeterminados["fill"]
        self.draw = estilos_predeterminados["draw"]
        self.tipo_de_linea = estilos_predeterminados["tipo_de_linea"]
        self.line_width = estilos_predeterminados["line_width"]
        self.metrica_validos = estilos_predeterminados["metrica_validos"]
        self.mensajes_de_error = []

    def validar_metrica(self,metrica_a_validar):
        unidad_metrica = re.compile("[a-z]")
        metrica = []
        distanciamiento_metrica = []
        for unidad in unidad_metrica.finditer(metrica_a_validar):
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
                    if unidad_metrica in self.metrica_validos:
                        valor_metrica = float(metrica_a_validar[:distanciamiento_metrica[0]])
                        if unidad_metrica == "pt":
                            return pt(valor_metrica)
                        elif unidad_metrica == "cm":
                            return cm(valor_metrica)
                    else:
                        return 1.0
        else:
            try:
                float(metrica_a_validar)
            except:
                self.mensajes_de_error.append("Error cerca de "+metrica_a_validar)
            if not len(self.mensajes_de_error):
                return float(metrica_a_validar)
        return 10.0
    
    def validar_estilos(self,tipo_dato,valor,valor_diccionario=None):
        def draw_tupla(valor,tupla=False):
            if tupla:
                valor = valor.strip()
            color_porcentaje = valor.split("!")
            if valor in self.colores_validos:
                self.draw = self.__color_a_rgb(valor)
            elif valor in self.tipo_de_linea_validos:
                self.tipo_de_linea = valor
            elif len(color_porcentaje)==3:#green!70!blue
                self.draw = self.__validar_color_porcentaje(color_porcentaje)
            else:
                self.mensajes_de_error.append("Error cerca de '"+valor+"'. No es un valor valido.")
        def draw_diccionario(valor,valor_diccionario,diccionario=False):
            if diccionario:
                key_original = valor
                valor_diccionario = valor_diccionario[key_original]
            key = valor.strip()
            if key.find("line width")!=-1:
                #Validar si es correcta la unidad de medida utilizada...
                self.line_width = self.validar_metrica(valor_diccionario)
            elif key.find("fill")!=-1 or key.find("color")!=-1 and key.find(" color")==-1:
                #Validar si es correcto el color utilizado...
                relleno = ""
                #Si es un codgio RGB
                if type(valor_diccionario) is list:
                    relleno = [int(num)/255 for num in valor_diccionario if int(num)>=0]
                    if len(relleno) == 3:
                        self.fill = relleno
                    else:
                        relleno = "("+",".join([str(elem) for elem in valor_diccionario])+")"
                        self.mensajes_de_error.append("Error cerca de '"+relleno+"'. No es un valor valido.")
                else:
                    relleno = valor_diccionario.strip()
                    color_porcentaje = relleno.split("!")
                    if relleno in self.colores_validos:
                        self.fill = self.__color_a_rgb(relleno)
                    elif len(color_porcentaje)==3:#green!70!blue
                        self.fill = self.__validar_color_porcentaje(color_porcentaje)
                    else:
                        self.mensajes_de_error.append("Error cerca de '"+relleno+"'. No es un valor valido.")
            elif key.find("draw")!=-1:
                borde_color = ""
                #Si es un codigo RGB...
                if type(valor_diccionario) is list:
                    borde_color = [int(num)/255 for num in valor_diccionario if int(num)>=0]
                    if len(borde_color) == 3:
                        self.draw = borde_color
                    else:
                        borde_color = "("+",".join([str(elem) for elem in valor_diccionario])+")"
                        self.mensajes_de_error.append("Error cerca de '"+borde_color+"'. No es un valor valido.")
                else: 
                    #Validar si es correcto el color utilizado...
                    borde_color = valor_diccionario.strip()
                    color_porcentaje = borde_color.split("!")
                    if borde_color in self.colores_validos:
                        self.draw = self.__color_a_rgb(borde_color)
                    elif len(color_porcentaje)==3:#green!70!blue
                        self.draw = self.__validar_color_porcentaje(color_porcentaje)
                    else:
                        self.mensajes_de_error.append("Error cerca de '"+borde_color+"'. No es un valor valido.")
            #left color, right color, top color, middle color, bottom color, inner color, outer color, ball color
            elif key.find("left color")!=-1:
                #Validar si es correcto el color utilizado...
                left_color = valor_diccionario.strip()
                color_porcentaje = left_color.split("!")
                if left_color in self.colores_validos:
                    self.degradients["left_color"] = self.__color_a_rgb(left_color)
                elif len(color_porcentaje)==3:#green!70!blue
                    self.degradients["left_color"] = self.__validar_color_porcentaje(color_porcentaje)
                else:
                    self.mensajes_de_error.append("Error cerca de '"+left_color+"'. No es un valor valido.")
            elif key.find("right color")!=-1:
                #Validar si es correcto el color utilizado...
                right_color = valor_diccionario.strip()
                color_porcentaje = right_color.split("!")
                if right_color in self.colores_validos:
                    self.degradients["right_color"] = self.__color_a_rgb(right_color)
                elif len(color_porcentaje)==3:#green!70!blue
                    self.degradients["right_color"] = self.__validar_color_porcentaje(color_porcentaje)
                else:
                    self.mensajes_de_error.append("Error cerca de '"+right_color+"'. No es un valor valido.")
            elif key.find("top color")!=-1:
                #Validar si es correcto el color utilizado...
                top_color = valor_diccionario.strip()
                color_porcentaje = top_color.split("!")
                if top_color in self.colores_validos:
                    self.degradients["top_color"] = self.__color_a_rgb(top_color)
                elif len(color_porcentaje)==3:#green!70!blue
                    self.degradients["top_color"] = self.__validar_color_porcentaje(color_porcentaje)
                else:
                    self.mensajes_de_error.append("Error cerca de '"+top_color+"'. No es un valor valido.")
            elif key.find("middle color")!=-1:
                #Validar si es correcto el color utilizado...
                middle_color = valor_diccionario.strip()
                color_porcentaje = middle_color.split("!")
                if middle_color in self.colores_validos:
                    self.degradients["middle_color"] = self.__color_a_rgb(middle_color)
                elif len(color_porcentaje)==3:#green!70!blue
                    self.degradients["middle_color"] = self.__validar_color_porcentaje(color_porcentaje)
                else:
                    self.mensajes_de_error.append("Error cerca de '"+middle_color+"'. No es un valor valido.")
            elif key.find("bottom color")!=-1:
                #Validar si es correcto el color utilizado...
                bottom_color = valor_diccionario.strip()
                color_porcentaje = bottom_color.split("!")
                if bottom_color in self.colores_validos:
                    self.degradients["bottom_color"] = self.__color_a_rgb(bottom_color)
                elif len(color_porcentaje)==3:#green!70!blue
                    self.degradients["bottom_color"] = self.__validar_color_porcentaje(color_porcentaje)
                else:
                    self.mensajes_de_error.append("Error cerca de '"+bottom_color+"'. No es un valor valido.")
            elif key.find("inner color")!=-1:
                #Validar si es correcto el color utilizado...
                inner_color = valor_diccionario.strip()
                color_porcentaje = inner_color.split("!")
                if inner_color in self.colores_validos:
                    self.degradients["inner_color"] = self.__color_a_rgb(inner_color)
                elif len(color_porcentaje)==3:#green!70!blue
                    self.degradients["inner_color"] = self.__validar_color_porcentaje(color_porcentaje)
                else:
                    self.mensajes_de_error.append("Error cerca de '"+inner_color+"'. No es un valor valido.")
            elif key.find("outer color")!=-1:
                #Validar si es correcto el color utilizado...
                outer_color = valor_diccionario.strip()
                color_porcentaje = outer_color.split("!")
                if outer_color in self.colores_validos:
                    self.degradients["outer_color"] = self.__color_a_rgb(outer_color)
                elif len(color_porcentaje)==3:#green!70!blue
                    self.degradients["outer_color"] = self.__validar_color_porcentaje(color_porcentaje)
                else:
                    self.mensajes_de_error.append("Error cerca de '"+outer_color+"'. No es un valor valido.")
            elif key.find("ball color")!=-1:
                #Validar si es correcto el color utilizado...
                ball_color = valor_diccionario.strip()
                color_porcentaje = ball_color.split("!")
                if ball_color in self.colores_validos:
                    self.degradients["ball_color"] = self.__color_a_rgb(ball_color)
                elif len(color_porcentaje)==3:#green!70!blue
                    self.degradients["ball_color"] = self.__validar_color_porcentaje(color_porcentaje)
                else:
                    self.mensajes_de_error.append("Error cerca de '"+ball_color+"'. No es un valor valido.")
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
        return (self.degradients,self.fill,self.draw,self.tipo_de_linea,self.line_width,self.mensajes_de_error)

    def __validar_color_porcentaje(self,color_porcentaje):
        porcentaje = color_porcentaje[1]
        try:
            porcentaje = int(porcentaje)
        except:
            self.mensajes_de_error.append("El porcentaje debe de tener un valor INTEGER")
        if not len(self.mensajes_de_error):
            if porcentaje > 100 or porcentaje < 0:
                self.mensajes_de_error.append("El porcentaje debe de tener un valor entre 0-100")
            elif not len(self.mensajes_de_error):
                color_1 = color_porcentaje[0].lower().strip()
                color_2 = color_porcentaje[2].lower().strip()
                color_1 = self.__color_a_rgb(color_1)
                color_2 = self.__color_a_rgb(color_2)
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
    
    def __color_a_rgb(self,color):
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
        elif color == "purple":
            return (.5019,0,.5019)
        else:
            self.mensajes_de_error.append("El color "+color+" no esta disponible.")
            return ()
