from functools import partial

from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton

class LanzarMDDialog():
    def lanzar_error_pytikz(self,error):
        btn_salir = MDRaisedButton(text="Ok", text_color=[0,0,0,1])
        md_dialog = MDDialog(
            title="Ocurrio un error al compilar el codigo Tikz",
            text=error,
            radius=[20, 7, 20, 7],
            buttons=[
                btn_salir
            ]
        )
        btn_salir.bind(on_press=partial(self.__cerrar_md_dialog,md_dialog))
        md_dialog.open()

    def __cerrar_md_dialog(self,md_dialog,*args):
        md_dialog.dismiss()