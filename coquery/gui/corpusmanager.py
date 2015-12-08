# -*- coding: utf-8 -*-

"""
corpusmanager.py is part of Coquery.

Copyright (c) 2015 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License.
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
from __future__ import division


from pyqt_compat import QtCore, QtGui

import sys
import corpusManagerUi
import fnmatch
import os
import imp
import logging

sys.path.append(os.path.join(sys.path[0], ".."))
import __init__
sys.path.append(os.path.join(sys.path[0], "../installer"))

import options
from defines import *

class CoqAccordionEntry(QtGui.QWidget):
    """ Define a QWidget that can be used as an entry in a accordion list."""
    def __init__(self, stack=None, *args):
        super(CoqAccordionEntry, self).__init__(*args)
        self._title = ""
        self._text = ""
        self._url = ""
        self._name = ""
        self._references = ""
        self._license = ""
        self._builder_class = None
        self.stack=stack
        
        self.verticalLayout_2 = QtGui.QVBoxLayout(self)
        self.corpus_description_frame = QtGui.QFrame(self)
        self.corpus_description_frame.setStyleSheet("QFrame { background-color: rgb(250, 250, 251); }")
        self.corpus_description_frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.corpus_description_frame.setFrameShadow(QtGui.QFrame.Sunken)
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.corpus_description_frame)
        self.verticalLayout_3.setSpacing(20)
        self.verticalLayout_3.setMargin(20)
        self.corpus_description = QtGui.QLabel(self.corpus_description_frame)
        self.corpus_description.setWordWrap(True)
        self.corpus_description.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.corpus_description.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextBrowserInteraction|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.corpus_description.setOpenExternalLinks(True)

        self.verticalLayout_3.addWidget(self.corpus_description)
        
        self.button_layout = QtGui.QHBoxLayout()
        self.button_layout.setSpacing(0)
        self.button_manage = QtGui.QPushButton(self.corpus_description_frame)
        self.button_layout.addWidget(self.button_manage)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.button_layout.addItem(spacerItem)
        self.verticalLayout_3.addLayout(self.button_layout)
        #spacerItem1 = QtGui.QSpacerItem(20, 215, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        #self.verticalLayout_3.addItem(spacerItem1)
        
        self.verticalLayout_2.addWidget(self.corpus_description_frame)

    def setupInstallState(self, installed):
        if installed:
            self.button_manage.setText("Remove")
            if self.stack:
                self.button_manage.clicked.connect(lambda x: 
                self.stack.removeCorpus.emit(self._name))
        else:
            self.button_manage.setText("Install")
            if self.stack:
                self.button_manage.clicked.connect(lambda x: 
                self.stack.installCorpus.emit(self._builder_class))
    
    def setReferences(self, ref):
        self._references = ref
        self.change_description()
    
    def setTitle(self, title):
        self._title = title
        self.change_description()
        
    def setLicense(self, license):
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
        self._url = url
        self.change_description()
        
    def change_description(self):
        self.corpus_description.setText(
            "<p><b>{title}</b></p><p><font size='100%'>{desc}</font></p>{ref}{license}<p><b>URL: </b><a href='{url}'>{url}</p>".format(
                title=self._title, 
                desc=self._text, 
                url=self._url, 
                ref=self._references, 
                license=self._license))

    #def setup_ui(self):
        #self.corpus_entry = QtGui.QFrame(self)
        
        #sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
        #sizePolicy.setHorizontalStretch(0)
        #sizePolicy.setVerticalStretch(0)
        #sizePolicy.setHeightForWidth(self.corpus_entry.sizePolicy().hasHeightForWidth())
        #self.corpus_entry.setSizePolicy(sizePolicy)

        
        
        #self.corpus_list_entry = QtGui.QVBoxLayout(self.corpus_entry)
        #self.corpus_list_entry.setSpacing(0)
        
        ##self.header_box = QtGui.QFrame(self.corpus_entry)
        ##self.header_box.setStyleSheet("background-color: lightgrey;")
        ##self.header_box.setFrameShape(QtGui.QFrame.Box)

        ##sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)
        ##sizePolicy.setHorizontalStretch(0)
        ##sizePolicy.setVerticalStretch(0)
        ##sizePolicy.setHeightForWidth(self.header_box.sizePolicy().hasHeightForWidth())
        ##self.header_box.setSizePolicy(sizePolicy)

        
        ##self.horizontalLayout_2 = QtGui.QHBoxLayout(self.header_box)
        ##self.horizontalLayout_2.setSpacing(0)
        ##self.horizontalLayout = QtGui.QHBoxLayout()
        ##self.horizontalLayout.setSpacing(0)
        ##self.horizontalLayout.setContentsMargins(10, -1, 10, -1)
        ##self.horizontalLayout.setObjectName("horizontalLayout")
        
        ##self.expand_button = QtGui.QLabel(self.header_box)
        ##self.expand_button.setText("+")
        ##sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        ##sizePolicy.setHorizontalStretch(0)
        ##sizePolicy.setVerticalStretch(0)
        ##sizePolicy.setHeightForWidth(self.expand_button.sizePolicy().hasHeightForWidth())
        
        ##self.expand_button.setSizePolicy(sizePolicy)
        ##self.expand_button.setAlignment(QtCore.Qt.AlignCenter)
        ##self.horizontalLayout.addWidget(self.expand_button)
        ##self.horizontalLayout_2.addLayout(self.horizontalLayout)

        ##self.label_title = QtGui.QLabel(self.header_box)
        ##sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Preferred)
        ##sizePolicy.setHorizontalStretch(0)
        ##sizePolicy.setVerticalStretch(0)
        ##sizePolicy.setHeightForWidth(self.label_title.sizePolicy().hasHeightForWidth())

        ##self.label_title.setSizePolicy(sizePolicy)
        ##self.label_title.setFrameShape(QtGui.QFrame.NoFrame)
        ##self.horizontalLayout_2.addWidget(self.label_title)
        ##self.corpus_list_entry.addWidget(self.header_box)

        #self.description_area = QtGui.QFrame(self.corpus_entry)
        #self.description_area.setStyleSheet("QFrame {color: black; background-color: white;}")
        #self.description_area.setFrameShape(QtGui.QFrame.Box)
        #self.description_area.setFrameShadow(QtGui.QFrame.Raised)
        #self.verticalLayout = QtGui.QVBoxLayout(self.description_area)
        #self.verticalLayout.setSpacing(20)
        #self.verticalLayout.setContentsMargins(45, 20, 20, 20)

        #self.corpus_description = QtGui.QLabel(self.description_area)
        #sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        #sizePolicy.setHorizontalStretch(0)
        #sizePolicy.setVerticalStretch(0)
        #sizePolicy.setHeightForWidth(self.corpus_description.sizePolicy().hasHeightForWidth())
        #self.corpus_description.setSizePolicy(sizePolicy)
        #self.corpus_description.setWordWrap(True)
        #self.verticalLayout.addWidget(self.corpus_description)

        #self.layout_button = QtGui.QHBoxLayout()
        #self.button_install = QtGui.QPushButton(self.description_area)
        #self.button_install.setText("Install")
        
        #sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        #sizePolicy.setHorizontalStretch(0)
        #sizePolicy.setVerticalStretch(0)
        #sizePolicy.setHeightForWidth(self.button_install.sizePolicy().hasHeightForWidth())
        #self.button_install.setSizePolicy(sizePolicy)

        #self.layout_button.addWidget(self.button_install)

        #spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        #self.layout_button.addItem(spacerItem)
        #self.verticalLayout.addLayout(self.layout_button)
        #self.corpus_list_entry.addWidget(self.description_area)

class CorpusManager(QtGui.QDialog):
    removeCorpus = QtCore.Signal(object)
    installCorpus = QtCore.Signal(object)

    def __init__(self, parent=None):
        super(CorpusManager, self).__init__(parent)
        self.ui = corpusManagerUi.Ui_corpusManager()
        self.ui.setupUi(self)
        self.icon = QtGui.QIcon.fromTheme("server-database")
        
        try:
            self.resize(self.width(), options.cfg.corpus_manager_view_height)
        except AttributeError:
            pass
        try:
            self.resize(options.cfg.corpus_manager_view_width, self.height())
        except AttributeError:
            pass

        
        #self.corpus_form_layout = QtGui.QVBoxLayout()
        #self.group_box = QtGui.QGroupBox()
        
        #self.list_model = QtGui.QStandardItemModel(self.ui.corpus_list)
        #self.ui.corpus_list.setModel(self.list_model)
        
    def read(self, path):
        matches = []
        row = 0
        for root, dirnames, filenames in os.walk(path):
            installer_list = sorted(fnmatch.filter(filenames, 'coq_install_*.py'), reverse=True)
            try:
                installer_list.remove("coq_install_generic.py")
            except ValueError:
                pass
            for fullpath in installer_list:
                module_path = os.path.join(root, fullpath)
                basename, ext = os.path.splitext(os.path.basename(fullpath))
                try:
                    module = imp.load_source(basename, module_path)
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
                    builder_class = module.BuilderClass
                except AttributeError:
                    continue
                entry = CoqAccordionEntry(stack=self)

                name = builder_class.get_name()
                entry.setName(name)

                title = builder_class.get_title()
                entry.setTitle(title)
                
                if builder_class.get_url():
                    entry.setURL(builder_class.get_url())
                
                if builder_class.get_description():
                    entry.setDescription(
                        "".join(["<p>{}</p>".format(x) for x in builder_class.get_description()]))
                    
                if builder_class.get_references():
                    references = "".join(["<p><span style='padding-left: 2em; text-indent: 2em;'>{}</span></p>".format(x) for x in builder_class.get_references()])
                    entry.setReferences("<p><b>References</b>{}".format(references))
                    
                if builder_class.get_license():
                    entry.setLicense("<p><b>License</b></p><p>{}</p>".format(builder_class.get_license()))

                entry.setupInstallState(name.lower() in options.get_available_resources(options.cfg.current_server))
                entry.setBuilderClass(builder_class)

                self.ui.corpus_stack.addItem(entry, self.icon, name)
                
        self.ui.scroll_area_corpus.setWidgetResizable(True)
        self.ui.corpus_stack.setCurrentIndex(self.ui.corpus_stack.count() - 1)


    def closeEvent(self, *args):
        options.cfg.corpus_manager_view_height = self.height()
        options.cfg.corpus_manager_view_width = self.width()
                    
    @staticmethod
    def display(path, install_func, remove_func, parent=None):
        dialog = CorpusManager(parent=parent)        
        dialog.show()
        dialog.read(path)
        
        dialog.installCorpus.connect(install_func)
        dialog.removeCorpus.connect(remove_func)
        
        
        dialog.exec_()

    def add_source_label(self, name, content):
        pass

def main():
    app = QtGui.QApplication(sys.argv)
    installer_list = CorpusManager.display("../installer", lambda x: x, lambda x: x)
    #app.exec_()
    
if __name__ == "__main__":
    main()

logger = logging.getLogger(__init__.NAME)
