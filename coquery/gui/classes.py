# -*- coding: utf-8 -*-
"""
classes.py is part of Coquery.

Copyright (c) 2016-2022 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

import logging
import os
import pandas as pd
import numpy as np
from collections import deque

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal

from coquery import options
from coquery import managers
from coquery.unicode import utf8

from coquery.gui.pyqt_compat import (
    frameShadow, frameShape, get_toplevel_window)

from xml.sax.saxutils import escape


_left_align = int(QtCore.Qt.AlignLeft) | int(QtCore.Qt.AlignVCenter)
_right_align = int(QtCore.Qt.AlignRight) | int(QtCore.Qt.AlignVCenter)


class inputFocusFilter(QtCore.QObject):
    focusIn = pyqtSignal(object)

    def eventFilter(self, widget, event):
        input_widgets = (QtWidgets.QTextEdit, QtWidgets.QLineEdit)
        if (event.type() == QtCore.QEvent.FocusIn and
                isinstance(widget, input_widgets)):
            self.focusIn.emit(widget)
        return super(inputFocusFilter, self).eventFilter(widget, event)


try:
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
except Exception as e:
    print(e)


class CoqApplication(QtWidgets.QApplication):
    def __init__(self, *arg, **kwarg):
        super(CoqApplication, self).__init__(*arg, **kwarg)

        # remember the last 10 input widgets that had focus:
        self._input_focus_widgets = deque(maxlen=10)

        self.event_filter = inputFocusFilter()
        self.event_filter.focusIn.connect(self.addInputFocusWidget)
        self.installEventFilter(self.event_filter)

    def addInputFocusWidget(self, widget):
        self._input_focus_widgets.append(widget)

    def inputFocusWidgets(self):
        return self._input_focus_widgets


class CoqVerticalHeader(QtWidgets.QHeaderView):
    def enterEvent(self, event):
        self.parent().setCursor(QtCore.Qt.ArrowCursor)
        super(CoqVerticalHeader, self).enterEvent(event)
        event.accept()


class CoqHorizontalHeader(QtWidgets.QHeaderView):
    sectionFinallyResized = pyqtSignal(int, int, int)
    addedToSelection = pyqtSignal(int)
    removedFromSelection = pyqtSignal(int)
    alteredSelection = pyqtSignal(tuple)

    def __init__(self, *args, **kwargs):
        super(CoqHorizontalHeader, self).__init__(*args, **kwargs)
        self.button_pressed = False
        self._resizing = False
        self.sectionResized.connect(self.alert_resize)
        self._selected_columns = []

    def enterEvent(self, event):
        self.parent().setCursor(QtCore.Qt.ArrowCursor)
        super(CoqHorizontalHeader, self).enterEvent(event)
        event.accept()

    def alert_resize(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        self._resizing = True

    def mouseReleaseEvent(self, e):
        super(CoqHorizontalHeader, self).mouseReleaseEvent(e)
        if self._resizing:
            self.sectionFinallyResized.emit(*self._args, **self._kwargs)
            self._resizing = False
        else:
            ix = self.logicalIndexAt(e.pos())
            old_list = self._selected_columns
            if ix in self._selected_columns:
                mode = QtCore.QItemSelectionModel.Deselect
                self._selected_columns.remove(ix)
                self.removedFromSelection.emit(ix)
            else:
                mode = QtCore.QItemSelectionModel.Select
                self._selected_columns.append(ix)
                self.addedToSelection.emit(ix)
            new_list = self._selected_columns
            self.alteredSelection.emit((new_list, old_list))

            select = self.parent().selectionModel()
            model = self.model()
            top = model.index(0, ix, QtCore.QModelIndex())
            bottom = model.index(0, ix, QtCore.QModelIndex())
            selection = QtCore.QItemSelection(top, bottom)
            select.select(selection,
                          mode | QtCore.QItemSelectionModel.Columns)

        self.button_pressed = False

    def mousePressEvent(self, e):
        super(CoqHorizontalHeader, self).mousePressEvent(e)
        self.button_pressed = True

    def reset(self):
        super(CoqHorizontalHeader, self).reset()
        self._selected_columns = []


class CoqHelpBrowser(QtWidgets.QTextBrowser):
    def __init__(self, help_engine, *args, **kwargs):
        self.help_engine = help_engine
        super(CoqHelpBrowser, self).__init__(*args, **kwargs)

    def loadResource(self, resource_type, name):
        if name.scheme() == "qthelp":
            return self.help_engine.fileData(name)
        else:
            return super(CoqHelpBrowser, self).loadResource(
                resource_type, name)


class CoqFeatureList(QtWidgets.QListWidget):
    featureAdded = pyqtSignal(object)

    def __init__(self, parent=None):
        super(CoqFeatureList, self).__init__(parent)
        self.setDragDropMode(self.DragDrop)
        self.setSelectionMode(self.SingleSelection)
        self.setAcceptDrops(False)

        # add (and remove) dummy item to determine usual size of entries:
        super(CoqFeatureList, self).addItem(QtWidgets.QListWidgetItem(""))
        self._item_height = (self.visualItemRect(self.item(0)).height() +
                             self.padding())
        self._item_width = (self.visualItemRect(self.item(0)).width() +
                            self.padding())
        self.takeItem(0)

    def hasItem(self, which):
        which_column = which.data(QtCore.Qt.UserRole)
        for i in range(self.count()):
            item = self.item(i)
            column = item.data(QtCore.Qt.UserRole)
            if which_column == column:
                return True
        return False

    def addItem(self, item):
        if not self.hasItem(item):
            item.setSizeHint(QtCore.QSize(self.itemWidth(),
                                          self.itemHeight()))
            item.setToolTip(
                "Drag feature '{}' to receiving feature tray".format(
                    item.text()))
            super(CoqFeatureList, self).addItem(item)
        self.featureAdded.emit(item)

    def itemWidth(self):
        return self._item_width

    def itemHeight(self):
        return self._item_height

    def padding(self):
        return 4 * self.frameWidth()


class CoqFeatureTray(CoqFeatureList):
    """
    A feature tray is a CoqFeatureTable that can hold up to one feature.

    It never shows scrollbars or headers.
    """
    featureChanged = pyqtSignal(object)
    featureCleared = pyqtSignal()

    def __init__(self, parent=None):
        super(CoqFeatureTray, self).__init__(parent)
        self.setAcceptDrops(True)
        self.setEditTriggers(self.NoEditTriggers)

        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.setMaximumHeight(self.itemHeight() + 2 * self.frameWidth())
        self.setMinimumHeight(self.itemHeight() + 2 * self.frameWidth())

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored,
                                           QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)

        self._content_source = None
        self._placed_feature = None

    def padding(self):
        return 4 * self.frameWidth()

    def text(self):
        if self.count():
            return utf8(self.item(0).text())
        else:
            return None

    def data(self):
        if self.count() and self.isEnabled():
            return utf8(self.item(0).data(QtCore.Qt.UserRole))
        else:
            return None

    def send_back(self):
        item = self.takeItem(0)
        # return to sender
        if self._content_source is not None:
            self._content_source.addItem(item)
        self._content_source = None

    def clear(self, no_return=False):
        if self.count() and not no_return:
            self.send_back()
        super(CoqFeatureTray, self).clear()
        self.featureCleared.emit()

    def addItem(self, item):
        item.setSizeHint(QtCore.QSize(self.itemWidth(), self.itemHeight()))
        item.setToolTip(
            "Click on Clear button to remove '{}'".format(item.text()))
        super(QtWidgets.QListWidget, self).addItem(item)
        self.featureAdded.emit(item)

    def setItem(self, item, source):
        if self.count():
            self.send_back()
        self._content_source = source
        self.addItem(item)
        item.setSizeHint(QtCore.QSize(self.itemWidth(), self.itemHeight()))
        self.setCurrentItem(item)
        self.featureChanged.emit(item)

    def dropEvent(self, e):
        if self.count():
            self.send_back()

        if isinstance(e.source(), CoqFeatureTray):
            self._content_source = e.source()._content_source
            e.source().clear(no_return=True)
        else:
            self._content_source = e.source()
        super(CoqFeatureTray, self).dropEvent(e)
        self.setFocus()
        self.selectionModel().clear()
        item = self.item(0)
        self.setCurrentItem(item)
        self.featureChanged.emit(item)


class CoqRotatedButton(QtWidgets.QPushButton):
    """
    A rotated push button.
    """

    def paintEvent(self, event):
        painter = QtWidgets.QStylePainter(self)
        painter.rotate(270)
        painter.translate(-self.height(), 0)
        painter.drawControl(QtWidgets.QStyle.CE_PushButton,
                            self.getSyleOptions())

    def minimumSizeHint(self):
        size = QtWidgets.QPushButton(self.text()).minimumSizeHint()
        size.transpose()
        return size

    def sizeHint(self):
        size = QtWidgets.QPushButton(self.text()).sizeHint()
        size.transpose()
        return size

    def getSyleOptions(self):
        options = QtWidgets.QStyleOptionButton()
        options.initFrom(self)
        size = options.rect.size()
        size.transpose()
        options.rect.setSize(size)

        # get default ButtonFeature for a normal push button (0x00):
        options.features = QtWidgets.QStyleOptionButton.ButtonFeature(0)

        features = []

        if self.isFlat():
            features.append(QtWidgets.QStyleOptionButton.Flat)
        elif not self.isDown():
            features.append(QtWidgets.QStyle.State_Raised)

        if self.menu():
            features.append(QtWidgets.QStyleOptionButton.HasMenu)
        if self.isDefault():
            features.append(QtWidgets.QStyleOptionButton.AutoDefaultButton)
            features.append(QtWidgets.QStyleOptionButton.DefaultButton)
        if self.autoDefault():
            features.append(QtWidgets.QStyleOptionButton.AutoDefaultButton)
        if self.isDown() or (self.menu() and self.menu().isVisible()):
            features.append(QtWidgets.QStyle.State_Sunken)
        if self.isChecked():
            features.append(QtWidgets.QStyle.State_On)

        for feat in features:
            options.features = options.features | feat

        options.text = self.text()
        options.icon = self.icon()
        options.iconSize = self.iconSize()
        return options


class CoqInfoLabel(QtWidgets.QLabel):
    entered = pyqtSignal()
    left = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(CoqInfoLabel, self).__init__(*args, **kwargs)
        self.setCursor(QtCore.Qt.WhatsThisCursor)

        self.setText("")
        self.setPixmap(get_toplevel_window().get_icon("Info").pixmap(
            QtCore.QSize(QtWidgets.QSpinBox().sizeHint().height(),
                         QtWidgets.QSpinBox().sizeHint().height())))


class CoqClickableLabel(QtWidgets.QLabel):
    clicked = pyqtSignal()
    textChanged = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(CoqClickableLabel, self).__init__(*args, **kwargs)
        self._content = None

    def mousePressEvent(self, ev):
        self.clicked.emit()

    def setPlaceholderText(self, s):
        super(CoqClickableLabel, self).setText(s)

    def setText(self, s):
        super(CoqClickableLabel, self).setText(s)
        self._content = s
        self.textChanged.emit()

    def text(self):
        return self._content


class CoqExclusiveGroup(object):
    def __init__(self, lst):
        self._widget_list = [x for x in lst if hasattr(x, "toggled")]
        _checked = None
        self._maxwidth = 0
        for element in self._widget_list:
            self._maxwidth = max(self._maxwidth, element.sizeHint().width())
            if _checked is not None:
                if element.isChecked():
                    element.setChecked(False)
            else:
                _checked = element.isChecked()

        for element in self._widget_list:
            element.setMaximumWidth(self._maxwidth)
            element.setMinimumWidth(self._maxwidth)
            element.toggled.connect(lambda x: self.toggle_group(x))

    def toggle_group(self, widget):
        if widget.isChecked():
            for element in [x for x in self._widget_list if x != widget]:
                if element.isChecked():
                    element.setChecked(False)


class CoqGroupBox(QtWidgets.QGroupBox):
    """
    """

    style_opened = """
        CoqGroupBox {{
            font: {title_weight};
            background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                              stop: 0 {button_button},
                                              stop: 1 {button_midlight});
            border: 1px solid gray;
            border-radius: 2px;
            border-style: inset;
            margin-top: {header_size};
        }}

        CoqGroupBox::title {{
            font: {title_weight};

            background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 {button_midlight},
                                            stop: 1 {button_button});
            border-top: 1px;
            border-left: 1px;
            border-right: 1px;
            border-bottom: 0px;
            border-radius: 5px;
            border-color: {button_mid};
            border-style: inset;

            subcontrol-origin: margin;
            subcontrol-position: top left; /* position at the top center */
            padding: 0 {pad_right}px 0 0;
            margin-top: 0px;
            margin-left: 0px;
            margin-bottom: 2px;
        }}

        CoqGroupBox::indicator {{
            width: {icon_size}px;
            height: {icon_size}px;
        }}

        CoqGroupBox::indicator:unchecked {{
            image: url({path}/{sign_down});
        }}

        CoqGroupBox::indicator:checked {{
            image: url({path}/{sign_up});
        }}"""

    style_closed = """
        CoqGroupBox {{
            font: {title_weight};
            border: 0px solid gray;
            border-radius: 0px;
            margin-top: 0px;
            margin-left: 0px;
            margin-right: 0px;
            margin-bottom: 4px;
        }}

        CoqGroupBox::title {{
            font: {title_weight};
            background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 {button_button},
                                            stop: 1 {button_midlight});
            border-top: 1px;
            border-left: 1px;
            border-right: 1px;
            border-bottom: 1px;
            border-radius: 5px;
            border-color: {button_mid};
            border-style: outset;

            subcontrol-origin: margin;
            subcontrol-position: top left; /* position at the top center */
            padding: 0 {pad_right}px 0 0;
            margin-top: 1px;
        }}

        CoqGroupBox::indicator {{
            width: {icon_size}px;
            height: {icon_size}px;
        }}

        CoqGroupBox::indicator:unchecked {{
            image: url({path}/{sign_down});

        }}

        CoqGroupBox::indicator:checked {{
            image: url({path}/{sign_up});
        }}"""

    toggled = pyqtSignal(QtWidgets.QWidget)

    def __init__(self, *args, **kwargs):
        super(CoqGroupBox, self).__init__(*args, **kwargs)
        self._text = ""
        self._alternative = None
        self.clicked.connect(self.setChecked)
        self.setStyleSheet(self.style_opened)

    def set_style(self, **kwargs):
        if self.isChecked():
            s = self.style_opened
        else:
            s = self.style_closed

        icon_size = QtWidgets.QPushButton().sizeHint().height() - 6
        header_size = icon_size + 1
        pad = 10
        if "title_weight" not in kwargs:
            kwargs["title_weight"] = "normal"
        palette = options.cfg.app.palette()
        s = s.format(path=os.path.join(options.cfg.base_path, "icons",
                                       "small-n-flat", "PNG"),
                     sign_up="sign-minimize.png",
                     sign_down="sign-maximize.png",
                     icon_size=icon_size, header_size=header_size,
                     pad_right=pad,
                     button_light=palette.color(QtGui.QPalette.Light).name(),
                     button_midlight=palette.color(
                         QtGui.QPalette.Midlight).name(),
                     button_button=palette.color(QtGui.QPalette.Button).name(),
                     button_mid=palette.color(QtGui.QPalette.Mid).name(),
                     button_dark=palette.color(QtGui.QPalette.Dark).name(),
                     box_light=palette.color(QtGui.QPalette.Window).name(),
                     box_dark=palette.color(QtGui.QPalette.Window).name(),
                     focus=palette.color(QtGui.QPalette.Highlight).name(),
                     **kwargs)
        self.setStyleSheet(s)

    def setTitle(self, text, *args, **kwargs):
        super(CoqGroupBox, self).setTitle(text, *args, **kwargs)
        self._text = text
        if self._alternative == "":
            self._alternative = text

    def setAlternativeTitle(self, text):
        self._alternative = text

    def title(self):
        return self._text

    def alternativeTitle(self):
        return self._alternative

    def _hide_content(self, element=None):
        if element is None:
            element = self.layout()
        if element is None:
            return
        if element.isWidgetType():
            element.hide()
        else:
            for x in element.children():
                self._show_content(x)
            for i in range(element.count()):
                item = element.itemAt(i)
                if isinstance(item, QtWidgets.QWidgetItem):
                    self._hide_content(item.widget())
                else:
                    self._hide_content(item)

    def _show_content(self, element=None):
        if element is None:
            element = self.layout()
        if element is None:
            return
        if element.isWidgetType():
            element.show()
        else:
            for x in element.children():
                self._show_content(x)
            for i in range(element.count()):
                item = element.itemAt(i)
                if isinstance(item, QtWidgets.QWidgetItem):
                    self._show_content(item.widget())
                else:
                    self._show_content(item)

    def sizeHint(self, *args, **kwargs):
        x = super(CoqGroupBox, self).sizeHint(*args, **kwargs)
        try:
            x.setWidth(self._width)
        except AttributeError:
            pass
        return x

    def size(self, *args, **kwargs):
        x = super(CoqGroupBox, self).size(*args, **kwargs)
        return x

    def setChecked(self, checked):
        super(CoqGroupBox, self).setChecked(checked)
        if checked is True:
            self._show_content()
        else:
            self._hide_content()

        self.set_style()
        self.toggled.emit(self)


class CoqDetailBox(QtWidgets.QWidget):
    """
    Define a QLayout class that has the QPushButton 'header' as a clickable
    header, and a QFrame 'box' which can show any content in an exapnding box
    below the button.
    """
    clicked = pyqtSignal(QtWidgets.QWidget)
    expanded = pyqtSignal()
    collapsed = pyqtSignal()

    def __init__(self, text="", box=None, alternative=None, *args, **kwargs):
        if isinstance(text, QtWidgets.QWidget):
            if args:
                args = tuple(list(args).insert(0, text))
            else:
                args = tuple([text])
            text = ""
        super(CoqDetailBox, self).__init__(*args, **kwargs)

        if not box:
            self.box = QtWidgets.QFrame(self)
        else:
            self.box = box

        self.frame = QtWidgets.QFrame(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                           QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(frameShape)
        self.frame.setFrameShadow(frameShadow)

        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.setSpacing(4)

        self.header = QtWidgets.QPushButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                           QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.header.sizePolicy().hasHeightForWidth())
        self.header.setSizePolicy(sizePolicy)
        self.header.setStyleSheet(
            "text-align: left; padding: 4px; padding-left: 1px;")
        self.header.clicked.connect(self.onClick)
        self.header_layout.addWidget(self.header)

        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.addItem(self.header_layout)
        self.verticalLayout_2.addWidget(self.box)

        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.addWidget(self.frame)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)

        self._text = text
        if alternative:
            self._alternative = alternative
        else:
            self._alternative = text
        self._expanded = False
        self.update()
        self.setText(text)
        self._data = {}

    def data(self, role):
        return self._data[role]

    def setData(self, role, data):
        self._data[role] = data

    def onClick(self):
        self.clicked.emit(self)
        self.toggle()

    def replaceBox(self, widget):
        self.verticalLayout.removeWidget(self.box)
        self.verticalLayout.addWidget(widget)
        widget.setParent(self)
        self.box = widget
        self.update()

    def setText(self, text):
        self._text = text

    def setAlternativeText(self, text):
        self._alternative = text

    def text(self):
        return self._text

    def setExpandedText(self, alternative):
        self._alternative = alternative

    def toggle(self):
        self._expanded = not self._expanded
        if self._expanded:
            self.expanded.emit()
        else:
            self.collapsed.emit()
        self.update()

    def update(self):
        def get_pal(x):
            return options.cfg.app.palette().color(x).name()

        try:
            up = get_toplevel_window().get_icon("Multiply")
            down = get_toplevel_window().get_icon("Plus Math")
        except AttributeError:
            up = None
            down = None
        if self._expanded:
            self.box.show()
            self.header.setFlat(False)
            self.header.setText(self._alternative)
            s = utf8(options.cfg.app.translate(
                "MainWindow",
                "Click to hide corpus information",
                None))
            self.header.setToolTip(s)
            icon = up
        else:
            try:
                self.header.setText(self._text)
                s = utf8(options.cfg.app.translate(
                    "MainWindow",
                    "Click to show corpus information",
                    None))
                self.header.setToolTip(s)

                highlight = options.cfg.app.palette().color(
                    QtGui.QPalette.Highlight)
                darker_highlight = QtGui.QColor(highlight)
                darker_highlight.setAlpha(0.5)

                kwargs = {
                    "border": get_pal(QtGui.QPalette.Button),
                    "hoverborder": get_pal(QtGui.QPalette.Midlight),
                    "hoverhighlight": get_pal(QtGui.QPalette.Highlight),
                    "hoverlowlight": darker_highlight.name(),
                    "presshighlight": get_pal(QtGui.QPalette.Button),
                    "presslowlight": get_pal(QtGui.QPalette.Midlight),
                    "hovercolor": get_pal(QtGui.QPalette.HighlightedText)}
                self.header.setStyleSheet("""
                    QPushButton {{
                        text-align: left;
                        padding: 4px;
                        padding-left: 2px;
                        border: 0px solid {border} }}
                    QPushButton:hover {{
                        text-align: left;
                        padding: 4px;
                        padding-left: 1px;
                        border: 1px solid {hoverborder};
                        color: {hovercolor};
                        background-color: qLineargradient(
                            x1: 0, y1: 0, x2: 0, y2: 1,
                            stop: 0 {hoverhighlight},
                            stop: 0.15 {hoverlowlight}); }}
                    QPushButton:pressed {{
                        text-align: left;
                        padding: 4px;
                        padding-left: 1px;
                        border: 1px solid {hoverborder};
                        background-color: qLineargradient(
                            x1: 0, y1: 0, x2: 0, y2: 1,
                            stop: 0 {presshighlight},
                            stop: 0.85 {presslowlight}); }}
                    """.format(**kwargs))
                self.box.hide()
            except RuntimeError:
                # The box may have been deleted already, which raises a
                # harmless RuntimeError
                pass
            self.header.setFlat(True)
            self.header.update()
            icon = down
        if icon:
            self.header.setIcon(icon)

    def setExpanded(self, b):
        self._expanded = b
        if self._expanded:
            self.expanded.emit()
        else:
            self.collapsed.emit()
        self.update()

    def isExpanded(self):
        return self._expanded


class CoqSpinner(QtWidgets.QWidget):
    """
    A QWidget subclass that contains an animated spinner.
    """

    @staticmethod
    def get_spinner(size=None):
        """
        Return a movie that shows the spinner animation.

        Parameters
        ----------
        size : QSize or int
            The size of the spinner
        """
        sizes = [24, 32, 64, 96, 128]
        distances = [abs(x - size) for x in sizes]
        opt_size = sizes[distances.index(min(distances))]
        path = os.path.join(options.cfg.base_path,
                            "icons",
                            "progress_{0}x{0}.gif".format(opt_size))
        anim = QtGui.QMovie(path)
        anim.setScaledSize(QtCore.QSize(size, size))
        return anim

    def __init__(self, size=None, *args, **kwargs):
        super(CoqSpinner, self).__init__(*args, **kwargs)
        self._layout = QtWidgets.QHBoxLayout(self)
        self._label = QtWidgets.QLabel()
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.addWidget(self._label)
        self._label.hide()
        self._size = size

    def sizeHint(self):
        return self._label.sizeHint()

    def start(self):
        self._anim = self.get_spinner(self._label.sizeHint().height())
        self._label.setMovie(self._anim)
        self._label.show()
        self._anim.start()

    def stop(self):
        self._label.hide()
        self._anim.stop()


class CoqProgressDialog(QtWidgets.QDialog):
    def __init__(self, title="", parent=None):
        super(CoqProgressDialog, self).__init__(parent)
        from .ui.progressDialogUi import Ui_ProgressDialog
        self.ui = Ui_ProgressDialog()
        self.ui.setupUi(self)
        self.setWindowTitle(title)

    def setMaximum(self, val):
        self.ui.progressBar.setMaximum(val)

    def maximum(self):
        return self.ui.progressBar.maximum()

    def setValue(self, val):
        self.ui.progressBar.setValue(val)

    def value(self):
        return self.ui.progressBar.value()

    def setFormat(self, s):
        self.ui.progressBar.setFormat(s)

    def format(self):
        self.ui.progressBar.format()


class CoqTableItem(QtWidgets.QTableWidgetItem):
    def __init__(self, *args, **kwargs):
        super(CoqTableItem, self).__init__(*args, **kwargs)
        self._objectName = ""

    def setObjectName(self, s):
        self._objectName = s

    def objectName(self):
        return self._objectName


class CoqTreeItem(QtWidgets.QTreeWidgetItem):
    """
    Define a tree element class that stores the output column options in
    the resource feature tree.
    """
    def __init__(self, *args, **kwargs):
        super(CoqTreeItem, self).__init__(*args, **kwargs)
        self._objectName = ""
        self._link_by = None
        self._func = None

    def isLinked(self):
        """
        Return True if the entry represenets a linked table.
        """
        return self._link_by is not None

    def setText(self, column, text, *args):
        text = utf8(text)
        feature = utf8(self.objectName())
        if feature.endswith("_table"):
            self.setToolTip(column, "Corpus table: {}".format(text))
        else:
            self.setToolTip(column, "Corpus field:\n{}".format(text))

        super(CoqTreeItem, self).setText(column, text)

    def setObjectName(self, name):
        """ Store resource variable name as object name. """
        self._objectName = utf8(name)

    def objectName(self):
        """ Retrieve resource variable name from object name. """
        return utf8(self._objectName)

    def check_children(self, column=0):
        """
        Compare the check state of all children.

        Parameters
        ----------
        column : int (default=0)
            The column of the tree widget

        Returns
        -------
        state : bool
            True if all children have the same check state, False if at least
            one child has a different check state than another.
        """
        child_states = self.get_children_states(column)

        all_checked = all([x == QtCore.Qt.Checked for x in child_states])
        all_unchecked = all([x == QtCore.Qt.Unchecked for x in child_states])

        return all_checked or all_unchecked

    def get_children_states(self, column=0):
        """
        Return a list of values representing the check states of the children.
        """
        return [self.child(i).checkState(column)
                for i in range(self.childCount())]

    def on_change(self):
        if self.checkState(0) == QtCore.Qt.Unchecked:
            if (self.childCount() and
                    self.check_children() and
                    self.child(0).checkState(0) != QtCore.Qt.Unchecked):
                self.setCheckState(0, QtCore.Qt.PartiallyChecked)

    def update_checkboxes(self, column, expand=False):
        """
        Propagate the check state of the item to the other tree items.

        This method propagates the check state of the current item to its
        children (e.g. if the current item is checked, all children are also
        checked). It also toggles the check state of the parent, but only if
        the current item is a native feature of the parent, and not a linked
        table.

        If the argument 'expand' is True, the parents of items with checked
        children will be expanded.

        Parameters
        ----------
        column : int
            The nubmer of the column
        expand : bool
            If True, a parent node will be expanded if the item is checked
        """
        check_state = self.checkState(column)
        mother = self.parent()

        if check_state != QtCore.Qt.PartiallyChecked:
            self.set_children_checkboxes(column, check_state)

        if (utf8(self._objectName).endswith("_table") and
                check_state != QtCore.Qt.Unchecked):
            self.setExpanded(True)

        if mother:
            if not mother.check_children():
                mother.setCheckState(column, QtCore.Qt.PartiallyChecked)
            else:
                mother.setCheckState(column, check_state)

    def set_children_checkboxes(self, column, check_state):
        for child in [self.child(i) for i in range(self.childCount())]:
            if not isinstance(child, CoqTreeExternalTable):
                child.setCheckState(column, check_state)


class CoqTreeExternalTable(CoqTreeItem):
    """
    Define a CoqTreeItem class that represents a linked table.
    """
    def setLink(self, link):
        self._link_by = link
        self.link = link

    def update_checkboxes(self, column, expand=False):
        check_state = self.checkState(column)
        mother = self.parent()

        if check_state != QtCore.Qt.PartiallyChecked:
            self.set_children_checkboxes(column, check_state)

        all_siblings_unchecked = all([x == QtCore.Qt.Unchecked for x in
                                      mother.get_children_states(column)])

        if check_state == QtCore.Qt.Unchecked:
            if (mother.checkState(column) == QtCore.Qt.PartiallyChecked and
                    all_siblings_unchecked):
                mother.setCheckState(column, QtCore.Qt.Unchecked)
        else:
            if (mother.checkState(column) == QtCore.Qt.Unchecked):
                mother.setCheckState(column, QtCore.Qt.PartiallyChecked)

    def setText(self, column, text, *args):
        super(CoqTreeItem, self).setText(column, text, *args)
        self.setToolTip(column, "External table: {}".format(utf8(text)))


class CoqTreeExternalItem(CoqTreeItem):
    """
    Define a CoqTreeItem class that represents a resource from a linked table.
    """
    def setText(self, column, text, *args):
        super(CoqTreeItem, self).setText(column, text, *args)
        self.setToolTip(column, "External column: {}".format(utf8(text)))


class CoqTreeWidget(QtWidgets.QTreeWidget):
    """
    Define a tree widget that stores the available output columns in a tree
    with check boxes for each variable.
    """
    def __init__(self, *args):
        super(CoqTreeWidget, self).__init__(*args)
        self.itemChanged.connect(self.update)
        self.setDragEnabled(True)
        self.setAnimated(True)

    def update(self, item, column):
        """ Update the checkboxes of parent and child items whenever an
        item has been changed. """
        item.update_checkboxes(column)

    def getItem(self, object_name):
        """ Set the checkstate of the item that matches the object_name. If
        the state is Checked, also expand the parent of the item. """

        for root in [self.topLevelItem(i)
                     for i in range(self.topLevelItemCount())]:
            for child in [root.child(i)
                          for i in range(root.childCount())]:
                if child.objectName() == object_name:
                    return child

    def setCheckState(self, object_name, state, column=0):
        """
        Recursively set the checkstate of the item that matches the
        object_name. If the state is Checked, also expand the parent of
        the item. """

        def _check_state(item, object_name, state, column=0):
            # is this the feature you're looking for?
            if item.objectName() == object_name:
                # Group columns are always required features, so if a
                # group column is supposed to be unchecked, it is still
                # checked partially.
                if (state == QtCore.Qt.Unchecked and
                        object_name in options.cfg.group_columns):
                    item.setCheckState(column, QtCore.Qt.PartiallyChecked)
                else:
                    item.setCheckState(column, state)

                if state == QtCore.Qt.Checked:
                    item.parent().setExpanded(True)
                self.update(item, column)
            for child in [item.child(i)
                          for i in range(item.childCount())]:
                _check_state(child, object_name, state, column)

        if type(state) != QtCore.Qt.CheckState:
            if state:
                state = QtCore.Qt.Checked
            else:
                state = QtCore.Qt.Unchecked

        for root in [self.topLevelItem(i)
                     for i in range(self.topLevelItemCount())]:
            if root.objectName() == object_name:
                try:
                    root.setChecked(column, state)
                except AttributeError:
                    # The corpus table raises this exception, but it seems
                    # that this is not really a problem.
                    # FIXME: Figure out why this happens, and remove the
                    # cause
                    print("Exception raised")
                    pass
                self.update(root, column)

            for child in [root.child(i)
                          for i in range(root.childCount())]:
                _check_state(child, object_name, state, column)

    def getCheckState(self, object_name):
        for root in [self.topLevelItem(i)
                     for i in range(self.topLevelItemCount())]:
            for child in [root.child(i)
                          for i in range(root.childCount())]:
                if child.objectName() == object_name:
                    return child.checkState(0)
        return None

    def mimeData(self, *args):
        """ Add the resource variable name to the MIME data (for drag and
        drop). """
        value = super(CoqTreeWidget, self).mimeData(*args)
        value.setText(", ".join([x.objectName() for x in args[0]]))
        return value

    def get_checked(self, column=0):
        check_list = []
        for root in [self.topLevelItem(i)
                     for i in range(self.topLevelItemCount())]:
            for child in [root.child(i)
                          for i in range(root.childCount())]:
                if child.checkState(column) == QtCore.Qt.Checked:
                    check_list.append(utf8(child._objectName))
        return check_list


class CoqTableWidget(QtWidgets.QTableWidget):
    def mimeData(self, *args):
        val = super(CoqTableWidget, self).mimeData(*args)
        val.setText(",".join([x.data(QtCore.Qt.UserRole) for x in args[0]]))
        return val


class LogTableModel(QtCore.QAbstractTableModel):
    """
    Define a QAbstractTableModel class that stores logging messages.
    """
    def __init__(self, data, parent, *args):
        super(LogTableModel, self).__init__(parent, *args)
        self.content = data
        self.header = ["Date", "Time", "Level", "Message"]

    def data(self, index, role):
        if not index.isValid():
            return None

        record = self.content[index.row()]
        if role == QtCore.Qt.DisplayRole:
            day, time = record.asctime.split()
            return (day,
                    time,
                    record.levelname,
                    record.message)[index.column()]
        elif role == QtCore.Qt.ForegroundRole:
            if record.levelno in [logging.ERROR, logging.CRITICAL]:
                return QtGui.QBrush(QtCore.Qt.white)
            else:
                return None
        elif role == QtCore.Qt.BackgroundRole:
            if record.levelno == logging.WARNING:
                return QtGui.QBrush(QtGui.QColor("lightyellow"))
            elif record.levelno in [logging.ERROR, logging.CRITICAL]:
                return QtGui.QBrush(QtGui.QColor("#aa0000"))
        else:
            return None

    def rowCount(self, parent):
        return len(self.content)

    def columnCount(self, parent):
        return len(self.header)


class LogProxyModel(QtCore.QSortFilterProxyModel):
    """
    Define a QSortFilterProxyModel that manages access to the logging
    messages.
    """

    def __init__(self, *args, **kwargs):
        super(LogProxyModel, self).__init__(*args, **kwargs)
        self.updateFilter()

    def updateFilter(self):
        if not options.cfg.show_log_messages:
            S = "---"
        else:
            S = "|".join(options.cfg.show_log_messages)
        regexp = QtCore.QRegExp(S,
                                QtCore.Qt.CaseInsensitive,
                                QtCore.QRegExp.RegExp)
        self.setFilterRegExp(regexp)
        self.setFilterKeyColumn(2)

    def headerData(self, index, orientation, role):
        if orientation == QtCore.Qt.Vertical:
            return
        else:
            # column names:
            header = self.sourceModel().header
            if not header or index > len(header):
                return None

            if role == QtCore.Qt.DisplayRole:
                return header[index]


class CoqTextEdit(QtWidgets.QTextEdit):
    """
    Defines a QTextEdit class that accepts dragged objects.
    """
    def __init__(self, *args):
        super(CoqTextEdit, self).__init__(*args)
        self.setAcceptDrops(True)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, e):
        e.acceptProposedAction()

    def dragMoveEvent(self, e):
        e.acceptProposedAction()

    def dropEvent(self, e):
        # get the relative position from the mime data
        if ("application/x-qabstractitemmodeldatalist"
                in e.mimeData().formats()):
            label = e.mimeData().text()
            if label == "word_label":
                self.insertPlainText("*")
                e.setDropAction(QtCore.Qt.CopyAction)
            elif label == "word_pos":
                self.insertPlainText("*.[*]")
                e.setDropAction(QtCore.Qt.CopyAction)
            elif label == "lemma_label":
                self.insertPlainText("[*]")
                e.setDropAction(QtCore.Qt.CopyAction)
            elif label == "lemma_transcript":
                self.insertPlainText("[/*/]")
                e.setDropAction(QtCore.Qt.CopyAction)
            elif label == "word_transcript":
                self.insertPlainText("/*/")
                e.setDropAction(QtCore.Qt.CopyAction)
        elif e.mimeData().hasText():
            self.insertPlainText(e.mimeData().text())
            e.setDropAction(QtCore.Qt.CopyAction)

        e.accept()


class CoqListWidget(QtWidgets.QListWidget):
    itemDropped = pyqtSignal(QtWidgets.QListWidgetItem)
    featureAdded = pyqtSignal(str)
    featureRemoved = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(CoqListWidget, self).__init__(*args, **kwargs)

    def dropEvent(self, e):
        new_item = self.addFeature(e.mimeData().text())
        if new_item is not None:
            self.itemDropped.emit(new_item)
            e.acceptProposedAction()

    def get_item(self, rc_feature):
        rc_feature = utf8(rc_feature)
        for i in range(self.count()):
            item = self.item(i)
            if utf8(item.data(QtCore.Qt.UserRole)) == rc_feature:
                return item
        return None

    def addFeature(self, rc_feature):
        rc_feature = utf8(rc_feature)
        if self.get_item(rc_feature) is not None:
            return

        try:
            label = getattr(get_toplevel_window().resource, rc_feature)
        except AttributeError:
            try:
                label = (get_toplevel_window()
                         .Session.translate_header(rc_feature))
            except AttributeError:
                return None

        new_item = QtWidgets.QListWidgetItem(label)
        new_item.setData(QtCore.Qt.UserRole, rc_feature)
        self.addItem(new_item)
        self.setCurrentItem(new_item)
        self.itemActivated.emit(new_item)
        self.featureAdded.emit(rc_feature)
        return new_item


class CoqFloatEdit(QtWidgets.QLineEdit):
    """
    Define a QLineEidt class that takes float numbers as input.

    Allowed characters are numbers 0-9, '-' and the decimal point character.
    The backspace character '\b' is also allowed.
    """
    allowed_characters = "0123456789-"
    valueChanged = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(CoqFloatEdit, self).__init__(*args, **kwargs)
        self.dec = QtCore.QLocale().decimalPoint()
        self.textChanged.connect(self._fire)

    def _fire(self):
        self.valueChanged.emit()

    def setValue(self, val):
        if val is not None:
            self.setText(QtCore.QLocale().toString(val))

    def value(self):
        val, success = QtCore.QLocale().toDouble(self.text())
        if success:
            return val
        else:
            return None

    def keyPressEvent(self, ev):
        def get_next_char_event():
            """
            Get a QKeyEvent instance that moves the cursor to the next
            character. It tries to handle correctly left-to-right and
            right-to-left writing systems. But of course, this won't work
            straightaway...
            """
            if QtCore.QLocale().textDirection() == QtCore.Qt.LeftToRight:
                key = QtCore.Qt.Key_Right
            else:
                key = QtCore.Qt.Key_Left

            return QtGui.QKeyEvent(QtCore.QEvent.KeyRelease,
                                   key,
                                   QtCore.Qt.NoModifier)

        text = ev.text()
        content = utf8(self.text())
        leading_figures = content[:self.cursorPosition()].strip("-")
        text_to_dec = content.partition(self.dec)[0]

        # handle special keys that don't have a visual representation or are
        # represented by an escape sequence:
        if (not "{}".format(text) or
                ev.key() in (QtCore.Qt.Key_Delete, QtCore.Qt.Key_Enter,
                             QtCore.Qt.Key_Return, QtCore.Qt.Key_Backspace)):
            return super(CoqFloatEdit, self).keyPressEvent(ev)

        # handle the decimal point key:
        if text == self.dec:
            try:
                current_char = content[self.cursorPosition()]
            except IndexError:
                current_char = None
            if current_char == self.dec:
                ev = get_next_char_event()
            elif self.dec in content or not leading_figures:
                return ev.ignore()

            return super(CoqFloatEdit, self).keyPressEvent(ev)

        # handle the remaining allowed characters:
        if text in self.allowed_characters:
            if (text == "-" and
                    self.cursorPosition() > 0):
                return ev.ignore()
            elif (text == "0" and
                    self.cursorPosition() == 0 and
                    text_to_dec == "0"):
                ev = get_next_char_event()
            elif (text == "0" and
                    self.cursorPosition() > 0 and
                    all([x == "0" for x in leading_figures])):
                return ev.ignore()

            return super(CoqFloatEdit, self).keyPressEvent(ev)

        ev.ignore()


class CoqIntEdit(CoqFloatEdit):
    dec = None

    def __init__(self, *args, **kwargs):
        super(CoqIntEdit, self).__init__(*args, **kwargs)
        self.dec = None

    def value(self):
        val, success = QtCore.QLocale().toInt(self.text())
        if success:
            return val
        else:
            return None


class CoqTableView(QtWidgets.QTableView):
    resizeRow = pyqtSignal(int, int)

    def __init__(self, *args, **kwargs):
        super(CoqTableView, self).__init__(*args, **kwargs)
        self.resizeRow.connect(self.setRowHeight)
        self.setMouseTracking(True)

    def selectAll(self):
        super(CoqTableView, self).selectAll()
        h_header = self.horizontalHeader()
        h_header._selected_columns = list(range(len(h_header)))

    def setWordWrap(self, wrap, *args, **kwargs):
        super(CoqTableView, self).setWordWrap(wrap, *args, **kwargs)
        self._wrap_flag = int(QtCore.Qt.TextWordWrap) if bool(wrap) else 0

    def resizeRowsToContents(self, *args, **kwargs):
        def set_height(n, row, metric):
            # determine the maximum required height for this row by
            # checking the height of each cell

            height = 0
            for col in row.index:
                height = max(
                    height,
                    metric.boundingRect(
                        rects[col], self._wrap_flag, str(row[col])).height())
            if self.rowHeight(n) != height:
                self.resizeRow.emit(n, height)

        # FIXME: This method may be obsolete

        cols = [x for x in self.model().header
                if x in (("coq_context_left",
                          "coq_context_right",
                          "coq_context_string"))]
        if not cols:
            return
        df = self.model().content

        metric = self.fontMetrics()
        # create a dictionary of QRect, each as wide as a column in the
        # table
        rects = {
            df.columns[i]: QtCore.QRect(0, 0, self.columnWidth(i) - 2, 99999)
            for i in range(self.horizontalHeader().count())}

        df[cols].apply(
            lambda x: set_height(np.where(df.index == x.name)[0], x, metric),
            axis="columns")

    def resizeColumnsToContents(self, *args, **kwargs):
        self.setVisible(False)
        super(CoqTableView, self).resizeColumnsToContents(*args, **kwargs)
        self.setVisible(True)

    def mouseMoveEvent(self, event):
        pos = event.pos()
        index = self.indexAt(pos)
        self.setCursor(QtCore.Qt.ArrowCursor)
        if index.isValid():
            if self.model().header[index.column()].startswith("coq_userdata"):
                self.setCursor(QtCore.Qt.IBeamCursor)
            else:
                self.setCursor(QtCore.Qt.CrossCursor)
        super(CoqTableView, self).mouseMoveEvent(event)


class CoqTableModel(QtCore.QAbstractTableModel):
    """ Define a QAbstractTableModel class that stores the query results in a
    pandas DataFrame object. It provides the required methods so that they
    can be shown in the results view. """

    def __init__(self, df, session=None, parent=None, *args):
        super(CoqTableModel, self).__init__(parent, *args)
        self._parent = parent

        self.content = df[[x for x in df.columns
                           if not x.startswith("coquery_invisible")]]
        self.invisible_content = df[[x for x in df.columns
                                     if x.startswith("coquery_invisible")]]
        self.header = self.content.columns
        self._session = session
        self._manager = managers.get_manager(options.cfg.MODE,
                                             session.Resource.name)
        self._align = []
        self._dtypes = []

        columns = self.header
        if len(columns) != len(columns.unique()):
            logging.warn("Duplicate column headers: {}".format(columns))
            columns = columns.unique()

        # prepare look-up lists that speed up data retrieval:
        for i, col in enumerate(columns):
            # remember dtype of columns:
            dtype = df[col].dropna().convert_dtypes().dtype
            self._dtypes.append(dtype)

            sorter = self._manager.get_sorter(col)

            # set right alignment for reverse sort, numeric data types, or
            # the right-hand context:
            if ((sorter and sorter.reverse)
                    or pd.api.types.is_numeric_dtype(dtype)
                    or col == "coq_context_left"):
                self._align.append(_right_align)
            else:
                # otherwise, left-align:
                self._align.append(_left_align)
        self.formatted = self.format_content(self.content)

    def flags(self, index):
        flags = super(CoqTableModel, self).flags(index)
        try:
            if self.content.columns[index.column()].startswith("coq_userdata"):
                editable = (get_toplevel_window()
                            .ui.aggregate_radio_list[0].isChecked())
                if editable:
                    return flags | QtCore.Qt.ItemIsEditable
        except IndexError:
            pass
        return flags

    def get_dtype(self, column):
        return self._dtypes[list(self.header).index(column)]

    def setData(self, index, value, role):
        col = self.content.columns[index.column()]
        row = self.content.index[index.row()]
        tab = self._session.data_table
        if (role == QtCore.Qt.EditRole and
                col.startswith("coq_userdata")):
            self.content[col][row] = value
            self.formatted[col][row] = value
            _id_column = "coquery_invisible_corpus_id"
            corpus_id = self.invisible_content.iloc[index.row(_id_column)]
            which = tab.coquery_invisible_corpus_id == corpus_id
            tab[col][which] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    @staticmethod
    def format_content(source):
        """
        Create a data frame that contains the visual representations of the
        input data frame.

        This function is required for several reasons:
        - QTableView is very slow for data types that are not strings
        - Missing values need special treatment
        - Boolean and float columns require special formatting
        """
        df = pd.DataFrame(index=source.index)

        for col in source:
            val = source[col]
            dtype = val.dropna().convert_dtypes().dtype

            # copy invisible columns:
            if col.startswith("coquery_invisible"):
                df[col] = val
                continue

            # FIXME: the sign of G test statistic should not be handled
            # in the output!
            if col.startswith("statistics_g_test"):
                val = abs(val)

            if pd.api.types.is_numeric_dtype(dtype):
                if pd.api.types.is_integer_dtype(dtype):
                    # integers are just converted to strings
                    to_str_fnc = str
                else:
                    # floats use the float format string function
                    to_str_fnc = options.cfg.float_format.format

                val = map(lambda x: (to_str_fnc(x)
                                     if not pd.isna(x) else
                                     options.cfg.na_string),
                          val.values)

            elif pd.api.types.is_bool_dtype(dtype):
                # use bool substitute labels:
                val = map(lambda x: (["no", "yes"][x]
                                     if not pd.isna(x) else
                                     options.cfg.na_string),
                          val.values)
            else:
                # just a string
                val = val.fillna(options.cfg.na_string)
            df[col] = pd.Series(val)

        return df

    def data(self, index, role):
        """
        Return a representation of the data cell indexed by 'index', using
        the specified Qt role.

        Note that the foreground and background colors of the cells are
        handled by the delegate CoqResultCellDelegate().
        """

        # DisplayRole: return the content of the cell in the data frame:
        # ToolTipRole: also returns the cell content, but in a form suitable
        # for QHTML:
        ix = index.column()
        if role == QtCore.Qt.DisplayRole:
            return self.formatted.values[index.row()][ix]

        elif role == QtCore.Qt.EditRole:
            return self.formatted.values[index.row()][ix]

        # ToolTipRole: return the content as a tooltip:
        elif role == QtCore.Qt.ToolTipRole:
            formatted_val = self.formatted.values[index.row()][ix]
            return "<div>{}</div>".format(escape(formatted_val))

        # TextAlignmentRole: return the alignment of the column:
        elif role == QtCore.Qt.TextAlignmentRole:
            return self._align[ix]

        elif role == QtCore.Qt.UserRole:
            # The UserRole is used when clicking on a cell in the results
            # table. It is handled differently depending on the query type
            # that produced the table.
            manager = self._session.get_manager()
            if isinstance(manager, managers.ContrastMatrix):
                return manager.get_cell_content(
                    index,
                    self._session.output_object,
                    self._session)

        elif role == QtCore.Qt.UserRole + 1:
            # This role is used to retrieve the G test statistics
            return self.content.values[index.row()][ix]

        return None

    def headerData(self, index, orientation, role):
        """
        Return the header at the given index, taking the sorting settings
        into account.
        """

        # Return row names?
        if orientation == QtCore.Qt.Vertical:
            if role == QtCore.Qt.DisplayRole:
                val = self.content.index[index]
                return (utf8(val + 1)
                        if isinstance(val, (np.integer, int))
                        else utf8(val))
            else:
                return None

        # Get header string:
        column = self.header[index]

        if role == QtCore.Qt.DisplayRole:
            display_name = self._session.translate_header(column)
            tag_list = []
            # Add sorting order number if more than one sorting columns have
            # been selected:
            sorter = self._manager.get_sorter(column)
            if sorter:
                if len(self._manager.sorters) > 1:
                    tag_list.append("{}".format(sorter.position + 1))
                if sorter.reverse:
                    tag_list.append("rev")

            return "{}{}".format(
                    display_name,
                    ["", " ({}) ".format(", ".join(tag_list))][bool(tag_list)])

        # Get header decoration (i.e. the sorting arrows)?
        elif role == QtCore.Qt.DecorationRole:
            sorter = self._manager.get_sorter(column)
            if sorter:
                icon = {(False, False): "Descending Sorting",
                        (True, False): "Ascending Sorting",
                        (False, True): "Descending Reverse Sorting",
                        (True, True): "Ascending Reverse Sorting"}[
                            sorter.ascending,
                            sorter.reverse]
                return get_toplevel_window().get_icon(icon)
            else:
                return None
        else:
            return None

    def rowCount(self, parent=None):
        """ Return the number of rows. """
        return len(self.content)

    def columnCount(self, parent=None):
        """ Return the number of columns. """
        return self.content.columns.size


class CoqHiddenTableModel(CoqTableModel):
    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            return self.formatted.values[index.row()][index.column()]
        else:
            return super(CoqHiddenTableModel, self).data(index, role)


class CoqWidgetListView(QtWidgets.QListView):
    """
    Define a QListView class that conveniently handles widgets as
    representations of the items.

    Specifically, it passes changes in the view selection on to the widgets
    so that they can react to the changes, and vice versa. The slots
    toggleSelect() and changeSelect() are used for this.
    """
    def changeSelect(self, selected, deselected):
        """
        Pass changes in the selection to the widgets in the list.

        Specifically, the check state of widgets that have a setCheckState()
        method will be set to Checked if the widget is in the selection, and
        to Unchecked if the widget is not in the selection.
        """
        self.selectionModel().blockSignals(True)
        for selection_range in selected:
            for index in selection_range.indexes():
                widget = self.indexWidget(index)
                try:
                    widget.setCheckState(QtCore.Qt.Checked)
                except AttributeError:
                    pass
        for selection_range in deselected:
            for index in selection_range.indexes():
                widget = self.indexWidget(index)
                try:
                    widget.setCheckState(QtCore.Qt.Unchecked)
                except AttributeError:
                    pass
        self.selectionModel().blockSignals(False)

    def toggleSelect(self, item):
        """
        Toggle the selection state of the item.

        This slot can be used to react to signals emitted by the widgets in
        the list.
        """
        selection_model = self.selectionModel()
        index = item.index()
        if index:
            selection_model.select(index, selection_model.Toggle)

    def setModel(self, model):
        """
        Set the current model.

        This method connects the selectionChanged signal from the model to
        the changeSelect slot of the view. Also, for each item in the model
        that has a widget in its UserRole, that widget is set to be used in
        the view.
        """
        super(CoqWidgetListView, self).setModel(model)
        self.selectionModel().selectionChanged.connect(self.changeSelect)
