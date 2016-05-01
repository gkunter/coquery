# -*- coding: utf-8 -*-
"""
corpusbuilder_interface.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

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

from coquery import options
from coquery import sqlhelper
from coquery import sqlwrap
from coquery.defines import * 
from coquery.errors import *
from coquery.unicode import utf8

from . import classes
from . import errorbox
from .pyqt_compat import QtCore, QtGui, frameShadow, frameShape
from .ui.corpusInstallerUi import Ui_CorpusInstaller

class InstallerGui(QtGui.QDialog):
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
        
        self.ui = Ui_CorpusInstaller()
        self.ui.setupUi(self)
        self.ui.label_pos_tagging.hide()
        self.ui.use_pos_tagging.hide()
        self.ui.progress_box.hide()
        self.ui.button_input_path.clicked.connect(self.select_path)
        self.ui.input_path.textChanged.connect(lambda: self.validate_dialog(check_path=True))
        self.ui.radio_complete.toggled.connect(self.changed_radio)
        self.ui.radio_only_module.toggled.connect(self.changed_radio)
        self.ui.input_path.textChanged.connect(self.check_input)

        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Yes).setText(self.button_label)
        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Yes).clicked.connect(self.start_install)
        
        self.ui.verticalLayout_3.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        
        self.installStarted.connect(self.show_progress)
        self.progressSet.connect(self.set_progress)
        self.labelSet.connect(self.set_label)
        self.progressUpdate.connect(self.update_progress)
        
        self.generalUpdate.connect(self.general_update)
        
        if options.cfg.corpus_source_path != os.path.expanduser("~"):
            self.ui.input_path.setText(options.cfg.corpus_source_path)
        
        self.accepted = False
        try:
            self.builder_class = builder_class
        except Exception as e:
            msg = msg_corpus_broken.format(
                name=basename,
                type=sys.exc_info()[0],
                code=sys.exc_info()[1])
            logger.error(msg)
            QtGui.QMessageBox.critical(
                None, "Corpus error – Coquery", 
                msg, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
            return

        self.ui.corpus_description.setText(
                utf8(self.ui.corpus_description.text()).format(
                    utf8(builder_class.get_title()), utf8(options.cfg.current_server)))
        
        self.ui.label_ngram_info.setText("")
        self.ui.label_ngram_info.setPixmap(self.parent().get_icon("sign-info").pixmap(
            QtCore.QSize(self.ui.spin_n.sizeHint().height(),
                         self.ui.spin_n.sizeHint().height())))
        
        notes = builder_class.get_installation_note()
        if notes:
            self.ui.notes_box = classes.CoqDetailBox("Installation notes")
            self.ui.verticalLayout.addWidget(self.ui.notes_box)

            self.ui.notes_label = QtGui.QLabel(notes)
            self.ui.notes_label.setWordWrap(True)
            self.ui.notes_label.setOpenExternalLinks(True)            
            try:
                self.ui.notes_label.setBackgroundRole(QtGui.QPalette.ColorRole.Base)
            except:
                print(dir(QtGui.QPalette.ColorRole), type(QtGui.QPalette.ColorRole))
            self.ui.notes_label.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)

            self.ui.notes_scroll = QtGui.QScrollArea()                                                                                      
            self.ui.notes_scroll.setWidgetResizable(True)
            self.ui.notes_scroll.setWidget(self.ui.notes_label)
                                                                                                                                        
            self.ui.notes_box.replaceBox(self.ui.notes_scroll)
        try:
            self.resize(options.settings.value("corpusinstaller_size"))
        except TypeError:
            pass
        
        if not options.cfg.experimental:
            try:
                self.ui.widget_ngram.hide()
                self.ui.check_ngram.setChecked(False)
            except AttributeError:
                # ignore exceptions raised if widgets do not exist
                pass
            
    def closeEvent(self, event):
        options.settings.setValue("corpusinstaller_size", self.size())

    def validate_dialog(self, check_path=True):
        self.ui.input_path.setStyleSheet("")
        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Yes).setEnabled(True)
        if self.ui.radio_only_module.isChecked():
            return
        if check_path:
            path = str(self.ui.input_path.text())
            if not path:
                self.ui.buttonBox.button(QtGui.QDialogButtonBox.Yes).setEnabled(False)
                return
            if not os.path.isdir(path):
                self.ui.input_path.setStyleSheet('QLineEdit {background-color: lightyellow; }')
                self.ui.buttonBox.button(QtGui.QDialogButtonBox.Yes).setEnabled(False)
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
        name = QtGui.QFileDialog.getExistingDirectory(directory=options.cfg.corpus_source_path, options=QtGui.QFileDialog.ReadOnly|QtGui.QFileDialog.ShowDirsOnly|QtGui.QFileDialog.HideNameFilterDetails)
        if type(name) == tuple:
            name = name[0]
        if name:
            options.cfg.corpus_source_path = name
            self.ui.input_path.setText(name)

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.reject()
            
    def changed_radio(self):
        if self.ui.radio_complete.isChecked():
            self.ui.box_build_options.setEnabled(True)
            #self.check_input()
        else:
            self.ui.box_build_options.setEnabled(False)
            #self.ui.buttonBox.button(QtGui.QDialogButtonBox.Yes).setEnabled(True)
        self.validate_dialog()

    def show_progress(self):
        self.ui.progress_box.show()
        self.ui.progress_box.update()
            
    def do_install(self):
        self.builder.build()

    def finish_install(self):
        if self.state == "failed":
            S = "Installation of {} failed.".format(self.builder.name)
            self.ui.progress_box.hide()
            self.ui.buttonBox.button(QtGui.QDialogButtonBox.Yes).setEnabled(True)
            self.ui.frame.setEnabled(True)
        else:
            self.state = "finished"
            S = "Finished installing {}.".format(self.builder.name)
            self.ui.label.setText("Installation complete.")
            self.ui.progress_bar.hide()
            self.ui.progress_general.hide()
            self.ui.buttonBox.removeButton(self.ui.buttonBox.button(QtGui.QDialogButtonBox.Yes))
            self.ui.buttonBox.removeButton(self.ui.buttonBox.button(QtGui.QDialogButtonBox.Cancel))
            self.ui.buttonBox.addButton(QtGui.QDialogButtonBox.Ok)
            self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).clicked.connect(self.accept)
            self.parent().showMessage(S)
            self.accept()
        self.parent().showMessage(S)
        
    def install_exception(self):
        self.state = "failed"
        if isinstance(self.exception, RuntimeError):
            QtGui.QMessageBox.critical(self, "Installation error – Coquery",
                                        str(self.exception))
        elif isinstance(self.exception, DependencyError):
            QtGui.QMessageBox.critical(self, "Missing Python module – Coquery",
                                        str(self.exception))
        else:
            errorbox.ErrorBox.show(self.exc_info, self, no_trace=False)

    def reject(self):
        try:
            if self.state == "finished":
                self.accept()
            elif self.install_thread:
                response = QtGui.QMessageBox.warning(self,
                    "Aborting installation", 
                    msg_install_abort,
                    QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
                if response:
                    self.install_thread.quit()
                    super(InstallerGui, self).reject()
        except AttributeError:
            super(InstallerGui, self).reject()
            
    def check_input(self):
        if self.ui.radio_only_module.isChecked():
            self.ui.input_path.setStyleSheet('')
            self.ui.buttonBox.button(QtGui.QDialogButtonBox.Yes).setEnabled(True)
        else:
            path = str(self.ui.input_path.text())
            if os.path.isdir(path):
                self.ui.input_path.setStyleSheet('')
                self.ui.buttonBox.button(QtGui.QDialogButtonBox.Yes).setEnabled(True)
            else:
                self.ui.input_path.setStyleSheet('QLineEdit {background-color: lightyellow; }')
                self.ui.buttonBox.button(QtGui.QDialogButtonBox.Yes).setEnabled(False)
        
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
        
        if self.ui.radio_complete.isChecked():
            l = self.builder_class.get_file_list(
                    str(self.ui.input_path.text()), self.builder_class.file_filter)                   
            try:
                self.builder_class.validate_files(l)
            except RuntimeError as e:
                reply = QtGui.QMessageBox.question(
                    None, "Corpus path not valid – Coquery",
                    msg_corpus_path_not_valid.format(e),
                    QtGui.QMessageBox.Ignore|QtGui.QMessageBox.Discard)
                if reply == QtGui.QMessageBox.Discard:
                    return

        self.installStarted.emit()
        self.accepted = True
        if hasattr(self, "_nltk_tagging"):
            pos = self.ui.use_pos_tagging.isChecked()
            self.builder = self.builder_class(pos=pos, gui=self)
        else:
            self.builder = self.builder_class(gui=self)

        self.builder.logger = self.logger
        self.builder.arguments = self.get_arguments_from_gui()
        self.builder.name = self.builder.arguments.name

        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Yes).setEnabled(False)
        self.ui.frame.setEnabled(False)

        #try:
            #self.do_install()
        #except RuntimeError as e:
            #errorbox.ErrorBox.show(sys.exc_info(), e, no_trace=True)
        #except Exception as e:
            #errorbox.ErrorBox.show(sys.exc_info(), e)
        #else:
            #self.finish_install()

        self.install_thread = classes.CoqThread(self.do_install, self)
        self.install_thread.setInterrupt(self.builder.interrupt)
        self.install_thread.taskFinished.connect(self.finish_install)
        self.install_thread.taskException.connect(self.install_exception)
        self.install_thread.start()
    
    def get_arguments_from_gui(self):
        namespace = argparse.Namespace()
        namespace.verbose = False
        namespace.use_nltk = False
        
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
            if self.ui.check_ngram.checkState():
                namespace.lookup_ngram = True
                namespace.ngram_width = int(self.ui.spin_n.value())
            else:
                namespace.lookup_ngram = False

        namespace.encoding = self.builder_class.encoding
        
        namespace.name = self.builder_class.get_name()
        namespace.path = str(self.ui.input_path.text())

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

    def __init__(self, builder_class, parent=None):
        super(BuilderGui, self).__init__(builder_class, parent)
        self.ui.input_path.textChanged.disconnect()

        self.logger = logging.getLogger(NAME)        

        self._nltk_lemmatize = False
        self._nltk_tokenize = False
        self._nltk_tagging = False
        self._testing = False

        self.ui.corpus_description.setText("<html><head/><body><p><span style='font-weight:600;'>Corpus builder</span></p><p>You have requested to create a new corpus from a selection of text files using the database connection '{}'. The corpus will afterwards be available for queries.</p></body></html>".format(options.cfg.current_server))
        self.ui.label_5.setText("Build corpus from local text files and install corpus module (if you have a local database server)")
        self.ui.label_8.setText("Path to text files:")
        self.setWindowTitle(self.window_title)
        
        self.ui.name_layout = QtGui.QHBoxLayout()
        self.ui.name_label = QtGui.QLabel("&Name of new corpus:")
        self.ui.issue_label = QtGui.QLabel("")
        self.ui.corpus_name = QtGui.QLineEdit()
        self.ui.corpus_name.setMaxLength(32)
        self.ui.corpus_name.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("[A-Za-z0-9_]*")))
        self.ui.name_label.setBuddy(self.ui.corpus_name)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)

        self.ui.name_layout.addWidget(self.ui.name_label)
        self.ui.name_layout.addWidget(self.ui.corpus_name)
        self.ui.name_layout.addWidget(self.ui.issue_label)
        self.ui.name_layout.addItem(spacerItem)
        self.ui.verticalLayout.insertLayout(1, self.ui.name_layout)

        self.ui.label_pos_tagging.show()
        self.ui.use_pos_tagging.show()
        label_text = ["Use NLTK for part-of-speech tagging and lemmatization"]

        try:
            val = options.settings.value("corpusbuilder_nltk") == "True"
            self.ui.use_pos_tagging.setChecked(val)
        except TypeError:
            pass

        if not options._use_nltk:
            label_text.append("(unavailble – NLTK is not installed)")
            self.ui.label_pos_tagging.setEnabled(False)
            self.ui.use_pos_tagging.setEnabled(False)
            self.ui.use_pos_tagging.setChecked(False)
        else:
            self.ui.use_pos_tagging.clicked.connect(self.pos_check)
            size = QtGui.QCheckBox().sizeHint()
            self.ui.icon_nltk_check = classes.CoqSpinner(size)
            self.ui.layout_nltk.addWidget(self.ui.icon_nltk_check)
            
        self.ui.label_pos_tagging.setText(" ".join(label_text))

        if options.cfg.text_source_path != os.path.expanduser("~"):
            self.ui.input_path.setText(options.cfg.text_source_path)
        else:
            self.ui.input_path.setText("")
            
        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Yes).setEnabled(False)
        self.ui.input_path.textChanged.connect(lambda: self.validate_dialog(check_path=False))
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

        if options._use_nltk:
            self._testing = True
            self.test_thread = classes.CoqThread(self.test_nltk_core, parent=self)
            self.test_thread.taskFinished.connect(self.test_nltk_results)
            self.test_thread.taskException.connect(self.test_nltk_exception)
            self._label_text = str(self.ui.label_pos_tagging.text())
            
            self.ui.icon_nltk_check.start()
            self.ui.label_pos_tagging.setText("Testing NLTK components, please wait...")
            self.ui.label_pos_tagging.setDisabled(True)
            self.ui.use_pos_tagging.setDisabled(True)
            self._old_button_state = self.ui.buttonBox.button(QtGui.QDialogButtonBox.Yes).isEnabled()
            self.ui.buttonBox.button(QtGui.QDialogButtonBox.Yes).setEnabled(False)
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
            print(s)
            match = re.match(r'.*Resource.*\'(.*)\'.*not found', s)
            if match:
                self.nltk_exceptions.append(match.group(1))
            self._nltk_lemmatize = False
        except Exception as e:
            self.nltk_exceptions.append("An unexpected error occurred when testing the lemmatizer:\n{}".format(sys.exc_info()))
            print(s)
            raise e
        else:
            self._nltk_lemmatize = True
        # test tokenzie:
        try:
            nltk.sent_tokenize("test")
        except LookupError as e:
            s = str(e).replace("\n", "")
            print(s)
            match = re.match(r'.*Resource.*\'(.*)\'.*not found', s)
            if match:
                self.nltk_exceptions.append(match.group(1))
            self._nltk_tokenize = False
        except Exception as e:
            self.nltk_exceptions.append("An unexpected error occurred when testing the tokenizer:\n{}".format(sys.exc_info()))
            print(s)
            raise e
        else:
            self._nltk_tokenize = True
        # test tagging:
        try:
            nltk.pos_tag("test")
        except LookupError as e:
            s = str(e).replace("\n", "")
            print(s)
            match = re.match(r'.*Resource.*\'(.*)\'.*not found', s)
            if match:
                self.nltk_exceptions.append(match.group(1))
            self._nltk_tagging = False
        except Exception as e:
            self.nltk_exceptions.append("An unexpected error occurred when testing the POS tagger:\n{}".format(sys.exc_info()))
            print(s)
            raise e
        else:
            self._nltk_tagging = True
        
    def test_nltk_results(self):
        def pass_check():
            return self._nltk_lemmatize and self._nltk_tokenize and self._nltk_tagging

        self.ui.icon_nltk_check.stop()
        self.ui.label_pos_tagging.setText(self._label_text)
        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Yes).setEnabled(self._old_button_state)
        if self.ui.use_pos_tagging.isChecked() and not pass_check():
            self.ui.use_pos_tagging.setChecked(False)
            from . import nltkdatafiles
            nltkdatafiles.NLTKDatafiles.ask(self.nltk_exceptions, parent=self)

        self._testing = False
        self.ui.label_pos_tagging.setDisabled(False)
        self.ui.use_pos_tagging.setDisabled(False)

    def closeEvent(self, event):
        options.settings.setValue("corpusbuilder_size", self.size())
        options.settings.setValue("corpusbuilder_nltk", str(self.ui.use_pos_tagging.isChecked()))
    
    def validate_dialog(self, check_path=True):
        if hasattr(self.ui, "corpus_name"):
            self.ui.corpus_name.setStyleSheet("")
        super(BuilderGui, self).validate_dialog()
        if hasattr(self.ui, "corpus_name"):
            self.ui.issue_label.setText("")
            try:
                db_host, db_port, db_type, db_user, db_password = options.get_con_configuration()
            except ValueError:
                raise SQLNoConfigurationError

            db_exists = sqlhelper.has_database(
                options.cfg.current_server,
                "coq_{}".format(str(self.ui.corpus_name.text()).lower()))
            # regardless of whether only the module or the whole corpus
            # is requested, the corpus needs a name:
            if not str(self.ui.corpus_name.text()):
                self.ui.corpus_name.setStyleSheet('QLineEdit {background-color: lightyellow; }')
                self.ui.issue_label.setText("The corpus name cannot be empty.")
                self.ui.buttonBox.button(QtGui.QDialogButtonBox.Yes).setEnabled(False)
            # make sure that there is no corpus with that name already:
            elif str(self.ui.corpus_name.text()) in options.cfg.current_resources:
                self.ui.corpus_name.setStyleSheet('QLineEdit {background-color: lightyellow; }')
                self.ui.issue_label.setText("There is already another corpus with this name..")
                self.ui.buttonBox.button(QtGui.QDialogButtonBox.Yes).setEnabled(False)
            else:
                # make sure that the database exists if only the module
                # install is requested:
                if self.ui.radio_only_module.isChecked() and not db_exists:
                    self.ui.corpus_name.setStyleSheet('QLineEdit {background-color: lightyellow; }')
                    self.ui.issue_label.setText("There is no database that uses this name.")
                    self.ui.buttonBox.button(QtGui.QDialogButtonBox.Yes).setEnabled(False)
                # make sure that no database exists if the complete
                # install is requested:
                elif self.ui.radio_complete.isChecked() and db_exists:
                    self.ui.corpus_name.setStyleSheet('QLineEdit {background-color: lightyellow; }')
                    self.ui.issue_label.setText("There is already another database that uses this name.")
                    self.ui.buttonBox.button(QtGui.QDialogButtonBox.Yes).setEnabled(False)
    
    def select_path(self):
        name = QtGui.QFileDialog.getExistingDirectory(directory=options.cfg.text_source_path)
        if type(name) == tuple:
            name = name[0]
        if name:
            options.cfg.text_source_path = name
            self.ui.input_path.setText(name)

    def install_exception(self):
        self.state = "failed"
        if type(self.exception) == RuntimeError:
            QtGui.QMessageBox.critical(self, "Corpus building error – Coquery",
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
        namespace.db_name = "coq_{}".format(namespace.name).lower()
        return namespace
