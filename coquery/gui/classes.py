# -*- coding: utf-8 -*-
"""
classes.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import

import logging
import numpy as np
import pandas as pd

from coquery import general
from coquery import options
from coquery import filters
from coquery import managers
from coquery.errors import *
from coquery.defines import *
from coquery.unicode import utf8

from .pyqt_compat import QtCore, QtGui, frameShadow, frameShape

from xml.sax.saxutils import escape


_left_align = int(QtCore.Qt.AlignLeft) | int(QtCore.Qt.AlignVCenter)
_right_align = int(QtCore.Qt.AlignRight) | int(QtCore.Qt.AlignVCenter)

class CoqThread(QtCore.QThread):
    taskStarted = QtCore.Signal()
    taskFinished = QtCore.Signal()
    taskException = QtCore.Signal(Exception)
    taskAbort = QtCore.Signal()

    def __init__(self, FUN, parent=None, *args, **kwargs):
        super(CoqThread, self).__init__(parent)
        self.FUN = FUN
        self.exiting = False
        self.args = args
        self.kwargs = kwargs

    def __del__(self):
        self.exiting = True
        try:
            self.wait()
        except RuntimeError:
            pass

    def setInterrupt(self, fun):
        self.INTERRUPT_FUN = fun

    def quit(self):
        self.INTERRUPT_FUN()
        super(CoqThread, self).quit()

    def run(self):
        self.taskStarted.emit()
        self.exiting = False
        result = None
        try:
            if options.cfg.profile:
                import cProfile
                profiler = cProfile.Profile()
                try:
                    result = profiler.runcall(self.FUN, *self.args, **self.kwargs)
                finally:
                    profiler.dump_stats(os.path.join(
                        general.get_home_dir(),
                        "thread{}.profile".format(hex(id(self)))))
            else:
                result = self.FUN(*self.args, **self.kwargs)
        except Exception as e:
            if self.parent:
                self.parent().exc_info = sys.exc_info()
                self.parent().exception = e
            self.taskException.emit(e)
            print("CoqThread.run():", e)
            raise e
        self.taskFinished.emit()
        return result


class CoqHorizontalHeader(QtGui.QHeaderView):
    sectionFinallyResized = QtCore.Signal(int, int, int)

    def __init__(self, *args, **kwargs):
        super(CoqHorizontalHeader, self).__init__(*args, **kwargs)
        self.button_pressed = False
        self._resizing = False
        self.sectionResized.connect(self.alert_resize)

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
            select = self.parent().selectionModel()
            model = self.model()
            top = model.index(0, ix, QtCore.QModelIndex())
            bottom = model.index(0, ix, QtCore.QModelIndex())
            selection = QtGui.QItemSelection(top, bottom)
            select.select(selection,
                            QtGui.QItemSelectionModel.Toggle |
                            QtGui.QItemSelectionModel.Columns)

        self.button_pressed = False

    def mousePressEvent(self, e):
        super(CoqHorizontalHeader, self).mousePressEvent(e)
        self.button_pressed = True


class CoqHelpBrowser(QtGui.QTextBrowser):
    def __init__(self, help_engine, *args, **kwargs):
        self.help_engine = help_engine
        super(CoqHelpBrowser, self).__init__(*args, **kwargs)

    def loadResource(self, resource_type, name):
        if name.scheme() == "qthelp":
            return self.help_engine.fileData(name)
        else:
            return super(CoqHelpBrowser, self).loadResource(resource_type, name)


class CoqInfoLabel(QtGui.QLabel):
    entered = QtCore.Signal()
    left = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super(CoqInfoLabel, self).__init__(*args, **kwargs)
        self.setCursor(QtCore.Qt.WhatsThisCursor)

        self.setText("")
        self.setPixmap(options.cfg.main_window.get_icon("sign-info").pixmap(
            QtCore.QSize(QtGui.QSpinBox().sizeHint().height(),
                         QtGui.QSpinBox().sizeHint().height())))


class CoqClickableLabel(QtGui.QLabel):
    clicked = QtCore.Signal()
    textChanged = QtCore.Signal()

    def mousePressEvent(self, ev):
        self.clicked.emit()

    def setText(self, s):
        super(CoqClickableLabel, self).setText(s)
        self.textChanged.emit()

class CoqSwitch(QtGui.QWidget):
    toggled = QtCore.Signal()

    def __init__(self, state=None, on="on", off="off", text="", *args, **kwargs):
        super(CoqSwitch, self).__init__(*args, **kwargs)

        self._layout = QtGui.QHBoxLayout(self)
        self._layout.setMargin(0)
        self._layout.setSpacing(-1)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self._frame = QtGui.QFrame()
        self._frame.setFrameShape(frameShape)
        self._frame.setFrameShadow(QtGui.QFrame.Sunken)
        #size = QtCore.QSize(
            #QtGui.QRadioButton().sizeHint().height() * 2,
            #QtGui.QRadioButton().sizeHint().height())
        #self._frame.setMaximumSize(size)
        self._layout.addWidget(self._frame)

        self._inner_layout = QtGui.QHBoxLayout(self._frame)
        self._inner_layout.setMargin(0)
        self._inner_layout.setSpacing(-1)
        self._inner_layout.setContentsMargins(0, 0, 0, 0)

        self._check = QtGui.QCheckBox(self)
        self._check.setObjectName("_check")
        self._inner_layout.addWidget(self._check)
        #self._slider = QtGui.QSlider(self)
        #self._slider.setOrientation(QtCore.Qt.Horizontal)
        #sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        #sizePolicy.setHorizontalStretch(0)
        #sizePolicy.setVerticalStretch(0)
        #self._slider.setSizePolicy(sizePolicy)
        #size = QtCore.QSize(
            #self._slider.sizeHint().height() * 1.61,
            #self._slider.sizeHint().height())
        #self._slider.setMaximumSize(size)
        #self._frame.setMaximumSize(size)

        #self._slider.setMaximum(1)
        #self._slider.setPageStep(1)
        #self._slider.setSliderPosition(0)
        #self._slider.setTickPosition(QtGui.QSlider.NoTicks)
        #self._slider.setTickInterval(1)
        #self._slider.setInvertedAppearance(True)
        #self._slider.setObjectName("_slider")

        #self._inner_layout.addWidget(self._slider)

        self._label = CoqClickableLabel(self)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        self._label.setSizePolicy(sizePolicy)
        self._label.setMinimumWidth(max(QtGui.QLabel(on).sizeHint().width(), QtGui.QLabel(off).sizeHint().width()))

        self._on_text = on
        self._off_text = off

        #self._layout.addWidget(self._label)
        self._inner_layout.addWidget(self._label)

        #grad0 = options.cfg.app.palette().color(QtGui.QPalette.Normal, QtGui.QPalette.Mid)
        #grad1 = options.cfg.app.palette().color(QtGui.QPalette.Normal, QtGui.QPalette.Button)
        #grad2 = options.cfg.app.palette().color(QtGui.QPalette.Normal, QtGui.QPalette.Light)
        #br = options.cfg.app.palette().color(QtGui.QPalette.Normal, QtGui.QPalette.Highlight)

        #self._style_handle = """QSlider#_slider::handle:horizontal {{
                #background: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                #stop:0 rgb({g0_r}, {g0_g}, {g0_b}),
                #stop:1 rgb({g1_r}, {g1_g}, {g1_b}));
                #border: 1px solid rgb({g1_r}, {g1_g}, {g1_b});
                #border-radius: {rad}px;
            #}}

            #QSlider#_slider::handle:horizontal:hover {{
                #background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                #stop:0 rgb({g2_r}, {g2_g}, {g2_b}),
                #stop:1 rgb({g1_r}, {g1_g}, {g1_b}));
                #border: 2px solid rgb({g2_r}, {g2_g}, {g2_b});
                #margin: -2px 0;
                #border-radius: {rad}px;
            #}}
        #""".format(
            #g0_r = grad0.red(), g0_g=grad0.green(), g0_b=grad0.blue(),
            #g1_r = grad1.red(), g1_g=grad1.green(), g1_b=grad1.blue(),
            #g2_r = grad2.red(), g2_g=grad2.green(), g2_b=grad2.blue(),
            #b_r = br.red(), b_g=br.green(), b_b=br.blue(),
            #rad=int(self._slider.sizeHint().height()*0.4))

        #self._style_handle = ""

        if not state:
            self.setOff()
        else:
            self.setOn()
        self._connect_signals()

    def _update(self):
        if self._on:
            self._check.setCheckState(QtCore.Qt.Checked)
            #self._slider.setValue(1)
            self._label.setText(self._on_text)

            #col = options.cfg.app.palette().color(QtGui.QPalette.Normal, QtGui.QPalette.Highlight)
            #s = """
            #{style_handle}

            #QSlider#_slider::add-page:horizontal {{
                #background: rgb({r}, {g}, {b});
            #}}

            #QSlider#_slider::sub-page:horizontal {{
                #background: rgb({r}, {g}, {b});
            #}}
            #"""
        else:
            #self._slider.setValue(0)
            self._check.setCheckState(QtCore.Qt.Unchecked)
            self._label.setText(self._off_text)

            #col = options.cfg.app.palette().color(QtGui.QPalette.Normal, QtGui.QPalette.Dark)
            #s = """
            #{style_handle}

            #QSlider#_slider::add-page:horizontal {{
                #background: rgb({r}, {g}, {b});
            #}}

            #QSlider#_slider::sub-page:horizontal {{
                #background: rgb({r}, {g}, {b});
            #}}
            #"""

        #self.setStyleSheet(s.format(
                #style_handle=self._style_handle,
                #r=col.red(), g=col.green(), b=col.blue()))

    def _connect_signals(self):
        #self._slider.valueChanged.connect(self.toggle)
        #self._slider.sliderReleased.connect(self._check_release)
        #self._slider.sliderPressed.connect(self._remember)
        self._check.stateChanged.connect(self.toggle)
        self._label.clicked.connect(self.toggle)

    def _disconnect_signals(self):
        #self._slider.valueChanged.disconnect(self.toggle)
        #self._slider.sliderReleased.disconnect(self._check_release)
        #self._slider.sliderPressed.disconnect(self._remember)
        self._check.stateChanged.disconnect(self.toggle)
        self._label.clicked.disconnect(self.toggle)

    #def _remember(self):
        #self._old_pos = int(self._slider.value())

    #def _check_release(self):
        #if int(self._slider.value()) == self._old_pos:
            #self.toggle()

    def toggle(self):
        self._disconnect_signals()
        self._on = not self._on
        self._update()
        self.toggled.emit()
        self._connect_signals()

    def isOn(self):
        return self._on

    def isOff(self):
        return not self._on

    def setOn(self):
        self._on = True
        self._update()

    def setOff(self):
        self._on = False
        self._update()


