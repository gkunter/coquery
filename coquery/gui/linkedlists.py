# -*- coding: utf-8 -*-
"""
linkedlists.py is part of Coquery.

Copyright (c) 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

from .pyqt_compat import QtCore, QtWidgets, QtGui
from .ui import coqLinkedListsUi


class CoqLinkedLists(QtWidgets.QAbstractItemView):
    """
    A QWidget that presents two hierarchical lists. The entries in the left
    list represent the higher order of the entries in the right list.
    """
    itemSelectionChanged = QtCore.Signal()
    currentItemChanged = QtCore.Signal(object)

    def __init__(self, *args, **kwargs):
        super(CoqLinkedLists, self).__init__(*args, **kwargs)
        self.ui = coqLinkedListsUi.Ui_CoqLinkedLists()
        self.ui.setupUi(self)
        self._width_left = None
        self._set_left_width(0)
        self.models = []
        self.ui.list_classes.currentRowChanged.connect(
            self.setCurrentCategoryRow)

    def verticalOffset(self):
        return 0

    def horizontalOffset(self):
        return 0

    def _set_left_width(self, w):
        max_w = QtWidgets.QWidget.sizeHint(self).width()
        self.ui.splitter.setSizes([w, max_w - w])
        self._width_left = w

    def addList(self, left_item, right_items):
        self.ui.list_classes.addItem(left_item)
        self._set_left_width(max(self._width_left,
                                 QtWidgets.QLabel(left_item.text()).sizeHint().width()))

        new_model = QtGui.QStandardItemModel()
        for item in right_items:
            new_model.appendRow(item)
        self.models.append(new_model)

    def list_(self, index):
        return self.models[index]

    def indexOfCategory(self, item):
        for i in range(self.ui.list_classes.count()):
            list_item = self.ui.list_classes.item(i)
            if item == list_item:
                return i
        return None

    def listCount(self):
        return len(self.models)

    def setCurrentListRow(self, i):
        index = self.ui.list_functions.model().index(i, 0)
        selection_model = self.ui.list_functions.selectionModel()
        selection_model.select(index, selection_model.Select)

    def setAlternatingRowColors(self, value):
        self.ui.list_functions.setAlternatingRowColors(value)

    def setCurrentCategoryRow(self, i):
        self.blockSignals(True)
        self.ui.list_classes.blockSignals(True)

        self.ui.list_functions.setModel(self.models[i])
        self.ui.list_classes.setCurrentRow(i)

        self.blockSignals(False)
        self.ui.list_classes.blockSignals(False)

    def setListDelegate(self, delegate):
        delegate.setParent(self.ui.list_functions)
        self.ui.list_functions.setItemDelegate(delegate)

    def setCategoryDelegate(self, delegate):
        delegate.setParent(self.ui.list_classes)
        self.ui.list_classes.setDelegate(delegate)

    def setEditTriggers(self, *args, **kwargs):
        self.ui.list_functions.setEditTriggers(*args, **kwargs)


def main():
    import sys
    from .groups import GroupFunctionWidget
    from .groups import GroupFunctionDelegate

    from ..functions import (
                        Function,
                        get_base_func,
                        #FilteredRows, PassingRows,
                        Entropy,
                        #SuperCondProb, ExternalCondProb,
                        Min, Max, Mean, Median, StandardDeviation,
                        InterquartileRange,
                        Freq, FreqNorm,
                        FreqPTW, FreqPMW,
                        ReferenceCorpusSize,
                        ReferenceCorpusFrequency,
                        ReferenceCorpusFrequencyPTW,
                        ReferenceCorpusFrequencyPMW,
                        ReferenceCorpusLLKeyness,
                        ReferenceCorpusDiffKeyness,
                        RowNumber,
                        Percent, Proportion,
                        Tokens, Types,
                        TypeTokenRatio,
                        CorpusSize, SubcorpusSize)

    x = (("Corpus", [CorpusSize, SubcorpusSize]),
         ("Distribution", [
             Freq, FreqNorm, FreqPTW, FreqPMW,
             Tokens, Types, TypeTokenRatio]),
         ("Statistics", [
             Min, Max, Mean, Median, StandardDeviation,
             InterquartileRange]),
         ("Reference corpus", [
             ReferenceCorpusSize,
             ReferenceCorpusFrequency,
             ReferenceCorpusFrequencyPTW,
             ReferenceCorpusFrequencyPMW,
             ReferenceCorpusDiffKeyness,
             ReferenceCorpusLLKeyness]),
         )


    app = QtWidgets.QApplication(sys.argv)

    l = CoqLinkedLists()
    l.setEditTriggers(l.CurrentChanged)
    l.setAlternatingRowColors(True)
    delegate = GroupFunctionDelegate()
    l.setListDelegate(delegate)

    for grp, lst in x:
        group_item = QtWidgets.QListWidgetItem(grp)
        function_items = []
        for fnc in lst:
            list_item = QtGui.QStandardItem(str(fnc))
            list_item.setData([fnc, [], [], False], QtCore.Qt.UserRole)
            function_items.append(list_item)

        l.addList(group_item, function_items)

    l.show()
    app.exec_()

    for i in range(l.listCount()):
        sublist = l.list_(i)
        for row in range(sublist.rowCount()):
            item = sublist.item(row, 0)
            print(item.data(QtCore.Qt.UserRole))



if __name__ == "__main__":
    main()