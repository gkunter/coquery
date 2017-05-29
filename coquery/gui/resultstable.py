# -*- coding: utf-8 -*-
"""
resultstable.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""
from __future__ import unicode_literals

import logging
from coquery import options
from coquery.defines import *
from coquery.unicode import utf8
from coquery import managers
from .pyqt_compat import QtCore, QtWidgets, QtGui, get_toplevel_window
from . import classes

_left_align = int(QtCore.Qt.AlignLeft) | int(QtCore.Qt.AlignVCenter)
_right_align = int(QtCore.Qt.AlignRight) | int(QtCore.Qt.AlignVCenter)

class CoqResultCellDelegate(QtWidgets.QStyledItemDelegate):
    fill = False

    def __init__(self, *args, **kwargs):
        threshold = kwargs.pop("threshold", 0.95)
        super(CoqResultCellDelegate, self).__init__(*args, **kwargs)
        CoqResultCellDelegate._app = options.cfg.app
        CoqResultCellDelegate._table = get_toplevel_window().table_model
        CoqResultCellDelegate.standard_bg = {
            True: [
                CoqResultCellDelegate._app.palette().color(
                    QtGui.QPalette.Normal, QtGui.QPalette.AlternateBase),
                CoqResultCellDelegate._app.palette().color(
                    QtGui.QPalette.Normal, QtGui.QPalette.Base)],
            False: [
                CoqResultCellDelegate._app.palette().color(
                    QtGui.QPalette.Disabled, QtGui.QPalette.AlternateBase),
                CoqResultCellDelegate._app.palette().color(
                    QtGui.QPalette.Disabled, QtGui.QPalette.Base)]}

        if not hasattr(CoqResultCellDelegate, "fg_color"):
            CoqResultCellDelegate.fg_color = None
        if not hasattr(CoqResultCellDelegate, "bg_color"):
            CoqResultCellDelegate.bg_color = None

    def get_foreground(self, option, index):
        if option.state & QtWidgets.QStyle.State_MouseOver:
            return self._app.palette().color(QtGui.QPalette().Link)
        elif option.state & QtWidgets.QStyle.State_Selected:
            return self._app.palette().color(QtGui.QPalette().HighlightedText)
        else:
            if self._table.is_visible(index):
                try:
                    return QtGui.QColor(options.cfg.row_color[self._table.content.index[index.row()]])
                except KeyError:
                    pass
                # return column color if specified:
                try:
                    return QtGui.QColor(options.cfg.column_color[self._table.header[index.column()]])
                except KeyError:
                    # return default color
                    return self.fg_color
            else:
                # return light grey for hidden cells:
                return self._app.palette().color(QtGui.QPalette.Disabled, QtGui.QPalette.Text)

    def get_background(self, option, index):
        if option.state & QtWidgets.QStyle.State_Selected:
            return self._app.palette().color(QtGui.QPalette().Highlight)
        else:
            if not self.bg_color:
                return self.standard_bg[self._table.is_visible(index)][index.row() & 1]
            else:
                return self.bg_color

    #def sizeHint(self, option, index):
        #rect = options.cfg.metrics.boundingRect(index.data(QtCore.Qt.DisplayRole))
        #return rect.adjusted(0, 0, 15, 0).size()

    def paint(self, painter, option, index):
        """
        Paint the results cell.

        The paint method of the cell delegates takes the representation
        from the table's :func:`data` method, using the DecorationRole role.
        On mouse-over, the cell is rendered like a clickable link.
        """
        content = index.data(QtCore.Qt.DisplayRole)
        if content == "" and not self.fill:
            return
        painter.save()

        # show content as a link on mouse-over:
        if option.state & QtWidgets.QStyle.State_MouseOver:
            font = painter.font()
            font.setUnderline(True)
            painter.setFont(font)

        fg = self.get_foreground(option, index)
        bg = self.get_background(option, index)
        if bg:
            painter.setBackground(bg)
            if option.state & QtWidgets.QStyle.State_Selected or self.fill:
                painter.fillRect(option.rect, bg)

        if fg:
            painter.setPen(QtGui.QPen(fg))

        try:
            if index.data(QtCore.Qt.TextAlignmentRole) == _left_align:
                painter.drawText(
                    option.rect.adjusted(2, 0, 2, 0),
                    _left_align | options.cfg.word_wrap,
                    content if isinstance(content, str) else str(content))
            else:
                painter.drawText(
                    option.rect.adjusted(-2, 0, -2, 0),
                    _right_align | options.cfg.word_wrap,
                    content if isinstance(content, str) else str(content))
        finally:
            painter.restore()


class CoqTotalDelegate(CoqResultCellDelegate):
    fill = True

    def __init__(self, *args, **kwargs):
        super(CoqTotalDelegate, self).__init__(*args, **kwargs)
        self.fg_color = self._app.palette().color(QtGui.QPalette.ButtonText)
        self.bg_color = self._app.palette().color(QtGui.QPalette.Button)


class CoqProbabilityDelegate(CoqResultCellDelegate):
    max_value = 1
    prefix = ""
    suffix = ""
    format_str = "{}{}{}"

    def paint(self, painter, option, index):
        """
        Paint the results cell.

        The paint method of the cell delegates takes the representation
        from the table's :func:`data` method, using the DecorationRole role.
        On mouse-over, the cell is rendered like a clickable link.
        """
        painter.save()

        try:
            value = float(index.data(QtCore.Qt.DisplayRole))
        except ValueError:
            painter.restore()
            return

        content = self.format_str.format(self.prefix, value, self.suffix)

        # show content as a link on mouse-over:
        if option.state & QtWidgets.QStyle.State_MouseOver:
            font = painter.font()
            font.setUnderline(True)
            painter.setFont(font)
        fg = self.get_foreground(option, index)
        bg = self.get_background(option, index)
        if bg:
            if option.state & QtWidgets.QStyle.State_Selected:
                painter.fillRect(option.rect, bg)
            elif value != 0:
                rect = QtCore.QRect(option.rect.topLeft(), option.rect.bottomRight())
                rect.setWidth(int(option.rect.width() * min(self.max_value, value)/self.max_value))
                painter.fillRect(rect, QtGui.QColor("lightgreen"))
        if fg:
            painter.setPen(QtGui.QPen(fg))

        try:
            if index.data(QtCore.Qt.TextAlignmentRole) == _left_align:
                painter.drawText(
                    option.rect.adjusted(2, 0, 2, 0),
                    _left_align | int(QtCore.Qt.TextWordWrap),
                    content)
            else:
                painter.drawText(
                    option.rect.adjusted(-2, 0, -2, 0),
                    _right_align | int(QtCore.Qt.TextWordWrap),
                    content)
        finally:
            painter.restore()

    #def get_background(self, option, index):
        #try:
            #value = float(index.data(QtCore.Qt.DisplayRole))
            #if  value > 1:
                #return QtGui.QColor("lightyellow")
            #else:
                #return super(CoqProbabilityDelegate, self).get_background(option, index)
        #except ValueError:
            #return super(CoqProbabilityDelegate, self).get_background(option, index)


class CoqPercentDelegate(CoqProbabilityDelegate):
    max_value = 100
    format_str = "{}{:3.1f}{}"
    suffix = "%"


class CoqLikelihoodDelegate(CoqResultCellDelegate):
    fill = True

    def __init__(self, *args, **kwargs):
        super(CoqLikelihoodDelegate, self).__init__(*args, **kwargs)
        self.threshold = kwargs.get("threshold")
        self.color_base = self._app.palette().color(QtGui.QPalette.Base)
        self.color_dark = self._app.palette().color(QtGui.QPalette.Button)
        self.color_darkest = self._app.palette().color(QtGui.QPalette.Mid)
        self.color_highlight = self._app.palette().color(QtGui.QPalette().Highlight)

    def paint(self, painter, option, index):
        self.col_label = self._table.header[index.column()].rpartition("_")[-1]
        self.group_value = self._table.content.iloc[:,0][index.row()]
        self.offs = self.col_label.count(":") + 1

        super(CoqLikelihoodDelegate, self).paint(painter, option, index)
        if (self.col_label.startswith(self.group_value) and
            self.col_label != self.group_value):
            painter.save()
            try:
                rect = option.rect
                painter.drawLine(rect.topLeft(), rect.topRight())
                painter.drawLine(rect.bottomLeft(), rect.bottomRight())
                painter.drawLine(rect.topLeft(), rect.bottomLeft())
                painter.drawLine(rect.topRight(), rect.bottomRight())
            finally:
                painter.restore()

    def get_background(self, option, index):
        if option.state & QtWidgets.QStyle.State_Selected:
            return self.color_highlight
        else:
            try:
                value = float(index.data(QtCore.Qt.UserRole+1))
            except (ValueError, TypeError):
                value = 0
            if abs(value) > self.threshold - 0.5/(10 ** options.cfg.digits):
                if value > 0:
                    return QtGui.QColor("#fc8d59")
                else:
                    return QtGui.QColor("#91bfdb")
            else:
                if index.column() - self.offs == index.row():
                    return self.color_dark
                else:
                    return self.color_base


class CoqResultsTableView(classes.CoqTableView):
    def __init__(self, *args, **kwargs):
        super(CoqResultsTableView, self).__init__(*args, **kwargs)
        self.next_ix = None

        self.setWordWrap(options.cfg.word_wrap)
        self.setFont(options.cfg.table_font)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setSortingEnabled(False)
        self.setSelectionBehavior(self.SelectItems)
        self.setSelectionMode(self.ExtendedSelection)

        v_header = classes.CoqVerticalHeader(QtCore.Qt.Vertical)
        v_header.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        v_header.setDefaultSectionSize(v_header.minimumSectionSize())
        self.setVerticalHeader(v_header)

        h_header = classes.CoqHorizontalHeader(QtCore.Qt.Horizontal)
        h_header.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        h_header.setDefaultAlignment(
            QtCore.Qt.AlignCenter |
            QtCore.Qt.AlignmentFlag(QtCore.Qt.TextWordWrap))
        self.setHorizontalHeader(h_header)

    def setDelegates(self):
        h_header = self.horizontalHeader()
        session = get_toplevel_window().Session
        manager = managers.get_manager(options.cfg.MODE, session.Resource.name)
        for i in range(h_header.count()):
            column = self.model().header[h_header.logicalIndex(i)]
            if column.startswith("func_"):
                fun = manager.get_function(column)
                try:
                    retranslate = dict(zip(COLUMN_NAMES.values(), COLUMN_NAMES.keys()))[fun.get_name()]
                except (KeyError, AttributeError):
                    pass
                else:
                    column = retranslate
            if column in ("statistics_proportion",
                      "statistics_normalized", "statistics_ttr",
                      "statistics_group_proportion", "statistics_group_ttr",
                      "coq_conditional_probability",
                      "coq_conditional_probability_left",
                      "coq_conditional_probability_right",
                      "coq_statistics_uniquenessratio"):
                deleg = CoqProbabilityDelegate(self)
            elif column in ("statistics_percent", "statistics_group_percent"):
                deleg = CoqPercentDelegate(self)
            elif column in ("statistics_column_total"):
                deleg = CoqTotalDelegate(self)
            elif column.startswith("statistics_g_test"):
                deleg = CoqLikelihoodDelegate(self, threshold=manager.threshold)
            else:
                deleg = CoqResultCellDelegate(self)
            self.setItemDelegateForColumn(i, deleg)

        # reset row delegates if an ALL row has previously been set:
        if hasattr(self, "_old_row_delegate"):
            row, delegate = self._old_row_delegate
            self.setItemDelegateForRow(row, delegate)
            del self._old_row_delegate

        # set row delegate for ALL row of Contingency aggregates:
        if (options.cfg.MODE == QUERY_MODE_CONTINGENCY and
            not session.is_statistics_session()):
            row = self.model().rowCount() - 1
            self._old_row_delegate = (row, self.itemDelegateForRow(row))
            self.setItemDelegateForRow(row, CoqTotalDelegate(self))


class CoqHiddenResultsTable(CoqResultsTableView):
    def setDelegates(self):
        pass
