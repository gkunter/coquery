# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'linkselect.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from coquery.gui.pyqt_compat import QtCore, QtGui, frameShadow, frameShape

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
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(LinkSelect.sizePolicy().hasHeightForWidth())
        LinkSelect.setSizePolicy(sizePolicy)
        self.verticalLayout = QtGui.QVBoxLayout(LinkSelect)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox = QtGui.QGroupBox(LinkSelect)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.tree_resource = CoqResourceTree(self.groupBox)
        self.tree_resource.setObjectName(_fromUtf8("tree_resource"))
        self.tree_resource.headerItem().setText(0, _fromUtf8("1"))
        self.gridLayout_2.addWidget(self.tree_resource, 0, 1, 1, 1)
        self.label_from_corpus = QtGui.QLabel(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_from_corpus.sizePolicy().hasHeightForWidth())
        self.label_from_corpus.setSizePolicy(sizePolicy)
        self.label_from_corpus.setObjectName(_fromUtf8("label_from_corpus"))
        self.gridLayout_2.addWidget(self.label_from_corpus, 0, 0, 1, 1, QtCore.Qt.AlignTop)
        self.gridLayout_2.setColumnStretch(1, 1)
        self.verticalLayout.addWidget(self.groupBox)
        self.groupbox = QtGui.QGroupBox(LinkSelect)
        self.groupbox.setObjectName(_fromUtf8("groupbox"))
        self.gridLayout = QtGui.QGridLayout(self.groupbox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tree_external = CoqResourceTree(self.groupbox)
        self.tree_external.setObjectName(_fromUtf8("tree_external"))
        self.tree_external.headerItem().setText(0, _fromUtf8("1"))
        self.gridLayout.addWidget(self.tree_external, 2, 1, 1, 1)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.combo_corpus = QtGui.QComboBox(self.groupbox)
        self.combo_corpus.setObjectName(_fromUtf8("combo_corpus"))
        self.verticalLayout_2.addWidget(self.combo_corpus)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.gridLayout.addLayout(self.verticalLayout_2, 2, 0, 1, 1)
        self.gridLayout.setColumnStretch(1, 1)
        self.verticalLayout.addWidget(self.groupbox)
        self.widget_link_info = QtGui.QWidget(LinkSelect)
        self.widget_link_info.setObjectName(_fromUtf8("widget_link_info"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.widget_link_info)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_from = QtGui.QLabel(self.widget_link_info)
        self.label_from.setObjectName(_fromUtf8("label_from"))
        self.horizontalLayout_2.addWidget(self.label_from)
        self.label_4 = QtGui.QLabel(self.widget_link_info)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.horizontalLayout_2.addWidget(self.label_4)
        self.label_to = QtGui.QLabel(self.widget_link_info)
        self.label_to.setObjectName(_fromUtf8("label_to"))
        self.horizontalLayout_2.addWidget(self.label_to)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.label_explain = QtGui.QLabel(self.widget_link_info)
        self.label_explain.setWordWrap(True)
        self.label_explain.setObjectName(_fromUtf8("label_explain"))
        self.verticalLayout_3.addWidget(self.label_explain)
        self.verticalLayout.addWidget(self.widget_link_info)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.checkBox = QtGui.QCheckBox(LinkSelect)
        self.checkBox.setChecked(True)
        self.checkBox.setObjectName(_fromUtf8("checkBox"))
        self.horizontalLayout.addWidget(self.checkBox)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.buttonBox = QtGui.QDialogButtonBox(LinkSelect)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout.addWidget(self.buttonBox)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 1)

        self.retranslateUi(LinkSelect)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), LinkSelect.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), LinkSelect.reject)
        QtCore.QMetaObject.connectSlotsByName(LinkSelect)

    def retranslateUi(self, LinkSelect):
        LinkSelect.setWindowTitle(_translate("LinkSelect", "Select link column – Coquery", None))
        self.groupBox.setTitle(_translate("LinkSelect", "&Current corpus", None))
        self.label_from_corpus.setText(_translate("LinkSelect", "<html><head/><body><p><span style=\" font-weight:600;\">{from_res}</span></p></body></html>", None))
        self.groupbox.setTitle(_translate("LinkSelect", "E&xternal corpus", None))
        self.label_from.setText(_translate("LinkSelect", "<html><head/><body><p><span style=\" font-weight:600;\">{from_table}.{from_resource}</span></p></body></html>", None))
        self.label_4.setText(_translate("LinkSelect", "will be linked to", None))
        self.label_to.setText(_translate("LinkSelect", "<html><head/><body><p><span style=\" font-weight:600;\">{to}.{to_table}.{to_resource}</span></p></body></html>", None))
        self.label_explain.setText(_translate("LinkSelect", "The remaining columns from {to}.{to_table} will be available as output columns.", None))
        self.checkBox.setText(_translate("LinkSelect", "Ignore case when comparing contents.", None))

from ..resourcetree import CoqResourceTree

