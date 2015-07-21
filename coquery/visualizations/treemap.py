""" Tree mapping based on http://hcil.cs.umd.edu/trs/91-03/91-03.html."""
from __future__ import division
from __future__ import print_function

import unittest
import sys
import os

import options
sys.path.append(os.path.join(sys.path[0], "../gui/"))
import visualizerUi
from pyqt_compat import QtGui, QtCore

def table_to_tree(table, label="count"):
    """ Return a tree that contains a tree representation of the table. It
    is assumed that the first column represents the highest tree level, the
    second column the second tree level, and so on. The last column gives
    the values of the terminal nodes."""
    tree = {}
    for path in table:
        parent = tree
        for i, child in enumerate(sorted(path[:-1])):
            if i == len(path[:-1]) - 1:
                parent = parent.setdefault(child, {label: path[-1]})
            else:
                parent = parent.setdefault(child, {})
    return tree

def tree_weight(tree, label="count"):
    """ Return the summed values of all terminal nodes in the tree."""
    i = 0
    for node in tree:
        if node == label:
            i += tree[node]
        else:
            i += tree_weight(tree[node])
    return i

table = [
    ["WIS", "male", "young", 3],
    ["WIS", "male", "middle", 1],
    ["WIS", "male", "old", 7],
    ["WIS", "female", "young", 2],
    ["WIS", "female", "middle", 3],
    ["WIS", "female", "old", 5],
    ["NC", "male", "young", 12],
    ["NC", "male", "old", 8],
    ["NC", "female", "young", 11],
    ["NC", "female", "old", 2]]


tree = {
    "WIS": {
        "male": {
            "young": {"count": 3}, 
            "old": {"count": 7}},
        "female": {
            "young": {"count": 2}, 
            "old": {"count": 5}}},
    "NC": {
        "male": {
            "young": {"count": 12}, 
            "old": {"count": 8}},
        "female": {
            "young": {"count": 11}, 
            "old": {"count": 2}}}}

color_map = {"young": "DarkOrange", "middle": "Red", "old": "RoyalBlue"}

color_pairs = ["rgb(166,206,227)", "rgb(31,120,180)", 
    "rgb(178,223,138)", "rgb(51,160,44)", 
    "rgb(251,154,153)", "rgb(227,26,28)", 
    "rgb(253,191,111)", "rgb(255,127,0)", 
    "rgb(202,178,214)", "rgb(106,61,154)", 
    "rgb(255,255,153)", "rgb(177,89,40)"]


color_categories = ["rgb(228,26,28)", "rgb(55,126,184)", "rgb(77,175,74)", 
"rgb(152,78,163)", "rgb(255,127,0)", "rgb(255,255,51)", 
"rgb(166,86,40)", "rgb(247,129,191)", "rgb(153,153,153)"]


class TestTreeMethods(unittest.TestCase):
    """ Define test cases for the tree functions. """

    def test_table_to_tree(self):
        self.assertEqual(table_to_tree(table), tree)

    def test_tree_weight(self):
        self.assertEqual(tree_weight(tree), 50)
        self.assertEqual(tree_weight(tree["NC"]), 33)
        self.assertEqual(tree_weight(tree["NC"]["female"]), 13)
        self.assertEqual(tree_weight(tree["NC"]["female"]["young"]), 11)

class TreeMap(QtGui.QWidget):
    def __init__(self, tree, parent=None, *args):
        super(TreeMap, self).__init__(parent, *args)
        self.tree = tree
        #self.ui = visualizerUi.Ui_visualizer()
        #self.ui.setupUi(self)
        #self.setWindowIcon(options.cfg.icon)

        
    def paintEvent(self, e):
        self.qp = QtGui.QPainter()
        self.qp.begin(self)
        size = self.size()
        self.tree_map(self.tree, [0, 0], [size.width(), size.height()], 0, None, None)
        self.qp.end()

    def paint_rectangle(self, p, q, color_name, name):
        self.qp.setPen(QtGui.QColor("black"))
        factor_level = color_name.rpartition("\t")[2]
        self.qp.setBrush(self.get_color(factor_level))
        self.qp.drawRect(p[0], p[1], q[0] - p[0], q[1] - p[1])
        
        name_metrics = self.qp.fontMetrics().boundingRect(name)
        rect = QtCore.QRect(p[0], p[1], q[0] - p[0], q[1] - p[1])
        #self.qp.drawText(rect, QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop, name)
        #if name_metrics.width() > q[0] - p[0]:
            #self.qp.rotate(-45)
        self.qp.drawText(rect, QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop, name.replace("\t", ":"))
        #self.qp.drawText(rect, QtCore.Qt.AlignRight|QtCore.Qt.AlignBottom, name)
        #if name_metrics.width() > q[0] - p[0]:
            #self.qp.rotate(45)

    def get_color(self, value):
        if not value:
            return
        col = color_categories[self.factor.index(value) % len(color_categories)]
        # transform stylesheet color spec to r, g, b:
        r, g, b = [int(x) for x in col.strip("rgb(").strip(")").split(",")] 
        return QtGui.QColor(r, g, b)
    
    def set_factor(self, levels):
        self.factor = levels

    def tree_map(self, root, p, q, axis, color, name=None, label="count"):
        """ P and Q are the upper right and lower left corners of the display. 
        By setting the axis argument to zero the initial partitions are made
        vertically."""
        width = q[axis] - p[axis]
        if label in root:
            self.paint_rectangle(p, q, name, name)
        for i, child_name in enumerate(root):
            if child_name != label:
                child = root[child_name]
                q[axis] = p[axis] + (tree_weight(child) / tree_weight(root)) * width
                if name:
                    new_name = "{}\t{}".format(name, child_name)
                else:
                    new_name = child_name
                self.tree_map(child, list(p), list(q), 1 - axis, color, new_name)
                p[axis] = q[axis]

class TreeMapVisualizer(QtGui.QDialog):
    def __init__(self, parent=None):
        super(TreeMapVisualizer, self).__init__(parent)
        
        self.ui = visualizerUi.Ui_visualizer()
        self.ui.setupUi(self)
        self.setWindowIcon(options.cfg.icon)

    @staticmethod
    def MosaicPlot(table, parent=None):
        """ Plot a mosaic plot for the data provided in 'table'. The last
        column of 'table' contains the frequency/weight of the row. The 
        other rows are a hierarchical set of factors."""
        levels = set([])
        for row in table:
            levels.add(row[-2])
        levels = list(levels) 
        tree = table_to_tree(table)
        dialog = TreeMapVisualizer(parent)
        tm = TreeMap(tree, parent)
        tm.set_factor(levels)
        dialog.ui.verticalLayout.addWidget(tm)
        return dialog.show()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.accept()

if __name__ == "__main__":
    unittest.main()
            
    #app = QtGui.QApplication(sys.argv)

    #TreeMap.MosaicPlot(table)
    #TreeMap.MosaicPlot([x for x in table if x[0] == "WIS" and x[1] == "female"])
    #tm.tree_map(tree, [0, 0], [500, 500], 0, None, None)
    #sys.exit(app.exec_())
