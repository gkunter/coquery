# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'installerSteps.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_InstallerStepSelection(object):
    def setupUi(self, InstallerStepSelection):
        InstallerStepSelection.setObjectName("InstallerStepSelection")
        InstallerStepSelection.resize(400, 300)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(InstallerStepSelection)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.checkbox_create_tables = QtWidgets.QCheckBox(InstallerStepSelection)
        self.checkbox_create_tables.setEnabled(False)
        self.checkbox_create_tables.setCheckable(False)
        self.checkbox_create_tables.setChecked(False)
        self.checkbox_create_tables.setObjectName("checkbox_create_tables")
        self.verticalLayout.addWidget(self.checkbox_create_tables)
        self.checkbox_load_files = QtWidgets.QCheckBox(InstallerStepSelection)
        self.checkbox_load_files.setEnabled(False)
        self.checkbox_load_files.setCheckable(False)
        self.checkbox_load_files.setChecked(False)
        self.checkbox_load_files.setObjectName("checkbox_load_files")
        self.verticalLayout.addWidget(self.checkbox_load_files)
        self.checkbox_optimize_columns = QtWidgets.QCheckBox(InstallerStepSelection)
        self.checkbox_optimize_columns.setChecked(True)
        self.checkbox_optimize_columns.setObjectName("checkbox_optimize_columns")
        self.verticalLayout.addWidget(self.checkbox_optimize_columns)
        self.checkbox_create_indices = QtWidgets.QCheckBox(InstallerStepSelection)
        self.checkbox_create_indices.setChecked(True)
        self.checkbox_create_indices.setObjectName("checkbox_create_indices")
        self.verticalLayout.addWidget(self.checkbox_create_indices)
        self.checkbox_write_corpus_module = QtWidgets.QCheckBox(InstallerStepSelection)
        self.checkbox_write_corpus_module.setChecked(True)
        self.checkbox_write_corpus_module.setTristate(False)
        self.checkbox_write_corpus_module.setObjectName("checkbox_write_corpus_module")
        self.verticalLayout.addWidget(self.checkbox_write_corpus_module)
        spacerItem = QtWidgets.QSpacerItem(20, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(InstallerStepSelection)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(InstallerStepSelection)
        self.buttonBox.accepted.connect(InstallerStepSelection.accept)
        self.buttonBox.rejected.connect(InstallerStepSelection.reject)
        QtCore.QMetaObject.connectSlotsByName(InstallerStepSelection)

    def retranslateUi(self, InstallerStepSelection):
        _translate = QtCore.QCoreApplication.translate
        InstallerStepSelection.setWindowTitle(_translate("InstallerStepSelection", "Choose installer steps – Coquery"))
        self.checkbox_create_tables.setText(_translate("InstallerStepSelection", "Create SQL tables"))
        self.checkbox_load_files.setText(_translate("InstallerStepSelection", "Load files"))
        self.checkbox_optimize_columns.setText(_translate("InstallerStepSelection", "Optimize columns"))
        self.checkbox_create_indices.setText(_translate("InstallerStepSelection", "Create indices"))
        self.checkbox_write_corpus_module.setText(_translate("InstallerStepSelection", "Write corpus module"))
