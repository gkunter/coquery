from __future__ import division
from __future__ import unicode_literals

from pyqt_compat import QtCore, QtGui

import sys
import contextviewUi
import options

class ContextView(QtGui.QWidget):
    def __init__(self, corpus, token_id, source_id, token_width, parent=None):
        
        super(ContextView, self).__init__(parent)
        
        self.corpus = corpus
        self.token_id = token_id
        self.source_id = source_id
        self.token_width = token_width
        
        self.ui = contextviewUi.Ui_ContextView()
        self.ui.setupUi(self)
        
        
        #self.ui.button_close.setIcon(
            #QtGui.qApp.style().standardIcon(QtGui.QStyle.SP_SP_DialogCloseButton))


        self.ui.spin_context_width.valueChanged.connect(self.spin_changed)
        self.ui.slider_context_width.valueChanged.connect(self.slider_changed)
        self.ui.slider_context_width.setTracking(True)
        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Ok).clicked.connect(self.closeEvent)
        self.add_source_label("Token ID", token_id)
        self.add_source_label("Source ID", source_id)
            
        self.update_context()
        
    def add_source_label(self, name, content):
        """ Add the label 'name' with value 'content' to the context viewer.
        """
        layout_row = self.ui.form_information.count()
        self.ui.source_name = QtGui.QLabel(self.ui.box_context)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui.source_name.sizePolicy().hasHeightForWidth())
        self.ui.source_name.setSizePolicy(sizePolicy)
        self.ui.source_name.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTop|QtCore.Qt.AlignTrailing)
        self.ui.source_name.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.ui.form_information.setWidget(layout_row, QtGui.QFormLayout.LabelRole, self.ui.source_name)
        self.ui.source_content = QtGui.QLabel(self.ui.box_context)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui.source_content.sizePolicy().hasHeightForWidth())
        self.ui.source_content.setSizePolicy(sizePolicy)
        self.ui.source_content.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.ui.source_content.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.ui.form_information.setWidget(layout_row, QtGui.QFormLayout.FieldRole, self.ui.source_content)
        
        if name:
            name = str(name).strip()
            if not name.endswith(":"):
                name += ":"
            self.ui.source_name.setText(name)
        if content:
            content = str(content).strip()
            self.ui.source_content.setText(content)
        
    def spin_changed(self):
        self.ui.slider_context_width.valueChanged.disconnect(self.slider_changed)
        self.ui.slider_context_width.setValue(self.ui.spin_context_width.value())
        self.update_context()
        self.ui.slider_context_width.valueChanged.connect(self.slider_changed)
    
    def slider_changed(self):
        self.ui.spin_context_width.valueChanged.disconnect(self.spin_changed)
        self.ui.spin_context_width.setValue(self.ui.slider_context_width.value())
        self.update_context()
        self.ui.spin_context_width.valueChanged.connect(self.spin_changed)
    
    def update_context(self):
        if self.corpus:
            self.corpus.render_context(
                self.token_id, 
                self.source_id, 
                self.token_width,
                self.ui.slider_context_width.value(), self)
        
    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.accept()
            
    def closeEvent(self, *args):
        options.cfg.context_view_height = self.height()
        options.cfg.context_view_width = self.width()
        options.cfg.context_view_words = self.ui.slider_context_width.value()
        options.cfg.main_window.widget_list.remove(self)
        
    @staticmethod
    def display(resource, token_id, source_id, token_width, parent=None):
        dialog = ContextView(resource, token_id, source_id, token_width, parent=None)        
        try:
            dialog.ui.slider_context_width.setValue(options.cfg.context_view_words)
        except AttributeError:
            pass
        try:
            dialog.resize(dialog.width(), options.cfg.context_view_height)
        except AttributeError:
            pass
        try:
            dialog.resize(options.cfg.context_view_width, dialog.height())
        except AttributeError:
            pass
        dialog.setVisible(True)
        options.cfg.main_window.widget_list.append(dialog)

def main():
    app = QtGui.QApplication(sys.argv)
    viewer = ContextView(None, None, None, None, 0)
    viewer.exec_()
    
if __name__ == "__main__":
    main()
    