from .submodules.indentador_tikz import IndentadorTikz
from .submodules.depurador_tikz import DepuradorTikz
from .submodules.validador_pytikz import ValidadorPytikz
from .submodules.kivy_python.lanzar_md_dialog import LanzarMDDialog

class Pytikz():

    def __init__(self,codigo_tikz,area_de_dibujar): 
        #Ordenar codigo de forma Jerarjica por Anidado.
        self.codigo_tikz_ordenado = IndentadorTikz(codigo_tikz).indentar()
        print("INDENTACION APLICADA")
        print(self.codigo_tikz_ordenado)

        #Se analiza cada codigo si esta escrito correctamente segun la documentacion TikZ
        depuracion_validado = DepuradorTikz(self.codigo_tikz_ordenado).depurar_codigo()

        #Si es valido...
        if(isinstance(depuracion_validado,list)):
            #Aqui se guardaran todos los comandos validos de Tikz.
            comandos_tikz_validados = depuracion_validado
            print("CODIGO TIKZ VALIDADO")
            print(comandos_tikz_validados)
            #Si esta escrito de forma correcta, se procede a dibujar...
            self.__ejecutar_pytikz(comandos_tikz_validados,area_de_dibujar)

        #Si lo no lo es...
        elif(isinstance(depuracion_validado,dict)):
            self.__lanzar_error(depuracion_validado["error"])

    def __ejecutar_pytikz(self,comandos_tikz_validados,area_de_dibujar):
        validador_pytikz = ValidadorPytikz(comandos_tikz_validados,area_de_dibujar)
        error_validacion = validador_pytikz.validar_pytikz()
        if(error_validacion):
            self.__lanzar_error(error_validacion["error"])

    def __lanzar_error(self,error_arr):
        #Si devuelve un error juntar los mensajes en un String
        mensaje_de_error = ""
        cantidad_error = 1
        for error in error_arr:
            mensaje_de_error+="#"+str(cantidad_error)+" "+error+"\n"
            cantidad_error+=1
        #Lanzar dialog de error
        md_dialog = LanzarMDDialog()
        md_dialog.lanzar_error_pytikz(mensaje_de_error)
        print(mensaje_de_error)