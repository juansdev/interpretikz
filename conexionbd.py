import pytz
from functools import partial
from datetime import datetime
#DB
import sqlite3

#KIVY
import kivy
from kivy.app import App
from kivy.lang.builder import Builder
#KIVY UIX
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup

class MensajePopup(Popup):
    pass

class ConexionBD():
    def __init__(self):
        #Obtiene la ruta actual de este archivo
        self.DB_PATH = "./db/main.db"

        #Conexion a la base de datos
        self.__connect_to_database(self.DB_PATH)
    
    #Conexion a la base de datos
    def __connect_to_database(self,path):
        con = sqlite3.connect(path)#Intentara conectar a la base de datos y si no existe lo creara.
        try:
            cursor = con.cursor()
            self.__crear_tablas(cursor,con)
            self.__insertar_datos_por_defecto(cursor,con)
            con.close()#Cerrar la conexion de BD
        except Exception as e:
            print(e)
        con.close()

    #Creacion de tablas
    def __crear_tablas(self,cursor,con):
        cursor.execute(
            """
            CREATE TABLE dibujos_usuario(
                id                    INTEGER        PRIMARY KEY NOT NULL,
                nombre_dibujo        TEXT                       NOT NULL,
                comandos_dibujo     TEXT                       NOT NULL
            )
            """
        )
        con.commit()#Guardar cambios en la BD
        cursor.execute(
            """
            CREATE TABLE imagenes_de_fondo(
                id                    INTEGER        PRIMARY KEY NOT NULL,
                ruta        TEXT                       NOT NULL,
                fecha_de_uso    TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        con.commit()#Guardar cambios en la BD
        cursor.execute(
            """
            CREATE TABLE estilos(
                id                    INTEGER        PRIMARY KEY NOT NULL,
                estilo        TEXT                       NOT NULL,
                fecha_de_uso    TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        con.commit()#Guardar cambios en la BD
    #Insertar datos por defecto en tablas
    def __insertar_datos_por_defecto(self,cursor,con):
        cursor.execute(
            """
            INSERT INTO imagenes_de_fondo (ruta) VALUES ("media/fondo_de_imagenes/Mobil.jpg");
            """
        )
        con.commit()#Guardar cambios en la BD
        cursor.execute(
            """
            INSERT INTO imagenes_de_fondo (ruta) VALUES ("media/fondo_de_imagenes/PC.jpg");
            """
        )
        con.commit()#Guardar cambios en la BD
        cursor.execute(
            """
            INSERT INTO estilos (estilo) VALUES ("Light");
            """
        )
        con.commit()#Guardar cambios en la BD
        cursor.execute(
            """
            INSERT INTO estilos (estilo) VALUES ("Dark");
            """
        )
        con.commit()#Guardar cambios en la BD

    def api_restful(self,instruccion_sql,nombre_tabla,array_valores=[]):
        instrucciones_sql_validas = ["SELECCIONAR","INSERTAR","ACTUALIZAR","ELIMINAR"]
        tablas_validas = ["dibujos_usuario","imagenes_de_fondo","estilos"]
        valores_validos = True
        longitud_valores_valida = True
        tipo_id_valido = True

        #Todo valor debe ser de tipo STRING, a excepcion del ID que debe de ser INT
        if len(array_valores) > 0:
            if len(array_valores) > 1:
                for valor in array_valores[1::]:
                    if not isinstance(valor,str):
                        return False
            if instruccion_sql == "ACTUALIZAR" and not isinstance(array_valores[0],int):
                tipo_id_valido = False
        
        #La cantidad de valores a insertar debe de coincidir con el numero de columnas de la tabla en cuestion
        if nombre_tabla == "dibujos_usuario" or nombre_tabla == "imagenes_de_fondo" or nombre_tabla == "estilos":
            if len(array_valores) > 3:
                longitud_valores_valida = False
        
        if instruccion_sql in instrucciones_sql_validas and valores_validos and nombre_tabla in tablas_validas and longitud_valores_valida and tipo_id_valido:
            con = sqlite3.connect(self.DB_PATH)#Conecta a la base de datos
            cursor = con.cursor()
            if instruccion_sql == "SELECCIONAR":
                if nombre_tabla == "dibujos_usuario":
                    s = "SELECT * FROM "+nombre_tabla+" ORDER BY ID ASC"
                else:
                    s = "SELECT * FROM "+nombre_tabla+" ORDER BY fecha_de_uso DESC"
                cursor.execute(s)
                datos = []
                for i in cursor:
                    datos.append(i)
                return datos
            elif instruccion_sql == "INSERTAR":
                a1 = tuple(array_valores)
                if nombre_tabla == "dibujos_usuario":
                    s1 = "INSERT INTO "+nombre_tabla+"(nombre_dibujo,comandos_dibujo)"
                    s2 = 'VALUES("%s","%s")' % a1
                elif nombre_tabla == "imagenes_de_fondo":
                    s1 = "INSERT INTO "+nombre_tabla+"(ruta)"
                    s2 = 'VALUES("%s")' % a1
                try:
                    cursor.execute(s1+" "+s2)
                    con.commit()
                    con.close()
                    return True
                except Exception as e:
                    popup = MensajePopup()
                    mensaje = popup.ids.mensaje
                    popup.open()
                    popup.title = "Error en la creacion de este dato."
                    if '' in a1:
                        mensaje.text = "Uno o más campos estan vacios"
                    else:
                        mensaje.text = str(e)
                print(s1+" "+s2+" "+s3)
            elif instruccion_sql == "ACTUALIZAR":
                if nombre_tabla == "dibujos_usuario":
                    a1 = ("nombre_dibujo",array_valores[1],"comandos_dibujo",array_valores[2])
                    s2 = '"%s"="%s", "%s"="%s"' % a1
                elif nombre_tabla == "imagenes_de_fondo":
                    a1 = ("ruta",array_valores[1],"fecha_de_uso",array_valores[2])
                    s2 = '"%s"="%s","%s"="%s"' % a1
                elif nombre_tabla == "estilos":
                    a1 = ("estilo",array_valores[1],"fecha_de_uso",array_valores[2])
                    s2 = '"%s"="%s","%s"="%s"' % a1
                s1 = "UPDATE "+nombre_tabla+" SET"
                s3 = 'WHERE id = %s' % array_valores[0]
                try:
                    cursor.execute(s1+" "+s2+" "+s3)
                    con.commit()
                    con.close()
                    return True
                except Exception as e:
                    popup = MensajePopup()
                    mensaje = popup.ids.mensaje
                    popup.open()
                    popup.title = "Error al actualizar este dato."
                    if '' in a1:
                        mensaje.text = "El campo esta vacio."
                    else:
                        mensaje.text = str(e)
                print(s1+" "+s2+" "+s3)
                con.close()
            elif instruccion_sql == "ELIMINAR":
                s = "DELETE FROM "+nombre_tabla+" WHERE id=%s" % array_valores[0]
                try:
                    cursor.execute(s)
                    con.commit()
                    con.close()
                    return True
                except Exception as e:
                    popup = MensajePopup()
                    mensaje = popup.ids.mensaje
                    popup.open()
                    popup.title = "Error en la eliminacion de este dato."
                    mensaje.text = str(e)
                print(s1+" "+s2+" "+s3)
                con.close()
        elif not valores_validos:
            print("ERROR DESARROLLADOR, EL VALOR A INSERTAR CORRESPONDE A UN TIPO DIFERENTE A STRING.")
        elif not nombre_tabla in tablas_validas:
            print("ERROR DESARROLLADOR, EL NOMBRE DE LA TABLA NO EXISTE EN LA BD.")
        elif not longitud_valores_valida:
            print("ERROR DESARROLLADOR LA CANTIDAD DE VALORES A INGRESAR SUPERA EL NUMERO DE COLUMNAS DE LA TABLA")
        elif not tipo_id_valido:
            print("ERROR DESARROLLADOR EL TIPO DE VALOR DE LA ID DEBE DE SER INT")
        elif not instruccion_sql in instrucciones_sql_validas:
            print("ERROR DESARROLLADOR INSTRUCCION "+instruccion_sql+" NO EXISTE.")
        else:
            print("ERROR EN LA BD")

        return False #Se produjo un error.

class MainApp(App):
    def __init__(self,**kwargs):
        super(MainApp, self).__init__(**kwargs)
        self.conexionBd = ConexionBD()
    def eliminarDato(self,nombre_tabla,id,instance):
        arr_datos = [id]
        self.conexionBd.api_restful("ELIMINAR",nombre_tabla,arr_datos)
    def insertarDato(self,nombre_tabla,instance):
        # arr_datos = ["test","TESTEANDO"]
        arr_datos = ["test"]
        self.conexionBd.api_restful("INSERTAR",nombre_tabla,arr_datos)
    def seleccionarDatos(self,nombre_tabla,instance):
        datos = self.conexionBd.api_restful("SELECCIONAR",nombre_tabla)
        print(datos)
    def actualizarDatos(self,nombre_tabla,id,instance):
        # arr_datos = [id,"ACTUALIZADO","TESTEANDO"]
        utc_ahora = datetime.utcnow().replace(tzinfo=pytz.utc)
        utc_formateado = datetime.strftime(utc_ahora,"%Y-%m-%d %H:%M:%S")
        arr_datos = [id,"media/fondo_de_imagenes/Mobil.jpg",utc_formateado]
        self.conexionBd.api_restful("ACTUALIZAR",nombre_tabla,arr_datos)
    def build(self):
        Builder.load_file("kivy/mensaje_popup.kv")
        nombre_tabla = "imagenes_de_fondo"
        btn = Button(text="GENERAR DATO EN BD")
        btn.bind(on_press=partial(self.seleccionarDatos,nombre_tabla))
        # btn.bind(on_press=partial(self.insertarDato,nombre_tabla))
        # btn.bind(on_press=partial(self.actualizarDatos,nombre_tabla,1))
        # btn.bind(on_press=partial(self.eliminarDato,nombre_tabla,1))
        wid = Widget()
        wid.add_widget(btn)
        return wid

if __name__ == "__main__":
    MainApp().run()