class CoqExclusiveGroup(object):
    def __init__(self, l):
        self._widget_list = [x for x in l if hasattr(x, "toggled")]
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


class CoqGroupBox(QtGui.QGroupBox):
    """
    """

    style_opened = """
        CoqGroupBox {{
            font: {title_weight};
            background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 {button_button}, stop: 1 {button_midlight});
            border: 1px solid gray;
            border-radius: 2px;
            border-style: inset;
            margin-top: {header_size};
        }}

        CoqGroupBox::title {{
            font: {title_weight};

            background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 {button_midlight}, stop: 1 {button_button});
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
                                            stop: 0 {button_button}, stop: 1 {button_midlight});
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

    toggled = QtCore.Signal(QtGui.QWidget)

    def set_style(self, **kwargs):
        if self.isChecked():
            s = self.style_opened
        else:
            s = self.style_closed

        icon_size = QtGui.QPushButton().sizeHint().height() - 6
        header_size = icon_size + 1
        pad = 10
        if "title_weight" not in kwargs:
            kwargs["title_weight"] = "normal"
        s = s.format(path=os.path.join(options.cfg.base_path, "icons", "small-n-flat", "PNG"),
                    sign_up="sign-minimize.png",
                    sign_down="sign-maximize.png",
                    icon_size=icon_size, header_size=header_size,
                    pad_right=pad,
                    button_light=options.cfg.app.palette().color(QtGui.QPalette.Light).name(),
                    button_midlight=options.cfg.app.palette().color(QtGui.QPalette.Midlight).name(),
                    button_button=options.cfg.app.palette().color(QtGui.QPalette.Button).name(),
                    button_mid=options.cfg.app.palette().color(QtGui.QPalette.Mid).name(),
                    button_dark=options.cfg.app.palette().color(QtGui.QPalette.Dark).name(),
                    box_light=options.cfg.app.palette().color(QtGui.QPalette.Window).name(),
                    box_dark=options.cfg.app.palette().color(QtGui.QPalette.Window).name(),
                    focus=options.cfg.app.palette().color(QtGui.QPalette.Highlight).name(),
                    **kwargs)
        self.setStyleSheet(s)

    def __init__(self, *args, **kwargs):
        super(CoqGroupBox, self).__init__(*args, **kwargs)
        self._text = ""
        self._alternative = None
        self.clicked.connect(self.setChecked)
        self.setStyleSheet(self.style_opened)

    def setTitle(self, text, *args, **kwargs):
        super(CoqGroupBox, self).setTitle(text, *args, **kwargs)
        self._text = text
        if self._alternative is "":
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
                if isinstance(item, QtGui.QWidgetItem):
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
                if isinstance(item, QtGui.QWidgetItem):
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


class CoqDetailBox(QtGui.QWidget):
    """
    Define a QLayout class that has the QPushButton 'header' as a clickable
    header, and a QFrame 'box' which can show any content in an exapnding box
    below the button.
    """
    clicked = QtCore.Signal(QtGui.QWidget)

    def __init__(self, text="", box=None, alternative=None, *args, **kwargs):
        if isinstance(text, QtGui.QWidget):
            if args:
                args = tuple(list(args).insert(0, text))
            else:
                args = tuple([text])
            text = ""
        super(CoqDetailBox, self).__init__(*args, **kwargs)

        if not box:
            self.box = QtGui.QFrame(self)
        else:
            self.box = box

        self.frame = QtGui.QFrame(self)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(frameShape)
        self.frame.setFrameShadow(frameShadow)

        self.header_layout = QtGui.QHBoxLayout()

        self.header = QtGui.QPushButton(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.header.sizePolicy().hasHeightForWidth())
        self.header.setSizePolicy(sizePolicy)
        self.header.setStyleSheet("text-align: left; padding: 4px; padding-left: 1px;")
        self.header.clicked.connect(self.onClick)
        self.header_layout.addWidget(self.header)

        self.verticalLayout_2 = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.addItem(self.header_layout)
        self.verticalLayout_2.addWidget(self.box)

        self.verticalLayout = QtGui.QVBoxLayout(self)
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
        self.update()

    def update(self):
        try:
            up = options.cfg.main_window.get_icon("Up Squared")
            down = options.cfg.main_window.get_icon("Down Squared")
        except AttributeError:
            up = None
            down = None
        if self._expanded:
            self.box.show()
            self.header.setFlat(False)
            self.header.setText(self._alternative)
            icon = up
        else:
            try:
                self.header.setText(self._text)
                self.box.hide()
            except RuntimeError:
                # The box may have been deleted already, which raises a
                # harmless RuntimeError
                pass
            self.header.setFlat(True)
            icon = down
        if icon:
            self.header.setIcon(icon)

    def setExpanded(self, b):
        self._expanded = b
        self.update()

    def isExpanded(self):
        return self._expanded


class CoqSpinner(QtGui.QWidget):
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
        anim = QtGui.QMovie(os.path.join(options.cfg.base_path, "icons", "progress_{0}x{0}.gif".format(opt_size)))
        anim.setScaledSize(QtCore.QSize(size, size))
        return anim

    def __init__(self, size=None, *args, **kwargs):
        super(CoqSpinner, self).__init__(*args, **kwargs)
        self._layout = QtGui.QHBoxLayout(self)
        self._label = QtGui.QLabel()
        self._layout.setSpacing(0)
        self._layout.setMargin(0)
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


class CoqListItem(QtGui.QListWidgetItem):
    def __init__(self, *args, **kwargs):
        super(CoqListItem, self).__init__(*args, **kwargs)
        self._objectName = ""

    def setObjectName(self, s):
        self._objectName = s

    def objectName(self):
        return self._objectName


class CoqTableItem(QtGui.QTableWidgetItem):
    def __init__(self, *args, **kwargs):
        super(CoqTableItem, self).__init__(*args, **kwargs)
        self._objectName = ""

    def setObjectName(self, s):
        self._objectName = s

    def objectName(self):
        return self._objectName


class CoqTreeItem(QtGui.QTreeWidgetItem):
    """
    Define a tree element class that stores the output column options in
    the options tree.
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
        return self._link_by != None

    def setText(self, column, text, *args):
        text = utf8(text)
        feature = utf8(self.objectName())
        if feature.endswith("_table"):
            self.setToolTip(column, "Corpus table: {}".format(text))
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
        child_states = set([])
        for child in [self.child(i) for i in range(self.childCount())]:
            child_states.add(child.checkState(column))
        return len(child_states) == 1

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

        if check_state == QtCore.Qt.PartiallyChecked:
            # do not propagate a partially checked state
            return

        if utf8(self._objectName).endswith("_table") and check_state:
            self.setExpanded(True)

        # propagate check state to children:
        for child in [self.child(i) for i in range(self.childCount())]:
            if not isinstance(child, CoqTreeLinkItem):
                child.setCheckState(column, check_state)
        # adjust check state of parent, but not if linked:
        if self.parent() and not self._link_by:
            if not self.parent().check_children():
                self.parent().setCheckState(column, QtCore.Qt.PartiallyChecked)
            else:
                self.parent().setCheckState(column, check_state)
            if expand:
                if self.parent().checkState(column) in (QtCore.Qt.PartiallyChecked, QtCore.Qt.Checked):
                    self.parent().setExpanded(True)


