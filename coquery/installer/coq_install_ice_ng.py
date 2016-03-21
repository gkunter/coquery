# -*- coding: utf-8 -*-
"""
coq_install_ice_ng.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals
from __future__ import print_function
import os.path
import codecs, string
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO
    
from coquery.corpusbuilder import *
from coquery.bibliography import *

class corpus_code():
    #def get_tag_translate(self, tag):
        #translate_dict = {
            #"p": "p",
            #"punctuation": "",
            #"heading": "h1",
            #"boldface": "b",
            #"italics": "i",
            #"underline": "u",
            #"superscript": "sup",
            #"subscript": "sup",
            #"text": "html", 
            #"deleted": "s",
            #"other-language": "span style='font-style: italic;'",
            #"quote": "span style='font-style: italic; color: darkgrey; '",
            #"error": "s"}
        #if tag in translate_dict:
            #return translate_dict[tag]
        #else:
            #print("unsupported tag: ", tag)
            #return tag

    def get_tag_translate(self, tag):
        translate_dict = {
            "p": "p",
            "punctuation": "",
            "heading": "span style='font-style: bold'",
            #"heading": "span style='font-style: bold; font-size:150%'",
            #"h1": "span style='font-style: bold; font-size:150%'",
            "boldface": "b",
            "italics": "i",
            "underline": "u",
            "superscript": "sup",
            "subscript": "sup",
            "object": "object",
            "text": "html"}
        
        if tag in translate_dict:
            return translate_dict[tag]
        else:
            print("unsupported tag: ", tag)
            return tag

    def get_context_stylesheet(self):
        """
        """
        return "h1 { background-color: #aa0000; }"

    def renderer_open_element(self, tag, attributes):
        context = super(Corpus, self).renderer_open_element(tag, attributes)
        if tag == "object":
            path = os.path.join(options.cfg.base_path, "icons", "artwork")
            # add placeholder images for <object> tags
            if attributes.get("type") == "formula":
                context.append("<br/><img src='{}/formula.png'/><br/>".format(path))
            elif attributes.get("type") == "table":
                context.append("<br/><img src='{}/placeholder_table.png'/><br/>".format(path))
            elif attributes.get("type") == "graphic":
                context.append("<br/><img src='{}/placeholder.png'/><br/>".format(path))
        if tag == "x-anonym-x":
            anon_type = "anonymized"
            try:
                anon_type = attributes["type"]
            except KeyError:
                pass
            context.append(' <span style="color: lightgrey; background: black;">&nbsp;&nbsp;&nbsp;{}&nbsp;&nbsp;&nbsp;</span> '.format(anon_type))

        if tag == "x-anonym-x":
            anon_type = "anonymized"
            try:
                anon_type = attributes["type"]
            except KeyError:
                pass
            context.append(' <span style="color: lightgrey; background: black;">&nbsp;&nbsp;&nbsp;{}&nbsp;&nbsp;&nbsp;</span> '.format(anon_type))

        return context

    def renderer_close_element(self, tag, attributes):
        context = super(Corpus, self).renderer_close_element(tag, attributes)
        if tag == "error":
            try:
                context.append('<span style="color: darkgreen;">{}</span>'.format(attributes["corrected"]))
            except KeyError:
                pass
        #if tag == "x-anonym-x":
            #anon_type = "anonymized"
            #try:
                #anon_type = attributes["type"]
            #except AttributeError:
                #pass
            #context.append('<span style="color: lightgrey; background: black;">&nbsp;&nbsp;&nbsp;{}&nbsp;&nbsp;&nbsp;</span>'.format(anon_type))

        return context


    #def render_context(self, token_id, source_id, token_width, context_width, widget):
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
            ##row = [x.decode("utf-8", errors="replace") if isinstance(x, str) else x for x in row]
            #if row[self.resource.corpus_id] not in entities:
                #entities[row[self.resource.corpus_id]] = []
            #entities[row[self.resource.corpus_id]].append(row)

        #context = []
        ## we need to keep track of any opening and closing tag that does not
        ## have its matching tag in the selected context:
        #opened_tags = []
        #closed_tags = []
        #correct_word = ""
        #for token in sorted(entities):
            #entity_list = sorted(entities[token], key=lambda x:x[self.resource.tag_id])
            #text_output = False
            #word = entity_list[0][self.resource.word_label]
            #for row in entity_list:
                #tag = row[self.resource.tag_label]
                
                ## special treatment for tags:
                #if tag:
                    #attributes = row[self.resource.tag_attribute]
                    #tag_type = row[self.resource.tag_type]

                    #if tag_type == "empty":
                        #if tag == "object":
                            ## add placeholder images for <object> tags
                            #if "type=table" in attributes:
                                #context.append("<br/><img src='../logo/placeholder_table.png'/><br/>")
                            #if "type=graphic" in attributes:
                                #context.append("<br/><img src='../logo/placeholder.png'/><br/>")
                            #if "type=formula" in attributes:
                                #context.append("<br/><img src='../logo/formula.png'/><br/>")
                        #elif tag == "error":
                            #if attributes.startswith("corrected="):
                                #correct_word = attributes[len("corrected="):]
                                #context.append('<span style="color: darkgreen;">{}</span>'.format(correct_word))
                            #correct_word  = ""
                        #elif tag == "break":
                            #context.append("<br/>")
                        #elif tag == "x-anonym-x":
                            #context.append('<span style="color: lightgrey; background: black;">&nbsp;&nbsp;&nbsp;{}&nbsp;&nbsp;&nbsp;</span>'.format(attributes[len("type="):]))
                        #else:
                            #print(tag)
                
                    #elif tag_type == "open":
                        #if tag == "error":
                            #if attributes.startswith("corrected="):
                                #correct_word = attributes[len("corrected="):]
                            #attributes = 'style="color: darkgrey;"'
                        ##elif tag == "other-language":
                            ##context.append('<span style="font-style: italic;">')
                        #tag = self.tag_to_qhtml(tag)
                        #if attributes:
                            #context.append("<{} {}>".format(tag, attributes))
                        #else:
                            #context.append("<{}>".format(tag))
                        #opened_tags.append(row[self.resource.tag_label])

                    #elif tag_type == "close":
                        ## if there is still a dangling correction from an 
                        ## open <error> tag, add the correct word now:
                        #if correct_word:
                            #context.append('<span style="color: darkgreen;">{}</span>'.format(correct_word))
                            #correct_word = ""
                        ## add the current token before processing any other
                        ## closing tag:
                        #if not text_output:
                            #text_output = True
                            #if token == token_id:
                                #context.append('<span style="font-weight: bold; background-color: lightyellow; border-style: outset;" >')
                            #context.append(word)
                        
                        #if attributes:
                            #context.append("</{} {}>".format(self.tag_to_qhtml(tag), attributes))
                        #else:
                            #context.append("</{}>".format(self.tag_to_qhtml(tag)))
                        ## if the current tag closes an earlier opening tag,
                        ## remove that tag from the list of open environments:
                        #try:
                            #if opened_tags[-1] == row[self.resource.tag_label]:
                                #opened_tags.pop(len(opened_tags)-1)
                        #except IndexError:
                            #closed_tags.append(tag)
                            #pass
                        #if tag == "other-language":
                            #context.append('</span>')
            #if not text_output:
                #if token == token_id:
                    #context.append('<span style="font-weight: bold; background-color: lightyellow; border-style: outset;" >')
                #context.append(word)
            #if token == token_id + token_width - 1:
                #context.append('</span>')
        #for x in opened_tags[::-1]:
            #context.append("</{}>".format(self.tag_to_qhtml(x)))
        #for x in closed_tags:
            #context.insert(0, ("<{}>".format(self.tag_to_qhtml(x))))

        #widget.ui.context_area.setText(collapse_words(context))

class BuilderClass(BaseCorpusBuilder):
    encoding = "latin-1"
    file_filter = "*.xml.pos"

    corpus_table = "Corpus"
    corpus_id = "ID"
    corpus_word_id = "WordId"
    corpus_file_id = "FileId"
    corpus_source_id = "SourceId"

    word_table = "Lexicon"
    word_id = "WordId"
    word_lemma = "Lemma"
    word_label = "Word"
    word_pos = "Pos"

    file_table = "Files"
    file_id = "FileId"
    file_name = "Filename"
    file_path = "Path"
    
    source_table = "Sources"
    source_id = "SourceId"
    source_mode = "Mode"
    source_age = "Age"
    source_gender = "Gender"
    source_ethnicity = "Ethnicity"
    source_date = "Date"
    source_icetext = "ICE_text_category"
    source_icetextcode = "ICE_text_code"
    source_place = "Place"

    expected_files = [
        'Pr_58.xml.pos', 'Pr_20.xml.pos', 'Pr_25.xml.pos', 
        'Pr_39.xml.pos', 'Pr_69.xml.pos', 'Pr_59.xml.pos', 
        'Pr_52.xml.pos', 'Pr_21.xml.pos', 'Pr_42.xml.pos', 
        'Pr_30.xml.pos', 'Pr_19.xml.pos', 'Pr_53.xml.pos', 
        'Pr_17.xml.pos', 'Pr_14.xml.pos', 'Pr_43.xml.pos', 
        'Pr_33.xml.pos', 'Pr_08.xml.pos', 'Pr_22.xml.pos', 
        'Pr_05.xml.pos', 'Pr_57.xml.pos', 'Pr_26.xml.pos', 
        'Pr_50.xml.pos', 'Pr_10.xml.pos', 'Pr_67.xml.pos', 
        'Pr_01.xml.pos', 'Pr_44.xml.pos', 'Pr_27.xml.pos', 
        'Pr_56.xml.pos', 'Pr_51.xml.pos', 'Pr_62.xml.pos', 
        'Pr_48.xml.pos', 'Pr_13.xml.pos', 'Pr_49.xml.pos', 
        'Pr_16.xml.pos', 'Pr_06.xml.pos', 'Pr_35.xml.pos', 
        'Pr_32.xml.pos', 'Pr_63.xml.pos', 'Pr_36.xml.pos', 
        'Pr_47.xml.pos', 'Pr_66.xml.pos', 'Pr_31.xml.pos', 
        'Pr_64.xml.pos', 'Pr_68.xml.pos', 'Pr_12.xml.pos', 
        'Pr_07.xml.pos', 'Pr_24.xml.pos', 'Pr_38.xml.pos', 
        'Pr_37.xml.pos', 'Pr_29.xml.pos', 'Pr_02.xml.pos', 
        'Pr_11.xml.pos', 'Pr_46.xml.pos', 'Pr_28.xml.pos', 
        'Pr_65.xml.pos', 'Pr_18.xml.pos', 'Pr_61.xml.pos', 
        'Pr_04.xml.pos', 'Pr_09.xml.pos', 'Pr_60.xml.pos', 
        'Pr_34.xml.pos', 'Pr_45.xml.pos', 'Pr_23.xml.pos', 
        'Pr_41.xml.pos', 'Pr_40.xml.pos', 'Pr_03.xml.pos', 
        'Pr_54.xml.pos', 'Pr_15.xml.pos', 'Pr_55.xml.pos', 
        'PNsc_13.xml.pos', 'PNsc_04.xml.pos', 'PNsc_09.xml.pos', 
        'PNsc_01.xml.pos', 'PNsc_05.xml.pos', 'PNsc_02.xml.pos', 
        'PNsc_14.xml.pos', 'PNsc_11.xml.pos', 'PNsc_06.xml.pos', 
        'PNsc_18.xml.pos', 'PNsc_15.xml.pos', 'PNsc_16.xml.pos', 
        'PNsc_19.xml.pos', 'PNsc_10.xml.pos', 'PNsc_12.xml.pos', 
        'PNsc_07.xml.pos', 'PNsc_03.xml.pos', 'PNsc_17.xml.pos', 
        'PNsc_08.xml.pos', 'PHum_09.xml.pos', 'PHum_12.xml.pos', 
        'PHum_08.xml.pos', 'PHum_01.xml.pos', 'PHum_20.xml.pos', 
        'PHum_02.xml.pos', 'PHum_06.xml.pos', 'PHum_14.xml.pos', 
        'PHum_11.xml.pos', 'PHum_15.xml.pos', 'PHum_16.xml.pos', 
        'PHum_10.xml.pos', 'PHum_05.xml.pos', 'PHum_18.xml.pos', 
        'PHum_13.xml.pos', 'PHum_04.xml.pos', 'PHum_03.xml.pos', 
        'PHum_07.xml.pos', 'PHum_17.xml.pos', 'PHum_19.xml.pos', 
        'ASsc_05.xml.pos', 'ASsc_11.xml.pos', 'ASsc_06.xml.pos', 
        'ASsc_07.xml.pos', 'ASsc_10.xml.pos', 'ASsc_08.xml.pos', 
        'ASsc_04.xml.pos', 'ASsc_02.xml.pos', 'ASsc_03.xml.pos', 
        'ASsc_01.xml.pos', 'ASsc_09.xml.pos', 'ess_10.xml.pos', 
        'ess_09.xml.pos', 'ess_06.xml.pos', 'ess_01.xml.pos', 
        'ess_07.xml.pos', 'ess_05.xml.pos', 'ess_11.xml.pos', 
        'ess_03.xml.pos', 'ess_12.xml.pos', 'ess_02.xml.pos', 
        'ess_04.xml.pos', 'ess_08.xml.pos', 'nov_14.xml.pos', 
        'nov_03.xml.pos', 'nov_07.xml.pos', 'nov_04.xml.pos', 
        'nov_15.xml.pos', 'nov_13.xml.pos', 'nov_05.xml.pos', 
        'nov_16.xml.pos', 'nov_11.xml.pos', 'nov_20.xml.pos', 
        'nov_06.xml.pos', 'nov_02.xml.pos', 'nov_01.xml.pos', 
        'nov_08.xml.pos', 'nov_09.xml.pos', 'nov_19.xml.pos', 
        'nov_12.xml.pos', 'nov_10.xml.pos', 'nov_18.xml.pos', 
        'nov_17.xml.pos', 'bl_28.xml.pos', 'bl_60.xml.pos', 
        'bl_15.xml.pos', 'bl_30.xml.pos', 'bl_20.xml.pos', 
        'bl_43.xml.pos', 'bl_70.xml.pos', 'bl_83.xml.pos', 
        'bl_33.xml.pos', 'bl_38.xml.pos', 'bl_54.xml.pos', 
        'bl_23.xml.pos', 'bl_88.xml.pos', 'bl_74.xml.pos', 
        'bl_82.xml.pos', 'bl_48.xml.pos', 'bl_14.xml.pos', 
        'bl_85.xml.pos', 'bl_59.xml.pos', 'bl_80.xml.pos', 
        'bl_36.xml.pos', 'bl_05.xml.pos', 'bl_03.xml.pos', 
        'bl_22.xml.pos', 'bl_61.xml.pos', 'bl_90.xml.pos', 
        'bl_73.xml.pos', 'bl_67.xml.pos', 'bl_53.xml.pos', 
        'bl_69.xml.pos', 'bl_01.xml.pos', 'bl_64.xml.pos', 
        'bl_91.xml.pos', 'bl_24.xml.pos', 'bl_52.xml.pos', 
        'bl_93.xml.pos', 'bl_81.xml.pos', 'bl_26.xml.pos', 
        'bl_18.xml.pos', 'bl_39.xml.pos', 'bl_77.xml.pos', 
        'bl_86.xml.pos', 'bl_46.xml.pos', 'bl_27.xml.pos', 
        'bl_42.xml.pos', 'bl_11.xml.pos', 'bl_09.xml.pos', 
        'bl_50.xml.pos', 'bl_35.xml.pos', 'bl_21.xml.pos', 
        'bl_16.xml.pos', 'bl_56.xml.pos', 'bl_87.xml.pos', 
        'bl_45.xml.pos', 'bl_34.xml.pos', 'bl_92.xml.pos', 
        'bl_68.xml.pos', 'bl_62.xml.pos', 'bl_25.xml.pos', 
        'bl_58.xml.pos', 'bl_79.xml.pos', 'bl_41.xml.pos', 
        'bl_72.xml.pos', 'bl_19.xml.pos', 'bl_12.xml.pos', 
        'bl_75.xml.pos', 'bl_65.xml.pos', 'bl_08.xml.pos', 
        'bl_89.xml.pos', 'bl_07.xml.pos', 'bl_78.xml.pos', 
        'bl_32.xml.pos', 'bl_47.xml.pos', 'bl_55.xml.pos', 
        'bl_10.xml.pos', 'bl_51.xml.pos', 'bl_76.xml.pos', 
        'bl_06.xml.pos', 'bl_66.xml.pos', 'bl_13.xml.pos', 
        'bl_49.xml.pos', 'bl_71.xml.pos', 'bl_44.xml.pos', 
        'bl_63.xml.pos', 'bl_84.xml.pos', 'bl_02.xml.pos', 
        'bl_37.xml.pos', 'bl_17.xml.pos', 'bl_40.xml.pos', 
        'bl_57.xml.pos', 'bl_04.xml.pos', 'bl_31.xml.pos', 
        'bl_29.xml.pos', 'ATec_05.xml.pos', 'ATec_06.xml.pos', 
        'ATec_02.xml.pos', 'ATec_07.xml.pos', 'ATec_10.xml.pos', 
        'ATec_04.xml.pos', 'ATec_01.xml.pos', 'ATec_11.xml.pos', 
        'ATec_08.xml.pos', 'ATec_03.xml.pos', 'ATec_09.xml.pos', 
        'PSsc_06.xml.pos', 'PSsc_09.xml.pos', 'PSsc_03.xml.pos', 
        'PSsc_05.xml.pos', 'PSsc_01.xml.pos', 'PSsc_12.xml.pos', 
        'PSsc_14.xml.pos', 'PSsc_04.xml.pos', 'PSsc_15.xml.pos', 
        'PSsc_13.xml.pos', 'PSsc_11.xml.pos', 'PSsc_08.xml.pos', 
        'PSsc_07.xml.pos', 'PSsc_02.xml.pos', 'PSsc_10.xml.pos', 
        'SkHo_14.xml.pos', 'SkHo_12.xml.pos', 'SkHo_24.xml.pos', 
        'SkHo_18.xml.pos', 'SkHo_02.xml.pos', 'SkHo_10.xml.pos', 
        'SkHo_01.xml.pos', 'SkHo_04.xml.pos', 'SkHo_09.xml.pos', 
        'SkHo_17.xml.pos', 'SkHo_15.xml.pos', 'SkHo_22.xml.pos', 
        'SkHo_03.xml.pos', 'SkHo_06.xml.pos', 'SkHo_16.xml.pos', 
        'SkHo_11.xml.pos', 'SkHo_20.xml.pos', 'SkHo_07.xml.pos', 
        'SkHo_25.xml.pos', 'SkHo_13.xml.pos', 'SkHo_23.xml.pos', 
        'SkHo_05.xml.pos', 'SkHo_08.xml.pos', 'SkHo_19.xml.pos', 
        'SkHo_21.xml.pos', 'sl_38.xml.pos', 'sl_09.xml.pos', 
        'sl_46.xml.pos', 'sl_17.xml.pos', 'sl_15.xml.pos', 
        'sl_27.xml.pos', 'sl_41.doc.xml.pos', 'sl_23.xml.pos', 
        'sl_26.xml.pos', 'sl_39.doc.xml.pos', 'sl_32.xml.pos', 
        'sl_04.xml.pos', 'sl_47.xml.pos', 'sl_18.xml.pos', 
        'sl_01.xml.pos', 'sl_19.xml.pos', 'sl_30.xml.pos', 
        'sl_43.xml.pos', 'sl_33.xml.pos', 'sl_06.xml.pos', 
        'sl_08.xml.pos', 'sl_29.xml.pos', 'sl_03.xml.pos', 
        'sl_36.xml.pos', 'sl_28.xml.pos', 'sl_35.xml.pos', 
        'sl_13.xml.pos', 'sl_34.xml.pos', 'sl_24.xml.pos', 
        'sl_16.xml.pos', 'sl_44.xml.pos', 'sl_10.xml.pos', 
        'sl_45.xml.pos', 'sl_05.xml.pos', 'sl_14.xml.pos', 
        'sl_07.xml.pos', 'sl_22.xml.pos', 'sl_25.xml.pos', 
        'sl_11.xml.pos', 'sl_40.doc.xml.pos', 'sl_12.xml.pos', 
        'sl_42.xml.pos', 'sl_02.xml.pos', 'sl_20.xml.pos', 
        'sl_21.xml.pos', 'sl_48.xml.pos', 'sl_37.xml.pos', 
        'sl_31.xml.pos', 'ANsc_11.xml.pos', 'ANsc_06.xml.pos', 
        'ANsc_03.xml.pos', 'ANsc_08.xml.pos', 'ANsc_02.xml.pos', 
        'ANsc_01.xml.pos', 'ANsc_10.xml.pos', 'ANsc_09.xml.pos', 
        'ANsc_07.xml.pos', 'ANsc_05.xml.pos', 'ANsc_04.xml.pos', 
        'AHum_10.xml.pos', 'AHum_02.xml.pos', 'AHum_09.xml.pos', 
        'AHum_07.xml.pos', 'AHum_04.xml.pos', 'AHum_05.xml.pos', 
        'AHum_11.xml.pos', 'AHum_08.xml.pos', 'AHum_06.xml.pos', 
        'AHum_01.xml.pos', 'AHum_03.xml.pos', 'ex_30.xml.pos', 
        'ex_26.xml.pos', 'ex_29.xml.pos', 'ex_33.xml.pos', 
        'ex_13.xml.pos', 'ex_08.xml.pos', 'ex_02.xml.pos', 
        'ex_54.xml.pos', 'ex_10.xml.pos', 'ex_35.xml.pos', 
        'ex_40.xml.pos', 'ex_50.xml.pos', 'ex_42.xml.pos', 
        'ex_46.xml.pos', 'ex_28.xml.pos', 'ex_16.xml.pos', 
        'ex_34.xml.pos', 'ex_31.xml.pos', 'ex_21.xml.pos', 
        'ex_14.xml.pos', 'ex_19.xml.pos', 'ex_23.xml.pos', 
        'ex_47.xml.pos', 'ex_20.xml.pos', 'ex_25.xml.pos', 
        'ex_43.xml.pos', 'ex_11.xml.pos', 'ex_39.xml.pos', 
        'ex_17.xml.pos', 'ex_01.xml.pos', 'ex_15.xml.pos', 
        'ex_37.xml.pos', 'ex_38.xml.pos', 'ex_41.xml.pos', 
        'ex_05.xml.pos', 'ex_24.xml.pos', 'ex_44.xml.pos', 
        'ex_49.xml.pos', 'ex_27.xml.pos', 'ex_06.xml.pos', 
        'ex_51.xml.pos', 'ex_48.xml.pos', 'ex_09.xml.pos', 
        'ex_53.xml.pos', 'ex_04.xml.pos', 'ex_07.xml.pos', 
        'ex_22.xml.pos', 'ex_18.xml.pos', 'ex_52.xml.pos', 
        'ex_36.xml.pos', 'ex_32.xml.pos', 'ex_03.xml.pos', 
        'ex_12.xml.pos', 'ex_45.xml.pos', 'PTec_22.xml.pos', 
        'PTec_19.xml.pos', 'PTec_31.xml.pos', 'PTec_16.xml.pos', 
        'PTec_01.xml.pos', 'PTec_33.xml.pos', 'PTec_06.xml.pos', 
        'PTec_13.xml.pos', 'PTec_02.xml.pos', 'PTec_15.xml.pos', 
        'PTec_12.xml.pos', 'PTec_26.xml.pos', 'PTec_29.xml.pos', 
        'PTec_27.xml.pos', 'PTec_10.xml.pos', 'PTec_32.xml.pos', 
        'PTec_14.xml.pos', 'PTec_24.xml.pos', 'PTec_08.xml.pos', 
        'PTec_07.xml.pos', 'PTec_21.xml.pos', 'PTec_11.xml.pos', 
        'PTec_17.xml.pos', 'PTec_04.xml.pos', 'PTec_03.xml.pos', 
        'PTec_09.xml.pos', 'PTec_30.xml.pos', 'PTec_23.xml.pos', 
        'PTec_20.xml.pos', 'PTec_25.xml.pos', 'PTec_28.xml.pos', 
        'PTec_18.xml.pos', 'PTec_05.xml.pos', 'adm_30.png.xml.pos', 
        'adm_26.xml.pos', 'adm_18.xml.pos', 'adm_04.xml.pos', 
        'adm_09.xml.pos', 'adm_15.xml.pos', 'adm_17.xml.pos', 
        'adm_28.png.xml.pos', 'adm_13.xml.pos', 'adm_07.xml.pos', 
        'adm_20.xml.pos', 'adm_21.xml.pos', 'adm_02.xml.pos', 
        'adm_23.xml.pos', 'adm_06.xml.pos', 'adm_01.xml.pos', 
        'adm_12.xml.pos', 'adm_25.xml.pos', 'adm_24.xml.pos', 
        'adm_19.xml.pos', 'adm_16.xml.pos', 'adm_08.xml.pos', 
        'adm_03.xml.pos', 'adm_14.xml.pos', 'adm_22.xml.pos', 
        'adm_27.xml.pos', 'adm_05.xml.pos', 'adm_29.png.xml.pos', 
        'adm_11.xml.pos', 'adm_10.xml.pos', 'ed_16.xml.pos', 
        'ed_14.xml.pos', 'ed_06.xml.pos', 'ed_25.xml.pos', 
        'ed_11.xml.pos', 'ed_02.xml.pos', 'ed_20.xml.pos', 
        'ed_17.xml.pos', 'ed_09.xml.pos', 'ed_26.xml.pos', 
        'ed_15.xml.pos', 'ed_18.xml.pos', 'ed_22.xml.pos', 
        'ed_01.xml.pos', 'ed_23.xml.pos', 'ed_10.xml.pos', 
        'ed_19.xml.pos', 'ed_28.xml.pos', 'ed_27.xml.pos', 
        'ed_04.xml.pos', 'ed_12.xml.pos', 'ed_13.xml.pos', 
        'ed_05.xml.pos', 'ed_24.xml.pos', 'ed_21.xml.pos', 
        'ed_07.xml.pos', 'ed_08.xml.pos', 'ed_03.xml.pos'] 

    def __init__(self, gui=False, *args):
        """
        Initialize the corpus builder.
        
        During initialization, the database table structure is defined.
        
        All corpus installers have to call the inherited initializer
        :func:`BaseCorpusBuilder.__init__`.
        
        Parameters
        ----------
        gui : bool
            True if the graphical installer is used, and False if the 
            installer runs on the console.
        """
        super(BuilderClass, self).__init__(gui, *args)

        # specify which features are provided by this corpus and lexicon:
        #self.lexicon_features = ["LEX_WORDID", "LEX_LEMMA", "LEX_ORTH", "LEX_POS"]
        #self.corpus_features = ["CORP_CONTEXT", "CORP_FILENAME", "CORP_STATISTICS", "CORP_SOURCE"]

        self.check_arguments()
        
        # add table descriptions for the tables used in this database.
        #
        # Every table has a primary key that uniquely identifies each entry
        # in the table. This primary key is used to link an entry from one
        # table to an entry from another table. The name of the primary key
        # stored in a string is given as the second argument to the function
        # add_table_description().
        #
        # A table description is a dictionary with at least a 'CREATE' key
        # which takes a list of strings as its value. Each of these strings
        # represents a MySQL instruction that is used to create the table.
        # Typically, this instruction is a column specification, but you can
        # also add other table options for this table. Note that the primary
        # key cannot be set manually.
        # 
        # Additionaly, the table description can have an 'INDEX' key which
        # takes a list of tuples as its value. Each tuple has three 
        # elements. The first element is a list of strings containing the
        # column names that are to be indexed. The second element is an
        # integer value specifying the index length for columns of Text
        # types. The third element specifies the index type (e.g. 'HASH' or
        # 'BTREE'). Note that not all MySQL storage engines support all 
        # index types.
        
        # Add the main corpus table. Each row in this table represents a 
        # token in the corpus. It has the following columns:
        # 
        # TokenId
        # An int value containing the unique identifier of the token
        #
        # WordId
        # An int value containing the unique identifier of the lexicon
        # entry associated with this token.
        #
        # FileId
        # An int value containing the unique identifier of the data file 
        # that contains this token.
        
        #self.corpus_table = "corpus"
        #self.corpus_id = "TokenId"
        #self.corpus_word_id = "WordId"
        #self.corpus_file_id = "FileId"
        #self.corpus_source_id = "SourceId"
        
        # Add the main lexicon table. Each row in this table represents a
        # word-form that occurs in the corpus. It has the following columns:
        #
        # WordId
        # An int value containing the unique identifier of this word-form.
        #
        # LemmaId
        # An int value containing the unique identifier of the lemma that
        # is associated with this word-form.
        # 
        # Text
        # A text value containing the orthographic representation of this
        # word-form.
        #
        # Additionally, if NLTK is used to tag part-of-speech:
        #
        # Pos
        # A text value containing the part-of-speech label of this 
        # word-form.
        
        #self.word_table = "word"
        #self.word_id = "WordId"
        #self.word_lemma = "Lemma"
        #self.word_label = "Text"
        #self.word_pos = "Pos"
        
        self.create_table_description(self.word_table,
            [Identifier(self.word_id, "SMALLINT(5) UNSIGNED NOT NULL"),
             Column(self.word_label, "VARCHAR(36) NOT NULL"),
             Column(self.word_lemma, "VARCHAR(36) NOT NULL"),
             Column(self.word_pos, "ENUM('CC','CD','DT','EX','FW','IN','JJ','JJR','JJS','LS','MD','NN','NNS','NP','NPS','PDT','POS','PP','PP$','PUNCT','RB','RBR','RBS','RP','SYM','TO','UH','VB','VBD','VBG','VBN','VBP','VBZ','WDT','WP','WP$','WRB') NOT NULL")])
             

        # Add the file table. Each row in this table represents a data file
        # that has been incorporated into the corpus. Each token from the
        # corpus table is linked to exactly one file from this table, and
        # more than one token may be linked to each file in this table.
        # The table contains the following columns:
        #
        # FileId
        # An int value containing the unique identifier of this file.
        # 
        # Path
        # A text value containing the path that points to this data file.
        
        #self.file_table = "file"
        #self.file_id = "FileId"
        #self.file_name = "Filename"
        #self.file_path = "Path"
        
        self.create_table_description(self.file_table,
            [Identifier(self.file_id, "SMALLINT(3) UNSIGNED NOT NULL"),
             Column(self.file_name, "TINYTEXT NOT NULL"),
             Column(self.file_path, "TINYTEXT NOT NULL")])
            
        #self.sentence_table = "sentence"
        #self.sentence_id = "SentenceId"
        
        #self.add_table_description(self.sentence_table, self.sentence_id,
            #{"CREATE" : [
                #"`{}` MEDIUMINT(5) UNSIGNED NOT NULL".format(self.sentence_id)]})
        
        #self.source_table = "source"
        #self.source_id = "SourceId"
        #self.source_mode = "Mode"
        #self.source_age = "Age"
        #self.source_gender = "Gender"
        #self.source_ethnicity = "Ethnicity"
        #self.source_date = "Date"
        #self.source_icetext = "ICE_text_category"
        #self.source_icetextcode = "ICE_text_code"
        #self.source_place = "Place"
        
        self.add_time_feature(self.source_date)
        self.add_time_feature(self.source_age)

        self.create_table_description(self.source_table,
            [Identifier(self.source_id, "SMALLINT(3) UNSIGNED NOT NULL"),
            Column(self.source_mode, "TINYTEXT NOT NULL"),
            Column(self.source_date, "VARCHAR(10) NOT NULL"), 
            Column(self.source_icetext, "ENUM('Academic writing humanities','Academic writing natural sciences','Academic writing social sciences','Academic writing technical','Administrative/instructive writing','Business letters','Editorials','Exams','Instructive writing/skills and hobbies','Novels','Popular writing humanities','Popular writing natural sciences','Popular writing social sciences','Popular writing technology','Press reportage','Social letters','Students essays') NOT NULL"), 
            Column(self.source_icetextcode, "ENUM('W1A','W1B','W2A','W2B','W2C','W2D','W2E','W2F') NOT NULL"), 
            Column(self.source_place, "VARCHAR(30) NOT NULL"), 
            Column(self.source_age, "VARCHAR(5) NOT NULL"),  
            Column(self.source_gender, "VARCHAR(1) NOT NULL"),  
            Column(self.source_ethnicity, "VARCHAR(15) NOT NULL")])

        self.create_table_description(self.corpus_table,
            [Identifier(self.corpus_id, "MEDIUMINT(6) UNSIGNED NOT NULL"),
             Link(self.corpus_file_id, self.file_table),
             Link(self.corpus_word_id, self.word_table),
             Link(self.corpus_source_id, self.source_table)])
                
        self._corpus_id = 0
        self._corpus_code = corpus_code
        

    def xml_preprocess_tag(self, element):
        #self.tag_token(self._corpus_id, element.tag, element.attrib, op=True)
        self.tag_next_token(element.tag, element.attrib)
        #if element.text or list(element):
            #self.tag_next_token(element.tag, element.attrib)
        #else:
            #self.add_empty_tag(element.tag, element.attrib)
            #if element.tag == "x-anonym-x":
                ## ICE-NG contains anonymized labels for names, placenames,
                ## and other nouns. Insert a special label in that case:
                #self._word_id = self.table_get(self.word_table, 
                        #{self.word_label: "ANONYMIZED", 
                        #self.word_lemma: "ANONYMIZED", 
                        #self.word_pos: "np"}, case=True)

    def xml_postprocess_tag(self, element):
        self.tag_token(self._corpus_id, element.tag, element.attrib, cl=True)
        # mon-empty tag
        #if element.text or list(element):
            #self.tag_last_token(element.tag, element.attrib)

    def process_text(self, text):
        for row in text.splitlines():
            try:
                self._value_word_label, self._value_word_pos, self._value_word_lemma = [x.strip() for x in row.split("\t")]
            except ValueError:
                pass
            else:
                self._value_word_label = self._replace_encoding_errors(self._value_word_label)
                self._value_word_lemma = self._replace_encoding_errors(self._value_word_lemma)
                new_sentence = False
                
                if self._value_word_pos == "CD":
                    self._value_word_lemma = self._value_word_label
                if self._value_word_pos in string.punctuation or self._value_word_pos == "''":
                    self._value_word_pos = "PUNCT"
                if self._value_word_pos == "SENT":
                    new_sentence = True
                    self._value_word_pos = "PUNCT"
                    
                if self._value_word_label and self._value_word_lemma:
                    self._word_id = self.table(self.word_table).get_or_insert(
                        {self.word_label: self._value_word_label, 
                        self.word_lemma: self._value_word_lemma, 
                        self.word_pos: self._value_word_pos}, case=True)
                        
                    self.add_token_to_corpus(
                        {self.corpus_word_id: self._word_id,
                        self.corpus_file_id: self._file_id,
                        self.corpus_source_id: self._source_id})

                #if new_sentence:
                    #self._sentence_id = self.table_get(self.sentence_table,
                        #{self.sentence_source_id: self._source_id})

    def xml_process_content(self, element_text):
        """ In ICE-NG, the XML elements contain rows of words. This method 
        processes these rows, and creates token entries in the corpus table. 
        It also creates new entries in the word table if necessary."""
        if element_text:
            self.process_text(element_text)

    def xml_process_tail(self, element_tail_text):
        if element_tail_text:
            self.process_text(element_tail_text)
        
    def xml_get_meta_information(self, root):
        meta = root.find("meta")

        try:
            self._value_source_date = meta.find("date").text.strip().split("\t")[0]
        except AttributeError:
            self._value_source_date = ""
        self._value_source_date = self._value_source_date.strip().strip("-")
        
        if self._value_source_date in ["TODO"]:
            self._value_source_date = ""

        try:
            self._value_source_place = meta.find("place").text.strip().split("\t")[0]
        except AttributeError:
            self._value_source_place = ""
            
        author = meta.find("author")

        try:
            self._value_source_gender = author.find("gender").text.strip().split("\t")[0]
        except AttributeError:
            self._value_source_gender = ""
        try:
            self._value_source_age = author.find("age").text.strip().split("\t")[0]
        except AttributeError:
            self._value_source_gage = ""
        try:
            self._value_source_ethnicity = author.find("ethnic-group").text.strip().split("\t")[0]
            self._value_source_ethnicity = self._value_source_ethnicity.strip("/")
            
        except AttributeError:
            self._value_source_ethnicity = ""

        # get text category, based on filename (see ICE-NG documentation):
        self._value_source_icetext, self._value_source_icetextcode = self._get_ice_text_category(self._current_file)
        
        # currently, only the written component is used:
        self._value_source_mode = "written"

        # all meta data gathered, store it:
        self._source_id = self.table(self.source_table).get_or_insert(
            {self.source_age: self._value_source_age,
             self.source_gender: self._value_source_gender,
             self.source_ethnicity: self._value_source_ethnicity,
             self.source_date: self._value_source_date,
             self.source_mode: self._value_source_mode,
             self.source_icetext: self._value_source_icetext,
             self.source_icetextcode: self._value_source_icetextcode,
             self.source_place: self._value_source_place})
                
    def _get_ice_text_category(self, file_name):
        """
        Retrieve the ICE text category for the file.
        
        The ICE-Nigeria documentation contains a list that maps the file
        names used in the corpus to ICE text categories. This list is used
        here to return a tuple with the description and the code as values.
        
        Parameters
        ----------
        file_name : string
            The name of the file
            
        Returns
        -------
        tup : tuple
            A tuple containing two strings: first, the description of the 
            category, second, the ICEtext category code.
        """
        
        mapping = {
            "ahum": ("Academic writing humanities", "W2A"),
            "ansc": ("Academic writing natural sciences", "W2A"),
            "assc": ("Academic writing social sciences", "W2A"),
            "atec": ("Academic writing technical", "W2A"),
            "adm":  ("Administrative/instructive writing", "W2D"),
            "bl":   ("Business letters", "W1B"),
            "ed":   ("Editorials", "W2E"),
            "ex":   ("Exams", "W1A"),
            "nov":  ("Novels", "W2F"),
            "phum": ("Popular writing humanities", "W2B"),
            "pnsc": ("Popular writing natural sciences", "W2B"),
            "pssc": ("Popular writing social sciences", "W2B"),
            "ptec": ("Popular writing technology", "W2B"),
            "pr":   ("Press reportage", "W2C"),
            "skho": ("Instructive writing/skills and hobbies", "W2D"),
            "sl":   ("Social letters", "W1B"),
            "ess":  ("Students essays", "W1A")}
        
        name = os.path.split(file_name)[1].lower()
        desc, code = mapping[name.partition("_")[0]]
        return desc, code
    
    def process_xml_file(self, current_file):
        """ Reads an XML file."""

        # There are a few errors in the XML files that are fixed in this 
        # method.
        #
        # First, if the lemma of the word is unknown, the non-conforming XML
        # tag '<unknown>' is used in the files. The fix is that in such a
        # case, the value of the first column (i.e. the orhtographic word) 
        # is copied to the last column (i.e. the lemma).
        #
        # Second, HTML entities (e.g. &quot;) are malformed. They are placed
        # in two lines, the first starting with the ampersand plus the name,
        # teh second line containing the closing semicolon.
        #
        # Third, sometimes the opening XML tag is fed into the POS tagger,
        # with disastrous results, e.g. from Pr_54.xml.pos, line 235:
        #
        #    <error  NN  <unknown>
        #    corrected=  NN  <unknown>
        #    "   ''  "
        #    &quot   NN  <unknown>
        #    ;   :   ;
        #    ."> JJ  <unknown>
        #    &quot   NN  <unknown>
        #    ;   :   ;
        #    </error>
        #
        # This is fixed by a hack: a line that contains more '<' than '>'
        # is considered malformed. The first column of every following line
        # is concatenated to the content of the first column of the 
        # malformed line, up to the point where a line is encountered that
        # contains more '>' than '<'. After that line, the file is processed
        # normally. This hack transforms the malformed lines above into
        # a well-formed XML segment that corresponds to the content of 
        # Pr_54.xml:
        #
        #     <error corrected="&quot;.">
        #     &quot;   PUNCT   &quot;
        #     </error>

        
        self._current_file = current_file

        file_buffer = StringIO()
        with codecs.open(current_file, "r", encoding = self.arguments.encoding) as input_file:
            skip = False
            fix_split_token = ""
            for i, line in enumerate(input_file):
                line = line.strip()
                if line.count("\t") == 2:
                    word, pos, lemma = line.split("\t")
                else:
                    word = line
                    pos = ""
                    lemma = ""
                
                # Some lines with only a semicolon in the word column are
                # left-overs from malformed HTML entities. Skip them if 
                # necessary:
                if word.strip() == ";" and skip:
                    skip = False
                else:                    
                    # HTML entities don't seem to be correctly encoded in 
                    # the POS files. Fix that:
                    if word.startswith("&") and not word.endswith(";"):
                        word = "{};".format(word)
                        pos = "PUNCT"
                        line = "{}\t{}\t{}".format(word, pos, lemma)
                        
                        # the next line will be skipped if it contains the
                        # trailing semicolon:
                        skip = True
                        
                    if not fix_split_token:
                        # if there are more opening brackets than closing
                        # brackets in a line, we may be dealing with a split
                        # XML token:
                        if line.count("<") != line.count(">") and line.find("\t") > -1:
                            fix_split_token = word + " "
                            
                        # '<unknown>' is not a valid XML tag:
                        if lemma == "<unknown>":
                            line = "{}\t{}\t{}".format(word, pos, word)
                    else:
                        # Fix split tokens by looking for a line with more
                        # closing brackets than opening brackets:
                        if line.count(">") > line.count("<"):
                            if fix_split_token.endswith('"'):
                                if (fix_split_token.count('"') % 2):
                                    line = "".join([fix_split_token, word])
                                else:
                                    line = " ".join([fix_split_token, word])
                            else:
                                line = "".join([fix_split_token, word])
                            fix_split_token = ""
                        else:
                            if word.startswith("'") > 0:
                                if fix_split_token.count("'") % 2:
                                    fix_split_token = "".join([fix_split_token, word])
                                else:
                                    fix_split_token = " ".join([fix_split_token, word])
                            elif word.startswith('"') > 0:
                                if fix_split_token.count('"') % 2:
                                    fix_split_token = "".join([fix_split_token, word])
                                else:
                                    fix_split_token = " ".join([fix_split_token, word])
                            else:
                                if fix_split_token.endswith('"'):
                                    
                                    if (fix_split_token.count('"') % 2):
                                        fix_split_token = "".join([fix_split_token, word])
                                    else:
                                        fix_split_token = " ".join([fix_split_token, word])
                                else:
                                    fix_split_token = "".join([fix_split_token, word])
                    if fix_split_token:
                        pass
                    else:
                        # The file buffer uses byte-strings, not unicode 
                        # strings. Therefore, encode the string first:
                        #file_buffer.write(line.encode("utf-8"))
                        #file_buffer.write("\n")
                        try:
                            file_buffer.write(line)
                        except UnicodeEncodeError:
                            file_buffer.write(line.encode("utf-8"))
                            
                        file_buffer.write("\n")
                        last = line

        S = file_buffer.getvalue()

        e = self.xml_parse_file(StringIO(S))
        self.xml_get_meta_information(e)
        self.xml_process_element(self.xml_get_body(e))
        
    def xml_get_body(self, root):
        return root.find("text")
        
    def process_file(self, current_file):
        # Process every file except for bl_18a.xml.pos. This file only 
        # contains unimportant meta information:
        if current_file.lower().find("bl_18a.xml.pos") == -1:
            self.process_xml_file(current_file)

    def get_file_identifier(self, path):
        _, base = os.path.split(path)
        while "." in base:
            base, _= os.path.splitext(base)
        return base.lower()

    @staticmethod
    def _replace_encoding_errors(s):
        """
        Replace erroneous character sequences by the correct character
        
        Unfortunately, some data files in ICE-NG have corrput character 
        encodings, which can limit the usefulness of the corpus data. This
        function attempts to reverse the faulty encoding by replacing any
        character sequence that appears to be the result of an encdoing 
        error by the character that was probably intended.
        
        Parameters
        ----------
        s : string
            The character string
            
        Returns
        -------
        s : string
            The input string with known encoding errors fixed.
        """
        
        # apparently, the character sequence â marks any faulty encoding,
        # and the next character is the actual encoding error. The problem
        # is that in ICE_NG, this three-character sequence can be split up
        # into two 'words', e.g. for the dash in Pr_13.txt, line 36 
        # ('hereas others – notably top officials'). In Pr_13.xml.pos, this
        # dash is represented in two separate rows in lines 381-382.
        
        # My solution is to find the two-character marker and replace it by
        # an empty string. Then, the next character is replaced, using the
        # lookup table.
        # The installer has to check, then, if the string is empty after
        # replacement. If so, it should discard the current line.
        
        # CHECK CHARACTERS after 'i' in ATec_01.xml.pos, ATec_06.xml.pos
        
        replace_list = [
            ("â", "‘"),
            ("â", "’"),

            ("â", "“"),
            ("â", "”"),

            ("â", "–"),
            
            ("Â°", "°"),
            ("Â·", "·"),

            ("Ã ", "à"),
            ("Ãš", "è"),
            ("Ã¬", "ì"),
            ("Ã²", "ò"),
            
            ("Ä", "ĕ"),

            ("Ã©", "é"),
            ("Ã­", "í"),
            ("Ãº", "ú"),

            ("Ã€", "ä"),
            
            ("Ã", "Ì"),
            
            ("Ã±", "ñ"),

            ("Ê€", "ʤ"),
            
            ("Î¼", "μ"),
            ("â", "∆"),
            ]
        corrupt_replace_list = [
            ("", "’"),
            ("", "–"),
        ]
        for old, new in replace_list:
            s = s.replace(old, new)

        for old, new in corrupt_replace_list:
            s = s.replace(old.replace("â", ""), new)
            
        return s

    @staticmethod
    def get_name():
        return "ICE_NG"

    @staticmethod
    def get_db_name():
        return "ice_ng"

    @staticmethod
    def get_language():
        return "English"
    
    @staticmethod
    def get_language_code():
        return "en-NG"
        
    @staticmethod
    def get_title():
        return "International Corpus of English – Nigeria"

    @staticmethod
    def get_description():
        return [
            "The International Corpus of English – Nigeria is a member of the ICE family of English corpora. It contains approximately 460.000 tokens of spoken Nigerian English, dating mostly from the first decade of the 21st century. Where known, the corpus provides speaker information (age, gender, ethnicity). The corpus also contains some textual meta information on the layout of the texts."]

    @staticmethod
    def get_license():
        return "ICE Nigeria is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike license (<a href='https://creativecommons.org/licenses/by-nc-sa/3.0/'>CC BY-NC-SA 3.0</a> DE)."
        
    @staticmethod
    def get_references():
        return [str(Article(
                authors=PersonList(
                    Person(first = "Eva-Maria", last = "Wunder"), 
                    Person(first = "Holger", last = "Voormann"), 
                    Person(first = "Ulrike", last = "Gut")), 
                title = "The ICE Nigeria corpus project: Creating an open, rich and accurate corpus",
                year = 2009,
                journal = "ICAME Journal",
                volume = 34,
                pages = "78-88"))]

    @staticmethod
    def get_url():
        return "http://ice-corpora.net/ice/index.htm"
    
if __name__ == "__main__":
    BuilderClass().build()
