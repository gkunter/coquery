# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import division

from pyqt_compat import QtCore, QtGui

import sys
import corpusInstallUi
import fnmatch
import os
import imp

sys.path.append(os.path.join(sys.path[0], ".."))
sys.path.append(os.path.join(sys.path[0], "../installer"))

class CoqAccordionEntry(QtGui.QWidget):
    """ Define a QWidget that can be used as an entry in a accordion list."""
    def __init__(self, *args):
        super(CoqAccordionEntry, self).__init__(*args)
        self._title = ""
        self._text = ""
        self._url = ""
        self.setup_ui()
    
    def setTitle(self, title):
        self._title = title
        self.label_title.setText(self._title)

    def setDescription(self, text):
        self._text = text
        self.change_description()
        
    def setURL(self, url):
        self._url = url
        self.change_description()
        
    def change_description(self):
        self.corpus_description.setText(
            "<p><font size='100%'>{0}</font></p><p><a href='{1}'>{1}</p>".format(
                self._text, self._url))

    def setup_ui(self):
        self.corpus_entry = QtGui.QFrame(self)
        self.corpus_list_entry = QtGui.QVBoxLayout(self.corpus_entry)
        self.corpus_list_entry.setSpacing(0)
        
        self.header_box = QtGui.QFrame(self.corpus_entry)
        self.header_box.setStyleSheet("background-color: lightgrey;")
        self.header_box.setFrameShape(QtGui.QFrame.Box)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.header_box.sizePolicy().hasHeightForWidth())
        self.header_box.setSizePolicy(sizePolicy)

        
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.header_box)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setContentsMargins(10, -1, 10, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        
        self.expand_button = QtGui.QLabel(self.header_box)
        self.expand_button.setText("+")
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.expand_button.sizePolicy().hasHeightForWidth())
        
        self.expand_button.setSizePolicy(sizePolicy)
        self.expand_button.setAlignment(QtCore.Qt.AlignCenter)
        self.horizontalLayout.addWidget(self.expand_button)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)

        self.label_title = QtGui.QLabel(self.header_box)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_title.sizePolicy().hasHeightForWidth())

        self.label_title.setSizePolicy(sizePolicy)
        self.label_title.setFrameShape(QtGui.QFrame.NoFrame)
        self.horizontalLayout_2.addWidget(self.label_title)
        self.corpus_list_entry.addWidget(self.header_box)

        self.description_area = QtGui.QFrame(self.corpus_entry)
        self.description_area.setStyleSheet("QFrame {color: black; background-color: white;}")
        self.description_area.setFrameShape(QtGui.QFrame.Box)
        self.description_area.setFrameShadow(QtGui.QFrame.Raised)
        self.verticalLayout = QtGui.QVBoxLayout(self.description_area)
        self.verticalLayout.setSpacing(20)
        self.verticalLayout.setContentsMargins(45, 20, 20, 20)

        self.corpus_description = QtGui.QLabel(self.description_area)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.corpus_description.sizePolicy().hasHeightForWidth())
        self.corpus_description.setSizePolicy(sizePolicy)
        self.corpus_description.setWordWrap(True)
        self.verticalLayout.addWidget(self.corpus_description)

        self.layout_button = QtGui.QHBoxLayout()
        self.button_install = QtGui.QPushButton(self.description_area)
        self.button_install.setText("Install")
        
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_install.sizePolicy().hasHeightForWidth())
        self.button_install.setSizePolicy(sizePolicy)

        self.layout_button.addWidget(self.button_install)

        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.layout_button.addItem(spacerItem)
        self.verticalLayout.addLayout(self.layout_button)
        self.corpus_list_entry.addWidget(self.description_area)

