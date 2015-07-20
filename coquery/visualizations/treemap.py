from __future__ import division

import unittest


""" Tree mapping based on http://hcil.cs.umd.edu/trs/91-03/91-03.html: 

root : a pointer to the root of the tree or subtree

P, Q : arrays of length 2 with (x,y) coordinate pairs of opposite corners of the current rectangle (assume that Q contains the higher coordinates and P the lower coordinates, but this does not affect the correctness of the algorithm, only the order in which rectangles are drawn)

axis : varies between 0 and 1 to indicate cuts to be made vertically and horizontally

color: indicates the color to be used for the current rectangle.

In addition we need:

Paint_rectangle : a procedure that paints within the rectangle using a given color, and resets the color variable.

Size : a function that returns the number of bytes in the node pointed to by the argument. Alternatively, the size could be pre-computed and stored in each node. """

class Point(object):
    def __init__(self, x=None, y=None):
        self._x = x
        self._y = y
        
    @property
    def x(self):
        return self._x
    
    @x.setter
    def x(self, value):
        self._x = value
    
    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value


def paint_rectangle(p, q, color, name):
    """ p and q are the upper right and lower left corner of the rectangle."""
    print("{}: Painting from {}/{} to {}/{}".format(name, p[0], p[1], q[0], q[1]))

def tree_map(root, p, q, axis, color, name=None, label="count"):
    """ P and Q are the upper right and lower left corners of the display. 
    By setting the axis argument to zero the initial partitions are made
    vertically. It is assumed that arguments P and Q are passed by value
    (since P, Q are modified within):

    tree_map(root, p[0..1], q[0..1], axis, color)"""

    paint_rectangle(p, q, color, name)
    width = q[axis] - p[axis]
    print(width)
    for i, child_name in enumerate(root):
        if child_name != label:
            child = root[child_name]
            print(tree_weight(child), tree_weight(root))
            q[axis] = p[axis] + (tree_weight(child) / tree_weight(root)) * width
            tree_map(child, p, q, 1 - axis, color, child_name)
            p[axis] = q[axis]

def table_to_tree(table, label="count"):
    """ Return a tree that contains a tree representation of the table. It
    is assumed that the first column represents the highest tree level, the
    second column the second tree level, and so on. The last column gives
    the values of the terminal nodes."""
    tree = {}
    for path in table:
        parent = tree
        for i, child in enumerate(path[:-1]):
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

class TestTreeMethods(unittest.TestCase):
    """ Define test cases for the tree functions. """
    
    table = [
        ["A", "M", "X", 3],
        ["A", "M", "Y", 7],
        ["A", "N", "X", 2],
        ["A", "N", "Y", 5],
        ["B", "M", "X", 12],
        ["B", "M", "Y", 8],
        ["B", "N", "X", 11],
        ["B", "N", "Y", 2]]


    tree = {
        "A": {
            "M": {
                "X": {"count": 3}, 
                "Y": {"count": 7}},
            "N": {
                "X": {"count": 2}, 
                "Y": {"count": 5}}},
        "B": {
            "M": {
                "X": {"count": 12}, 
                "Y": {"count": 8}},
            "N": {
                "X": {"count": 11}, 
                "Y": {"count": 2}}}}

    def test_table_to_tree(self):
        self.assertEqual(table_to_tree(self.table), self.tree)

    def test_tree_weight(self):
        self.assertEqual(tree_weight(self.tree), 50)
        self.assertEqual(tree_weight(self.tree["B"]), 33)
        self.assertEqual(tree_weight(self.tree["B"]["N"]), 13)
        self.assertEqual(tree_weight(self.tree["B"]["N"]["X"]), 11)

if __name__ == "__main__":
    unittest.main()
        
