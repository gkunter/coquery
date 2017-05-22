# -*- coding: utf-8 -*-
"""
corpusbuilder_interface.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
from __future__ import print_function

import argparse
import codecs
import re
import logging
import os
import sys

from coquery import options
from coquery import sqlhelper
from coquery import NAME
from coquery.defines import (msg_invalid_metadata,
                             msg_install_abort,
                             msg_corpus_path_not_valid)
from coquery.errors import SQLNoConfigurationError, DependencyError
from coquery.unicode import utf8

from . import classes
from . import errorbox
from . import csvoptions
from .pyqt_compat import QtCore, QtWidgets, QtGui
from .ui.corpusInstallerUi import Ui_CorpusInstaller


class InstallerGui(QtWidgets.QDialog):
    button_label = "&Install"
    window_title = "Corpus installer – Coquery"

    installStarted = QtCore.Signal()
    showNLTKDownloader = QtCore.Signal(str)

    progressSet = QtCore.Signal(int, str)
    labelSet = QtCore.Signal(str)
    progressUpdate = QtCore.Signal(int)
    generalUpdate = QtCore.Signal(int)

    def __init__(self, builder_class, parent=None):
        super(InstallerGui, self).__init__(parent)

        self.logger = logging.getLogger(NAME)

        self.state = None
        self._testing = False
        self._onefile = False
        self.builder_class = builder_class

        self.ui = Ui_CorpusInstaller()
        self.ui.setupUi(self)
        self.ui.label_pos_tagging.hide()
        self.ui.use_pos_tagging.hide()
        self.ui.progress_box.hide()

        self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Yes).setText(self.button_label)
        self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Yes).clicked.connect(self.start_install)

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
            except:
                print("corpusbuilder_interface.InstallerGui.__init__(): Could not set background color of installation note box")
            self.ui.notes_label.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)

            self.ui.notes_scroll = QtWidgets.QScrollArea()
            self.ui.notes_scroll.setWidgetResizable(True)
            self.ui.notes_scroll.setWidget(self.ui.notes_label)

            self.ui.notes_box.replaceBox(self.ui.notes_scroll)

        if not options.cfg.experimental:
            try:
                self.ui.widget_n_gram.hide()
                self.ui.check_n_gram.setChecked(False)
            except AttributeError:
                # ignore exceptions raised if widgets do not exist
                pass

        self.restore_settings()
        self.ui.issue_label.setText("")
        self.ui.corpus_name.setStyleSheet("")

        self.ui.button_input_path.clicked.connect(self.select_path)
        self.ui.button_metafile.clicked.connect(self.select_metafile)
        self.ui.label_metafile.clicked.connect(self.select_metafile)

        self.ui.radio_read_files.toggled.connect(lambda x: self.activate_read(True))
        self.ui.radio_only_module.toggled.connect(lambda x: self.activate_read(False))
        self.ui.check_use_metafile.toggled.connect(self.toggle_use_metafile)

        self.installStarted.connect(self.show_progress)
        self.progressSet.connect(self.set_progress)
        self.labelSet.connect(self.set_label)
        self.progressUpdate.connect(self.update_progress)

        self.generalUpdate.connect(self.general_update)

    def restore_settings(self):
        self.ui.radio_read_files.blockSignals(True)
        self.ui.radio_only_module.blockSignals(True)
        try:
            self.resize(options.settings.value("corpusinstaller_size"))
        except TypeError:
            pass

        if isinstance(self, BuilderGui):
            target = "corpusinstaller_data_path"
        else:
            target = "corpusinstaller_corpus_source"
        self.ui.input_path.setText(utf8(options.settings.value(target, "")))

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

        val = options.settings.value("corpusinstaller_use_nltk", "false")
        self.ui.use_pos_tagging.setChecked(val == "true" or val is True)
        val = options.settings.value("corpusinstaller_use_ngram_table", "false")
        self.ui.check_n_gram.setChecked(val == "true" or val is True)
        self.ui.spin_n.setValue(
            int(options.settings.value("corpusinstaller_n_gram_width", 2)))
        self.ui.radio_read_files.blockSignals(False)
        self.ui.radio_only_module.blockSignals(False)

    def accept(self):
        super(InstallerGui, self).accept()
        options.settings.setValue("corpusinstaller_size", self.size())
        if isinstance(self, BuilderGui):
            target = "corpusinstaller_data_path"
        else:
            target = "corpusinstaller_corpus_source"
        options.settings.setValue(target, utf8(self.ui.input_path.text()))
        options.settings.setValue("corpusinstaller_read_files",
                                  self.ui.radio_read_files.isChecked())
        options.settings.setValue("corpusinstaller_metafile",
                                  utf8(self.ui.label_metafile.text()))
        options.settings.setValue("corpusinstaller_use_metafile",
                                  self.ui.check_use_metafile.isChecked())
        options.settings.setValue("corpusinstaller_use_nltk",
                                  self.ui.use_pos_tagging.isChecked())
        options.settings.setValue("corpusinstaller_use_ngram_table",
                                  self.ui.check_n_gram.isChecked())
        options.settings.setValue("corpusinstaller_ngram_width",
                                  self.ui.spin_n.value())

    def validate_dialog(self, check_path=True):
        self.ui.input_path.setStyleSheet("")
        self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Yes).setEnabled(True)
        self.ui.issue_label.setText("")

        if self.ui.radio_read_files.isChecked() and check_path:
            path = utf8(self.ui.input_path.text())
            if not path:
                self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Yes).setEnabled(False)
                return
            if ((self._onefile and not os.path.isfile(path)) or
                (not self._onefile and not os.path.isdir(path))):
                self.ui.issue_label.setText("Illegal data source path.")
                self.ui.input_path.setStyleSheet('QLineEdit {background-color: lightyellow; }')
                self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Yes).setEnabled(False)
                return

    def display(self):
        self.exec_()
        return self.state

    def general_update(self, i):
        self.ui.progress_general.setValue(i)

    def set_label(self, s):
        self.ui.progress_bar.setFormat(s)

    def set_progress(self, vmax, s):
        self.ui.progress_bar.setFormat(s)
        self.ui.progress_bar.setMaximum(vmax)
        self.ui.progress_bar.setValue(0)

    def update_progress(self, i):
        self.ui.progress_bar.setValue(i)

    def select_path(self):
        path = utf8(self.ui.input_path.text())
        if not path:
            path = os.path.join(options.cfg.base_path, "texts", "alice")
        name = QtWidgets.QFileDialog.getExistingDirectory(
            directory=path,
            options=(QtWidgets.QFileDialog.ReadOnly |
                     QtWidgets.QFileDialog.ShowDirsOnly |
                     QtWidgets.QFileDialog.HideNameFilterDetails))
        if type(name) == tuple:
            name = name[0]
        if name:
            self.ui.input_path.setText(name)
            self.validate_dialog()

    def select_metafile(self):
        path = os.path.split(utf8(self.ui.label_metafile.text()))[0]
        if not path:
            path = utf8(self.ui.input_path.text())
        if not path:
            path = os.path.expanduser("~")

        name = QtWidgets.QFileDialog.getOpenFileName(directory=path)
        if type(name) is tuple:
            name = name[0]
        if name:
            if not self.builder_class.probe_metadata(name):
                QtWidgets.QMessageBox.critical(self,
                                           "Invalid meta data file – Coquery",
                                           msg_invalid_metadata,
                                           QtWidgets.QMessageBox.Yes)
            else:
                self.ui.label_metafile.setText(name)
                self.ui.check_use_metafile.setChecked(True)

    def toggle_use_metafile(self):
        self.ui.check_use_metafile.blockSignals(True)
        if not self.ui.check_use_metafile.isChecked():
            self.ui.label_metafile.setText("")
        elif self.ui.label_metafile.text() == "":
            self.select_metafile()
            if self.ui.label_metafile.text() == "":
                self.ui.check_use_metafile.setChecked(False)
        self.ui.check_use_metafile.blockSignals(False)

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.reject()

    def activate_read(self, activate):
        self.ui.radio_read_files.blockSignals(True)
        self.ui.radio_only_module.blockSignals(True)
        self.ui.radio_read_files.setChecked(activate)
        self.ui.radio_only_module.setChecked(not activate)
        self.ui.widget_read_files.setEnabled(activate)
        self.validate_dialog()
        self.ui.radio_read_files.blockSignals(False)
        self.ui.radio_only_module.blockSignals(False)

    def show_progress(self):
        self.ui.progress_box.show()
        self.ui.progress_box.update()

    def do_install(self):
        self.builder.build()

    def finish_install(self):
        if self.state == "failed":
            S = "Installation of {} failed.".format(self.builder.name)
            self.ui.progress_box.hide()
            self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Yes).setEnabled(True)
            self.ui.widget_options.setEnabled(True)
        else:
            self.state = "finished"
            S = "Finished installing {}.".format(self.builder.name)
            self.ui.label.setText("Installation complete.")
            self.ui.progress_bar.hide()
            self.ui.progress_general.hide()
            self.ui.buttonBox.removeButton(self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Yes))
            self.ui.buttonBox.removeButton(self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel))
            self.ui.buttonBox.addButton(QtWidgets.QDialogButtonBox.Ok)
            self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(self.accept)
            self.parent().showMessage(S)
            self.accept()
        self.parent().showMessage(S)

    def install_exception(self):
        self.state = "failed"
        if isinstance(self.exception, RuntimeError):
            QtWidgets.QMessageBox.critical(self, "Installation error – Coquery",
                                        str(self.exception))
        elif isinstance(self.exception, DependencyError):
            QtWidgets.QMessageBox.critical(self, "Missing Python module – Coquery",
                                        str(self.exception))
        else:
            errorbox.ErrorBox.show(self.exc_info, self, no_trace=False)

    def reject(self):
        try:
            if self.state == "finished":
                self.accept()
            elif self.install_thread:
                response = QtWidgets.QMessageBox.warning(self,
                    "Aborting installation",
                    msg_install_abort,
                    QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.Yes)
                if response:
                    self.install_thread.quit()
                    super(InstallerGui, self).reject()
        except AttributeError:
            super(InstallerGui, self).reject()

    def check_input(self):
        button = self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Yes)
        if self.ui.radio_only_module.isChecked():
            self.ui.input_path.setStyleSheet('')
            button.setEnabled(True)
        else:
            path = str(self.ui.input_path.text())
            if os.path.isdir(path):
                self.ui.input_path.setStyleSheet('')
                button.setEnabled(True)
            else:
                self.ui.input_path.setStyleSheet('QLineEdit {background-color: lightyellow; }')
                button.setEnabled(False)

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
            l = self.builder_class.get_file_list(
                    str(self.ui.input_path.text()), self.builder_class.file_filter)
            try:
                self.builder_class.validate_files(l)
            except RuntimeError as e:
                reply = QtWidgets.QMessageBox.question(
                    None, "Corpus path not valid – Coquery",
                    msg_corpus_path_not_valid.format(e),
                    QtWidgets.QMessageBox.Ignore | QtWidgets.QMessageBox.Discard)
                if reply == QtWidgets.QMessageBox.Discard:
                    return

        self.installStarted.emit()

        if self._onefile:
            self.builder = self.builder_class(
                gui=self,
                mapping=self._table_options.mapping,
                dtypes=self._table_options.dtypes,
                table_options=self._table_options)
        elif hasattr(self, "_nltk_tagging"):
            pos = self.ui.use_pos_tagging.isChecked()
            self.builder = self.builder_class(pos=pos, gui=self)
        else:
            self.builder = self.builder_class(gui=self)

        self.builder.logger = self.logger
        self.builder.arguments = self.get_arguments_from_gui()
        self.builder.name = self.builder.arguments.name

        self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Yes).setEnabled(False)
        self.ui.widget_options.setEnabled(False)

        self.install_thread = classes.CoqThread(self.do_install, self)
        self.install_thread.setInterrupt(self.builder.interrupt)
        self.install_thread.taskFinished.connect(self.finish_install)
        self.install_thread.taskException.connect(self.install_exception)
        self.install_thread.start()

    def get_arguments_from_gui(self):
        namespace = argparse.Namespace()
        namespace.verbose = False
        namespace.use_nltk = False
        namespace.use_meta = False
        namespace.metadata = utf8(self.ui.label_metafile.text())

        if self.ui.radio_only_module.isChecked():
            namespace.o = False
            namespace.i = False
            namespace.l = False
            namespace.c = False
            namespace.w = True
            namespace.lookup_ngram = False
            namespace.only_module = True
        else:
            namespace.w = True
            namespace.o = True
            namespace.i = True
            namespace.l = True
            namespace.c = True
            namespace.only_module = False
            if self.ui.check_n_gram.checkState():
                namespace.lookup_ngram = True
                namespace.ngram_width = int(self.ui.spin_n.value())
            else:
                namespace.lookup_ngram = False

        namespace.encoding = self.builder_class.encoding

        namespace.name = self.builder_class.get_name()
        namespace.path = utf8(self.ui.input_path.text())

        namespace.db_name = self.builder_class.get_db_name()
        try:
            namespace.db_host, namespace.db_port, namespace.db_type, namespace.db_user, namespace.db_password = options.get_con_configuration()
        except ValueError:
            raise SQLNoConfigurationError
        namespace.current_server = options.cfg.current_server

        return namespace


class BuilderGui(InstallerGui):
    button_label = "&Build"
    window_title = "Corpus builder – Coquery"

    def __init__(self, builder_class, onefile=False, parent=None):
        super(BuilderGui, self).__init__(builder_class, parent)

        self.logger = logging.getLogger(NAME)

        self._nltk_lemmatize = False
        self._nltk_tokenize = False
        self._nltk_tagging = False
        self._testing = False
        self._onefile = onefile
        self._table_options = csvoptions.CSVOptions(
            sep=options.cfg.input_separator,
            header=options.cfg.file_has_headers,
            quote_char=options.cfg.quote_char,
            skip_lines=options.cfg.skip_lines,
            encoding=options.cfg.input_encoding,
            selected_column=None)

        if self._onefile:
            self.ui.label_read_files.setText("Build new corpus from data table")
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
        else:
            self.ui.label_read_files.setText("Build new corpus from text files")
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
            label_text = ["Use NLTK for part-of-speech tagging and lemmatization"]

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

        self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Yes).setEnabled(False)
        self.ui.corpus_name.textChanged.connect(lambda: self.validate_dialog(check_path=False))
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
            self.test_thread = classes.CoqThread(self.test_nltk_core, parent=self)
            self.test_thread.taskFinished.connect(self.test_nltk_results)
            self.test_thread.taskException.connect(self.test_nltk_exception)
            self._label_text = str(self.ui.label_pos_tagging.text())

            self.ui.icon_nltk_check.start()
            self.ui.label_pos_tagging.setText("Testing NLTK components, please wait...")
            self.ui.label_pos_tagging.setDisabled(True)
            self.ui.use_pos_tagging.setDisabled(True)
            self._old_button_state = self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Yes).isEnabled()
            self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Yes).setEnabled(False)
            self.test_thread.start()

    def test_nltk_exception(self):
        errorbox.ErrorBox.show(self.exc_info, self, no_trace=True)

    def test_nltk_core(self):
        import nltk
        # test lemmatizer:
        try:
            nltk.stem.wordnet.WordNetLemmatizer().lemmatize("Test")
        except LookupError as e:
            s = str(e).replace("\n", "").strip("*")
            match = re.match(r'.*Resource.*\'(.*)\'.*not found', s)
            if match:
                self.nltk_exceptions.append(match.group(1))
            self._nltk_lemmatize = False
        except Exception as e:
            self.nltk_exceptions.append("An unexpected error occurred when testing the lemmatizer:\n{}".format(sys.exc_info()))
            raise e
        else:
            self._nltk_lemmatize = True
        # test tokenzie:
        try:
            nltk.sent_tokenize("test")
        except LookupError as e:
            s = str(e).replace("\n", "")
            match = re.match(r'.*Resource.*\'(.*)\'.*not found', s)
            if match:
                self.nltk_exceptions.append(match.group(1))
            self._nltk_tokenize = False
        except Exception as e:
            self.nltk_exceptions.append("An unexpected error occurred when testing the tokenizer:\n{}".format(sys.exc_info()))
            raise e
        else:
            self._nltk_tokenize = True
        # test tagging:
        try:
            nltk.pos_tag("test")
        except LookupError as e:
            s = str(e).replace("\n", "")
            match = re.match(r'.*Resource.*\'(.*)\'.*not found', s)
            if match:
                self.nltk_exceptions.append(match.group(1))
            self._nltk_tagging = False
        except Exception as e:
            self.nltk_exceptions.append("An unexpected error occurred when testing the POS tagger:\n{}".format(sys.exc_info()))
            raise e
        else:
            self._nltk_tagging = True

    def test_nltk_results(self):
        def pass_check():
            return self._nltk_lemmatize and self._nltk_tokenize and self._nltk_tagging

        self.ui.icon_nltk_check.stop()
        self.ui.label_pos_tagging.setText(self._label_text)
        self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Yes).setEnabled(self._old_button_state)
        if self.ui.use_pos_tagging.isChecked() and not pass_check():
            self.ui.use_pos_tagging.setChecked(False)
            from . import nltkdatafiles
            nltkdatafiles.NLTKDatafiles.ask(self.nltk_exceptions, parent=self)

        self._testing = False
        self.ui.label_pos_tagging.setDisabled(False)
        self.ui.use_pos_tagging.setDisabled(False)

    def file_options(self):
        """ Get CSV file options for current query input file. """
        from .namedtableoptions import NamedTableOptionsDialog

        result = NamedTableOptionsDialog.getOptions(
            utf8(self.ui.input_path.text()), [],
            self._table_options, self, options.cfg.icon)
        if result:
            self._table_options = result
            self.ui.input_path.setText(result.file_name)

        self.validate_dialog()

    def validate_dialog(self, check_path=False):
        def validate_name_not_empty():
            if not utf8(self.ui.corpus_name.text()):
                self.ui.corpus_name.setStyleSheet('QLineEdit {background-color: lightyellow; }')
                self.ui.issue_label.setText("The corpus name cannot be empty.")
                button.setEnabled(False)

        def validate_name_is_unique():
            if utf8(self.ui.corpus_name.text()) in options.cfg.current_resources:
                self.ui.corpus_name.setStyleSheet('QLineEdit {background-color: lightyellow; }')
                self.ui.issue_label.setText("There is already another corpus with this name..")
                button.setEnabled(False)

        def validate_db_does_not_exist():
            db_exists = sqlhelper.has_database(
                options.cfg.current_server,
                "coq_{}".format(utf8(self.ui.corpus_name.text()).lower()))
            if db_exists:
                self.ui.corpus_name.setStyleSheet('QLineEdit {background-color: lightyellow; }')
                self.ui.issue_label.setText("There is already another corpus that uses a database with this name.")
                button.setEnabled(False)

        def validate_db_does_exist():
            db_exists = sqlhelper.has_database(
                options.cfg.current_server,
                "coq_{}".format(utf8(self.ui.corpus_name.text()).lower()))
            if not db_exists:
                self.ui.corpus_name.setStyleSheet('QLineEdit {background-color: lightyellow; }')
                self.ui.issue_label.setText("There is no database that uses this name.")
                button.setEnabled(False)

        super(BuilderGui, self).validate_dialog(check_path)

        button = self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Yes)
        button.setEnabled(True)
        self.ui.issue_label.setText("")
        if hasattr(self.ui, "corpus_name"):
            self.ui.corpus_name.setStyleSheet("")

        if hasattr(self.ui, "corpus_name"):
            validate_name_not_empty()
            if self.ui.radio_only_module.isChecked():
                validate_db_does_exist()
            else:
                validate_name_is_unique()
                validate_db_does_not_exist()

    def select_path(self):
        if self._onefile:
            if not options.cfg.corpus_table_source_path:
                path = os.path.expanduser("~")
            else:
                path = os.path.split(options.cfg.corpus_table_source_path)[0]
            name = QtWidgets.QFileDialog.getOpenFileName(directory=path)
        else:
            name = QtWidgets.QFileDialog.getExistingDirectory(directory=options.cfg.text_source_path)

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
            QtWidgets.QMessageBox.critical(self, "Corpus building error – Coquery",
                                        str(self.exception))
        else:
            errorbox.ErrorBox.show(self.exc_info, self, no_trace=False)

    def finish_install(self, *args, **kwargs):
        super(BuilderGui, self).finish_install(*args, **kwargs)

        options.settings.setValue("corpusbuilder_size", self.size())
        options.settings.setValue("corpusbuilder_nltk", str(self.ui.use_pos_tagging.isChecked()))

        if self.state == "finished":
            # Create an installer in the adhoc directory:
            path = os.path.join(
                options.cfg.adhoc_path, "coq_install_{}.py".format(
                    self.builder.arguments.db_name))
            with codecs.open(path, "w", encoding="utf-8") as output_file:
                for line in self.builder.create_installer_module():
                    output_file.write(utf8(line))

    def get_arguments_from_gui(self):
        namespace = super(BuilderGui, self).get_arguments_from_gui()

        namespace.name = utf8(self.ui.corpus_name.text())
        namespace.use_nltk = self.ui.use_pos_tagging.checkState()
        namespace.use_meta = self.ui.check_use_metafile.checkState()
        namespace.db_name = "coq_{}".format(namespace.name).lower()
        namespace.one_file = self._onefile
        return namespace
