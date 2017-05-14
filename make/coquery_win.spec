# -*- mode: python -*-

import os
import sys
import glob

sys.setrecursionlimit(10000)

block_cipher = None

VERSION = os.getenv("COQ_VERSION")

coq_path = os.path.realpath(os.path.join(os.getenv("HOMEPATH"), "coquery-{}".format(VERSION), "coquery"))
python_path = os.path.split(sys.executable)[0]

binaries = []
l = []
data = []


if sys.platform == "win32":
    binaries = []

    # This site recommends to include two C++ runtime dlls with the installer
    # https://shanetully.com/2013/08/cross-platform-deployment-of-python-applications-with-pyinstaller/

    dll_path = os.path.join(python_path, "Lib", "site-packages", "numpy", "core", "*.dll")
    for file in glob.glob(dll_path):
        if "mkl_" in file or "libiomp5md.dll" in file:
            binaries.append((file, "."))

for file in glob.glob(os.path.join(coq_path, "icons", "small-n-flat", "PNG")):
    data.append((file, os.path.join("icons", "small-n-flat", "PNG")))
for file in glob.glob(os.path.join(coq_path, "icons", "Icons8", "PNG")):
    data.append((file, os.path.join("icons", "Icons8", "PNG")))
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
             binaries=binaries,
             datas=data + l,
             hiddenimports=['transpose'] + [os.path.splitext(os.path.basename(x))[0] for x, _ in l],
             hookspath=["."],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

if False and sys.platform == "win32":
    exe = EXE(pyz,
              a.scripts,
              exclude_binaries=True,
              name='Coquery',
              debug=False,
              strip=False,
              upx=True,
              icon=os.path.join(coq_path, 'icons', 'artwork', 'coquery.ico'),
              console=False )
else:
    exe = EXE(pyz,
              a.scripts,
              exclude_binaries=True,
              name='Coquery',
              debug=False,
              strip=False,
              upx=True,
              console=False )


coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='Coquery')

if sys.platform == "darwin":
    app = BUNDLE(exe,
                 name='Coquery.app',
                 icon=os.path.join(coq_path, "icons", "artwork", "coquery.icns"))


# a.binaries = [x for x in a.binaries if not x[0].startswith("scipy")]

# a.binaries = [x for x in a.binaries if not x[0].startswith("IPython")]

# a.binaries = [x for x in a.binaries if not x[0].startswith("zmq")]

# a.binaries = a.binaries - TOC([
#  ('tcl85.dll', None, None),
#  ('tk85.dll', None, None),
#  ('_ssl', None, None),
#  ('_tkinter', None, None)])

