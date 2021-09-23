# -*- mode: python -*-

"""
    En primer lugar, asegúrese de importar lo que necesite para su aplicación.
"""

import os, sys

from kivy import kivy_data_dir
from kivy.deps import sdl2, glew
from kivy.tools.packaging import pyinstaller_hooks as hooks

""" 
   A continuación, asegúrese de tener todas las dependencias de kivys
"""

block_cipher = None
kivy_deps_all = hooks.get_deps_all()
kivy_factory_modules = hooks.get_factory_modules()

"""
    Luego, incluya los archivos que pueda necesitar para su aplicación
"""

datas = [
    ('bd', 'bd'),
    ('globales', 'globales'),
    ('kivy', 'kivy'),
    ('media', 'media'),
    ('modulos', 'modulos'),
    ('pytikzgenerate', 'pytikzgenerate')
]

# Lista de modulos para excluir del analisis
excludes_a = ['docutils', 'pygments']

# Lista de hiddenimports
hiddenimports = kivy_deps_all['hiddenimports'] + kivy_factory_modules

# Datos binarios
sdl2_bin_tocs = [Tree(p) for p in sdl2.dep_bins]
glew_bin_tocs = [Tree(p) for p in glew.dep_bins]
bin_tocs = sdl2_bin_tocs + glew_bin_tocs

# Assets
kivy_assets_toc = Tree(kivy_data_dir, prefix=os.path.join('kivy_install', 'data'))
assets_toc = [kivy_assets_toc]

tocs = bin_tocs + assets_toc

a = Analysis(['main.py'],
             pathex=[os.getcwd()],
             binaries=None,
             datas=datas,
             hiddenimports=hiddenimports,
             hookspath=[],
             runtime_hooks=[],
             excludes=excludes_a,
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)


pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

"""
    Put your *tocs underneath the a.data (this would go under the collect if 
    we wanted the app to be a dir and not a onefile)
"""

def resourcePath(file):
    if(hasattr(sys, '_MEIPASS')):
        return os.path.join(sys._MEIPASS,file)
    return os.path.join(os.path.abspath('.'),file)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          *tocs,
          name='Interpretikz',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True,
          icon=resourcePath("media\\favicon.ico"))

coll = COLLECT(exe,
   a.binaries,
   a.zipfiles,
   a.datas,
   *tocs,
   strip=False,
   upx=True,
   name='Interpretikz')