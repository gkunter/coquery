# -*- coding: utf-8 -*-
"""
corpusmanager.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
from __future__ import division

import sys
import fnmatch
import os
import imp
import logging

from coquery import options
from coquery import corpusbuilder
from coquery.errors import *
from coquery.defines import *
from coquery.unicode import utf8

from . import classes
from .pyqt_compat import QtCore, QtGui, frameShadow, frameShape
from .ui.corpusManagerUi import Ui_corpusManager

class CoqAccordionEntry(QtGui.QWidget):
    """ Define a QWidget that can be used as an entry in a accordion list."""
    def __init__(self, path=None, stack=None, *args, **kwargs):
        super(CoqAccordionEntry, self).__init__(*args, **kwargs)
        self._title = ""
        self._text = ""
        self._url = ""
        self._name = ""
        self._references = ""
        self._license = ""
        self._builder_class = None
        self._checksum = ""
        self._validation = ""
        self._modules = []
        self._stack = stack
        self._is_builder = False
        self._adhoc = False
        self._language = ""
        self._code = ""
        self._path = path
        
        self.verticalLayout_2 = QtGui.QVBoxLayout(self)
        self.corpus_description_frame = QtGui.QFrame(self)
        
        button_col = options.cfg.app.palette().color(QtGui.QPalette().Light)
        style = "QFrame {{ background-color: rgb({}, {}, {}); }}".format(button_col.red(), button_col.green(), button_col.blue())
        self.corpus_description_frame.setStyleSheet(style)
        self.corpus_description_frame.setFrameShape(frameShape)
        self.corpus_description_frame.setFrameShadow(frameShadow)
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.corpus_description_frame)
        self.verticalLayout_3.setSpacing(20)
        self.verticalLayout_3.setMargin(20)
        self.corpus_description = QtGui.QLabel(self.corpus_description_frame)
        self.corpus_description.setWordWrap(True)
        self.corpus_description.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.corpus_description.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextBrowserInteraction|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.corpus_description.linkActivated.connect(self.open_link)

        self.verticalLayout_3.addWidget(self.corpus_description)
        
        self.button_layout = QtGui.QHBoxLayout()
        self.button_layout.setSpacing(8)

        self.validation_label = QtGui.QLabel("")
        self.button_layout.addWidget(self.validation_label)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.button_layout.addItem(spacerItem)
        self.verticalLayout_3.addLayout(self.button_layout)
        
        self.verticalLayout_2.addWidget(self.corpus_description_frame)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)

    @property
    def name(self):
        return self._name
    
    @property
    def adhoc(self):
        return self._adhoc
    
    @property
    def builtin(self):
        return self._builtin

    def open_link(self, link):
        """
        Process any link clicked from the corpus description label.
        
        Usually, the URL of the link is opened. One exception is the link 
        '_to_clipboard', which copies the references to the clipboard.
        """
        if utf8(link) == "_to_clipboard":
            QtGui.QApplication.clipboard().setText("\n".join([utf8(x) for x in self._reference_list]))
        else:
            QtGui.QDesktopServices.openUrl(QtCore.QUrl(link))

    def setup_buttons(self, installed, entry_widget):
        """
        Add buttons depending on the install state of the entry. 
        
        For entries that are not installed, add an "Install" button. 
        For installed adhoc corpora, add a "Remove" button.
        For other installed corpora, add both a "Remove" and a "Reinstall"
        button.
        
        Also conenct the buttons to the appropriate methods.
        """
        self.widget_layout = QtGui.QHBoxLayout()
        entry_widget.header_layout.addLayout(self.widget_layout)
        
        button_build = QtGui.QPushButton()
        button_build.setIcon(self._stack.parent().get_icon("cone"))
        button_build.setText("Build")
        button_build.setToolTip("Build new corpus")
        button_remove = QtGui.QPushButton()
        button_remove.setIcon(self._stack.parent().get_icon("sign-delete"))
        button_remove.setText("Remove")
        button_remove.setToolTip("Remove corpus")
        button_install = QtGui.QPushButton()
        button_install.setIcon(self._stack.parent().get_icon("sign-add"))
        button_install.setText("Install")
        button_install.setToolTip("Install corpus")
        button_reinstall = QtGui.QPushButton()
        button_reinstall.setIcon(self._stack.parent().get_icon("sign-sync"))
        button_reinstall.setText("Reinstall")
        button_reinstall.setToolTip("Reinstall corpus")

        # make all buttons the same width:
        max_width = 0
        for button in [button_build, button_remove, button_install, button_reinstall]:
            max_width = max(max_width, button.sizeHint().width())
        
        for button in [button_build, button_remove, button_install, button_reinstall]:
            button.setMinimumWidth(max_width)
        
        if self._is_builder:
            self.button_build = button_build
            self.button_build.setParent(entry_widget)
            entry_widget.header_layout.addWidget(self.button_build)
            self.button_build.clicked.connect(lambda: self._stack.buildCorpus.emit(self))
        else:
            if installed or not self._builtin:
                self.button_remove = button_remove
                self.button_remove.setParent(entry_widget)
                self.widget_layout.addWidget(self.button_remove)

                if self._stack:
                    self.button_remove.clicked.connect(lambda: 
                    self._stack.removeCorpus.emit(self))

            if not self._adhoc:
                if not installed:
                    self.button_install = button_install
                else:
                    self.button_install = button_reinstall
                self.button_install.setParent(entry_widget)
                self.widget_layout.addWidget(self.button_install)

                if self._checksum:
                    self.validation_label.setText(
                        "<b>MD5 checksum:</b> {} ({})".format(
                        self._checksum, self._validation))

            if self._stack and not self._adhoc:
                self.button_install.clicked.connect(self.safe_install)
    
    def safe_install(self):
        if self._validation == "validated":
            msg = msg_validated_install
            box = QtGui.QMessageBox.question
            default = QtGui.QMessageBox.Yes
        elif self._validation == "unvalidated":
            msg = msg_unvalidated_install
            default = QtGui.QMessageBox.No
            box = QtGui.QMessageBox.warning
        elif self._validation == "failed":
            msg = msg_failed_install
            default = QtGui.QMessageBox.No
            box = QtGui.QMessageBox.warning
        elif self._validation == "rejected":
            msg = msg_rejected_install
            default = QtGui.QMessageBox.No
            box = QtGui.QMessageBox.critical
        #msg = msg.format(corpus=self._name)

        #response = box(None, 
            #"Unvalidated corpus installer – Coquery", 
            #msg, QtGui.QMessageBox.Yes| QtGui.QMessageBox.No, default)
        if True or response == QtGui.QMessageBox.Yes:
            self._stack.installCorpus.emit(self._builder_class)
    
    def setReferences(self, ref):
        self._reference_list = ref
    
        references = "".join(["<p><span style='padding-left: 2em; text-indent: 2em;'>{}</span></p>".format(utf8(x)) for x in ref])
        self._references = "<p><b>References</b> <a href='_to_clipboard'>(copy to clipboard)</a>{}</p>".format(references)
        self.change_description()
    
    def setTitle(self, title):
        self._title = title
        self.change_description()
        
    def setLanguage(self, language, code):
        if language != corpusbuilder.BaseCorpusBuilder.get_language():
            self._language = language
        if code != corpusbuilder.BaseCorpusBuilder.get_language_code():
            self._code = code
        self.change_description()
        
    def setModules(self, modules):
        self._modules = modules
        self.change_description()
        
    def setChecksum(self, checksum):
        self._checksum = checksum
        if self.validate_checksum(checksum):
            self._validation = "validated"
        else:
            self._validation = "unvalidated"
        
    def validate_checksum(self, checksum):
        return False
        
    def setLicense(self, license):
        if self._adhoc:
            return
        self._license = license
        self.change_description()

    def setName(self, name):
        self._name = name

    def setBuilderClass(self, builder_class):
        self._builder_class = builder_class

    def setDescription(self, text):
        self._text = text
        self.change_description()
        
    def setURL(self, url):
        if self._adhoc:
            return
        self._url = url
        self.change_description()
        
    def change_description(self):
        string_list = []
        if self._title:
            if self._url:
                string_list.append("<p><b>{name}</b> (<a href='{url}'>{url}</a>)</p>".format(
                    name=self._title, url=self._url))
            else:
                string_list.append("<p><b>{}</b></p>".format(self._title))
        if self._text:
            string_list.append("<p><font size='100%'>{}</font></p>".format(self._text))
        if self._language or self._code:
            string_list.append("<p><b>Language</b></p><p>{}{}</p>".format(
                self._language, " ({})".format(self._code) if self._code else ""))
        if self._references:
            string_list.append(self._references)
        if self._license:
            string_list.append(self._license)
        if self._modules:
            l = []
            for name, module, url in self._modules:
                if url:
                   s = "<p>{module} (<a href='{url}'>{url}</a>)</p>".format(
                       module=utf8(module), url=utf8(url))
                else:
                   s = "<p>{}</p>".format(module)
                l.append(s)
            string_list.append("<p><b>Required additional Python modules</b></p>{}".format(
                "".join(l)))
        self.corpus_description.setText(
            "".join(string_list))

class CorpusManager(QtGui.QDialog):
    removeCorpus = QtCore.Signal(object)
    installCorpus = QtCore.Signal(object)
    buildCorpus = QtCore.Signal(object)

    def __init__(self, parent=None):
        super(CorpusManager, self).__init__(parent)
        self.ui = Ui_corpusManager()
        self.ui.setupUi(self)

        try:
            self.resize(options.settings.value("corpusmanager_size"))
        except TypeError:
            pass

        self.paths = []
        self.last_detail_box = None
        
        try:
            self.resize(self.width(), options.cfg.corpus_manager_view_height)
        except AttributeError:
            pass
        try:
            self.resize(options.cfg.corpus_manager_view_width, self.height())
        except AttributeError:
            pass

        self.paths.append((options.cfg.adhoc_path, INSTALLER_ADHOC))
        self.paths.append((options.cfg.installer_path, INSTALLER_DEFAULT))
        if options.cfg.custom_installer_path:
            self.paths.append((options.cfg.custom_installer_path, INSTALLER_CUSTOM))

        self.update()

    def built_in(self, path):
        """
        Check if the path points to a built-in installer, i.e. one that is 
        included in the default Coquery package.
        
        Parameters
        ----------
        path : str 
            A string containing the path to a corpus installer
            
        Returns
        -------
        b : bool 
            True if the path is in the default Coquery directory tree, or 
            False otherwise (i.e. with custom installers or ad-hoc corpora)
        """
        return os.path.abspath(options.cfg.installer_path) in os.path.abspath(path)

    def update(self):
        """
        Read the installers from the path, and add a widget for each to the 
        installer list.
        """
        options.cfg.current_resources = options.get_available_resources(options.cfg.current_server)
        # clear existing installer list:
        QtGui.QWidget().setLayout(self.ui.list_content.layout())

        self.ui.list_layout = QtGui.QVBoxLayout(self.ui.list_content)
        self.ui.list_layout.setMargin(0)
        self.ui.list_layout.setSpacing(0)
        
        for path, label in self.paths:
            header_row = self.ui.list_layout.count()
            count = 0

            for root, dirnames, filenames in os.walk(path):
                installer_list = sorted(fnmatch.filter(filenames, 'coq_install_*.py'), reverse=False)
                
                for fullpath in installer_list:
                    module_path = os.path.join(root, fullpath)
                    basename, ext = os.path.splitext(os.path.basename(fullpath))

                    ## Validate the file, i.e. determine whether the file contains
                    ## only those instructions that are allowed for installer 
                    ## modules.
                    
                    try:
                        hashsum = options.validate_module(module_path, 
                                expected_classes=["BuilderClass"], 
                                whitelisted_modules="all",
                                allow_if = True).hexdigest()
                    except (IllegalCodeInModuleError,
                            IllegalFunctionInModuleError,
                            IllegalImportInModuleError,
                            ModuleIncompleteError) as e:
                        QtGui.QMessageBox.critical(
                            None, "Corpus validation error – Coquery", 
                            msg_invalid_installer.format(name=basename, code=str(e)), QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
                        continue
                    except (ImportError, SyntaxError) as e:
                        msg = msg_corpus_broken.format(
                            name=basename,
                            type=sys.exc_info()[0],
                            code=sys.exc_info()[1])
                        logger.error(msg)
                        QtGui.QMessageBox.critical(
                            None, "Corpus error – Coquery", 
                            msg, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
                        continue

                    try:
                        # load the module:
                        module = imp.load_source(basename, module_path)
                    except ImportError:
                        msg = msg_corpus_broken.format(
                            name=basename,
                            type=sys.exc_info()[0],
                            code=sys.exc_info()[1])
                        logger.error(msg)
                        QtGui.QMessageBox.critical(
                            None, "Corpus error – Coquery", 
                            msg, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
                        continue
                    try:
                        builder_class = module.BuilderClass
                    except AttributeError:
                        continue

                    # create a new accordion entry:
                    entry = CoqAccordionEntry(stack=self)

                    name = utf8(builder_class.get_name())
                    self.detail_box = classes.CoqDetailBox(name, entry, alternative=name)

                    if basename != "coq_install_generic":
                        entry._adhoc = hasattr(builder_class, "_is_adhoc")
                        entry._builtin = self.built_in(module_path)
                        entry.setName(name)
                        
                        #entry.setChecksum(hashsum)

                        title = utf8(builder_class.get_title())
                        entry.setTitle(title)
                        
                        if builder_class.get_url():
                            entry.setURL(utf8(builder_class.get_url()))
                            
                        if builder_class.get_description():
                            entry.setDescription(
                                "".join(["<p>{}</p>".format(utf8(x)) for x in builder_class.get_description()]))
                                
                        if builder_class.get_language():
                            entry.setLanguage(
                                utf8(builder_class.get_language()), utf8(builder_class.get_language_code()))
                            
                        if builder_class.get_references():
                            entry.setReferences(builder_class.get_references())
                                
                        if builder_class.get_license():
                            entry.setLicense("<p><b>License</b></p><p>{}</p>".format(utf8(builder_class.get_license())))

                        if builder_class.get_modules():
                            entry.setModules(builder_class.get_modules())

                        entry.setup_buttons(name in options.cfg.current_resources, entry_widget=self.detail_box)
                        entry.setBuilderClass(builder_class)

                        self.detail_box.clicked.connect(lambda x: self.update_accordion(x))

                        # add entry to installer list:
                        self.ui.list_layout.addWidget(self.detail_box)
                        count += 1
            
            if label == INSTALLER_ADHOC:
                entry = CoqAccordionEntry(stack=self)
                entry._is_builder = True
                entry.setTitle("Build a new corpus")
                entry.setDescription("<p>You can build a new corpus by storing the words from a selection of text files in a database that can be queried by Coquery. If the Natural Language Toolkit NLTK (<a href='http://www.nltk.org'>http://www.nltk.org</a>) is installed on your computer, you can choose the new corpus to be automatically lemmatized and tagged  for their part of speech.</p>")

                self.detail_box = classes.CoqDetailBox("Build new corpus...", entry)
                entry.setup_buttons(False, self.detail_box)
                self.ui.list_layout.addWidget(self.detail_box)
                count += 1
            
            # if a label was provided and at least one installer added, insert 
            # the header at the remembered position:
            if label and count:
                header = QtGui.QLabel("<b>{}</b>".format(label))
                height = header.sizeHint().height()
                if header_row == 0:
                    # no top margin if this is the first widget in the layout:
                    header.setContentsMargins(0, 0, 0, int(height * 0.25))
                else:
                    # add spacing otherwise:
                    header.setContentsMargins(0, int(height * 0.75), 0, int(height * 0.25))
                self.ui.list_layout.insertWidget(header_row, header)
        self.ui.list_layout.addItem(QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))

    def update_accordion(self, detail_box):
        """
        Closes the last installer entry, and remembers the current one.
        """
        if self.last_detail_box and self.last_detail_box.isExpanded() and self.last_detail_box != detail_box:
            self.last_detail_box.toggle()
        self.last_detail_box = detail_box            

    def closeEvent(self, event):
        options.settings.setValue("corpusmanager_size", self.size())
        options.set_current_server(options.cfg.current_server)
                    
def main():
    app = QtGui.QApplication(sys.argv)
    installer_list = CorpusManager.display("../installer", lambda x: x, lambda x: x)
    #app.exec_()
    
if __name__ == "__main__":
    main()

logger = logging.getLogger(NAME)
