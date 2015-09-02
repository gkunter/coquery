# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'linkselect.ui'
#
# Created: Wed Sep  2 20:44:16 2015
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from pyqt_compat import QtCore, QtGui, frameShadow

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_LinkSelect(object):
    def setupUi(self, LinkSelect):
        LinkSelect.setObjectName(_fromUtf8("LinkSelect"))
        LinkSelect.resize(640, 480)
        self.verticalLayout_2 = QtGui.QVBoxLayout(LinkSelect)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.frame = QtGui.QFrame(LinkSelect)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(frameShadow)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.verticalLayout = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout.setSpacing(20)
        self.verticalLayout.setMargin(10)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(self.frame)
        self.label.setWordWrap(True)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.checkBox = QtGui.QCheckBox(self.frame)
        self.checkBox.setChecked(True)
        self.checkBox.setObjectName(_fromUtf8("checkBox"))
        self.verticalLayout.addWidget(self.checkBox)
        self.label_2 = QtGui.QLabel(self.frame)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.treeWidget = QtGui.QTreeWidget(self.frame)
        self.treeWidget.setAlternatingRowColors(False)
        self.treeWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
        self.treeWidget.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.treeWidget.setIndentation(40)
        self.treeWidget.setAnimated(True)
        self.treeWidget.setAllColumnsShowFocus(True)
        self.treeWidget.setHeaderHidden(True)
        self.treeWidget.setColumnCount(1)
        self.treeWidget.setObjectName(_fromUtf8("treeWidget"))
        self.treeWidget.header().setVisible(False)
        self.treeWidget.header().setCascadingSectionResizes(False)
        self.treeWidget.header().setSortIndicatorShown(False)
        self.treeWidget.header().setStretchLastSection(True)
        self.verticalLayout.addWidget(self.treeWidget)
        self.verticalLayout_2.addWidget(self.frame)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(LinkSelect)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout.addWidget(self.buttonBox)
        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.retranslateUi(LinkSelect)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), LinkSelect.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), LinkSelect.reject)
        QtCore.QMetaObject.connectSlotsByName(LinkSelect)

    def retranslateUi(self, LinkSelect):
        LinkSelect.setWindowTitle(_translate("LinkSelect", "Select link column – Coquery", None))
        self.label.setText(_translate("LinkSelect", "<html><head/><body><p>You can link a data table from another corpus to the currently selected corpus by choosing a link column from the selector below. The content in the link column is compared to the content of the column <span style=\" font-weight:600;\">\'{resource_feature}\'</span> from the currently selected corpus. If the contents match, the columns from the linked data table can be included in the results view by selecting them as additional output columns.</p><p><span style=\" font-weight:600;\">Note:</span> If you select an external output column, query result from the currently selected corpus that does not match an entry in the linked external table are <span style=\" font-weight:600;\">dropped</span> from the results table. In other words, only complete records with data from the currently selected corpus and the external data table are queried.</p><p><span style=\" font-weight:600;\">Note:</span>  If you select an external output column, the time needed to execute the query may increase significantly.</p></body></html>", None))
        self.checkBox.setText(_translate("LinkSelect", "Ignore case when comparing contents.", None))
        self.label_2.setText(_translate("LinkSelect", "Link <b>{resource_feature}</b> to...", None))
        self.treeWidget.headerItem().setText(0, _translate("LinkSelect", "Corpus", None))