class CoqTreeLinkItem(CoqTreeItem):
    """
    Define a CoqTreeItem class that represents a linked table.
    """
    def setLink(self, link):
        self._link_by = link
        self.link = link

    def setText(self, column, text, *args):
        super(CoqTreeLinkItem, self).setText(column, text)
        #self.setToolTip(column, "External table: {}\nLinked by: {}".format(text, self.link.feature_name))


class CoqTreeWidget(QtGui.QTreeWidget):
    """
    Define a tree widget that stores the available output columns in a tree
    with check boxes for each variable.
    """
    addLink = QtCore.Signal(CoqTreeItem)
    addFunction = QtCore.Signal(CoqTreeItem)
    removeItem = QtCore.Signal(CoqTreeItem)

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

        for root in [self.topLevelItem(i) for i in range(self.topLevelItemCount())]:
            for child in [root.child(i) for i in range(root.childCount())]:
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
                if state == QtCore.Qt.Unchecked and object_name in options.cfg.group_columns:
                    item.setCheckState(column, QtCore.Qt.PartiallyChecked)
                else:
                    item.setCheckState(column, state)

                if state == QtCore.Qt.Checked:
                    item.parent().setExpanded(True)
                self.update(item, column)
            for child in [item.child(i) for i in range(item.childCount())]:
                _check_state(child, object_name, state, column)

        if type(state) != QtCore.Qt.CheckState:
            if state:
                state = QtCore.Qt.Checked
            else:
                state = QtCore.Qt.Unchecked

        for root in [self.topLevelItem(i) for i in range(self.topLevelItemCount())]:
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

            for child in [root.child(i) for i in
                            range(root.childCount())]:
                _check_state(child, object_name, state, column)

    def getCheckState(self, object_name):
        for root in [self.topLevelItem(i) for i in range(self.topLevelItemCount())]:
            for child in [root.child(i) for i in range(root.childCount())]:
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
        for root in [self.topLevelItem(i) for i in range(self.topLevelItemCount())]:
            for child in [root.child(i) for i in range(root.childCount())]:
                if child.checkState(column) == QtCore.Qt.Checked:
                    check_list.append(utf8(child._objectName))
        return check_list