class CorpusInstallList(QtGui.QDialog):
    def __init__(self, parent=None):
        super(CorpusInstallList, self).__init__(parent)
        self.ui = corpusInstallUi.Ui_Dialog()
        self.ui.setupUi(self)
        
        self.corpus_form_layout = QtGui.QVBoxLayout()
        self.group_box = QtGui.QGroupBox()
        
        #self.list_model = QtGui.QStandardItemModel(self.ui.corpus_list)
        #self.ui.corpus_list.setModel(self.list_model)
        

    def read(self, path):
        matches = []
        row = 0
        for root, dirnames, filenames in os.walk(path):
            for fullpath in fnmatch.filter(filenames, 'coq_*.py'):
                module_path = os.path.join(root, fullpath)
                basename, ext = os.path.splitext(os.path.basename(fullpath))
                try:
                    module = imp.load_source(basename, module_path)
                except ImportError as e:
                    continue
                try:
                    builder_class = module.BuilderClass
                except AttributeError:
                    continue

                title = builder_class.get_title()
                url = builder_class.get_url()
                description = "".join(["<p>{}</p>".format(x) for x in builder_class.get_description()])

                self.entry_list = []

                entry = CoqAccordionEntry()
                entry.setTitle(title)
                entry.setDescription(description)
                entry.setURL(url)
                self.entry_list.append(entry)

                self.corpus_form_layout.addWidget(entry)

                entry = CoqAccordionEntry()
                entry.setTitle(title)
                entry.setDescription(description)
                entry.setURL(url)
                self.entry_list.append(entry)

                self.corpus_form_layout.addWidget(entry)
            
                entry = CoqAccordionEntry()
                entry.setTitle(title)
                entry.setDescription(description)
                entry.setURL(url)
                self.entry_list.append(entry)

                self.corpus_form_layout.addWidget(entry)
                
                
        self.group_box.setLayout(self.corpus_form_layout)
        self.ui.scroll_area_corpus.setWidget(self.group_box)
        self.ui.scroll_area_corpus.setWidgetResizable(True)

                    
    #def accept(self):
        #pass
    
    #def reject(self):
        #pass
        
    @staticmethod
    def display(parent=None):
        dialog = CorpusInstallList(parent=parent)        
        dialog.read(os.path.abspath(os.path.normpath(os.path.join(sys.path[0], "../installer"))))
        
        foods = [
            'Cookie dough', # Must be store-bought
            'Hummus', # Must be homemade
            'Spaghetti', # Must be saucy
            'Dal makhani', # Must be spicy
            'Chocolate whipped cream' # Must be plentiful
        ]
        
        for food in foods * 10:
            # Create an item with a caption
            item = QtGui.QStandardItem()
        
            # Add the item to the model
            #dialog.list_model.appendRow(item)
        
        dialog.exec_()

    def add_source_label(self, name, content):
        pass

def main():
    app = QtGui.QApplication(sys.argv)
    installer_list = CorpusInstallList.display()
    #app.exec_()
    
if __name__ == "__main__":
    main()



def main2():
    app = QtGui.QApplication(sys.argv)
    entry1 = CoqAccordionEntry()
    entry1.setTitle("British National Corpus")
    entry1.setText("For a long time, Qt has allowed you to decorate your GUIs with CSS’ish style sheets. Inspired by the web, stylesheets are a great way to stylize your Qt GUI, but it seems that few people use them. In this tutorial, we’ll create an example dialog in Qt using Designer and stylesheets. This tutorial assumes that you can get around in Qt Designer, and that you understand a little about Qt layouts.")
    
    entry2 = CoqAccordionEntry()
    entry2.setTitle("Corpus of Contemporary American English")
    entry2.setText("The creation of non standard presentations for Lists/Libraries  is a fairly common  scenario and using the XSLT List View Web Part (XLV) possibilities that can be achieved pretty easily. Let’s take a look how to render list of question and answers using Accordion Menu in SharePoint. Actually the idea for this post appeared after posting  of corresponding question on StackOverflow. So, let’s discuss how it could be accomplished using XLV. For Accordion we will utilize jQuery UI library.")
    
    
    #widget_layout = QtGui.QVBoxLayout()
    #widget_layout.addWidget(entry1)
    #widget_layout.addWidget(entry2)
    ##widget_layout.addStretch()
    ##widget_layout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
    
    #widget = QtGui.QWidget()
    #widget.setLayout(widget_layout)
    
    #widget.show()
    
    #itemN = QtGui.QListWidgetItem()
    #itemN.setSizeHint(widget.sizeHint())
    #list_view = QtGui.QListWidget()
    #list_view.addItem(itemN)
    #list_view.setItemWidget(itemN, widget)
    
    #list_view.show()
    
    itemN = QtGui.QListWidgetItem() 
    #Create widget
    widget = QtGui.QWidget()
    widgetText = QtGui.QLabel("I love PyQt!")
    widgetButton = QtGui.QPushButton("Push Me")
    widgetLayout = QtGui.QVBoxLayout()
    widgetLayout.addWidget(widgetText)
    widgetLayout.addWidget(widgetButton)
    widgetLayout.addWidget(entry1)
    widgetLayout.addWidget(entry2)
    
    widgetLayout.addStretch()

    widgetLayout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
    widget.setLayout(widgetLayout)  
    itemN.setSizeHint(widget.sizeHint())    

    funList = QtGui.QListWidget()
    #Add widget to QListWidget funList
    funList.addItem(itemN)
    funList.setItemWidget(itemN, widget)
    
    funList.show()
    
    app.exec_()
    print("done")
