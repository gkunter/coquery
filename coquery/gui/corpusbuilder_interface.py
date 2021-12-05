# -*- coding: utf-8 -*-
"""
corpusbuilder_interface.py is part of Coquery.

Copyright (c) 2016-2018 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
from __future__ import print_function

import argparse
import codecs
import re
import os
import sys
import zipfile

from coquery import options
from coquery.options import CSVOptions
from coquery.defines import (msg_install_abort,
                             msg_nltk_message_error,
                             msg_corpus_path_not_valid)
from coquery.errors import DependencyError
from coquery.unicode import utf8

from . import classes
from . import errorbox
from . import csvoptions
from .threads import CoqThread
from .pyqt_compat import QtCore, QtWidgets, QtGui, STYLE_WARN
from .ui.corpusInstallerUi import Ui_CorpusInstaller
from .ui.corpusTableUi import Ui_CorpusTable
from .ui.readPackageUi import Ui_PackageInstaller
from .namedtableoptions import NamedTableOptionsDialog


class MetaGui(QtWidgets.QDialog):
    button_label = "&Install"

    progressSet = QtCore.Signal(int, str)
    labelSet = QtCore.Signal(str)
    progressUpdate = QtCore.Signal(int)
    generalUpdate = QtCore.Signal(int)
    installStarted = QtCore.Signal()

    def __init__(self, builder_class, gui=None, parent=None):
        super(MetaGui, self).__init__(parent)
        self.state = None
        self._testing = False
        self._onefile = False
        self._meta_options = None
        self.builder_class = builder_class

        self.ui = gui()
        self.ui.setupUi(self)

        if hasattr(self.ui, "progress_box"):
            self.ui.progress_box.hide()

        if hasattr(self.ui, "buttonBox"):
            self.ui.yes_button = self.ui.buttonBox.button(
                self.ui.buttonBox.Yes)
            self.ui.yes_button.setText(self.button_label)
            self.ui.yes_button.clicked.connect(self.start_install)

        if hasattr(self.ui, "issue_label"):
            self.ui.issue_label.setText("")
            self.ui.corpus_name.setStyleSheet("")

        self.restore_settings()

        self.installStarted.connect(self.show_progress)
        self.progressSet.connect(self.set_progress)
        self.progressUpdate.connect(self.update_progress)
        self.generalUpdate.connect(self.general_update)
        self.labelSet.connect(self.set_label)

        if (hasattr(self.ui, "label_only_module") and
                hasattr(self.ui.label_only_module, "clicked")):
            self.ui.label_only_module.clicked.connect(
                self.ui.radio_only_module.click)
        if (hasattr(self.ui, "label_read_files") and
                hasattr(self.ui.label_read_files, "clicked")):
            self.ui.label_read_files.clicked.connect(
                self.ui.radio_read_files.click)

    def show_progress(self):
        if hasattr(self.ui, "progress_box"):
            self.ui.progress_box.show()
            self.ui.progress_box.update()

    def set_progress(self, vmax, s):
        if hasattr(self.ui, "progress_bar"):
            self.ui.progress_bar.setFormat(s)
            self.ui.progress_bar.setMaximum(vmax)
            self.ui.progress_bar.setValue(0)

    def update_progress(self, i):
        if hasattr(self.ui, "progress_bar"):
            self.ui.progress_bar.setValue(i)

    def general_update(self, i):
        if hasattr(self.ui, "progress_general"):
            self.ui.progress_general.setValue(i)

    def set_label(self, s):
        if hasattr(self.ui, "progress_bar"):
            self.ui.progress_bar.setFormat(s)

    def progress(self, pb, tup):
        if hasattr(self.ui, "progress_bar") and (pb == self.ui.progress_bar):
            i, n = tup
            if n is None:
                pb.setMaximum(i)
                pb.setValue(i)
                pb.setFormat("Chunk %v")
            else:
                pb.setMaximum(n)
                pb.setValue(i)
                pb.setFormat("%p%")
        elif hasattr(self.ui, "progress_general"):
            self.ui.progress_general.setFormat("")
            file_name, stage = tup
            val = pb.value()
            pb.setValue(val + 1)
            pb.setFormat("{} {}...".format(stage, file_name))

    def start_install(self):
        pass

    def restore_settings(self):
        try:
            self.resize(options.settings.value("corpusinstaller_size"))
        except TypeError:
            pass

        if isinstance(self, BuilderGui):
            target = "corpusinstaller_data_path"
        else:
            target = "corpusinstaller_corpus_source"

        if hasattr(self.ui, "input_path"):
            val = options.settings.value(target, "")
            self.ui.input_path.setText(utf8(val))

    def display(self):
        self.exec_()
        return self.state

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.reject()

    def accept(self):
        options.settings.setValue("corpusinstaller_size", self.size())
        if isinstance(self, BuilderGui):
            target = "corpusinstaller_data_path"
        else:
            target = "corpusinstaller_corpus_source"

        if hasattr(self.ui, "input_path"):
            options.settings.setValue(target, utf8(self.ui.input_path.text()))

        if hasattr(self.ui, "radio_read_files"):
            options.settings.setValue(
                "corpusinstaller_read_files",
                self.ui.radio_read_files.isChecked())

        return super(MetaGui, self).accept()

    def validate_name_not_empty(self, button):
        if hasattr(self.ui, "corpus_name"):
            if not utf8(self.ui.corpus_name.text()):
                self.ui.corpus_name.setStyleSheet(STYLE_WARN)
                if hasattr(self.ui, "issue_label"):
                    self.ui.issue_label.setText(
                        "The corpus name cannot be empty.")
                button.setEnabled(False)

    def validate_name_is_unique(self, button):
        if hasattr(self.ui, "corpus_name"):
            if (utf8(self.ui.corpus_name.text())
                    in options.cfg.current_connection.resources()):
                self.ui.corpus_name.setStyleSheet(STYLE_WARN)
                if hasattr(self.ui, "issue_label"):
                    self.ui.issue_label.setText(
                        "There is already another corpus with this name.")
                button.setEnabled(False)

    def validate_db_does_not_exist(self, button):
        if hasattr(self.ui, "corpus_name"):
            name = "coq_{}".format(utf8(self.ui.corpus_name.text()).lower())
            db_exists = options.cfg.current_connection.has_database(name)
            if db_exists:
                self.ui.corpus_name.setStyleSheet(STYLE_WARN)
                if hasattr(self.ui, "issue_label"):
                    self.ui.issue_label.setText(
                        "There is already another corpus that uses a database "
                        "with this name.")
                button.setEnabled(False)

    def validate_db_does_exist(self, button):
        if hasattr(self.ui, "corpus_name"):
            name = "coq_{}".format(utf8(self.ui.corpus_name.text()).lower())
            db_exists = options.cfg.current_connection.has_database(name)
            if not db_exists:
                self.ui.corpus_name.setStyleSheet(STYLE_WARN)
                if hasattr(self.ui, "issue_label"):
                    self.ui.issue_label.setText(
                        "There is no database that uses this name.")
                button.setEnabled(False)

    def validate_path_exists(self, button):
        if hasattr(self.ui, "input_path"):
            path = utf8(self.ui.input_path.text())
            if not path:
                button.setEnabled(False)

            if (not os.path.isdir(path)):
                self.ui.input_path.setStyleSheet(STYLE_WARN)
                if hasattr(self.ui, "issue_label"):
                    self.ui.issue_label.setText("Illegal data source path.")
                button.setEnabled(False)

    def validate_file_exists(self, button):
        if hasattr(self.ui, "input_path"):
            path = utf8(self.ui.input_path.text())
            if not path:
                button.setEnabled(False)

            if (not os.path.isfile(path)):
                self.ui.input_path.setStyleSheet(STYLE_WARN)
                if hasattr(self.ui, "issue_label"):
                    self.ui.issue_label.setText("Invalid data file.")
                button.setEnabled(False)

    def do_install(self):
        self.builder.build()

    def finish_install(self):
        yes = QtWidgets.QDialogButtonBox.Yes
        cancel = QtWidgets.QDialogButtonBox.Cancel
        ok = QtWidgets.QDialogButtonBox.Ok

        if self.state == "failed":
            S = "Installation of {} failed.".format(self.builder.name)
            if hasattr(self.ui, "progress_box"):
                self.ui.progress_box.hide()
            self.ui.buttonBox.button(yes).setEnabled(True)
            self.ui.widget_options.setEnabled(True)
        else:
            self.state = "finished"
            S = "Finished installing {}.".format(self.builder.name)

            if hasattr(self.ui, "label"):
                self.ui.label.setText("Installation complete.")

            if hasattr(self.ui, "progress_bar"):
                self.ui.progress_bar.hide()
            if hasattr(self.ui, "progress_general"):
                self.ui.progress_general.hide()

            self.ui.buttonBox.removeButton(self.ui.buttonBox.button(yes))
            self.ui.buttonBox.removeButton(self.ui.buttonBox.button(cancel))
            self.ui.buttonBox.addButton(ok)
            self.ui.buttonBox.button(ok).clicked.connect(self.accept)

            self.parent().showMessage(S)
            self.accept()

        self.parent().showMessage(S)

    def install_exception(self):
        self.state = "failed"
        if isinstance(self.exception, RuntimeError):
            QtWidgets.QMessageBox.critical(
                self, "Installation error – Coquery", str(self.exception))
        elif isinstance(self.exception, DependencyError):
            QtWidgets.QMessageBox.critical(
                self, "Missing Python module – Coquery", str(self.exception))
        else:
            errorbox.ErrorBox.show(self.exc_info, self, no_trace=False)

    def get_arguments_from_gui(self):
        namespace = argparse.Namespace()
        namespace.verbose = False
        namespace.use_nltk = False
        namespace.use_meta = False
        namespace.lookup_ngram = False
        namespace.metadata = False

        # FIXME: check if the following one-letter variables are still used
        # in CorpusBuilder.build().
        if (hasattr(self.ui, "radio_only_module") and
                self.ui.radio_only_module.isChecked()):
            namespace.o = False
            namespace.i = False
            namespace.l = False
            namespace.c = False
            namespace.w = True
            namespace.only_module = True
        else:
            namespace.w = True
            namespace.o = True
            namespace.i = True
            namespace.l = True
            namespace.c = True
            namespace.only_module = False

        if hasattr(self.ui, "input_path"):
            namespace.path = utf8(self.ui.input_path.text())

        namespace.db_name = self.builder_class.get_db_name()
        namespace.name = self.builder_class.get_name()
        namespace.encoding = self.builder_class.encoding

        return namespace


class InstallerGui(MetaGui):
    window_title = "Corpus installer – Coquery"

    showNLTKDownloader = QtCore.Signal(str)

    def __init__(self, builder_class, parent=None):
        super(InstallerGui, self).__init__(
            builder_class, gui=Ui_CorpusInstaller, parent=parent)

        self.ui.label_pos_tagging.hide()
        self.ui.use_pos_tagging.hide()

        self.ui.corpus_name.setText(builder_class.get_name())
        self.ui.corpus_name.setReadOnly(True)
        self.ui.button_metafile.hide()
        self.ui.label_metafile.hide()
        self.ui.check_use_metafile.hide()

        notes = builder_class.get_installation_note()
        if notes:
            self.ui.notes_box = classes.CoqDetailBox("Installation notes")
            self.ui.verticalLayout_5.insertWidget(2, self.ui.notes_box)

            self.ui.notes_label = QtWidgets.QLabel(notes)
            self.ui.notes_label.setWordWrap(True)
            self.ui.notes_label.setOpenExternalLinks(True)
            try:
                self.ui.notes_label.setBackgroundRole(
                    QtGui.QPalette.ColorRole.Base)
            except Exception as e:
                s = ("corpusbuilder_interface.InstallerGui.__init__(): Could "
                     "not set background color of installation note box")
                print(s)
                print(str(e))
            self.ui.notes_label.setTextInteractionFlags(
                QtCore.Qt.TextBrowserInteraction)

            self.ui.notes_scroll = QtWidgets.QScrollArea()
            self.ui.notes_scroll.setWidgetResizable(True)
            self.ui.notes_scroll.setWidget(self.ui.notes_label)

            self.ui.notes_box.replaceBox(self.ui.notes_scroll)

        self.ui.button_input_path.clicked.connect(self.select_path)
        self.ui.button_metafile.clicked.connect(self.select_metafile)
        self.ui.label_metafile.clicked.connect(self.select_metafile)

        self.ui.radio_read_files.toggled.connect(
            lambda x: self.activate_read(True))
        self.ui.radio_only_module.toggled.connect(
            lambda x: self.activate_read(False))
        self.ui.check_use_metafile.toggled.connect(self.toggle_use_metafile)

    def restore_settings(self):
        super(InstallerGui, self).restore_settings()

        self.ui.radio_read_files.blockSignals(True)
        self.ui.radio_only_module.blockSignals(True)

        val = options.settings.value("corpusinstaller_read_files", "true")
        self.activate_read(val == "true" or val is True)

        self.ui.check_use_metafile.setChecked(False)
        self.ui.label_metafile.setText("")
        meta = options.settings.value("corpusinstaller_metafile", None)
        if meta is not None:
            val = options.settings.value("corpusinstaller_use_metafile",
                                         "false")
            self.ui.check_use_metafile.setChecked(val == "true" or
                                                  val is True)
            self.ui.label_metafile.setText(utf8(meta))
            val = options.settings.value("corpusinstaller_metafile_column",
                                         None)
            self._metafile_column = val

        val = options.settings.value("corpusinstaller_use_nltk", "false")
        self.ui.use_pos_tagging.setChecked(val == "true" or val is True)

        if not options.cfg.experimental:
            self.ui.widget_n_gram.hide()
        else:
            self.ui.widget_n_gram.show()
            val = options.settings.value("corpusinstaller_use_ngram_table",
                                         "false")
            self.ui.check_n_gram.setChecked(val == "true")
            self.ui.spin_n.setValue(
                int(options.settings.value("corpusinstaller_n_gram_width",
                                           2)))

        self.ui.radio_read_files.blockSignals(False)
        self.ui.radio_only_module.blockSignals(False)

    def accept(self):
        options.settings.setValue("corpusinstaller_use_metafile",
                                  self.ui.check_use_metafile.isChecked())
        options.settings.setValue("corpusinstaller_use_nltk",
                                  self.ui.use_pos_tagging.isChecked())
        options.settings.setValue("corpusinstaller_use_ngram_table",
                                  self.ui.check_n_gram.isChecked())
        options.settings.setValue("corpusinstaller_ngram_width",
                                  self.ui.spin_n.value())
        return super(InstallerGui, self).accept()

    def validate_dialog(self, check_path=True):
        self.ui.input_path.setStyleSheet("")
        self.ui.yes_button.setEnabled(True)
        self.ui.issue_label.setText("")

        if self.ui.radio_read_files.isChecked() and check_path:
            path = utf8(self.ui.input_path.text())
            if not path:
                self.ui.yes_button.setEnabled(False)
                return
            if (not os.path.isdir(path)):
                self.ui.issue_label.setText("Illegal data source path.")
                self.ui.input_path.setStyleSheet(STYLE_WARN)
                self.ui.yes_button.setEnabled(False)
                return

    def select_path(self):
        path = utf8(self.ui.input_path.text())
        if not path:
            path = os.path.join(options.cfg.base_path, "texts", "alice")
        name = QtWidgets.QFileDialog.getExistingDirectory(
                directory=path,
                options=(QtWidgets.QFileDialog.DontUseNativeDialog |
                         QtWidgets.QFileDialog.ReadOnly))
        if type(name) == tuple:
            name = name[0]
        if name:
            self.ui.input_path.setText(name)
            self.validate_dialog()

    def select_metafile(self):
        dialog = NamedTableOptionsDialog(
            filename=utf8(self.ui.label_metafile.text()),
            default=self._meta_options,
            parent=self,
            icon=options.cfg.icon)

        dialog.ui.group_mappings.setTitle("Set filename column")
        dialog.add_required_mapping("filename")
        dialog.set_mappings([("Filename", "filename")])
        result = dialog.exec_()

        if result:
            self._meta_options = result
            self._metafile_column = result.mapping["filename"]
            self.ui.label_metafile.setText(result.file_name)
            self.ui.check_use_metafile.setChecked(True)
            self.validate_dialog()

    def toggle_use_metafile(self):
        self.ui.check_use_metafile.blockSignals(True)
        if not self.ui.check_use_metafile.isChecked():
            self.ui.label_metafile.setText("")
        elif self.ui.label_metafile.text() == "":
            self.select_metafile()
            if self.ui.label_metafile.text() == "":
                self.ui.check_use_metafile.setChecked(False)
        self.ui.check_use_metafile.blockSignals(False)

    def activate_read(self, activate):
        self.ui.radio_read_files.blockSignals(True)
        self.ui.radio_only_module.blockSignals(True)
        self.ui.radio_read_files.setChecked(activate)
        self.ui.radio_only_module.setChecked(not activate)
        self.ui.widget_read_files.setEnabled(activate)
        self.validate_dialog()
        self.ui.radio_read_files.blockSignals(False)
        self.ui.radio_only_module.blockSignals(False)

    def reject(self):
        try:
            if self.state == "finished":
                self.accept()
            elif self.install_thread:
                response = QtWidgets.QMessageBox.warning(
                    self,
                    "Aborting installation",
                    msg_install_abort,
                    QtWidgets.QMessageBox.No,
                    QtWidgets.QMessageBox.Yes)
                if response:
                    self.install_thread.quit()
                    super(InstallerGui, self).reject()
        except AttributeError:
            super(InstallerGui, self).reject()

    def check_input(self):
        if self.ui.radio_only_module.isChecked():
            self.ui.input_path.setStyleSheet('')
            self.ui.yes_button.setEnabled(True)
        else:
            path = str(self.ui.input_path.text())
            if os.path.isdir(path):
                self.ui.input_path.setStyleSheet('')
                self.ui.yes_button.setEnabled(True)
            else:
                self.ui.input_path.setStyleSheet(STYLE_WARN)
                self.ui.yes_button.setEnabled(False)

    def start_install(self):
        """
        Launches the installation.

        This method starts a new thread that runs the do_install() method.

        If this is a full install, i.e. the data base containing the
        corpus is to be created, a call to validate_files() is made first
        to check whether the input path is valid. The thread is only
        started if the path is valid, or if the user decides to ignore
        the invalid path.
        """

        if self.ui.radio_read_files.isChecked():
            lst = self.builder_class.get_file_list(
                str(self.ui.input_path.text()),
                self.builder_class.file_filter)
            try:
                self.builder_class.validate_files(lst)
            except RuntimeError as e:
                reply = QtWidgets.QMessageBox.question(
                    None, "Corpus path not valid – Coquery",
                    msg_corpus_path_not_valid.format(e),
                    (QtWidgets.QMessageBox.Ignore |
                     QtWidgets.QMessageBox.Discard))
                if reply == QtWidgets.QMessageBox.Discard:
                    return

        self.installStarted.emit()

        if hasattr(self, "_nltk_tagging"):
            pos = self.ui.use_pos_tagging.isChecked()
            self.builder = self.builder_class(pos=pos, gui=self)
        else:
            self.builder = self.builder_class(gui=self)

        self.builder.arguments = self.get_arguments_from_gui()
        self.builder.name = self.builder.arguments.name

        self.ui.yes_button.setEnabled(False)
        self.ui.widget_options.setEnabled(False)

        self.install_thread = CoqThread(self.do_install, self)
        self.install_thread.setInterrupt(self.builder.interrupt)
        self.install_thread.taskFinished.connect(self.finish_install)
        self.install_thread.taskException.connect(self.install_exception)
        self.install_thread.start()

    def get_arguments_from_gui(self):
        namespace = super(InstallerGui, self).get_arguments_from_gui()

        namespace.metadata = utf8(self.ui.label_metafile.text())
        if hasattr(self, "_metafile_column"):
            namespace.metadata_column = self._metafile_column
        if hasattr(self, "_meta_options"):
            namespace.metaoptions = self._meta_options

        if self.ui.radio_read_files.isChecked():
            if (self.ui.check_n_gram.checkState() and
                    options.cfg.experimental):
                namespace.lookup_ngram = True
                namespace.ngram_width = int(self.ui.spin_n.value())

        return namespace


class BuilderGui(InstallerGui):
    button_label = "&Build"
    window_title = "Corpus builder – Coquery"
    nltk_label = "Use NLTK for part-of-speech tagging and lemmatization"

    def __init__(self, builder_class, onefile=False, parent=None):
        super(BuilderGui, self).__init__(builder_class, parent)

        self._nltk_lemmatize = False
        self._nltk_tokenize = False
        self._nltk_tagging = False
        self._testing = False
        self._onefile = onefile

        self._meta_options = CSVOptions(
            sep=options.cfg.input_separator,
            header=options.cfg.file_has_headers,
            quote_char=options.cfg.quote_char,
            skip_lines=options.cfg.skip_lines,
            encoding=options.cfg.input_encoding,
            selected_column=None)
        self._metafile_column = None

        if self._onefile:
            self.ui.label_read_files.setText(
                "Build new corpus from data table")
            self.ui.label_input_path.setText("Use table file:")
            self.ui.button_input_path.setIcon(self.ui.button_metafile.icon())
            self.ui.button_input_path.setText("Change")
            self.ui.button_input_path.clicked.disconnect(self.select_path)
            self.ui.button_input_path.clicked.connect(self.file_options)
            self.ui.input_path.clicked.connect(self.file_options)
            self.ui.widget_n_gram.hide()
            self.ui.radio_only_module.hide()
            self.ui.label_only_module.hide()
            self.ui.radio_read_files.setChecked(True)
            self.ui.groupBox.hide()

        else:
            self.ui.label_read_files.setText(
                "Build new corpus from text files")
            self.ui.label_input_path.setText("Path to text files:")
            self.ui.input_path.clicked.connect(self.select_path)
            self.ui.label_pos_tagging.show()
            self.ui.use_pos_tagging.show()
            self.ui.label_metafile.show()
            self.ui.check_use_metafile.show()
            self.ui.button_metafile.show()

        self.setWindowTitle(self.window_title)

        self.ui.issue_layout = QtWidgets.QVBoxLayout()
        self.ui.name_layout = QtWidgets.QHBoxLayout()
        self.ui.issue_label.setStyleSheet("QLabel { color: red; }")

        self.ui.corpus_name.setReadOnly(False)
        self.ui.corpus_name.setText("")
        self.ui.corpus_name.setValidator(
            QtGui.QRegExpValidator(QtCore.QRegExp("[A-Za-z0-9_]*")))
        self.ui.name_label.setBuddy(self.ui.corpus_name)

        self.ui.verticalLayout.insertLayout(0, self.ui.issue_layout)

        if not self._onefile:
            self.ui.label_pos_tagging.show()
            self.ui.use_pos_tagging.show()
            label_text = [self.nltk_label]

            try:
                val = options.settings.value("corpusbuilder_nltk") == "True"
                self.ui.use_pos_tagging.setChecked(val)
            except TypeError:
                pass

            if not options.use_nltk:
                label_text.append("(unavailble – NLTK is not installed)")
                self.ui.label_pos_tagging.setEnabled(False)
                self.ui.use_pos_tagging.setEnabled(False)
                self.ui.use_pos_tagging.setChecked(False)
            else:
                self.ui.use_pos_tagging.clicked.connect(self.pos_check)
                size = QtWidgets.QCheckBox().sizeHint()
                self.ui.icon_nltk_check = classes.CoqSpinner(size)
                self.ui.layout_nltk.addWidget(self.ui.icon_nltk_check)

            self.ui.label_pos_tagging.setText(" ".join(label_text))
            if self.ui.use_pos_tagging.isChecked():
                self.pos_check()

        if self._onefile:
            self.ui.input_path.setText(options.cfg.corpus_table_source_path)
        else:
            if options.cfg.text_source_path != os.path.expanduser("~"):
                self.ui.input_path.setText(options.cfg.text_source_path)
            else:
                self.ui.input_path.setText("")

        self.ui.yes_button.setEnabled(False)
        self.ui.corpus_name.textChanged.connect(
            lambda: self.validate_dialog(check_path=False))
        self.ui.check_use_metafile.toggled.connect(
            lambda: self.validate_dialog(check_path=False))
        self.ui.corpus_name.setFocus()
        try:
            self.resize(options.settings.value("corpusbuilder_size"))
        except TypeError:
            pass

    def pos_check(self):
        """
        This is called when the NLTK box is checked.
        """
        if self._testing:
            return
        if not self.ui.use_pos_tagging.isChecked():
            return

        self._nltk_lemmatize = False
        self._nltk_tokenize = False
        self._nltk_tagging = False
        self.nltk_exceptions = []

        if options.use_nltk:
            self._testing = True
            self.test_thread = CoqThread(self.test_nltk_core, parent=self)
            self.test_thread.taskFinished.connect(self.test_nltk_results)
            self.test_thread.taskException.connect(self.test_nltk_exception)
            self._label_text = str(self.ui.label_pos_tagging.text())

            self.ui.icon_nltk_check.start()
            self.ui.label_pos_tagging.setText(
                "Testing NLTK components, please wait...")
            self.ui.label_pos_tagging.setDisabled(True)
            self.ui.use_pos_tagging.setDisabled(True)
            self._old_button_state = self.ui.yes_button.isEnabled()
            self.ui.yes_button.setEnabled(False)
            self.test_thread.start()

    def test_nltk_exception(self):
        errorbox.ErrorBox.show(self.exc_info, self, no_trace=True)

    def test_nltk_core(self):
        import nltk
        # test lemmatizer:

        # This regular expression matches the error output of nltk.LookupError
        # of the form
        #
        # Resource [ANSI|']resource_name[ANSI|'] not found
        #
        # where ANSI can be any ANSI sequence, e.g. one used to change the
        # color of the output. The ANSI part is based on
        # https://stackoverflow.com/a/33925425

        regstr = (r".*Resource\s*"
                  "(?:(?:\x9B|\x1B\[)[0-?]*[ -\/]*[@-~])?"
                  "\s*'?"
                  "(\w+)"
                  "'?\s*"
                  "(?:(?:\x9B|\x1B\[)[0-?]*[ -\/]*[@-~])?"
                  "\s*not found")

        regexp = re.compile(regstr)

        try:
            nltk.stem.wordnet.WordNetLemmatizer().lemmatize("Test")
        except LookupError as e:
            s = str(e).replace("\n", "").strip("*")
            match = regexp.match(s)
            if match:
                self.nltk_exceptions.append(match.group(1).strip("'"))
            else:
                error_msg = str(e).replace("\n", "<br>")
                raise RuntimeError(msg_nltk_message_error.format(error_msg))
            self._nltk_lemmatize = False
        except Exception as e:
            self.nltk_exceptions.append(
                ("An unexpected error occurred when testing the "
                 "lemmatizer:\n{}".format(sys.exc_info())))
            raise e
        else:
            self._nltk_lemmatize = True

        # test tokenzie:
        try:
            nltk.sent_tokenize("test")
        except LookupError as e:
            s = str(e).replace("\n", "")
            match = regexp.match(s)
            if match:
                self.nltk_exceptions.append(match.group(1).strip("'"))
            else:
                error_msg = str(e).replace("\n", "<br>")
                raise RuntimeError(msg_nltk_message_error.format(error_msg))
            self._nltk_tokenize = False
        except Exception as e:
            self.nltk_exceptions.append(
                ("An unexpected error occurred when testing the "
                 "tokenizer:\n{}".format(sys.exc_info())))
            raise e
        else:
            self._nltk_tokenize = True

        # test tagging:
        try:
            nltk.pos_tag(["test"])
        except LookupError as e:
            s = str(e).replace("\n", "")
            match = regexp.match(s)
            if match:
                self.nltk_exceptions.append(match.group(1).strip("'"))
            else:
                error_msg = str(e).replace("\n", "<br>")
                raise RuntimeError(msg_nltk_message_error.format(error_msg))
            self._nltk_tagging = False
        except Exception as e:
            self.nltk_exceptions.append(
                ("An unexpected error occurred when testing the POS "
                 "tagger:\n{}".format(sys.exc_info())))
            raise e
        else:
            self._nltk_tagging = True

    def test_nltk_results(self):
        def pass_check():
            return (self._nltk_lemmatize and
                    self._nltk_tokenize and
                    self._nltk_tagging)

        self.ui.icon_nltk_check.stop()
        self.ui.yes_button.setEnabled(self._old_button_state)
        if self.ui.use_pos_tagging.isChecked() and not pass_check():
            self.ui.use_pos_tagging.setChecked(False)
            from . import nltkdatafiles
            self._nltk_data_files = nltkdatafiles.NLTKDatafiles(
                self.nltk_exceptions, parent=self)

            self._nltk_data_files.packagesInstalled.connect(
                lambda: self.ui.use_pos_tagging.setChecked(True))

            self._nltk_data_files.exec_()

        self._testing = False
        self.ui.label_pos_tagging.setDisabled(False)
        self.ui.use_pos_tagging.setDisabled(False)
        self.ui.label_pos_tagging.setText(self.nltk_label)
        self.validate_dialog()

    def file_options(self):
        """ Get CSV file options for current query input file. """
        from .namedtableoptions import NamedTableOptionsDialog
        dialog = NamedTableOptionsDialog(
            filename=utf8(self.ui.input_path.text()),
            default=self._table_options,
            parent=self,
            icon=options.cfg.icon)
        dialog.add_required_mapping("word")

        result = dialog.exec_()
        if result:
            self._table_options = result
            self.ui.input_path.setText(result.file_name)

        self.validate_dialog()

    def validate_metadata(self, button):
        if (self.ui.check_use_metafile.isChecked() and
                self._metafile_column is None):
            self.ui.label_metafile.setStyleSheet(
                STYLE_WARN.replace("QLineEdit", "CoqClickableLabel"))
            self.ui.issue_label.setText(
                "No file name colum is set for the metadata file.")
            button.setEnabled(False)
        else:
            self.ui.label_metafile.setStyleSheet("")

    def validate_dialog(self, check_path=False):
        super(BuilderGui, self).validate_dialog(check_path)

        self.ui.yes_button.setEnabled(True)
        self.ui.issue_label.setText("")
        if hasattr(self.ui, "corpus_name"):
            self.ui.corpus_name.setStyleSheet("")
            self.validate_name_not_empty(self.ui.yes_button)
            if self.ui.radio_only_module.isChecked():
                self.validate_db_does_exist(self.ui.yes_button)
            else:
                self.validate_name_is_unique(self.ui.yes_button)
                self.validate_db_does_not_exist(self.ui.yes_button)
                if not self._onefile:
                    self.validate_metadata(self.ui.yes_button)

    def select_path(self):
        if self._onefile:
            if not options.cfg.corpus_table_source_path:
                path = os.path.expanduser("~")
            else:
                path = os.path.split(options.cfg.corpus_table_source_path)[0]
            name = QtWidgets.QFileDialog.getOpenFileName(directory=path)
        else:
            name = QtWidgets.QFileDialog.getExistingDirectory(
                directory=options.cfg.text_source_path,
                options=(QtWidgets.QFileDialog.DontUseNativeDialog |
                         QtWidgets.QFileDialog.ReadOnly))

        if type(name) == tuple:
            name = name[0]
        if name:
            if not self._onefile:
                options.cfg.text_source_path = name
            else:
                options.cfg.corpus_table_source_path = name
            self.ui.input_path.setText(name)

    def install_exception(self):
        self.state = "failed"
        if type(self.exception) == RuntimeError:
            QtWidgets.QMessageBox.critical(
                self, "Corpus building error – Coquery", str(self.exception))
        else:
            errorbox.ErrorBox.show(self.exc_info, self, no_trace=False)

    def write_adhoc(self):
        # Create an installer in the adhoc directory:
        path = os.path.join(
            options.cfg.adhoc_path, "coq_install_{}.py".format(
                self.builder.arguments.db_name))
        with codecs.open(path, "w", encoding="utf-8") as output_file:
            for line in self.builder.create_installer_module():
                output_file.write(utf8(line))

    def finish_install(self, *args, **kwargs):
        super(BuilderGui, self).finish_install(*args, **kwargs)

        options.settings.setValue("corpusbuilder_size", self.size())
        options.settings.setValue("corpusbuilder_nltk",
                                  str(self.ui.use_pos_tagging.isChecked()))
        options.settings.setValue("corpusbuilder_metafile",
                                  utf8(self.ui.label_metafile.text()))
        options.settings.setValue("corpusbuilder_metafile_column",
                                  self._metafile_column)

        if self.state == "finished":
            self.write_adhoc()

    def get_arguments_from_gui(self):
        namespace = super(BuilderGui, self).get_arguments_from_gui()

        namespace.use_nltk = self.ui.use_pos_tagging.checkState()
        namespace.use_meta = self.ui.check_use_metafile.checkState()

        if self.ui.check_use_metafile.isChecked():
            namespace.metadata = utf8(self.ui.label_metafile.text())
        else:
            namespace.metadata = None

        namespace.metadata_column = self._metafile_column
        namespace.metaoptions = self._meta_options
        namespace.one_file = self._onefile
        namespace.name = utf8(self.ui.corpus_name.text())
        namespace.db_name = "coq_{}".format(namespace.name).lower()
        return namespace


class PackageGui(BuilderGui):
    button_label = "Read package"

    chunkProgress = QtCore.Signal(int, int)
    fileProgress = QtCore.Signal(str, str)

    def __init__(self, builder_class, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.builder_class = builder_class
        self.ngram_width = None
        self.state = None
        self._onefile = True

        self.ui = Ui_PackageInstaller()
        self.ui.setupUi(self)

        self.ui.yes_button = self.ui.buttonBox.button(
            QtWidgets.QDialogButtonBox.Yes)
        self.ui.yes_button.setText(self.button_label)
        self.ui.yes_button.clicked.connect(self.start_install)

        self.ui.button_input_path.clicked.connect(self.select_file)
        self.ui.input_path.clicked.connect(self.select_file)
        self.ui.corpus_name.textChanged.connect(self.validate_dialog)
        self.validate_dialog()

    def select_file(self):
        """
        Set the path to the package file.
        """
        name = QtWidgets.QFileDialog.getOpenFileName(
            directory=options.cfg.export_file_path,
            caption="Select corpus package file",
            filter="Coquery package files (*.coq);;Any file (*.*)")

        if type(name) == tuple:
            name = name[0]
        name = utf8(name)
        if name:
            try:
                corpus_name, license, ngram_width = self.validate_file(name)
            except RuntimeError as e:
                QtWidgets.QMessageBox.critical(
                    self, "Invalid package file", str(e))
            else:
                self.file_name = name
                self.ngram_width = ngram_width
                options.cfg.export_file_path = os.path.dirname(name)
                self.ui.corpus_name.setText(corpus_name)
                self.ui.text_license.setText(license)
                self.ui.input_path.setText(name)
                self.validate_dialog()

    def validate_file(self, file_name):
        """
        Check if the file is a valid package file.

        A file is considered a package file if
        - it is a valid ZIP file
        - contains a table file 'tables.json'
        - contains a license file 'LICENSE'
        - contains a file named 'corpus.csv'
        - contains exactly one file that ends in '.py'

        If any of these conditions is not met, a RuntimeError is raised.
        """
        err = "The file does not appear to be a valid package file: {}"
        try:
            zf = zipfile.ZipFile(file_name, "r")
            packaged_files = zf.namelist()
        except zipfile.BadZipFile:
            raise RuntimeError(err.format("Illegal file format"))

        check_tables_file = [os.path.basename(x) == "tables.json"
                             for x in packaged_files]
        check_license_file = [os.path.basename(x) == "LICENSE"
                              for x in packaged_files]
        check_module_file = [x for x in packaged_files if
                             os.path.basename(x).endswith(".py")]
        check_corpus_file = [os.path.basename(x) == "corpus.csv"
                             for x in packaged_files]

        if not any(check_tables_file):
            raise RuntimeError(
                err.format("Missing <code>tables.json</code>"))
        if not any(check_license_file):
            raise RuntimeError(err.format("Missing <code>LICENSE</code>"))
        if not any(check_corpus_file):
            raise RuntimeError(err.format("Missing <code>corpus.csv</code>"))
        if len(check_module_file) == 0:
            raise RuntimeError(err.format("Missing corpus module"))
        if len(check_module_file) > 1:
            raise RuntimeError(err.format("Too many corpus modules"))

        license = utf8(zf.read("LICENSE"))

        corpus_name = None
        corpusngram_width = None
        module = utf8(zf.read(check_module_file[0])).split("\n")
        for line in module:
            line = line.strip()
            match = re.match("name = '(.*)'", line)
            if match:
                corpus_name = match.group(1)
            match = re.match("corpusngram_width = '(.*)'", line)
            if match:
                corpusngram_width = int(match.group(1))
        return (corpus_name, license, corpusngram_width)

    def validate_dialog(self):
        """
        Enable or disable widgets according to the current state of the
        interface.
        """
        self.ui.input_path.setStyleSheet("")
        self.ui.issue_label.setText("")
        self.ui.yes_button.setEnabled(True)
        self.ui.group_options.show()
        self.ui.progress_box.hide()

        path = utf8(self.ui.input_path.text())
        if not path or not os.path.isfile(path):
            if path and not os.path.isfile(path):
                self.ui.input_path.setStyleSheet(STYLE_WARN)
            self.ui.yes_button.setDisabled(True)
            self.ui.group_options.hide()
        else:
            super(PackageGui, self).validate_dialog(check_path=False)

    def start_install(self):
        self.ui.progress_box.show()
        self.ui.group_options.hide()

        self.installStarted.emit()
        self.builder = self.builder_class(
            gui=self, package=utf8(self.ui.input_path.text()))

        self.builder.setChunkSignal(self.chunkProgress)
        self.builder.setFileSignal(self.fileProgress)
        self.chunkProgress.connect(
            lambda *tup: self.progress(self.ui.progress_bar, tup))
        self.fileProgress.connect(
            lambda *tup: self.progress(self.ui.progress_general, tup))

        self.builder.name = utf8(self.ui.corpus_name.text())
        self.builder.arguments = self.get_arguments_from_gui()

        self.ui.yes_button.setDisabled(True)

        self.install_thread = CoqThread(self.do_install, self)
        self.install_thread.setInterrupt(self.builder.interrupt)
        self.install_thread.taskFinished.connect(self.finish_install)
        self.install_thread.taskException.connect(self.install_exception)
        self.install_thread.start()

    def finish_install(self):
        self.ui.progress_box.hide()

        if self.state == "failed":
            S = "Installation of {} failed.".format(self.builder.name)
            self.ui.yes_button.setEnabled(True)
            self.ui.group_options.show()
        else:
            self.state = "finished"
            self.write_adhoc()
            S = "Finished installing {}.".format(self.builder.name)
            self.ui.label.setText("Installation complete.")
            self.ui.buttonBox.removeButton(self.ui.yes_button)
            self.ui.buttonBox.removeButton(
                self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel))
            self.ui.buttonBox.addButton(QtWidgets.QDialogButtonBox.Ok)
            self.ui.buttonBox.button(
                QtWidgets.QDialogButtonBox.Ok).clicked.connect(self.accept)
            self.parent().showMessage(S)
            self.accept()

        self.parent().showMessage(S)

    def accept(self):
        super(InstallerGui, self).accept()

    def get_arguments_from_gui(self):
        namespace = argparse.Namespace()
        namespace.only_module = self.ui.radio_only_module.isChecked()
        namespace.lookup_ngram = False
        namespace.ngram_width = None
        namespace.metadata = None
        if self.ngram_width is not None:
            namespace.lookup_ngram = True
            namespace.ngram_width = self.ngram_width

        namespace.name = self.builder.name
        namespace.encoding = "utf-8"
        namespace.db_name = "coq_{}".format(self.builder.name.lower())

        return namespace


class TableGui(MetaGui):
    button_label = "&Build"
    window_title = "Corpus builder – Coquery"

    def __init__(self, builder_class, onefile=True, parent=None):
        super(TableGui, self).__init__(builder_class,
                                       gui=Ui_CorpusTable,
                                       parent=parent)

        self._table_options = CSVOptions(
            sep=options.cfg.input_separator,
            header=options.cfg.file_has_headers,
            quote_char=options.cfg.quote_char,
            skip_lines=options.cfg.skip_lines,
            encoding=options.cfg.input_encoding,
            selected_column=None)

        self.ui.issue_layout = QtWidgets.QVBoxLayout()
        self.ui.name_layout = QtWidgets.QHBoxLayout()
        self.ui.issue_label.setStyleSheet("QLabel { color: red; }")

        self.ui.corpus_name.setReadOnly(False)
        self.ui.corpus_name.setText("")
        self.ui.corpus_name.setValidator(
            QtGui.QRegExpValidator(QtCore.QRegExp("[A-Za-z0-9_]*")))
        self.ui.name_label.setBuddy(self.ui.corpus_name)

        self.ui.verticalLayout.insertLayout(0, self.ui.issue_layout)

        self.ui.input_path.setText(options.cfg.corpus_table_source_path)

        self.ui.yes_button.setEnabled(False)
        self.ui.corpus_name.textChanged.connect(
            lambda: self.validate_dialog(check_path=False))

        self.ui.button_input_path.clicked.connect(self.select_file)
        self.ui.input_path.clicked.connect(self.select_file)

        self.ui.radio_only_module.toggled.connect(
            lambda: self.validate_dialog())
        self.ui.radio_only_module.toggled.connect(
            lambda: self.validate_dialog())

        self.ui.corpus_name.setFocus()

        try:
            self.resize(options.settings.value("corpusbuilder_size"))
        except TypeError:
            pass

    def validate_dialog(self, check_path=False):
        self.ui.yes_button.setEnabled(True)
        self.ui.issue_label.setText("")
        self.ui.corpus_name.setStyleSheet("")

        self.validate_name_not_empty(self.ui.yes_button)
        self.validate_file_exists(self.ui.yes_button)

        if self.ui.radio_only_module.isChecked():
            self.validate_db_does_exist(self.ui.yes_button)
        else:
            self.validate_name_is_unique(self.ui.yes_button)
            self.validate_db_does_not_exist(self.ui.yes_button)

    def select_path(self):
        if not options.cfg.corpus_table_source_path:
            path = os.path.expanduser("~")
        else:
            path = os.path.split(options.cfg.corpus_table_source_path)[0]
        name = QtWidgets.QFileDialog.getOpenFileName(directory=path)

        if type(name) == tuple:
            name = name[0]
        if name:
            options.cfg.corpus_table_source_path = name
            self.ui.input_path.setText(name)

    def install_exception(self):
        self.state = "failed"
        if type(self.exception) == RuntimeError:
            QtWidgets.QMessageBox.critical(
                self, "Corpus building error – Coquery", str(self.exception))
        else:
            errorbox.ErrorBox.show(self.exc_info, self, no_trace=False)

    def write_adhoc(self):
        # Create an installer in the adhoc directory:
        path = os.path.join(
            options.cfg.adhoc_path, "coq_install_{}.py".format(
                self.builder.arguments.db_name))
        with codecs.open(path, "w", encoding="utf-8") as output_file:
            for line in self.builder.create_installer_module():
                output_file.write(utf8(line))

    def finish_install(self, *args, **kwargs):
        super(TableGui, self).finish_install(*args, **kwargs)

        options.settings.setValue("corpusbuilder_size", self.size())
        if self.state == "finished":
            self.write_adhoc()

    def get_arguments_from_gui(self):
        namespace = super(TableGui, self).get_arguments_from_gui()
        namespace.name = utf8(self.ui.corpus_name.text())

        namespace.db_name = "coq_{}".format(namespace.name).lower()
        namespace.one_file = True
        return namespace

    def select_file(self):
        """ Get CSV file options for current query input file. """
        from .namedtableoptions import NamedTableOptionsDialog
        dialog = NamedTableOptionsDialog(
            filename=utf8(self.ui.input_path.text()),
            default=self._table_options,
            parent=self,
            icon=options.cfg.icon)
        dialog.add_required_mapping("word")

        result = dialog.exec_()
        if result:
            self._table_options = result
            self.ui.input_path.setText(result.file_name)

        self.validate_dialog()

    def start_install(self):
        if self.ui.radio_read_files.isChecked():
            lst = self.builder_class.get_file_list(
                str(self.ui.input_path.text()),
                self.builder_class.file_filter)
            try:
                self.builder_class.validate_files(lst)
            except RuntimeError as e:
                reply = QtWidgets.QMessageBox.question(
                    None, "Corpus path not valid – Coquery",
                    msg_corpus_path_not_valid.format(e),
                    (QtWidgets.QMessageBox.Ignore |
                     QtWidgets.QMessageBox.Discard))
                if reply == QtWidgets.QMessageBox.Discard:
                    return

        self.installStarted.emit()

        self.builder = self.builder_class(
            gui=self,
            mapping=self._table_options.mapping,
            dtypes=self._table_options.dtypes,
            table_options=self._table_options)

        self.builder.arguments = self.get_arguments_from_gui()
        self.builder.name = self.builder.arguments.name

        self.ui.yes_button.setEnabled(False)
        self.ui.widget_options.setEnabled(False)

        self.install_thread = CoqThread(self.do_install, self)
        self.install_thread.setInterrupt(self.builder.interrupt)
        self.install_thread.taskFinished.connect(self.finish_install)
        self.install_thread.taskException.connect(self.install_exception)
        self.install_thread.start()
