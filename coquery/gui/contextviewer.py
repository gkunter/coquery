# -*- coding: utf-8 -*-
"""
contextviewer.py is part of Coquery.

Copyright (c) 2016-2019 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import division
from __future__ import unicode_literals

import os
try:
    import tgt
    use_tgt = True
except ImportError:
    use_tgt = False

from coquery import options
from coquery.unicode import utf8
from . import classes
from .threads import CoqThread
from .widgets.coqstaticbox import CoqStaticBox
from .pyqt_compat import QtCore, QtWidgets, QtGui, get_toplevel_window
from .ui.contextViewerUi import Ui_ContextView
from coquery.gui.app import get_icon


class ContextView(QtWidgets.QWidget):
    def __init__(self, resource, token_id, source_id, token_width,
                 icon=None, parent=None):

        super(ContextView, self).__init__(parent)

        self.resource = resource
        self.corpus = resource.corpus
        self.token_id = token_id
        self.source_id = source_id
        self.token_width = token_width
        self.context_thread = QtCore.QThread(self)
        self.rescheduled = False

        self.meta_data = get_toplevel_window().table_model.invisible_content

        self.ui = Ui_ContextView()
        self.ui.setupUi(self)
        self.ui.button_prev.setIcon(get_icon("Circled Chevron Left"))
        self.ui.button_next.setIcon(get_icon("Circled Chevron Right"))
        self.ui.progress_bar.hide()

        if icon:
            self.setWindowIcon(icon)

        self.ui.slider_context_width.setTracking(True)

        # Add clickable header
        self.ui.button_ids = classes.CoqDetailBox()
        self.ui.button_ids.clicked.connect(self.remember_state)
        self.ui.layout_main.insertWidget(0, self.ui.button_ids)
        self.ui.layout_meta = QtWidgets.QFormLayout(
            self.ui.button_ids.box)

        self.audio = None
        if not self.resource.audio_features:
            self.ui.tab_widget.removeTab(1)
            self.ui.tab_widget.tabBar().hide()

        words = options.settings.value("contextviewer_words", None)
        if words is not None:
            try:
                self.ui.spin_context_width.setValue(int(words))
                self.ui.slider_context_width.setValue(int(words))
            except ValueError:
                pass

        self.ui.spin_context_width.valueChanged.connect(self.spin_changed)
        self.ui.slider_context_width.valueChanged.connect(self.slider_changed)
        self.ui.button_next.clicked.connect(self.next_context)
        self.ui.button_prev.clicked.connect(self.previous_context)

        self.get_context()
        self.set_meta_data()

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

        self.ui.context_area.setStyleSheet(
            self.corpus.get_context_stylesheet())

    def set_meta_data(self):
        s = "{} – Token ID {}".format(self.resource.name, self.token_id)
        self.ui.button_ids.setText(s)
        self.ui.button_ids.setAlternativeText(s)

        # clear meta information layout:
        for i in reversed(range(self.ui.layout_meta.count())):
            self.ui.layout_meta.itemAt(i).widget().setParent(None)

        # fill meta information layout:
        lst = self.resource.get_origin_data(self.token_id)
        for table, fields in sorted(lst):
            self.add_source_label(table)
            for label in sorted(fields.keys()):
                if label not in self.resource.audio_features:
                    self.add_source_label(label, fields[label])
                else:
                    from coquery import sound
                    self.audio = sound.Sound(fields[label])

        self.ui.button_ids.update()

    def remember_state(self):
        options.settings.setValue("contextviewer_details",
                                  utf8(not self.ui.button_ids.isExpanded()))

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
        layout_row = self.ui.layout_meta.count()
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
        self.ui.layout_meta.setWidget(layout_row,
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
        self.ui.layout_meta.setWidget(layout_row,
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
            self.context_thread = CoqThread(self.retrieve_context,
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

        has_prev = self.lookup_row(self.token_id, self.meta_data, -1)
        has_next = self.lookup_row(self.token_id, self.meta_data, +1)
        self.ui.button_prev.setEnabled(has_prev is not None)
        self.ui.button_next.setEnabled(has_next is not None)

    @classmethod
    def lookup_row(cls, token_id, df, offset):
        """
        Look up that row that precedes or follows the row specified by token_id
        in the given data frame by the stated offset.
        """
        row = df[df["coquery_invisible_corpus_id"] == token_id]
        try:
            if offset < 0 and row.index.min() == 0:
                return None
            if offset > 0 and row.index.max() == df.index.max():
                return None
                offset = 0
            return df.loc[row.index + offset]
        except KeyError:
            return None

    def change_context(self, row):
        """
        Changes the current context to the given row from the results table.
        """
        if row is not None:
            row = row.iloc[0]
            self.token_id = int(row["coquery_invisible_corpus_id"])
            self.source_id = int(row["coquery_invisible_origin_id"])
            self.token_width = int(row["coquery_invisible_number_of_tokens"])
            self.get_context()
            self.set_meta_data()

    def previous_context(self):
        row = self.lookup_row(self.token_id, self.meta_data, -1)
        self.change_context(row)

    def next_context(self):
        row = self.lookup_row(self.token_id, self.meta_data, +1)
        self.change_context(row)

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

        styles = ["line-height: {}px".format(font.pointSize() * 1.85),
                  'font-family: "{}", Times, Serif'.format(font.family()),
                  "font-size: {}px".format(font.pointSize() * 1.25),
                  "font-style: {}".format(style),
                  "font-weight: {}".format(weight),
                  "font-strech: {}".format(stretch)]

        text = self.context["text"]

        if font.underline():
            text = "<u>{}</u>".format(text)
        if font.strikeOut():
            text = "<s>{}</s>".format(text)
        s = "<div style='{}'>{}</div>".format("; ".join(styles), text)
        self.ui.context_area.setText(s)

        self.ui.progress_bar.hide()

    def prepare_textgrid(self, df, offset):
        if not use_tgt:
            return None
        grid = tgt.TextGrid()
        tier = tgt.IntervalTier()
        tier.name = "Words"
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

    def __init__(self, resource, token_id, source_id, token_width,
                 icon=None, parent=None):
        super(ContextViewAudio, self).__init__(resource, token_id, source_id,
                                               token_width, icon=None,
                                               parent=None)
        if ContextViewAudio._run_first:
            s = "Initializing sound system.<br><br>Please wait..."
            title = "Initializing sound system – Coquery"
            msg_box = CoqStaticBox(title, s, parent=self)

        from .textgridview import CoqTextgridView

        self.ui.textgrid_area = CoqTextgridView(self.ui.tab_textgrid)
        self.ui.layout_audio_tab.insertWidget(0, self.ui.textgrid_area)
        self.ui.layout_audio_tab.setStretch(0, 1)

        if ContextViewAudio._run_first:
            msg_box.close()
            msg_box.hide()
            del msg_box
            ContextViewAudio._run_first = False

        self.ui.spin_dynamic_range.valueChanged.connect(
            self.ui.textgrid_area.change_dynamic_range)
        self.ui.spin_window_length.valueChanged.connect(
            self.ui.textgrid_area.change_window_length)

    def finalize_context(self):
        super(ContextViewAudio, self).finalize_context()
        audio = self.audio.extract_sound(self.context["start_time"],
                                         self.context["end_time"])
        textgrid = self.prepare_textgrid(self.context["df"],
                                         self.context["start_time"])

        self.ui.textgrid_area.setSound(audio)
        self.ui.textgrid_area.setTextgrid(textgrid)
        self.ui.textgrid_area.display(offset=self.context["start_time"])

        self.ui.progress_bar.hide()
