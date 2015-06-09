pyside = False
pyqt = False

try:
    import PySide.QtCore as QtCore
    import PySide.QtGui as QtGui
    pyside = True
except ImportError:
    try:
        import PyQt4.QtCore as QtCore
        import PyQt4.QtGui as QtGui
        pyqt = True
    except ImportError:
        raise ImportError('Neither PyQt4 nor PySide available')

if pyqt:
    print("Using PyQt.")
    QtCore.Signal = QtCore.pyqtSignal
    QtCore.Slot = QtCore.pyqtSlot
    QtCore.Property = QtCore.pyqtProperty
else:
    
    print("Using PySide.")
    QtCore.pyqtSignal = QtCore.Signal
    QtCore.pyqtSlot = QtCore.Slot
    QtCore.pyqtProperty = QtCore.Property
    QtCore.QVariant = lambda x: x   
    if "setMargin" not in dir(QtGui.QHBoxLayout):
        QtGui.QHBoxLayout.setMargin = lambda x, y: True
    if "setMargin" not in dir(QtGui.QVBoxLayout):
        QtGui.QVBoxLayout.setMargin = lambda x, y: True
    if "setMargin" not in dir(QtGui.QGridLayout):
        QtGui.QGridLayout.setMargin = lambda x, y: True
