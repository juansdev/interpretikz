
                    #left color, right color, top color, middle color, bottom color, inner color, outer color, ball color
                    elif key.find("left color")!=-1:
                        #Validar si es correcto el color utilizado...
                        left_color = valor_diccionario[key_original].strip()
                        color_porcentaje = left_color.split("!")
                        if left_color in self.colores_validos:
                            self.left_color = self.Color(left_color)
                        elif len(color_porcentaje)==3:#green!70!blue
                            self.Color_porcentaje(color_porcentaje,"draw")
                    elif key.find("right color")!=-1:
                        #Validar si es correcto el color utilizado...
                        right_color = valor_diccionario[key_original].strip()
                        color_porcentaje = right_color.split("!")
                        if right_color in self.colores_validos:
                            self.right_color = self.Color(right_color)
                        elif len(color_porcentaje)==3:#green!70!blue
                            self.Color_porcentaje(color_porcentaje,"draw")
                    elif key.find("top color")!=-1:
                        #Validar si es correcto el color utilizado...
                        top_color = valor_diccionario[key_original].strip()
                        color_porcentaje = top_color.split("!")
                        if top_color in self.colores_validos:
                            self.top_color = self.Color(top_color)
                        elif len(color_porcentaje)==3:#green!70!blue
                            self.Color_porcentaje(color_porcentaje,"draw")
                    elif key.find("middle color")!=-1:
                        #Validar si es correcto el color utilizado...
                        middle_color = valor_diccionario[key_original].strip()
                        color_porcentaje = middle_color.split("!")
                        if middle_color in self.colores_validos:
                            self.middle_color = self.Color(middle_color)
                        elif len(color_porcentaje)==3:#green!70!blue
                            self.Color_porcentaje(color_porcentaje,"draw")
                    elif key.find("bottom color")!=-1:
                        #Validar si es correcto el color utilizado...
                        bottom_color = valor_diccionario[key_original].strip()
                        color_porcentaje = bottom_color.split("!")
                        if bottom_color in self.colores_validos:
                            self.bottom_color = self.Color(bottom_color)
                        elif len(color_porcentaje)==3:#green!70!blue
                            self.Color_porcentaje(color_porcentaje,"draw")
                    elif key.find("inner color")!=-1:
                        #Validar si es correcto el color utilizado...
                        inner_color = valor_diccionario[key_original].strip()
                        color_porcentaje = inner_color.split("!")
                        if inner_color in self.colores_validos:
                            self.inner_color = self.Color(inner_color)
                        elif len(color_porcentaje)==3:#green!70!blue
                            self.Color_porcentaje(color_porcentaje,"draw")
                    elif key.find("outer color")!=-1:
                        #Validar si es correcto el color utilizado...
                        outer_color = valor_diccionario[key_original].strip()
                        color_porcentaje = outer_color.split("!")
                        if outer_color in self.colores_validos:
                            self.outer_color = self.Color(outer_color)
                        elif len(color_porcentaje)==3:#green!70!blue
                            self.Color_porcentaje(color_porcentaje,"draw")
                    elif key.find("ball color")!=-1:
                        #Validar si es correcto el color utilizado...
                        ball_color = valor_diccionario[key_original].strip()
                        color_porcentaje = ball_color.split("!")
                        if ball_color in self.colores_validos:
                            self.ball_color = self.Color(ball_color)
                        elif len(color_porcentaje)==3:#green!70!blue
                            self.Color_porcentaje(color_porcentaje,"draw")