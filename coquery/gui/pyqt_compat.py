# -*- coding: utf-8 -*-
"""
pyqt_compat.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import sys

pyside = False
pyqt = False

try:
    import PySide.QtCore as QtCore
    import PySide.QtGui as QtGui
    import PySide.QtHelp as QtHelp
    pyside = True
except ImportError:
    try:
        import sip
        sip.setapi('QVariant', 2)        
        import PyQt4.QtCore as QtCore
        import PyQt4.QtGui as QtGui
        import PyQt4.QtHelp as QtHelp
        pyqt = True
    except ImportError:
        raise ImportError('Neither PyQt4 nor PySide available')

if pyqt:
    QtCore.Signal = QtCore.pyqtSignal
    QtCore.Slot = QtCore.pyqtSlot
    QtCore.Property = QtCore.pyqtProperty
    QtCore.QString = str
else:
    QtCore.pyqtSignal = QtCore.Signal
    QtCore.pyqtSlot = QtCore.Slot
    QtCore.pyqtProperty = QtCore.Property
    QtCore.QVariant = lambda x: x   
    QtCore.QString = str
    if "setMargin" not in dir(QtGui.QHBoxLayout):
        QtGui.QHBoxLayout.setMargin = lambda x, y: True
    if "setMargin" not in dir(QtGui.QVBoxLayout):
        QtGui.QVBoxLayout.setMargin = lambda x, y: True
    if "setMargin" not in dir(QtGui.QGridLayout):
        QtGui.QGridLayout.setMargin = lambda x, y: True


def QWebView(*args, **kwargs):
    if pyside:
        import PySide.QtWebKit as QtWebKit
    elif pyqt:
        import PyQt4.QtWebKit as QtWebKit
    return QtWebKit.QWebView(*args, **kwargs)
        
if sys.platform == 'win32':
    frameShadow = QtGui.QFrame.Raised
    frameShape = QtGui.QFrame.Panel
else:
    frameShadow = QtGui.QFrame.Raised
    frameShape = QtGui.QFrame.StyledPanel
    
    