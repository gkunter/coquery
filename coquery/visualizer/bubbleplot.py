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
import time

from coquery.visualizer import visualizer as vis
import seaborn as sns
import matplotlib.pyplot as plt


class Bubbleplot(vis.Visualizer):
    name = "Bubble Chart"
    icon = "Scatterplot"

    sqrt_dict = {}

    _angle_cache = {}
    _angle_calls = 0
    _r_cache = {}
    _r_calls = 0
    _vector_cache = {}
    _vector_calls = 0

    def __init__(self, *args, **kwargs):
        super(Bubbleplot, self).__init__(*args, **kwargs)
        self.circles = []

    #def set_defaults(self):
        #self.options["color_palette"] = "Blues"
        #self.options["color_number"] = len(self._levels[-1])
        #super(Bubbleplot, self).set_defaults()
        #self.options["label_y_axis"] = ""
        #self.options["label_x_axis"] = "[bubble labels]"

    def setup_figure(self):
        with sns.axes_style("white"):
            super(Bubbleplot, self).setup_figure()

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

    def plot_facet(self, data, color, **kwargs):
        def r(freq):
            self._r_calls += 1
            try:
                return self._r_cache[freq]
            except KeyError:
                self._r_cache[freq] = math.sqrt(freq / math.pi)
                return self._r_cache[freq]

        def rotate_vector(x, theta):
            """
            Rotate the vector (x, 0) by the given angle.

            Returns
            -------
            v : tuple
                The rotated vector.
            """
            return x * math.cos(theta), x * math.sin(theta)
            self._vector_calls += 1
            _key = round(theta, 2)
            try:
                cos_theta, sin_theta = self._vector_cache[_key]
            except KeyError:
                cos_theta = math.cos(theta)
                sin_theta = math.sin(theta)
                self._vector_cache[_key] = (cos_theta, sin_theta)

            return (x * cos_theta, x * sin_theta)

        def get_angle(a, b, c):
            """
            Return the angle A by using the Law of Cosines.

            Parameters
            ----------
            a, b, c : float
                The length of sides a, b, c in a triangle.

            """
            self._angle_calls += 1
            _key = a, b, c
            try:
                return self._angle_cache[_key]
            except KeyError:
                assert (b != 0.0,
                        "Zero length detected (b={}, c={})".format(b, c))
                assert (c != 0.0,
                        "Zero length detected (b={}, c={})".format(b, c))
                x = (b ** 2 + c ** 2 - a ** 2) / (2 * b * c)
                if x > 1 or x < 0:
                    #print("\t\tget_angle({:.2}, {:.2}, {:.2}) = NONE ({:.2})".format(
                        #a, b, c, x))
                    raise ValueError("Illegal angle")
                # Allow angles > 180 degrees:
                if x > 1:
                    self._angle_cache[_key] = math.acos(x - 1)
                else:
                    self._angle_cache[_key] = math.acos(x)
            val = self._angle_cache[_key]
            #print("\t\tget_angle({:.2}, {:.2}, {:.2}) = {:.2} ({:.2})".format(
                #a, b, c, val, x))
            return val

        def get_position(r, a, n):
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
            #print("\tget_position(r={:.2}, a={}, n={})".format(r, a, n))
            A = self.pos[a]
            N = self.pos[n]

            #       I
            #      / \
            #   b /   \ a
            #    /     \
            #  A ------- N
            #       c

            # get side lengths:
            l_a = radii[n] + r
            l_b = radii[a] + r

            # l_c is actually the distance between the centers of the
            # anchor and the neighbor circles:
            l_c = math.sqrt((A[0] - N[0]) ** 2 + (A[1] - N[1]) ** 2)

            # the starting angle is the angle between a union vector
            # and the vector between the anchor and the neighbor:
            # start_angle = angle_vect((1,  0), (N[0] - A[0], N[1] - A[1]))

            # in this special case, the call to angle_vect() can be
            # replaced by this expression:
            start_angle = math.atan2(N[1] - A[1],
                                     N[0] - A[0])

            theta = get_angle(l_a, l_b, l_c) + start_angle

            val = (A[0] + l_b * math.cos(theta), A[1] + l_b * math.sin(theta))
            #print("\tPosition = {:3.2f}, {:3.2f}".format(*val))
            return val

        def intersecting(tup1, tup2):
            ((x1, y1), r1) = tup1
            ((x2, y2), r2) = tup2

            lower = (r1 - r2) ** 2
            upper = (r1 + r2) ** 2

            val = (x1 - x2) ** 2 + (y1 - y2) ** 2

            return lower <= val < upper - 0.01

        def draw_circle(k):
            row = df_freq.iloc[k]
            freq = row["Freq"]
            rad = radii[k]

            group = row[[cat for cat in [self.x, self.y] if cat]].values
            label = " | ".join(group)
            #print("draw_circle({}, {}, {}, {:.3})".format(
                #k, label, int(rad ** 2 * math.pi), rad))
            c = self.palette[k]
            x, y = self.pos[k]

            circ = plt.Circle((x, y), rad, color=c)
            ax.add_artist(circ)
            circ.set_edgecolor("black")

            #font = self.options.get("font_x_axis",
                                    #self.options["figure_font"])
            ax.text(x, y,
                    #"{}: {}".format(label.replace(" | ", "\n"), freq),
                    str(k),
                    ha="center",
                    va="center")
                    #family=font.family(),
                    #fontsize=font.pointSize())

            self.max_x = max(self.max_x, x + rad)
            self.max_y = max(self.max_y, y + rad)
            self.min_x = min(self.min_x, x - rad)
            self.min_y = min(self.min_y, y - rad)
            self.circles.append(((x, y), rad, "{}: {}".format(label, freq)))

            return group

        def get_intersections(circ, lower, upper):
            for x, trial in enumerate(zip(self.pos[lower:upper],
                                       radii[lower:upper])):
                if intersecting(circ, trial):
                    #print("\tget_intersections(from={}, to={}) = {}".format(
                        #lower, upper, x))
                    raise ValueError
                    return x


            #print("\tget_intersections(from={}, to={}): None".format(lower, upper))
            return None


        grouping = [cat for cat in [self.x, self.y] if cat]

        aggregator = vis.Aggregator()
        aggregator.add("coquery_invisible_corpus_id", "count", "Freq")
        df_freq = aggregator.process(data, grouping)
        self.palette = sns.color_palette("Purples", len(df_freq))

        if (self.x and self.y):
            df_freq = df_freq.sort_values(by=[self.y, "Freq"],
                                          ascending=[True, False])
        else:
            df_freq = df_freq.sort_values(by="Freq", ascending=False)

        #df_freq = df_freq.sort_values(grouping + ["Freq"],
                                      #ascending=[True] * len(grouping) + [False])
        radii = list(map(r, df_freq["Freq"].values))
        ax = plt.gca()

        self.max_x = 0
        self.max_y = 0
        self.min_x = 0
        self.min_y = 0
        ax.set_aspect(1)

        # Algorithm:
        #
        # * place anchor bubble A at origin (0, 0)
        # * add neighbor bubble N to the right of A so that they touch
        # * For each additional bubble:
        #   * Repeat until a position P is found:
        #     * calculate the position P where I touches A and N
        #     * check if I at P intersects with any preceding bubble
        #       (ignoring any bubble earlier than A)
        #       * YES: set A to the next bubble after current A
        #       * NO: draw bubble at P

        a = 0
        completed = 0

        self.pos = [(0, 0)] * len(df_freq)
        draw_circle(0)

        if len(df_freq) > 1:
            n = 1
            self.pos[1] = (self.pos[0][0] + radii[0] + radii[n],
                           self.pos[0][1])
            last_group = draw_circle(1)

            for i in range(n + 1, len(df_freq)):
                r = radii[i]
                group = df_freq.iloc[i][grouping].values
                #print("----", i)

                while True:
                    try:
                        pos = get_position(r, a, n)
                        intersect = get_intersections((pos, r), 0, i - 1)

                    except (ValueError, ZeroDivisionError):
                        if a < i - 1:
                            a = a + 1
                            #print("\n\tOVERLAP, SET NEW ANCHOR={}".format(a))
                        else:
                            a = n
                            n = n - 1
                            while True:
                                try:
                                    new_pos = get_position(r, a, n)
                                    get_intersections((new_pos, r), 0, i - 1)
                                except (ValueError, ZeroDivisionError):
                                    if n == 0:
                                        a = a - 1
                                        n = a - 1
                                    else:
                                        n = n - 1

                                else:
                                    #print("\n\tOUT OF CHOICES: NEW NEIGBOR={}, RESET ANCHOR={}".format(n, a))
                                    break
                    else:
                        break
                #completed = max(a, completed)

                self.pos[i] = pos
                draw_circle(i)
                n = i

        ax.set_ylim(self.min_y * 1.01, self.max_y * 1.01)
        ax.set_xlim(self.min_x * 1.01, self.max_x * 1.01)
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)


provided_visualizations = [Bubbleplot]
