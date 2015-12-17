
from pyqt_compat import QtGui, QtCore
 
class FlowLayout(QtGui.QLayout):
    """ Define a QLayout with flowing widgets that reorder automatically. """
 
    def __init__(self, parent=None, margin=0, spacing=-1):
        super(FlowLayout, self).__init__(parent)
        try:
            self.setMargin(margin)
        except AttributeError:
            pass
        self.setSpacing(spacing)
        self.itemList = []
 
    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)
 
    def clear(self):
        for tag in [x.widget() for x in self.itemList]:
            tag.removeRequested()
 
    def addItem(self, item):
        self.itemList.append(item)
        self.update()

    def count(self):
        return len(self.itemList)
 
    def itemAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList[index]
        return None
 
    def takeAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList.pop(index)
        return None
 
    def insertWidget(self, index, widget):
        """ Insert a widget at a specific position. """
        
        # first, add the widget, and then move its position to
        # the specified index:
        self.addWidget(widget)
        self.itemList.insert(index, self.itemList.pop(-1))
            
    def findWidget(self, widget):
        """ Return the index number of the widget, or -1 if the widget is not
        in the layout. """
        try:
            return [x.widget() for x in self.itemList].index(widget)
        except ValueError:
            return -1
    
    def expandingDirections(self):
        return QtCore.Qt.Orientations(QtCore.Qt.Horizontal)
 
    def hasHeightForWidth(self):
        return True
 
    def heightForWidth(self, width):
        height = self.doLayout(QtCore.QRect(0, 0, width, 0), True)
        return height
 
    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)
 
    def sizeHint(self):
        return self.minimumSize()
 
    def minimumSize(self):
        size = QtCore.QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
        size += QtCore.QSize(2 * self.margin(), 2 * self.margin())
        return size
 
    def margin(self):
        return 0
 
    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0
 
        for item in self.itemList:
            wid = item.widget()
            spaceX = self.spacing()
            spaceY = self.spacing()
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0
 
            if not testOnly:
                item.setGeometry(QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))
 
            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())
 
        return y + lineHeight - rect.y()