class LogTableModel(QtCore.QAbstractTableModel):
    """
    Define a QAbstractTableModel class that stores logging messages.
    """
    def __init__(self, parent, *args):
        super(LogTableModel, self).__init__(parent, *args)
        try:
            self.content = options.cfg.gui_logger.log_data
        except AttributeError:
            self.content = []
        self.header = ["Date", "Time", "Level", "Message"]

    def data(self, index, role):
        if not index.isValid():
            return None
        row = index.row()
        column = index.column()

        record = self.content[row]
        if role == QtCore.Qt.DisplayRole:
            if column == 0:
                return record.asctime.split()[0]
            elif column == 1:
                return record.asctime.split()[1]
            elif column == 2:
                return record.levelname
            elif column == 3:
                return record.message
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


class LogProxyModel(QtGui.QSortFilterProxyModel):
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
        regexp = QtCore.QRegExp(S, QtCore.Qt.CaseInsensitive, QtCore.QRegExp.RegExp)
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


class CoqTextEdit(QtGui.QTextEdit):
    """
    Defines a QTextEdit class that accepts dragged objects.
    """
    def __init__(self, *args):
        super(CoqTextEdit, self).__init__(*args)
        self.setAcceptDrops(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
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
        if "application/x-qabstractitemmodeldatalist" in e.mimeData().formats():
            label = e.mimeData().text()
            if label == "word_label":
                self.insertPlainText("*")
                e.setDropAction(QtCore.Qt.CopyAction)
                e.accept()
            elif label == "word_pos":
                self.insertPlainText(".[*]")
                e.setDropAction(QtCore.Qt.CopyAction)
                e.accept()
            elif label == "lemma_label":
                self.insertPlainText("[*]")
                e.setDropAction(QtCore.Qt.CopyAction)
                e.accept()
            elif label == "lemma_transcript":
                self.insertPlainText("[/*/]")
                e.setDropAction(QtCore.Qt.CopyAction)
                e.accept()
            elif label == "word_transcript":
                self.insertPlainText("/*/")
                e.setDropAction(QtCore.Qt.CopyAction)
                e.accept()
        elif e.mimeData().hasText():
            self.insertPlainText(e.mimeData().text())
            e.setDropAction(QtCore.Qt.CopyAction)
            e.accept()
        #x, y = map(int, mime.split(','))

        #if e.keyboardModifiers() & QtCore.Qt.ShiftModifier:
            ## copy
            ## so create a new button
            #button = Button('Button', self)
            ## move it to the position adjusted with the cursor position at drag
            #button.move(e.pos()-QtCore.QPoint(x, y))
            ## show it
            #button.show()
            ## store it
            #self.buttons.append(button)
            ## set the drop action as Copy
            #e.setDropAction(QtCore.Qt.CopyAction)
        #else:
            ## move
            ## so move the dragged button (i.e. event.source())
            #e.source().move(e.pos()-QtCore.QPoint(x, y))
            ## set the drop action as Move
            #e.setDropAction(QtCore.Qt.MoveAction)
        # tell the QDrag we accepted it
        e.accept()

    def setAcceptDrops(self, *args):
        super(CoqTextEdit, self).setAcceptDrops(*args)


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

        self.label = QtGui.QLabel(self)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setLineWidth(0)

        self.horizontalLayout.addWidget(self.label)
        self.close_button = QtGui.QPushButton(self)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.close_button.sizePolicy().hasHeightForWidth())
        self.close_button.setSizePolicy(sizePolicy)
        self.close_button.setFlat(True)

        self.horizontalLayout.addWidget(self.close_button)

        icon = options.cfg.main_window.get_icon("Delete")

        height = self.fontMetrics().height()
        new_height = int(height * 0.75)
        self._style_font = "font-size: {}px".format(new_height)
        self._style_border_radius = "border-radius: {}px".format(int(new_height / 3))
        self.setBackground("lavender")
        self.close_button.setIcon(icon)
        self.close_button.setIconSize(QtCore.QSize(new_height, new_height))
        self.adjustSize()

    def setBackground(self, color):
        self._style_background = "background-color: {}".format(color)
        s = " ".join(["{};".format(x) for x in [self._style_background, self._style_border_radius, self._style_font]])
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

        self.parent().parent().parent().parent().dragTag(drag, self)

    def removeRequested(self):
        self.parent().parent().parent().parent().destroyTag(self)

    def validate(self):
        """ Validate the content, and return True if the content is valid,
        or False otherwise. """
        return True


