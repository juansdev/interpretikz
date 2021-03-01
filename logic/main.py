from .depurador.depurador_tikz import Depurador_tikz 
from .graficar_tikz.graficar_tikz import Graficar_tikz 

class Pytikz():

    def __init__(self,codigo_tikz,area_de_dibujar):
        #Ordenar codigo de forma Jerarjica por Anidado.
        self.codigo_tikz_ordenado = codigo_tikz.split("\\")
        print("CODIGO ORIGINAL")
        print(self.codigo_tikz_ordenado)
        self.identacion(self.codigo_tikz_ordenado)
        #Se analiza cada codigo si esta escrito correctamente segun la documentacion TikZ.
        self.depurado_codigo = self.depurar_codigo_tikz()
        if(self.depurado_codigo):
            self.dibujar_tikz(self.comandos_tikz,area_de_dibujar)

    def identacion(self,codigo_tikz_ordenado):
        #FASE 1: Se saca las indentaciones del codigo TikZ
        codigo_tikz_ordenado = codigo_tikz_ordenado
        codigo_tikz_ordenado_2 = []
        indentacion = []
        indice = 0
        for codigo in codigo_tikz_ordenado:
            if codigo:
                codigo_tikz_ordenado_2.append(codigo[slice(0,codigo.find("\n") if codigo.find("\n") != -1 else len(codigo))])
                #Sacar longitud de la indentacion
                str_inverso = codigo[len(codigo)::-1]
                if codigo.find("\n") != -1:
                    slice_object = slice(codigo.find("\n")+1,len(str_inverso)-str_inverso.find(" "))
                    if indice == 0:
                        indentacion.append(0)    
                    indentacion.append(len(codigo[slice_object]))
                else:
                    if indice == 0:
                        indentacion.append(0)
                indice += 1
        #FASE 2: Se ordena el Codigo TikZ en una Matriz segun Jerarquia dada por la Indentacion del Codigo.
        indice = 0
        indice_anidado = 0
        indentado_anterior = None
        codigo_tikz_ordenado = []
        print("CODIGO TIKZ ORDENADO")
        print(codigo_tikz_ordenado_2)
        #[\begin{figure},[\centering,\begin{tikzpicture},[\draw[estilo global] (0,0) rectangle (2.5, 2.5);],\end{tikzpicture}],\end{figure}]
        for indentado in indentacion:
            #Si el siguiente comando pertecene al mismo nivel del anterior comando o es el primer comando...
            if indentado == indentado_anterior or indentado_anterior == None:
                #Nivel 0
                if indentado == 0 or indentado_anterior == None:
                    if len(codigo_tikz_ordenado_2) > indice:
                        codigo_tikz_ordenado.append(codigo_tikz_ordenado_2[indice])#FUNCIONA
                #Nivel 1
                elif indentado == 4:
                    codigo_tikz_ordenado[indice_anidado].append(codigo_tikz_ordenado_2[indice])
                #Nivel 2
                elif indentado == 8:
                    codigo_tikz_ordenado[indice_anidado_anterior][indice_anidado_posterior].append(codigo_tikz_ordenado_2[indice])
                indentado_anterior = indentado

            #Si el siguiente comando pertecene a un nivel diferente del anterior comando...
            elif indentado != indentado_anterior:
                # print("Indentado: "+str(indentado))
                # print("Indentado anterior: "+str(indentado_anterior))
                #NIVEL 1 -> NIVEL 2
                if indentado_anterior == 4 and indentado == 8:
                    #Actualizar matriz de codigo tikz ordenado
                    indice_anidado_anterior = indice_anidado#Estara anidado en el ultimo elemento de la anidacion PADRE.
                    codigo_tikz_ordenado[indice_anidado_anterior].append([codigo_tikz_ordenado_2[indice]])
                    indice_anidado_posterior = len(codigo_tikz_ordenado[indice_anidado_anterior])-1#Estara anidado en el ultimo elemento de la anidacion PADRE que es una Anidacion (Matriz).
                    #Ya ubicado la matriz dentro de su anidacion correspondiente, no se volvera a ejecutar este codigo hasta que se cambie la anidacion...
                    indentado_anterior = indentado
                
                #NIVEL 0 -> NIVEL 1
                #0 != 4 = YEPA
                #indentado == 0 and indentado_anterior == 4 -> Este sera el ultimo comando anidado antes de cambiar de nivel de anidacion.
                elif indentado_anterior == 0 and indentado == 4:
                    #Actualizar matriz de codigo tikz ordenado
                    codigo_tikz_ordenado.append([codigo_tikz_ordenado_2[indice]])
                    indice_anidado = len(codigo_tikz_ordenado)-1#Esta anidado en el ultimo elemento de la matriz...
                    #Ya ubicado la matriz dentro de su anidacion correspondiente, no se volvera a ejecutar este codigo hasta que se cambie la anidacion...
                    indentado_anterior = indentado

                #NIVEL 1 -> NIVEL 0
                elif indentado_anterior == 4 and indentado == 0:
                    #Actualizar matriz de codigo tikz ordenado
                    codigo_tikz_ordenado.append(codigo_tikz_ordenado_2[indice])
                    indice_anidado = 0#No esta anidado...
                    #Ya ubicado la matriz dentro de su anidacion correspondiente, no se volvera a ejecutar este codigo hasta que se cambie la anidacion...
                    indentado_anterior = indentado
                
                #NIVEL 2 -> NIVEL 1
                elif indentado_anterior == 8 and indentado == 4:
                    #Actualizar matriz de codigo tikz ordenado
                    codigo_tikz_ordenado[indice_anidado_anterior].append(codigo_tikz_ordenado_2[indice])
                    indice_anidado = len(codigo_tikz_ordenado)-1#Esta anidado en el ultimo elemento de la matriz...
                    #Ya ubicado la matriz dentro de su anidacion correspondiente, no se volvera a ejecutar este codigo hasta que se cambie la anidacion...
                    indentado_anterior = indentado
            indice+=1
        self.codigo_tikz_ordenado = codigo_tikz_ordenado
        print("INDENTACION")
        print(indentacion)
        print("LINEAS DE CODIGO")
        print(self.codigo_tikz_ordenado)
        
    def depurar_codigo_tikz(self):
        #1. SIEMPRE EMPIEZA EL COMANDO CON "\"
        #2. DESPUES DEL COMANDO PEGADO PUEDE VENIR CON UNOS PARAMETROS {} O [] O () O PALABRA_CLAVE
        #3. LOS [] SE COMPORTAN COMO MATRICES.
        #4. LOS {} SE COMPORTAN COMO DICCIONARIOS.
        #5. LOS () SE COMPORTAN COMO TUPLAS.
        #6. LA PALABRA_CLAVE PUEDE TENER UN PARAMETRO EJ: PALABRA_CLAVE[]
        #7. LOS PARAMETROS CON {} PUEDE TENER A SU VEZ MAS ANIDACIONES {}
        #8. EL COMANDO DENTRO DEL COMANDO SIEMPRE VA CON UNOS ESPACIOS MINIMO DE 4.
        depurador_tikz = Depurador_tikz(self.codigo_tikz_ordenado) 
        self.comandos_tikz = depurador_tikz.depurar_codigo() #Aqui se guardaran todos los comandos validos de Tikz.
        
        if(len(self.comandos_tikz)>0):
            print("CODIGO TIKZ DETECTADOS")
            print(self.comandos_tikz)
            return True
        else:
            return False

    def dibujar_tikz(self,comandos_tikz_validos,area_de_dibujar):
        graficar_tikz = Graficar_tikz(area_de_dibujar)
        graficar_tikz.graficar(comandos_tikz_validos)