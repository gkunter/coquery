# -*- coding: utf-8 -*-

from pyqt_compat import QtCore, QtGui

class CoqStopWord(QtGui.QListWidgetItem):
    def __init__(self, *args):
        super(CoqStopWord, self).__init__(*args)
        #icon = QtGui.qApp.style().standardIcon(QtGui.QStyle.SP_DockWidgetCloseButton)
        #self.setIcon(icon)
        brush = QtGui.QBrush(QtGui.QColor("lightcyan"))
        self.setBackground(brush)
        
class CoqStopwordDelegate(QtGui.QStyledItemDelegate):
    def __init__(self, parent=None, *args):
        super(CoqStopwordDelegate, self).__init__(parent, *args)

    def paint(self, painter, option, index):
        painter.save()

        painter.drawPixmap(0, 0, 
                QtGui.qApp.style().standardPixmap(QtGui.QStyle.SP_DockWidgetCloseButton))
        # set background color
        painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        if option.state & QtGui.QStyle.State_Selected:
            painter.setBrush(QtGui.QBrush(QtCore.Qt.red))
        else:
            painter.setBrush(QtGui.QBrush(QtGui.QColor("lightcyan")))
        painter.drawRect(option.rect)

        # set text color
        painter.setPen(QtGui.QPen(QtCore.Qt.black))
        value = index.data(QtCore.Qt.DisplayRole)
        painter.drawText(option.rect, QtCore.Qt.AlignLeft, value)
        

        painter.restore()

        
class CoqAddWord(CoqStopWord):
    def __init__(self, *args):
        super(CoqStopWord, self).__init__(*args)
        self.reset()
    
    def reset(self):
        self.setText("Add...")
        
class CoqStopwordList(QtGui.QListWidget):
    def __init__(self, *args):
        super(CoqStopwordList, self).__init__(*args)
        
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.setFlow(QtGui.QListView.TopToBottom)
        self.setProperty("isWrapping", True)
        self.setMovement(QtGui.QListView.Static)
        self.setResizeMode(QtGui.QListView.Adjust)
        self.setSpacing(10)
        self.setFlow(QtGui.QListView.LeftToRight)
        self.setViewMode(QtGui.QListView.IconMode)
        self.setWordWrap(True)
        self.setSelectionRectVisible(True)

        self.itemClicked.connect(self.onClick)
        self.add_item = None
 
        self.setItemDelegate(CoqStopwordDelegate(parent=self))
 
    def onClick(self, item):
        if item == self.add_item:
            #self.add_item.setText("")
            self.openPersistentEditor(self.add_item)
            print("editing")
            self.itemChanged.connect(self.onChange)
            
    def onChange(self, item):
        if item == self.add_item:
            print("change")
            self.itemChanged.disconnect(self.onChange)
            self.closePersistentEditor(self.add_item)
            words = str(self.add_item.text()).split()
            for x in words:
                self.insertItem(self.count() - 1, CoqStopWord(x))
            self.add_item.reset()

    def addAddItem(self, item, *args):
        super(CoqStopwordList, self).addItem(item, *args)
        self.add_item = item
        