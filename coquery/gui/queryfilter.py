# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from pyqt_compat import QtCore, QtGui
from flowlayout import FlowLayout
import random
import sys

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

class CoqTextTag(QtGui.QFrame):
    """ Define a QFrame that functions as a text tag. """

    def __init__(self, *args):
        super(CoqTextTag, self).__init__(*args)
        self.setupUi()
        self.close_button.clicked.connect(self.removeRequested)

    def setText(self, *args):
        self.label.setText(*args)

    def text(self, *args):
        return self.label.text(*args)

    def setupUi(self):
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.horizontalLayout = QtGui.QHBoxLayout(self)
        self.horizontalLayout.setContentsMargins(2, 1, 2, 1)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(self)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setLineWidth(0)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.close_button = QtGui.QPushButton(self)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.close_button.sizePolicy().hasHeightForWidth())
        self.close_button.setSizePolicy(sizePolicy)
        self.close_button.setFlat(True)
        self.close_button.setObjectName(_fromUtf8("close_button"))
        self.horizontalLayout.addWidget(self.close_button)

        icon = QtGui.qApp.style().standardIcon(QtGui.QStyle.SP_DockWidgetCloseButton)
        
        height = self.fontMetrics().height()
        new_height = int(height * 0.75)
        self._style_font = "font-size: {}px".format(new_height)
        self._style_border_radius = "border-radius: {}px".format(int(new_height / 3))
        self.setBackground("rgb(255, 255, 192)")
        self.close_button.setIcon(icon)
        self.close_button.setIconSize(QtCore.QSize(new_height, new_height))
        self.adjustSize()

    def setBackground(self, color):
        self._style_background = "background-color: {}".format(color)
        s = " ".join(["{};".format(x) for x in [self._style_background, self._style_border_radius, self._style_font]])
        print(s)
        self.setStyleSheet(s)

    def content(self):
        return self.text()
    
    def setContent(self, text):
        """ Set the content of the tag to text. Validate the content, and set 
        the tag background accordingly. """
        self.setText(self.format_content(text))

    @staticmethod
    def format_content(text):
        """ Return the text string as it appears on the tag. """
        return text
    
    def mouseMoveEvent(self, e):
        """ Define a mouse event that allows dragging of the tag by pressing
        and holding the left mouse button on it. """
        if e.buttons() != QtCore.Qt.LeftButton:
            return

        mimeData = QtCore.QMimeData()
        mimeData.setText(self.content())
        
        pixmap = QtGui.QPixmap.grabWidget(self)
        
        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        drag.setPixmap(pixmap)
        drag.setHotSpot(e.pos())

        self.parent().dragTag(drag, self)

    def removeRequested(self):
        self.parent().destroyTag(self)

    def validate(self):
        """ Validate the content, and return True if the content is valid,
        or False otherwise. """
        return True
    
