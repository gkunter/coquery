# -*- coding: utf-8 -*-

import sys
from PySide import QtCore, QtGui
import os

sys.path.append(os.path.join(sys.path[0], "../coquery"))
sys.path.append(os.path.join(sys.path[0], "../coquery/corpora"))
from corpus import collapse_words
from ice_ng import Resource

class Corpus(object):
    def __init__(self):
        self.resource = Resource()

    def tag_to_qhtml(self, s):
        translate_dict = {
            "heading": "h1",
            "boldface": "b",
            "italics": "i",
            "underline": "u",
            "superscript": "sup",
            "subscript": "sup",
            "text": "html", 
            "other-language": "i",
            "deleted": "s",
            "error": "s"}
        if s in translate_dict:
            return translate_dict[s]
        else:
            return s

    def render_context(self, token_id = 215852, token_width=1):
        #start = max(0, token_id - context_width)
        #end = token_id + token_width + context_width - 1

        #S = "SELECT {corpus}.{corpus_id}, {word}, {tag}, {tag_type}, {attribute}, {tag_id} FROM {corpus} INNER JOIN {word_table} ON {corpus}.{corpus_word_id} = {word_table}.{word_id} LEFT JOIN {tag_table} ON {corpus}.{corpus_id} = {tag_table}.{tag_corpus_id} WHERE {corpus}.{corpus_id} BETWEEN {start} AND {end} AND {corpus}.{source_id} = {current_source_id}".format(
            #corpus=self.resource.corpus_table,
            #corpus_id=self.resource.corpus_id,
            #corpus_word_id=self.resource.corpus_word_id,
            #source_id=self.resource.corpus_source_id,
            
            #word=self.resource.word_label,
            #word_table=self.resource.word_table,
            #word_id=self.resource.word_id,
            
            #tag_table=self.resource.tag_table,
            #tag=self.resource.tag_label,
            #tag_id=self.resource.tag_id,
            #tag_corpus_id=self.resource.tag_corpus_id,
            #tag_type=self.resource.tag_type,
            #attribute=self.resource.tag_attribute,
            
            #current_source_id=source_id,
            #start=start, end=end)
        #cur = self.resource.DB.execute_cursor(S)
        #entities = {}
        #for row in cur:
            #if row[self.resource.corpus_id] not in entities:
                #entities[row[self.resource.corpus_id]] = []
            #entities[row[self.resource.corpus_id]].append(row)

        entities = {215850: [{'TokenId': 215850, 'Attribute': '', 'TagId': 18271, 'Tag': 'p', 'Text': '.', 'Type': 'close'}], 215851: [{'TokenId': 215851, 'Attribute': '', 'TagId': 18272, 'Tag': 'heading', 'Text': 'RESULTS', 'Type': 'open'}, {'TokenId': 215851, 'Attribute': '', 'TagId': 18273, 'Tag': 'heading', 'Text': 'RESULTS', 'Type': 'close'}], 215852: [{'TokenId': 215852, 'Attribute': 'type=graphic', 'TagId': 1874, 'Tag': 'object', 'Text': 'Sex', 'Type': 'entity'}, {'TokenId': 215852, 'Attribute': '', 'TagId': 18274, 'Tag': 'p', 'Text': 'Sex', 'Type': 'open'}, {'TokenId': 215852, 'Attribute': '', 'TagId': 18275, 'Tag': 'boldface', 'Text': 'Sex', 'Type': 'open'}, {'TokenId': 215852, 'Attribute': '', 'TagId': 18276, 'Tag': 'boldface', 'Text': 'Sex', 'Type': 'close'}], 215853: [{'TokenId': 215853, 'Attribute': None, 'TagId': None, 'Tag': None, 'Text': ':', 'Type': None}], 215854: [{'TokenId': 215854, 'Attribute': None, 'TagId': None, 'Tag': None, 'Text': 'Data', 'Type': None}]}


        context = []
        # we need to keep track of any opening and closing tag that does not
        # have its matching tag in the selected context:
        opened_tags = []
        closed_tags = []
        for token in sorted(entities):
            entity_list = sorted(entities[token], key=lambda x:x[self.resource.tag_id])
            text_output = False
            word = entity_list[0][self.resource.word_label]
            correct_word = False
            for row in entity_list:
                tag = row[self.resource.tag_label]
                attributes = row[self.resource.tag_attribute]
                tag_type = row[self.resource.tag_type]
                if tag == "object":
                    if "type=table" in attributes:
                        context.append("<table>")
                        context.append("<tr>")
                        context.append("<td>")
                        context.append("[placeholder table]")
                        context.append("</td>")
                        context.append("</tr>")
                        context.append("</table>")

                    if "type=graphic" in attributes:
                        context.append("<br/><img src='../logo/placeholder.png'/><br/>")
                        
                if tag == "error":
                    for x in [attr.split("=") for attr in attributes.split(",") if "=" in attr]:
                        if x[0] == "corrected":
                            correct_word = x[1]
                            break
                if tag_type == "entity":
                    if tag == "error":
                        if attributes.startswith("corrected="):
                            correct_word = attributes[len("corrected="):]
                        context.append('<span style="color: darkgreen;">{}</span>'.format(correct_word))
                    elif tag == "x-anonym-x":
                        context.append("█████")
                if tag_type == "open":
                    if tag == "error":
                        attributes = 'style="color: darkgrey;"'
                    if tag == "other-language":
                        attributes = 'style="color: darkblue;"'
                    tag = self.tag_to_qhtml(tag)
                    context.append("<{} {}>".format(tag, attributes))
                    opened_tags.append(row[self.resource.tag_label])
                elif tag_type == "close":
                    #if tag == "error":
                        #tag = "span"
                    if not text_output:
                        text_output = True
                        if token == token_id:
                            context.append('<span style="font-weight: bold; background-color: palegreen; border-style: outset;" >')
                        context.append(word)
                    context.append("</{} {}>".format(self.tag_to_qhtml(tag), attributes))
                    try:
                        if opened_tags[-1] == row[self.resource.tag_label]:
                            opened_tags.pop(len(opened_tags)-1)
                    except IndexError:
                        closed_tags.append(tag)
                        pass
                    if correct_word:
                        context.append('<span style="color: darkgreen;">{}</span>'.format(correct_word))
                        correct_word = ""
            if not text_output:
                if token == token_id:
                    context.append('<span style="font-weight: bold; background-color: palegreen; border-style: outset;" >')
                context.append(word)
            if token == token_id + token_width - 1:
                context.append('</span>')
        for x in opened_tags[::-1]:
            context.append("</{}>".format(self.tag_to_qhtml(x)))
        
        for x in closed_tags:
            context.insert(0, ("<{}>".format(self.tag_to_qhtml(x))))

            
        return collapse_words(context)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    dialog = QtGui.QWidget()
    layout = QtGui.QHBoxLayout(dialog)
    label = QtGui.QLabel()
    print(Corpus().render_context())
    label.setText(Corpus().render_context())
    layout.addWidget(label)
    dialog.show()
    sys.exit(app.exec_())
