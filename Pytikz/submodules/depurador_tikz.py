import re, json

class Depurador_tikz():
    def __init__(self,codigo_tikz_ordenado):
        self.codigo_tikz_ordenado = codigo_tikz_ordenado
        self.comandos_tikz = [] #Aqui se guardaran todos los comandos validos de Tikz.
        #Cantidad de lineas de codigo...
        self.linea_codigo = 1
        #Mensajes de error de codigo
        self.mensajes_de_error = []
        
    def depurar_codigo(self):
        for codigo in self.codigo_tikz_ordenado:
            if(len(self.mensajes_de_error)>0):
                for error in self.mensajes_de_error:
                    print(error)
                    return []
            #Comando utilizado...
            self.comando_tikz = ""#EJ:\draw, \shade, \filldraw

            #Se utiliza en: \tikzset \begin
            self.funcion_de_comando = [[],{}]

            #Libreria o estilo o texto a utilizar por ese comando...
            self.draw_objeto = {}#\begin{figure} o \caption{Cuadro hola mundo Tikz} o \tikzset{estilo global/.style = {line width=1.25pt, draw = cyan!75!gray,dashed}}

            #EJ COMANDO: \draw[red, dotted, line width= 3pt] (0,0) rectangle (2.5, 2.5);
            #Se utiliza en: \draw, \shade, \filldraw
            self.parametros_comando = [[],{}]#EJ:[red, dotted, line width= 3pt]

            #Se utiliza en: \draw, \filldraw, \shade
            self.posiciones = []#EJ:[(0,0),(2.5, 2.5)]

            #Se utiliza en: \draw
            self.figuras = [] #EJ: rectangle

            #Se utiliza en: \draw
            self.funcion_de_figura = [[],{}]#EJ: arc[start angle = 0, end angle = 45, radius = 1];

            #Si no hay codigo anidado... Nivel 0
            if(not isinstance(codigo,list)):
                self.validador_codigo(codigo)
            #Si hay codigo anidado... Nivel 0 -> Nivel 1
            if(isinstance(codigo,list)):
                codigo_anidado = codigo
                for codigo in codigo_anidado:
                    #Si hay codigo anidado... Nivel 1 -> Nivel 2
                    if(isinstance(codigo,list)):
                        codigo_anidado = codigo
                        #No deberia de haber codigo anidado Nivel 2 -> Nivel 3
                        for codigo in codigo_anidado:
                            self.validador_codigo(codigo)
                    else:
                        self.validador_codigo(codigo)
                    #Limpiar parametros...
                    self.comando_tikz = ""
                    self.funcion_de_comando = [[],{}]
                    self.draw_objeto = {}
                    self.parametros_comando = [[],{}]
                    self.posiciones = []
                    self.figuras = []
                    self.funcion_de_figura = [[],{}]
            self.linea_codigo += 1
        if(len(self.mensajes_de_error)>0):
            for error in self.mensajes_de_error:
                print(error)
                return []
        return self.comandos_tikz

    def validador_codigo(self,codigo):
        #Draw o filldraw o fill solo tienen 2 formas: "draw " o "draw["
        if(re.search("^draw ",codigo) or re.search("^filldraw ",codigo) or re.search("^fill ",codigo) or re.search("^draw\\[",codigo) or re.search("^filldraw\\[",codigo) or re.search("^fill\\[",codigo)):
            if(re.search("^draw ",codigo) or re.search("^draw\\[",codigo)):
                self.comando_tikz = "draw"
            elif(re.search("^filldraw ",codigo) or re.search("^filldraw\\[",codigo)):
                self.comando_tikz = "filldraw"
            elif(re.search("^fill ",codigo) or re.search("^fill\\[",codigo)):
                self.comando_tikz = "fill"
                
            self.figuras = self.validar_figuras(codigo)
            self.validador_parametros_comando(codigo)
            self.validador_posiciones(codigo)
            self.comandos_tikz.append([self.comando_tikz,self.parametros_comando,self.posiciones,self.figuras,self.funcion_de_figura])
        
        elif(re.search("^shade",codigo)):
            self.comando_tikz = "shade"
            self.validador_parametros_comando(codigo)
            self.validador_posiciones(codigo)
            self.comandos_tikz.append([self.comando_tikz,self.parametros_comando,self.posiciones,self.figuras,self.funcion_de_figura])

        elif(re.search("^tikzset",codigo)):
            self.comando_tikz = "tikzset"
            self.validador_parametros_comando(codigo)
            self.comandos_tikz.append([self.comando_tikz, self.funcion_de_comando])
        else:
            self.mensajes_de_error.append("Error en la Linea "+str(self.linea_codigo)+ " el comando TikZ no es valido.")

    def validador_parametros_comando(self,codigo):
        #Tiene parametros
        if(codigo.find(self.comando_tikz+"[") != -1):
            if(codigo.find("]") != -1):
                raw_parametros = codigo[slice(codigo.find("[")+1,codigo.find("]"))].split(",")
                #\draw[red, dotted, line width= 3pt] (0,0) rectangle (2.5, 2.5);
                #[['red', ' dotted', ' line width= 3pt'], {' line width': ' 3pt'}]
                for parametro in raw_parametros:
                    if(parametro.find("=") != -1):
                        clave_parametro = parametro[slice(0,parametro.find("="))]
                        valor_parametro = parametro[slice(parametro.find("=")+1,len(parametro))]
                        self.parametros_comando[1][clave_parametro] = valor_parametro
                    else:
                        self.parametros_comando[0].append(parametro)
        #Tiene parametros funcion de Comando \tikzset{}
        elif(codigo.find(self.comando_tikz+"{")!= -1):
            if(codigo.find("}") != -1):
                ##estilo global/.style = {line width=1.25pt, draw = cyan!75!gray,dashed}
                #Si hay objeto como valor...
                cantidad_de_objetos = [i for i, letra in enumerate(codigo) if letra == "}"]
                if len(cantidad_de_objetos) == 1:
                    #{figure}
                    objeto_str = codigo[slice(codigo.find("{")+1,codigo.find("}"))]
                    #figure
                    self.funcion_de_comando[0] = objeto_str
                elif len(cantidad_de_objetos) == 2:
                    ##{estilo global/.style = {line width=1.25pt, draw = cyan!75!gray,dashed}}
                    objeto_str = codigo[slice(codigo.find("{"),cantidad_de_objetos[1]+1)]
                    index_declaracion_valor = [i for i, letra in enumerate(objeto_str) if letra == "="]
                    index_declaracion_valor = index_declaracion_valor[0]
                    ##{estilo global/.style : {line width=1.25pt, draw = cyan!75!gray,dashed}}
                    objeto_str = "{"+'"'+objeto_str[objeto_str.find("{")+1:objeto_str.find("=")]+'":"'+objeto_str[objeto_str.find("=")+1:len(objeto_str)-1]+'"}'
                    #"'"+test[:len(test)]+"'" 
                    diccionario_objeto = {}
                    try:
                        ##OBJETO {estilo global/.style : "{line width=1.25pt, draw = cyan!75!gray,dashed}"}
                        diccionario_objeto = json.loads(objeto_str)
                    except:
                        self.mensajes_de_error.append("Error en la Linea "+str(self.linea_codigo))
                    if diccionario_objeto:
                        key_diccionario_objeto = list(diccionario_objeto.keys())[0]
                        valor_diccionario_objeto = diccionario_objeto[key_diccionario_objeto]
                        valor_diccionario_objeto = valor_diccionario_objeto[slice(valor_diccionario_objeto.find("{")+1,valor_diccionario_objeto.find("}"))].split(",")
                        objeto_valor = [[],{}]
                        for parametro in valor_diccionario_objeto:
                            if(parametro.find("=") != -1):
                                valor_clave_parametro = parametro[slice(0,parametro.find("="))]
                                valor_valor_parametro = parametro[slice(parametro.find("=")+1,len(parametro))]
                                objeto_valor[1][valor_clave_parametro] = valor_valor_parametro
                            else:
                                objeto_valor[0].append(parametro)
                        #[[],{estilo global/.style: [["dashed"],{line width:1.25pt,draw:cyan!75!gray}]}]
                        self.funcion_de_comando[1][key_diccionario_objeto] = objeto_valor
                else:
                    #{estilo global/.style n args = {2}}
                    objeto_str = codigo[slice(codigo.find("{"),cantidad_de_objetos[0]+1)]+"}"
                    index_declaracion_valor = [i for i, letra in enumerate(objeto_str) if letra == "="]
                    objeto_valor_objeto_str = [i for i, letra in enumerate(objeto_str) if letra == "{"]
                    objeto_valor_general = [i for i, letra in enumerate(codigo) if letra == "{"]
                    index_declaracion_valor = index_declaracion_valor[0]
                    #{"estilo global/.style n args" = {"2":ARRAY_STR}}
                    objeto_str = "{"+'"'+objeto_str[objeto_str.find("{")+1:objeto_str.find("=")]+'":{"'+objeto_str[objeto_valor_objeto_str[1]+1:objeto_str.find("}")]+'":"'+codigo[objeto_valor_general[2]:len(codigo)-1]+'"}}'
                    diccionario_objeto = {}
                    try:
                        diccionario_objeto = json.loads(objeto_str)
                    except:
                        self.mensajes_de_error.append("Error en la Linea "+str(self.linea_codigo))
                    if diccionario_objeto:
                        #estilo global/.style n args 
                        key_diccionario_objeto_padre = list(diccionario_objeto.keys())[0]#'estilo global/.style n args '
                        valor_diccionario_objeto = diccionario_objeto[key_diccionario_objeto_padre]#{'2': '{line width=1.25pt, draw = #1, #2}, estilo global/.default = {cyan}{dotted}'}
                        key_diccionario_objeto = list(valor_diccionario_objeto.keys())[0]#"2"
                        valor_diccionario_objeto = valor_diccionario_objeto[str(key_diccionario_objeto)]
                        #ARRAY['{line width=1.25pt', ' draw = #1', ' #2}', ' estilo global/.default = {cyan}{dotted}']
                        valor_diccionario_objeto = valor_diccionario_objeto.split(",")
                        valor_diccionario_objeto_limpio = []
                        for valor in valor_diccionario_objeto:
                            if valor.find("{") != -1 or valor.find("}") != -1:
                                valor_limpio = ""
                                if valor.find("{") != -1:
                                    valor_limpio = valor[valor.find("{")+1::].strip()
                                    if valor_limpio.find("}") != -1:
                                        valor_limpiar_impureza = []
                                        valor_limpio = [valor for valor in valor_limpio.split("}") if valor]
                                        for valor_2 in valor_limpio:
                                            if valor_2.find("{") != -1:
                                                valor_limpiar_impureza.append(valor_2[valor_2.find("{")+1::])
                                            else:
                                                valor_limpiar_impureza.append(valor_2)
                                        valor_limpio = "["+",".join(valor_limpiar_impureza)+"]"
                                    valor_diccionario_objeto_limpio.append(valor[0:valor.find("{")].strip()+valor_limpio)
                                else:
                                    valor_diccionario_objeto_limpio.append(valor[0:valor.find("}")].strip())
                            else:
                                valor_diccionario_objeto_limpio.append(valor.strip())
                        # print("valor_diccionario_objeto")
                        # print(valor_diccionario_objeto)
                        objeto_valor = [[[],{}],[[],{}]]
                        indice = 0
                        for parametro in valor_diccionario_objeto_limpio:
                            if indice != len(valor_diccionario_objeto_limpio)-1:
                                if(parametro.find("=") != -1):
                                    valor_clave_parametro = parametro[slice(0,parametro.find("="))]
                                    valor_valor_parametro = parametro[slice(parametro.find("=")+1,len(parametro))]
                                    objeto_valor[0][1][valor_clave_parametro] = valor_valor_parametro
                                else:
                                    objeto_valor[0][0].append(parametro)
                            else:
                                if(parametro.find("=") != -1):
                                    valor_clave_parametro = parametro[slice(0,parametro.find("="))]
                                    valor_valor_parametro = parametro[slice(parametro.find("=")+1,len(parametro))]
                                    objeto_valor[1][1][valor_clave_parametro] = valor_valor_parametro
                                else:
                                    objeto_valor[1][0].append(parametro)
                            indice+=1
                        self.funcion_de_comando[1][key_diccionario_objeto_padre] = {key_diccionario_objeto:objeto_valor}
                #estilo global/.style n args = {2}{line width=1.25pt, draw = #1, #2}, estilo global/.default = {cyan}{dotted}
                #ARRAY[0] = [[#2],{line width:1.25pt, draw : #1}] -> [['#2'], {'line width': '1.25pt', ' draw ': ' #1'}]
                #ARARY[1] = [[],{estilo global/.default:["cyan","dotted"]}] -> [[], {'estilo global/.default ': '[cyan,dotted]'}]]
                #[[],{estilo global/.style n args: {2:[[#ARRAY 0],[#ARRAY 1]]}}]

    def validar_figuras(self,codigo):
        figuras = []
        if(codigo.find(" rectangle ")!=-1):
            figuras_regex = re.compile(" rectangle ")
            for figura in figuras_regex.finditer(codigo):
                figuras.append(figura.group().strip())
        if(codigo.find(" arc ")!=-1):
            figuras_regex = re.compile(" arc ")
            for figura in figuras_regex.finditer(codigo):
                figuras.append(figura.group().strip())
        if(codigo.find("circle")!=-1):
            figuras_regex = re.compile(" circle ")
            for figura in figuras_regex.finditer(codigo):
                figuras.append(figura.group().strip())
        if(codigo.find(" controls ")!=-1):
            figuras_regex = re.compile(" controls ")
            for figura in figuras_regex.finditer(codigo):
                figuras.append(figura.group().strip())
        if(codigo.find(" -- ")!=-1):
            figuras.append("--")
        #Tiene figura con parametro
        if(codigo.find("arc[")):
            codigo_copia = codigo[slice(codigo.find("arc["),len(codigo))]
            # print(codigo_copia)
            if(codigo_copia.find("]") != -1):
                raw_parametros = codigo_copia[slice(codigo_copia.find("[")+1,codigo_copia.find("]"))].split(",")
                #\draw[thick, <->, >=stealth](2,-2) arc[start angle = 0, end angle = 45, radius = 1]; 
                for parametro in raw_parametros:
                    if(parametro.find("=") != -1):
                        clave_parametro = parametro[slice(0,parametro.find("="))]
                        valor_parametro = parametro[slice(parametro.find("=")+1,len(parametro))]
                        self.funcion_de_figura[1][clave_parametro] = valor_parametro
                    else:
                        self.funcion_de_figura[0].append(parametro)
                figuras.append("arc")
        print("figuras por linea")
        print(figuras)
        return figuras if len(figuras)>0 else ""

    def validador_posiciones(self,codigo):
        #Tiene posiciones ()
        if codigo.find("(") != -1 or codigo.find(")") != -1:
            codigo_copia = codigo
            #Primero se saca el contenido de los ()
            while True:
                if codigo_copia.find("(") != -1 and codigo_copia.find(")") != -1:
                    posicion_normal = codigo_copia[slice(codigo_copia.find("(")+1,codigo_copia.find(")"))].split(",")
                    posicion_por_angulo = codigo_copia[slice(codigo_copia.find("(")+1,codigo_copia.find(")"))].split(":")
                elif codigo_copia.find("(") != -1 or codigo_copia.find(")") != -1:
                    self.mensajes_de_error.append("Error en la linea "+str(self.linea_codigo)+" se esperaba ()")
                    posicion_normal = []
                    posicion_por_angulo = []
                else:
                    posicion_normal = []
                    posicion_por_angulo = []
                # print("CODIGO COPIA ANTERIOR")
                # print(codigo_copia)
                #arc (0:30:3mm) -> Parametros donde (Angulo inicial, Angulo final, radio)
                if(len(posicion_por_angulo)==3):
                    posicion_valido = True
                    #Se verifica si los valores de los () sean validos
                    indice = 0
                    for posicion in posicion_por_angulo:
                        #["",""]
                        if not posicion:
                            self.mensajes_de_error.append("Debe de haber 3 coordenadas, el Valor Angulo Inicial, Angulo Final, Radio")
                            posicion_valido = False
                            break
                        #[1.1,2.2]
                        else:
                            if indice < 2:
                                try:
                                    float(posicion)
                                except:
                                    self.mensajes_de_error.append("El valor debe de ser de tipo FLOAT o INTEGER")
                                    posicion_valido = False
                                    break
                        indice+=1
                    if posicion_valido:
                        self.posiciones.append(tuple(map(str,posicion_por_angulo)))
                        #Elimino el parametro ya validado del codigo.
                        codigo_copia = codigo_copia[slice(codigo_copia.find(")")+1,len(codigo_copia))]
                        # print("CODIGO COPIA ACTUALIZADO")
                        # print(codigo_copia)
                    else:
                        self.posiciones = []
                        #\draw[line width= 1.5pt, fill = yellow, draw  = black](5,0) -- (8,0) -- (5,3) -- cycle;
                        break
                #\draw (0,0) -- (90:1cm); -> Parametros donde (Angulo, Unidad a dibujar a partir del angulo.)
                elif(len(posicion_por_angulo)==2):
                    posicion_valido = True
                    #Se verifica si los valores de los () sean validos
                    indice = 0
                    for posicion in posicion_por_angulo:
                        #["",""]
                        if not posicion:
                            self.mensajes_de_error.append("Debe de haber 2 valores, el Angulo y la Unidad Metrica")
                            posicion_valido = False
                            break
                        #[1.1,2.2]
                        else:
                            if indice < 1:
                                try:
                                    float(posicion)
                                except:
                                    self.mensajes_de_error.append("El valor debe de ser de tipo FLOAT o INTEGER")
                                    posicion_valido = False
                                    break
                        indice+=1
                    if posicion_valido:
                        valor_angulo = ":".join(posicion_por_angulo)
                        self.posiciones.append(valor_angulo)
                        #Elimino el parametro ya validado del codigo.
                        codigo_copia = codigo_copia[slice(codigo_copia.find(")")+1,len(codigo_copia))]
                        # print("CODIGO COPIA ACTUALIZADO")
                        # print(codigo_copia)
                    else:
                        self.posiciones = []
                        #\draw[line width= 1.5pt, fill = yellow, draw  = black](5,0) -- (8,0) -- (5,3) -- cycle;
                        break
                #Solo hay 2 posiciones X y Y.
                elif(len(posicion_normal)==2):
                    # print(posicion_normal)
                    posicion_valido = True
                    #Se verifica si los valores de los () sean validos
                    for posicion in posicion_normal:
                        #["",""]
                        if not posicion:
                            self.mensajes_de_error.append("Debe de haber 2 coordenadas, el Valor X y el Valor Y")
                            posicion_valido = False
                            break
                    if posicion_valido:
                        self.posiciones.append(tuple(map(str,posicion_normal)))
                        #Elimino el parametro ya validado del codigo.
                        codigo_copia = codigo_copia[slice(codigo_copia.find(")")+1,len(codigo_copia))]
                        # print("CODIGO COPIA ACTUALIZADO")
                        # print(codigo_copia)
                    else:
                        self.posiciones = []
                        #\draw[line width= 1.5pt, fill = yellow, draw  = black](5,0) -- (8,0) -- (5,3) -- cycle;
                        break
                #Solo hay 1 parametro... 
                #\Circle
                elif(len(posicion_normal)==1 and "circle" in self.figuras):
                    self.posiciones.append(posicion_normal[0])#"0.8cm"
                    #Elimino el parametro ya validado del codigo.
                    codigo_copia = codigo_copia[slice(codigo_copia.find(")")+1,len(codigo_copia))]
                else:
                    for posicion in posicion_normal:
                        #Si hay mas o menos de 2 posiciones...
                        print("ERROR EN")
                        print(posicion)
                        if(posicion!=""):
                            self.mensajes_de_error.append("En la Linea "+str(self.linea_codigo)+" se esperaban 2 coordenadas con un valor valido.")
                            break
                        else:
                            self.mensajes_de_error.append("El valor de la coordenada debe de ser de tipo FLOAT o INTEGER")
                            break
                    break
        #Luego se añade el Cycle "Si existe"
        if codigo.find("cycle;") != -1 and len(self.posiciones) > 0:
            #Este Cycle solo debe de existir al final...
            self.posiciones.append("cycle")