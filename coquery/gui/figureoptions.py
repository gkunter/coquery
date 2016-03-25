# -*- coding: utf-8 -*-
"""
figureoptions.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import division

import sys
import seaborn as sns
import matplotlib as mpl

from coquery import options
from .pyqt_compat import QtGui, QtCore
from .ui.figureOptionsUi import Ui_FigureOptions

class CoqColorItem(QtGui.QListWidgetItem):
    def __init__(self, color):
        super(CoqColorItem, self).__init__()
        r, g, b = color
        self.set_color((int(r * 255), int(g * 255), int(b * 255)))
        self.color = color
    
    def data(self, role, *args):
        if role == QtCore.Qt.UserRole:
            return self.color
        else:
            return super(CoqColorItem, self).data(role, *args)
        
    def set_color(self, color):
        self.setText("#{:02X}{:02X}{:02X}".format(*color))
        self.color = color
        self.setBackground(QtGui.QBrush(QtGui.QColor(*color)))
        if sum(color) > (255 * 3) / 2:
            self.setForeground(QtGui.QBrush(QtGui.QColor("black")))
        else:
            self.setForeground(QtGui.QBrush(QtGui.QColor("white")))

class FigureOptions(QtGui.QDialog):
    def __init__(self, default=dict(), parent=None, icon=None):
        super(FigureOptions, self).__init__(parent)
        
        self.options = default
        self.parent = parent
        self.ui = Ui_FigureOptions()
        self.ui.setupUi(self)
        
        # set up labels tab:
        self.ui.label_main.setText(self.options.get("label_main", ""))
        self.ui.label_x_axis.setText(self.options.get("label_x_axis", ""))
        self.ui.label_y_axis.setText(self.options.get("label_y_axis", ""))
        self.ui.label_legend.setText(self.options.get("label_legend", ""))
        self.ui.spin_columns.setValue(self.options.get("label_legend_columns", 1))
    
        # Color editing is currently not implemented, so hide all widgets 
        # that relate to that:
        self.ui.button_remove_custom.hide()
        self.ui.combo_custom.hide()        
        
        # set up colors tab:
        self.palette_name = self.options.get("color_palette", "")
        if self.palette_name:
            self.setup_palette_combo()
        
        self.ui.spin_number.setValue(self.options.get("color_number", 6))
        
        #self.current_palette = QtGui.QStandardItemModel(self.ui.color_test_area)
        if self.palette_name == "custom":
            self.custom_palette = self.options.get("color_palette_values", [])

        # set fonts from options:
        for x in ["main", "x_axis", "x_ticks", "y_axis", "y_ticks", "legend", "legend_entries"]:
            self.set_element_font(x, self.options.get("font_{}".format(x)))

        self.ui.radio_qualitative.clicked.connect(self.change_palette)
        self.ui.radio_sequential.clicked.connect(self.change_palette)
        self.ui.radio_diverging.clicked.connect(self.change_palette)
        self.ui.radio_custom.clicked.connect(self.change_palette)
        self.ui.combo_qualitative.currentIndexChanged.connect(lambda x: self.change_palette(True))
        self.ui.combo_sequential.currentIndexChanged.connect(lambda x: self.change_palette(True))
        self.ui.combo_diverging.currentIndexChanged.connect(lambda x: self.change_palette(True))
        #self.ui.combo_custom.currentIndexChanged.connect(lambda x: self.change_palette(True))
        self.ui.button_reverse_order.clicked.connect(self.reverse_palette)
        self.ui.spin_number.valueChanged.connect(self.change_palette_length)
        self.change_palette()

        if self.palette_name != "custom":
            self.ui.radio_custom.setDisabled(True)
            
        # set up signals so that a dragged color is unselected after drop:
        self.item_entered = False
        self.ui.color_test_area.itemSelectionChanged.connect(self.check_for_drag)
        self.ui.color_test_area.itemEntered.connect(self.set_entered)
        self.ui.color_test_area.clicked.connect(self.change_color)

        # set up fonts tab:
        font_family = self.options.get("font_main").family()
        index = self.ui.combo_font_figure.findText(font_family)
        self.ui.combo_font_figure.setCurrentIndex(index)
        self.ui.combo_font_figure.currentIndexChanged.connect(self.change_font)
        
        # set up spinners
        for x in dir(self.ui):
            if x.startswith("spin_size"):
                element_name = x.rpartition("spin_size_")[-1]
                font = self.options.get("font_{}".format(element_name))
                getattr(self.ui, x).setValue(font.pointSize())
                
        self.ui.spin_size_main.valueChanged.connect(lambda: self.font_resize("main"))
        self.ui.spin_size_x_axis.valueChanged.connect(lambda: self.font_resize("x_axis"))
        self.ui.spin_size_x_ticks.valueChanged.connect(lambda: self.font_resize("x_ticks"))
        self.ui.spin_size_y_axis.valueChanged.connect(lambda: self.font_resize("y_axis"))
        self.ui.spin_size_y_ticks.valueChanged.connect(lambda: self.font_resize("y_ticks"))
        self.ui.spin_size_legend.valueChanged.connect(lambda: self.font_resize("legend"))
        self.ui.spin_size_legend_entries.valueChanged.connect(lambda: self.font_resize("legend_entries"))
                
        self.ui.label_main.setFocus()

        try:
            self.resize(options.settings.value("figureoptions_size"))
        except TypeError:
            pass

    def closeEvent(self, event):
        options.settings.setValue("figureoptions_size", self.size())
        
    def _change_to_custom(self):
        self.ui.radio_custom.setEnabled(True)
        self.ui.radio_custom.setChecked(True)
        self.custom_palette = self.get_current_palette()
        self.change_palette()
        
    def change_to_palette(self, palette_name):
        if self.palette_name == "custom":
            self.custom_palette = self.get_current_palette()
        self.palette_name = str(palette_name)

    def change_color(self, index):
        item = self.ui.color_test_area.item(index.row())
        col = QtGui.QColorDialog.getColor(QtGui.QColor(str(item.text())))
        if col.isValid():
            item.set_color((col.red(), col.green(), col.blue()))
            self._change_to_custom()
        self.ui.color_test_area.clearSelection()

    def set_entered(self):
        self.item_entered = True
    
    def color_has_moved(self):
        self._change_to_custom()
    
    def check_for_drag(self):
        if self.item_entered:
            self.ui.color_test_area.clearSelection()
            self.item_entered = False
            self._change_to_custom()
    
    def change_palette_length(self):
        self.ui.radio_custom.setEnabled(True)
        self.ui.radio_custom.setChecked(True)
        self.custom_palette = self.get_current_palette()
        self.test_palette()
    
    def set_current_palette(self, palette):
        self.ui.color_test_area.clear()
        for x in palette:
            self.ui.color_test_area.addItem(CoqColorItem(x))
        #self.current_palette.clear()
        #for x in palette:
            #self.current_palette.appendRow(CoqColorItem(x))
    
    def get_current_palette(self):
        #items = []
        #for i in range(self.current_palette.rowCount()):
            #items.append(
                #self.current_palette.data(
                    #self.current_palette.index(i, 0),
                    #role=QtCore.Qt.UserRole))

        items = []
        for i in range(self.ui.color_test_area.count()):
            items.append(QtGui.QColor(self.ui.color_test_area.item(i).text()))
        items = [(x.red() / 255, x.green() / 255, x.blue() / 255) for x in items]
        return items
    
    def reverse_palette(self):
        items = self.get_current_palette()
        self.set_current_palette(items[::-1])
        self._change_to_custom()
    
    def change_palette(self, select_combo=False):
        self.ui.combo_qualitative.setEnabled(False)
        self.ui.combo_sequential.setEnabled(False)
        self.ui.combo_diverging.setEnabled(False)
        self.ui.combo_custom.setEnabled(False)
        
        self.ui.button_remove_custom.setEnabled(False)
        
        if self.ui.radio_qualitative.isChecked():
            self.ui.combo_qualitative.setEnabled(True)
            self.change_to_palette(self.ui.combo_qualitative.currentText())
            if select_combo:
                self.ui.combo_qualitative.setFocus()
        elif self.ui.radio_sequential.isChecked():
            self.ui.combo_sequential.setEnabled(True)
            self.change_to_palette(self.ui.combo_sequential.currentText())
            if select_combo:
                self.ui.combo_sequential.setFocus()
        elif self.ui.radio_diverging.isChecked():
            self.ui.combo_diverging.setEnabled(True)
            self.change_to_palette(self.ui.combo_diverging.currentText())
            if select_combo:
                self.ui.combo_diverging.setFocus()
        elif self.ui.radio_custom.isChecked():
            #self.ui.combo_custom.setEnabled(True)
            #self.ui.button_remove_custom.setEnabled(True)
            self.palette_name = "custom"
            if select_combo:
                self.ui.combo_custom.setFocus()
        else:
            self.ui.radio_qualitative.setChecked(True)
            self.change_palette()
        self.test_palette()

    def setup_palette_combo(self):
        if self.palette_name == "custom":
            self.ui.radio_custom.setEnabled(True)
            self.ui.radio_custom.setChecked(True)
        else:
            for palette_type in ["qualitative", "sequential", "diverging"]:
                combo_box = getattr(self.ui, "combo_{}".format(palette_type))
                if combo_box.findText(self.palette_name) > -1:
                    radio_button = getattr(self.ui, "radio_{}".format(palette_type))
                    radio_button.setChecked(True)
                    combo_box.setCurrentIndex(combo_box.findText(self.palette_name))
    
    def test_palette(self):
        if self.palette_name == "custom":
            palette = self.custom_palette
        else:
            palette = sns.color_palette(self.palette_name, int(self.ui.spin_number.value()))
        self.ui.color_test_area.clear()
        for color in palette:
            item = CoqColorItem(color)
            self.ui.color_test_area.addItem(item)
    
    def set_element_font(self, element_name, font):
        name = "label_sample_{}".format(element_name)
        current_field = getattr(self.ui, name)
        current_field.setFont(font)
        current_field.setText("{} {}".format(font.family(), font.pointSize()))

    def font_resize(self, element_name):
        name = "label_sample_{}".format(element_name)
        current_field = getattr(self.ui, name)
        font = self.options.get(element_name, current_field.font())
        font.setPointSize(int(getattr(self.ui, "spin_size_{}".format(element_name)).value()))
        self.set_element_font(element_name, font)

    def change_font(self):
        new_font = QtGui.QFont(self.ui.combo_font_figure.currentText())
        self.options["figure_font"] = new_font
        for x in dir(self.ui):
            if x.startswith("label_sample_"):
                element_name = x.split("label_sample_")[-1]
                pointsize = int(getattr(self.ui, "spin_size_{}".format(element_name)).value())
                self.set_element_font(element_name, QtGui.QFont(new_font.family(), pointsize))

    def accept(self):
        self.options["label_main"] = str(self.ui.label_main.text())
        self.options["label_x_axis"] = str(self.ui.label_x_axis.text())
        self.options["label_y_axis"] = str(self.ui.label_y_axis.text())
        self.options["label_legend"] = str(self.ui.label_legend.text())
        self.options["label_legend_columns"] = int(self.ui.spin_columns.value())

        self.options["color_palette"] = self.palette_name
        self.options["color_palette_values"] = self.get_current_palette()
        if len(self.options["color_palette_values"]) < self.options.get("color_number", 6):
            self.options["color_palette_values"] = (self.options["color_palette_values"] * self.options.get("color_number", 6))[:self.options.get("color_number", 6)]

        for x in ["main", "x_axis", "x_ticks", "y_axis", "y_ticks", "legend", "legend_entries"]:
            self.options["font_{}".format(x)] = getattr(self.ui, "label_sample_{}".format(x)).font()
        
        super(FigureOptions, self).accept()
        options.settings.setValue("figureoptions_size", self.size())
        

    @staticmethod
    def get_default():
        return

    @staticmethod
    def manage(default=dict(), parent=None, icon=None):
        dialog = FigureOptions(default=dict(default), parent=parent, icon=icon)
        result = dialog.exec_()
        if result == QtGui.QDialog.Accepted:
            return dialog.options
        else:
            return None

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.reject()
            
def main():
    app = QtGui.QApplication(sys.argv)
    print(FigureOptions.manage())
    
if __name__ == "__main__":
    main()
    
