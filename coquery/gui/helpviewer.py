# -*- coding: utf-8 -*-
"""
helpviewer.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import os
import sys

from pyqt_compat import QtCore, QtGui, QtHelp

import classes
import options

class HelpViewer(QtGui.QDialog):
    def __init__(self, *args, **kwargs):
        super(HelpViewer, self).__init__(*args, **kwargs)

        self.content = QtGui.QTextBrowser(self)
        self.content.setSource(QtCore.QUrl(
            os.path.join(sys.path[0], "doc", "build", "qthelp", "firststeps.html")))
        
        self.index = QtGui.QTextBrowser(self)
        self.index.setSource(QtCore.QUrl(
            os.path.join(sys.path[0], "doc", "build", "qthelp", "index.html")))
       
        self.splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.insertWidget(0, self.index)
        self.splitter.insertWidget(1, self.content)
        
        #self.splitter.hide()

        self.HorizontalLayout = QtGui.QHBoxLayout(self)
        self.HorizontalLayout.addWidget(self.splitter)


        self.show()








        #path = os.path.join(sys.path[0], "doc", "build", "qthelp", "coquery.qhc")
        
        #help_engine = QtHelp.QHelpEngine(path, self)
        #help_engine.setupData()
        #content_model = help_engine.contentModel()
        #content_widget = help_engine.contentWidget()
        #index_model = help_engine.indexModel()
        #index_widget = help_engine.indexWidget()
        
        #splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)

        #splitter.addWidget(content_widget)
        #splitter.addWidget(index_widget)
        #content_widget.setModel(content_model)
        #index_widget.setModel(index_model)
        
        #splitter.show()
        
        self.setWindowTitle("Help – Coquery")
        
        #self.engine = QtHelp.QHelpEngine(path, self)
        #self.engine.setupData()

        #print(self.engine.contentModel().rowCount())

        #self.browser = classes.CoqHelpBrowser()
        #self.browser.webkit.setUrl(QtCore.QUrl(
            #os.path.join(sys.path[0], "doc", "build", "qthelp", "index.html")))

            
        #self.HorizontalLayout = QtGui.QHBoxLayout(self)
        #self.HorizontalLayout.addWidget(self.browser)

        #self.engine.contentWidget().linkActivated.connect(self.show_content)
        #self.engine.indexWidget().linkActivated.connect(self.show_index)

        #self.tabs = QtGui.QTabWidget()
        #self.tabs.addTab(self.engine.contentWidget(), "Contents")
        #self.tabs.addTab(self.engine.indexWidget(), "Index")
        
        #self.engine.contentWidget().setModel(self.engine.contentModel())
        #self.engine.indexWidget().setModel(self.engine.indexModel())
       
        #self.splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
        #self.splitter.insertWidget(0, self.tabs)
        #self.splitter.insertWidget(1, self.browser)
        
        #self.tabs.setMaximumWidth(self.tabs.minimumSizeHint().width() * 2)

        ##self.splitter.hide()

        #self.HorizontalLayout = QtGui.QHBoxLayout(self)
        #self.HorizontalLayout.addWidget(self.splitter)

        try:
            self.resize(options.settings.value("help_size"))
        except TypeError:
            pass

    def show_content(self):
        print("show_content")
        
    def show_index(self):
        print("show_index")

    def closeEvent(self, event):
        options.settings.setValue("help_size", self.size())
        