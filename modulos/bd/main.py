#BD
from typing import Union, List
from sqlite3 import *

#Librerias propias
from modulos.kivy.otros_widgets.aviso_informativo import AvisoInformativo
from modulos.logging import *

class ConexionBD(object):
    """Realiza la conexion a la base de datos, crea tablas si no existen ya en la base de datos y se accede al Api RestFul de la BD.
    
    Propiedad:
    RUTA_BD = './bd/main.db' (str), ruta de la base de datos.
    """
    RUTA_BD = './bd/main.db'

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
            ConexionBD.__instance.__conectar_a_la_base_de_datos(ConexionBD.__instance)
        return ConexionBD.__instance
    
    def __init__(self):
        """1. Crea una base de datos en la ruta "./bd/main.db", si la BD no esta creado.
        2. Realiza una conexion a la base de datos.
        3. Agrega las tablas necesarias para el aplicativo, en la base de datos si estas no existen.
        4. Se añadiran datos por defecto a las tablas recien creadas.
        """

    def __conectar_a_la_base_de_datos(self, *args) -> None:
        """Agrega las tablas necesarias para el aplicativo, en la base de datos si estas no existen. Si la base de datos ya existe, se generara un mensaje de diagnostico."""
        con = connect(self.RUTA_BD)
        try:
            cursor = con.cursor()
            self.__crear_tablas(cursor,con)
            self.__insertar_datos_por_defecto(cursor,con)
            con.close()
        except Exception as e:
            GenerarDiagnostico("["+self.__class__.__name__+"      ] %s"%e,'info')
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
        - con (Connection)"""
        cursor.execute(
            """
            INSERT INTO imagenes_de_fondo (ruta) VALUES ("media/fondo_de_imagenes/Fondo_claro.jpg");
            """
        )
        con.commit()
        cursor.execute(
            """
            INSERT INTO imagenes_de_fondo (ruta) VALUES ("media/fondo_de_imagenes/Fondo_oscuro.jpg");
            """
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

    def api_restful(self,nombre_tabla:str,instruccion_sql:str,valores:List[Union[str,int,float]]=[]) -> Union[bool,list]:
        """Interactua con la base de datos de la aplicacion. Si ocurre algun error a nivel del cliente, se lanzara una ventana informativa. Si ocurre algun error a nivel de desarrollo, se generara un diagnostico.
        
        Parametros:
        - nombre_tabla (str), entre los valores permitidos estan ["dibujos_usuario","imagenes_de_fondo","estilos"].
        - instruccion_sql (str), entre los valores permitidos estan ["SELECCIONAR","INSERTAR","ACTUALIZAR","ELIMINAR"].
        - valores (str|int|float), son los valores que deseas añadir en la tabla. 
        Si la instruccion_sql es "ACTUALIZAR" o "ELIMINAR" el primer valor se deducira como el valor de una ID y debe de ser de tipo Int.
        
        Retorna:
        - True/False, si la operacion es exitosa o no.
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
            con = connect(self.RUTA_BD)#Conecta a la base de datos
            cursor = con.cursor()
            if instruccion_sql == 'SELECCIONAR':
                if nombre_tabla == 'dibujos_usuario':
                    s = 'SELECT * FROM %s ORDER BY ID ASC'%nombre_tabla
                else:
                    s = 'SELECT * FROM %s ORDER BY fecha_de_uso DESC'%nombre_tabla
                cursor.execute(s)
                datos = []
                for i in cursor:
                    datos.append(i)
                con.close()
                return datos
            elif instruccion_sql == 'INSERTAR':
                if nombre_tabla == 'dibujos_usuario':
                    nombre_dibujo, comandos_dibujo = valores
                    s1 = 'INSERT INTO %s(nombre_dibujo,comandos_dibujo)'%nombre_tabla
                    s2 = 'VALUES("%s","%s")' %(nombre_dibujo,comandos_dibujo)
                elif nombre_tabla == "imagenes_de_fondo":
                    ruta = valores[0]
                    s1 = 'INSERT INTO %s(ruta)'%nombre_tabla
                    s2 = 'VALUES("%s")' %ruta
                try:
                    cursor.execute('%s %s'%(s1,s2))
                    con.commit()
                    con.close()
                    return True
                except Exception as e:
                    titulo = 'Error en la creacion de este dato.'
                    if '' in valores:
                        mensaje = 'Uno o más campos estan vacios'
                    else:
                        mensaje = str(e)
                    AvisoInformativo(titulo=titulo,mensage=mensaje)
                    con.close()
                    return False
            elif instruccion_sql == 'ACTUALIZAR':
                id = valores[0]
                if nombre_tabla == 'dibujos_usuario':
                    nombre_dibujo, comandos_dibujo = valores[1::]
                    a1 = ('nombre_dibujo',nombre_dibujo,'comandos_dibujo',comandos_dibujo)
                    s2 = '"%s"="%s", "%s"="%s"' % a1
                elif nombre_tabla == 'imagenes_de_fondo':
                    ruta, fecha_de_uso = valores[1::]
                    a1 = ('ruta',ruta,'fecha_de_uso',fecha_de_uso)
                    s2 = '"%s"="%s","%s"="%s"' % a1
                else:
                    estilo, fecha_de_uso = valores[1::]
                    a1 = ('estilo',estilo,'fecha_de_uso',fecha_de_uso)
                    s2 = '"%s"="%s","%s"="%s"' % a1
                s1 = 'UPDATE %s SET'%nombre_tabla
                s3 = 'WHERE id = %s'%id
                try:
                    cursor.execute("%s %s %s"%(s1,s2,s3))
                    con.commit()
                    con.close()
                    return True
                except Exception as e:
                    titulo = 'Error al actualizar este dato.'
                    if '' in valores[1::]:
                        mensaje = 'El campo esta vacio.'
                    else:
                        mensaje = str(e)
                    AvisoInformativo(titulo=titulo,mensage=mensaje)
                    con.close()
                    return False
            else:
                id = valores[0]
                s = 'DELETE FROM %s WHERE id=%s'% (nombre_tabla,id)
                try:
                    cursor.execute(s)
                    con.commit()
                    con.close()
                    return True
                except Exception as e:
                    titulo = 'Error en la eliminacion de este dato.'
                    mensaje = str(e)
                    AvisoInformativo(titulo=titulo,mensage=mensaje)
                    con.close()
                    return False
        elif not nombre_tabla in tablas_validas:
            GenerarDiagnostico('El nombre de la tabla %s no existe en la BD, las tablas que existen son: %r.'%(nombre_tabla,tablas_validas),'error')
        elif not instruccion_sql in instrucciones_sql_validas:
            GenerarDiagnostico('La instruccion SQL %s no es valido, se esperaba uno de los siguientes valores: %r.'%instrucciones_sql_validas,'error')
        elif not valores_validos:
            GenerarDiagnostico('Para la instruccion SQL %s se esperaba mas de un valor de tipo String.'%instruccion_sql,'error')
        elif not longitud_valores_valida:
            GenerarDiagnostico('Para la instruccion SQL %s se esperaba algun valor o sobrepasaste la cantidad de valores a la cantidad de campos en la tabla %s.'%(instruccion_sql,nombre_tabla),'error')
        else:
            GenerarDiagnostico('En la instruccion %s la "id" debe de ser de tipo Int.'%instruccion_sql,'error')

        return False