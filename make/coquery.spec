# -*- mode: python -*-

import glob
import os.path
import sys

sys.exit(1)

base_path = "C:\\Users\\dadasd\\coquery\\make"
coq_path = "C:\\Users\\dadasd\\coquery\\coquery"

block_cipher = None

binaries = []
l = []
data = []

for file in glob.glob("C:\\Users\\dadasd\\WinPython-32bit-3.4.3.7Slim\\python-3.4.3\\Lib\\site-packages\\numpy\\core\\*.dll"):
	if "mkl_" in file or "libiomp5md.dll" in file:
		binaries.append((file, "."))

for file in glob.glob(os.path.join(coq_path, "icons", "small-n-flat", "PNG")):
	data.append((file, os.path.join("icons", "small-n-flat", "PNG")))
for file in glob.glob(os.path.join(coq_path, "icons", "artwork")):
	data.append((file, os.path.join("icons", "artwork")))

for file in glob.glob(os.path.join(coq_path, "texts")):
	data.append((file, os.path.join("texts")))
for file in glob.glob(os.path.join(coq_path, "help")):
    data.append((file, os.path.join("help")))
for file in glob.glob(os.path.join(coq_path, "stopwords")):
    data.append((file, os.path.join("stopwords")))

for file in glob.glob(os.path.join(coq_path, "installer", "coq_install_*.py")):
	l.append((file, "installer"))
for file in glob.glob(os.path.join(coq_path, 'visualizer', '*.py')):
	l.append((file, "visualizer"))

a = Analysis([os.path.join('..', 'Coquery.py')],
             pathex=[coq_path,
                 os.path.join(coq_path, "visualizer"),
                 os.path.join(coq_path, "installer")],
             binaries=None,
             datas=data + l,
             hiddenimports=['transpose'] + [os.path.splitext(os.path.basename(x))[0] for x, _ in l],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='Coquery',
          debug=False,
          strip=False,
          upx=True,
          icon=os.path.join(coq_path, 'icons', 'artwork', 'logo.ico'),
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='Coquery')

               
# a.binaries = [x for x in a.binaries if not x[0].startswith("scipy")]

# a.binaries = [x for x in a.binaries if not x[0].startswith("IPython")]

# a.binaries = [x for x in a.binaries if not x[0].startswith("zmq")]

# a.binaries = a.binaries - TOC([
#  ('tcl85.dll', None, None),
#  ('tk85.dll', None, None),
#  ('_ssl', None, None),
#  ('_tkinter', None, None)])
