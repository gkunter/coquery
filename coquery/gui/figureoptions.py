# -*- coding: utf-8 -*-

"""
figureoptions.py is part of Coquery.

Copyright (c) 2015 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License.
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

import sys
import seaborn as sns
import matplotlib as mpl

from pyqt_compat import QtGui, QtCore
import figureOptionsUi

class CoqColorListItem(QtGui.QListWidgetItem):
    def __init__(self, color):
        super(CoqColorListItem, self).__init__()
        self.set_color(color)
        self.color = color
        
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
        self.ui = figureOptionsUi.Ui_FigureOptions()
        self.ui.setupUi(self)

        # set up labels tab:
        self.ui.label_main.setText(self.options.get("label_main", ""))
        self.ui.label_x_axis.setText(self.options.get("label_x_axis", ""))
        self.ui.label_y_axis.setText(self.options.get("label_y_axis", ""))
        self.ui.label_legend.setText(self.options.get("label_legend", ""))
        self.ui.spin_columns.setValue(self.options.get("label_legend_columns", 1))

        # Color editing is currently not implemented, so hide all widgets 
        # that relate to that:
        self.ui.button_edit_qualitative.hide()
        self.ui.button_edit_sequential.hide()
        self.ui.button_edit_diverging.hide()
        self.ui.button_edit_custom.hide()
        self.ui.button_remove_custom.hide()
        #self.ui.radio_custom.hide()
        self.ui.combo_custom.hide()        
        
        # set up colors tab:
        self.current_palette = self.options.get("color_palette", "")
        if self.current_palette:
            self.set_palette_combo()
        self.ui.check_reverse.setChecked(self.options.get("color_palette_reverse", False))
        self.ui.spin_number.setValue(self.options.get("color_number", 6))
        
        self.ui.radio_qualitative.clicked.connect(self.change_palette)
        self.ui.radio_sequential.clicked.connect(self.change_palette)
        self.ui.radio_diverging.clicked.connect(self.change_palette)
        #if self.ui.combo_custom.count():
            #self.ui.radio_custom.clicked.connect(self.change_palette)
        #else:
            #self.ui.radio_custom.setEnabled(False)            
        self.ui.combo_qualitative.currentIndexChanged.connect(lambda x: self.change_palette(True))
        self.ui.combo_sequential.currentIndexChanged.connect(lambda x: self.change_palette(True))
        self.ui.combo_diverging.currentIndexChanged.connect(lambda x: self.change_palette(True))
        #self.ui.combo_custom.currentIndexChanged.connect(lambda x: self.change_palette(True))
        self.ui.check_reverse.clicked.connect(self.change_palette)
        self.ui.spin_number.valueChanged.connect(self.change_palette_length)
        self.change_palette()

        if self.current_palette != "custom":
            self.ui.radio_custom.setDisabled(True)
        
        # set up signals so that a dragged color is unselected after drop:
        self.item_entered = False
        self.ui.color_test_area.itemSelectionChanged.connect(self.check_for_drag)
        self.ui.color_test_area.itemEntered.connect(self.set_entered)
        self.ui.color_test_area.itemClicked.connect(self.change_color)

        # set up fonts tab:
        self.ui.button_select_main.clicked.connect(lambda: self.font_select("main"))
        self.ui.button_select_x.clicked.connect(lambda: self.font_select("x"))
        self.ui.button_select_x_ticks.clicked.connect(lambda: self.font_select("x_ticks"))
        self.ui.button_select_y.clicked.connect(lambda: self.font_select("y"))
        self.ui.button_select_y_ticks.clicked.connect(lambda: self.font_select("y_ticks"))
        self.ui.button_select_legend.clicked.connect(lambda: self.font_select("legend"))
        self.ui.button_select_legend_entries.clicked.connect(lambda: self.font_select("legend_entries"))

        for x in dir(self.ui):
            if x.startswith("button_select_"):
                element_name = x.rpartition("button_select_")[-1]
                default_font = self.options.get("font_{}".format(element_name), self.font())
                self.set_element_font(element_name, default_font)
                
        self.ui.label_main.setFocus(True)

    def change_color(self, item):
        col = QtGui.QColorDialog.getColor(QtGui.QColor(str(item.text())))
        if col:
            item.set_color((col.red(), col.green(), col.blue()))
        self.ui.color_test_area.clearSelection()
        self.ui.radio_custom.setEnabled(True)
        self.ui.radio_custom.setChecked(True)
        self.change_palette()

    def set_entered(self):
        self.item_entered = True
    
    def check_for_drag(self):
        if self.item_entered:
            self.ui.color_test_area.clearSelection()
            self.item_entered = False
    
    def change_palette_length(self):
        self.test_palette()
    
    def change_palette(self, select_combo=False):
        self.ui.combo_qualitative.setEnabled(False)
        self.ui.combo_sequential.setEnabled(False)
        self.ui.combo_diverging.setEnabled(False)
        self.ui.combo_custom.setEnabled(False)
        
        self.ui.button_edit_qualitative.setEnabled(False)
        self.ui.button_edit_sequential.setEnabled(False)
        self.ui.button_edit_diverging.setEnabled(False)
        self.ui.button_edit_custom.setEnabled(False)
        self.ui.button_remove_custom.setEnabled(False)
        
        if self.ui.radio_qualitative.isChecked():
            self.ui.combo_qualitative.setEnabled(True)
            self.ui.button_edit_qualitative.setEnabled(True)
            self.current_palette = str(self.ui.combo_qualitative.currentText())
            if select_combo:
                self.ui.combo_qualitative.setFocus(True)
        elif self.ui.radio_sequential.isChecked():
            self.ui.combo_sequential.setEnabled(True)
            self.ui.button_edit_sequential.setEnabled(True)
            self.current_palette = str(self.ui.combo_sequential.currentText())
            if select_combo:
                self.ui.combo_sequential.setFocus(True)
        elif self.ui.radio_diverging.isChecked():
            self.ui.combo_diverging.setEnabled(True)
            self.ui.button_edit_diverging.setEnabled(True)
            self.current_palette = str(self.ui.combo_diverging.currentText())
            if select_combo:
                self.ui.combo_diverging.setFocus(True)
        elif self.ui.radio_custom.isChecked():
            self.ui.combo_custom.setEnabled(True)
            self.ui.button_edit_custom.setEnabled(True)
            self.ui.button_remove_custom.setEnabled(True)
            self.current_palette = "custom"
            if select_combo:
                self.ui.combo_custom.setFocus(True)
        else:
            self.ui.radio_qualitative.setChecked(True)
            self.change_palette()
        if self.current_palette != "custom":
            self.test_palette()

    def set_palette_combo(self):
        for palette_type in ["qualitative", "sequential", "diverging", "custom"]:
            combo = getattr(self.ui, "combo_{}".format(palette_type))
            if combo.findText(self.current_palette) > -1:
                getattr(self.ui, "radio_{}".format(palette_type)).setChecked(True)
                combo.setCurrentIndex(combo.findText(self.current_palette))

    @staticmethod
    def get_rgb_palette(palette_name, number, rev):
        palette = [(int(r * 255), int(g * 255), int(b * 255)) for r, g, b in sns.color_palette(palette_name, n_colors=number)]
        if rev:
            palette = palette[::-1]
        return palette
    
    def get_current_palette(self):
        return [mpl.colors.ColorConverter().to_rgb(self.ui.color_test_area.item(x).text()) for x in range(self.ui.color_test_area.count())]
    
    def test_palette(self):
        palette = self.get_rgb_palette(self.current_palette, int(self.ui.spin_number.value()), bool(self.ui.check_reverse.isChecked()))
        self.ui.color_test_area.clear()
        for color in palette:
            item = CoqColorListItem(color)
            self.ui.color_test_area.addItem(item)
    
    def set_element_font(self, element_name, font):
        current_field = getattr(self.ui, "label_sample_{}".format(element_name))
        current_field.setFont(font)
        current_field.setText("{} {}".format(font.family(), font.pointSize()))

    def font_select(self, element_name):
        current_field = getattr(self.ui, "label_sample_{}".format(element_name))
        current_font = current_field.font()
        font, accepted = QtGui.QFontDialog.getFont(current_font, self.parent)
        if accepted:
            self.set_element_font(element_name, font)
        
    def accept(self):
        self.options["label_main"] = str(self.ui.label_main.text())
        self.options["label_x_axis"] = str(self.ui.label_x_axis.text())
        self.options["label_y_axis"] = str(self.ui.label_y_axis.text())
        self.options["label_legend"] = str(self.ui.label_legend.text())
        self.options["label_legend_columns"] = int(self.ui.spin_columns.value())

        self.options["color_palette"] = self.current_palette
        self.options["color_palette_values"] = self.get_current_palette()
        self.options["color_palette_reverse"] = bool(self.ui.check_reverse.isChecked())
        if len(self.options["color_palette_values"]) < self.options.get("color_number", 6):
            self.options["color_palette_values"] = (self.options["color_palette_values"] * self.options.get("color_number", 6))[:self.options.get("color_number", 6)]

        self.options["font_main"] = self.ui.label_sample_main.font()
        self.options["font_x_axis"] = self.ui.label_sample_x.font()
        self.options["font_x_axis_ticks"] = self.ui.label_sample_x_ticks.font()
        self.options["font_y_axis"] = self.ui.label_sample_y.font()
        self.options["font_y_axis_ticks"] = self.ui.label_sample_legend.font()
        self.options["font_legend"] = self.ui.label_sample_y.font()
        self.options["font_legend_entries"] = self.ui.label_sample_legend_entries.font()
        super(FigureOptions, self).accept()

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
    