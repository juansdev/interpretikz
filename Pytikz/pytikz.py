from .submodules.indentador_tikz import Indentador_tikz
from .submodules.depurador_tikz import Depurador_tikz
from .submodules.validador_pytikz import Validador_pytikz

class Pytikz():

    def __init__(self,codigo_tikz,area_de_dibujar): 
        #Ordenar codigo de forma Jerarjica por Anidado.
        self.codigo_tikz_ordenado = Indentador_tikz(codigo_tikz).indentar()
        print("INDENTACION APLICADA")
        print(self.codigo_tikz_ordenado)
        #Se analiza cada codigo si esta escrito correctamente segun la documentacion TikZ.
        depuracion_validado = self.__depurar_codigo_tikz()
        if(depuracion_validado):
            self.__ejecutar_pytikz(self.comandos_tikz_validados,area_de_dibujar)
        
    def __depurar_codigo_tikz(self):
        self.comandos_tikz_validados = Depurador_tikz(self.codigo_tikz_ordenado).depurar_codigo() #Aqui se guardaran todos los comandos validos de Tikz.
        if(len(self.comandos_tikz_validados)>0):
            print("CODIGO TIKZ VALIDADO")
            print(self.comandos_tikz_validados)
            return True
        else:
            return False

    def __ejecutar_pytikz(self,comandos_tikz_validados,area_de_dibujar):
        Validador_pytikz(comandos_tikz_validados,area_de_dibujar).validar_pytikz()