class CoqListWidget(QtGui.QListWidget):
    itemDropped = QtCore.Signal(QtGui.QListWidgetItem)
    featureRemoved = QtCore.Signal(str)

    def __init__(self, *args, **kwargs):
        super(CoqListWidget, self).__init__(*args, **kwargs)
        self.columns = []

    def dropEvent(self, e):
        new_item = self.add_resource(e.mimeData().text())
        if new_item is not None:
            self.itemDropped.emit(new_item)
            e.acceptProposedAction()

    def clear(self):
        for _ in range(self.count()):
            self.takeItem(0)
        self.columns = []

    def find_resource(self, rc_feature):
        rc_feature = utf8(rc_feature)
        for i, (_, x) in enumerate(self.columns):
            if x == rc_feature:
                return i
        return None

    def get_item(self, rc_feature):
        rc_feature = utf8(rc_feature)
        for item, x in self.columns:
            if x == rc_feature:
                return item
        return None

    def get_feature(self, item):
        for x, rc_feature in self.columns:
            if x == item:
                return rc_feature
        return None

    def add_resource(self, rc_feature):
        rc_feature = utf8(rc_feature)
        if self.get_item(rc_feature) is not None:
            return
        label = getattr(options.cfg.main_window.resource, rc_feature)
        new_item = QtGui.QListWidgetItem(label)

        self.columns.append((new_item, rc_feature))
        self.addItem(new_item)
        self.setCurrentItem(new_item)
        self.itemActivated.emit(new_item)
        return new_item

    def insert_resource(self, i, rc_feature):
        rc_feature = utf8(rc_feature)
        if self.get_item(rc_feature) is not None:
            return
        label = getattr(options.cfg.main_window.resource, rc_feature)
        new_item = QtGui.QListWidgetItem(label)
        self.columns.insert(i, (new_item, rc_feature))
        self.insertItem(i, new_item)
        self.setCurrentItem(new_item)
        self.itemActivated.emit(new_item)
        try:
            new_item.setObjectName(rc_feature)
        except AttributeError as e:
            print(e)

    def remove_item(self, item):
        i = self.row(item)
        _, rc_feature = self.columns[i]
        self.takeItem(i)
        self.remove_resource(rc_feature)

    def remove_resource(self, rc_feature):
        rc_feature = utf8(rc_feature)
        i = self.find_resource(rc_feature)
        if i is not None:
            item, _ = self.columns.pop(i)
            self.takeItem(self.row(item))
            self.featureRemoved.emit(rc_feature)


class CoqTagEdit(QtGui.QLineEdit):
    """ Define a QLineEdit class that is used to enter query filters. """

    filter_examples = []

    def __init__(self, *args):
        super(CoqTagEdit, self).__init__(*args)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        #self.setStyleSheet(_fromUtf8('CoqTagEdit { border-radius: 5px; font: condensed; }'))

        if self.filter_examples:
            self.setPlaceholderText("e.g. {}".format(random.sample(self.filter_examples, 1)[0]))


class CoqTagContainer(QtGui.QWidget):
    def __init__(self, parent=None):
        super(CoqTagContainer, self).__init__(parent)
        self.layout = CoqFlowLayout(spacing=5)
        self.setLayout(self.layout)
        # make this widget take up all available space:
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)

    def add(self, item):
        self.layout.addWidget(item)