class CoqFilterTag(CoqTextTag):
    """ Defines a CoqTextTag class that acts as a query filter tag. """

    operators = (">", "<", "IN", "IS", "=", "LIKE")
    valid_variables = []
    
    @staticmethod
    def setValidVariables(variableList):
        CoqFilterTag.valid_variables = variableList
    
    def setContent(self, text):
        super(CoqFilterTag, self).setContent(text)
        if self.validate():
            self.setBackground("rgb(207, 236, 255)")
        else:
            self.setBackground("rgb(255, 192, 192)")

    def __init__(self, *args):
        super(CoqFilterTag, self).__init__(*args)

    @staticmethod
    def format_content(text):
        text = str(text)
        var, op, value_list, value_range = CoqFilterTag.parse_tag(text.strip())
        if value_list:
            return "{} {} {}".format(var.capitalize(), op.lower(), ", ".join(sorted(value_list)))
        elif value_range:
            return "{} {} {}-{}".format(var.capitalize(), op.lower(), min(value_range), max(value_range))
        else:
            return text.strip()
        
    @staticmethod
    def parse_tag(text):
        """ Parse the text and return a tuple with the query filter 
        components.  The tuple contains the components (in order) variable, 
        operator, value_list, value_range.
        
        The component value_list is a list of all specified values. The 
        componment value_range is a tuple with the lower and the upper limit
        of the range specified in the text. Only one of the two components 
        value_list and value_range contains valid values, the other is None.
        
        If the text is not a valid filter text, the tuple None, None, None, 
        None is returned."""
        
        error_value = None, None, None, None
        
        text = text.replace("=", " = ")
        text = text.replace("<", " < ")
        text = text.replace(">", " > ")
        
        fields = str(text).split()
        try:
            var = fields[0]
        except:
            return error_value
        try:
            operator = fields[1]
        except:
            return error_value            
        try:
            values = fields[2:]
        except:
            return error_value
        
        if not values:
            return error_value
        
        # check for range:
        collapsed_values = "".join(fields[2:])
        if collapsed_values.count("-") == 1:
            value_list = None
            value_range = tuple(collapsed_values.split("-"))
        else:
            value_range = None
            value_list = sorted([x.strip("(),").strip() for x in values])

        if (value_range or len(value_list) > 1) and operator.lower() in ("is", "="):
            operator = "in"

        return var, operator, value_list, value_range
        
    def validate(self):
        """ Check if the text contains a valid filter. A filter is valid if
        it has the form 'x OP y', where x is a resource variable name, OP is
        a comparison operator, and value is either a string, a number or a 
        list. """
        var, op, value_range, value_list = self.parse_tag(self.text())
        self.parse_tag(self.text())
        if not var:
            return False
        if self.valid_variables:
            if var.lower() not in [x.lower() for x in self.valid_variables]:
                return False
        if op.lower() not in [x.lower() for x in self.operators]:
            return False
        return True
    
class CoqTagEdit(QtGui.QLineEdit):
    """ Define a QLineEdit class that is used to enter query filters. """

    filter_examples = ["Year > 1999", "Gender is m", "Genre in MAG, NEWS", 
                       "Year in 2005-2010", "Year = 2012", "File is b0*"]

    def __init__(self, *args):
        super(CoqTagEdit, self).__init__(*args)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        #self.setStyleSheet(_fromUtf8('CoqTagEdit { border-radius: 5px; font: condensed; }'))
        self.setObjectName(_fromUtf8("edit_source_filter"))
        self.setPlaceholderText("e.g. {}".format(random.sample(self.filter_examples, 1)[0]))

