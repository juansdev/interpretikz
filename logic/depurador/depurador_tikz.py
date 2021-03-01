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
            self.draw_parametros = [[],{}]#EJ:[red, dotted, line width= 3pt]

            #Se utiliza en: \draw, \filldraw, \shade
            self.posiciones = []#EJ:[(0,0),(2.5, 2.5)]

            #Se utiliza en: \draw
            self.figura = "" #EJ: rectangle

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
                    self.draw_parametros = [[],{}]
                    self.posiciones = []
                    self.figura = ""
                    self.funcion_de_figura = [[],{}]
            self.linea_codigo += 1
        if(len(self.mensajes_de_error)>0):
            for error in self.mensajes_de_error:
                print(error)
                return []
        return self.comandos_tikz

    def validador_codigo(self,codigo):
        def figuras(codigo):
            if(codigo.find("rectangle")!=-1):
                return "rectangle"
            elif(codigo.find("arc ")!=-1):
                return "arc"
            elif(codigo.find("circle")!=-1):
                return "circle"
            elif(codigo.find("controls")!=-1):
                return "controls"
            return ""
        
        if(re.search("^draw",codigo)):
            self.comando_tikz = "draw"
            #\draw[red, dotted, line width= 3pt] (0,0) rectangle (2.5, 2.5);
            #Tiene figura
            self.figura = figuras(codigo)
            self.validador_parametros(codigo)
            self.validador_posiciones(codigo)
            #Si no tiene figura
            if not self.figura:
                if(codigo.find("arc[")):
                    codigo_copia = codigo[slice(codigo.find("arc["),len(codigo))]
                    # print(codigo_copia)
                    if(codigo_copia.find("]") != -1):
                        self.figura = "arc"
                        raw_parametros = codigo_copia[slice(codigo_copia.find("[")+1,codigo_copia.find("]"))].split(",")
                        #\draw[thick, <->, >=stealth](2,-2) arc[start angle = 0, end angle = 45, radius = 1]; 
                        for parametro in raw_parametros:
                            if(parametro.find("=") != -1):
                                clave_parametro = parametro[slice(0,parametro.find("="))]
                                valor_parametro = parametro[slice(parametro.find("=")+1,len(parametro))]
                                self.funcion_de_figura[1][clave_parametro] = valor_parametro
                            else:
                                self.funcion_de_figura[0].append(parametro)
            self.comandos_tikz.append([self.comando_tikz,self.draw_parametros,self.posiciones,self.figura,self.funcion_de_figura])
        
        elif(re.search("^filldraw",codigo)):
            self.comando_tikz = "filldraw"
            #\draw[red, dotted, line width= 3pt] (0,0) rectangle (2.5, 2.5);
            #Tiene figura
            self.figura = figuras(codigo)
            self.validador_parametros(codigo)
            self.validador_posiciones(codigo)
            self.comandos_tikz.append([self.comando_tikz,self.draw_parametros,self.posiciones,self.figura])
        
        elif(re.search("^shade",codigo)):
            self.comando_tikz = "shade"
            #\draw[red, dotted, line width= 3pt] (0,0) rectangle (2.5, 2.5);
            self.validador_parametros(codigo)
            self.validador_posiciones(codigo)
            self.comandos_tikz.append([self.comando_tikz,self.draw_parametros,self.posiciones])

        elif(re.search("^tikzset",codigo)):
            self.comando_tikz = "tikzset"
            self.validador_parametros(codigo)
            self.comandos_tikz.append([self.comando_tikz,self.funcion_de_comando])

    def validador_parametros(self,codigo):
        #Tiene parametros
        if(codigo.find("draw[") != -1):
            if(codigo.find("]") != -1):
                raw_parametros = codigo[slice(codigo.find("[")+1,codigo.find("]"))].split(",")
                #\draw[red, dotted, line width= 3pt] (0,0) rectangle (2.5, 2.5);
                #[['red', ' dotted', ' line width= 3pt'], {' line width': ' 3pt'}]
                for parametro in raw_parametros:
                    if(parametro.find("=") != -1):
                        clave_parametro = parametro[slice(0,parametro.find("="))]
                        valor_parametro = parametro[slice(parametro.find("=")+1,len(parametro))]
                        self.draw_parametros[1][clave_parametro] = valor_parametro
                    else:
                        self.draw_parametros[0].append(parametro)
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
                    print("objeto_str")
                    print(objeto_str)
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
                        print("valor_diccionario_objeto")
                        print(valor_diccionario_objeto)#[line width=1.25pt, draw = cyan!75!gray,dashed]
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
                        # print("valor_diccionario_objeto")
                        # print(valor_diccionario_objeto)
                        objeto_valor = [[[],{}],[[],{}]]
                        indice = 0
                        for parametro in valor_diccionario_objeto:
                            if(parametro.find("=") != -1):
                                valor_clave_parametro = parametro[slice(0,parametro.find("="))]
                                valor_valor_parametro = parametro[slice(parametro.find("=")+1,len(parametro))]
                                if indice == 0:
                                    objeto_valor[0][1][valor_clave_parametro] = valor_valor_parametro
                                elif indice == 1:
                                    objeto_valor[1][1][valor_clave_parametro] = valor_valor_parametro
                            else:
                                if indice == 0:
                                    objeto_valor[0][0].append(parametro)
                                elif indice == 1:
                                    objeto_valor[1][0].append(parametro)
                            indice+=1
                        self.funcion_de_comando[1][key_diccionario_objeto_padre] = {key_diccionario_objeto:objeto_valor}
                #estilo global/.style n args = {2}{line width=1.25pt, draw = #1, #2}, estilo global/.default = {cyan}{dotted}
                #ARRAY[0] = [[#2],{line width:1.25pt, draw : #1}]
                #ARARY[1] = [[],{estilo global/.default:["cyan","dotted"]}]
                #[[],{estilo global/.style n args: {2:[[#ARRAY 0],[#ARRAY 1]]}}]
                        
    def validador_posiciones(self,codigo):
        #Tiene posiciones ()
        if codigo.find("(") != -1 or codigo.find(")") != -1:
            codigo_copia = codigo
            #Primero se saca el contenido de los ()
            while True:
                if codigo_copia.find("(") != -1 and codigo_copia.find(")") != -1:
                    posiciones_validar = codigo_copia[slice(codigo_copia.find("(")+1,codigo_copia.find(")"))].split(",")
                    radio_arc = codigo_copia[slice(codigo_copia.find("(")+1,codigo_copia.find(")"))].split(":")
                elif codigo_copia.find("(") != -1 or codigo_copia.find(")") != -1:
                    self.mensajes_de_error.append("Error en la linea "+str(self.linea_codigo)+" se esperaba ()")
                    posiciones_validar = []
                    radio_arc = []
                else:
                    posiciones_validar = []
                    radio_arc = []
                # print("CODIGO COPIA ANTERIOR")
                # print(codigo_copia)
                #arc (0:30:3mm) -> Parametros donde (Angulo inicial, Angulo final, radio)
                if(len(radio_arc)==3):
                    posicion_valido = True
                    #Se verifica si los valores de los () sean validos
                    indice = 0
                    for posicion in radio_arc:
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
                        self.posiciones.append(tuple(map(str,radio_arc)))
                        #Elimino el parametro ya validado del codigo.
                        codigo_copia = codigo_copia[slice(codigo_copia.find(")")+1,len(codigo_copia))]
                        # print("CODIGO COPIA ACTUALIZADO")
                        # print(codigo_copia)
                    else:
                        self.posiciones = []
                        #\draw[line width= 1.5pt, fill = yellow, draw  = black](5,0) -- (8,0) -- (5,3) -- cycle;
                        break
                #Solo hay 2 posiciones X y Y.
                elif(len(posiciones_validar)==2):
                    # print(posiciones_validar)
                    posicion_valido = True
                    #Se verifica si los valores de los () sean validos
                    for posicion in posiciones_validar:
                        #["",""]
                        if not posicion:
                            self.mensajes_de_error.append("Debe de haber 2 coordenadas, el Valor X y el Valor Y")
                            posicion_valido = False
                            break
                        #[1.1,2.2]
                        else:
                            try:
                                float(posicion)
                            except:
                                self.mensajes_de_error.append("El valor de la coordenada debe de ser de tipo FLOAT o INTEGER")
                                posicion_valido = False
                                break
                    if posicion_valido:
                        self.posiciones.append(tuple(map(float,posiciones_validar)))
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
                elif(len(posiciones_validar)==1 and self.figura == "circle"):
                    try:
                        int(posiciones_validar)
                        self.mensajes_de_error.append("Error en la Linea "+str(self.linea_codigo)+" se esperaba una Unidad Metrica valida.")
                        self.posiciones = []
                        break
                    except:
                        self.posiciones.append(posiciones_validar[0])#"0.8cm"
                        #Elimino el parametro ya validado del codigo.
                        codigo_copia = codigo_copia[slice(codigo_copia.find(")")+1,len(codigo_copia))]
                else:
                    for posicion in posiciones_validar:
                        #Si hay mas o menos de 2 posiciones...
                        # print("ERROR EN")
                        # print(posicion)
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