# -*- mode: python -*-

import os
import sys
import glob


block_cipher = None

coq_path = os.path.expanduser(os.path.join("~", "coquery", "coquery"))

data = []
l = []

for file in glob.glob(os.path.join(coq_path, "icons", "small-n-flat", "PNG")):
	data.append((file, os.path.join("icons", "small-n-flat", "PNG")))
for file in glob.glob(os.path.join(coq_path, "icons", "artwork")):
	data.append((file, os.path.join("icons", "artwork")))
for file in glob.glob(os.path.join(coq_path, "icons", "Icons8", "PNG")):
    data.append((file, os.path.join("icons", "Icons8", "PNG")))

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
