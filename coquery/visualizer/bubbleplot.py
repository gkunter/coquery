# -*- coding: utf-8 -*-
"""
bubbleplot.py is part of Coquery.

Copyright (c) 2016-2018 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
from __future__ import division
import math

import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

from coquery.visualizer import visualizer as vis
from coquery.visualizer.treemap import TreeMap


class BubblePlot(TreeMap):
    name = "Bubble Chart"
    icon = "Scatterplot"
    axes_style = "white"

    COL_COLUMN = "COQ_HUE"
    NUM_COLUMN = "COQ_NUMERIC"

    sqrt_dict = {}

    _angle_cache = {}
    _angle_calls = 0
    _r_cache = {}
    _r_calls = 0
    _vector_cache = {}
    _vector_calls = 0

    def format_coord(self, x, y, title):
        """

        """
        for (cx, cy), r, label in self.circles:
            if math.sqrt((cx - x) ** 2 + (cy - y) ** 2) <= r:
                if title:
                    S = "{} – {}".format(title, label)
                else:
                    S = label
                self.set_tooltip(S)
                return S
        self.set_tooltip("")
        return ""

    def add_text(self, label, x, y):
        plt.gca().text(x, y, label,
                       va="center", ha="center",
                       rotation=90 if self.text_rotate else 0,
                       bbox=self.box_style if self.text_boxes else None)

    def draw_circles(self, data, ax=None, **kwargs):
        lst = []

        if ax is None:
            ax = plt.gca()

        for ((x, y), rad, label) in data:
            rad = rad - self._padding
            circ = plt.Circle((x, y), rad)
            ax.add_patch(circ)
            self.add_text(label, x, y)
            lst.append(circ)

        return lst

    def colorize_plot(self):
        for circ, col in zip(self.artists, self.colors):
            circ.set_color(col)
            if self.box_border:
                circ.set_edgecolor("black")

    @classmethod
    def rotate_vector(cls, x, theta):
        """
        Rotate the vector (x, 0) by the given angle.

        Returns
        -------
        v : tuple
            The rotated vector.
        """
        return x * math.cos(theta), x * math.sin(theta)
        cls._vector_calls += 1
        _key = round(theta, 2)
        try:
            cos_theta, sin_theta = cls._vector_cache[_key]
        except KeyError:
            cos_theta = math.cos(theta)
            sin_theta = math.sin(theta)
            cls._vector_cache[_key] = (cos_theta, sin_theta)

        return (x * cos_theta, x * sin_theta)

    @classmethod
    def get_angle(cls, a, b, c):
        """
        Return the angle A given lengths a, b, and c by using the
        Law of Cosines.

              C
             / \
          b /   \ a
           /     \
          A-------B
              c

        Parameters
        ----------
        a, b, c : float
            The length of sides a, b, c in a triangle.

        """
        x = (b ** 2 + c ** 2 - a ** 2) / (2 * b * c)
        if abs(x) > 1:
            raise ValueError("Illegal angle")
        # Allow angles > 180 degrees:
        if x > 1:
            val = math.acos(x - 1)
        else:
            val = math.acos(x)
        return val

    @staticmethod
    def intersecting(tup1, tup2):
        ((x1, y1), r1) = tup1
        ((x2, y2), r2) = tup2

        lower = (r1 - r2) ** 2
        upper = (r1 + r2) ** 2

        val = (x1 - x2) ** 2 + (y1 - y2) ** 2

        return lower <= val < upper - 0.01

    def get_label(self, row, grouping, numerical):
        cat_label = " | ".join(row[grouping].values)
        val = row[numerical]
        if numerical != self.NUM_COLUMN:
            frm_str = ": M={}".format(self.frm_str)
        else:
            frm_str = " ({})"
        label = "{}{}".format(cat_label,
                              frm_str.format(self.frm_str.format(val)))

        return label

    def get_position(self, r, a, n):
        """
        Return the position of the next bubble I.

        a specifies the 'anchor' bubble A (i.e. the bubble with the
        circumference around which the algorithm attempts to place
        the next bubble) and n gives the 'neighbor' bubble N (i.e.
        the last bubble that has been drawn, and which should be
        tangent to the next bubble).

        The position of I is chosen so that I and A are tangent, as
        well as I and N. A and N themselves do not have to be tangent
        (they can be, though).

        Raises
        ------
        e : ValueError
            A ValueError exception is raised if no valid position
            exists.

        Parameters
        ----------
        r : int
            The radius of the next bubble (i)

        a, n : int
            The index of the anchor bubble (a) and the
            neighboring bubble (n).

        """
        (x_a, y_a), r_a, _ = a
        (x_n, y_n), r_n, _ = n

        #       I
        #      / \
        #   b /   \ a
        #    /     \
        #  A ------- N
        #       c

        # get side lengths:
        l_a = r_n + r
        l_b = r_a + r

        # l_c is actually the distance between the centers of the
        # anchor and the neighbor circles:
        l_c = math.sqrt((x_a - x_n) ** 2 + (y_a - y_n) ** 2)

        # the starting angle is the angle between a union vector
        # and the vector between the anchor and the neighbor:
        # start_angle = get_angle((1,  0), (x_n - x_a, y_n - y_a))

        # in this special case, the call to get_angle() can be
        # replaced by this expression:
        start_angle = math.atan2(y_n - y_a, x_n - x_a)

        theta = -self.get_angle(l_a, l_b, l_c) + start_angle
        val = (x_a + l_b * math.cos(theta), y_a + l_b * math.sin(theta))
        return val

    def get_intersections(self, circ, trials):
        for pos, r, _ in trials[::-1]:
            if self.intersecting(circ, (pos, r)):
                raise ValueError("Intersection detected")

    def get_dataframe(self, data, x, y, z):
        grouping = []
        numerical = None

        for feature in [x, y]:
            if self.dtype(feature, data) != object:
                numerical = feature
            else:
                grouping.append(feature)

        aggregator = vis.Aggregator()

        if z:
            z_statistic = ("mode" if data[z].dtype == object else
                           "mean")
            aggregator.add(z, z_statistic, name=self.COL_COLUMN)

        if numerical:
            aggregator.add(numerical, "mean", self.NUM_COLUMN)
        else:
            aggregator.add(self.get_default_index(), "count", self.NUM_COLUMN)

        df = aggregator.process(data, grouping)

        by = [self.NUM_COLUMN]
        ascending = [False]

        if (x and y):
            if numerical:
                by = by + grouping
                ascending = ascending + [True] * len(grouping)
            else:
                by = grouping + by
                ascending = [True] * len(grouping) + ascending
        df = df.sort_values(by=by, ascending=ascending)
        return df

    def place_circles(self, df):
        radii = np.sqrt(df[self.NUM_COLUMN].values / np.pi)
        if self.box_padding:
            self._padding = radii.min() * 0.05
        else:
            self._padding = 0

        radii = radii + self._padding

        a = 0

        numerical = self.NUM_COLUMN
        grouping = [col for col in [self.x, self.y]
                    if col in df.columns and df[col].dtype == object]
        circles = [((0, 0),
                    radii[0],
                    self.get_label(df.iloc[0], grouping, numerical))]
        if len(df) > 1:
            n = 1
            pos = (0 + radii[0] + radii[n], 0)

            for i in range(2, len(df)):
                last_anchor = a
                label = self.get_label(df.iloc[n], grouping, numerical)
                circles.append((pos, radii[n], label))

                r = radii[i]

                while True:
                    try:
                        pos = self.get_position(r, circles[a], circles[n])
                        self.get_intersections((pos, r), circles)
                    except ValueError:
                        # Either no angle could be detected between the
                        # last bubble and the anchor bubble, or the current
                        # bubble intersects with any other bubble.
                        if a + 1 < n:
                            a = a + 1
                        else:
                            a = last_anchor + 1
                            while True:
                                try:
                                    new_pos = self.get_position(
                                        r, circles[a], circles[n])
                                    self.get_intersections(
                                        (new_pos, r), circles)
                                except ValueError:
                                    if a + 1 == n:
                                        a = last_anchor
                                        n = n - 1
                                    else:
                                        a = a + 1
                                else:
                                    break
                    else:
                        break
                n = i
            label = self.get_label(df.iloc[n], grouping, numerical)
            circles.append((pos, radii[n], label))

        return circles

    def prepare_arguments(self, data, x, y, z, levels_x, levels_y):
        """
        Bubble placement algorithm:

        * place anchor bubble A at origin (0, 0)
        * add neighbor bubble N to the right of A so that they touch
        * For each additional bubble:
          * Repeat until a position P is found:
            * calculate the position P where I touches A and N
            * check if I at P intersects with any preceding bubble
              (ignoring any bubble earlier than A)
              * YES: set A to the next bubble after current A
              * NO: draw bubble at P
        """
        self.x = x
        self.y = y
        self.z = z

        df_freq = self.get_dataframe(data, x, y, z)
        circles = self.place_circles(df_freq)
        if z:
            _color_column = df_freq[self.COL_COLUMN]
        else:
            _color_column = df_freq.index
        return {"data": circles, "cix": _color_column}

    def plot_facet(self, data, color, **kwargs):
        self.args = self.prepare_arguments(data, self.x, self.y, self.z,
                                           self.levels_x, self.levels_y)
        cix = self.args.pop("cix")
        if self.z:
            self.colors = self.colorizer.get_hues(cix)
        else:
            self.colors = self.colorizer.get_palette(n=len(cix))

        self.artists = self.draw_circles(**self.args)
        self.colorize_plot()

        ax = plt.gca()
        ax.set_aspect(1)
        ax.autoscale(True, "both", True)
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        sns.despine(ax=ax, top=True, bottom=True, left=True, right=True)


provided_visualizations = [BubblePlot]
