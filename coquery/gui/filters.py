# -*- coding: utf-8 -*-
"""
addfilter.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import division
from __future__ import unicode_literals

from coquery import options
from .pyqt_compat import QtCore, QtWidgets
from .ui.filterDialogUi import Ui_FilterDialog


class FilterDialog(QtWidgets.QDialog):
    def __init__(self, filter_list, columns, dtypes, session, parent=None):
        super(FilterDialog, self).__init__(parent)
        self.ui = Ui_FilterDialog()
        self.ui.setupUi(self)
        self.ui.widget.setData(columns, dtypes, filter_list, session)
        self.ui.widget.listChanged.connect(self.update_buttons)
        self.update_buttons()

        try:
            self.resize(options.settings.value("filterdialog_size"))
        except TypeError:
            pass

    def update_buttons(self):
        ok_button = self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Ok)
        ok_button.setEnabled(self.ui.widget.isModified())

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.reject()

    def closeEvent(self, *args):
        options.settings.setValue("filterdialog_size", self.size())

    def exec_(self):
        result = super(FilterDialog, self).exec_()
        if result == self.Accepted:
            return self.ui.widget.filters()
        else:
            return None

    @staticmethod
    def set_filters(filter_list, **kwargs):
        dialog = FilterDialog(filter_list=filter_list, **kwargs)
        dialog.setVisible(True)

        return dialog.exec_()
