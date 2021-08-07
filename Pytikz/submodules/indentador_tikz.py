import re

class IndentadorTikz():
    def __init__(self,codigo_tikz):
        #Todos los Foreach
        codigo_foreach = re.findall(
            re.compile(r" *\\foreach+ [\\\w]+ \[?.*?\]?in {.+?} *{\n.*?\n*};",re.DOTALL),
            codigo_tikz
        )
        codigo_foreach_ordenado = []
        for foreach in codigo_foreach:
            codigo_foreach_ordenado.append(foreach.split("\n"))
            for one_foreach in codigo_foreach_ordenado:
                for each in one_foreach:
                    codigo_tikz = codigo_tikz.replace(each,"")
        #Todo código que no sea Foreach
        self.codigo_tikz_ordenado = []
            #Generar un Array por comando separandolos por "\"
        for codigo in codigo_tikz.split("\\"):
            if codigo:
                codigo = re.escape("\\"+codigo)
                codigo_valido = re.search(r" *"+codigo,codigo_tikz)
                if codigo_valido:
                    self.codigo_tikz_ordenado.append(codigo_valido.group())
        #Añadir código Foreach al listado de codigos.
        for one_foreach in codigo_foreach_ordenado:
            for each in one_foreach:
                self.codigo_tikz_ordenado.append(each)
        self.codigo_tikz_ordenado_2 = []
        self.indentacion = []
    def indentar(self):
        #FASE 1: Se saca las indentaciones del codigo TikZ
        indice = 0
        for codigo in self.codigo_tikz_ordenado:
            if codigo:
                if(codigo.find("\n") != -1):
                    codigo_a_agregar = codigo[slice(0,codigo.find("\n"))]
                    if(codigo_a_agregar):
                        self.codigo_tikz_ordenado_2.append(codigo_a_agregar)
                    else: continue
                else:
                    codigo_a_agregar = codigo[slice(0,len(codigo))]
                    if(len(codigo_a_agregar)>2):
                        self.codigo_tikz_ordenado_2.append(codigo_a_agregar)
                    else: continue
                #Sacar longitud de la indentacion
                if codigo.find("\n"):
                    if(re.search(r"^ ",codigo) and re.search(r"\b\S",codigo)):
                        self.indentacion.append(len(codigo[
                            re.search(r"^ ",codigo).start():#Desde el primer espacio
                            re.search(r"\b\S",codigo).start()-1]#Hasta el primer caracter
                        ))
                    else: self.indentacion.append(0)
                elif indice == 0:
                    self.indentacion.append(0)
                indice += 1
        print("CODIGO TIKZ ORIGINAL")
        print(self.codigo_tikz_ordenado_2)
        #FASE 2: Se ordena el Codigo TikZ en una Matriz segun Jerarquia dada por la Indentacion del Codigo.
        indice = 0
        indice_anidado = 0
        indentado_anterior = None
        self.codigo_tikz_ordenado = []
        for indentado in self.indentacion:
            def anidarCambioDeIndentacion(indentado_anterior):
                #Nivel 0
                if indentado == 0 or indentado_anterior == None:
                    if len(self.codigo_tikz_ordenado_2) > indice:
                        self.codigo_tikz_ordenado.append(self.codigo_tikz_ordenado_2[indice])#FUNCIONA
                #Nivel 1
                elif indentado == 4:
                    self.codigo_tikz_ordenado[indice_anidado].append(self.codigo_tikz_ordenado_2[indice])
                #Nivel 2
                elif indentado == 8:
                    self.codigo_tikz_ordenado[indice_anidado_anterior][indice_anidado_posterior].append(self.codigo_tikz_ordenado_2[indice])
                return indentado
            #Si el siguiente comando pertecene al mismo nivel del anterior comando o es el primer comando...
            if indentado == indentado_anterior or indentado_anterior == None:
                indentado_anterior = anidarCambioDeIndentacion(indentado_anterior)

            #Si el siguiente comando pertecene a un nivel diferente del anterior comando...
            elif indentado != indentado_anterior:
                if len(self.codigo_tikz_ordenado_2) > indice:
                    #NIVEL 1 -> NIVEL 2
                    if indentado_anterior == 4 and indentado == 8:
                        #Actualizar matriz de codigo tikz ordenado
                        indice_anidado_anterior = indice_anidado#Estara anidado en el ultimo elemento de la anidacion PADRE.
                        self.codigo_tikz_ordenado[indice_anidado_anterior].append([self.codigo_tikz_ordenado_2[indice]])
                        indice_anidado_posterior = len(self.codigo_tikz_ordenado[indice_anidado_anterior])-1#Estara anidado en el ultimo elemento de la anidacion PADRE que es una Anidacion (Matriz).
                        #Ya ubicado la matriz dentro de su anidacion correspondiente, no se volvera a ejecutar este codigo hasta que se cambie la anidacion...
                        indentado_anterior = indentado
                    
                    #NIVEL 0 -> NIVEL 1
                    elif indentado_anterior == 0 and indentado == 4:
                        #Actualizar matriz de codigo tikz ordenado
                        self.codigo_tikz_ordenado.append([self.codigo_tikz_ordenado_2[indice]])
                        indice_anidado = len(self.codigo_tikz_ordenado)-1#Esta anidado en el ultimo elemento de la matriz...
                        #Ya ubicado la matriz dentro de su anidacion correspondiente, no se volvera a ejecutar este codigo hasta que se cambie la anidacion...
                        indentado_anterior = indentado

                    #NIVEL 1 -> NIVEL 0
                    elif indentado_anterior == 4 and indentado == 0:
                        #Actualizar matriz de codigo tikz ordenado
                        self.codigo_tikz_ordenado.append(self.codigo_tikz_ordenado_2[indice])
                        indice_anidado = 0#No esta anidado...
                        #Ya ubicado la matriz dentro de su anidacion correspondiente, no se volvera a ejecutar este codigo hasta que se cambie la anidacion...
                        indentado_anterior = indentado
                    
                    #NIVEL 2 -> NIVEL 1
                    elif indentado_anterior == 8 and indentado == 4:
                        #Actualizar matriz de codigo tikz ordenado
                        self.codigo_tikz_ordenado[indice_anidado_anterior].append([self.codigo_tikz_ordenado_2[indice]])
                        indice_anidado = len(self.codigo_tikz_ordenado)-1#Esta anidado en el ultimo elemento de la matriz...
                        #Ya ubicado la matriz dentro de su anidacion correspondiente, no se volvera a ejecutar este codigo hasta que se cambie la anidacion...
                        indentado_anterior = indentado
            indice+=1
        print("INDENTACION DETECTADAS POR LINEAS")
        print(self.indentacion)
        return self.codigo_tikz_ordenado