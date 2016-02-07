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

        path = os.path.join(sys.path[0], "doc", "build", "qthelp", "coquery.qhc")

        self.engine = QtHelp.QHelpEngine(path, self)
        self.engine.setupData()

        self.browser = classes.CoqHelpBrowser(self.engine)
        self.browser.setSource(QtCore.QUrl(
            os.path.join(sys.path[0], "doc", "build", "qthelp", "index.html")))
        
        self.engine.contentWidget().linkActivated.connect(lambda x: self.browser.setSource(x))
        self.engine.indexWidget().linkActivated.connect(lambda x: self.browser.setSource(x))

        self.tabs = QtGui.QTabWidget()
        self.tabs.addTab(self.engine.contentWidget(), "Contents")
        self.tabs.addTab(self.engine.indexWidget(), "Index")
        
        self.splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.insertWidget(0, self.tabs)
        self.splitter.insertWidget(1, self.browser)
        
        self.tabs.setMaximumWidth(self.tabs.minimumSizeHint().width() * 2)

        #self.splitter.hide()

        self.HorizontalLayout = QtGui.QHBoxLayout(self)
        self.HorizontalLayout.addWidget(self.splitter)

        try:
            self.resize(options.settings.value("help_size"))
        except TypeError:
            pass

    def closeEvent(self, event):
        options.settings.setValue("help_size", self.size())
        