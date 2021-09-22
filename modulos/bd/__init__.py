"""Modulo encargado de realizar la conexion a la base de datos de la aplicacion y de acceder al Api RestFul del mismo.

Clase: 
- ConexionBD"""

#Otras librerias
import os, codecs
#BD
from typing import Union, List
from sqlite3 import *
#Librerias propias
import globales
from modulos.kivy.otros_widgets.aviso_informativo import AvisoInformativo
from modulos.logging import GenerarDiagnostico
class ConexionBD(object):
    """Realiza la conexion a la base de datos, crea tablas si no existen ya en la base de datos y se accede al Api RestFul de la BD."""

    __instance = None

    def __new__(cls, *args):
        """Utilizamos el patron de diseño Singleton, almacena la primera instanciazacion en la propiedad "__instance".

        Parametro:
        - cls (object), clase a instanciar.
        - args (List[any]), argumentos de la clase.
        
        Retorna:
        - La clase instanciada (object).
        """
        if ConexionBD.__instance is None:
            ConexionBD.__instance = object.__new__(cls)
            ConexionBD.__instance.__init__(ConexionBD.__instance)
            ConexionBD.__instance.__conectar_a_la_base_de_datos(ConexionBD.__instance)
        return ConexionBD.__instance
    
    def __init__(self, *args):
        """1. Crea una base de datos en la ruta "bd/main.db", si la BD no esta creado.
        2. Realiza una conexion a la base de datos.
        3. Agrega las tablas necesarias para el aplicativo, en la base de datos si estas no existen.
        4. Se añadiran datos por defecto a las tablas recien creadas.
        
        Atributo:
        ruta_bd = 'bd/main.db' (str), ruta de la base de datos.
        """
        self.ruta_bd = os.path.join(globales.ruta_raiz,'bd/main.db')

    def __conectar_a_la_base_de_datos(self, *args) -> None:
        """Agrega las tablas necesarias para el aplicativo, en la base de datos si estas no existen. Si la base de datos ya existe, se generara un mensaje de diagnostico."""
        con = connect(self.ruta_bd)
        cursor = con.cursor()
        try:
            self.__crear_tablas(cursor,con)
            GenerarDiagnostico(self.__class__.__name__,"Tablas cargadas de forma exitosa a la base de datos",'info')
        except Exception as e:
            GenerarDiagnostico(self.__class__.__name__,e,'info')
        datos_por_defecto_insertados = self.__insertar_datos_por_defecto(cursor,con)
        if(datos_por_defecto_insertados):
            GenerarDiagnostico(self.__class__.__name__,"Datos por defecto cargados de forma exitosa a la base de datos",'info')
        else:
            GenerarDiagnostico(self.__class__.__name__,"Los datos por defectos ya habian sido cargados por primera vez",'info')
        con.close()

    def __crear_tablas(self,cursor:Cursor,con:Connection) -> None:
        """Crea las tablas necesarias del aplicativo en la base de datos.
        
        Parametros:
        - cursor (Cursor)
        - con (Connection)"""
        cursor.execute(
            """
            CREATE TABLE dibujos_usuario(
                id                    INTEGER        PRIMARY KEY NOT NULL,
                nombre_dibujo        TEXT                       NOT NULL,
                comandos_dibujo     TEXT                       NOT NULL
            )
            """
        )
        con.commit()
        cursor.execute(
            """
            CREATE TABLE imagenes_de_fondo(
                id                    INTEGER        PRIMARY KEY NOT NULL,
                ruta        TEXT                       NOT NULL,
                fecha_de_uso    TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        con.commit()
        cursor.execute(
            """
            CREATE TABLE estilos(
                id                    INTEGER        PRIMARY KEY NOT NULL,
                estilo        TEXT                       NOT NULL,
                fecha_de_uso    TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        con.commit()
    
    def __insertar_datos_por_defecto(self,cursor:Cursor,con:Connection) -> None:
        """Inserta datos por defecto, en las tablas recien creadas.
        
        Parametros:
        - cursor (Cursor)
        - con (Connection)
        
        Retorna:
        True/False, en el caso de que sea la primera vez que se abre la aplicacion retornara True, caso contrario False."""
        datos = self.api_restful("estilos","SELECCIONAR")
        #Si no hay datos en la tabla de estilos, se deduce de que es la primera vez que abre la aplicacion.
        if(not len(datos)):
            ruta_fondo_claro = os.path.join(globales.ruta_raiz,"media/fondo_de_imagenes/Fondo_claro.jpg")
            cursor.execute(
                "INSERT INTO imagenes_de_fondo (ruta) VALUES ('"+ruta_fondo_claro+"');"
            )
            con.commit()
            ruta_fondo_oscuro = os.path.join(globales.ruta_raiz,"media/fondo_de_imagenes/Fondo_oscuro.jpg")
            cursor.execute(
                "INSERT INTO imagenes_de_fondo (ruta) VALUES ('"+ruta_fondo_oscuro+"');"
            )
            con.commit()
            cursor.execute(
                """
                INSERT INTO estilos (estilo) VALUES ("Light");
                """
            )
            con.commit()
            cursor.execute(
                """
                INSERT INTO estilos (estilo) VALUES ("Dark");
                """
            )
            con.commit()
            return True
        else:
            return False

    def api_restful(self,nombre_tabla:str,instruccion_sql:str,valores:List[Union[str,int,float]]=[]) -> Union[None,str,list]:
        """Interactua con la base de datos de la aplicacion. Si ocurre algun error a nivel del cliente, se devolvera un mensaje con el error. Si ocurre algun error a nivel de desarrollo, se generara un diagnostico.
        
        Parametros:
        - nombre_tabla (str), entre los valores permitidos estan ["dibujos_usuario","imagenes_de_fondo","estilos"].
        - instruccion_sql (str), entre los valores permitidos estan ["SELECCIONAR","INSERTAR","ACTUALIZAR","ELIMINAR"].
        - valores (str|int|float), son los valores que deseas añadir en la tabla. 
        Si la instruccion_sql es "ACTUALIZAR" o "ELIMINAR" el primer valor se deducira como el valor de una ID y debe de ser de tipo Int.
        
        Retorna:
        - None, si la operacion es exitosa.
        - str, si ocurre un error devolvera el mensaje de error.
        - List[any], una lista con los datos de la base de datos (Si la instruccion SQL fue "SELECCIONAR")."""

        tablas_validas = ['dibujos_usuario','imagenes_de_fondo','estilos']
        instrucciones_sql_validas = ['SELECCIONAR','INSERTAR','ACTUALIZAR','ELIMINAR']
        
        valores_validos = True
        longitud_valores_valida = True
        tipo_id_valido = True

        if nombre_tabla in tablas_validas and instruccion_sql in instrucciones_sql_validas and len(valores):
            if len(valores) == 1:
                id = valores[0]
                if instruccion_sql == 'ELIMINAR' and not isinstance(id,int):
                    tipo_id_valido = False
                elif not instruccion_sql == 'ELIMINAR':
                    if not nombre_tabla in ["dibujos_usuario","imagenes_de_fondo"]:
                        valores_validos = False
            elif len(valores) > 1:
                if len(valores) > 3:
                    longitud_valores_valida = False
                else:
                    for valor in valores[1::]:
                        if not isinstance(valor,str):
                            valores_validos = False
                            break
        else:
            if not instruccion_sql == "SELECCIONAR":
                longitud_valores_valida = False
        
        if nombre_tabla in tablas_validas and instruccion_sql in instrucciones_sql_validas and valores_validos and longitud_valores_valida and tipo_id_valido:
            con = connect(self.ruta_bd)#Conecta a la base de datos
            cursor = con.cursor()
            if instruccion_sql == 'SELECCIONAR':
                if nombre_tabla == 'dibujos_usuario':
                    s = 'SELECT * FROM %r ORDER BY ID ASC'%nombre_tabla
                else:
                    s = 'SELECT * FROM %r ORDER BY fecha_de_uso DESC'%nombre_tabla
                cursor.execute(s)
                datos = []

                def decodificar(dato:any)->any:
                    """Si el dato es de tipo string, lo decodifica y lo devuelve en str. Si no es un tipo String devuelve ese mismo dato"""
                    if(isinstance(dato,str)):
                        try:
                            dato = codecs.decode(dato, 'unicode_escape')
                        except Exception as e:
                            GenerarDiagnostico(self.__class__.__name__,e,"info")
                    return dato
                
                for dato in cursor:
                    dato = list(map(decodificar, dato))
                    datos.append(dato)
                con.close()
                return datos
            elif instruccion_sql == 'INSERTAR':
                mensaje_de_error = 'Uno o más campos estan vacios'
                if nombre_tabla == 'dibujos_usuario':
                    nombre_dibujo, comandos_dibujo = valores
                    if nombre_dibujo is '': mensaje_de_error = "El nombre del dibujo esta vacio."
                    else: mensaje_de_error = "No hay comandos para guardar."
                    s1 = 'INSERT INTO %r(nombre_dibujo,comandos_dibujo)'%nombre_tabla
                    s2 = 'VALUES(%r,%r)' %(nombre_dibujo,comandos_dibujo)
                elif nombre_tabla == "imagenes_de_fondo":
                    ruta = valores[0]
                    if ruta is '': mensaje_de_error = "La ruta esta vacia."
                    s1 = 'INSERT INTO %r(ruta)'%nombre_tabla
                    s2 = 'VALUES(%r)' %ruta
                if '' in valores:
                    con.close()
                    return mensaje_de_error
                else:
                    try:
                        cursor.execute('%s %s'%(s1,s2))
                        con.commit()
                        con.close()
                        return
                    except Exception as e:
                        mensaje_de_error = str(e)
                        con.close()
                        return mensaje_de_error
            elif instruccion_sql == 'ACTUALIZAR':
                id = valores[0]
                mensaje_de_error = 'Uno o más campos estan vacios'
                if nombre_tabla == 'dibujos_usuario':
                    nombre_dibujo, comandos_dibujo = valores[1::]
                    if nombre_dibujo is '': mensaje_de_error = "El nombre del dibujo esta vacio."
                    else: mensaje_de_error = "No hay comandos para guardar."
                    a1 = ('nombre_dibujo',nombre_dibujo,'comandos_dibujo',comandos_dibujo)
                    s2 = '%r=%r, %r=%r' % a1
                elif nombre_tabla == 'imagenes_de_fondo':
                    ruta, fecha_de_uso = valores[1::]
                    if ruta is '': mensaje_de_error = 'La ruta esta vacia.'
                    else: mensaje_de_error = 'La fecha de uso esta vacia.'
                    a1 = ('ruta',ruta,'fecha_de_uso',fecha_de_uso)
                    s2 = '%r=%r,%r=%r' % a1
                else:
                    estilo, fecha_de_uso = valores[1::]
                    if estilo is '': mensaje_de_error = "El estilo esta vacio."
                    else: mensaje_de_error = "La fecha de uso esta vacia."
                    a1 = ('estilo',estilo,'fecha_de_uso',fecha_de_uso)
                    s2 = '%r=%r,%r=%r' % a1
                s1 = 'UPDATE %r SET'%nombre_tabla
                s3 = 'WHERE id = %r'%id
                if '' in valores[1::]:
                    con.close()
                    return mensaje_de_error
                else:
                    try:
                        cursor.execute("%s %s %s"%(s1,s2,s3))
                        con.commit()
                        con.close()
                        return
                    except Exception as e:
                        mensaje_de_error = str(e)
                        con.close()
                        return mensaje_de_error
            else:
                id = valores[0]
                s = 'DELETE FROM %r WHERE id=%r'% (nombre_tabla,id)
                try:
                    cursor.execute(s)
                    con.commit()
                    con.close()
                    return
                except Exception as e:
                    mensaje_de_error = str(e)
                    con.close()
                    return mensaje_de_error
        elif not nombre_tabla in tablas_validas:
            GenerarDiagnostico(self.__class__.__name__,'El nombre de la tabla %s no existe en la BD, las tablas que existen son: %r.'%(nombre_tabla,tablas_validas),'error')
        elif not instruccion_sql in instrucciones_sql_validas:
            GenerarDiagnostico(self.__class__.__name__,'La instruccion SQL %s no es valido, se esperaba uno de los siguientes valores: %r.'%instrucciones_sql_validas,'error')
        elif not valores_validos:
            GenerarDiagnostico(self.__class__.__name__,'Para la instruccion SQL %s se esperaba mas de un valor de tipo String.'%instruccion_sql,'error')
        elif not longitud_valores_valida:
            GenerarDiagnostico(self.__class__.__name__,'Para la instruccion SQL %s se esperaba algun valor o sobrepasaste la cantidad de valores a la cantidad de campos en la tabla %s.'%(instruccion_sql,nombre_tabla),'error')
        else:
            GenerarDiagnostico(self.__class__.__name__,'En la instruccion %s la "id" debe de ser de tipo Int.'%instruccion_sql,'error')

        return "Falla al nivel de la aplicacion, por favor reportar esta falla al desarrollador."