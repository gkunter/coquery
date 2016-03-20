# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mysql_guide.ui'
#
# Created: Wed Nov 18 15:28:56 2015
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from coquery.gui.pyqt_compat import QtCore, QtGui, frameShadow

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

class Ui_mysql_guide(object):
    def setupUi(self, mysql_guide):
        mysql_guide.setObjectName(_fromUtf8("mysql_guide"))
        mysql_guide.resize(640, 480)
        mysql_guide.setModal(True)
        mysql_guide.setWizardStyle(QtGui.QWizard.ModernStyle)
        mysql_guide.setOptions(QtGui.QWizard.NoBackButtonOnStartPage|QtGui.QWizard.NoCancelButton)
        self.wizardPage1 = QtGui.QWizardPage()
        self.wizardPage1.setObjectName(_fromUtf8("wizardPage1"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.wizardPage1)
        self.horizontalLayout.setMargin(50)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(self.wizardPage1)
        self.label.setWordWrap(True)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setContentsMargins(-1, 10, -1, 10)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.logo_label = QtGui.QLabel(self.wizardPage1)
        self.logo_label.setObjectName(_fromUtf8("logo_label"))
        self.verticalLayout.addWidget(self.logo_label)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.horizontalLayout.setStretch(0, 1)
        mysql_guide.addPage(self.wizardPage1)
        self.wizardPage2 = QtGui.QWizardPage()
        self.wizardPage2.setObjectName(_fromUtf8("wizardPage2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.wizardPage2)
        self.verticalLayout_2.setMargin(50)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.label_2 = QtGui.QLabel(self.wizardPage2)
        self.label_2.setWordWrap(True)
        self.label_2.setOpenExternalLinks(False)
        self.label_2.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout_2.addWidget(self.label_2)
        mysql_guide.addPage(self.wizardPage2)
        self.wizardPage = QtGui.QWizardPage()
        self.wizardPage.setObjectName(_fromUtf8("wizardPage"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.wizardPage)
        self.verticalLayout_3.setMargin(50)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.label_3 = QtGui.QLabel(self.wizardPage)
        self.label_3.setWordWrap(True)
        self.label_3.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout_3.addWidget(self.label_3)
        mysql_guide.addPage(self.wizardPage)
        self.wizardPage_2 = QtGui.QWizardPage()
        self.wizardPage_2.setObjectName(_fromUtf8("wizardPage_2"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.wizardPage_2)
        self.verticalLayout_4.setMargin(50)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.label_4 = QtGui.QLabel(self.wizardPage_2)
        self.label_4.setWordWrap(True)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.verticalLayout_4.addWidget(self.label_4)
        mysql_guide.addPage(self.wizardPage_2)
        self.wizardPage_3 = QtGui.QWizardPage()
        self.wizardPage_3.setObjectName(_fromUtf8("wizardPage_3"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.wizardPage_3)
        self.horizontalLayout_2.setMargin(50)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_5 = QtGui.QLabel(self.wizardPage_3)
        self.label_5.setWordWrap(True)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.horizontalLayout_2.addWidget(self.label_5)
        mysql_guide.addPage(self.wizardPage_3)
        self.wizardPage_4 = QtGui.QWizardPage()
        self.wizardPage_4.setObjectName(_fromUtf8("wizardPage_4"))
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.wizardPage_4)
        self.verticalLayout_5.setMargin(50)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.label_6 = QtGui.QLabel(self.wizardPage_4)
        self.label_6.setWordWrap(True)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.verticalLayout_5.addWidget(self.label_6)
        mysql_guide.addPage(self.wizardPage_4)

        self.retranslateUi(mysql_guide)
        QtCore.QMetaObject.connectSlotsByName(mysql_guide)

    def retranslateUi(self, mysql_guide):
        mysql_guide.setWindowTitle(_translate("mysql_guide", "MySQL server guide – Coquery", None))
        self.label.setText(_translate("mysql_guide", "<html><head/><body><p><span style=\" font-weight:600;\">MySQL server guide</span></p><p>This guide will assist you in setting up a MySQL database server so that it can be used by Coquery.</p></body></html>", None))
        self.logo_label.setText(_translate("mysql_guide", "logo", None))
        self.label_2.setText(_translate("mysql_guide", "<html><head/><body><p><span style=\" font-weight:600;\">MySQL server guide</span></p><p>Coquery requires a database server to make corpus queries. A <a href=\"https://en.wikipedia.org/wiki/Database_server\"><span style=\" text-decoration: underline; color:#0057ae;\">database server</span></a> is a computer program running in the background that provides access to the rows and columns of the data tables that are created when a Coquery corpus module is installed, and whenever you query the corpus.</p><p>The easiest way to access a database server is to install it locally on your computer. The corpus databases will also be saved on your harddisk. This guide will assist you in this setup.</p></body></html>", None))
        self.label_3.setText(_translate("mysql_guide", "<html><head/><body><p><span style=\" font-weight:600;\">MySQL server guide</span></p><p>There are different database servers. Coquery uses <a href=\"https://en.wikipedia.org/wiki/MySQL\"><span style=\" text-decoration: underline; color:#0057ae;\">MySQL</span></a> (or compatible), which considered to be fast and reliable. It is also available for free. </p><p>The MySQL homepage provides download instructions and installation guides for Windows, Mac OS X, and Linux computers. Click on the link: <a href=\"https://dev.mysql.com/usingmysql/get_started.html\"><span style=\" text-decoration: underline; color:#0057ae;\">\'Get Started with MySQL page\'</span></a> and follow the steps described on that page to install a MySQL server.</p><p>During the installation, you will have to create a MySQL root user. Keep a note of the user name and password that you enter.</p></body></html>", None))
        self.label_4.setText(_translate("mysql_guide", "<html><head/><body><p><span style=\" font-weight:600;\">MySQL server guide</span></p><p>You should now have a MySQL server installed on your computer.</p><p>Enter the root name and password that you noted during the installation into the MySQL Settings dialog. If the server was successfully installed, Coquery should be able to establish a connection to the server. The status area at the bottom of the screen should indicate this.</p></body></html>", None))
        self.label_5.setText(_translate("mysql_guide", "<html><head/><body><p><span style=\" font-weight:600;\">MySQL server guide</span></p><p>If the connection has successfully been established, you can close the MySQL Settings dialog. </p><p>If you do not wish to use the MySQL root account to run queries in Coquery, you can also create a new MySQL user. Enter the desired user name and password into the fields, and press tje button \'Create user\'. After you have provided the root account credentials and retyped the new user password, you can create this new user account.</p><p>Enter the new user credentials into the MySQL Settings account. If the user was successfully created, Coquery should now be connected to the server using this account.</p></body></html>", None))
        self.label_6.setText(_translate("mysql_guide", "<html><head/><body><p><span style=\" font-weight:600;\">MySQL server guide</span></p><p>If you follow these steps, your MySQL server should be ready. </p><p>As the next step, you can now install a corpus module. Installing corpus modules is done in the Corpus manager which can be started from the \'Corpus\' menu.</p><p><br/></p><p>Enjoy querying your corpora!</p></body></html>", None))


