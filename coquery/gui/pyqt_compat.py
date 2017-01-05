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
import warnings

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


class CoqSettings(QtCore.QSettings):
    def value(self, key, default=None):
        if default is None:
            warnings.warn("Settings key '{}' requested without default value".format(key))
        try:
            val = super(CoqSettings, self).value(key, default)
        except Exception as e:
            s = "Exception when requesting setting key '{}': {}".format(key, e)
            print(s)
            warnings.warn(s)
            val = default
        return val

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
    
def get_toplevel_window(name="MainWindow"):
    """
    Retrieves the top-level widget with the given name. By default, retrieve
    the main window.
    """
    for widget in QtGui.qApp.topLevelWidgets():
        if widget.objectName() == "MainWindow":
            return widget
    return None
