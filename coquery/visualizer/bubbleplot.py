# -*- coding: utf-8 -*-
""" 
bubbleplot.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
from __future__ import division
import math

from coquery.visualizer import visualizer as vis
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

from coquery import options

class Visualizer(vis.BaseVisualizer):
    dimensionality=2

    sqrt_dict = {}

    _angle_cache = {}
    _angle_calls = 0
    _r_cache = {}
    _r_calls = 0
    _vector_cache = {}
    _vector_calls = 0

    def __init__(self, *args, **kwargs):
        super(Visualizer, self).__init__(*args, **kwargs)
        self.circles = []


    def set_defaults(self):
        self.options["color_palette"] = "Blues"
        self.options["color_number"] = len(self._levels[-1])
        super(Visualizer, self).set_defaults()
        self.options["label_y_axis"] = ""
        self.options["label_x_axis"] = "[bubble labels]"

    def setup_figure(self):
        with sns.axes_style("white"):
            super(Visualizer, self).setup_figure()

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

    def draw(self):
        """ 
        Draw a bubble chart. 
        """
        
        def plot_facet(data, color):
            def r(freq):
                self._r_calls += 1
                try:
                    return self._r_cache[freq]
                except KeyError:
                    self._r_cache[freq] = math.sqrt(freq / math.pi)
                    return self._r_cache[freq]

            def rotate_vector(v, angle):
                """
                Rotate the vector (x, y) by the given angle.
                
                Returns
                -------
                v : tuple
                    The rotated vector.
                """
                self._vector_calls += 1
                (x, y) = v
                _key = round(angle, 2)
                try:
                    cos_theta, sin_theta = self._vector_cache[_key]
                except KeyError:
                    cos_theta = math.cos(angle)
                    sin_theta = math.sin(angle)
                    self._vector_cache[_key] = (cos_theta, sin_theta)

                return x*cos_theta - y*sin_theta, x*sin_theta + y*cos_theta

            def get_angle(a, b, c):
                """
                Return the angle A by using the Law of Cosines.
                
                Parameters
                ----------
                a, b, c : float
                    The length of sides a, b, c in a triangle.
                
                """
                self._angle_calls += 1
                _key = (round(a, 2), round(b, 2), round(c, 2))
                try:
                    return self._angle_cache[_key]
                except KeyError:
                    x = (b**2 + c**2 - a**2) / (2 * b * c)
                    if x > 2:
                        raise ValueError("Illegal angle")
                    # Allow angles > 180 degrees:
                    if x > 1:
                        self._angle_cache[_key] = (math.acos(x-1))
                    else:
                        self._angle_cache[_key] = math.acos(x)
                return self._angle_cache[_key]
            
            #def angle_vect((x1, y1), (x2, y2)):
                #return math.atan2(x1*y2 - y1*x2, x1*x2 + y1*y2)  # atan2(y, x) or atan2(sin, cos)
            
            def get_position(i, a, n):
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
                i, a, n : int 
                    The index of the next bubble (i), the anchor bubble (a),
                    and the neighboring bubble (n).

                """
                # get radii:
                r_a = df_freq.iloc[a]["r"]
                r_n = df_freq.iloc[n]["r"]
                r_i = df_freq.iloc[i]["r"]
                
                A = self.pos[a]
                N = self.pos[n]

                #       I
                #      / \
                #   b /   \ a
                #    /     \
                #  A ------- N
                #       c

                # get side lengths:
                l_a = r_n + r_i
                l_b = r_a + r_i
                # l_c is actually the distance between the centers of the 
                # anchor and the neighbor circles:
                l_c = math.sqrt((A[0] - N[0]) ** 2 + (A[1] - N[1]) ** 2)
                
                # the starting angle is the angle between a union vector
                # and the vector between the anchor and the neighbor:
                #start_angle = angle_vect(
                    #(1,  0),
                    #(N[0] - A[0], N[1] - A[1]))
                
                # in this special case, the call to angle_vect() can be 
                # replaced by this expression:
                start_angle = math.atan2(N[1] - A[1], N[0] - A[0])

                angle = get_angle(l_a, l_b, l_c) + start_angle
                nx, ny = rotate_vector((l_b, 0), angle)
                nx = nx + A[0]
                ny = ny + A[1]

                return (nx, ny)

            def intersecting(p, q):
                r_p = df_freq.iloc[p]["r"]
                r_q = df_freq.iloc[q]["r"]
                x_p, y_p = self.pos[p]
                x_q, y_q = self.pos[q]

                lower = (r_p - r_q)**2
                upper = (r_p + r_q)**2
                
                return lower <= (x_p - x_q) ** 2 + (y_p - y_q) ** 2 < upper - 0.01

            def draw_circle(k):
                row = df_freq.iloc[k]
                freq = row["Freq"]
                rad = row["r"]
                label = " | ".join(list(row[self._groupby]))
                #c = self.options["color_palette_values"][k % self.options["color_number"]]

                c = self._col_dict[row[self._groupby[-1]]]
                x, y = self.pos[k]
                
                circ = plt.Circle((x, y), max(0, rad - 0.05), color=c)
                ax.add_artist(circ)
                circ.set_edgecolor("black")
                
                try:
                    font = self.options.get("font_x_axis", self.options["figure_font"])
                    ax.text(x, y, 
                            "{}: {}".format(label.replace(" | ", "\n"), freq), 
                            ha="center", 
                            va="center",
                            family=font.family(),
                            fontsize=font.pointSize())
                except Exception as e:
                    print(e)
                    raise 
                self.max_x = max(self.max_x, x + rad)
                self.max_y = max(self.max_y, y + rad)
                self.min_x = min(self.min_x, x - rad)
                self.min_y = min(self.min_y, y - rad)
                self.circles.append((self.pos[k], rad,  "{}: {}".format(label, freq)))

            def get_intersections(i, lower, upper):
                for x in range(lower, upper):
                    if intersecting(i, x):
                        return True
                return False

            group_columns = [x for x in data.columns if not x.startswith("coquery_invisible")]
            gp = data.fillna("").groupby(group_columns)
            df_freq = gp.agg(len).reset_index()
            columns = list(df_freq.columns)
            columns[-1] = "Freq"
            df_freq.columns = columns
            self.set_palette_values(len(set(df_freq[self._groupby[-1]])))
            if len(self._groupby) == 2:
                df_freq.sort([self._groupby[-1], "Freq"], ascending=[False, False], inplace=True)
                self._col_dict = dict(zip(self._levels[-1], self.options["color_palette_values"]))
            else:
                df_freq.sort("Freq", ascending=False, inplace=True)
                self._col_dict = dict(zip(df_freq[self._groupby[-1]], self.options["color_palette_values"]))
            df_freq["r"] = df_freq["Freq"].map(r)
            ax = plt.gca()
            

            self.max_x = 0
            self.max_y = 0
            self.min_x = 0
            self.min_y = 0
            ax.set_aspect(1)
            
            a = 0

            self.pos = [(None, None)] * len(df_freq.index)
            
            completed = 0
            for i in range(len(df_freq.index)):
                if i == 0:
                    self.pos[i] = 0, 0
                elif i == 1:
                    self.pos[1] = self.pos[0][0] + df_freq.iloc[0]["r"] + df_freq.iloc[1]["r"], self.pos[0][1]
                else:
                    self.pos[i] = get_position(i, a, n)
                    while get_intersections(i, completed, n) and a < i:
                        a = a + 1
                        # Intersections not only trigger an anchor bubble change,
                        # they also indicate that a closed ring of bubbles has 
                        # been completed. All bubbles within the closed ring do
                        # not have to be considered for collision detections, so
                        # keeping track of the completed bubbles speeds up the 
                        # algorithm:
                        # (at least, that's the idea, but it doesn't seem to
                        # work like this -- therefore, this speed-up is 
                        # currently disabled)
                        # completed = a
                        # If there is no position at which the next bubble can be 
                        # placed so that it is tangent to both the neighbor and 
                        # the anchor, get_position() raises a ValueError 
                        # exception.
                        try:
                            self.pos[i] = get_position(i, a, n)
                        except ValueError:
                            continue

                draw_circle(i)
                # The current bubble becomes the new neighbor bubble:
                n = i
                    
            ax.set_ylim(self.min_y * 1.05, self.max_y * 1.05)
            ax.set_xlim(self.min_x * 1.05, self.max_x * 1.05)
            ax.get_xaxis().set_visible(False)
            ax.get_yaxis().set_visible(False)
            
        sns.despine(self.g.fig, 
                    left=True, right=True, top=True, bottom=True)

        try:
            self.map_data(plot_facet)
        except Exception as e:
            print(e)
            raise e
        
        if len(self._groupby) == 2:
            self.add_legend(levels=self._levels[-1])
