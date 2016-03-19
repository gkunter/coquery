""" Tree mapping based on http://hcil.cs.umd.edu/trs/91-03/91-03.html.

Another Python implementation is given here:

http://wiki.scipy.org/Cookbook/Matplotlib/TreeMap

"""

from __future__ import division
from __future__ import print_function

import unittest
import math

from coquery.defines import *

from matplotlib.patches import Rectangle
from coquery.visualizer import visualizer as vis

class Visualizer(vis.BaseVisualizer):
    dimensionality = 1
    def update_data(self):
        super(Visualizer, self).update_data()

        self._tree = self.get_content_tree(self._table)
        self.max_weight = self.tree_weight(self._tree)
        
        self.factor = self.get_levels(self._column_order[-2])
        col = [[x / 256 for x in rgb] for rgb in color_categories]
        self.colors = dict(zip(self.factor, (col * ((len(col) // len(self.factor))))[0:len(self.factor)]))
        
    def paint_rectangle(self, p, q, name, weight=None):
        rect = Rectangle((p[0], p[1]), q[0] - p[0], q[1] - p[1], 
                         facecolor=self.colors[name], label=name)
        self.subplot.add_patch(rect)
       
    def get_content_tree(self, table, label="count"):
        """ 
        Return a tree that contains a tree representation of the table.
        
        It is assumed that the first column represents the highest tree 
        level, the second column the second tree level, and so on. The last 
        column gives the values of the terminal nodes.
        
        Parameters
        ----------
        table : container object
            A data object containing one or more columns that will be used
            as branches for the tree, and a numeric column as the last 
            column which will be used as the weight value for each branch.
        label : string
            The string used to label branch weights.        
            
        Returns
        -------
        tree : dict
            A dictionary containing the tree structure of the data table.
        """
        tree = {}
        
        # go through each table entry:
        for path in table:
            parent = tree
            for i, child in enumerate(path[:-1]):
                if i == len(path[:-1]) - 1:
                    parent = parent.setdefault(child, {label: path[-1]})
                else:
                    parent = parent.setdefault(child, {})
        return tree

    def tree_weight(self, tree):
        """
        Return the summed values of all terminal nodes in the tree.
        
        Parameters
        ----------
        tree : dict
            A dictionary created by :func:`get_content_tree`.
        """
        i = 0
        for node in tree:
            if isinstance(tree[node], (int, float, long)):
                i += tree[node]
            else:
                i += self.tree_weight(tree[node])
        return i
       
    def tree_map(self, root, p, q, axis, color, name=None, label="count"):
        """ P and Q are the upper right and lower left corners of the display. 
        By setting the axis argument to zero the initial partitions are made
        vertically."""
        #if not name:
            #self.paint_rectangle(p, q, name, 0)
        width = q[axis] - p[axis]
        if label in root:
            self.paint_rectangle(p, q, name, self.tree_weight(root))
        for i, child_name in enumerate(sorted(root)):
            if child_name != label:
                child = root[child_name]
                q[axis] = p[axis] + (width * float(self.tree_weight(child))) / self.tree_weight(root)
                #if name:
                    #new_name = "{}\t{}".format(name, child_name)
                #else:
                    #new_name = child_name
                new_name = child_name
                #margin_x = (q[1 - axis] - p[1 - axis]) * 0.01
                #margin_y = (q[axis] - p[axis]) * 0.01
                self.tree_map(child, list(p), list(q), 1 - axis, color, new_name)
                p[axis] = q[axis]

    def setup_figure(self, *args):
        super(Visualizer, self).setup_figure(*args)
        self.subplot.set_ylim(0, math.sqrt(self.max_weight) - 1)
        self.subplot.set_xlim(0, math.sqrt(self.max_weight) - 1)

    def draw(self):
        self.tree_map(self._tree, [0, 0], [math.sqrt(self.max_weight) - 1, math.sqrt(self.max_weight) - 1], 0, None, None)
        self.subplot.legend(self.colors, list(self.factor), loc="center left")
        self.figure.tight_layout()
