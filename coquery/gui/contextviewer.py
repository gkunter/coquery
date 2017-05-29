# -*- coding: utf-8 -*-
"""
contextview.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import division
from __future__ import unicode_literals

import os
import tgt

from coquery import options
from coquery.unicode import utf8
from . import classes
from .pyqt_compat import QtCore, QtWidgets, QtGui
from .ui.contextViewerUi import Ui_ContextView


class ContextView(QtWidgets.QWidget):
    def __init__(self, corpus, token_id, source_id, token_width,
                 icon=None, parent=None):

        super(ContextView, self).__init__(parent)

        self.corpus = corpus
        self.token_id = token_id
        self.source_id = source_id
        self.token_width = token_width
        self.context_thread = QtCore.QThread(self)
        self.rescheduled = False

        self.ui = Ui_ContextView()
        self.ui.setupUi(self)
        self.ui.progress_bar.hide()

        if icon:
            self.setWindowIcon(icon)

        self.ui.slider_context_width.setTracking(True)

        # Add clickable header
        self.ui.button_ids = classes.CoqDetailBox(
            "{} – Token ID {}".format(corpus.resource.name, token_id))
        self.ui.button_ids.clicked.connect(
            lambda: options.settings.setValue(
                "contextviewer_details",
                utf8(not self.ui.button_ids.isExpanded())))
        self.ui.verticalLayout_3.insertWidget(0, self.ui.button_ids)
        self.ui.form_information = QtWidgets.QFormLayout(
            self.ui.button_ids.box)

        self.audio = None
        if not corpus.resource.audio_features:
            self.ui.tab_widget.removeTab(1)
            self.ui.tab_widget.tabBar().hide()

        L = self.corpus.get_origin_data(token_id)
        for table, fields in sorted(L):
            self.add_source_label(table)
            for label in sorted(fields.keys()):
                if label not in corpus.resource.audio_features:
                    self.add_source_label(label, fields[label])
                else:
                    from coquery import sound
                    self.audio = sound.Sound(fields[label])


        words = options.settings.value("contextviewer_words", None)
        if words is not None:
            try:
                self.ui.spin_context_width.setValue(int(words))
                self.ui.slider_context_width.setValue(int(words))
            except ValueError:
                pass

        self.ui.spin_context_width.valueChanged.connect(self.spin_changed)
        self.ui.slider_context_width.valueChanged.connect(self.slider_changed)

        self.get_context()

        try:
            self.resize(options.settings.value("contextviewer_size"))
        except TypeError:
            pass
        try:
            self.ui.slider_context_width(
                options.settings.value("contextviewer_words"))
        except TypeError:
            pass
        val = options.settings.value("contextviewer_details") != "False"
        if val:
            self.ui.button_ids.setExpanded(val)
        else:
            self.ui.button_ids.setExpanded(False)

        self.ui.context_area.setStyleSheet(corpus.get_context_stylesheet())

    def set_view(self, context):
        if context:
            self.ui.tab_widget.setCurrentIndex(0)
        else:
            self.ui.tab_widget.setCurrentIndex(1)

    def closeEvent(self, *args):
        options.settings.setValue("contextviewer_size", self.size())
        options.settings.setValue("contextviewer_words",
                                  self.ui.slider_context_width.value())

    def add_source_label(self, name, content=None):
        """
        Add the label 'name' with value 'content' to the context viewer.
        """
        layout_row = self.ui.form_information.count()
        self.ui.source_name = QtWidgets.QLabel(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                           QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.ui.source_name.sizePolicy().hasHeightForWidth())
        self.ui.source_name.setSizePolicy(sizePolicy)
        self.ui.source_name.setAlignment(
            QtCore.Qt.AlignRight |
            QtCore.Qt.AlignTop |
            QtCore.Qt.AlignTrailing)
        self.ui.source_name.setTextInteractionFlags(
            QtCore.Qt.LinksAccessibleByMouse |
            QtCore.Qt.TextSelectableByKeyboard |
            QtCore.Qt.TextSelectableByMouse)
        self.ui.form_information.setWidget(layout_row,
                                           QtWidgets.QFormLayout.LabelRole,
                                           self.ui.source_name)
        self.ui.source_content = QtWidgets.QLabel(self)
        self.ui.source_content.setWordWrap(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                           QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.ui.source_content.sizePolicy().hasHeightForWidth())
        self.ui.source_content.setSizePolicy(sizePolicy)
        self.ui.source_content.setAlignment(QtCore.Qt.AlignLeading |
                                            QtCore.Qt.AlignLeft |
                                            QtCore.Qt.AlignTop)
        self.ui.source_content.setTextInteractionFlags(
            QtCore.Qt.LinksAccessibleByMouse |
            QtCore.Qt.TextSelectableByKeyboard |
            QtCore.Qt.TextSelectableByMouse)
        self.ui.form_information.setWidget(layout_row,
                                           QtWidgets.QFormLayout.FieldRole,
                                           self.ui.source_content)

        if name:
            if content is None:
                name = "<b>{}</b>".format(name)
            else:
                name = utf8(name).strip()
                if not name.endswith(":"):
                    name += ":"
            self.ui.source_name.setText(name)

        if content:
            content = utf8(content).strip()
            if os.path.exists(content) or "://" in content:
                content = "<a href={0}>{0}</a>".format(content)
                self.ui.source_content.setOpenExternalLinks(True)
                self.ui.source_content.setTextInteractionFlags(
                    QtCore.Qt.TextBrowserInteraction)
            self.ui.source_content.setText(content)

    def spin_changed(self):
        self.ui.slider_context_width.blockSignals(True)
        self.ui.slider_context_width.setValue(
            self.ui.spin_context_width.value())
        self.get_context()
        self.ui.slider_context_width.blockSignals(False)
        options.settings.setValue("contextviewer_words",
                                  self.ui.slider_context_width.value())

    def slider_changed(self):
        self.ui.spin_context_width.blockSignals(True)
        self.ui.spin_context_width.setValue(
            self.ui.slider_context_width.value())
        self.get_context()
        self.ui.spin_context_width.blockSignals(False)
        options.settings.setValue("contextviewer_words",
                                  self.ui.slider_context_width.value())

    def get_context(self):
        if hasattr(self, "context_thread"):
            self.context_thread.quit()
        self.next_value = self.ui.slider_context_width.value()
        if not self.context_thread.isRunning():
            self.context_thread = classes.CoqThread(self.retrieve_context,
                                                    next_value=self.next_value,
                                                    parent=self)
            self.context_thread.taskFinished.connect(self.finalize_context)
            self.context_thread.taskException.connect(self.onException)
            self.ui.progress_bar.show()
            self.context_thread.start()
        else:
            print("rescheduled: ", self.rescheduled)
            if not self.rescheduled:
                self.rescheduled = True
                self.context_thread.taskFinished.disconnect(
                    self.finalize_context)
                self.context_thread.taskFinished.connect(self.get_context)

    def retrieve_context(self, next_value):
        try:
            context = self.corpus.get_rendered_context(
                self.token_id,
                self.source_id,
                self.token_width,
                next_value, self)
        except Exception as e:
            print("Exception in retrieve_context(): ", e)
            raise e
        if not self.context_thread.quitted:
            self.context = context

    def onException(self):
        self.ui.progress_bar.hide()
        QtWidgets.QMessageBox.critical(self,
                                       "Context error – Coquery",
                                       "Error retrieving context")

    def finalize_context(self):
        self.rescheduled = False
        font = options.cfg.context_font

        if int(font.style()) == int(QtGui.QFont.StyleItalic):
            style = "italic"
        elif int(font.style()) == int(QtGui.QFont.StyleOblique):
            style = "oblique"
        else:
            style = "normal"

        if font.stretch() == int(QtGui.QFont.UltraCondensed):
            stretch = "ultra-condensed"
        elif font.stretch() == int(QtGui.QFont.ExtraCondensed):
            stretch = "extra-condensed"
        elif font.stretch() == int(QtGui.QFont.Condensed):
            stretch = "condensed"
        elif font.stretch() == int(QtGui.QFont.SemiCondensed):
            stretch = "semi-condensed"
        elif font.stretch() == int(QtGui.QFont.Unstretched):
            stretch = "normal"
        elif font.stretch() == int(QtGui.QFont.SemiExpanded):
            stretch = "semi-expanded"
        elif font.stretch() == int(QtGui.QFont.Expanded):
            stretch = "expanded"
        elif font.stretch() == int(QtGui.QFont.ExtraExpanded):
            stretch = "extra-expanded"
        elif font.stretch() == int(QtGui.QFont.UltraExpanded):
            stretch = "ultra-expanded"
        else:
            stretch = "normal"

        weight = int(font.weight()) * 10

        styles = []

        styles.append('line-height: {}px'.format(font.pointSize() * 1.85))
        styles.append('font-family: "{}", Times, Serif'.format(
            font.family()))
        styles.append("font-size: {}px".format(font.pointSize() * 1.25))
        styles.append("font-style: {}".format(style))
        styles.append("font-weight: {}".format(weight))
        styles.append("font-strech: {}".format(stretch))

        text = self.context["text"]

        if font.underline():
            text = "<u>{}</u>".format(text)
        if font.strikeOut():
            text = "<s>{}</s>".format(text)
        s = "<div style='{}'>{}</div>".format("; ".join(styles), text)
        self.ui.context_area.setText(s)

        self.ui.progress_bar.hide()


    def prepare_textgrid(self, df, offset):
        grid = tgt.TextGrid()
        tier = tgt.IntervalTier()
        tier.name = "Context"
        grid.add_tier(tier)
        for x in df.index:
            start = df.loc[x]["coq_word_starttime_1"]
            end = df.loc[x]["coq_word_endtime_1"]
            text = df.loc[x]["coq_word_label_1"]
            interval = tgt.Interval(start - offset, end - offset)
            interval.text = text
            tier.add_interval(interval)
        return grid

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()


class ContextViewAudio(ContextView):
    _run_first = True

    def __init__(self, corpus, token_id, source_id, token_width,
                 icon=None, parent=None):

        super(ContextViewAudio, self).__init__(corpus, token_id, source_id,
                                               token_width, icon=None,
                                               parent=None)

        if ContextViewAudio._run_first:
            s = "Initializing sound system.<br><br>Please wait..."
            title = "Initializing sound system – Coquery"
            msg_box = classes.CoqStaticBox(title, s, parent=self)
            self.add_textgrid_area()
            msg_box.close()
            msg_box.hide()
            del msg_box
            ContextViewAudio._run_first = False

        self.add_textgrid_area()

        self.ui.spin_dynamic_range.valueChanged.connect(
            self.ui.textgrid_area.change_dynamic_range)
        self.ui.spin_window_length.valueChanged.connect(
            self.ui.textgrid_area.change_window_length)

    def add_textgrid_area(self):
        from .textgridview import CoqTextgridView
        try:
            del self.ui.textgrid_area
        except AttributeError:
            pass
        self.ui.textgrid_area = CoqTextgridView(self.ui.tab_textgrid)
        self.ui.layout_audio_tab.insertWidget(0, self.ui.textgrid_area)
        self.ui.layout_audio_tab.setStretch(0, 1)

    def finalize_context(self):
        super(ContextViewAudio, self).finalize_context()
        self.ui.progress_bar.show()
        audio = self.audio.extract_sound(self.context["start_time"],
                                            self.context["end_time"])
        textgrid = self.prepare_textgrid(self.context["df"],
                                            self.context["start_time"])
        try:
            self.ui.layout_audio_tab.removeWidget(self.ui.textgrid_area)
        except AttributeError:
            pass
        else:
            self.ui.textgrid_area.clear()
        self.add_textgrid_area()
        self.ui.textgrid_area.setSound(audio)
        self.ui.textgrid_area.setTextgrid(textgrid)
        self.ui.textgrid_area.display(offset=self.context["start_time"])

        self.ui.progress_bar.hide()