class CoqTagBox(QtGui.QWidget):
    """ Defines a QWidget class that contains and manages filter tags. """

    def __init__(self, parent=None, label="Filter"):
        super(CoqTagBox, self).__init__(parent)
        if not label.endswith(":"):
            label = label + ":"
        self._label = label
        self.setupUi()
        self.edit_tag.returnPressed.connect(lambda: self.addTag(utf8(self.edit_tag.text())))
        self.edit_tag.textEdited.connect(self.editTagText)
        # self._tagList stores the
        self._tagList = []
        self._filterList = []
        self._tagType = CoqTextTag
        self.edit_tag.setStyleSheet("CoqTagEdit { border-radius: 5px; font: condensed; }")

    def setTagType(self, tagType):
        self._tagType = tagType

    def setTagList(self, tagList):
        self._tagList = tagList

    def tagList(self):
        return self._tagList

    def setupUi(self):
        # make this widget take up all available space:
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)

        self.scroll_area = QtGui.QScrollArea()
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scroll_area.sizePolicy().hasHeightForWidth())
        self.scroll_area.setSizePolicy(sizePolicy)
        self.scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scroll_area.setWidgetResizable(True)

        self.scroll_content = QtGui.QWidget()
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scroll_content.sizePolicy().hasHeightForWidth())
        self.scroll_content.setSizePolicy(sizePolicy)

        self.cloud_area = CoqFlowLayout(spacing=5)
        self.scroll_content.setLayout(self.cloud_area)
        self.scroll_area.setWidget(self.scroll_content)

        self.edit_label = QtGui.QLabel(self._label)
        self.edit_tag = CoqTagEdit()

        self.edit_layout = QtGui.QHBoxLayout(spacing=5)
        self.edit_layout.addWidget(self.edit_label)
        self.edit_layout.addWidget(self.edit_tag)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edit_tag.sizePolicy().hasHeightForWidth())
        self.edit_tag.setSizePolicy(sizePolicy)

        self.layout = QtGui.QVBoxLayout(self)
        self.layout.addWidget(self.scroll_area)
        self.layout.addLayout(self.edit_layout)
        self.layout.setStretch(1, 0)

        self.setAcceptDrops(True)

        col = options.cfg.app.palette().color(QtGui.QPalette.Light)
        color = "{ background-color: rgb(%s, %s, %s) ; }" % (col.red(), col.green(), col.blue())
        S = 'QScrollArea {}'.format(color)
        self.scroll_content.setStyleSheet(S)

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

    def addTag(self, s):
        """ Add the current text as a query filter. """
        if not s:
            s = utf8(self.edit_tag.text())
        tag = self._tagType(self)

        tag.setContent(s)
        #if self.edit_tag.setStyleSheet(_fromUtf8('CoqTagEdit { border-radius: 5px; font: condensed; background-color: rgb(255, 255, 192); }'))
            #return

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
        for tag_label in [utf8(self.cloud_area.itemAt(x).widget().text()) for x in range(self.cloud_area.count())]:
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
        self.edit_tag.setStyleSheet("CoqTagEdit { border-radius: 5px; font: condensed; }")


class QueryFilterBox(CoqTagBox):
    """
    Define a CoqTagBox that manages query filters.
    """
    def destroyTag(self, tag):
        """
        Remove the tag from the tag cloud as well as the filter from the
        global filter list.
        """
        options.cfg.filter_list = [x for x in options.cfg.filter_list if x.text != utf8(tag.text())]
        super(QueryFilterBox, self).destroyTag(tag)

    def addTag(self, *args):
        """
        Add the tag to the tag cloud and the global filter list.
        """
        filt = filters.QueryFilter()
        try:
            filt.resource = self.resource
        except AttributeError:
            return
        try:
            if args:
                filt.text = args[0]
            else:
                filt.text = utf8(self.edit_tag.text())
        except InvalidFilterError:
            self.edit_tag.setStyleSheet('CoqTagEdit { border-radius: 5px; font: condensed;background-color: rgb(255, 255, 192); }')
        else:
            super(QueryFilterBox, self).addTag(filt.text)
            options.cfg.filter_list.append(filt)


class CoqTableView(QtGui.QTableView):
    resizeRow = QtCore.Signal(int, int)

    def __init__(self, *args, **kwargs):
        super(CoqTableView, self).__init__(*args, **kwargs)
        self.resizeRow.connect(self.setRowHeight)

    def setWordWrap(self, wrap, *args, **kwargs):
        super(CoqTableView, self).setWordWrap(wrap, *args, **kwargs)
        self._wrap_flag = int(QtCore.Qt.TextWordWrap) if bool(wrap) else 0

    def resizeRowsToContents(self, *args, **kwargs):
        def set_height(n, row):
            # determine the maximum required height for this row by
            # checking the height of each cell

            height = 0
            for col in row.index:
                height = max(height, metric.boundingRect(rects[col], self._wrap_flag, str(row[col])).height())
            if self.rowHeight(n) != height:
                self.resizeRow.emit(n, height)

        cols = [x for x in self.model().header if x in (("coq_context_left",
                                                         "coq_context_right",
                                                         "coq_context_string"))]
        if not cols:
            return

        df = self.model().content

        metric = self.fontMetrics()
        # create a dictionary of QRect, each as wide as a column in the
        # table
        rects = dict([
            (df.columns[i], QtCore.QRect(0, 0, self.columnWidth(i) - 2, 99999)) for i in range(self.horizontalHeader().count())])

        df[cols].apply(lambda x: set_height(np.where(df.index == x.name)[0], x),
                       axis="columns")

    def resizeColumnsToContents(self, *args, **kwargs):
        self.setVisible(False)
        super(CoqTableView, self).resizeColumnsToContents(*args, **kwargs)
        self.setVisible(True)


