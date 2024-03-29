# -*- coding: utf-8 -*-
"""
coqtagbox.py is part of Coquery.

Copyright (c) 2018-2022 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""
from PyQt5 import QtCore, QtGui, QtWidgets
import random

from coquery import options
from coquery.unicode import utf8
from coquery.gui.pyqt_compat import get_toplevel_window
from coquery.gui.widgets.coqflowlayout import CoqFlowLayout


class CoqTagEdit(QtWidgets.QLineEdit):
    """ Define a QLineEdit class that is used to enter query filters. """

    filter_examples = []

    def __init__(self, *args):
        super(CoqTagEdit, self).__init__(*args)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                           QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)

        if self.filter_examples:
            self.setPlaceholderText("e.g. {}".format(
                random.sample(self.filter_examples, 1)[0]))


class CoqTextTag(QtWidgets.QFrame):
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
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                           QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.horizontalLayout = QtWidgets.QHBoxLayout(self)
        self.horizontalLayout.setContentsMargins(2, 1, 2, 1)

        self.label = QtWidgets.QLabel(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setLineWidth(0)

        self.horizontalLayout.addWidget(self.label)
        self.close_button = QtWidgets.QPushButton(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                           QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.close_button.sizePolicy().hasHeightForWidth())
        self.close_button.setSizePolicy(sizePolicy)
        self.close_button.setFlat(True)

        self.horizontalLayout.addWidget(self.close_button)

        icon = get_toplevel_window().get_icon("Delete")

        height = self.fontMetrics().height()
        new_height = int(height * 0.75)
        self._style_font = "font-size: {}px".format(new_height)
        self._style_border_radius = "border-radius: {}px".format(
            int(new_height / 3))
        self.setBackground("lavender")
        self.close_button.setIcon(icon)
        self.close_button.setIconSize(QtCore.QSize(new_height, new_height))
        self.adjustSize()

    def setBackground(self, color):
        self._style_background = "background-color: {}".format(color)
        s = " ".join(["{};".format(x) for x in [self._style_background,
                                                self._style_border_radius,
                                                self._style_font]])
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

        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        drag.setPixmap(self.grab())
        drag.setHotSpot(e.pos())

        self.parent().parent().parent().parent().dragTag(drag, self)

    def removeRequested(self):
        self.parent().parent().parent().parent().destroyTag(self)

    def validate(self):
        """ Validate the content, and return True if the content is valid,
        or False otherwise. """
        return True


class CoqTagBox(QtWidgets.QWidget):
    """ Defines a QWidget class that contains and manages filter tags. """

    def __init__(self, parent=None, label="Filter"):
        super(CoqTagBox, self).__init__(parent)
        if not label.endswith(":"):
            label = label + ":"
        self._label = label
        self.setupUi()
        self.edit_tag.returnPressed.connect(
            lambda: self.addTag(utf8(self.edit_tag.text())))
        self.edit_tag.textEdited.connect(self.editTagText)
        # self._tagList stores the
        self._tagList = []
        self._filterList = []
        self._tagType = CoqTextTag
        self.edit_tag.setStyleSheet(
            "CoqTagEdit { border-radius: 5px; font: condensed; }")

    def setTagType(self, tagType):
        self._tagType = tagType

    def setTagList(self, tagList):
        self._tagList = tagList

    def tagList(self):
        return self._tagList

    def setupUi(self):
        # make this widget take up all available space:
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)

        self.scroll_area = QtWidgets.QScrollArea()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.scroll_area.sizePolicy().hasHeightForWidth())
        self.scroll_area.setSizePolicy(sizePolicy)
        self.scroll_area.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOn)
        self.scroll_area.setWidgetResizable(True)

        self.scroll_content = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                           QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.scroll_content.sizePolicy().hasHeightForWidth())
        self.scroll_content.setSizePolicy(sizePolicy)

        self.cloud_area = CoqFlowLayout(spacing=5)
        self.scroll_content.setLayout(self.cloud_area)
        self.scroll_area.setWidget(self.scroll_content)

        self.edit_label = QtWidgets.QLabel(self._label)
        self.edit_tag = CoqTagEdit()

        self.edit_layout = QtWidgets.QHBoxLayout()
        self.edit_layout.setSpacing(5)
        self.edit_layout.addWidget(self.edit_label)
        self.edit_layout.addWidget(self.edit_tag)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                           QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.edit_tag.sizePolicy().hasHeightForWidth())
        self.edit_tag.setSizePolicy(sizePolicy)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.scroll_area)
        self.layout.addLayout(self.edit_layout)
        self.layout.setStretch(1, 0)

        self.setAcceptDrops(True)

        col = options.cfg.app.palette().color(QtGui.QPalette.Light)
        S = "QScrollArea {{ background-color: rgb({}, {}, {}); }}".format(
            col.red(), col.green(), col.blue())
        self.scroll_content.setStyleSheet(S)

    def dragEnterEvent(self, e):
        e.acceptProposedAction()

    def dragMoveEvent(self, e):
        pos1 = (e.pos() -
                self.drag.pixmap().rect().topLeft() -
                self.drag.hotSpot())
        pos2 = (e.pos() +
                self.drag.pixmap().rect().bottomRight() -
                self.drag.hotSpot())
        current_rect = QtCore.QRect(pos1, pos2)

        for i, tag in enumerate(self.cloud_area.itemList):
            if (tag.geometry().contains(current_rect.topLeft()) or
                    tag.geometry().contains(current_rect.bottomLeft()) and
                    abs(i - self.ghost_index) == 1):
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

    def addTag(self, s):
        """ Add the current text as a query filter. """
        if not s:
            s = utf8(self.edit_tag.text())
        tag = self._tagType(self)

        tag.setContent(s)

        self._filterList.append(tag)
        self.cloud_area.addWidget(tag)
        self.edit_tag.setText("")
        self.editTagText("")

    def destroyTag(self, tag):
        self.cloud_area.removeWidget(tag)
        tag.close()

    def insertTag(self, index, tag):
        self.cloud_area.insertWidget(index, tag)

    def hasTag(self, s):
        """
        Check if there is a tag with the given string.

        Parameters
        ----------
        s : str
            The string to search for.

        Returns
        -------
        b : bool
            True if there is a tag that contains the string as a label, or
            False otherwise.
        """
        for tag_label in [utf8(self.cloud_area.itemAt(x).widget().text())
                          for x in range(self.cloud_area.count())]:
            if s == tag_label:
                return True
        return False

    def findTag(self, tag):
        """ Returns the index number of the tag in the cloud area, or -1 if
        the tag is not in the cloud area. """
        return self.cloud_area.findWidget(tag)

    def dragTag(self, drag, tag):
        # check if there is only one tag in the tag area:
        if self.cloud_area.count() == 1:
            return

        self.drag = drag

        self.ghost_tag = QtWidgets.QLabel(self)
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
        self.edit_tag.setStyleSheet(
            "CoqTagEdit { border-radius: 5px; font: condensed; }")
