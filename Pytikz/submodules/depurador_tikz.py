from copy import copy, deepcopy
import enum
import re, json
from .tools_depurador_tikz.agregar_comando.tratamiento_parametros import TratamientoParametros

class Depurador_tikz():
    def __init__(self,codigo_tikz_ordenado):
        self.codigo_tikz_ordenado = codigo_tikz_ordenado
        self.comandos_tikz_validados = [] #Aqui se guardaran todos los comandos validos de Tikz.
        #Cantidad de lineas de codigo...
        self.linea_codigo = 1
        #Mensajes de error de codigo
        self.mensajes_de_error = []
        #Aqui se guardan los comandos que tienen comandos anidados dentro de si...
        self.comandos_anidadores = ["newcommand","animarPytikz"]
        #Aqui se guarnda los comandos creados por el usuario...
        self.comandos_de_usuario = {}
        #Delimitadores de los parametros del comando creados por el usuario...
        delimitadores_parametros_comando = ["!"]
        #Tool utilizado por las funciones agregar_comando y cuando se invoca ese comando creado por el usuario...
        self.tratamiento_parametros = TratamientoParametros(delimitadores_parametros_comando)
        
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
                self.__validador_codigo(codigo)
            #Si hay codigo anidado... Nivel 0 -> Nivel 1
            if(isinstance(codigo,list)):
                codigo_anidado = codigo
                for codigo in codigo_anidado:
                    #Si hay codigo anidado... Nivel 1 -> Nivel 2
                    if(isinstance(codigo,list)):
                        codigo_anidado = codigo
                        #No deberia de haber codigo anidado Nivel 2 -> Nivel 3
                        for codigo in codigo_anidado:
                            self.__validador_codigo(codigo)
                    else:
                        #Leer comandos que se almacenaran en esta clase...
                        if self.comandos_tikz_validados[len(self.comandos_tikz_validados)-1][0] in self.comandos_anidadores:
                            codigo = self.__validador_codigo(codigo,True)
                            if "ejecutar" in list(self.comandos_tikz_validados[len(self.comandos_tikz_validados)-1][1][1].keys()):
                                array_codigo = self.comandos_tikz_validados[len(self.comandos_tikz_validados)-1][1][1]["ejecutar"]
                                array_codigo.append(codigo)
                                self.comandos_tikz_validados[len(self.comandos_tikz_validados)-1][1][1]["ejecutar"] = array_codigo
                            else:
                                self.comandos_tikz_validados[len(self.comandos_tikz_validados)-1][1][1]["ejecutar"] = [codigo]
                        else:
                            self.__validador_codigo(codigo)
                    #Limpiar parametros...
                    self.comando_tikz = ""
                    self.funcion_de_comando = [[],{}]
                    self.draw_objeto = {}
                    self.parametros_comando = [[],{}]
                    self.posiciones = []
                    self.figuras = []
                    self.funcion_de_figura = [[],{}]
                #Guardar los comandos creados por el usuario y luego borrar la linea de comando que lo creo en la variable...
                if self.comandos_tikz_validados[len(self.comandos_tikz_validados)-1][0] in self.comandos_anidadores:
                    self.__agregar_comando(self.comandos_tikz_validados[len(self.comandos_tikz_validados)-1][1])
                    self.comandos_tikz_validados.pop()
            self.linea_codigo += 1
        if(len(self.mensajes_de_error)>0):
            for error in self.mensajes_de_error:
                print(error)
                return []
        return self.comandos_tikz_validados

    def __validador_codigo(self,codigo,contenido_comando=False):
        #Draw o filldraw o fill solo tienen 2 formas: "draw " o "draw["
        if(re.search("^draw ",codigo) or re.search("^filldraw ",codigo) or re.search("^fill ",codigo) or re.search("^draw\\[",codigo) or re.search("^filldraw\\[",codigo) or re.search("^fill\\[",codigo)):
            if(re.search("^draw ",codigo) or re.search("^draw\\[",codigo)):
                self.comando_tikz = "draw"
            elif(re.search("^filldraw ",codigo) or re.search("^filldraw\\[",codigo)):
                self.comando_tikz = "filldraw"
            elif(re.search("^fill ",codigo) or re.search("^fill\\[",codigo)):
                self.comando_tikz = "fill"
            self.figuras = self.__validar_figuras(codigo)
            self.__validador_parametros_comando(codigo)
            self.__validador_posiciones(codigo)
            if not contenido_comando:
                self.comandos_tikz_validados.append([self.comando_tikz,self.parametros_comando,self.posiciones,self.figuras,self.funcion_de_figura])
            else:
                return [self.comando_tikz,self.parametros_comando,self.posiciones,self.figuras,self.funcion_de_figura]
        
        elif(re.search("^shade",codigo)):
            #[['draw', [[], {'line width': ' 1.5pt', ' fill ': ' yellow', ' draw  ': ' black'}], [('200', '350'), ('200', '350'), ('50', '550'), ('40', '500'), 'cycle'], ['--'], [[], {}]]]
            #[['shade', [[], {'top color': 'red!30!red', 'bottom color': 'blue!70!black', ' line width ': ' 1pt', 'rounded corners': '2ex', 'xshift': '0cm', 'yshift': '0cm'}], [('100', '100'), ('100', '200'), ('0', '150'), ('120', '200'), ('120', '100'), ('100', '100')], ['--'], [[], {}]]]
            self.comando_tikz = "shade"
            self.figuras = self.__validar_figuras(codigo)
            self.__validador_parametros_comando(codigo)
            self.__validador_posiciones(codigo)
            if not contenido_comando:
                self.comandos_tikz_validados.append([self.comando_tikz,self.parametros_comando,self.posiciones,self.figuras,self.funcion_de_figura])
            else:
                return [self.comando_tikz,self.parametros_comando,self.posiciones,self.figuras,self.funcion_de_figura]

        elif(re.search("^tikzset",codigo)):
            self.comando_tikz = "tikzset"
            self.__validador_parametros_comando(codigo)
            if not contenido_comando:
                self.comandos_tikz_validados.append([self.comando_tikz, self.funcion_de_comando])
            else:
                return [self.comando_tikz, self.funcion_de_comando]

        elif(re.search("^definecolor",codigo)):
            self.comando_tikz = "definecolor"
            self.__validador_parametros_comando(codigo)
            if not contenido_comando:
                self.comandos_tikz_validados.append([self.comando_tikz, self.funcion_de_comando])
            else:
                return [self.comando_tikz, self.funcion_de_comando]
        
        elif(re.search("^newcommand",codigo) or re.search("^animarPytikz",codigo)):
            if re.search("^newcommand",codigo):
                self.comando_tikz = "newcommand"
            elif re.search("^animarPytikz",codigo):
                self.comando_tikz = "animarPytikz"
            self.__validador_parametros_comando(codigo)
            if not contenido_comando:
                self.comandos_tikz_validados.append([self.comando_tikz, self.funcion_de_comando])
            else:
                return [self.comando_tikz, self.funcion_de_comando]

        else:
            #Si se trata de un comando creado por el usuario...
            comando_usuario_valido = False
            for k in list(self.comandos_de_usuario.keys()):
                if(re.search("^"+k,codigo)):
                    self.comando_tikz = k
                    self.__validador_parametros_comando(codigo)
                    comando_usuario_valido = True
            if not comando_usuario_valido:
                self.mensajes_de_error.append("Error en la Linea "+str(self.linea_codigo)+ " el comando TikZ no es valido.")

    def __validador_parametros_comando(self,codigo):
        def parametros_array(codigo):
            if self.comando_tikz == "newcommand":
                raw_parametros = codigo[slice(codigo.find("[")+1,codigo.find("]["))].split(",")
            else:
                raw_parametros = codigo[slice(codigo.find("[")+1,codigo.find("]"))].split(",")
            #\draw[red, dotted, line width= 3pt] (0,0) rectangle (2.5, 2.5);
            #[['red', ' dotted', ' line width= 3pt'], {' line width': ' 3pt'}]
            for parametro in raw_parametros:
                if(parametro.find("=") != -1):
                    clave_parametro = parametro[slice(0,parametro.find("="))]
                    valor_parametro = parametro[slice(parametro.find("=")+1,len(parametro))]
                    self.parametros_comando[1][clave_parametro] = valor_parametro
                else:
                    if self.comando_tikz == "newcommand":
                        self.funcion_de_comando[0].append(parametro)
                    else:
                        self.parametros_comando[0].append(parametro)
                        #En el caso de que se cree despues de [] unos objetos asi: []{}
                        indice_de_objeto = [i for i, letra in enumerate(codigo) if letra == "}"]
                        parametros_objeto_consecutivos(self.comando_tikz,codigo,indice_de_objeto)

        def parametros_objeto_consecutivos(comando,codigo,indice_de_objeto):
            if len(indice_de_objeto):
                objeto_str = codigo[slice(codigo.find("{"),indice_de_objeto[0]+1)]+"}"
            else:
                objeto_str = ""
            #\definecolor{colfive}{RGB}{245,238,197}
            if comando == "definecolor":
                nombre_color = objeto_str.replace("{","")
                nombre_color = nombre_color.replace("}","")
                tipo_color = codigo[slice(indice_de_objeto[0]+1,indice_de_objeto[1]+1)]
                tipo_color = tipo_color.replace("{","")
                tipo_color = tipo_color.replace("}","")
                codigo_color = codigo[slice(indice_de_objeto[1]+1,indice_de_objeto[2]+1)]
                codigo_color = codigo_color.replace("{","")
                codigo_color = codigo_color.replace("}","").split(",")
                objeto_valor = [[],{tipo_color:codigo_color}]
                #[[],{estilo global/.style: [["dashed"],{line width:1.25pt,draw:cyan!75!gray}]}]
                self.funcion_de_comando[1][nombre_color] = objeto_valor
            #\mano[-0.12+\x*0.01/10]{M}{-0.25+\x*0.05/10,0.8-\x*1.42/10}{45-\x*5}{0}{-0.12+\x*0.05/10}{\c}
            elif comando in list(self.comandos_de_usuario.keys()):
                valores_a_establecer = []
                #Extraer los valores establecidos en matrices...
                for parametro in self.parametros_comando[0]:
                    valores_a_establecer.append(parametro)
                    self.parametros_comando = [[],{}]
                if objeto_str:
                    primer_objeto = objeto_str.replace("{","")
                    primer_objeto = primer_objeto.replace("}","")
                    valores_a_establecer.append(primer_objeto)
                    #Extraer los valores establecidos en objetos...
                    for i in range(len(indice_de_objeto)):
                        if i != len(indice_de_objeto)-1:
                            #0-1,1-2,2-3,3-4,4-5
                            valor = codigo[slice(indice_de_objeto[i]+1,indice_de_objeto[i+1]+1)]
                            valor = valor.replace("{","")
                            valor = valor.replace("}","")
                            valores_a_establecer.append(valor)
                #Extraer y validar los parametros a definir comparando con los parametros definidos por el usuario...
                arr_result = self.__extraer_validar_parametros_a_definir(comando)
                cantidad_de_parametros = arr_result[0]
                parametros_sin_establecer = arr_result[1]
                valores_estilos = [valor for valor in valores_a_establecer if not valor.isnumeric()]
                valores_posicion = [valor for valor in valores_a_establecer if valor.isnumeric()]
                if cantidad_de_parametros == len(valores_a_establecer):
                    #Reemplazar los valores establecido en los parametros...
                    comandos_sin_establecer = deepcopy(self.comandos_de_usuario)
                    count_exterior=0
                    for parametro in parametros_sin_establecer:#parametros_sin_establecer=> [[["#1","#2"],["#1","#2"]],[["#1","#2"],["#1","#2"]]]
                        linea_de_codigo = 0
                        for conjunto_parametro in parametro:#parametro=> [["#2"],["#2"]]
                            #conjunto_parametro=>["#2"]
                            cant_param = len(set(conjunto_parametro))-1#¿Tiene uno (0) o mas de un parametro en los mismos comandos de estilo o de posicion?
                            if cant_param>=0:
                                count_interior = 0
                                for parametro in list(set(conjunto_parametro)):#conjunto_parametro=>["#1","#2"]
                                    if count_exterior == 0:#Si son parametros a establecer en estilos...
                                        count_interior_max = len(valores_estilos)-1#Cantidad de parametros a definir...
                                        # for e,_ in enumerate(comandos_sin_establecer[comando]):
                                        comandos_sin_establecer_object = comandos_sin_establecer[comando][linea_de_codigo][1][1]#{'top color': '#1!30!white', 'bottom color': '#1!70!black', ' line width ': ' 1pt', 'rounded corners': '2ex', 'yshift': '-0.3cm', 'xshift': '0.2cm'}
                                        for k in comandos_sin_establecer_object:
                                            comandos_sin_establecer[comando][linea_de_codigo][1][1][k] = comandos_sin_establecer_object[k].replace(parametro,valores_estilos[count_interior])
                                        if count_interior_max > count_interior:
                                            count_interior+=1
                                        else:
                                            count_interior=0
                                    elif count_exterior == 1:#Si son parametros a establecer en posiciones...
                                        count_interior_max = len(valores_posicion)-1#Cantidad de parametros a definir...
                                        # for i,_ in enumerate(comandos_sin_establecer[comando]):
                                        comandos_sin_establecer_arr = comandos_sin_establecer[comando][linea_de_codigo][2]
                                        for e,_ in enumerate(comandos_sin_establecer_arr):
                                            arr_actualizado = [comando for comando in comandos_sin_establecer_arr[e]]
                                            get_indexs_a_actualizar = lambda x, xs: [i for (y, i) in zip(xs, range(len(xs))) if x == y]
                                            indexs_a_actualizar = get_indexs_a_actualizar(parametro,arr_actualizado)
                                            if len(indexs_a_actualizar):
                                                for index in indexs_a_actualizar:
                                                    arr_actualizado[index]  = arr_actualizado[index].replace(parametro,valores_posicion[count_interior])
                                                    comandos_sin_establecer[comando][linea_de_codigo][2][e] = tuple(arr_actualizado)
                                        if count_interior_max > count_interior:
                                            count_interior+=1
                                        else:
                                            count_interior=0
                            linea_de_codigo+=1
                        count_exterior+=1
                    # print("DESPUES")
                    # print(comandos_sin_establecer[comando])
                    for comando_establecido in comandos_sin_establecer[comando]:
                        self.comandos_tikz_validados.append(comando_establecido)
                else:
                    self.mensajes_de_error.append("La cantidad de valores a colocar "+str(len(valores_a_establecer))+" es diferente a la cantidad de parametros del comando (#) "+str(cantidad_de_parametros))
        #Tiene parametros
        if(codigo.find(self.comando_tikz+"[") != -1):
            if(codigo.find("]") != -1):
                parametros_array(codigo)
        #Tiene parametros funcion de Comando \tikzset{}
        elif(codigo.find(self.comando_tikz+"{")!= -1):
            if(codigo.find("}") != -1):
                #Si hay objeto como valor...
                indice_de_objeto = [i for i, letra in enumerate(codigo) if letra == "}"]
                if len(indice_de_objeto) == 1:
                    #{figure} o {mano}
                    objeto_str = codigo[slice(codigo.find("{")+1,codigo.find("}"))]
                    if self.comando_tikz == "newcommand":
                        #mano
                        self.funcion_de_comando[1]["comando"] = objeto_str
                        #Tiene parametros
                        if(codigo.find("}[") != -1):
                            if(codigo.find("][") != -1):
                                parametros_array(codigo)
                    else:
                        #figure
                        self.funcion_de_comando[0] = objeto_str
                elif len(indice_de_objeto) == 2:
                    ##{estilo global/.style = {line width=1.25pt, draw = cyan!75!gray,dashed}}
                    objeto_str = codigo[slice(codigo.find("{"),indice_de_objeto[1]+1)]
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
                    objeto_str = codigo[slice(codigo.find("{"),indice_de_objeto[0]+1)]+"}"
                    index_declaracion_valor = [i for i, letra in enumerate(objeto_str) if letra == "="]
                    if not len(index_declaracion_valor):
                        parametros_objeto_consecutivos(self.comando_tikz,codigo,indice_de_objeto)
                    else:
                        #{estilo global/.style n args = {2}}
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
        #No tiene parametros... Se trata de un comando creado que esta invocando el usuario sin parametro alguno...
        elif(self.comando_tikz in list(self.comandos_de_usuario.keys())):
            #Extraer y validar los parametros a definir comparando con los parametros definidos por el usuario...
            arr_result = self.__extraer_validar_parametros_a_definir(self.comando_tikz)
            cantidad_de_parametros = arr_result[0]
            if not cantidad_de_parametros:
                for comando_establecido in self.comandos_de_usuario[self.comando_tikz]:
                    self.comandos_tikz_validados.append(comando_establecido)
            else:
                self.mensajes_de_error.append("Error: Debes de definir la cantidad de parametros de "+str(cantidad_de_parametros)+" en el comando que invocaste.")

    def __extraer_validar_parametros_a_definir(self,comando):
        #Extraer los parametros a definir...
        parametros_sin_establecer = [[],[]]#[0] => Parametros de estilos, [1] => Parametros de posiciones...
        for i in range(len(self.comandos_de_usuario[comando])):
            estilos_parametrizados = self.comandos_de_usuario[comando][i][1][1]
            estilos_sin_definir = self.tratamiento_parametros.extraerParametrosSinDefinir(estilos_parametrizados=estilos_parametrizados,comando_invocado=True)

            posiciones_parametrizados = self.comandos_de_usuario[comando][i][2]
            posiciones_sin_definir = self.tratamiento_parametros.extraerParametrosSinDefinir(posiciones_parametrizados,comando_invocado=True)

            if len(estilos_sin_definir):
                parametros_sin_establecer[0].append(estilos_sin_definir)
            if len(posiciones_parametrizados):
                parametros_sin_establecer[1].append(posiciones_sin_definir)

        #Validar si la cantidad de parametros corresponde a la cantidad de valores a establecer..
        len_param = []
        num_superior = 0
        for i,arr in enumerate(parametros_sin_establecer):
            cantidad_de_parametros = []#[[#1],[#1,#2]]
            for parametro in arr:#[#1,#1]
                cantidad_de_parametros.append(list(set(parametro)))
            for parametro in cantidad_de_parametros:
                for param in parametro:#["#1,#2"]
                    param = int(param.replace("#",""))
                    len_param.append(param)
                len_param = list(set(len_param))
                if num_superior < len(len_param):
                    num_superior = len(len_param)
        return[num_superior,parametros_sin_establecer]

    def __validar_figuras(self,codigo):
        figuras = []
        if(codigo.find(" rectangle ")!=-1):
            figuras_regex = re.compile(" rectangle ")
            for figura in figuras_regex.finditer(codigo):
                figuras.append(figura.group().strip())
        if(codigo.find(" arc ")!=-1 or codigo.find(" arc(")!=-1):
            figuras_regex = re.compile(" arc ")
            for figura in figuras_regex.finditer(codigo):
                figuras.append(figura.group().strip())
            if not len(figuras):
                figuras_regex = re.compile(" arc\(")
                for figura in figuras_regex.finditer(codigo):
                    figuras.append(figura.group().replace("(","").strip())
        if(codigo.find("circle")!=-1):
            figuras_regex = re.compile(" circle ")
            for figura in figuras_regex.finditer(codigo):
                figuras.append(figura.group().strip())
            if not len(figuras):
                figuras_regex = re.compile(" circle\(")
                for figura in figuras_regex.finditer(codigo):
                    figuras.append(figura.group().replace("(","").strip())
        if(codigo.find(" controls ")!=-1):
            figuras_regex = re.compile(" controls ")
            for figura in figuras_regex.finditer(codigo):
                figuras.append(figura.group().strip())
        if(codigo.find(" -- ")!=-1 or codigo.find("--")!=-1):
            figuras.append("--")
        #Tiene figura con parametro
        if(codigo.find("arc[")):
            codigo_copia = codigo[slice(codigo.find("arc["),len(codigo))]
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
        return figuras if len(figuras)>0 else ""

    def __validador_posiciones(self,codigo):
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
                    else:
                        self.posiciones = []
                        #\draw[line width= 1.5pt, fill = yellow, draw  = black](5,0) -- (8,0) -- (5,3) -- cycle;
                        break
                #Solo hay 2 posiciones X y Y.
                elif(len(posicion_normal)==2):
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

    def __agregar_comando(self,funcion_de_comando):
        #[['7'], {'comando': 'mano', 'ejecutar': ['shade', [[], {'top color': '#7!30!white', 'bottom color': '#7!70!black', ' line width ': ' 1pt', 'rounded corners': '2ex', 'xshift': '0cm', 'yshift': '0cm'}], 
        # [('-0.3', '-1'), ('-0.3', '0.6'), ('0', '1'), ('0.3', '0.6'), ('0.3', '-1'), ('-0.3', '-1')], [], [[], {}]]}]
        cantidad_de_parametros = funcion_de_comando[0][0]
        nombre_funcion = funcion_de_comando[1]["comando"]
        funcion_ejecutable = funcion_de_comando[1]["ejecutar"]
        #Validar si se cumple con la cantidad de parametros en Funcion Ejecutable, establecida...
        for i in range(len(funcion_ejecutable)):
            estilos_parametrizados = funcion_ejecutable[i][1][1]
            estilos_sin_definir = self.tratamiento_parametros.extraerParametrosSinDefinir(estilos_parametrizados=estilos_parametrizados)

            posiciones_parametrizados = funcion_ejecutable[i][2]
            posiciones_sin_definir = self.tratamiento_parametros.extraerParametrosSinDefinir(posiciones_parametrizados)
            
            if len(estilos_sin_definir) and len(posiciones_sin_definir):
                parametros_sin_definir = estilos_sin_definir+posiciones_sin_definir
            elif len(estilos_sin_definir):
                parametros_sin_definir = estilos_sin_definir
            elif len(posiciones_sin_definir):
                parametros_sin_definir = posiciones_sin_definir
            else:
                parametros_sin_definir = []
            result_validacion_secuencia = self.tratamiento_parametros.validarSecuenciaNumerica(cantidad_de_parametros,parametros_sin_definir)
            if type(result_validacion_secuencia) is dict:
                self.mensajes_de_error.append(result_validacion_secuencia["error"])
                break

        if not len(self.mensajes_de_error):
            #Si todas las validaciones son correctas...
            self.comandos_de_usuario[nombre_funcion] = funcion_ejecutable