class CoqTableModel(QtCore.QAbstractTableModel):
    """ Define a QAbstractTableModel class that stores the query results in a
    pandas DataFrame object. It provides the required methods so that they
    can be shown in the results view. """

    def __init__(self, df, session=None, parent=None, *args):
        super(CoqTableModel, self).__init__(parent, *args)
        self._parent = parent

        self.content = df[[x for x in df.columns if not x.startswith("coquery_invisible")]]
        self.invisible_content = df[[x for x in df.columns if x.startswith("coquery_invisible")]]
        self.header = self.content.columns
        self._session = session
        self._manager = managers.get_manager(options.cfg.MODE, session.Resource.name)
        self._align = []
        self._dtypes = []
        self._hidden_columns = []
        # prepare look-up lists that speed up data retrieval:
        for i, col in enumerate(self.header):
            # remember hidden columns:
            if col in self._manager.hidden_columns:
                self._hidden_columns.append(i)

            # remember dtype of columns:
            self._dtypes.append(df.dtypes[col])

            sorter = self._manager.get_sorter(col)

            # set alignment:
            if sorter and sorter.reverse:
                # right-align columns with reverse sorting:
                self._align.append(_right_align)
            elif df.dtypes[col] in (int, float):
                # always right-align numeric columns:
                self._align.append(_right_align)
            elif col == "coq_context_left":
                # right-align the left context column:
                self._align.append(_right_align)
            else:
                # otherwise, left-align:
                self._align.append(_left_align)

        self.formatted = self.format_content(self.content)

    def get_dtype(self, column):
        return self._dtypes[list(self.header).index(column)]

    @staticmethod
    def format_content(source):
        df = pd.DataFrame(index=source.index)

        for col in source.columns:
            # copy invisible columns:
            if col.startswith("coquery_invisible"):
                df[col] = source[col]
                continue

            # special case: only NAs?
            if source[col].isnull().all():
                df[col] = source[col].astype(object)
                continue

            dtype = pd.Series(source[col].dropna().tolist()).dtype

            # float
            if dtype == float:
                # try to force floats to int:
                try:
                    as_int = source[col].astype(int, error_on_fail=False)
                except (ValueError, TypeError):
                    as_int = pd.Series(index=source[col].index)

                if all(as_int == source[col]):
                    df[col] = as_int.apply(lambda x: str(x) if (
                                                x is not None and
                                                x is not pd.np.nan) else None)
                else:
                    df[col] = source[col].apply(lambda x: options.cfg.float_format.format(x) if (
                                                x is not None and
                                                x is not pd.np.nan) else None)

            # int
            elif dtype == int:
                df[col] = source[col].apply(lambda x: str(x) if (
                                                x is not None and
                                                x is not pd.np.nan) else None)

            # bool
            elif dtype == bool:
                df[col] = source[col].apply(lambda x: ["no", "yes"][bool(x)] if (
                                                x is not None and
                                                x is not pd.np.nan) else None)
            # object
            elif dtype == object:
                df[col] = source[col]
            # unknown column type
            else:
                raise TypeError
        df = df.fillna(options.cfg.na_string)
        return df

    def is_visible(self, index):
        try:
            return index.column() not in self._hidden_columns

            row_vis = self._session.row_visibility[session.query_type]
            ix = self.content.index[index.row()]

            return (not self._manager.is_hidden_column(col) and
                row_vis[ix])
        except Exception as e:
            print("is_visible():", e)
            return False

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
        if role == QtCore.Qt.DisplayRole:
            ix = index.column()
            if ix not in self._hidden_columns:
                return self.formatted.values[index.row()][ix]
            else:
                return "[hidden]"

        # ToolTipRole: return the content as a tooltip:
        elif role == QtCore.Qt.ToolTipRole:
            ix = index.column()
            if ix not in self._hidden_columns:
                if self._dtypes[ix] == float:
                    return "<div>{}</div>".format(escape(options.cfg.float_format.format(self.content.values[index.row()][ix])))
                elif self._dtypes[ix] in (int, bool):
                    return "<div>{}</div>".format(self.content.values[index.row()][ix])
                else:
                    return "<div>{}</div>".format(escape(self.content.values[index.row()][ix]))
            else:
                return "[hidden]"

        # TextAlignmentRole: return the alignment of the column:
        elif role == QtCore.Qt.TextAlignmentRole:
            return self._align[index.column()]

        #elif role == QtCore.Qt.UserRole:
            ## The UserRole is used when clicking on a cell in the results
            ## table. It is handled differently depending on the query type
            ## that produced the table.
            #if session.query_type == queries.ContrastQuery:
                #return queries.ContrastQuery.get_cell_content(
                    #index,
                    #session.output_object,
                    #session)
        return None

    def headerData(self, index, orientation, role):
        """ Return the header at the given index, taking the sorting settings
        into account. """

        # Return row names?
        if orientation == QtCore.Qt.Vertical:
            if role == QtCore.Qt.DisplayRole:
                val = self.content.index[index]
                return utf8(val + 1) if isinstance(val, (np.integer, int)) else utf8(val)
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
            # no decorator for hidden columns:
            if column in self._manager.hidden_columns:
                return None

            sorter = self._manager.get_sorter(column)
            try:
                # add arrows as sorting direction indicators if necessary:
                if not sorter.ascending:
                    return options.cfg.main_window.get_icon("Descending Sorting")
                else:
                    return options.cfg.main_window.get_icon("Ascending Sorting")
            except AttributeError:
                return None

        return None

    def rowCount(self, parent=None):
        """ Return the number of rows. """
        return len(self.content)

    def columnCount(self, parent=None):
        """ Return the number of columns. """
        return self.content.columns.size


