"""
linkselect.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import division
from __future__ import unicode_literals

from coquery import options
from coquery.unicode import utf8
from coquery.links import Link

from .pyqt_compat import QtCore, QtWidgets, get_toplevel_window
from .ui.linkselectUi import Ui_LinkSelect

class LinkSelect(QtWidgets.QDialog):
    def __init__(self, res_from=None, rc_from=None, parent=None):
        super(LinkSelect, self).__init__(parent)
        self.res_from = res_from
        try:
            self.corpus_name = res_from.name
        except AttributeError:
            self.corpus_name = None
        self.rc_from = rc_from

        self.ui = Ui_LinkSelect()
        self.ui.setupUi(self)
        self.from_text = utf8(self.ui.label_from.text())
        self.from_corpus_text = utf8(self.ui.label_from_corpus.text())
        self.to_text = utf8(self.ui.label_to.text())
        self.explain_text = utf8(self.ui.label_explain.text())

        self.insert_data()
        self.ui.combo_corpus.currentIndexChanged.connect(self.external_changed)
        self.ui.tree_resource.currentItemChanged.connect(self.resource_changed)
        self.ui.tree_external.currentItemChanged.connect(self.external_resource_changed)

        self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)

        try:
            self.resize(options.settings.value("linkselect_size"))
        except TypeError:
            pass

        self.ui.tree_resource.setup_resource(get_toplevel_window().resource,
                                             skip=("coquery", "db"),
                                             checkable=False,
                                             links=False)
        self.ui.tree_resource.allSetExpanded(True)
        self.ui.tree_resource.setCurrentItemByString(self.rc_from)

    def check_dialog(self):
        self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
        self.ui.widget_link_info.hide()
        from_item = self.ui.tree_resource.currentItem()
        to_item = self.ui.tree_external.currentItem()
        if not to_item or not from_item:
            return
        if to_item.childCount() or from_item.childCount():
            return

        self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)
        self.ui.widget_link_info.show()

    def set_to_labels(self, **kwargs):
        self.ui.label_to.setText(self.to_text.format(**kwargs))
        self.ui.label_explain.setText(self.explain_text.format(**kwargs))

    def set_from_labels(self, **kwargs):
        self.ui.label_from.setText(self.from_text.format(**kwargs))
        self.ui.label_from_corpus.setText(self.from_corpus_text.format(**kwargs))

    def closeEvent(self, event):
        options.settings.setValue("linkselect_size", self.size())

    def exec_(self, *args, **kwargs):
        result = super(LinkSelect, self).exec_(*args, **kwargs)
        if result == self.Accepted:
            kwargs = {
                "res_from": self.corpus_name,
                "res_to": utf8(self.ui.combo_corpus.currentText()),
                "case": bool(self.ui.checkBox.checkState())}
            from_item = self.ui.tree_resource.currentItem()
            try:
                kwargs["rc_from"] = utf8(from_item.objectName())
            except AttributeError:
                kwargs["rc_from"] = None
            to_item = self.ui.tree_external.currentItem()
            try:
                kwargs["rc_to"] = utf8(to_item.objectName())
            except AttributeError:
                kwargs["rc_to"] = None
            return Link(**kwargs)
        else:
            return None

    @staticmethod
    def pick(res_from, rc_from, parent=None):
        dialog = LinkSelect(res_from, rc_from, parent=parent)
        dialog.setVisible(True)
        return dialog.exec_()

    def resource_changed(self, current, prev):
        if current.parent():
            from_table = utf8(current.parent().text(0))
            from_resource = utf8(current.text(0))
        else:
            from_table = "<not selected>"
            from_resource = "<not selected>"
        self.set_from_labels(
            from_res=self.corpus_name,
            from_table=from_table,
            from_resource=from_resource)
        self.check_dialog()

    def external_changed(self, index):
        if type(index) == int:
            corpus = utf8(self.ui.combo_corpus.itemText(index))
        else:
            corpus = utf8(index)
        if not corpus:
            return

        resource, _, _ = options.get_resource(corpus)
        self.ui.tree_external.setup_resource(resource,
                                             skip=("coquery"),
                                             checkable=False,
                                             links=False,
                                             view_tables=True)
        self.ui.tree_external.allSetExpanded(True)

    def external_resource_changed(self, current, prev):
        to_res = utf8(self.ui.combo_corpus.currentText())
        to_feature = utf8(current.text(0))
        if current.parent():
            to_table = utf8(current.parent().text(0))
        else:
            to_table = "invalid"
        self.set_to_labels(to=to_res, to_resource=to_feature, to_table=to_table)
        self.check_dialog()

    def clear_data(self):
        self.ui.combo_corpus.clear()
        self.ui.tree_external.clear()

    def insert_data(self):
        corpora = sorted([resource.name for _, (resource, _, _, _)
                          in options.cfg.current_resources.items()
                          if resource.name != self.corpus_name])
        self.ui.combo_corpus.addItems(corpora)
        min_width = self.ui.combo_corpus.sizeHint().width()
        self.ui.label_from_corpus.setMinimumWidth(min_width)
        self.external_changed(self.ui.combo_corpus.itemText(0))

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.reject()


class CorpusSelect(LinkSelect):
    def __init__(self, current, exclude_corpus=None, title=None, subtitle=None, parent=None):
        super(CorpusSelect, self).__init__(parent=parent)
        self.corpus_name = exclude_corpus

        # set widget content to current parameters
        self.ui.combo_corpus.blockSignals(True)
        self.clear_data()
        self.insert_data()
        ix = self.ui.combo_corpus.findText(current)
        if ix == -1:
            ix = 0
        self.ui.combo_corpus.setCurrentIndex(ix)
        self.ui.combo_corpus.blockSignals(False)

        self.ui.group_current_corpus.hide()
        self.ui.widget_link_info.hide()
        self.ui.checkBox.hide()
        self.ui.combo_corpus.setFocus()

        self.ui.tree_external.setSelectionMode(self.ui.tree_external.NoSelection)
        self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)
        if subtitle:
            self.ui.group_external_corpus.setTitle(subtitle)
        if title:
            self.setWindowTitle(title)

    @staticmethod
    def pick(current, exclude_corpus, title=None, subtitle=None, parent=None):
        dialog = CorpusSelect(current, exclude_corpus, title, subtitle, parent)
        dialog.setVisible(True)
        link = dialog.exec_()
        if link:
            return link.res_to
        else:
            return None

    def check_dialog(self):
        pass
