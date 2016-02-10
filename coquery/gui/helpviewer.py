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

from ui.helpViewerUi import Ui_HelpViewer

class HelpViewer(QtGui.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(HelpViewer, self).__init__(*args, **kwargs)

        self.ui = Ui_HelpViewer()
        self.ui.setupUi(self)
        
        self.ui.index.anchorClicked.connect(self.show_index)
        self.ui.content.anchorClicked.connect(self.show_content)
        
        self.ui.action_prev.triggered.connect(self.ui.content.backward)
        self.ui.action_next.triggered.connect(self.ui.content.forward)
        self.ui.action_home.triggered.connect(lambda:
            self.ui.content.setSource(QtCore.QUrl(
                os.path.join(options.cfg.base_path, "doc", "build", "qthelp", "welcome.html"))))
        self.ui.action_zoom_in.triggered.connect(self.ui.content.zoomIn)
        self.ui.action_zoom_in.triggered.connect(self.ui.index.zoomIn)
        self.ui.action_zoom_out.triggered.connect(self.ui.content.zoomOut)
        self.ui.action_zoom_out.triggered.connect(self.ui.index.zoomOut)
        
        
        self.ui.content.setSource(QtCore.QUrl(
            os.path.join(options.cfg.base_path, "doc", "build", "qthelp", "welcome.html")))
        self.ui.index.setSource(QtCore.QUrl(
            os.path.join(options.cfg.base_path, "doc", "build", "qthelp", "index.html")))

        self.ui.splitter.setSizes([
            self.sizeHint().width() * 0.38,
            self.sizeHint().width() * 0.62])

        try:
            self.resize(options.settings.value("help_size"))
        except TypeError:
            pass
        try:
            self.ui.splitter.restoreState(options.settings.value("help_splitter"))
        except TypeError:
            pass
        
    def show_content(self):
        print("show_content")
        
    def show_index(self, *args, **kwargs):
        self.ui.content.setSource(args[0])

    def closeEvent(self, event):
        options.settings.setValue("help_size", self.size())
        options.settings.setValue("help_splitter", self.ui.splitter.saveState())