class CoqTagBox(QtGui.QWidget):
    """ Defines a QWidget class that contains and manages filter tags. """
    
    def __init__(self, *args):
        super(CoqTagBox, self).__init__(*args)
        self.setupUi()
        self.edit_tag.returnPressed.connect(self.addTag)
        self.edit_tag.textEdited.connect(self.editTagText)
        self._tagList = []
        self._filterList = []
        self._tagType = CoqTextTag
        
    def setTagType(self, tagType):
        self._tagType = tagType
        
    def setTagList(self, tagList):
        self._tagList = tagList
        
    def tagList(self):
        return self._tagList
        
    def setupUi(self):
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.cloud_area = FlowLayout(spacing=2)
        self.cloud_area.setObjectName(_fromUtf8("cloud_area"))
        self.verticalLayout.addLayout(self.cloud_area)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(self)
        self.label.setObjectName(_fromUtf8("label"))
        self.label.setText(_fromUtf8("Filter:"))
        self.horizontalLayout.addWidget(self.label)
        self.edit_tag = CoqTagEdit(self)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edit_tag.sizePolicy().hasHeightForWidth())
        self.edit_tag.setSizePolicy(sizePolicy)
        self.edit_tag.setObjectName(_fromUtf8("edit_tag"))
        self.horizontalLayout.addWidget(self.edit_tag)
        self.horizontalLayout.setStretch(1, 0)
        self.verticalLayout.addLayout(self.horizontalLayout)
        #self.verticalLayout.setStretch(0, 1)

        self.setAcceptDrops(True)

    def dragEnterEvent(self, e):
        e.acceptProposedAction()

    def dragMoveEvent(self, e):
        current_rect = QtCore.QRect(
            e.pos() - self.drag.pixmap().rect().topLeft() - self.drag.hotSpot(),
            e.pos() + self.drag.pixmap().rect().bottomRight() - self.drag.hotSpot())
        
        for i, tag in enumerate(self.cloud_area.itemList):
            if tag.geometry().contains(current_rect.topLeft()) or             tag.geometry().contains(current_rect.bottomLeft()) and abs(i - self.ghost_index) == 1:
                self.cloud_area.removeWidget(self.ghost_tag)
                self.cloud_area.insertWidget(i, self.ghost_tag)
                self.ghost_tag.show()
                self.ghost_index = i
                break
        else:
            self.cloud_area.removeWidget(self.ghost_tag)
            self.cloud_area.addWidget(self.ghost_tag)
            self.ghost_tag.show()
            self.ghost_index = i
        e.acceptProposedAction()


    def dropEvent(self, e):
        e.acceptProposedAction()

    def addTag(self, *args):
        """ Add the current text as a query filter. """
        #if args:
        #if type(f) == int:
            #filt = self.edit_tag.text()
        #else:
            #filt = f
        filt = self.edit_tag.text()
        filter_tag = self._tagType(self)
        filter_tag.setContent(filt)
        if not filter_tag.validate():
            self.edit_tag.setStyleSheet(_fromUtf8('CoqTagEdit { border-radius: 5px; font: condensed; background-color: rgb(255, 255, 192); }'))
            return

        self._filterList.append(filt)
        
        self.cloud_area.addWidget(filter_tag)
        self.edit_tag.setText("")
        self.editTagText("")

    def destroyTag(self, tag):
        self.cloud_area.removeWidget(tag)
        tag.close()
        
    def insertTag(self, index, tag):
        self.cloud_area.insertWidget(index, tag)

    def findTag(self, tag):
        """ Returns the index number of the tag in the cloud area, or -1 if
        the tag is not in the cloud area. """
        return self.cloud_area.findWidget(tag)

    def dragTag(self, drag, tag):
        # check if there is only one tag in the tag area:
        if self.cloud_area.count() == 1:
            return

        self.drag = drag
        #self.ghost_tag = self._tagType(self)
        #self.ghost_tag.setContent(tag.content())
        
        self.ghost_tag = QtGui.QLabel(self)
        ghost_pixmap = drag.pixmap().copy()
        painter = QtGui.QPainter(ghost_pixmap)
        painter.setCompositionMode(painter.CompositionMode_DestinationIn)
        painter.fillRect(ghost_pixmap.rect(), QtGui.QColor(0, 0, 0, 96))
        painter.end()
        self.ghost_tag.setPixmap(ghost_pixmap)
        
        
        # the ghost tag will initially be shown at the old position, but
        # may move around depending on the drag position
        old_index = self.findTag(tag)
        self.ghost_index = old_index
        self.cloud_area.removeWidget(tag)
        self.cloud_area.insertWidget(old_index, self.ghost_tag)
        tag.hide()

        if drag.exec_(QtCore.Qt.MoveAction) == QtCore.Qt.MoveAction:
            self.insertTag(self.ghost_index, tag)
        else:
            self.insertTag(old_index, tag)
        tag.show()
        self.cloud_area.removeWidget(self.ghost_tag)
        self.ghost_tag.close()
        self.ghost_tag = None

    def editTagText(self, s):
        """ Set the current background to default. """
        self.edit_tag.setStyleSheet(_fromUtf8("CoqTagEdit { border-radius: 5px; font: condensed; }"))

if __name__ == "__main__":
    app = QtGui.QApplication([])
    filt = CoqTagBox()
    filt.show()
    filt.resize(640, 515)

    sys.exit(app.exec_())