class CoqResultCellDelegate(QtGui.QStyledItemDelegate):
    fill = False

    def __init__(self, *args, **kwargs):
        super(CoqResultCellDelegate, self).__init__(*args, **kwargs)
        CoqResultCellDelegate._app = options.cfg.app
        CoqResultCellDelegate._table = options.cfg.main_window.table_model
        CoqResultCellDelegate.standard_bg = {
            True: [
                CoqResultCellDelegate._app.palette().color(
                    QtGui.QPalette.Normal, QtGui.QPalette.AlternateBase),
                CoqResultCellDelegate._app.palette().color(
                    QtGui.QPalette.Normal, QtGui.QPalette.Base)],
            False: [
                CoqResultCellDelegate._app.palette().color(
                    QtGui.QPalette.Disabled, QtGui.QPalette.AlternateBase),
                CoqResultCellDelegate._app.palette().color(
                    QtGui.QPalette.Disabled, QtGui.QPalette.Base)]}

        if not hasattr(CoqResultCellDelegate, "fg_color"):
            CoqResultCellDelegate.fg_color = None
        if not hasattr(CoqResultCellDelegate, "bg_color"):
            CoqResultCellDelegate.bg_color = None

    def get_foreground(self, option, index):
        if option.state & QtGui.QStyle.State_MouseOver:
            return self._app.palette().color(QtGui.QPalette().Link)
        elif option.state & QtGui.QStyle.State_Selected:
            return self._app.palette().color(QtGui.QPalette().HighlightedText)
        else:
            if self._table.is_visible(index):
                try:
                    return QtGui.QColor(options.cfg.row_color[self._table.content.index[index.row()]])
                except KeyError:
                    pass
                # return column color if specified:
                try:
                    return QtGui.QColor(options.cfg.column_color[self._table.header[index.column()]])
                except KeyError:
                    # return default color
                    return self.fg_color
            else:
                # return light grey for hidden cells:
                return self._app.palette().color(QtGui.QPalette.Disabled, QtGui.QPalette.Text)

    def get_background(self, option, index):
        if option.state & QtGui.QStyle.State_Selected:
            return self._app.palette().color(QtGui.QPalette().Highlight)
        else:
            if not self.bg_color:
                return self.standard_bg[self._table.is_visible(index)][index.row() & 1]
            else:
                return self.bg_color

    #def sizeHint(self, option, index):
        #rect = options.cfg.metrics.boundingRect(index.data(QtCore.Qt.DisplayRole))
        #return rect.adjusted(0, 0, 15, 0).size()

    def paint(self, painter, option, index):
        """
        Paint the results cell.

        The paint method of the cell delegates takes the representation
        from the table's :func:`data` method, using the DecorationRole role.
        On mouse-over, the cell is rendered like a clickable link.
        """
        content = index.data(QtCore.Qt.DisplayRole)
        if content == "" and not self.fill:
            return
        painter.save()

        # show content as a link on mouse-over:
        if option.state & QtGui.QStyle.State_MouseOver:
            font = painter.font()
            font.setUnderline(True)
            painter.setFont(font)

        fg = self.get_foreground(option, index)
        bg = self.get_background(option, index)
        if bg:
            painter.setBackground(bg)
            if option.state & QtGui.QStyle.State_Selected or self.fill:
                painter.fillRect(option.rect, bg)

        if fg:
            painter.setPen(QtGui.QPen(fg))

        try:
            if index.data(QtCore.Qt.TextAlignmentRole) == _left_align:
                painter.drawText(
                    option.rect.adjusted(2, 0, 2, 0),
                    _left_align | options.cfg.word_wrap,
                    content if isinstance(content, str) else str(content))
            else:
                painter.drawText(
                    option.rect.adjusted(-2, 0, -2, 0),
                    _right_align | options.cfg.word_wrap,
                    content if isinstance(content, str) else str(content))
        finally:
            painter.restore()


class CoqTotalDelegate(CoqResultCellDelegate):
    fill = True

    def __init__(self, *args, **kwargs):
        super(CoqTotalDelegate, self).__init__(*args, **kwargs)
        self.fg_color = self._app.palette().color(QtGui.QPalette.ButtonText)
        self.bg_color = self._app.palette().color(QtGui.QPalette.Button)


class CoqProbabilityDelegate(CoqResultCellDelegate):
    max_value = 1
    prefix = ""
    suffix = ""
    format_str = "{}{}{}"

    def paint(self, painter, option, index):
        """
        Paint the results cell.

        The paint method of the cell delegates takes the representation
        from the table's :func:`data` method, using the DecorationRole role.
        On mouse-over, the cell is rendered like a clickable link.
        """
        painter.save()

        try:
            value = float(index.data(QtCore.Qt.DisplayRole))
        except ValueError:
            print(1, value)
            painter.restore()
            return

        content = self.format_str.format(self.prefix, value, self.suffix)

        # show content as a link on mouse-over:
        if option.state & QtGui.QStyle.State_MouseOver:
            font = painter.font()
            font.setUnderline(True)
            painter.setFont(font)
        fg = self.get_foreground(option, index)
        bg = self.get_background(option, index)
        if bg:
            if option.state & QtGui.QStyle.State_Selected:
                painter.fillRect(option.rect, bg)
            elif value != 0:
                rect = QtCore.QRect(option.rect.topLeft(), option.rect.bottomRight())
                rect.setWidth(int(option.rect.width() * min(self.max_value, value)/self.max_value))
                painter.fillRect(rect, QtGui.QColor("lightgreen"))
        if fg:
            painter.setPen(QtGui.QPen(fg))

        try:
            if index.data(QtCore.Qt.TextAlignmentRole) == _left_align:
                painter.drawText(
                    option.rect.adjusted(2, 0, 2, 0),
                    _left_align | int(QtCore.Qt.TextWordWrap),
                    content)
            else:
                painter.drawText(
                    option.rect.adjusted(-2, 0, -2, 0),
                    _right_align | int(QtCore.Qt.TextWordWrap),
                    content)
        finally:
            painter.restore()

    #def get_background(self, option, index):
        #try:
            #value = float(index.data(QtCore.Qt.DisplayRole))
            #if  value > 1:
                #return QtGui.QColor("lightyellow")
            #else:
                #return super(CoqProbabilityDelegate, self).get_background(option, index)
        #except ValueError:
            #return super(CoqProbabilityDelegate, self).get_background(option, index)


class CoqPercentDelegate(CoqProbabilityDelegate):
    max_value = 100
    format_str = "{}{:3.1f}{}"
    suffix = "%"


class CoqLikelihoodDelegate(CoqResultCellDelegate):
    fill = True

    def get_background(self, option, index):
        if option.state & QtGui.QStyle.State_Selected:
            return self._app.palette().color(QtGui.QPalette().Highlight)
        else:
            try:
                value = float(index.data(QtCore.Qt.DisplayRole))
            except ValueError:
                value = 0
            if value > 3.841:
                return QtGui.QColor("lightblue")
            else:
                return self.bg_color


class CoqFlowLayout(QtGui.QLayout):
    """ Define a QLayout with flowing widgets that reorder automatically. """

    def __init__(self, parent=None, margin=0, spacing=-1):
        super(CoqFlowLayout, self).__init__(parent)
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
        super(CoqFlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        w = self.geometry().width()
        h = self.doLayout(QtCore.QRect(0, 0, w, 0), True)
        return QtCore.QSize(w + 2 * self.margin(), h + 2 * self.margin())

    def margin(self):
        return 0

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0
        spaceX = self.spacing()
        spaceY = self.spacing()

        for item in self.itemList:
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

logger = logging.getLogger(NAME)
