# -*- coding: utf-8 -*-
"""
settings.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

from coquery import options
from coquery.defines import AUTO_VISIBILITY, AUTO_APPLY_DEFAULT
from coquery.errors import remove_source_path, add_source_path
from coquery.unicode import utf8
from .pyqt_compat import QtWidgets, QtCore, get_toplevel_window
from .ui.settingsUi import Ui_SettingsDialog


class Settings(QtWidgets.QDialog):
    def __init__(self, _options, parent=None):
        super(Settings, self).__init__(parent)
        self._options = _options
        self.ui = Ui_SettingsDialog()
        self.ui.setupUi(self)
        #self.ui.check_ignore_punctuation.setEnabled(False)
        #self.ui.check_experimental.setEnabled(False)
        self.ui.edit_visualizer_path.setEnabled(False)
        self.ui.button_visualizer_path.setEnabled(False)

        if not options.cfg.use_cache:
            self.ui.edit_cache_path.setEnabled(False)
            self.ui.button_cache_path.setEnabled(False)

        for button, slot in (
                (self.ui.button_installer_path, self.select_installer_path),
                (self.ui.button_visualizer_path, self.select_visualizer_path),
                (self.ui.button_binary_path, self.select_binary_path),
                (self.ui.button_cache_path, self.select_cache_path),
                (self.ui.button_clear_cache, self.cache_button_clicked)):
            button.clicked.connect(slot)

        self._table_font = self._options.table_font
        self._context_font = self._options.context_font

        self.ui.label_sample_table.setFont(self._table_font)
        self.ui.label_sample_context.setFont(self._context_font)
        self.ui.label_sample_table.setText(self._table_font.family())
        self.ui.label_sample_context.setText(self._context_font.family())

        self.ui.button_table_font.clicked.connect(
            lambda: self.select_font(self.ui.label_sample_table))
        self.ui.button_context_font.clicked.connect(
            lambda: self.select_font(self.ui.label_sample_context))
        self.ui.button_reset_table.clicked.connect(
            lambda: self.reset_font(self.ui.label_sample_table))
        self.ui.button_reset_context.clicked.connect(
            lambda: self.reset_font(self.ui.label_sample_context))

        self.set_ui_options()

        try:
            self.resize(options.settings.value("settings_size"))
        except TypeError:
            pass

    def cache_button_clicked(self):
        if options.cfg.use_cache:
            if not options.cfg.query_cache.has_backup():
                options.cfg.query_cache.clear()
            else:
                options.cfg.query_cache.restore()

        self.setup_cache_button()

    def setup_cache_button(self):
        self.ui.button_clear_cache.setText("Clear cache")
        self.ui.button_clear_cache.setEnabled(True)
        icon = get_toplevel_window().get_icon("Delete")
        if options.cfg.use_cache:
            if options.cfg.query_cache.has_backup():
                self.ui.button_clear_cache.setText("Restore cache")
                icon = get_toplevel_window().get_icon("Recycling symbol")
            else:
                self.ui.button_clear_cache.setEnabled(
                    options.cfg.query_cache.size() > 0)
        self.ui.button_clear_cache.setIcon(icon)

    def closeEvent(self, event):
        options.settings.setValue("settings_size", self.size())

    def reset_font(self, label):
        font = QtWidgets.QLabel().font()
        label.setText(font.family())
        label.setFont(font)
        if label == self.ui.label_sample_table:
            self._table_font = font
        elif label == self.ui.label_sample_context:
            self._context_font = font

    def select_font(self, label):
        if label == self.ui.label_sample_table:
            font = self._table_font
        elif label == self.ui.label_sample_context:
            font = self._context_font
        new_font, accepted = QtWidgets.QFontDialog.getFont(font,
                                                           self.parent())
        if not accepted:
            return

        if label == self.ui.label_sample_table:
            self._table_font = new_font
        elif label == self.ui.label_sample_context:
            self._context_font = new_font
        #new_font.setPointSize(QtWidgets.QLabel().font().pointSize())
        #new_font.setStyle(QtWidgets.QFont.StyleNormal)
        #new_font.setWeight(QtWidgets.QFont.Normal)
        label.setFont(new_font)
        label.setText(new_font.family())

    def get_path(self, prev):
        name = QtWidgets.QFileDialog.getExistingDirectory(
            directory=prev,
            options=(QtWidgets.QFileDialog.ReadOnly |
                     QtWidgets.QFileDialog.ShowDirsOnly |
                     QtWidgets.QFileDialog.HideNameFilterDetails))
        if type(name) == tuple:
            name = name[0]
        return name

    def select_installer_path(self):
        name = self.get_path(self.ui.edit_installer_path.text())
        if name:
            self._options.custom_installer_path = name
            self.ui.edit_installer_path.setText(name)

    def select_visualizer_path(self):
        name = self.get_path(self.ui.edit_visualizer_path.text())
        if name:
            self._options.visualizer_path = name
            self.ui.edit_visualizer_path.setText(name)

    def select_cache_path(self):
        name = self.get_path(self.ui.edit_cache_path.text())
        if name:
            self._options.cache_path = name
            self.ui.edit_cache_path.setText(name)

    def select_binary_path(self):
        name = self.get_path(self.ui.edit_binary_path.text())
        if name:
            self._options.binary_path = name
            self.ui.edit_binary_path.setText(name)

    def set_ui_options(self):
        try:
            if not self._options.output_case_sensitive:
                try:
                    if self._options.output_to_lower:
                        self.ui.radio_output_case_lower.setChecked(True)
                    else:
                        self.ui.radio_output_case_upper.setChecked(True)
                except AttributeError:
                    self.ui.radio_output_case_lower.setChecked(True)
            else:
                self.ui.radio_output_case_leave.setChecked(True)
        except AttributeError:
            self.ui.radio_output_case_leave.setChecked(True)
        try:
            self.ui.check_ignore_case_query.setChecked(
                not self._options.query_case_sensitive)
        except AttributeError:
            pass
        try:
            self.ui.check_regular_expressions.setChecked(self._options.regexp)
        except AttributeError:
            pass
        #try:
            #self.ui.check_ignore_punctuation.setChecked(bool(self._options.ignore_punctuation))
        #except AttributeError:
            #pass
        #try:
            #self.ui.check_experimental.setChecked(bool(self._options.experimental))
        #except AttributeError:
            #pass
        try:
            self.ui.check_align_quantified.setChecked(
                bool(self._options.align_quantified))
        except AttributeError:
            pass
        try:
            self.ui.check_word_wrap.setChecked(bool(self._options.word_wrap))
        except AttributeError:
            pass
        try:
            self.ui.spin_digits.setValue(int(self._options.digits))
        except AttributeError:
            pass
        try:
            self.ui.edit_na_string.setText(self._options.na_string)
        except AttributeError:
            pass
        try:
            self.ui.check_drop_empty_queries.setChecked(
                bool(self._options.drop_on_na))
        except AttributeError:
            pass
        try:
            self.ui.check_remove_duplicates.setChecked(
                bool(self._options.drop_duplicates))
        except AttributeError:
            pass
        try:
            self.ui.edit_installer_path.setText(
                self._options.custom_installer_path)
        except AttributeError:
            pass
        try:
            self.ui.edit_binary_path.setText(
                self._options.binary_path)
        except AttributeError:
            pass
        try:
            self.ui.edit_visualizer_path.setText(
                self._options.visualizer_path)
        except AttributeError:
            pass
        try:
            self.ui.edit_cache_path.setText(self._options.cache_path)
        except AttributeError:
            pass
        try:
            self.ui.check_ask_on_quit.setChecked(
                bool(self._options.ask_on_quit))
        except AttributeError:
            pass
        try:
            self.ui.check_save_query_string.setChecked(
                bool(self._options.save_query_string))
        except AttributeError:
            pass
        try:
            self.ui.check_save_query_file.setChecked(
                bool(self._options.save_query_file))
        except AttributeError:
            pass

        try:
            if not options.use_cachetools:
                self.ui.widget_cache.setDisabled(True)
                self.ui.progress_used.hide()
                self.ui.label_10.hide()
            else:
                self.ui.spin_cache_size.setValue(
                    int(self._options.query_cache_size // (1024 * 1024)))
                self.ui.check_use_cache.setChecked(self._options.use_cache)
                self.ui.progress_used.setMaximum(
                    self.ui.spin_cache_size.value())
                self.ui.progress_used.setValue(
                    options.cfg.query_cache.size() // (1024*1024))
        except AttributeError:
            pass

        l = []
        for i in range(self.ui.list_auto_apply.count()):
            item = self.ui.list_auto_apply.item(i)
            if i in options.settings.value("settings_auto_apply",
                                           AUTO_APPLY_DEFAULT):
                state = QtCore.Qt.Checked
            else:
                state = QtCore.Qt.Unchecked
            item.setCheckState(state)


    def change_options(self):
        self._options.output_case_sensitive = (
            bool(self.ui.radio_output_case_leave.isChecked()))
        self._options.output_to_lower = (
            bool(self.ui.radio_output_case_lower.isChecked()))

        # Query options
        self._options.query_case_sensitive = (
            not bool(self.ui.check_ignore_case_query.isChecked()))
        self._options.regexp = (
            bool(self.ui.check_regular_expressions.isChecked()))
        self._options.drop_on_na = (
            bool(self.ui.check_drop_empty_queries.isChecked()))
        self._options.drop_duplicates = (
            bool(self.ui.check_remove_duplicates.isChecked()))
        self._options.use_cache = (
            bool(self.ui.check_use_cache.isChecked()))
        self._options.last_cache_size = (
            int(self.ui.spin_cache_size.value()))
        if self._options.use_cache:
            if self._options.query_cache_size != self._options.last_cache_size:
                self._options.query_cache_size = self._options.last_cache_size * 1024 * 1024
                self._options.query_cache.resize(self._options.query_cache_size)
            new_cache_path = utf8(self.ui.edit_cache_path.text())
            if new_cache_path != self._options.cache_path:
                try:
                    self._options.query_cache.move(new_cache_path)
                except Exception as e:
                    print(e)
                    raise e
                else:
                    self._options.cache_path = new_cache_path

        # Quitting options
        self._options.ask_on_quit = (
            bool(self.ui.check_ask_on_quit.isChecked()))
        self._options.save_query_file = (
            bool(self.ui.check_save_query_file.isChecked()))
        self._options.save_query_string = (
            bool(self.ui.check_save_query_string.isChecked()))

        self._options.digits = int(self.ui.spin_digits.value())
        self._options.align_quantified = (
            bool(self.ui.check_align_quantified.isChecked()))
        self._options.word_wrap = (
            bool([0, int(QtCore.Qt.TextWordWrap)]
                 [bool(self.ui.check_word_wrap.isChecked())]))
        self._options.float_format = "{:.%if}" % self._options.digits
        remove_source_path(self._options.custom_installer_path)
        self._options.custom_installer_path = (
            utf8(self.ui.edit_installer_path.text()))
        self._options.binary_path = utf8(self.ui.edit_binary_path.text())
        add_source_path(self._options.custom_installer_path)
        self._options.table_font = self._table_font
        self._options.context_font = self._context_font
        self._options.na_string = utf8(self.ui.edit_na_string.text())

        l = []
        for i in range(self.ui.list_auto_apply.count()):
            item = self.ui.list_auto_apply.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                l.append(i)
        options.settings.setValue("settings_auto_apply", l)

    @staticmethod
    def manage(options, parent=None):
        dialog = Settings(options, parent)
        result = dialog.exec_()
        if result == QtWidgets.QDialog.Accepted:
            dialog.change_options()
        return result

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
